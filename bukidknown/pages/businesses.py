# =============================================================================
# pages/businesses.py  –  Nearby Businesses
# Shows verified local businesses: Cafes, Restaurants, Tourist Shops, etc.
# Priority listings appear first (is_priority = TRUE).
# =============================================================================

import streamlit as st
from database.db import fetch_all_businesses, increment_business_stat


BIZ_ICONS = {
    "Cafe":         "☕",
    "Restaurant":   "🍽️",
    "Tourist Shop": "🛍️",
    "Accommodation":"🏨",
    "Transport":    "🚐",
    "Tour Guide":   "🧭",
    "Other":        "🏢",
}


def render():
    st.markdown("<div class='bk-section-title'>🏪 Nearby Businesses</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Discover local cafes, restaurants, tour services, and shops</div>",
        unsafe_allow_html=True
    )

    # Category filter
    categories = ["All", "Cafe", "Restaurant", "Tourist Shop", "Accommodation",
                  "Transport", "Tour Guide", "Other"]
    sel_cat = st.selectbox("Filter by Business Type", categories, label_visibility="collapsed")

    businesses = fetch_all_businesses(verified_only=True)

    if sel_cat != "All":
        businesses = [b for b in businesses if b["category"] == sel_cat]

    st.markdown(f"**{len(businesses)} business(es) found** — Priority listings shown first")
    st.divider()

    if not businesses:
        st.info("No businesses in this category yet.")
        return

    # ── Priority listings highlighted ─────────────────────────────────────
    priority = [b for b in businesses if b["is_priority"]]
    regular  = [b for b in businesses if not b["is_priority"]]

    if priority:
        st.markdown("### ⭐ Priority Listings")
        _render_business_grid(priority, key_prefix="pri")
        st.markdown("<br>", unsafe_allow_html=True)

    if regular:
        if priority:
            st.markdown("### 🏪 All Businesses")
        _render_business_grid(regular, key_prefix="reg")


def _render_business_grid(businesses, key_prefix):
    import html as _html
    cols = st.columns(2)
    for i, biz in enumerate(businesses):
        icon = BIZ_ICONS.get(biz["category"], "🏢")
        img  = biz["image_path"] or ""

        # Escape all user-supplied text so it cannot break HTML
        biz_name = _html.escape(str(biz["business_name"] or ""))
        category = _html.escape(str(biz["category"] or ""))
        address  = _html.escape(str(biz["address"] or ""))
        contact  = _html.escape(str(biz["contact_number"] or ""))
        raw_desc = str(biz["description"] or "")
        desc     = _html.escape(raw_desc[:120]) + ("..." if len(raw_desc) > 120 else "")
        views    = int(biz.get("views", 0))
        clicks   = int(biz.get("clicks", 0))

        priority_badge = (
            "<span class='bk-biz-priority'>&#11088; Priority</span>"
            if biz["is_priority"] else ""
        )
        pill_cls  = "bk-pill-verified" if biz["is_verified"] else "bk-pill-unverified"
        pill_text = "&#10003; Verified"  if biz["is_verified"] else "&#8987; Pending"

        with cols[i % 2]:
            # Image (if available)
            if img:
                st.markdown(
                    "<img src='" + img + "' style='width:100%;height:140px;"
                    "object-fit:cover;border-radius:10px;margin-bottom:8px'>",
                    unsafe_allow_html=True
                )

            card = (
                "<div class='bk-biz-card' style='margin-bottom:14px'>"
                + priority_badge
                + f"<div class='bk-biz-name'>{icon} {biz_name}</div>"
                + f"<div class='bk-biz-meta' style='margin-top:4px'>"
                + f"&#128193; {category} &nbsp;|&nbsp;"
                + f"<span class='bk-pill {pill_cls}'>{pill_text}</span>"
                + "</div>"
                + f"<div style='font-size:0.85rem;color:#374151;margin-top:6px;line-height:1.5'>{desc}</div>"
                + f"<div style='margin-top:8px;font-size:0.82rem;color:#6B7280'>"
                + f"&#128205; {address}<br>&#128222; {contact}"
                + "</div>"
                + f"<div style='margin-top:6px;font-size:0.78rem;color:#9CA3AF'>"
                + f"&#128065; {views} views &nbsp;|&nbsp; &#128432; {clicks} clicks"
                + "</div>"
                + "</div>"
            )
            st.markdown(card, unsafe_allow_html=True)

            if st.button(f"📞 Inquire / View", key=f"{key_prefix}_biz_{biz['id']}", use_container_width=True):
                increment_business_stat(biz["id"], "inquiries")
                increment_business_stat(biz["id"], "clicks")
                st.info(f"📞 Contact: **{biz['contact_number']}** | 📍 {biz['address']}")
