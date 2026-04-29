# =============================================================================
# pages/analytics.py  –  Admin Analytics Dashboard
#
# Displays platform-wide KPIs, top destinations, category breakdown,
# business performance, and booking trends using Streamlit charts.
# =============================================================================

import streamlit as st
import pandas as pd
from database.db import fetch_platform_analytics, fetch_user_by_id


def _require_admin():
    uid  = st.session_state.get("user_id")
    user = fetch_user_by_id(uid) if uid else None
    if not user or user["role"] != "admin":
        st.error("🚫 Admin access only.")
        st.stop()
    return user


def render():
    _require_admin()

    st.markdown("<div class='bk-section-title'>📈 Analytics Dashboard</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Platform-wide performance metrics and insights</div>",
        unsafe_allow_html=True
    )

    data = fetch_platform_analytics()

    # ── Row 1: KPI Cards ───────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "👤", data["total_users"],        "Total Users"),
        (k2, "🏞️", data["total_destinations"], "Active Spots"),
        (k3, "📅", data["total_bookings"],      "Total Bookings"),
        (k4, "⭐", f"{data['avg_rating']}★",    "Avg. Rating"),
    ]
    for col, icon, val, label in kpis:
        with col:
            st.markdown(f"""
            <div class="bk-kpi">
                <div style="font-size:1.4rem">{icon}</div>
                <div class="bk-kpi-value">{val}</div>
                <div class="bk-kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Pending Items ───────────────────────────────────────────────
    st.markdown("### ⏳ Pending Items")
    p1, p2, p3 = st.columns(3)
    pending_items = [
        (p1, "🏞️", data["pending_dests"],      "Spots Pending Approval"),
        (p2, "🏪", data["pending_businesses"],  "Businesses Pending Verification"),
        (p3, "📅", data["pending_bookings"],    "Bookings Pending Review"),
    ]
    for col, icon, val, label in pending_items:
        color = "#EF4444" if val > 0 else "#10B981"
        with col:
            st.markdown(f"""
            <div style="background:{color}15;border:1px solid {color}40;
                border-radius:10px;padding:16px;text-align:center">
                <div style="font-size:1.5rem">{icon}</div>
                <div style="font-family:'Playfair Display',serif;font-size:2rem;
                    font-weight:900;color:{color}">{val}</div>
                <div style="font-size:0.78rem;color:#6B7280;margin-top:2px">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Charts ─────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        # Destinations by category (bar chart)
        st.markdown("### 🗂️ Destinations by Category")
        cat_data = data["dests_by_category"]
        if cat_data:
            df_cat = pd.DataFrame(cat_data)
            df_cat.columns = ["Category", "Count"]
            df_cat = df_cat.set_index("Category")
            st.bar_chart(df_cat, use_container_width=True, height=250)
        else:
            st.info("No destination data yet.")

    with col_right:
        # Bookings by status (horizontal bar)
        st.markdown("### 📅 Bookings by Status")
        bk_status = data["bookings_by_status"]
        if bk_status:
            df_bk = pd.DataFrame(bk_status)
            df_bk.columns = ["Status", "Count"]
            df_bk = df_bk.set_index("Status")
            st.bar_chart(df_bk, use_container_width=True, height=250)
        else:
            st.info("No booking data yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Destinations ───────────────────────────────────────────────────
    st.markdown("### 🏆 Most Booked Destinations")
    top_dests = data["top_destinations"]
    if top_dests:
        max_cnt = max(d["cnt"] for d in top_dests) or 1
        for d in top_dests:
            pct = int(d["cnt"] / max_cnt * 100)
            st.markdown(f"""
            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;
                    font-weight:500;font-size:0.9rem;margin-bottom:4px">
                    <span>🏞️ {d['destination']}</span>
                    <span style="color:#2D6A4F;font-weight:700">{d['cnt']} booking(s)</span>
                </div>
                <div style="background:#E5E7EB;border-radius:100px;height:8px">
                    <div style="background:#2D6A4F;width:{pct}%;
                        height:8px;border-radius:100px"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No booking data yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Businesses ─────────────────────────────────────────────────────
    st.markdown("### 🏪 Business Engagement (Top 5)")
    top_biz = data["top_businesses"]
    if top_biz:
        df_biz = pd.DataFrame(top_biz)
        df_biz.columns = ["Business", "Views", "Clicks", "Inquiries"]
        df_biz = df_biz.set_index("Business")
        st.dataframe(df_biz, use_container_width=True)
    else:
        st.info("No business engagement data yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── User Breakdown ─────────────────────────────────────────────────────
    st.markdown("### 👥 User Breakdown")
    u1, u2, u3 = st.columns(3)
    user_breakdown = [
        (u1, "👤", data["total_tourists"],     "Tourists"),
        (u2, "🏪", data["total_businesses_u"], "Business Owners"),
        (u3, "🛠️", data["total_users"] - data["total_tourists"] - data["total_businesses_u"], "Admins"),
    ]
    for col, icon, val, label in user_breakdown:
        with col:
            st.markdown(f"""
            <div class="bk-stat">
                <div class="bk-stat-icon">{icon}</div>
                <div class="bk-stat-value">{val}</div>
                <div class="bk-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
