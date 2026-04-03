import streamlit as st
from database import (
    get_lockers, create_booking,
    get_user_bookings, get_booking_by_id,
    identify_product, get_products_catalog, LOCKER_ZONES
)
from utils import generate_qr_code, generate_qr_bytes, send_email_with_qr, QR_AVAILABLE
from auth import logout
from config import GMAIL_SENDER, GMAIL_APP_PASS
from invoice_pdf import generate_invoice_pdf
import base64


def page_user():
    name = st.session_state.user_name or st.session_state.user_email
    st.markdown(f"""
        <div class="welcome-box">
            <p style="font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;opacity:.7;margin-bottom:.2rem;">
                Welcome back
            </p>
            <h2>{name}!</h2>
            <p>{st.session_state.user_email}</p>
            <span class="role-badge">📦 User</span>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔒 Lockers", "📋 My Orders"])

    with tab1:
        _show_lockers()
    with tab2:
        _show_user_bookings()

    st.markdown("---")
    if st.button("🚪 Sign Out", key="btn_logout_user"):
        logout(); st.rerun()


# ============================================================
# LOCKERS
# ============================================================
def _show_lockers():
    st.subheader("🔒 Available Lockers")

    if st.button("🔄 Refresh", key="refresh_lockers"):
        st.rerun()

    lockers = get_lockers(st.session_state.user_token)

    if not lockers:
        st.warning("⚠️ No lockers configured at the moment.")
    else:
        available = sum(1 for v in lockers.values() if v.get("statut") == "disponible")
        reserved  = len(lockers) - available

        st.markdown(f"""
        <div style="display:flex;gap:10px;margin-bottom:1rem;">
            <div style="background:#F0FFF8;border:1.5px solid #AEEFD1;border-radius:12px;
                        padding:.6rem 1rem;font-size:.82rem;font-weight:700;color:#0B6B42;">
                ● {available} available
            </div>
            <div style="background:#FFF5F5;border:1.5px solid #FFC5C5;border-radius:12px;
                        padding:.6rem 1rem;font-size:.82rem;font-weight:700;color:#8B2020;">
                ● {reserved} reserved
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(2)
        for i, (lid, locker) in enumerate(lockers.items()):
            is_available = locker.get("statut") == "disponible"
            zone = locker.get("zone", LOCKER_ZONES.get(lid, "—"))
            with cols[i % 2]:
                if is_available:
                    st.markdown(f"""
                        <div class="locker-available">
                            <div style="display:inline-flex;align-items:center;gap:5px;
                                        background:#C6F7E2;color:#0B6B42;font-size:.7rem;
                                        font-weight:700;letter-spacing:.05em;text-transform:uppercase;
                                        padding:.2rem .65rem;border-radius:40px;margin-bottom:.6rem;">
                                <span>●</span> Available
                            </div>
                            <h3>{locker.get('nom', lid)}</h3>
                            <p>📍 {locker.get('position','—')}</p>
                            <p>🗺️ Zone: <b>{zone}</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Reserve →", key=f"book_{lid}"):
                        st.session_state.selected_locker = {"id": lid, "zone": zone, **locker}
                        st.rerun()
                else:
                    st.markdown(f"""
                        <div class="locker-reserved">
                            <div style="display:inline-flex;align-items:center;gap:5px;
                                        background:#FFD9D9;color:#8B2020;font-size:.7rem;
                                        font-weight:700;letter-spacing:.05em;text-transform:uppercase;
                                        padding:.2rem .65rem;border-radius:40px;margin-bottom:.6rem;">
                                <span>●</span> Reserved
                            </div>
                            <h3>{locker.get('nom', lid)}</h3>
                            <p>📍 {locker.get('position','—')}</p>
                            <p>🗺️ Zone: <b>{zone}</b></p>
                        </div>
                    """, unsafe_allow_html=True)

    if st.session_state.selected_locker:
        _show_booking_form()

    if st.session_state.booking_success:
        _show_booking_confirmation()


# ============================================================
# BOOKING FORM
# ============================================================
def _show_booking_form():
    locker = st.session_state.selected_locker
    st.markdown("---")
    zone = locker.get("zone", "—")

    st.markdown(f"""
    <div style="background:#fff;border:1px solid #EBEBEB;border-radius:20px;
                padding:1.5rem;margin-bottom:1rem;
                box-shadow:0 2px 20px rgba(0,0,0,.05);">
        <p style="font-size:1rem;font-weight:700;color:#1A1A1A;margin:0 0 .3rem;">
            📦 Reserve: {locker.get('nom', locker['id'])}
        </p>
        <p style="font-size:.82rem;color:#999;margin:0;">
            📍 {locker.get('position','—')} &nbsp;·&nbsp; 🗺️ Zone: <b style="color:#FF6B35;">{zone}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 View product catalog", expanded=False):
        catalog = get_products_catalog(st.session_state.get("user_token",""))
        rows = [f"| {n} | {d['poids_kg']} kg | {d['prix_base']:.2f} TND |" for n,d in catalog.items()]
        st.markdown("| Product | Weight | Fee |\n|---|---|---|\n" + "\n".join(rows))

    produit = st.text_input("🛍️ Product name", placeholder="e.g. Smartphone, Laptop, Book...", key="form_produit")

    product_key = product_data = None
    if produit:
        product_key, product_data = identify_product(produit, st.session_state.get("user_token",""))
        if product_data:
            st.markdown(f"""
            <div style="background:#F0FFF8;border:1.5px solid #AEEFD1;border-radius:12px;
                        padding:.7rem 1rem;font-size:.85rem;color:#0B6B42;font-weight:600;margin:.5rem 0;">
                ✅ Identified: <b>{product_key}</b> · {product_data['poids_kg']} kg · {product_data['prix_base']:.2f} TND
            </div>
            """, unsafe_allow_html=True)
        else:
            catalog2 = get_products_catalog(st.session_state.get("user_token",""))
            st.error("❌ Product not in catalog. Available: " + ", ".join(catalog2.keys()))

    description = st.text_area("📝 Description", placeholder="Size, color, fragile items, special notes...", height=80, key="form_description")
    recipient_email = st.text_input("📧 Courier email address", placeholder="e.g. courier@example.com", key="form_recipient_email")
    st.caption("The QR code will be sent to this address. No Droplock account required.")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    confirmed = col1.button("🛒 Place Order", key="btn_confirm_booking", disabled=(product_data is None and produit != ""))
    cancelled = col2.button("❌ Cancel", key="btn_cancel_booking")

    if confirmed:
        if not produit:
            st.error("⚠️ Please enter a product name.")
        elif not product_data:
            st.error("❌ Product not in catalog.")
        elif not recipient_email or "@" not in recipient_email:
            st.error("⚠️ Please enter a valid courier email address.")
        else:
            with st.spinner("⏳ Creating your order and sending the QR code..."):
                booking_id, booking_data, token_id, courrier = create_booking(
                    st.session_state.user_id, st.session_state.user_email,
                    st.session_state.user_name, locker["id"],
                    locker.get("nom", locker["id"]), product_key, description,
                    token=st.session_state.user_token, product_data=product_data, locker_zone=zone
                )
                qr_bytes = generate_qr_bytes(token_id)
                booking_info = {
                    "user_email":  st.session_state.user_email,
                    "produit":     product_key,
                    "locker_name": locker.get("nom", locker["id"]),
                    "timestamp":   booking_data.get("timestamp","")
                }
                success, err = send_email_with_qr(
                    to_email=recipient_email, token_id=token_id, qr_bytes=qr_bytes,
                    booking_info=booking_info, has_account=False,
                    gmail_sender=GMAIL_SENDER, gmail_pass=GMAIL_APP_PASS
                )
                if success:
                    st.success(f"📬 QR code sent to **{recipient_email}**")
                else:
                    st.warning(f"⚠️ Email could not be sent: {err}")

                if courrier and courrier.get("email") and courrier["email"] != recipient_email:
                    send_email_with_qr(
                        to_email=courrier["email"], token_id=token_id, qr_bytes=qr_bytes,
                        booking_info=booking_info, has_account=True,
                        gmail_sender=GMAIL_SENDER, gmail_pass=GMAIL_APP_PASS
                    )

                st.session_state.selected_locker   = None
                st.session_state.booking_success   = booking_id
                st.session_state.last_token_id     = token_id
                st.session_state.last_courrier     = courrier
                st.session_state.last_recipient    = recipient_email
                st.session_state.last_booking_data = booking_data
                st.rerun()

    if cancelled:
        st.session_state.selected_locker = None; st.rerun()


# ============================================================
# BOOKING CONFIRMATION + INVOICE
# ============================================================
def _show_booking_confirmation():
    bid          = st.session_state.booking_success
    token_id     = st.session_state.get("last_token_id","")
    recipient    = st.session_state.get("last_recipient","—")
    booking_data = st.session_state.get("last_booking_data",{})

    st.markdown("---")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#FF6B35,#FF3CAC);border-radius:18px;
                padding:1.2rem 1.5rem;color:white;margin-bottom:1rem;">
        <p style="font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;opacity:.75;margin:0 0 .2rem;">
            Order confirmed
        </p>
        <p style="font-family:'Instrument Serif',serif;font-size:1.5rem;font-style:italic;margin:0;">
            #{bid} ✓
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        booking = get_booking_by_id(bid, st.session_state.user_token)
        if booking:
            booking_data = booking
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
**🛍️ Product:** {booking.get('produit','—')}
**⚖️ Weight:** {booking.get('poids_kg','—')} kg
**🔒 Locker:** {booking.get('locker_name','—')}
**🗺️ Zone:** {booking.get('locker_zone','—')}
**📅 Date:** {booking.get('timestamp','—')}
                """)
            with col2:
                prix = booking.get('prix', 0)
                tva  = round(prix * 0.19, 2)
                total = round(prix + tva, 2)
                st.markdown(f"""
**🎫 QR Token:** `{token_id}`
**📧 Sent to:** {recipient}
**🟡 Status:** Pending
**💰 Price:** {prix:.2f} + VAT {tva:.2f} = **{total:.2f} TND**
                """)
    except:
        pass

    if token_id and QR_AVAILABLE:
        qr_bytes = generate_qr_bytes(token_id)
        st.markdown("### 📱 Your QR Code")
        st.image(qr_bytes, width=220, caption=token_id)
        st.caption("This QR code has also been emailed to the courier.")

    st.markdown("### 🧾 Invoice")
    if booking_data:
        try:
            pdf_bytes    = generate_invoice_pdf(booking_data, token_id)
            b64_pdf      = base64.b64encode(pdf_bytes).decode()
            pdf_filename = f"droplock_invoice_{bid}.pdf"
            st.markdown(f"""
            <a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}"
               style="display:inline-block;background:linear-gradient(135deg,#FF6B35,#FF3CAC);
                      color:white;padding:.65rem 1.4rem;border-radius:12px;
                      text-decoration:none;font-weight:700;font-size:.9rem;
                      box-shadow:0 4px 16px rgba(255,107,53,.3);">
               📄 Download Invoice (PDF)
            </a>
            <br><br>
            <iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600px"
                    style="border:1px solid #EBEBEB;border-radius:16px;">
            </iframe>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ Could not generate invoice: {e}")
    else:
        st.info("Invoice data unavailable.")

    if st.button("🔄 Place Another Order", key="new_booking"):
        st.session_state.booking_success   = False
        st.session_state.last_token_id     = ""
        st.session_state.last_courrier     = None
        st.session_state.last_recipient    = ""
        st.session_state.last_booking_data = {}
        st.rerun()


# ============================================================
# MY ORDERS
# ============================================================
def _show_user_bookings():
    st.subheader("📋 My Orders")

    if st.button("🔄 Refresh", key="refresh_bookings"):
        st.rerun()

    bookings = get_user_bookings(st.session_state.user_id, st.session_state.user_token)

    if not bookings:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#999;">
            <div style="font-size:2.5rem;margin-bottom:.8rem;">📭</div>
            <p style="font-weight:600;color:#555;">No orders yet</p>
            <p style="font-size:.85rem;">Reserve a locker to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    status_cfg = {
        "en_attente": {"label":"Pending",     "bg":"#FFF4E0","color":"#9A6A00","border":"#FFE08A"},
        "en_cours":   {"label":"In Progress", "bg":"#EEF0FF","color":"#3D3EBD","border":"#C5C5F5"},
        "livré":      {"label":"Delivered",   "bg":"#E6FBF2","color":"#0B6B42","border":"#AEEFD1"},
        "annulé":     {"label":"Cancelled",   "bg":"#FFF5F5","color":"#8B2020","border":"#FFC5C5"},
    }

    st.markdown(f"<p style='font-size:.82rem;color:#999;margin-bottom:.8rem;'>{len(bookings)} order(s) total</p>", unsafe_allow_html=True)

    for b in sorted(bookings, key=lambda x: x.get("timestamp",""), reverse=True):
        s   = b.get("statut","")
        cfg = status_cfg.get(s, {"label":s,"bg":"#F5F5F5","color":"#555","border":"#DDD"})
        prix = b.get("prix",0)
        zone = b.get("locker_zone","—")

        st.markdown(f"""
        <div style="background:#fff;border:1px solid #EBEBEB;border-radius:16px;
                    padding:1rem 1.2rem;margin:.65rem 0;
                    display:flex;justify-content:space-between;align-items:center;gap:1rem;">
            <div style="flex:1;">
                <p style="font-size:.7rem;font-weight:700;color:#CCC;letter-spacing:.08em;
                           text-transform:uppercase;margin:0 0 .2rem;">
                    Order #{b.get('booking_id','—')}
                </p>
                <p style="font-size:.95rem;font-weight:700;color:#1A1A1A;margin:0 0 .2rem;">
                    {b.get('produit','—')}
                </p>
                <p style="font-size:.76rem;color:#AAA;margin:0;">
                    🔒 {b.get('locker_name','—')} · 🗺️ {zone} · 📅 {b.get('timestamp','—')}
                    <br>💰 {prix:.2f} TND
                </p>
            </div>
            <div style="background:{cfg['bg']};color:{cfg['color']};
                        border:1.5px solid {cfg['border']};padding:.3rem .85rem;
                        border-radius:40px;font-size:.72rem;font-weight:700;
                        letter-spacing:.05em;text-transform:uppercase;white-space:nowrap;">
                {cfg['label']}
            </div>
        </div>
        """, unsafe_allow_html=True)
