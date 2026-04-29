# =============================================================================
# pages/booking.py  –  Book Tour Services
#
# Workflow (from spec):
#   Tourist sends booking request → Agency checks guide availability
#   → Guide accepts or rejects → Status: Pending | Accepted | Rejected
# =============================================================================

import streamlit as st
from database.db import (
    insert_booking, fetch_all_bookings,
    fetch_all_destinations, fetch_user_by_id
)


STATUS_STYLE = {
    "Pending":  "bk-pill-pending",
    "Accepted": "bk-pill-accepted",
    "Rejected": "bk-pill-rejected",
}


def _require_login():
    uid  = st.session_state.get("user_id")
    user = fetch_user_by_id(uid) if uid else None
    if not user:
        st.warning("⚠️ Please login to access booking.")
        if st.button("🔑 Go to Login"):
            st.session_state.page = "auth"
            st.rerun()
        st.stop()
    return user


def render():
    user = _require_login()

    st.markdown("<div class='bk-section-title'>📅 Book a Tour</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>"
        "Submit a booking request to a tour agency. They will contact you to confirm availability."
        "</div>",
        unsafe_allow_html=True
    )

    tab_new, tab_my = st.tabs(["📋 New Booking", "🗂️ My Bookings"])

    # ── New Booking ────────────────────────────────────────────────────────
    with tab_new:
        all_spots  = fetch_all_destinations()
        spot_names = {s["name"]: s for s in all_spots}

        with st.form("booking_form"):
            st.markdown("#### 🏞️ Select Destination")
            spot_name = st.selectbox("Destination", list(spot_names.keys()))
            spot_obj  = spot_names[spot_name]

            # Show spot cost summary
            fee = spot_obj["entrance_fee"]
            st.markdown(f"""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;
                padding:10px 14px;margin-bottom:10px;font-size:0.87rem">
                📍 {spot_obj['municipality']} &nbsp;|&nbsp;
                🎟️ <strong>₱{fee:.0f}</strong> entrance &nbsp;|&nbsp;
                💰 Est. ₱{spot_obj['estimated_cost']:.0f} budget
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                tour_date   = st.date_input("📅 Preferred Tour Date")
                num_persons = st.number_input("👥 Number of Persons", 1, 100, 1)
            with col2:
                agency_name = st.text_input("🏢 Tour Agency", value="BukidKnown Tours")
                contact     = st.text_input("📞 Your Contact Number")

            notes = st.text_area("💬 Special Requests or Notes (optional)")

            submitted = st.form_submit_button(
                "📅 Submit Booking Request", type="primary", use_container_width=True
            )

        if submitted:
            if not contact.strip():
                st.error("❌ Contact number is required.")
            else:
                insert_booking({
                    "tourist_name":   user["name"] or user["username"],
                    "tourist_id":     user["id"],
                    "destination":    spot_name,
                    "destination_id": spot_obj["id"],
                    "agency_name":    agency_name,
                    "tour_date":      str(tour_date),
                    "num_persons":    num_persons,
                    "contact":        contact,
                    "notes":          notes,
                })
                st.success(
                    "✅ Booking request submitted successfully! "
                    "The agency will contact you via your provided number."
                )

        # Booking flow info
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#EEF2FF;border-radius:10px;padding:16px 20px;font-size:0.88rem;color:#3730A3">
            <strong>ℹ️ How the Booking Process Works</strong><br><br>
            1️⃣ &nbsp;Tourist submits a booking request<br>
            2️⃣ &nbsp;Agency receives the request and checks guide availability<br>
            3️⃣ &nbsp;Tour guide accepts or rejects the booking<br>
            4️⃣ &nbsp;Agency contacts you to confirm the booking<br>
            5️⃣ &nbsp;Status updates to <strong>Accepted</strong> or <strong>Rejected</strong>
        </div>
        """, unsafe_allow_html=True)

    # ── My Bookings ────────────────────────────────────────────────────────
    with tab_my:
        bookings = fetch_all_bookings(user_id=user["id"])

        if not bookings:
            st.info("You have no bookings yet. Submit your first booking above!")
            return

        st.markdown(f"**{len(bookings)} booking(s) found**")

        for bk in bookings:
            pill_cls = STATUS_STYLE.get(bk["status"], "bk-pill-pending")
            st.markdown(f"""
            <div class="bk-form" style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                        <strong style="font-size:1rem">{bk['destination']}</strong><br>
                        <span style="font-size:0.82rem;color:#6B7280">
                            🏢 {bk['agency_name']} &nbsp;|&nbsp;
                            📅 {bk['tour_date']} &nbsp;|&nbsp;
                            👥 {bk['num_persons']} person(s) &nbsp;|&nbsp;
                            📞 {bk['contact']}
                        </span>
                        {f"<br><span style='font-size:0.82rem;color:#374151'>💬 {bk['notes']}</span>" if bk.get('notes') else ''}
                    </div>
                    <span class="bk-pill {pill_cls}">{bk['status']}</span>
                </div>
                <div style="font-size:0.74rem;color:#9CA3AF;margin-top:6px">
                    Submitted: {bk['created_at'][:16]}
                </div>
            </div>
            """, unsafe_allow_html=True)
