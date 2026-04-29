# =============================================================================
# main.py  –  BukidKnown Tourism Web Platform
# Entry point: configures the page, loads CSS, renders the sidebar navigation,
# and routes to the correct page module.
# =============================================================================

import streamlit as st
from database.db import init_db, fetch_user_by_id, count_unread


# ── Page configuration (must be first Streamlit call) ─────────────────────
st.set_page_config(
    page_title="BukidKnown – Discover Bukidnon",
    page_icon="https://scontent.fcgy3-2.fna.fbcdn.net/v/t1.15752-9/683155885_2053233712272604_5427929101685615630_n.png?_nc_cat=100&ccb=1-7&_nc_sid=9f807c&_nc_eui2=AeGO-V5xkyKmTuvz-5MtCB8p4wxRxNcD7objDFHE1wPuhukmcDZfmwJyHpQLrhesH1luSv-oX7of7v-eYjmW_-i2&_nc_ohc=QEA_x5q_eSkQ7kNvwHA8Pq5&_nc_oc=Adowb0wX2XiywU3ctQhGPON5Avq8OjqjM-y5oCo8AbhkqPDcqcn414aoz3v1vziUXf4&_nc_zt=23&_nc_ht=scontent.fcgy3-2.fna&_nc_ss=7b2a8&oh=03_Q7cD5AHHgO76T9POsEBO1knPBKHcp4EhYaGYKtci27f8_y9vUA&oe=6A198263",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_css():
    try:
        with open("assets/style.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found (assets/style.css)")

load_css()

st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)



# ── Initialize database on first run ──────────────────────────────────────
init_db()

# ── Inject global stylesheet ──────────────────────────────────────────────
with open("assets/style.css", encoding="utf-8") as _f:
    st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)


# ── Helper: get current logged-in user ────────────────────────────────────
def _current_user():
    uid = st.session_state.get("user_id")
    return fetch_user_by_id(uid) if uid else None


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="bk-logo">
        <img src="https://scontent.fcgy3-2.fna.fbcdn.net/v/t1.15752-9/683155885_2053233712272604_5427929101685615630_n.png?_nc_cat=100&ccb=1-7&_nc_sid=9f807c&_nc_eui2=AeGO-V5xkyKmTuvz-5MtCB8p4wxRxNcD7objDFHE1wPuhukmcDZfmwJyHpQLrhesH1luSv-oX7of7v-eYjmW_-i2&_nc_ohc=QEA_x5q_eSkQ7kNvwHA8Pq5&_nc_oc=Adowb0wX2XiywU3ctQhGPON5Avq8OjqjM-y5oCo8AbhkqPDcqcn414aoz3v1vziUXf4&_nc_zt=23&_nc_ht=scontent.fcgy3-2.fna&_nc_ss=7b2a8&oh=03_Q7cD5AHHgO76T9POsEBO1knPBKHcp4EhYaGYKtci27f8_y9vUA&oe=6A198263" class="bk-logo-img">
    </div>
    """, unsafe_allow_html=True)

    user = _current_user()

    # User greeting + role badge
    if user:
        role_icons = {"admin": "🛠️", "business": "🏪", "tourist": "👤"}
        icon = role_icons.get(user["role"], "👤")
        unread = count_unread(user["id"])
        notif_badge = f"  🔔 {unread}" if unread > 0 else ""
        st.markdown(
            f"**{icon} {user['name'] or user['username']}**  "
            f"`{user['role']}`{notif_badge}"
        )
        st.markdown("---")

    # ── Navigation ──────────────────────────────────────────────────────
    st.markdown("**🧭 Navigation**")

    # Pages available to everyone (tourist + guest)
    public_pages = [
        ("🏠", "Home",              "home"),
        ("🏞️", "Tourist Spots",     "spots"),
        ("🔍", "Search",            "search"),
        ("📍", "Nearby Spots",      "nearby"),
        ("💰", "Expense Estimator", "estimator"),
        ("🏪", "Nearby Businesses", "businesses"),
        ("📅", "Book a Tour",       "booking"),
        ("⭐", "Reviews",           "reviews"),
        ("💬", "Chat Support",      "chat"),
    ]

    # Business-only pages
    business_pages = [
        ("📊", "Business Dashboard", "biz_dashboard"),
    ]

    # Admin-only pages
    admin_pages = [
        ("🛠️", "Admin Panel",      "admin"),
        ("📈", "Analytics",        "analytics"),
    ]

    if "page" not in st.session_state:
        st.session_state.page = "home"

    def _nav_btn(emoji, label, key):
        full_label = f"{emoji} {label}"
        if st.button(full_label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    for emoji, label, key in public_pages:
        _nav_btn(emoji, label, key)

    if user and user["role"] in ("business", "admin"):
        st.markdown("---")
        st.markdown("**🏪 Business**")
        for emoji, label, key in business_pages:
            _nav_btn(emoji, label, key)

    if user and user["role"] == "admin":
        st.markdown("---")
        st.markdown("**🛠️ Admin**")
        for emoji, label, key in admin_pages:
            _nav_btn(emoji, label, key)

    st.markdown("---")

    # Auth buttons
    if user:
        if st.button("🔔 Notifications", key="nav_notif", use_container_width=True):
            st.session_state.page = "notifications"
            st.rerun()
        if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    else:
        if st.button("🔑 Login / Register", key="nav_auth", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem;color:rgba(255,255,255,0.4);text-align:center'>"
        "BukidKnown v1.0 · Northern Mindanao</div>",
        unsafe_allow_html=True
    )


# ── Page Router ────────────────────────────────────────────────────────────
_page = st.session_state.get("page", "home")

if _page == "home":
    from pages.home import render; render()

elif _page == "spots":
    from pages.spots import render; render()

elif _page == "spot_detail":
    from pages.spot_detail import render; render()

elif _page == "search":
    from pages.search import render; render()

elif _page == "nearby":
    from pages.nearby import render; render()

elif _page == "estimator":
    from pages.estimator import render; render()

elif _page == "businesses":
    from pages.businesses import render; render()

elif _page == "booking":
    from pages.booking import render; render()

elif _page == "reviews":
    from pages.reviews import render; render()

elif _page == "chat":
    from pages.chat import render; render()

elif _page == "biz_dashboard":
    from pages.biz_dashboard import render; render()

elif _page == "admin":
    from pages.admin import render; render()

elif _page == "analytics":
    from pages.analytics import render; render()

elif _page == "auth":
    from pages.auth import render; render()

elif _page == "notifications":
    from pages.notifications import render; render()

else:
    st.error(f"Page '{_page}' not found.")
    st.session_state.page = "home"
    st.rerun()
