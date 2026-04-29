# =============================================================================
# pages/biz_dashboard.py  –  Business Owner Dashboard
#
# Tabs:
#   1. My Listings   – view all business listings for this user
#   2. Add Business  – register a new business (fields from spec)
#   3. Submit Spot   – submit a new tourist destination for admin review
#   4. Analytics     – views, clicks, inquiries per listing
# =============================================================================

import streamlit as st
from database.db import (
    fetch_all_businesses, insert_business, update_business,
    fetch_all_destinations, insert_destination,
    fetch_user_by_id
)


BUSINESS_CATEGORIES = [
    "Cafe", "Restaurant", "Accommodation", "Tourist Shop",
    "Transport", "Tour Guide", "Adventure Activity", "Other"
]

DEST_CATEGORIES = ["Waterfall", "Nature", "Hiking", "Resort", "Cultural"]


def _require_role(*roles):
    uid  = st.session_state.get("user_id")
    user = fetch_user_by_id(uid) if uid else None
    if not user:
        st.warning("⚠️ Please login to access this page.")
        if st.button("🔑 Go to Login"):
            st.session_state.page = "auth"
            st.rerun()
        st.stop()
    if user["role"] not in roles:
        st.error("🚫 You do not have permission to access this page.")
        st.stop()
    return user


def render():
    user = _require_role("business", "admin")

    st.markdown("<div class='bk-section-title'>🏪 Business Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Manage your business listings and promotions</div>",
        unsafe_allow_html=True
    )

    tab_list, tab_add, tab_spot, tab_analytics = st.tabs([
        "📋 My Listings",
        "➕ Register Business",
        "🏞️ Submit a Spot",
        "📊 My Analytics",
    ])

    # ── My Listings ────────────────────────────────────────────────────────
    with tab_list:
        # Admin sees all; business user sees only theirs
        uid_filter = None if user["role"] == "admin" else user["id"]
        listings   = fetch_all_businesses(user_id=uid_filter)

        if not listings:
            st.info("You have no business listings yet. Use 'Register Business' to add one.")
        else:
            st.markdown(f"**{len(listings)} listing(s)**")
            for biz in listings:
                verified_html = (
                    "<span class='bk-pill bk-pill-verified'>✅ Verified</span>"
                    if biz["is_verified"]
                    else "<span class='bk-pill bk-pill-unverified'>⏳ Pending Verification</span>"
                )
                priority_html = (
                    "<span class='bk-pill bk-pill-priority'>⭐ Priority</span>"
                    if biz["is_priority"] else ""
                )
                st.markdown(f"""
                <div class="bk-form" style="margin-bottom:14px">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:6px">
                        <div>
                            <strong style="font-size:1.05rem">{biz['business_name']}</strong>
                            <div style="font-size:0.82rem;color:#6B7280;margin-top:2px">
                                🗂️ {biz['category']} &nbsp;|&nbsp;
                                📍 {biz['address']} &nbsp;|&nbsp;
                                📞 {biz['contact_number']}
                            </div>
                        </div>
                        <div style="display:flex;gap:6px;flex-wrap:wrap">
                            {verified_html} {priority_html}
                        </div>
                    </div>
                    <div style="font-size:0.88rem;color:#374151;margin-top:8px">
                        {biz['description'][:160]}{'…' if len(biz['description'] or '')>160 else ''}
                    </div>
                    <div style="font-size:0.76rem;color:#9CA3AF;margin-top:6px">
                        👁️ {biz['views']} views &nbsp;|&nbsp;
                        🖱️ {biz['clicks']} clicks &nbsp;|&nbsp;
                        📨 {biz['inquiries']} inquiries
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Register Business ──────────────────────────────────────────────────
    with tab_add:
        st.markdown("""
        <div style="background:#EEF2FF;border-left:4px solid #6366F1;border-radius:8px;
            padding:12px 16px;margin-bottom:16px;font-size:0.88rem;color:#3730A3">
            Fill in your business details below. Your listing will appear publicly
            after admin verification. Priority listings appear at the top of results.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_business_form"):
            st.markdown("#### 📝 Business Information")
            col1, col2 = st.columns(2)
            with col1:
                biz_name    = st.text_input("Business Name *")
                category    = st.selectbox("Category *", BUSINESS_CATEGORIES)
                contact_num = st.text_input("Contact Number *")
            with col2:
                address     = st.text_input("Address / Location *")
                image_url   = st.text_input("Photo URL (optional)")
                is_priority = st.checkbox(
                    "⭐ Priority Listing — appears at top of business list",
                    value=False
                )

            description = st.text_area("Business Description *", height=100)
            promotion   = st.text_area("Promotions / Packages (optional)", height=80)

            submitted = st.form_submit_button(
                "Register Business", type="primary", use_container_width=True
            )

        if submitted:
            if not all([biz_name.strip(), address.strip(), contact_num.strip(), description.strip()]):
                st.error("❌ Please fill in all required fields (marked with *).")
            else:
                insert_business({
                    "user_id":        user["id"],
                    "business_name":  biz_name.strip(),
                    "description":    description.strip(),
                    "address":        address.strip(),
                    "contact_number": contact_num.strip(),
                    "category":       category,
                    "image_path":     image_url.strip(),
                    "is_priority":    1 if is_priority else 0,
                })
                st.success(
                    "✅ Business submitted for admin verification! "
                    "It will appear publicly once approved."
                )

    # ── Submit a Spot ──────────────────────────────────────────────────────
    with tab_spot:
        st.markdown("""
        <div style="background:#F0FDF4;border-left:4px solid #6EE7B7;border-radius:8px;
            padding:12px 16px;margin-bottom:16px;font-size:0.88rem;color:#065F46">
            Know a hidden gem in Bukidnon? Submit it here for admin review.
            Approved destinations appear on the public spot listings.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_spot_form"):
            st.markdown("#### 🏞️ Destination Information")
            col1, col2 = st.columns(2)
            with col1:
                name         = st.text_input("Spot Name *")
                category     = st.selectbox("Category *", DEST_CATEGORIES)
                municipality = st.text_input("Municipality *")
                entrance_fee = st.number_input("Entrance Fee (₱)", min_value=0.0, step=10.0)
                est_budget   = st.number_input("Estimated Total Budget (₱)", min_value=0.0, step=50.0)
            with col2:
                location  = st.text_input("Full Location / Address")
                image_url = st.text_input("Image URL (optional)")
                lat       = st.number_input("Latitude (GPS)", value=8.1575, format="%.4f")
                lng       = st.number_input("Longitude (GPS)", value=125.1278, format="%.4f")

            description = st.text_area("Description *", height=100)
            safety_tips = st.text_area("Safety Tips (optional)", height=80)

            submitted = st.form_submit_button(
                "Submit Spot for Review", type="primary", use_container_width=True
            )

        if submitted:
            if not all([name.strip(), municipality.strip(), description.strip()]):
                st.error("❌ Please fill in all required fields (marked with *).")
            else:
                insert_destination({
                    "name":          name.strip(),
                    "description":   description.strip(),
                    "location":      location.strip() or municipality.strip(),
                    "category":      category,
                    "entrance_fee":  entrance_fee,
                    "estimated_cost": est_budget,
                    "image_path":    image_url.strip(),
                    "latitude":      lat,
                    "longitude":     lng,
                    "safety_tips":   safety_tips.strip(),
                    "municipality":  municipality.strip(),
                    "is_approved":   0,   # requires admin approval
                })
                st.success(
                    "✅ Spot submitted for admin review! "
                    "It will appear publicly once approved."
                )

    # ── My Analytics ───────────────────────────────────────────────────────
    with tab_analytics:
        uid_filter = None if user["role"] == "admin" else user["id"]
        listings   = fetch_all_businesses(user_id=uid_filter)

        if not listings:
            st.info("No business listings to show analytics for.")
            return

        st.markdown("### 📊 Business Performance")

        total_views    = sum(b["views"]    for b in listings)
        total_clicks   = sum(b["clicks"]   for b in listings)
        total_inquiries= sum(b["inquiries"]for b in listings)

        k1, k2, k3 = st.columns(3)
        for col, icon, val, label in [
            (k1, "👁️", total_views,     "Total Views"),
            (k2, "🖱️", total_clicks,    "Total Clicks"),
            (k3, "📨", total_inquiries, "Total Inquiries"),
        ]:
            with col:
                st.markdown(f"""
                <div class="bk-kpi">
                    <div style="font-size:1.5rem">{icon}</div>
                    <div class="bk-kpi-value">{val}</div>
                    <div class="bk-kpi-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### Per-Listing Breakdown")

        for biz in listings:
            max_v = max((b["views"] for b in listings), default=1) or 1
            pct   = int(biz["views"] / max_v * 100)
            st.markdown(f"""
            <div style="margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;font-weight:500;font-size:0.9rem">
                    <span>{biz['business_name']}</span>
                    <span style="color:#6B7280">
                        👁️ {biz['views']} &nbsp; 🖱️ {biz['clicks']} &nbsp; 📨 {biz['inquiries']}
                    </span>
                </div>
                <div style="background:#E5E7EB;border-radius:100px;height:7px;margin-top:5px">
                    <div style="background:#2D6A4F;width:{pct}%;height:7px;border-radius:100px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
