import streamlit as st
from auth import page_login, page_signup
from page_user import page_user
from page_courrier import page_courrier

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Droplock", page_icon="🔒", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    .title { text-align:center; font-size:2rem; font-weight:700; color:#1a1a2e; margin-bottom:0.2rem; }
    .subtitle { text-align:center; color:#666; margin-bottom:1.5rem; font-size:0.95rem; }
    .stButton > button {
        width:100%; background-color:#1a1a2e; color:white;
        border:none; padding:0.6rem 1rem; border-radius:8px;
        font-size:1rem; font-weight:600; cursor:pointer; transition:background-color 0.3s;
    }
    .stButton > button:hover { background-color:#16213e; }
    .welcome-box {
        background:linear-gradient(135deg,#1a1a2e,#16213e); color:white;
        padding:1.5rem; border-radius:12px; text-align:center; margin-bottom:1.5rem;
    }
    .role-badge {
        display:inline-block; padding:0.3rem 0.8rem; border-radius:20px;
        font-size:0.85rem; font-weight:600; margin-top:0.5rem;
    }
    .badge-user { background-color:#4CAF50; color:white; }
    .badge-courrier { background-color:#2196F3; color:white; }
    .locker-available {
        background:#d4edda; border:2px solid #28a745; border-radius:12px;
        padding:1rem; margin:0.5rem 0; text-align:center;
    }
    .locker-reserved {
        background:#f8d7da; border:2px solid #dc3545; border-radius:12px;
        padding:1rem; margin:0.5rem 0; text-align:center; opacity:0.7;
    }
    .booking-card {
        background:white; border-radius:12px; padding:1.2rem;
        box-shadow:0 2px 12px rgba(0,0,0,0.08); margin:0.8rem 0;
        border-left:4px solid #2196F3;
    }
    .separator { text-align:center; color:#aaa; margin:1rem 0; font-size:0.9rem; }
    #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
for key, default in [
    ("page", "login"), ("user_email", ""), ("user_role", ""),
    ("user_token", ""), ("user_id", ""), ("user_name", ""),
    ("selected_locker", None), ("booking_success", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# ROUTEUR PRINCIPAL
# ============================================================
page = st.session_state.page

if page == "login":
    page_login()

elif page == "signup":
    page_signup()

elif page == "user":
    if not st.session_state.user_token:
        st.session_state.page = "login"
        st.rerun()
    else:
        page_user()

elif page == "courrier":
    if not st.session_state.user_token:
        st.session_state.page = "login"
        st.rerun()
    else:
        page_courrier()
