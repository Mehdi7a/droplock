import streamlit as st
from config import auth
from database import get_user_role, register_new_user

# ============================================================
# AUTHENTIFICATION
# ============================================================

def logout():
    """Déconnecte l'utilisateur et réinitialise le session state."""
    for key in ["user_email", "user_role", "user_token", "user_id", "user_name"]:
        st.session_state[key] = ""
    st.session_state.selected_locker = None
    st.session_state.booking_success = False
    st.session_state.page = "login"

def handle_login_success(user_id, email, name, token):
    """Logique commune après une connexion réussie."""
    role = get_user_role(user_id)
    if role is None:
        st.error("❌ Compte introuvable. Recréez un compte.")
        return
    st.session_state.update({
        "user_email": email,
        "user_name": name,
        "user_id": user_id,
        "user_token": token,
        "user_role": role,
        "page": role if role in ["user", "courrier"] else "login"
    })

def page_login():
    """Page de connexion."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="title">🔒 Droplock</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Connectez-vous à votre compte</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    email = st.text_input("📧 Email", placeholder="exemple@email.com", key="login_email")
    password = st.text_input("🔑 Mot de passe", type="password", key="login_password")
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Se connecter", key="btn_login"):
        if not email or not password:
            st.error("⚠️ Remplissez tous les champs.")
        else:
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                handle_login_success(user["localId"], email, email.split("@")[0], user["idToken"])
                st.rerun()
            except Exception as e:
                err = str(e)
                if "INVALID_PASSWORD" in err or "INVALID_LOGIN_CREDENTIALS" in err:
                    st.error("❌ Mot de passe incorrect.")
                elif "EMAIL_NOT_FOUND" in err:
                    st.error("❌ Email introuvable.")
                elif "TOO_MANY_ATTEMPTS" in err:
                    st.error("❌ Trop de tentatives. Réessayez plus tard.")
                else:
                    st.error("❌ Erreur de connexion.")

    st.markdown('<div class="separator">─── ou ───</div>', unsafe_allow_html=True)
    if st.button("✏️ Créer un compte", key="btn_go_signup"):
        st.session_state.page = "signup"
        st.rerun()

def page_signup():
    """Page d'inscription."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="title">✏️ Créer un compte</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Rejoignez Droplock</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    email = st.text_input("📧 Email", placeholder="exemple@email.com", key="signup_email")
    password = st.text_input("🔑 Mot de passe", type="password", placeholder="Minimum 6 caractères", key="signup_password")
    password_confirm = st.text_input("🔑 Confirmer", type="password", key="signup_confirm")
    role = st.selectbox(
        "👤 Je suis...",
        ["user", "courrier"],
        format_func=lambda x: "📦 Utilisateur (je reçois des colis)" if x == "user" else "🚚 Agent Courrier (je livre des colis)",
        key="signup_role"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✅ Créer mon compte", key="btn_signup"):
        if not email or not password or not password_confirm:
            st.error("⚠️ Remplissez tous les champs.")
        elif password != password_confirm:
            st.error("❌ Les mots de passe ne correspondent pas.")
        elif len(password) < 6:
            st.error("❌ Minimum 6 caractères.")
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                register_new_user(user["localId"], email, email.split("@")[0], role)
                st.success("✅ Compte créé ! Connectez-vous.")
                st.balloons()
                import time; time.sleep(1)
                st.session_state.page = "login"
                st.rerun()
            except Exception as e:
                err = str(e)
                if "EMAIL_EXISTS" in err: st.error("❌ Email déjà utilisé.")
                elif "WEAK_PASSWORD" in err: st.error("❌ Mot de passe trop faible.")
                else: st.error("❌ Erreur. Réessayez.")

    st.markdown('<div class="separator">─── ou ───</div>', unsafe_allow_html=True)
    if st.button("⬅️ Retour au login", key="btn_back"):
        st.session_state.page = "login"
        st.rerun()
