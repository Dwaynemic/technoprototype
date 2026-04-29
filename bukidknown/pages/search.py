# =============================================================================
# pages/search.py  –  Search Destinations
# Keyword search + category and municipality filters.
# =============================================================================

import streamlit as st
from database.db import search_destinations, fetch_avg_rating


def _badge(cat):
    m = {"Waterfall":"bk-badge-waterfall","Nature":"bk-badge-nature",
         "Hiking":"bk-badge-hiking","Resort":"bk-badge-resort","Cultural":"bk-badge-cultural"}
    return m.get(cat, "bk-badge-nature")


def render():
    st.markdown("<div class='bk-section-title'>🔍 Search Destinations</div>", unsafe_allow_html=True)
    st.markdown("<div class='bk-section-sub'>Find your perfect Bukidnon adventure</div>", unsafe_allow_html=True)

    # Filters
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        default_q = st.session_state.pop("search_query", "")
        query = st.text_input(
            "Keyword",
            value=default_q,
            placeholder="e.g. waterfall, hiking, Malaybalay…",
            label_visibility="collapsed"
        )
    with col2:
        category = st.selectbox(
            "Category",
            ["All", "Waterfall", "Nature", "Hiking", "Resort", "Cultural"],
            label_visibility="collapsed"
        )
    with col3:
        municipality = st.selectbox(
            "Municipality",
            ["All","Malaybalay","Manolo Fortich","Quezon","Impasug-ong",
             "Lantapan","San Fernando","Cabanglasan","Talakag","Kitaotao"],
            label_visibility="collapsed"
        )

    results = search_destinations(query, category, municipality)
    st.markdown(f"**{len(results)} result(s)** for your search")
    st.divider()

    if not results:
        st.markdown("""
        <div style="text-align:center;padding:56px 20px;color:#6B7280">
            <div style="font-size:3rem">🔭</div>
            <div style="font-size:1.2rem;margin-top:10px">No destinations found.</div>
            <div style="margin-top:4px">Try a different keyword or remove filters.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    cols = st.columns(3)
    for i, spot in enumerate(results):
        r   = fetch_avg_rating(spot["id"])
        img = spot["image_path"] or "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600"
        fee = f"₱{spot['entrance_fee']:.0f}" if spot["entrance_fee"] > 0 else "Free"

        with cols[i % 3]:
            st.markdown(f"""
            <div class="bk-dest-card">
                <img class="bk-dest-img" src="{img}" alt="{spot['name']}"/>
                <div class="bk-dest-body">
                    <div class="bk-dest-name">{spot['name']}</div>
                    <div class="bk-dest-meta">📍 {spot['municipality']}</div>
                    <div class="bk-dest-fee">🎟️ {fee}</div>
                    <span class="bk-badge {_badge(spot['category'])}">{spot['category']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Details →", key=f"sr_{spot['id']}", use_container_width=True):
                st.session_state.selected_spot_id = spot["id"]
                st.session_state.page = "spot_detail"
                st.rerun()
