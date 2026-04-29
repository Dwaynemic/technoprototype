# =============================================================================
# pages/spots.py  –  All Tourist Spots
# Lists all approved destinations with category and municipality filters.
# =============================================================================

import streamlit as st
from database.db import fetch_all_destinations, fetch_avg_rating


def _badge(cat):
    m = {"Waterfall":"bk-badge-waterfall","Nature":"bk-badge-nature",
         "Hiking":"bk-badge-hiking","Resort":"bk-badge-resort","Cultural":"bk-badge-cultural"}
    return m.get(cat, "bk-badge-nature")


def render():
    st.markdown("<div class='bk-section-title'>🏞️ Tourist Spots</div>", unsafe_allow_html=True)
    st.markdown("<div class='bk-section-sub'>All approved destinations across Bukidnon</div>", unsafe_allow_html=True)

    all_spots = fetch_all_destinations()
    municipalities = ["All"] + sorted({s["municipality"] for s in all_spots if s["municipality"]})
    categories     = ["All", "Waterfall", "Nature", "Hiking", "Resort", "Cultural"]

    col1, col2 = st.columns(2)
    with col1:
        sel_cat = st.selectbox("Filter by Category", categories)
    with col2:
        sel_mun = st.selectbox("Filter by Municipality", municipalities)

    filtered = all_spots
    if sel_cat != "All":
        filtered = [s for s in filtered if s["category"] == sel_cat]
    if sel_mun != "All":
        filtered = [s for s in filtered if s["municipality"] == sel_mun]

    st.markdown(f"**{len(filtered)} destination(s) found**")
    st.divider()

    if not filtered:
        st.info("No spots match your selected filters.")
        return

    cols = st.columns(3)
    for i, spot in enumerate(filtered):
        r   = fetch_avg_rating(spot["id"])
        img = spot["image_path"] or "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600"
        fee = f"₱{spot['entrance_fee']:.0f}" if spot["entrance_fee"] > 0 else "Free"

        with cols[i % 3]:
            # Use st.image for local files, HTML img for URLs
            if img and img.startswith("assets/"):
                st.image(img, use_container_width=True)
                st.markdown(f"""
                <div class="bk-dest-card" style="margin-top:-10px">
                    <div class="bk-dest-body">
                        <div class="bk-dest-name">{spot['name']}</div>
                        <div class="bk-dest-meta">📍 {spot['municipality']}</div>
                        <div class="bk-dest-fee">🎟️ {fee}</div>
                        <div style="color:#F59E0B;font-size:0.85rem">
                            {"⭐"*int(round(r['avg']))}{"☆"*(5-int(round(r['avg'])))}
                            <span style="font-size:0.75rem;color:#6B7280"> ({r['cnt']})</span>
                        </div>
                        <span class="bk-badge {_badge(spot['category'])}">{spot['category']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bk-dest-card">
                    <img class="bk-dest-img" src="{img}" alt="{spot['name']}"/>
                    <div class="bk-dest-body">
                        <div class="bk-dest-name">{spot['name']}</div>
                        <div class="bk-dest-meta">📍 {spot['municipality']}</div>
                        <div class="bk-dest-fee">🎟️ {fee}</div>
                        <div style="color:#F59E0B;font-size:0.85rem">
                            {"⭐"*int(round(r['avg']))}{"☆"*(5-int(round(r['avg'])))}
                            <span style="font-size:0.75rem;color:#6B7280"> ({r['cnt']})</span>
                        </div>
                        <span class="bk-badge {_badge(spot['category'])}">{spot['category']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("View Details →", key=f"spots_{spot['id']}", use_container_width=True):
                st.session_state.selected_spot_id = spot["id"]
                st.session_state.page = "spot_detail"
                st.rerun()
