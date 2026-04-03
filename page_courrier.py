import streamlit as st
from database import (
    get_bookings_for_courrier, get_all_delivered_bookings,
    update_booking_status, set_locker_available,
    get_courrier_tokens, mark_token_used,
    get_user_profile, update_user_profile, ZONES
)
from utils import generate_qr_code, generate_qr_bytes, QR_AVAILABLE
from auth import logout


# ============================================================
# PAGE COURRIER
# ============================================================
def page_courrier():
    st.markdown(f"""
        <div class="welcome-box">
            <p style="font-size:.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;opacity:.7;margin-bottom:.2rem;">
                Courier dashboard
            </p>
            <h2>{st.session_state.user_name or st.session_state.user_email}!</h2>
            <p>{st.session_state.user_email}</p>
            <span class="role-badge">📬 Courier Agent</span>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🎫 My QR Codes", "📦 Deliveries", "✅ History", "⚙️ Settings"])

    with tab1: _show_qr_tokens()
    with tab2: _show_pending_bookings()
    with tab3: _show_delivered_bookings()
    with tab4: _show_settings()

    st.markdown("---")
    if st.button("🚪 Sign Out", key="btn_logout_courrier"):
        logout(); st.rerun()


# ============================================================
# TAB 4 — SETTINGS
# ============================================================
def _show_settings():
    st.subheader("⚙️ Profile & Settings")

    uid   = st.session_state.user_id
    token = st.session_state.user_token
    profile = get_user_profile(uid, token)

    current_name  = profile.get("name", st.session_state.user_name or "")
    current_email = profile.get("email", st.session_state.user_email or "")
    current_zone  = profile.get("zone","")

    st.markdown("""
    <p style="font-size:.82rem;font-weight:700;color:#555;
               text-transform:uppercase;letter-spacing:.06em;margin-bottom:.6rem;">
        Personal Information
    </p>
    """, unsafe_allow_html=True)

    with st.form("courier_profile_form"):
        new_name = st.text_input("Full name", value=current_name, placeholder="Your full name", key="settings_name")
        st.text_input("Email address (read-only)", value=current_email, disabled=True, key="settings_email")

        st.markdown("""
        <p style="font-size:.82rem;font-weight:700;color:#555;
                   text-transform:uppercase;letter-spacing:.06em;margin:.8rem 0 .4rem;">
            Delivery Zone
        </p>
        <p style="font-size:.78rem;color:#999;margin-bottom:.6rem;">
            Select the zone you operate in. Orders from that zone will be prioritised for you.
        </p>
        """, unsafe_allow_html=True)

        zone_options = [""] + ZONES
        zone_labels  = ["— Select your zone —"] + ZONES
        zone_index   = zone_options.index(current_zone) if current_zone in zone_options else 0

        new_zone = st.selectbox(
            "My zone", options=zone_options,
            format_func=lambda x: zone_labels[zone_options.index(x)],
            index=zone_index, key="settings_zone"
        )
        submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

    if submitted:
        if not new_name.strip():
            st.error("⚠️ Name cannot be empty.")
        elif not new_zone:
            st.error("⚠️ Please select a delivery zone.")
        else:
            ok = update_user_profile(uid, {"name":new_name.strip(),"displayName":new_name.strip(),"zone":new_zone}, token)
            if ok:
                st.session_state.user_name = new_name.strip()
                st.success(f"✅ Profile saved — zone set to **{new_zone}**.")
                st.rerun()
            else:
                st.error("❌ Failed to save profile. Please try again.")

    if current_zone:
        st.markdown(f"""
        <div style="background:#FFF4F0;border-left:3px solid #FF6B35;border-radius:0 12px 12px 0;
                    padding:1rem;margin-top:1rem;">
            <p style="font-size:.85rem;font-weight:700;color:#FF6B35;margin:0 0 .2rem;">
                📍 Current zone: {current_zone}
            </p>
            <p style="font-size:.78rem;color:#999;margin:0;">
                You will receive delivery assignments for the <b>{current_zone}</b> area.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No zone set yet — orders may not be assigned to you.")


# ============================================================
# TAB 1 — QR CODES
# ============================================================
def _show_qr_tokens():
    st.subheader("🎫 My QR Codes")

    if st.button("🔄 Refresh", key="refresh_tokens"):
        st.rerun()

    tokens = get_courrier_tokens(st.session_state.user_id)

    if not tokens:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#999;">
            <div style="font-size:2.5rem;margin-bottom:.8rem;">📭</div>
            <p style="font-weight:600;color:#555;">No QR codes yet</p>
            <p style="font-size:.85rem;">QR codes appear here once a user places an order.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    total   = len(tokens)
    used_c  = sum(1 for t in tokens.values() if t.get("usedAt",""))
    pending = total - used_c

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total",   total)
    col2.metric("✅ Used",    used_c)
    col3.metric("⏳ Pending", pending)

    st.markdown("---")

    for token_id, td in tokens.items():
        is_used = bool(td.get("usedAt",""))

        if is_used:
            badge_bg = "#FFD9D9"; badge_color = "#8B2020"; badge_text = "Used"
            card_accent = "#FFC5C5"
        else:
            badge_bg = "#C6F7E2"; badge_color = "#0B6B42"; badge_text = "Active"
            card_accent = "#FF6B35"

        st.markdown(f"""
        <div style="background:#1A1A1A;border-radius:20px;padding:1.4rem 1.5rem;
                    margin:.8rem 0;position:relative;overflow:hidden;">
            <div style="position:absolute;top:-30px;right:-30px;width:120px;height:120px;
                        background:rgba(255,107,53,.2);border-radius:50%;pointer-events:none;"></div>
            <div style="position:absolute;top:1.2rem;right:1.3rem;
                        background:{badge_bg};color:{badge_color};
                        border:1px solid {badge_color}44;padding:.25rem .7rem;
                        border-radius:40px;font-size:.7rem;font-weight:700;letter-spacing:.05em;
                        text-transform:uppercase;">
                {badge_text}
            </div>
            <p style="font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
                      color:rgba(255,255,255,.45);margin:0 0 .4rem;">Delivery Token</p>
            <p style="font-family:'Instrument Serif',serif;font-size:1.5rem;font-style:italic;
                      color:white;margin:0 0 1rem;">{token_id}</p>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;">
                <div>
                    <p style="font-size:.65rem;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.06em;margin:0 0 .1rem;">Locker</p>
                    <p style="font-size:.82rem;font-weight:600;color:rgba(255,255,255,.9);margin:0;">{td.get('lockerName', td.get('lockerId','—'))}</p>
                </div>
                <div>
                    <p style="font-size:.65rem;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.06em;margin:0 0 .1rem;">Product</p>
                    <p style="font-size:.82rem;font-weight:600;color:rgba(255,255,255,.9);margin:0;">{td.get('produit','—')}</p>
                </div>
                <div>
                    <p style="font-size:.65rem;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.06em;margin:0 0 .1rem;">Client</p>
                    <p style="font-size:.78rem;font-weight:600;color:rgba(255,255,255,.9);margin:0;overflow:hidden;text-overflow:ellipsis;">{td.get('userEmail','—')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if QR_AVAILABLE:
            qr_bytes = generate_qr_bytes(token_id)
            st.image(qr_bytes, width=180, caption=f"Scan to unlock · {token_id}")

        if not is_used:
            if st.button("✅ Mark as Used", key=f"use_{token_id}"):
                mark_token_used(token_id, td.get("bookingId",""))
                if td.get("lockerId"):
                    set_locker_available(td["lockerId"])
                st.success(f"✅ Token {token_id} marked as used!")
                st.rerun()

        st.markdown("---")


# ============================================================
# TAB 2 — PENDING DELIVERIES
# ============================================================
def _show_pending_bookings():
    st.subheader("📦 Pending Deliveries")

    if st.button("🔄 Refresh", key="refresh_courier"):
        st.rerun()

    bookings = get_bookings_for_courrier()

    if not bookings:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#999;">
            <div style="font-size:2.5rem;margin-bottom:.8rem;">✅</div>
            <p style="font-weight:600;color:#555;">All caught up!</p>
            <p style="font-size:.85rem;">No deliveries pending right now.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"<p style='font-size:.82rem;color:#999;'><b style='color:#FF6B35;'>{len(bookings)}</b> delivery(ies) to process</p>", unsafe_allow_html=True)

    for b in bookings:
        with st.expander(f"📦 #{b.get('booking_id','—')} — {b.get('produit','—')} · {b.get('user_name','—')}"):
            col_info, col_qr = st.columns([2,1])

            with col_info:
                for label, val in [
                    ("👤 Client",      b.get('user_name','—')),
                    ("📧 Email",       b.get('user_email','—')),
                    ("🛍️ Product",    b.get('produit','—')),
                    ("⚖️ Weight",      f"{b.get('poids_kg','—')} kg"),
                    ("📝 Description", b.get('description','—')),
                    ("🔒 Locker",      b.get('locker_name','—')),
                    ("🗺️ Zone",       b.get('locker_zone','—')),
                    ("📅 Ordered",     b.get('timestamp','—')),
                ]:
                    st.markdown(f"**{label}:** {val}")

            with col_qr:
                st.markdown("**📱 QR Code**")
                if QR_AVAILABLE:
                    qr_data = {k: b.get(k) for k in ["booking_id","user_name","user_email","locker_name","locker_zone","produit","description","timestamp","statut"]}
                    try:
                        qr_b64 = generate_qr_code(qr_data)
                        st.markdown(f'<img src="data:image/png;base64,{qr_b64}" width="140"/>', unsafe_allow_html=True)
                    except:
                        st.warning("QR unavailable")
                else:
                    st.info("Install qrcode[pil]")

            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                if st.button("🚚 Mark In Progress", key=f"encours_{b['id']}"):
                    update_booking_status(b["id"],"en_cours"); st.success("✅ Status updated!"); st.rerun()
            with col_btn2:
                if st.button("✅ Mark Delivered", key=f"livre_{b['id']}"):
                    update_booking_status(b["id"],"livré"); set_locker_available(b["locker_id"])
                    st.success("✅ Delivery confirmed — locker released."); st.rerun()


# ============================================================
# TAB 3 — HISTORY
# ============================================================
def _show_delivered_bookings():
    st.subheader("✅ Delivery History")

    done = get_all_delivered_bookings()

    if not done:
        st.markdown("""
        <div style="text-align:center;padding:3rem 1rem;color:#999;">
            <div style="font-size:2.5rem;margin-bottom:.8rem;">📋</div>
            <p style="font-weight:600;color:#555;">No history yet</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"<p style='font-size:.82rem;color:#999;margin-bottom:.8rem;'>{len(done)} delivery(ies) completed</p>", unsafe_allow_html=True)

    for b in sorted(done, key=lambda x: x.get("timestamp",""), reverse=True):
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #EBEBEB;border-radius:16px;
                    padding:1rem 1.2rem;margin:.65rem 0;
                    border-left:3px solid #22C87A;">
            <p style="font-size:.95rem;font-weight:700;color:#1A1A1A;margin:0 0 .2rem;">
                #{b.get('booking_id','—')} — {b.get('produit','—')}
            </p>
            <p style="font-size:.76rem;color:#AAA;margin:0;">
                👤 {b.get('user_name','—')} · 🔒 {b.get('locker_name','—')} · 🗺️ {b.get('locker_zone','—')}
            </p>
            <p style="font-size:.76rem;margin:.3rem 0 0;">
                📅 {b.get('timestamp','—')} &nbsp;
                <span style="background:#E6FBF2;color:#0B6B42;border:1.5px solid #AEEFD1;
                              padding:.15rem .6rem;border-radius:40px;font-size:.7rem;font-weight:700;">
                    Delivered
                </span>
            </p>
        </div>
        """, unsafe_allow_html=True)
