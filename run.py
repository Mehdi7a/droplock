import streamlit as st
from auth import page_login, page_signup
from page_user import page_user
from page_courrier import page_courrier

st.set_page_config(page_title="Droplock", page_icon="🔒", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');

:root {
    --cream:  #FAFAF8;
    --white:  #FFFFFF;
    --ink:    #1A1A1A;
    --ink2:   #555;
    --muted:  #999;
    --border: #EBEBEB;
    --coral:  #FF6B35;
    --rose:   #FF3CAC;
    --mint:   #22C87A;
    --indigo: #3D3EBD;
    --grad:   linear-gradient(135deg,#FF6B35 0%,#FF3CAC 100%);
    --r:      14px;
}

html,body,[class*="css"] {
    font-family:'Plus Jakarta Sans',sans-serif;
    color:var(--ink);
    background:var(--cream)!important;
}
.stApp { background:var(--cream)!important; }

/* ── Brand ──────────────────────── */
.dl-brand {
    display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:.4rem;
}
.dl-icon {
    width:48px;height:48px;background:var(--grad);border-radius:14px;
    display:flex;align-items:center;justify-content:center;font-size:22px;
}
.dl-name {
    font-family:'Instrument Serif',serif;font-size:2rem;font-style:italic;
    letter-spacing:-.03em;color:var(--ink);
}
.dl-tagline {
    text-align:center;color:var(--muted);font-size:.88rem;margin-bottom:2rem;
}

/* ── Welcome banner ─────────────── */
.welcome-box {
    background:var(--grad);border-radius:22px;
    padding:1.8rem 1.6rem 1.5rem;color:white;
    margin-bottom:1.5rem;position:relative;overflow:hidden;
}
.welcome-box::after {
    content:'🔒';position:absolute;right:1.2rem;bottom:-.6rem;
    font-size:6rem;opacity:.12;pointer-events:none;
}
.welcome-box h2 {
    font-family:'Instrument Serif',serif;font-size:1.8rem;font-style:italic;
    font-weight:400;color:white;margin:0 0 .4rem;line-height:1.15;
}
.welcome-box p { font-size:.82rem;color:rgba(255,255,255,.72);margin:.1rem 0; }

/* ── Role badges ────────────────── */
.role-badge {
    display:inline-block;padding:.28rem .85rem;border-radius:40px;
    font-size:.73rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;
    margin-top:.6rem;background:rgba(255,255,255,.22);
    border:1px solid rgba(255,255,255,.35);color:white;
}

/* ── Buttons ────────────────────── */
.stButton > button {
    width:100%;background:var(--grad);color:white;border:none;
    padding:.75rem 1.2rem;border-radius:12px;
    font-family:'Plus Jakarta Sans',sans-serif;font-size:.92rem;font-weight:700;
    cursor:pointer;letter-spacing:.01em;transition:opacity .15s,transform .1s;
    box-shadow:0 4px 18px rgba(255,107,53,.28);
}
.stButton > button:hover {
    opacity:.9;transform:translateY(-1px);
    box-shadow:0 6px 24px rgba(255,107,53,.38);
}
.stButton > button:active { transform:translateY(0); }

/* ── Inputs ─────────────────────── */
.stTextInput label,.stTextArea label,.stSelectbox label {
    font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:.78rem!important;font-weight:600!important;
    color:var(--ink2)!important;letter-spacing:.01em!important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background:var(--white)!important;border:1.5px solid var(--border)!important;
    border-radius:12px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
    font-size:.88rem!important;color:var(--ink)!important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color:var(--coral)!important;
    box-shadow:0 0 0 3px rgba(255,107,53,.12)!important;
}
.stSelectbox > div > div {
    background:var(--white)!important;border:1.5px solid var(--border)!important;
    border-radius:12px!important;
}

/* ── Tabs ───────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap:4px;background:var(--white);border-radius:12px;
    padding:4px;border:1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px;color:var(--muted);
    font-family:'Plus Jakarta Sans',sans-serif;
    font-size:.85rem;font-weight:600;padding:.45rem .9rem;
}
.stTabs [aria-selected="true"] { background:var(--grad)!important;color:white!important; }

/* ── Metrics ────────────────────── */
[data-testid="metric-container"] {
    background:var(--white);border:1px solid var(--border);
    border-radius:var(--r);padding:1rem 1.1rem;
}
[data-testid="stMetricLabel"] {
    color:var(--muted)!important;font-size:.72rem!important;font-weight:700!important;
    text-transform:uppercase!important;letter-spacing:.08em!important;
}
[data-testid="stMetricValue"] {
    color:var(--ink)!important;font-family:'Instrument Serif',serif!important;
    font-style:italic!important;font-size:1.8rem!important;
}

/* ── Alerts ─────────────────────── */
.stSuccess {
    background:#F0FFF8!important;border:1.5px solid #AEEFD1!important;
    border-radius:12px!important;color:#0B6B42!important;
}
.stWarning {
    background:#FFFBF0!important;border:1.5px solid #FFE08A!important;
    border-radius:12px!important;color:#8A6200!important;
}
.stError {
    background:#FFF5F5!important;border:1.5px solid #FFC5C5!important;
    border-radius:12px!important;color:#8B2020!important;
}
.stInfo {
    background:#F0F0FF!important;border:1.5px solid #C5C5F5!important;
    border-radius:12px!important;color:#3D3EBD!important;
}

/* ── Expanders ──────────────────── */
.streamlit-expanderHeader {
    background:var(--white)!important;border:1px solid var(--border)!important;
    border-radius:12px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
    font-weight:600!important;color:var(--ink)!important;
}

/* ── Locker cards ───────────────── */
.locker-available {
    background:#F0FFF8;border:1.5px solid #AEEFD1;
    border-radius:18px;padding:1.1rem;margin:.5rem 0;text-align:center;
}
.locker-available h3 { font-size:.95rem;font-weight:700;color:#0B6B42;margin:0 0 .35rem; }
.locker-available p  { font-size:.78rem;color:#3A9E6A;margin:.1rem 0; }

.locker-reserved {
    background:#FFF5F5;border:1.5px solid #FFC5C5;
    border-radius:18px;padding:1.1rem;margin:.5rem 0;text-align:center;opacity:.7;
}
.locker-reserved h3 { font-size:.95rem;font-weight:700;color:#8B2020;margin:0 0 .35rem; }
.locker-reserved p  { font-size:.78rem;color:#BB5555;margin:.1rem 0; }

/* ── Booking cards ──────────────── */
.booking-card {
    background:var(--white);border:1px solid var(--border);
    border-radius:16px;padding:1rem 1.2rem;margin:.65rem 0;
    border-left:3px solid var(--coral);
}
.booking-card b     { color:var(--ink); }
.booking-card small { color:var(--muted); }

/* ── Separator ──────────────────── */
.separator {
    text-align:center;color:var(--muted);margin:1.2rem 0;font-size:.8rem;
    letter-spacing:.08em;
}

hr { border-color:var(--border)!important; }
#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────
for key, default in [
    ("page","login"),("user_email",""),("user_role",""),("user_token",""),
    ("user_id",""),("user_name",""),("selected_locker",None),
    ("booking_success",False),("last_token_id",""),("last_courrier",None),
    ("last_recipient",""),("last_booking_data",{}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Router ─────────────────────────────────────────────────
page = st.session_state.page

if page == "login":
    page_login()
elif page == "signup":
    page_signup()
elif page == "user":
    if not st.session_state.user_token:
        st.session_state.page = "login"; st.rerun()
    else:
        page_user()
elif page == "courrier":
    if not st.session_state.user_token:
        st.session_state.page = "login"; st.rerun()
    else:
        page_courrier()
