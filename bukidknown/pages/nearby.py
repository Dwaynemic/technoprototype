# =============================================================================
# pages/nearby.py  –  Nearby Tourist Spots
# Uses distance calculation from preset or custom coordinates.
# =============================================================================

import streamlit as st
from database.db import fetch_nearby_destinations, fetch_avg_rating


PRESET_LOCATIONS = {
    "Malaybalay City Center":   (8.1575, 125.1278),
    "Manolo Fortich Town":      (8.3627, 124.8572),
    "Quezon, Bukidnon":         (8.0243, 125.0935),
    "Lantapan Town":            (8.1747, 124.8801),
    "Impasug-ong Town":         (8.2916, 125.0003),
    "San Fernando, Bukidnon":   (7.9812, 125.0451),
    "Custom Coordinates…":      None,
}


def render():
    st.markdown("<div class='bk-section-title'>📍 Nearby Spots</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Find tourist destinations close to your current location</div>",
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style="background:#EEF2FF;border-left:4px solid #6366F1;border-radius:8px;
        padding:12px 16px;margin-bottom:16px;font-size:0.88rem;color:#3730A3">
        📡 Select your starting location or enter custom GPS coordinates to find nearby spots.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        preset = st.selectbox("📌 Starting Location", list(PRESET_LOCATIONS.keys()))
    with col2:
        radius = st.slider("Search Radius (km)", min_value=5, max_value=100, value=30)

    coords = PRESET_LOCATIONS[preset]
    if coords is None:
        cc1, cc2 = st.columns(2)
        with cc1:
            lat = st.number_input("Latitude",  value=8.1575, format="%.4f")
        with cc2:
            lng = st.number_input("Longitude", value=125.1278, format="%.4f")
    else:
        lat, lng = coords

    nearby = fetch_nearby_destinations(lat, lng, radius)
    st.markdown(f"**{len(nearby)} spot(s) found within {radius} km**")
    st.divider()

    # ── Map ────────────────────────────────────────────────────────────────
    if nearby:
        try:
            import folium
            import streamlit_folium as stf
            m = folium.Map(location=[lat, lng], zoom_start=10)
            folium.Marker(
                [lat, lng],
                popup="📍 Your Location",
                tooltip="Your Location",
                icon=folium.Icon(color="red", icon="home"),
            ).add_to(m)
            for s in nearby:
                if s["latitude"] and s["longitude"]:
                    folium.Marker(
                        [s["latitude"], s["longitude"]],
                        popup=f"{s['name']} ({s['distance_km']} km)",
                        tooltip=s["name"],
                        icon=folium.Icon(color="green", icon="star"),
                    ).add_to(m)
            stf.folium_static(m, width=700, height=360)
        except ImportError:
            st.info("Install `folium` and `streamlit-folium` for interactive maps.")

    st.markdown("<br>", unsafe_allow_html=True)

    if not nearby:
        st.info(f"No spots found within {radius} km. Try increasing the radius.")
        return

    cols = st.columns(3)
    for i, spot in enumerate(nearby):
        r   = fetch_avg_rating(spot["id"])
        img = spot["image_path"] or "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600"
        fee = f"₱{spot['entrance_fee']:.0f}" if spot["entrance_fee"] > 0 else "Free"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="bk-dest-card">
                <img class="bk-dest-img" src="{img}" alt="{spot['name']}"/>
                <div class="bk-dest-body">
                    <div class="bk-dest-name">{spot['name']}</div>
                    <div class="bk-dest-meta">📏 {spot['distance_km']} km away</div>
                    <div class="bk-dest-fee">🎟️ {fee}</div>
                    <div style="color:#F59E0B;font-size:0.82rem">
                        {"⭐"*int(round(r['avg']))}{"☆"*(5-int(round(r['avg'])))}
                        <span style="font-size:0.72rem;color:#6B7280"> ({r['cnt']})</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Details →", key=f"nearby_{spot['id']}", use_container_width=True):
                st.session_state.selected_spot_id = spot["id"]
                st.session_state.page = "spot_detail"
                st.rerun()
