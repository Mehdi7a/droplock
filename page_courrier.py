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

    # CSS mobile-friendly
    st.markdown("""
    <style>
        .delivery-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 1.2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
            border-left: 6px solid #2196F3;
        }
        .delivery-card-done {
            background: #ffffff;
            border-radius: 16px;
            padding: 1.2rem;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.12);
            border-left: 6px solid #28a745;
        }
        .info-row {
            display: flex;
            align-items: center;
            padding: 0.4rem 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 1rem;
            color: #1a1a2e;
        }
        .info-label {
            font-weight: 700;
            min-width: 120px;
            color: #1a1a2e;
        }
        .info-value {
            color: #333333;
            font-size: 1rem;
        }
        .statut-attente {
            background: #fff3cd;
            color: #856404;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.95rem;
        }
        .statut-encours {
            background: #cce5ff;
            color: #004085;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.95rem;
        }
        .statut-livre {
            background: #d4edda;
            color: #155724;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.95rem;
        }
        .card-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: #1a1a2e;
            margin-bottom: 0.8rem;
        }
    </style>
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


def _get_statut_badge(statut):
    """Retourne un badge coloré selon le statut."""
    if statut == "en_attente":
        return f'<span class="statut-attente">🟡 En attente</span>'
    elif statut == "en_cours":
        return f'<span class="statut-encours">🔵 En cours</span>'
    elif statut == "livré":
        return f'<span class="statut-livre">🟢 Livré</span>'
    return f'<span>{statut}</span>'


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
        statut_badge = _get_statut_badge(b.get("statut", ""))

        # Carte de livraison bien visible
        st.markdown(f"""
            <div class="delivery-card">
                <div class="card-title">
                    📦 #{b.get('booking_id','—')} — {b.get('produit','—')}
                </div>
                <div class="info-row">
                    <span class="info-label">👤 Client</span>
                    <span class="info-value">{b.get('user_name','—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📧 Email</span>
                    <span class="info-value">{b.get('user_email','—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🛍️ Produit</span>
                    <span class="info-value">{b.get('produit','—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📝 Description</span>
                    <span class="info-value">{b.get('description') or '—'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🔒 Locker</span>
                    <span class="info-value">{b.get('locker_name','—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">📅 Date</span>
                    <span class="info-value">{b.get('timestamp','—')}</span>
                </div>
                <div class="info-row" style="border-bottom:none;">
                    <span class="info-label">📌 Statut</span>
                    <span>{statut_badge}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # QR Code centré en dessous
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
                st.markdown(
                    f'<div style="text-align:center;margin:0.5rem 0;">'
                    f'<p style="font-weight:700;color:#1a1a2e;">📱 QR Code</p>'
                    f'<img src="data:image/png;base64,{qr_b64}" width="180"/>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            except:
                st.warning("QR indisponible")

        # Boutons d'action
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

        st.markdown("<hr style='margin:1.5rem 0;border-color:#eee;'>", unsafe_allow_html=True)


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
            <div class="delivery-card-done">
                <div class="card-title">
                    ✅ #{b.get('booking_id','—')} — {b.get('produit','—')}
                </div>
                <div class="info-row">
                    <span class="info-label">👤 Client</span>
                    <span class="info-value">{b.get('user_name','—')}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">🔒 Locker</span>
                    <span class="info-value">{b.get('locker_name','—')}</span>
                </div>
                <div class="info-row" style="border-bottom:none;">
                    <span class="info-label">📅 Date</span>
                    <span class="info-value">{b.get('timestamp','—')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
