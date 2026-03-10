import json
from io import BytesIO
import base64

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ============================================================
# GÉNÉRATION QR CODE
# ============================================================
def generate_qr_code(data: dict) -> str:
    """Génère un QR code à partir d'un dict et retourne une image base64."""
    if not QR_AVAILABLE:
        return None
    qr = qrcode.QRCode(version=1, box_size=6, border=3)
    qr.add_data(json.dumps(data, ensure_ascii=False))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()
