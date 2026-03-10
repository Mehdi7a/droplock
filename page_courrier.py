import streamlit as st
from database import (
    get_bookings_for_courrier,
    get_all_delivered_bookings,
    update_booking_status,
    set_locker_available
)
from utils import generate_qr_code, QR_AVAILABLE
from auth import logout

# ============================================================
# PAGE COURRIER
# ============================================================

def page_courrier():
    st.markdown(f"""
        <div class="welcome-box">
            <h2>🚚 Espace Courrier</h2>
            <p>{st.session_state.user_email}</p>
            <span class="role-badge badge-courrier">📬 Agent Courrier</span>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📦 Livraisons à traiter", "✅ Historique"])

    with tab1:
        _show_pending_bookings()

    with tab2:
        _show_delivered_bookings()

    st.markdown("---")
    if st.button("🚪 Se déconnecter", key="btn_logout_courrier"):
        logout()
        st.rerun()


def _show_pending_bookings():
    """Affiche les commandes en attente ou en cours."""
    st.subheader("📦 Commandes en attente")
    if st.button("🔄 Actualiser", key="refresh_courier"):
        st.rerun()

    bookings = get_bookings_for_courrier()

    if not bookings:
        st.success("✅ Aucune livraison en attente.")
        return

    st.markdown(f"**{len(bookings)} livraison(s) à traiter**")

    for b in bookings:
        with st.expander(f"📦 #{b.get('booking_id','—')} — {b.get('produit','—')} · {b.get('user_name','—')}"):
            col_info, col_qr = st.columns([2, 1])

            with col_info:
                st.markdown(f"**👤 Client :** {b.get('user_name','—')}")
                st.markdown(f"**📧 Email :** {b.get('user_email','—')}")
                st.markdown(f"**🛍️ Produit :** {b.get('produit','—')}")
                st.markdown(f"**📝 Description :** {b.get('description','—')}")
                st.markdown(f"**🔒 Locker :** {b.get('locker_name','—')}")
                st.markdown(f"**📅 Commande :** {b.get('timestamp','—')}")
                st.markdown(f"**🟡 Statut :** {b.get('statut','—')}")

            with col_qr:
                st.markdown("**📱 QR Code**")
                if QR_AVAILABLE:
                    qr_data = {
                        "booking_id": b.get("booking_id"),
                        "client": b.get("user_name"),
                        "email": b.get("user_email"),
                        "locker": b.get("locker_name"),
                        "produit": b.get("produit"),
                        "description": b.get("description", ""),
                        "date": b.get("timestamp"),
                        "statut": b.get("statut")
                    }
                    try:
                        qr_b64 = generate_qr_code(qr_data)
                        st.markdown(f'<img src="data:image/png;base64,{qr_b64}" width="140"/>', unsafe_allow_html=True)
                    except:
                        st.warning("QR indisponible")
                else:
                    st.info("Installez qrcode[pil]")

            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("🚚 En cours", key=f"encours_{b['id']}"):
                    update_booking_status(b["id"], "en_cours")
                    st.success("✅ Mis à jour !")
                    st.rerun()

            with col_btn2:
                if st.button("✅ Livré", key=f"livre_{b['id']}"):
                    update_booking_status(b["id"], "livré")
                    set_locker_available(b["locker_id"])
                    st.success("✅ Livraison confirmée ! Locker libéré.")
                    st.rerun()


def _show_delivered_bookings():
    """Affiche l'historique de toutes les livraisons effectuées."""
    st.subheader("✅ Historique des livraisons")

    done = get_all_delivered_bookings()

    if not done:
        st.info("Aucune livraison terminée.")
        return

    st.markdown(f"**{len(done)} livraison(s) effectuée(s)**")
    for b in sorted(done, key=lambda x: x.get("timestamp", ""), reverse=True):
        st.markdown(f"""
            <div class="booking-card" style="border-left-color:#28a745">
                <b>#{b.get('booking_id','—')} — {b.get('produit','—')}</b><br>
                <small>👤 {b.get('user_name','—')} &nbsp;|&nbsp; 🔒 {b.get('locker_name','—')}</small><br>
                <small>📅 {b.get('timestamp','—')} &nbsp;|&nbsp; 🟢 <b>Livré</b></small>
            </div>
        """, unsafe_allow_html=True)
