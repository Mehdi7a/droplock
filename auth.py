import json
import streamlit as st
from config import auth
from database import get_user_role, register_new_user


def _parse_firebase_error(e) -> str:
    raw = str(e)
    try:
        body = e.args[1] if len(e.args) > 1 else raw
        data = json.loads(body)
        return data.get("error", {}).get("message", raw)
    except Exception:
        pass
    try:
        start = raw.find("{")
        if start != -1:
            data = json.loads(raw[start:])
            msg = data.get("error", {}).get("message", "")
            if msg:
                return msg
    except Exception:
        pass
    return raw


def logout():
    for key in ["user_email","user_role","user_token","user_id","user_name"]:
        st.session_state[key] = ""
    st.session_state.selected_locker = None
    st.session_state.booking_success = False
    st.session_state.page = "login"


def handle_login_success(user_id, email, name, token):
    role = get_user_role(user_id, token)
    if role is None:
        st.error("❌ Account not found. Please create an account.")
        return
    st.session_state.update({
        "user_email": email,
        "user_name":  name,
        "user_id":    user_id,
        "user_token": token,
        "user_role":  role,
        "page":       role if role in ["user","courrier"] else "login"
    })


# ============================================================
# LOGIN PAGE
# ============================================================
def page_login():
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="dl-brand">
        <div class="dl-icon">🔒</div>
        <span class="dl-name">Droplock</span>
    </div>
    <div class="dl-tagline">Secure locker delivery, reimagined</div>
    """, unsafe_allow_html=True)

    # White card container
    st.markdown("""
    <div style="background:#fff;border:1px solid #EBEBEB;border-radius:22px;
                padding:2rem 1.8rem;max-width:400px;margin:0 auto;
                box-shadow:0 2px 40px rgba(0,0,0,.06);">
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:1.05rem;font-weight:700;color:#1A1A1A;margin:0 0 .2rem;">
        Welcome back
    </p>
    <p style="font-size:.83rem;color:#999;margin:0 0 1.4rem;">
        Sign in to manage your deliveries
    </p>
    """, unsafe_allow_html=True)

    email    = st.text_input("Email address", placeholder="you@example.com", key="login_email")
    password = st.text_input("Password", type="password", placeholder="Your password", key="login_password")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Sign In →", key="btn_login"):
        if not email or not password:
            st.error("⚠️ Please fill in all fields.")
        else:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                handle_login_success(user["localId"], email, email.split("@")[0], user["idToken"])
                st.rerun()
            except Exception as e:
                err = _parse_firebase_error(e)
                if "INVALID_PASSWORD" in err or "INVALID_LOGIN_CREDENTIALS" in err:
                    st.error("❌ Incorrect password.")
                elif "EMAIL_NOT_FOUND" in err:
                    st.error("❌ No account found with this email.")
                elif "TOO_MANY_ATTEMPTS" in err:
                    st.error("❌ Too many attempts. Try again later.")
                else:
                    st.error(f"❌ Sign-in failed: {err}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="separator">— or —</div>', unsafe_allow_html=True)

    if st.button("Create an Account", key="btn_go_signup"):
        st.session_state.page = "signup"
        st.rerun()


# ============================================================
# SIGNUP PAGE
# ============================================================
def page_signup():
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="dl-brand">
        <div class="dl-icon">✏️</div>
        <span class="dl-name">Droplock</span>
    </div>
    <div class="dl-tagline">Join Droplock — it only takes a moment</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#fff;border:1px solid #EBEBEB;border-radius:22px;
                padding:2rem 1.8rem;max-width:400px;margin:0 auto;
                box-shadow:0 2px 40px rgba(0,0,0,.06);">
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:1.05rem;font-weight:700;color:#1A1A1A;margin:0 0 .2rem;">
        Create your account
    </p>
    <p style="font-size:.83rem;color:#999;margin:0 0 1.4rem;">
        Free forever · No credit card required
    </p>
    """, unsafe_allow_html=True)

    email            = st.text_input("Email address", placeholder="you@example.com", key="signup_email")
    password         = st.text_input("Password", type="password", placeholder="At least 6 characters", key="signup_password")
    password_confirm = st.text_input("Confirm password", type="password", placeholder="Repeat your password", key="signup_confirm")
    role = st.selectbox(
        "I am a...",
        ["user","courrier"],
        format_func=lambda x: "📦 User — I receive packages" if x == "user" else "🚚 Courier — I deliver packages",
        key="signup_role"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Create My Account →", key="btn_signup"):
        if not email or not password or not password_confirm:
            st.error("⚠️ Please fill in all fields.")
        elif password != password_confirm:
            st.error("❌ Passwords do not match.")
        elif len(password) < 6:
            st.error("❌ Password must be at least 6 characters.")
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
            except Exception as e:
                err = _parse_firebase_error(e)
                if "EMAIL_EXISTS" in err:
                    st.error("❌ This email is already registered.")
                elif "WEAK_PASSWORD" in err:
                    st.error("❌ Password too weak — minimum 6 characters.")
                elif "INVALID_EMAIL" in err:
                    st.error("❌ Invalid email address.")
                elif "TOO_MANY_ATTEMPTS" in err:
                    st.error("❌ Too many attempts. Try again later.")
                else:
                    st.error(f"❌ Auth error: {err}")
                return

            try:
                signed_in = auth.sign_in_with_email_and_password(email, password)
                id_token  = signed_in["idToken"]
                register_new_user(user["localId"], email, email.split("@")[0], role, token=id_token)
            except Exception as e:
                st.warning(f"⚠️ Account created but database error: {str(e)}\nCheck your Firebase Realtime Database rules.")
                import time; time.sleep(2)
                st.session_state.page = "login"; st.rerun()
                return

            st.success("✅ Account created! You can now sign in.")
            st.balloons()
            import time; time.sleep(1)
            st.session_state.page = "login"; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="separator">— or —</div>', unsafe_allow_html=True)

    if st.button("← Back to Sign In", key="btn_back"):
        st.session_state.page = "login"; st.rerun()
