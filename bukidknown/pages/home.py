# =============================================================================
# pages/home.py  –  BukidKnown Home Page
# Shows: hero banner, quick stats, category filters, featured destinations,
# featured businesses, and a safety reminder banner.
# =============================================================================

import streamlit as st
from database.db import (
    fetch_all_destinations, fetch_all_businesses,
    fetch_platform_analytics, fetch_avg_rating
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _badge_class(category):
    return {
        "Waterfall": "bk-badge-waterfall",
        "Nature":    "bk-badge-nature",
        "Hiking":    "bk-badge-hiking",
        "Resort":    "bk-badge-resort",
        "Cultural":  "bk-badge-cultural",
    }.get(category, "bk-badge-nature")


def _stars(avg):
    full = int(round(avg))
    return "⭐" * full + "☆" * (5 - full)


def _dest_card(spot, key_prefix):
    img = spot["image_path"] or "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600"
    fee = f"₱{spot['entrance_fee']:.0f}" if spot["entrance_fee"] > 0 else "Free"
    r   = fetch_avg_rating(spot["id"])
    badge = _badge_class(spot["category"])

    # Use st.image for local files, HTML img for URLs
    if img and img.startswith("assets/"):
        st.image(img, use_container_width=True)
        st.markdown(f"""
        <div class="bk-dest-card" style="margin-top:-10px">
            <div class="bk-dest-body">
                <div class="bk-dest-name">{spot['name']}</div>
                <div class="bk-dest-meta">📍 {spot['municipality'] or spot['location']}</div>
                <div class="bk-dest-fee">🎟️ {fee} entrance</div>
                <div style="margin-top:4px">
                    <span style="color:#F59E0B;font-size:0.85rem">{_stars(r['avg'])}</span>
                    <span style="font-size:0.75rem;color:#6B7280"> ({r['cnt']})</span>
                </div>
                <span class="bk-badge {badge}">{spot['category']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bk-dest-card">
            <img class="bk-dest-img" src="{img}" alt="{spot['name']}"/>
            <div class="bk-dest-body">
                <div class="bk-dest-name">{spot['name']}</div>
                <div class="bk-dest-meta">📍 {spot['municipality'] or spot['location']}</div>
                <div class="bk-dest-fee">🎟️ {fee} entrance</div>
                <div style="margin-top:4px">
                    <span style="color:#F59E0B;font-size:0.85rem">{_stars(r['avg'])}</span>
                    <span style="font-size:0.75rem;color:#6B7280"> ({r['cnt']})</span>
                </div>
                <span class="bk-badge {badge}">{spot['category']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("View Details →", key=f"{key_prefix}_{spot['id']}", use_container_width=True):
        st.session_state.selected_spot_id = spot["id"]
        st.session_state.page = "spot_detail"
        st.rerun()


# ── Main render ────────────────────────────────────────────────────────────

def render():

    # ── Hero ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="bk-hero">
        <div class="bk-hero-eyebrow">🇵🇭 Northern Mindanao, Philippines</div>
        <div class="bk-hero-title">Discover the Heart<br>of Bukidnon</div>
        <div class="bk-hero-subtitle">
            Explore majestic waterfalls, highland adventures, cultural heritage,
            and lush nature reserves across the Province of Bukidnon.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick search bar ───────────────────────────────────────────────────
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        query = st.text_input(
            "Search",
            placeholder="🔍  Search destinations, activities, or municipalities…",
            label_visibility="collapsed"
        )
    with col_btn:
        if st.button("Search", type="primary", use_container_width=True):
            st.session_state.search_query = query
            st.session_state.page = "search"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Platform stats ─────────────────────────────────────────────────────
    analytics = fetch_platform_analytics()
    c1, c2, c3, c4 = st.columns(4)

    for col, icon, value, label in [
        (c1, "🏞️", analytics["total_destinations"], "Tourist Spots"),
        (c2, "👤", analytics["total_users"],         "Registered Users"),
        (c3, "📅", analytics["total_bookings"],      "Tours Booked"),
        (c4, "⭐", f"{analytics['avg_rating']}★",    "Avg. Rating"),
    ]:
        with col:
            st.markdown(f"""
            <div class="bk-stat">
                <div class="bk-stat-icon">{icon}</div>
                <div class="bk-stat-value">{value}</div>
                <div class="bk-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Category quick filter ──────────────────────────────────────────────
    st.markdown("### 🗂️ Browse by Category")
    categories = ["All", "Waterfall", "Nature", "Hiking", "Resort", "Cultural"]
    cat_icons  = {"All":"🌍","Waterfall":"💦","Nature":"🌿","Hiking":"🧗","Resort":"🏖️","Cultural":"🏛️"}

    cat_cols = st.columns(len(categories))
    if "home_cat" not in st.session_state:
        st.session_state.home_cat = "All"

    for i, cat in enumerate(categories):
        with cat_cols[i]:
            if st.button(
                f"{cat_icons[cat]} {cat}",
                key=f"home_cat_{cat}",
                use_container_width=True
            ):
                st.session_state.home_cat = cat
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Featured Destinations ─────────────────────────────────────────────
    st.markdown("### 🌟 Featured Destinations")

    all_spots = fetch_all_destinations()
    selected_cat = st.session_state.home_cat

    if selected_cat != "All":
        filtered = [s for s in all_spots if s["category"] == selected_cat]
    else:
        filtered = all_spots

    if not filtered:
        st.info(f"No destinations in the '{selected_cat}' category yet.")
    else:
        cols = st.columns(3)
        for i, spot in enumerate(filtered[:6]):
            with cols[i % 3]:
                _dest_card(spot, "home_spot")

        if len(filtered) > 6:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🏞️ View All Tourist Spots", type="primary", use_container_width=True):
                st.session_state.page = "spots"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Featured Businesses ───────────────────────────────────────────────
    st.markdown("### 🏪 Featured Local Businesses")
    businesses = fetch_all_businesses(verified_only=True)[:4]

    if businesses:
        biz_cols = st.columns(2)
        for i, biz in enumerate(businesses):
            with biz_cols[i % 2]:
                # Safely truncate and escape description to avoid broken HTML
                import html as _html
                desc      = _html.escape(str(biz["description"] or ""))
                desc_short= desc[:120] + ("..." if len(desc) > 120 else "")
                biz_name  = _html.escape(str(biz["business_name"] or ""))
                address   = _html.escape(str(biz["address"] or ""))
                contact   = _html.escape(str(biz["contact_number"] or ""))
                category  = _html.escape(str(biz["category"] or ""))

                priority_badge = (
                    "<span class='bk-biz-priority'>&#11088; Priority</span>"
                    if biz["is_priority"] else ""
                )

                card_html = (
                    "<div class='bk-biz-card' style='margin-bottom:12px'>"
                    + priority_badge
                    + f"<div class='bk-biz-name'>{biz_name}</div>"
                    + f"<div class='bk-biz-meta'>"
                    + f"&#128193; {category} &nbsp;|&nbsp; &#128205; {address}"
                    + "</div>"
                    + f"<div style='font-size:0.85rem;color:#374151;margin-top:6px'>{desc_short}</div>"
                    + f"<div style='font-size:0.8rem;color:#6B7280;margin-top:6px'>&#128222; {contact}</div>"
                    + "</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No verified businesses yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Safety banner ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="bk-safety">
        <strong>🛡️ Travel Safety Reminders</strong><br>
        Always register at the local tourism office before trekking ·
        Hire DENR-accredited guides for protected areas ·
        Bring a first-aid kit and enough water ·
        Respect wildlife and leave no trace ·
        Check weather conditions before visiting waterfalls or mountain areas.
    </div>
    """, unsafe_allow_html=True)