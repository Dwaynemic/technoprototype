# =============================================================================
# pages/spot_detail.py  –  Individual Destination Detail
# Tabs: About, Map, Reviews, Book Tour
# =============================================================================

import streamlit as st
from database.db import (
    fetch_destination_by_id, fetch_avg_rating,
    fetch_reviews, insert_review, insert_booking
)
from database.db import fetch_user_by_id


def _stars(avg, max_s=5):
    full = int(round(avg))
    return "⭐" * full + "☆" * (max_s - full)


def render():
    spot_id = st.session_state.get("selected_spot_id")
    if not spot_id:
        st.error("No destination selected.")
        return

    spot = fetch_destination_by_id(spot_id)
    if not spot:
        st.error("Destination not found.")
        return

    # Back button
    if st.button("← Back to Spots"):
        st.session_state.page = "spots"
        st.rerun()

    # Hero image
    img = spot["image_path"] or "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800"
    st.image(img, use_container_width=True)

    # Title row
    r = fetch_avg_rating(spot_id)
    col_title, col_cost = st.columns([3, 1])
    with col_title:
        st.markdown(
            f"<h1 style='font-family:Playfair Display,serif;margin-bottom:4px'>"
            f"{spot['name']}</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"📍 **{spot['municipality']}**, Bukidnon &nbsp;|&nbsp; "
            f"🗂️ **{spot['category']}**",
            unsafe_allow_html=True
        )
        if r["cnt"] > 0:
            st.markdown(
                f"<span style='color:#F59E0B;font-size:1.1rem'>{_stars(r['avg'])}</span> "
                f"**{r['avg']}** ({r['cnt']} reviews)",
                unsafe_allow_html=True
            )
    with col_cost:
        fee    = f"₱{spot['entrance_fee']:.0f}" if spot["entrance_fee"] > 0 else "FREE"
        budget = f"₱{spot['estimated_cost']:.0f}"
        st.markdown(f"""
        <div class="bk-stat" style="text-align:center">
            <div style="font-size:1.6rem">🎟️</div>
            <div class="bk-stat-value" style="font-size:1.5rem">{fee}</div>
            <div class="bk-stat-label">Entrance Fee</div>
            <hr style="margin:8px 0">
            <div class="bk-stat-label">Est. Budget: <strong>{budget}</strong></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs
    tab_about, tab_map, tab_reviews, tab_book = st.tabs(
        ["📋 About", "🗺️ Map", "⭐ Reviews", "📅 Book a Tour"]
    )

    # ── About ──────────────────────────────────────────────────────────────
    with tab_about:
        st.markdown("#### Description")
        st.write(spot["description"])

        if spot["safety_tips"]:
            st.markdown(f"""
            <div class="bk-safety" style="margin-top:14px">
                <strong>🛡️ Safety Tips</strong><br>{spot['safety_tips']}
            </div>
            """, unsafe_allow_html=True)

        # Quick expense estimator shortcut
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💰 Estimate Travel Cost for this Spot", use_container_width=True):
            st.session_state.estimator_spot_id = spot_id
            st.session_state.page = "estimator"
            st.rerun()

    # ── Map ────────────────────────────────────────────────────────────────
    with tab_map:
        lat, lng = spot["latitude"], spot["longitude"]
        if lat and lng:
            try:
                import folium
                import streamlit_folium as stf
                m = folium.Map(location=[lat, lng], zoom_start=13)
                folium.Marker(
                    [lat, lng],
                    popup=spot["name"],
                    tooltip=spot["name"],
                    icon=folium.Icon(color="green", icon="star"),
                ).add_to(m)
                stf.folium_static(m, width=700, height=380)
            except ImportError:
                st.info(f"📍 Coordinates: **{lat}, {lng}**")
                maps_link = f"https://maps.google.com/?q={lat},{lng}"
                st.markdown(f"[📍 Open in Google Maps]({maps_link})")
        else:
            st.info("Map coordinates are not available for this destination.")

    # ── Reviews ────────────────────────────────────────────────────────────
    with tab_reviews:
        uid = st.session_state.get("user_id")
        user = fetch_user_by_id(uid) if uid else None

        if user:
            with st.expander("✍️ Write a Review"):
                with st.form("review_form"):
                    rating  = st.slider("Your Rating", 1, 5, 5)
                    comment = st.text_area("Your Experience")
                    if st.form_submit_button("Submit Review", type="primary"):
                        insert_review(user["id"], spot_id, rating, comment,
                                      user["name"] or user["username"])
                        st.success("✅ Review submitted! Thank you.")
                        st.rerun()
        else:
            st.info("Please [login](/auth) to write a review.")

        st.markdown("#### All Reviews")
        reviews = fetch_reviews(spot_id)
        if not reviews:
            st.info("No reviews yet. Be the first to review this spot!")
        for rev in reviews:
            stars = "⭐" * rev["rating"] + "☆" * (5 - rev["rating"])
            st.markdown(f"""
            <div class="bk-review">
                <div style="display:flex;justify-content:space-between">
                    <span class="bk-review-author">👤 {rev['reviewer_name']}</span>
                    <span class="bk-review-date">{rev['created_at'][:10]}</span>
                </div>
                <div class="bk-review-stars">{stars}</div>
                <div class="bk-review-text">{rev['comment']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Book a Tour ────────────────────────────────────────────────────────
    with tab_book:
        uid  = st.session_state.get("user_id")
        user = fetch_user_by_id(uid) if uid else None

        if not user:
            st.info("Please login to submit a booking request.")
            if st.button("🔑 Login to Book"):
                st.session_state.page = "auth"
                st.rerun()
        else:
            st.markdown(f"**Booking for: {spot['name']}**")
            with st.form("detail_booking_form"):
                col1, col2 = st.columns(2)
                with col1:
                    tour_date   = st.date_input("📅 Tour Date")
                    num_persons = st.number_input("👥 Number of Persons", 1, 50, 1)
                with col2:
                    agency  = st.text_input("🏢 Tour Agency", value="BukidKnown Tours")
                    contact = st.text_input("📞 Your Contact Number")
                notes = st.text_area("💬 Special Requests (optional)")
                if st.form_submit_button("📅 Submit Booking Request", type="primary", use_container_width=True):
                    if not contact:
                        st.error("Contact number is required.")
                    else:
                        insert_booking({
                            "tourist_name":   user["name"] or user["username"],
                            "tourist_id":     user["id"],
                            "destination":    spot["name"],
                            "destination_id": spot_id,
                            "agency_name":    agency,
                            "tour_date":      str(tour_date),
                            "num_persons":    num_persons,
                            "contact":        contact,
                            "notes":          notes,
                        })
                        st.success("✅ Booking request submitted! The agency will contact you soon.")
