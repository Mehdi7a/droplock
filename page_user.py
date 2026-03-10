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

    # CSS mobile-friendly
    st.markdown("""
    <style>
        .locker-available {
            background: #d4edda;
            border: 2px solid #28a745;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            text-align: center;
        }
        .locker-available h3 {
            color: #155724 !important;
            font-size: 1.2rem !important;
        }
        .locker-available p {
            color: #155724 !important;
            font-size: 1rem !important;
        }
        .locker-reserved {
            background: #f8d7da;
            border: 2px solid #dc3545;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            text-align: center;
            opacity: 0.85;
        }
        .locker-reserved h3 {
            color: #721c24 !important;
            font-size: 1.2rem !important;
        }
        .locker-reserved p {
            color: #721c24 !important;
            font-size: 1rem !important;
        }
        .booking-card {
            background: white;
            border-radius: 12px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            border-left: 5px solid #2196F3;
        }
        .booking-card b {
            color: #1a1a2e !important;
            font-size: 1rem !important;
        }
        .booking-card small {
            color: #333333 !important;
            font-size: 0.9rem !important;
        }
        .booking-card .statut {
            color: #1a1a2e !important;
            font-size: 0.95rem !important;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔒 Lockers", "📋 Mes Commandes"])

    with tab1:
        _show_lockers()

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
                            <p style="font-size:0.85rem;color:#155724;font-weight:700;">✅ Disponible</p>
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
                            <p style="font-size:0.85rem;color:#721c24;font-weight:700;">🔒 Réservé</p>
                        </div>
                    """, unsafe_allow_html=True)

    if st.session_state.selected_locker:
        _show_booking_form()

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
                st.markdown(
                    f'<div style="text-align:center;">'
                    f'<img src="data:image/png;base64,{qr_b64}" width="220"/>'
                    f'</div>',
                    unsafe_allow_html=True
                )
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
            "en_attente": ("🟡", "#856404", "#fff3cd"),
            "en_cours":   ("🔵", "#004085", "#cce5ff"),
            "livré":      ("🟢", "#155724", "#d4edda"),
            "annulé":     ("🔴", "#721c24", "#f8d7da"),
        }
        st.markdown(f"**{len(bookings)} commande(s) au total**")

        for b in sorted(bookings, key=lambda x: x.get("timestamp", ""), reverse=True):
            statut = b.get("statut", "")
            icon, text_color, bg_color = statut_colors.get(statut, ("⚪", "#333", "#f8f9fa"))

            st.markdown(f"""
                <div style="
                    background: white;
                    border-radius: 12px;
                    padding: 1.2rem;
                    margin: 0.8rem 0;
                    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
                    border-left: 5px solid #2196F3;
                ">
                    <p style="font-size:1.05rem;font-weight:800;color:#1a1a2e;margin:0 0 0.5rem 0;">
                        📦 #{b.get('booking_id','—')} — {b.get('produit','—')}
                    </p>
                    <p style="font-size:0.95rem;color:#333333;margin:0.2rem 0;">
                        🔒 <b>{b.get('locker_name','—')}</b>
                    </p>
                    <p style="font-size:0.95rem;color:#333333;margin:0.2rem 0;">
                        📅 {b.get('timestamp','—')}
                    </p>
                    <p style="margin:0.5rem 0 0 0;">
                        <span style="
                            background:{bg_color};
                            color:{text_color};
                            padding:0.3rem 0.8rem;
                            border-radius:20px;
                            font-weight:700;
                            font-size:0.95rem;
                        ">{icon} {statut}</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
