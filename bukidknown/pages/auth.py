# =============================================================================
# pages/auth.py  –  Login & Registration
#
# Login system with role-based access (tourist / business / admin).
# Password is SHA-256 hashed before storage.
# =============================================================================

import streamlit as st
from database.db import fetch_user_by_login, insert_user


def render():
    st.markdown("<div class='bk-section-title'>🔑 Login / Register</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Access your BukidKnown account</div>",
        unsafe_allow_html=True
    )

    tab_login, tab_reg = st.tabs(["🔑 Login", "📝 Register"])

    # ── LOGIN ──────────────────────────────────────────────────────────────
    with tab_login:
        col_center, _, _ = st.columns([2, 1, 1])
        with col_center:
            st.markdown("<div class='bk-form'>", unsafe_allow_html=True)
            st.markdown("### Welcome Back! 👋")
            st.markdown("Sign in to access bookings, reviews, and more.")
            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("login_form"):
                username = st.text_input("👤 Username")
                password = st.text_input("🔒 Password", type="password")
                login_btn = st.form_submit_button(
                    "Login →", type="primary", use_container_width=True
                )

            if login_btn:
                if not username.strip() or not password.strip():
                    st.error("Please enter your username and password.")
                else:
                    user = fetch_user_by_login(username.strip(), password)
                    if user:
                        st.session_state.user_id = user["id"]
                        st.session_state.page    = "home"
                        st.success(f"✅ Welcome back, {user['name'] or user['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")

            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # Demo credentials box
            st.markdown("""
            <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;
                padding:16px 20px;font-size:0.87rem">
                <strong>🧪 Demo Accounts</strong><br><br>
                🛠️ <strong>Admin</strong><br>
                &nbsp;&nbsp; Username: <code>admin</code> &nbsp;|&nbsp; Password: <code>admin123</code><br><br>
                👤 <strong>Tourist</strong><br>
                &nbsp;&nbsp; Username: <code>tourist1</code> &nbsp;|&nbsp; Password: <code>tourist123</code><br><br>
                🏪 <strong>Business Owner</strong><br>
                &nbsp;&nbsp; Username: <code>business1</code> &nbsp;|&nbsp; Password: <code>business123</code>
            </div>
            """, unsafe_allow_html=True)

    # ── REGISTER ───────────────────────────────────────────────────────────
    with tab_reg:
        col_center, _, _ = st.columns([2, 1, 1])
        with col_center:
            st.markdown("<div class='bk-form'>", unsafe_allow_html=True)
            st.markdown("### Create an Account 🎉")
            st.markdown("Join BukidKnown to book tours, write reviews, and more.")
            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("reg_form"):
                col1, col2 = st.columns(2)
                with col1:
                    full_name = st.text_input("👤 Full Name *")
                    username  = st.text_input("🪪 Username *")
                with col2:
                    email     = st.text_input("📧 Email *")
                    role      = st.selectbox(
                        "Account Type *",
                        ["tourist", "business"],
                        format_func=lambda r: "👤 Tourist" if r == "tourist" else "🏪 Business Owner"
                    )

                password = st.text_input("🔒 Password * (min 6 characters)", type="password")
                confirm  = st.text_input("🔒 Confirm Password *", type="password")

                reg_btn = st.form_submit_button(
                    "Create Account →", type="primary", use_container_width=True
                )

            if reg_btn:
                # Validation
                errors = []
                if not full_name.strip(): errors.append("Full name is required.")
                if not username.strip():  errors.append("Username is required.")
                if not email.strip():     errors.append("Email is required.")
                if len(password) < 6:     errors.append("Password must be at least 6 characters.")
                if password != confirm:   errors.append("Passwords do not match.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    ok, msg = insert_user(
                        username.strip(), password,
                        role, full_name.strip(), email.strip()
                    )
                    if ok:
                        user = fetch_user_by_login(username.strip(), password)
                        st.session_state.user_id = user["id"]
                        st.session_state.page    = "home"
                        st.success(f"✅ Account created! Welcome, {full_name}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

            st.markdown("</div>", unsafe_allow_html=True)

            # Role info
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div class="bk-safety">
                <strong>ℹ️ Account Types</strong><br>
                👤 <strong>Tourist</strong> — Browse spots, book tours, write reviews,
                use expense estimator, and chat support.<br>
                🏪 <strong>Business Owner</strong> — All tourist features plus:
                register your business, manage listings, submit new spots, and view analytics.
            </div>
            """, unsafe_allow_html=True)
