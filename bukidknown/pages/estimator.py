# =============================================================================
# pages/estimator.py  –  Expense Estimator
#
# Formula (from spec):
#   Total Cost = (Entrance Fee × Number of Persons)
#              + Transportation Cost
#              + Food Budget
#
# Transportation Types:
#   Motorcycle = ₱200
#   Van        = ₱1,000
#   Bus        = ₱500
# =============================================================================

import streamlit as st
from database.db import fetch_all_destinations, fetch_destination_by_id


TRANSPORT_COSTS = {
    "Motorcycle (₱200)": 200,
    "Bus (₱500)":        500,
    "Van (₱1,000)":      1000,
}


def render():
    st.markdown("<div class='bk-section-title'>💰 Expense Estimator</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>"
        "Plan your trip budget before you go."
        "</div>",
        unsafe_allow_html=True
    )

    all_spots  = fetch_all_destinations()
    spot_names = {s["name"]: s for s in all_spots}

    # Pre-select spot if coming from spot detail page
    preselect = st.session_state.pop("estimator_spot_id", None)
    default_idx = 0
    if preselect:
        names_list = list(spot_names.keys())
        spot_obj   = fetch_destination_by_id(preselect)
        if spot_obj and spot_obj["name"] in names_list:
            default_idx = names_list.index(spot_obj["name"])

    st.markdown("<div class='bk-form'>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🏞️ Destination")
        spot_name = st.selectbox(
            "Select Destination",
            list(spot_names.keys()),
            index=default_idx
        )
        selected = spot_names[spot_name]

        # Show destination info
        fee = selected["entrance_fee"]
        st.markdown(f"""
        <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;
            padding:12px 14px;margin:8px 0;font-size:0.88rem">
            📍 {selected['municipality']} &nbsp;|&nbsp;
            🎟️ <strong>₱{fee:.0f}</strong> entrance &nbsp;|&nbsp;
            💰 Est. ₱{selected['estimated_cost']:.0f} total
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 👥 Group Size")
        num_persons = st.number_input(
            "Number of Persons",
            min_value=1, max_value=200, value=1, step=1
        )

    with col_right:
        st.markdown("#### 🚌 Transportation")
        transport_label = st.selectbox(
            "Transportation Type",
            list(TRANSPORT_COSTS.keys())
        )
        transport_cost = TRANSPORT_COSTS[transport_label]

        st.markdown("#### 🍽️ Food Budget")
        food_budget = st.number_input(
            "Food Budget per Group (₱)",
            min_value=0, max_value=50000, value=500, step=50
        )

        st.markdown("#### ➕ Other Expenses")
        other = st.number_input(
            "Other / Miscellaneous (₱)",
            min_value=0, max_value=50000, value=0, step=50
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Calculation ──────────────────────────────────────────────────────
    entrance_total = fee * num_persons
    grand_total    = entrance_total + transport_cost + food_budget + other

    st.markdown("### 📊 Estimated Trip Cost")
    st.markdown(f"""
    <div class="bk-estimate-box">
        <div class="bk-estimate-row">
            <span>🏞️ Destination</span>
            <strong>{spot_name}</strong>
        </div>
        <div class="bk-estimate-row">
            <span>👥 Group Size</span>
            <strong>{num_persons} person(s)</strong>
        </div>
        <div class="bk-estimate-row">
            <span>🎟️ Entrance Fee (₱{fee:.0f} × {num_persons})</span>
            <strong>₱{entrance_total:,.2f}</strong>
        </div>
        <div class="bk-estimate-row">
            <span>🚌 Transportation ({transport_label})</span>
            <strong>₱{transport_cost:,.2f}</strong>
        </div>
        <div class="bk-estimate-row">
            <span>🍽️ Food Budget</span>
            <strong>₱{food_budget:,.2f}</strong>
        </div>
        <div class="bk-estimate-row">
            <span>➕ Other Expenses</span>
            <strong>₱{other:,.2f}</strong>
        </div>
        <div style="margin-top:10px;padding-top:10px;border-top:2px solid #6EE7B7">
            <div style="font-size:0.85rem;color:#065F46;font-weight:600">💰 ESTIMATED TOTAL COST</div>
            <div class="bk-estimate-total">₱{grand_total:,.2f}</div>
            <div style="font-size:0.8rem;color:#6B7280;margin-top:4px">
                ≈ ₱{grand_total/max(num_persons,1):,.2f} per person
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tips ─────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="bk-safety">
        <strong>💡 Budget Tips</strong><br>
        • Bring extra cash (₱200–500) for unexpected expenses such as porters, parking, or emergency supplies.<br>
        • Book transportation in advance, especially on weekends — rates may vary.<br>
        • Pack your own food for remote destinations to save on food expenses.<br>
        • Group tours with 10+ persons often get discounted entrance fees.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📅 Book This Trip", type="primary", use_container_width=True):
            st.session_state.page = "booking"
            st.rerun()
    with c2:
        if st.button("🏞️ Back to Spots", use_container_width=True):
            st.session_state.page = "spots"
            st.rerun()
