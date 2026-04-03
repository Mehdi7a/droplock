import json
import smtplib
import random
import string
import base64
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ============================================================
# QR CODE — returns PNG bytes
# ============================================================
def generate_qr_bytes(token_id: str) -> bytes:
    if not QR_AVAILABLE:
        return b""
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(token_id)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a2e", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ============================================================
# QR CODE — returns base64 string
# ============================================================
def generate_qr_code(data: dict) -> str:
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(version=1, box_size=6, border=3)
    qr.add_data(json.dumps(data, ensure_ascii=False))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# ============================================================
# UNIQUE TOKEN GENERATOR
# ============================================================
def generate_token_id() -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"QR-S1-{suffix}"

# ============================================================
# SEND EMAIL WITH INLINE QR CODE
# ============================================================
def send_email_with_qr(to_email: str, token_id: str, qr_bytes: bytes,
                       booking_info: dict, has_account: bool = True,
                       gmail_sender: str = "", gmail_pass: str = ""):
    """
    Sends an HTML email with an inline QR code image via Gmail SMTP SSL.
    Returns (True, None) on success, (False, error_str) on failure.
    """
    if not to_email or "@" not in to_email:
        return False, "Invalid recipient email address."

    if not gmail_sender or not gmail_pass:
        return False, "Gmail credentials not configured."

    try:
        account_msg = (
            "Log in to your Droplock account to view the QR code in real time."
            if has_account else
            "You don't have a Droplock account yet. Your QR code is displayed below."
        )

        html_body = f"""
<html>
<body style="font-family:Arial,sans-serif;background:#f0f2f6;padding:20px;margin:0;">
<div style="max-width:520px;margin:auto;background:white;border-radius:16px;
            padding:2rem;box-shadow:0 4px 20px rgba(0,0,0,0.1);">

  <div style="text-align:center;background:#1a1a2e;color:white;
              padding:1.5rem;border-radius:12px;margin-bottom:1.5rem;">
    <h2 style="margin:0;font-size:1.6rem;">&#128274; Droplock</h2>
    <p style="margin:0.5rem 0 0;font-size:0.95rem;">New delivery assigned</p>
  </div>

  <h3 style="color:#1a1a2e;">Order Details</h3>
  <table style="width:100%;border-collapse:collapse;font-size:0.95rem;">
    <tr style="background:#f8f9fa;">
      <td style="padding:10px;font-weight:bold;width:40%;">Client</td>
      <td style="padding:10px;">{booking_info.get('user_email', '-')}</td>
    </tr>
    <tr>
      <td style="padding:10px;font-weight:bold;">Product</td>
      <td style="padding:10px;">{booking_info.get('produit', '-')}</td>
    </tr>
    <tr style="background:#f8f9fa;">
      <td style="padding:10px;font-weight:bold;">Locker</td>
      <td style="padding:10px;">{booking_info.get('locker_name', '-')}</td>
    </tr>
    <tr>
      <td style="padding:10px;font-weight:bold;">Date</td>
      <td style="padding:10px;">{booking_info.get('timestamp', '-')}</td>
    </tr>
    <tr style="background:#f8f9fa;">
      <td style="padding:10px;font-weight:bold;">QR Status</td>
      <td style="padding:10px;color:#28a745;font-weight:bold;">Not used yet</td>
    </tr>
  </table>

  <hr style="margin:1.5rem 0;border:none;border-top:1px solid #eee;">

  <h3 style="color:#1a1a2e;">Your QR Token</h3>
  <div style="background:#f8f9fa;border:2px dashed #1a1a2e;border-radius:8px;
              padding:1rem;text-align:center;font-family:monospace;
              font-size:1.4rem;font-weight:bold;color:#1a1a2e;
              letter-spacing:2px;margin-bottom:1rem;">
    {token_id}
  </div>

  <p style="color:#555;font-size:0.9rem;">{account_msg}</p>
"""

        # Only embed QR image if we have bytes
        if qr_bytes:
            html_body += """
  <div style="text-align:center;margin:1.2rem 0;">
    <img src="cid:qrcode_image"
         width="200" height="200"
         style="border-radius:8px;border:2px solid #eee;display:block;margin:auto;"
         alt="QR Code"/>
  </div>
"""

        html_body += f"""
  <p style="color:#aaa;font-size:0.78rem;text-align:center;margin-top:1.5rem;
            border-top:1px solid #eee;padding-top:1rem;">
    Automated message sent by Droplock &mdash; Please do not reply to this email.
  </p>
</div>
</body>
</html>
"""

        plain_text = (
            f"Droplock - New delivery\n"
            f"Token: {token_id}\n"
            f"Product: {booking_info.get('produit','-')}\n"
            f"Locker: {booking_info.get('locker_name','-')}\n"
            f"Date: {booking_info.get('timestamp','-')}\n"
        )

        # Build message: multipart/related (for inline image)
        msg_root = MIMEMultipart("related")
        msg_root["Subject"] = f"Droplock - New delivery [{token_id}]"
        msg_root["From"]    = gmail_sender
        msg_root["To"]      = to_email

        # Alternative: plain text + HTML
        msg_alt = MIMEMultipart("alternative")
        msg_alt.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg_alt.attach(MIMEText(html_body, "html", "utf-8"))
        msg_root.attach(msg_alt)

        # Attach inline QR image
        if qr_bytes:
            qr_img = MIMEImage(qr_bytes, _subtype="png")
            qr_img.add_header("Content-ID", "<qrcode_image>")
            qr_img.add_header("Content-Disposition", "inline", filename="qrcode.png")
            msg_root.attach(qr_img)

        # Send via Gmail SMTP SSL on port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(gmail_sender, gmail_pass)
            server.sendmail(gmail_sender, [to_email], msg_root.as_string())

        return True, None

    except smtplib.SMTPAuthenticationError:
        return False, "Gmail authentication failed. Check your App Password in config.py."
    except smtplib.SMTPRecipientsRefused:
        return False, f"Recipient address refused by server: {to_email}"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        import traceback
        print(f"[send_email_with_qr] ERROR: {e}\n{traceback.format_exc()}")
        return False, str(e)
