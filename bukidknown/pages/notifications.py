# =============================================================================
# pages/notifications.py  –  User Notifications
# =============================================================================

import streamlit as st
from database.db import (
    fetch_notifications, mark_all_read, fetch_user_by_id
)


def render():
    uid  = st.session_state.get("user_id")
    user = fetch_user_by_id(uid) if uid else None

    if not user:
        st.warning("Please login to view notifications.")
        if st.button("🔑 Login"):
            st.session_state.page = "auth"
            st.rerun()
        return

    st.markdown("<div class='bk-section-title'>🔔 Notifications</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Stay updated on your bookings and account activity</div>",
        unsafe_allow_html=True
    )

    notifications = fetch_notifications(user["id"])
    unread_count  = sum(1 for n in notifications if not n["is_read"])

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"**{len(notifications)} notification(s)** — {unread_count} unread")
    with col2:
        if unread_count > 0:
            if st.button("✅ Mark All Read", use_container_width=True):
                mark_all_read(user["id"])
                st.rerun()

    st.divider()

    if not notifications:
        st.markdown("""
        <div style="text-align:center;padding:50px 20px;color:#6B7280">
            <div style="font-size:2.5rem">🔔</div>
            <div style="font-size:1rem;margin-top:10px">No notifications yet.</div>
            <div style="margin-top:4px">We'll notify you about bookings and updates here.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for notif in notifications:
        unread_class = "bk-notif-unread" if not notif["is_read"] else ""
        dot = "🔵 " if not notif["is_read"] else ""
        st.markdown(f"""
        <div class="bk-notif {unread_class}">
            <div class="bk-notif-title">{dot}{notif['title']}</div>
            <div class="bk-notif-msg">{notif['message']}</div>
            <div style="font-size:0.72rem;color:#9CA3AF;margin-top:4px">
                {notif['created_at'][:16]}
            </div>
        </div>
        """, unsafe_allow_html=True)
