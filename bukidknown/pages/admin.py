# =============================================================================
# pages/admin.py  –  Admin Panel
#
# Admin Features (from spec):
#   1. Approve Business Listings
#   2. Manage Destination Data
#   3. Verify Businesses
#   4. Monitor Platform Activity
#   + Manage Bookings (accept / reject)
#   + Send Notifications
# =============================================================================

import streamlit as st
from database.db import (
    fetch_all_destinations, approve_destination, delete_destination,
    fetch_all_businesses, verify_business, delete_business,
    fetch_all_bookings, update_booking_status,
    fetch_all_users, insert_notification,
    fetch_user_by_id, mark_all_read
)


def _require_admin():
    uid  = st.session_state.get("user_id")
    user = fetch_user_by_id(uid) if uid else None
    if not user or user["role"] != "admin":
        st.error("🚫 Admin access only.")
        st.stop()
    return user


def render():
    user = _require_admin()
    mark_all_read(user["id"])   # clear notification badge when admin opens panel

    st.markdown("<div class='bk-section-title'>🛠️ Admin Panel</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Approve content, manage platform data, and monitor activity</div>",
        unsafe_allow_html=True
    )

    tabs = st.tabs([
        "🏞️ Destinations",
        "🏪 Businesses",
        "📅 Bookings",
        "👤 Users",
        "🔔 Notifications",
    ])

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 1 – DESTINATIONS
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[0]:
        all_dests   = fetch_all_destinations(approved_only=False)
        pending     = [d for d in all_dests if not d["is_approved"]]
        approved    = [d for d in all_dests if  d["is_approved"]]

        # ── Pending approvals ──────────────────────────────────────────────
        st.markdown(f"### ⏳ Pending Approval ({len(pending)})")
        if not pending:
            st.success("✅ All destinations are approved. No pending items.")
        else:
            for d in pending:
                with st.container():
                    col1, col2, col3 = st.columns([5, 1, 1])
                    with col1:
                        st.markdown(
                            f"**{d['name']}** — 🗂️ {d['category']} | "
                            f"📍 {d['municipality']}"
                        )
                        if d.get("description"):
                            st.caption(d["description"][:130] + "…")
                    with col2:
                        if st.button("✅ Approve", key=f"appr_d_{d['id']}", use_container_width=True):
                            approve_destination(d["id"])
                            st.success(f"Approved: {d['name']}")
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_d_{d['id']}", use_container_width=True):
                            delete_destination(d["id"])
                            st.warning(f"Deleted: {d['name']}")
                            st.rerun()
                    st.divider()

        # ── Approved destinations ──────────────────────────────────────────
        st.markdown(f"### ✅ Approved Destinations ({len(approved)})")
        for d in approved:
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(
                    f"**{d['name']}** — 🗂️ {d['category']} | "
                    f"📍 {d['municipality']} | 🎟️ ₱{d['entrance_fee']:.0f}"
                )
            with col2:
                if st.button("🗑️", key=f"del_appr_{d['id']}", use_container_width=True,
                             help="Delete this destination"):
                    delete_destination(d["id"])
                    st.rerun()

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 2 – BUSINESSES
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[1]:
        all_biz     = fetch_all_businesses()
        pending_biz = [b for b in all_biz if not b["is_verified"]]
        verified_biz= [b for b in all_biz if  b["is_verified"]]

        # ── Pending verification ───────────────────────────────────────────
        st.markdown(f"### ⏳ Pending Verification ({len(pending_biz)})")
        if not pending_biz:
            st.success("✅ All businesses are verified.")
        else:
            for b in pending_biz:
                col1, col2, col3 = st.columns([5, 1, 1])
                with col1:
                    st.markdown(
                        f"**{b['business_name']}** — 🗂️ {b['category']} | "
                        f"📍 {b['address']} | 📞 {b['contact_number']}"
                    )
                    if b.get("description"):
                        st.caption(b["description"][:120] + "…")
                with col2:
                    if st.button("✅ Verify", key=f"ver_b_{b['id']}", use_container_width=True):
                        verify_business(b["id"])
                        # Notify business owner
                        insert_notification(
                            b["user_id"],
                            "Business Verified! 🎉",
                            f"Your business '{b['business_name']}' has been verified "
                            f"and is now publicly visible on BukidKnown."
                        )
                        st.success(f"Verified: {b['business_name']}")
                        st.rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"del_b_{b['id']}", use_container_width=True):
                        delete_business(b["id"])
                        st.warning(f"Deleted: {b['business_name']}")
                        st.rerun()
                st.divider()

        # ── Verified businesses ────────────────────────────────────────────
        st.markdown(f"### ✅ Verified Businesses ({len(verified_biz)})")
        for b in verified_biz:
            col1, col2 = st.columns([6, 1])
            with col1:
                priority = " ⭐ Priority" if b["is_priority"] else ""
                st.markdown(
                    f"**{b['business_name']}**{priority} — "
                    f"🗂️ {b['category']} | 📍 {b['address']}"
                )
            with col2:
                if st.button("🗑️", key=f"del_ver_{b['id']}", use_container_width=True):
                    delete_business(b["id"])
                    st.rerun()

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 3 – BOOKINGS
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[2]:
        bookings = fetch_all_bookings()
        pending_bk  = [b for b in bookings if b["status"] == "Pending"]
        other_bk    = [b for b in bookings if b["status"] != "Pending"]

        st.markdown(f"### ⏳ Pending Bookings ({len(pending_bk)})")
        if not pending_bk:
            st.success("✅ No pending bookings.")

        for bk in pending_bk:
            with st.container():
                col1, col2, col3 = st.columns([5, 1, 1])
                with col1:
                    st.markdown(
                        f"**{bk['destination']}** — 👤 {bk['tourist_name']} | "
                        f"📅 {bk['tour_date']} | 👥 {bk['num_persons']} pax | "
                        f"📞 {bk['contact']}"
                    )
                    if bk.get("notes"):
                        st.caption(f"💬 {bk['notes']}")
                with col2:
                    if st.button("✅ Accept", key=f"acc_bk_{bk['id']}", use_container_width=True):
                        update_booking_status(bk["id"], "Accepted")
                        insert_notification(
                            bk["tourist_id"],
                            "Booking Accepted! 🎉",
                            f"Your booking for {bk['destination']} on {bk['tour_date']} "
                            f"has been accepted by {bk['agency_name']}."
                        )
                        st.success("Booking accepted!")
                        st.rerun()
                with col3:
                    if st.button("❌ Reject", key=f"rej_bk_{bk['id']}", use_container_width=True):
                        update_booking_status(bk["id"], "Rejected")
                        insert_notification(
                            bk["tourist_id"],
                            "Booking Update",
                            f"Unfortunately, your booking for {bk['destination']} on "
                            f"{bk['tour_date']} could not be accommodated. Please try another date."
                        )
                        st.warning("Booking rejected.")
                        st.rerun()
                st.divider()

        # All other bookings
        st.markdown(f"### 📋 All Bookings ({len(bookings)})")
        STATUS_COLORS = {
            "Pending":  "bk-pill-pending",
            "Accepted": "bk-pill-accepted",
            "Rejected": "bk-pill-rejected",
        }
        for bk in bookings:
            pill = STATUS_COLORS.get(bk["status"], "bk-pill-pending")
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(
                    f"**{bk['destination']}** — 👤 {bk['tourist_name']} | "
                    f"📅 {bk['tour_date']} | 🏢 {bk['agency_name']}"
                )
            with col2:
                st.markdown(
                    f"<span class='bk-pill {pill}'>{bk['status']}</span>",
                    unsafe_allow_html=True
                )
            with col3:
                new_status = st.selectbox(
                    "Status",
                    ["Pending", "Accepted", "Rejected"],
                    index=["Pending", "Accepted", "Rejected"].index(bk["status"]),
                    key=f"sel_bk_{bk['id']}",
                    label_visibility="collapsed"
                )
                if st.button("Update", key=f"upd_bk_{bk['id']}", use_container_width=True):
                    update_booking_status(bk["id"], new_status)
                    st.rerun()

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 4 – USERS
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[3]:
        users = fetch_all_users()
        st.markdown(f"### 👤 All Users ({len(users)})")

        role_counts = {}
        for u in users:
            role_counts[u["role"]] = role_counts.get(u["role"], 0) + 1

        r1, r2, r3 = st.columns(3)
        for col, role, icon in [
            (r1, "tourist",  "👤"),
            (r2, "business", "🏪"),
            (r3, "admin",    "🛠️"),
        ]:
            with col:
                count = role_counts.get(role, 0)
                st.markdown(f"""
                <div class="bk-stat">
                    <div class="bk-stat-icon">{icon}</div>
                    <div class="bk-stat-value">{count}</div>
                    <div class="bk-stat-label">{role.capitalize()}s</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        for u in users:
            role_icon = {"admin": "🛠️", "business": "🏪", "tourist": "👤"}.get(u["role"], "👤")
            st.markdown(
                f"{role_icon} **{u['name'] or u['username']}** "
                f"(`{u['username']}`) — `{u['role']}` — {u['email']} — "
                f"Joined: {u['created_at'][:10]}"
            )

    # ═══════════════════════════════════════════════════════════════════════
    # TAB 5 – NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════════════════
    with tabs[4]:
        st.markdown("### 🔔 Send a Notification")

        users      = fetch_all_users()
        non_admins = [u for u in users if u["role"] != "admin"]
        user_opts  = {
            f"{u['name'] or u['username']} ({u['role']})": u["id"]
            for u in non_admins
        }
        # Also allow broadcast
        user_opts  = {"📢 All Users (Broadcast)": "all", **user_opts}

        with st.form("notif_form"):
            selected_user = st.selectbox("Send To", list(user_opts.keys()))
            notif_title   = st.text_input("Notification Title *")
            notif_msg     = st.text_area("Message *")
            send_btn      = st.form_submit_button("Send Notification 🔔", type="primary")

        if send_btn:
            if not notif_title.strip() or not notif_msg.strip():
                st.error("Title and message are required.")
            else:
                target = user_opts[selected_user]
                if target == "all":
                    for u in non_admins:
                        insert_notification(u["id"], notif_title.strip(), notif_msg.strip())
                    st.success(f"✅ Broadcast sent to {len(non_admins)} users!")
                else:
                    insert_notification(target, notif_title.strip(), notif_msg.strip())
                    st.success("✅ Notification sent!")
