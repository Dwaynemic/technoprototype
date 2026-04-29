# =============================================================================
# pages/chat.py  –  Chat Support
# Tourist view: chat with auto-replies + send to admin inbox.
# Admin view: threaded inbox with ability to reply.
# =============================================================================

import streamlit as st
from database.db import (
    insert_message, fetch_messages,
    fetch_all_chat_threads, fetch_user_by_id
)


# ── Auto-reply keyword mapping ──────────────────────────────────────────────
CANNED_REPLIES = {
    ("book", "reserve", "schedule", "tour"):
        "To book a tour, go to 📅 Book a Tour in the navigation menu. "
        "Fill in the destination, date, and your contact details. "
        "The agency will reach out to confirm! 🙏",

    ("spot", "destination", "place", "visit", "where"):
        "You can browse all tourist spots in 🏞️ Tourist Spots. "
        "Use 🔍 Search to filter by category or municipality. "
        "We currently feature 10 curated destinations across Bukidnon!",

    ("cost", "fee", "price", "budget", "expense", "money"):
        "Use our 💰 Expense Estimator to calculate your trip cost! "
        "It calculates entrance fees × persons + transportation + food. "
        "Transportation options: Motorcycle ₱200, Bus ₱500, Van ₱1,000.",

    ("safe", "danger", "security", "risk"):
        "Bukidnon is generally safe for tourists. Always register at the "
        "local tourism office, hire DENR-accredited guides for protected areas, "
        "and check weather conditions before trekking. 🛡️",

    ("business", "list", "register", "promote", "shop"):
        "To list your business, create an account with the 'Business' role, "
        "then visit 🏪 Business Dashboard. Submit your details and our admin "
        "will verify and publish your listing!",

    ("nearby", "close", "distance", "km"):
        "Use 📍 Nearby Spots to find destinations close to you! "
        "Just select your starting location and set a search radius.",
}


def _auto_reply(msg: str) -> str:
    msg_lower = msg.lower()
    for keywords, reply in CANNED_REPLIES.items():
        if any(kw in msg_lower for kw in keywords):
            return reply
    return (
        "Thank you for reaching out! 🙏 "
        "A support team member will respond to your message shortly. "
        "In the meantime, feel free to explore our features using the sidebar navigation."
    )


# ── Render ──────────────────────────────────────────────────────────────────

def render():
    uid  = st.session_state.get("user_id")
    user = fetch_user_by_id(uid) if uid else None

    st.markdown("<div class='bk-section-title'>💬 Chat Support</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='bk-section-sub'>Get help from our tourism support team</div>",
        unsafe_allow_html=True
    )

    if not user:
        st.info("Please login to use Chat Support.")
        if st.button("🔑 Login"):
            st.session_state.page = "auth"
            st.rerun()
        return

    if user["role"] == "admin":
        _admin_chat_view()
    else:
        _tourist_chat_view(user)


def _tourist_chat_view(user):
    # Quick reply buttons
    st.markdown("**💡 Quick Questions — tap to ask instantly:**")
    q_cols = st.columns(3)
    quick_qs = [
        "How do I book a tour?",
        "What are the best spots?",
        "How is trip cost calculated?",
        "Is Bukidnon safe to travel?",
        "How do I list my business?",
        "Find spots near me?",
    ]
    for i, q in enumerate(quick_qs):
        with q_cols[i % 3]:
            if st.button(q, key=f"qq_{i}", use_container_width=True):
                insert_message(user["id"], "user", q)
                auto = _auto_reply(q)
                insert_message(user["id"], "support", auto)
                st.rerun()

    st.divider()
    st.markdown("**💬 Conversation**")

    messages = fetch_messages(user["id"])
    if not messages:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#6B7280">
            <div style="font-size:2.5rem">💬</div>
            <div style="font-size:1rem;margin-top:10px">
                No messages yet. Ask us anything using the quick questions above
                or type your message below!
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for m in messages:
            if m["sender"] == "user":
                st.markdown(f"""
                <div class="bk-chat-wrap">
                    <div style="text-align:right">
                        <span class="bk-chat-bubble bk-chat-user">{m['message']}</span>
                        <div class="bk-chat-ts" style="text-align:right">{m['created_at'][11:16]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bk-chat-wrap">
                    <div style="text-align:left">
                        <div style="font-size:0.73rem;color:#6B7280;margin-bottom:2px">
                            🏔️ BukidKnown Support
                        </div>
                        <span class="bk-chat-bubble bk-chat-support">{m['message']}</span>
                        <div class="bk-chat-ts">{m['created_at'][11:16]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Message input
    with st.form("chat_form", clear_on_submit=True):
        col_msg, col_send = st.columns([5, 1])
        with col_msg:
            text = st.text_input("Type your message…", label_visibility="collapsed")
        with col_send:
            sent = st.form_submit_button("Send 📤", use_container_width=True)
        if sent and text.strip():
            insert_message(user["id"], "user", text.strip())
            auto = _auto_reply(text.strip())
            insert_message(user["id"], "support", auto)
            st.rerun()


def _admin_chat_view():
    st.markdown("### 📨 All Support Threads")
    threads = fetch_all_chat_threads()

    if not threads:
        st.info("No chat threads yet.")
        return

    for t in threads:
        with st.expander(f"👤 {t['name']} (@{t['username']}) — last: {str(t['last_msg'])[:16]}"):
            msgs = fetch_messages(t["user_id"])
            for m in msgs[-15:]:
                label = f"👤 {t['name']}" if m["sender"] == "user" else "🏔️ Support"
                if m["sender"] == "user":
                    st.info(f"**{label}** `{m['created_at'][11:16]}`\n\n{m['message']}")
                else:
                    st.success(f"**{label}** `{m['created_at'][11:16]}`\n\n{m['message']}")

            with st.form(f"admin_reply_{t['user_id']}"):
                reply = st.text_input("Type a reply…", label_visibility="collapsed",
                                      placeholder="Type reply and press Send…")
                if st.form_submit_button("Send Reply 📤", use_container_width=True):
                    if reply.strip():
                        insert_message(t["user_id"], "support", reply.strip())
                        st.success("Reply sent!"); st.rerun()
