# =============================================================================
# pages/reviews.py  –  Reviews & Ratings
# =============================================================================

import streamlit as st
from database.db import (
    fetch_all_destinations, fetch_reviews,
    fetch_avg_rating, insert_review, fetch_user_by_id
)


def render():
    st.markdown("<div class='bk-section-title'>⭐ Reviews & Ratings</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>See what fellow travelers say about Bukidnon's destinations</div>",
        unsafe_allow_html=True
    )

    all_spots = fetch_all_destinations()

    # ── Top Rated ─────────────────────────────────────────────────────────
    st.markdown("### 🏆 Top Rated Spots")
    rated = [(s, fetch_avg_rating(s["id"])) for s in all_spots]
    rated = sorted(rated, key=lambda x: x[1]["avg"], reverse=True)[:4]

    top_cols = st.columns(4)
    for i, (spot, r) in enumerate(rated):
        with top_cols[i]:
            stars_str = "⭐" * int(round(r["avg"])) + "☆" * (5 - int(round(r["avg"])))
            st.markdown(f"""
            <div class="bk-stat">
                <div style="font-size:0.85rem;font-weight:600;color:#1A1A2E;margin-bottom:4px">
                    {spot['name']}
                </div>
                <div style="color:#F59E0B;font-size:1.1rem">{stars_str}</div>
                <div style="font-size:0.78rem;color:#6B7280;margin-top:2px">
                    {r['avg']} · {r['cnt']} review(s)
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Write a Review ─────────────────────────────────────────────────────
    uid  = st.session_state.get("user_id")
    user = fetch_user_by_id(uid) if uid else None

    if user:
        with st.expander("✍️ Write a Review"):
            with st.form("global_review_form"):
                dest_names = {s["name"]: s["id"] for s in all_spots}
                chosen_spot = st.selectbox("Choose Destination", list(dest_names.keys()))
                rating      = st.slider("Rating", 1, 5, 5)
                comment     = st.text_area("Your Experience")
                if st.form_submit_button("Submit Review", type="primary"):
                    insert_review(
                        user["id"], dest_names[chosen_spot],
                        rating, comment, user["name"] or user["username"]
                    )
                    st.success("✅ Review submitted!")
                    st.rerun()
    else:
        st.info("Please login to write a review.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filter & Browse Reviews ────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📝 All Reviews")
    with col2:
        filter_opts  = ["All Destinations"] + [s["name"] for s in all_spots]
        filter_spot  = st.selectbox("Filter by Spot", filter_opts, label_visibility="collapsed")

    if filter_spot == "All Destinations":
        reviews = fetch_reviews()
        spot_map = {s["id"]: s["name"] for s in all_spots}
    else:
        sid     = next(s["id"] for s in all_spots if s["name"] == filter_spot)
        reviews = fetch_reviews(sid)
        spot_map = {sid: filter_spot}

    if not reviews:
        st.info("No reviews yet.")
        return

    for rev in reviews:
        stars = "⭐" * rev["rating"] + "☆" * (5 - rev["rating"])
        dest_label = spot_map.get(rev["destination_id"], "Unknown Spot")
        st.markdown(f"""
        <div class="bk-review">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <div>
                    <span class="bk-review-author">👤 {rev['reviewer_name']}</span>
                    <span style="font-size:0.78rem;color:#6B7280;margin-left:8px">
                        on {dest_label}
                    </span>
                </div>
                <span class="bk-review-date">{rev['created_at'][:10]}</span>
            </div>
            <div class="bk-review-stars">{stars}</div>
            <div class="bk-review-text">{rev['comment']}</div>
        </div>
        """, unsafe_allow_html=True)
