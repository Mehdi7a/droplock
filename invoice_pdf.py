from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


# ============================================================
# COULEURS DROPLOCK
# ============================================================
DARK_BLUE  = colors.HexColor("#1a1a2e")
MID_BLUE   = colors.HexColor("#16213e")
ACCENT     = colors.HexColor("#2196F3")
SUCCESS    = colors.HexColor("#28a745")
LIGHT_GRAY = colors.HexColor("#f8f9fa")
BORDER     = colors.HexColor("#dee2e6")
TEXT_GRAY  = colors.HexColor("#6c757d")
WHITE      = colors.white


def generate_invoice_pdf(booking_data: dict, token_id: str) -> bytes:
    """
    Génère une facture PDF pour une commande Droplock.
    Retourne les bytes du PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=1.5*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Styles personnalisés
    title_style = ParagraphStyle(
        "DroplockTitle",
        parent=styles["Normal"],
        fontSize=28,
        fontName="Helvetica-Bold",
        textColor=WHITE,
        alignment=TA_CENTER,
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        "DroplockSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica",
        textColor=colors.HexColor("#b0c4de"),
        alignment=TA_CENTER
    )
    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Normal"],
        fontSize=13,
        fontName="Helvetica-Bold",
        textColor=DARK_BLUE,
        spaceBefore=12,
        spaceAfter=6
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=TEXT_GRAY
    )
    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=DARK_BLUE
    )
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        fontName="Helvetica",
        textColor=TEXT_GRAY,
        alignment=TA_CENTER
    )
    token_style = ParagraphStyle(
        "Token",
        parent=styles["Normal"],
        fontSize=16,
        fontName="Helvetica-Bold",
        textColor=DARK_BLUE,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=4
    )
    price_style = ParagraphStyle(
        "Price",
        parent=styles["Normal"],
        fontSize=20,
        fontName="Helvetica-Bold",
        textColor=SUCCESS,
        alignment=TA_CENTER
    )

    story = []

    # ── HEADER BANNER ─────────────────────────────────────
    header_data = [[
        Paragraph("🔒 Droplock", title_style),
    ]]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK_BLUE),
        ("ROUNDEDCORNERS", [12]),
        ("TOPPADDING",    (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(header_table)

    sub_data = [[Paragraph("Delivery Invoice", subtitle_style)]]
    sub_table = Table(sub_data, colWidths=[17*cm])
    sub_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), MID_BLUE),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 0.4*cm))

    # ── INVOICE META (numéro + date) ──────────────────────
    invoice_num = booking_data.get("booking_id", "—")
    invoice_date = datetime.now().strftime("%d/%m/%Y at %H:%M")

    meta_data = [
        [
            Paragraph(f"<b>Invoice #</b> {invoice_num}", value_style),
            Paragraph(f"<b>Date:</b> {invoice_date}", ParagraphStyle("R", parent=value_style, alignment=TA_RIGHT))
        ]
    ]
    meta_table = Table(meta_data, colWidths=[8.5*cm, 8.5*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LIGHT_GRAY),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4*cm))

    # ── ORDER DETAILS ─────────────────────────────────────
    story.append(Paragraph("📦 Order Details", section_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    order_rows = [
        ["Field", "Value"],
        ["Client",      booking_data.get("user_name", "—")],
        ["Email",       booking_data.get("user_email", "—")],
        ["Product",     booking_data.get("produit", "—")],
        ["Description", booking_data.get("description", "—") or "—"],
        ["Weight",      f"{booking_data.get('poids_kg', 0)} kg"],
        ["Order Date",  booking_data.get("timestamp", "—")],
        ["Status",      "⏳ Pending"],
    ]

    order_table = Table(
        [[Paragraph(str(r[0]), label_style), Paragraph(str(r[1]), value_style)] for r in order_rows],
        colWidths=[4.5*cm, 12.5*cm]
    )
    order_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  DARK_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(order_table)
    story.append(Spacer(1, 0.4*cm))

    # ── LOCKER & ZONE ─────────────────────────────────────
    story.append(Paragraph("🔒 Locker & Zone", section_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    locker_rows = [
        ["Field", "Value"],
        ["Locker Name", booking_data.get("locker_name", "—")],
        ["Zone / Sector", booking_data.get("locker_zone", "—")],
        ["Locker ID", booking_data.get("locker_id", "—")],
    ]
    locker_table = Table(
        [[Paragraph(str(r[0]), label_style), Paragraph(str(r[1]), value_style)] for r in locker_rows],
        colWidths=[4.5*cm, 12.5*cm]
    )
    locker_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  ACCENT),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(locker_table)
    story.append(Spacer(1, 0.4*cm))

    # ── COURIER ASSIGNED ──────────────────────────────────
    story.append(Paragraph("🚚 Assigned Courier", section_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    c_name  = booking_data.get("courrier_name", "—")
    c_email = booking_data.get("courrier_email", "—")

    courier_rows = [
        ["Field", "Value"],
        ["Courier Name",  c_name  if c_name  else "—"],
        ["Courier Email", c_email if c_email else "—"],
    ]
    courier_table = Table(
        [[Paragraph(str(r[0]), label_style), Paragraph(str(r[1]), value_style)] for r in courier_rows],
        colWidths=[4.5*cm, 12.5*cm]
    )
    courier_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  colors.HexColor("#6c757d")),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  10),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(courier_table)
    story.append(Spacer(1, 0.4*cm))

    # ── QR TOKEN ──────────────────────────────────────────
    story.append(Paragraph("🎫 QR Token", section_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    token_box = Table(
        [[Paragraph(token_id, token_style)]],
        colWidths=[17*cm]
    )
    token_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LIGHT_GRAY),
        ("BOX",           (0,0), (-1,-1), 2, DARK_BLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
    ]))
    story.append(token_box)
    story.append(Spacer(1, 0.4*cm))

    # ── PRICING SUMMARY ───────────────────────────────────
    story.append(Paragraph("💰 Pricing Summary", section_title))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=6))

    prix = booking_data.get("prix", 0)
    tva  = round(prix * 0.19, 2)
    total = round(prix + tva, 2)

    pricing_data = [
        [Paragraph("Description", label_style), Paragraph("Amount", ParagraphStyle("R2", parent=label_style, alignment=TA_RIGHT))],
        [Paragraph(f"Delivery fee ({booking_data.get('produit','—')})", value_style),
         Paragraph(f"{prix:.2f} TND", ParagraphStyle("R3", parent=value_style, alignment=TA_RIGHT))],
        [Paragraph("TVA (19%)", value_style),
         Paragraph(f"{tva:.2f} TND", ParagraphStyle("R4", parent=value_style, alignment=TA_RIGHT))],
        [Paragraph("<b>TOTAL</b>", ParagraphStyle("Bold", parent=value_style, fontName="Helvetica-Bold", fontSize=12)),
         Paragraph(f"<b>{total:.2f} TND</b>", ParagraphStyle("TotalR", parent=value_style, fontName="Helvetica-Bold", fontSize=12, alignment=TA_RIGHT, textColor=SUCCESS))],
    ]

    pricing_table = Table(pricing_data, colWidths=[12*cm, 5*cm])
    pricing_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  DARK_BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("ROWBACKGROUNDS",(0,1), (-1,-2), [WHITE, LIGHT_GRAY]),
        ("BACKGROUND",    (0,-1),(-1,-1), colors.HexColor("#e8f5e9")),
        ("BOX",           (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ]))
    story.append(pricing_table)
    story.append(Spacer(1, 0.6*cm))

    # ── FOOTER ────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))
    story.append(Paragraph(
        "This invoice was automatically generated by Droplock. "
        "Please keep it as proof of your order.",
        footer_style
    ))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"droplock.app@gmail.com  •  Generated on {invoice_date}",
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()
