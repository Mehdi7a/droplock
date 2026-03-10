import streamlit as st
from database import get_lockers, create_booking, get_user_bookings, get_booking_by_id
from utils import generate_qr_code, QR_AVAILABLE
from auth import logout

# ============================================================
# PAGE UTILISATEUR
# ============================================================

def page_user():
    name = st.session_state.user_name or st.session_state.user_email
    st.markdown(f"""
        <div class="welcome-box">
            <h2>👋 Bonjour, {name} !</h2>
            <p>{st.session_state.user_email}</p>
            <span class="role-badge badge-user">📦 Utilisateur</span>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔒 Lockers", "📋 Mes Commandes"])

    # ── TAB 1 : Lockers ───────────────────────────────────────────────────
    with tab1:
        _show_lockers()

    # ── TAB 2 : Historique commandes ──────────────────────────────────────
    with tab2:
        _show_user_bookings()

    st.markdown("---")
    if st.button("🚪 Se déconnecter", key="btn_logout_user"):
        logout()
        st.rerun()


def _show_lockers():
    """Affiche la liste des lockers et le formulaire de réservation."""
    st.subheader("🔒 Lockers Disponibles")
    if st.button("🔄 Actualiser", key="refresh_lockers"):
        st.rerun()

    lockers = get_lockers()

    if not lockers:
        st.warning("⚠️ Aucun locker configuré.")
    else:
        available = sum(1 for v in lockers.values() if v.get("statut") == "disponible")
        reserved = len(lockers) - available
        st.markdown(f"**{available} disponible(s)** · {reserved} réservé(s)")
        st.markdown("")

        cols = st.columns(2)
        for i, (lid, locker) in enumerate(lockers.items()):
            is_available = locker.get("statut") == "disponible"
            with cols[i % 2]:
                if is_available:
                    st.markdown(f"""
                        <div class="locker-available">
                            <h3>🟢 {locker.get('nom', lid)}</h3>
                            <p>📍 {locker.get('position', '—')}</p>
                            <p style="font-size:0.85rem;color:#155724;">✅ Disponible</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"📦 Réserver", key=f"book_{lid}"):
                        st.session_state.selected_locker = {"id": lid, **locker}
                        st.rerun()
                else:
                    st.markdown(f"""
                        <div class="locker-reserved">
                            <h3>🔴 {locker.get('nom', lid)}</h3>
                            <p>📍 {locker.get('position', '—')}</p>
                            <p style="font-size:0.85rem;color:#721c24;">🔒 Réservé</p>
                        </div>
                    """, unsafe_allow_html=True)

    # Formulaire de réservation
    if st.session_state.selected_locker:
        _show_booking_form()

    # QR Code après réservation
    if st.session_state.booking_success:
        _show_booking_confirmation()


def _show_booking_form():
    """Affiche le formulaire de réservation d'un locker."""
    locker = st.session_state.selected_locker
    st.markdown("---")
    st.subheader(f"📦 Réserver : {locker.get('nom', locker['id'])}")
    st.info(f"📍 Position : {locker.get('position', '—')}")

    with st.form("booking_form"):
        produit = st.text_input("🛍️ Nom du produit", placeholder="Ex: Colis Amazon, Vêtements...")
        description = st.text_area("📝 Description", placeholder="Taille, couleur, fragile...", height=80)
        col_submit, col_cancel = st.columns(2)
        submitted = col_submit.form_submit_button("✅ Confirmer")
        cancelled = col_cancel.form_submit_button("❌ Annuler")

    if submitted:
        if not produit:
            st.error("⚠️ Indiquez le nom du produit.")
        else:
            with st.spinner("Création de la commande..."):
                booking_id, _ = create_booking(
                    st.session_state.user_id,
                    st.session_state.user_email,
                    st.session_state.user_name,
                    locker["id"],
                    locker.get("nom", locker["id"]),
                    produit,
                    description
                )
                st.session_state.selected_locker = None
                st.session_state.booking_success = booking_id
                st.rerun()

    if cancelled:
        st.session_state.selected_locker = None
        st.rerun()


def _show_booking_confirmation():
    """Affiche la confirmation et le QR code après une réservation."""
    bid = st.session_state.booking_success
    st.markdown("---")
    st.success(f"✅ Commande **#{bid}** créée avec succès !")

    try:
        booking = get_booking_by_id(bid)
        if booking:
            qr_data = {
                "booking_id": bid,
                "client": booking.get("user_name"),
                "email": booking.get("user_email"),
                "locker": booking.get("locker_name"),
                "produit": booking.get("produit"),
                "description": booking.get("description", ""),
                "date": booking.get("timestamp"),
                "statut": booking.get("statut")
            }
            if QR_AVAILABLE:
                qr_b64 = generate_qr_code(qr_data)
                st.markdown("### 📱 Votre QR Code")
                st.markdown(f'<img src="data:image/png;base64,{qr_b64}" width="220"/>', unsafe_allow_html=True)
                st.caption("Montrez ce QR code à votre agent courrier.")
            else:
                st.info("📋 Détails de votre commande :")
                st.json(qr_data)
    except Exception as e:
        st.error(f"Erreur : {e}")

    if st.button("🔄 Nouvelle réservation", key="new_booking"):
        st.session_state.booking_success = False
        st.rerun()


def _show_user_bookings():
    """Affiche l'historique des commandes de l'utilisateur."""
    st.subheader("📋 Mes Commandes")
    if st.button("🔄 Actualiser", key="refresh_bookings"):
        st.rerun()

    bookings = get_user_bookings(st.session_state.user_id)

    if not bookings:
        st.info("Vous n'avez pas encore de commande.")
    else:
        statut_colors = {
            "en_attente": "🟡",
            "en_cours": "🔵",
            "livré": "🟢",
            "annulé": "🔴"
        }
        st.markdown(f"**{len(bookings)} commande(s) au total**")
        for b in sorted(bookings, key=lambda x: x.get("timestamp", ""), reverse=True):
            icon = statut_colors.get(b.get("statut", ""), "⚪")
            st.markdown(f"""
                <div class="booking-card">
                    <b>#{b.get('booking_id','—')} — {b.get('produit','—')}</b><br>
                    <small>🔒 {b.get('locker_name','—')} &nbsp;|&nbsp; 📅 {b.get('timestamp','—')}</small><br>
                    <small>{icon} Statut : <b>{b.get('statut','—')}</b></small>
                </div>
            """, unsafe_allow_html=True)
