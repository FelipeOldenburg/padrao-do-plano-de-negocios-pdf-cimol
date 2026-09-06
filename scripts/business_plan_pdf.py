#!/usr/bin/env python3
"""
Gera um PDF de Plano de Negócios no padrão visual CIMOL.

Uso:
  python scripts/business_plan_pdf.py --input examples/cimol.sample.json --output plano_negocios.pdf
  python scripts/business_plan_pdf.py --input plano.json --output plano.pdf --qr1 qr_github.png --qr2 qr_app.png
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape

from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# -----------------------------
# Visual tokens do padrão CIMOL
# -----------------------------
NAVY = colors.HexColor("#0F172A")
DEEP_BLUE = colors.HexColor("#0B2447")
SLATE = colors.HexColor("#334155")
MUTED = colors.HexColor("#64748B")
ACCENT = colors.HexColor("#E0EAFF")
GREEN = colors.HexColor("#DCFCE7")
BORDER = colors.HexColor("#CBD5E1")
WHITE = colors.white

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.35 * cm

BODY_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"


def color(value: Any, fallback: colors.Color) -> colors.Color:
    """Converte uma cor hexadecimal do briefing, preservando um fallback seguro."""
    try:
        return colors.HexColor(str(value)) if value else fallback
    except (TypeError, ValueError):
        return fallback


def apply_branding(data: dict[str, Any]) -> dict[str, Any]:
    """Aplica a paleta opcional do projeto sem perder o tema CIMOL como padrão."""
    global NAVY, DEEP_BLUE, SLATE, MUTED, ACCENT, GREEN, BORDER
    branding = data.get("branding", {})
    NAVY = color(branding.get("primary_color"), colors.HexColor("#0F172A"))
    DEEP_BLUE = color(branding.get("secondary_color"), colors.HexColor("#0B2447"))
    SLATE = color(branding.get("text_color"), colors.HexColor("#334155"))
    MUTED = color(branding.get("muted_color"), colors.HexColor("#64748B"))
    ACCENT = color(branding.get("accent_color"), colors.HexColor("#E0EAFF"))
    GREEN = color(branding.get("highlight_color"), colors.HexColor("#DCFCE7"))
    BORDER = color(branding.get("border_color"), colors.HexColor("#CBD5E1"))
    return branding


def register_fonts() -> None:
    """Registra uma fonte com suporte bom a acentos, com fallback seguro."""
    global BODY_FONT, BOLD_FONT
    windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ),
        (str(windows_fonts / "arial.ttf"), str(windows_fonts / "arialbd.ttf")),
    ]
    for regular, bold in candidates:
        if os.path.exists(regular) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont("AppRegular", regular))
            pdfmetrics.registerFont(TTFont("AppBold", bold))
            BODY_FONT = "AppRegular"
            BOLD_FONT = "AppBold"
            return


def make_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    return {
        "small": ParagraphStyle(
            name="Small",
            fontName=BODY_FONT,
            fontSize=8.4,
            leading=10.2,
            textColor=SLATE,
        ),
        "body": ParagraphStyle(
            name="Body",
            fontName=BODY_FONT,
            fontSize=9.3,
            leading=12.2,
            textColor=SLATE,
            spaceAfter=4,
        ),
        "title_main": ParagraphStyle(
            name="TitleMain",
            fontName=BOLD_FONT,
            fontSize=24,
            leading=28,
            textColor=WHITE,
        ),
        "subtitle": ParagraphStyle(
            name="SubTitle",
            fontName=BODY_FONT,
            fontSize=11,
            leading=14,
            textColor=WHITE,
        ),
        "section": ParagraphStyle(
            name="Section",
            fontName=BOLD_FONT,
            fontSize=14,
            leading=16,
            textColor=NAVY,
            spaceAfter=6,
        ),
        "mini_head": ParagraphStyle(
            name="MiniHead",
            fontName=BOLD_FONT,
            fontSize=10.2,
            leading=12,
            textColor=NAVY,
            spaceAfter=4,
        ),
        "card_title": ParagraphStyle(
            name="CardTitle",
            fontName=BOLD_FONT,
            fontSize=10.4,
            leading=12,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "card_text": ParagraphStyle(
            name="CardText",
            fontName=BODY_FONT,
            fontSize=8.5,
            leading=10.5,
            textColor=SLATE,
            alignment=TA_CENTER,
        ),
        "center_small": ParagraphStyle(
            name="CenterSmall",
            fontName=BODY_FONT,
            fontSize=8.3,
            leading=10,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "qr_title": ParagraphStyle(
            name="QRTitle",
            fontName=BOLD_FONT,
            fontSize=11,
            leading=13,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
    }


def text(value: Any) -> str:
    return escape(str(value or "")).replace("\n", "<br/>")


def p(value: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text(value), style)


def pbold(value: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f"<b>{text(value)}</b>", style)


def bullets(items: Iterable[str], styles: dict[str, ParagraphStyle], max_items: int | None = None) -> Paragraph:
    chosen = list(items or [])
    if max_items is not None:
        chosen = chosen[:max_items]
    html = "<br/>".join([f"• {text(item)}" for item in chosen])
    return Paragraph(html, styles["body"])


def table_style(header_rows: int = 1) -> TableStyle:
    ops = [
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header_rows:
        ops.append(("BACKGROUND", (0, 0), (-1, header_rows - 1), ACCENT))
    return TableStyle(ops)


def centered(table: Table) -> Table:
    """Mantém a tabela afastada das bordas e visualmente equilibrada."""
    table.hAlign = "CENTER"
    return table


def cover_logo_path(data: dict[str, Any]) -> str | None:
    """Valida a logo opcional usada para decorar a capa."""
    logo_path = data.get("branding", {}).get("logo_path")
    if not logo_path:
        return None
    path = Path(str(logo_path))
    if not path.is_file():
        raise FileNotFoundError(f"Logo não encontrada: {path}")
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("A logo deve estar em PNG ou JPG.")
    try:
        with PILImage.open(path) as logo:
            logo.verify()
    except (OSError, ValueError) as error:
        raise ValueError(f"Não foi possível ler a logo: {path}") from error
    return str(path)


def draw_cover_logo(c, logo_path: str) -> None:
    """Desenha a logo sobre um cartão claro para preservar contraste na capa."""
    logo = ImageReader(logo_path)
    original_width, original_height = logo.getSize()
    max_width, max_height = 3.0 * cm, 1.35 * cm
    scale = min(max_width / original_width, max_height / original_height)
    width, height = original_width * scale, original_height * scale
    card_x, card_y = 1.35 * cm, PAGE_HEIGHT - 2.45 * cm
    card_width, card_height = max_width + 0.45 * cm, max_height + 0.45 * cm
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.96))
    c.roundRect(card_x, card_y, card_width, card_height, 0.14 * cm, stroke=0, fill=1)
    c.drawImage(
        logo,
        card_x + (card_width - width) / 2,
        card_y + (card_height - height) / 2,
        width=width,
        height=height,
        mask="auto",
    )


def cover_canvas(c, doc, data: dict[str, Any]) -> None:
    branding = data.get("branding", {})
    cover_style = str(branding.get("cover_style", "geometric")).lower()
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, PAGE_HEIGHT - 7.5 * cm, PAGE_WIDTH, 7.5 * cm, stroke=0, fill=1)
    c.setFillColor(DEEP_BLUE)
    c.rect(0, PAGE_HEIGHT - 9.0 * cm, PAGE_WIDTH, 1.5 * cm, stroke=0, fill=1)
    if cover_style == "bold":
        c.setFillColor(ACCENT)
        c.rect(PAGE_WIDTH - 3.0 * cm, PAGE_HEIGHT - 7.5 * cm, 3.0 * cm, 7.5 * cm, stroke=0, fill=1)
    elif cover_style != "minimal":
        c.setFillColor(colors.Color(1, 1, 1, alpha=0.08))
        c.circle(PAGE_WIDTH - 2.2 * cm, PAGE_HEIGHT - 2.0 * cm, 2.6 * cm, fill=1, stroke=0)
        c.circle(PAGE_WIDTH - 5.0 * cm, PAGE_HEIGHT - 4.0 * cm, 1.2 * cm, fill=1, stroke=0)
    if branding.get("cover_label"):
        c.setFont(BOLD_FONT, 8)
        c.setFillColor(WHITE)
        c.drawRightString(PAGE_WIDTH - 1.4 * cm, PAGE_HEIGHT - 0.8 * cm, str(branding["cover_label"]))
    logo_path = cover_logo_path(data)
    if logo_path:
        draw_cover_logo(c, logo_path)

    c.setStrokeColor(BORDER)
    c.line(1.3 * cm, 1.1 * cm, PAGE_WIDTH - 1.3 * cm, 1.1 * cm)
    c.setFont(BODY_FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(1.4 * cm, 0.72 * cm, data.get("cover_footer", "Documento sintético - máximo de 5 páginas"))
    c.drawRightString(PAGE_WIDTH - 1.4 * cm, 0.72 * cm, "Página 1")
    c.restoreState()


def inside_canvas(c, doc, data: dict[str, Any]) -> None:
    page = c.getPageNumber()
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, PAGE_HEIGHT - 1.3 * cm, PAGE_WIDTH, 1.3 * cm, stroke=0, fill=1)
    c.setFont(BOLD_FONT, 10)
    c.setFillColor(WHITE)
    c.drawString(1.4 * cm, PAGE_HEIGHT - 0.85 * cm, f"{data.get('title', 'Plano de Negócios')} | {data.get('project_name', 'Projeto')}")

    c.setStrokeColor(BORDER)
    c.line(1.3 * cm, 1.1 * cm, PAGE_WIDTH - 1.3 * cm, 1.1 * cm)
    c.setFont(BODY_FONT, 8)
    c.setFillColor(MUTED)
    c.drawString(1.4 * cm, 0.72 * cm, data.get("updated_label", "Atualizado"))
    c.drawRightString(PAGE_WIDTH - 1.4 * cm, 0.72 * cm, f"Página {page}")
    c.restoreState()


def placeholder_image(label: str, size_px: int = 900) -> str:
    """Cria um PNG temporário simples para quando o QR code não foi passado."""
    temp_dir = Path(tempfile.gettempdir()) / "business_plan_pdf_placeholders"
    temp_dir.mkdir(exist_ok=True)
    path = temp_dir / f"{label.lower().replace(' ', '_')}.png"
    img = PILImage.new("RGB", (size_px, size_px), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, size_px - 20, size_px - 20), outline="black", width=6)
    message = f"{label}\nQR não informado"
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        str(Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arialbd.ttf"),
    ]
    font = next(
        (ImageFont.truetype(path, 54) for path in font_paths if Path(path).exists()),
        ImageFont.load_default(),
    )
    lines = message.split("\n")
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    total_h = sum(line_heights) + 22 * (len(lines) - 1)
    y = (size_px - total_h) / 2
    for line, w, h in zip(lines, line_widths, line_heights):
        draw.text(((size_px - w) / 2, y), line, fill="black", font=font)
        y += h + 22
    img.save(path)
    return str(path)


def qr_image(path: str | None, label: str) -> Image:
    if path:
        if not Path(path).exists():
            raise FileNotFoundError(f"Imagem de QR code não encontrada: {path}")
        return Image(path, width=6.1 * cm, height=6.1 * cm)
    return Image(placeholder_image(label), width=6.1 * cm, height=6.1 * cm)


def build_pdf(data: dict[str, Any], output: str, qr1: str | None = None, qr2: str | None = None) -> None:
    apply_branding(data)
    cover_logo_path(data)
    register_fonts()
    styles = make_styles()
    story: list[Any] = []

    # Página 1
    story.append(Spacer(1, 2.1 * cm))
    story.append(Paragraph(text(data.get("title", "Plano de Negócios")), styles["title_main"]))
    story.append(Spacer(1, 0.18 * cm))
    story.append(Paragraph(text(data.get("project_name", "Projeto")), styles["title_main"]))
    story.append(Spacer(1, 0.28 * cm))
    story.append(Paragraph(text(data.get("subtitle", "")), styles["subtitle"]))
    story.append(Spacer(1, 2.2 * cm))

    cards = data.get("summary_cards", [])[:4]
    while len(cards) < 4:
        cards.append({"label": "Resumo", "text": "Preencher informação principal do plano."})

    card_rows = [[pbold(card.get("label"), styles["card_title"]), p(card.get("text"), styles["card_text"])] for card in cards]
    card_table = Table(card_rows, colWidths=[4.0 * cm, 10.7 * cm], rowHeights=[1.2 * cm, 1.85 * cm, 1.85 * cm, 1.85 * cm])
    card_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), ACCENT),
        ("BACKGROUND", (1, 0), (1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(centered(card_table))
    story.append(Spacer(1, 0.45 * cm))
    story.append(Paragraph(text(data.get("value_proposition", "")), styles["center_small"]))
    story.append(PageBreak())

    # Página 2
    page2 = data.get("page2", {})
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("1. Oportunidade, problema e solução", styles["section"]))

    def section_blocks(sections: list[dict[str, Any]], limit_bullets: int = 4) -> list[Any]:
        blocks: list[Any] = []
        for sec in sections:
            blocks.append(pbold(sec.get("title", "Seção"), styles["mini_head"]))
            if sec.get("paragraphs"):
                for paragraph in sec.get("paragraphs", [])[:3]:
                    blocks.append(p(paragraph, styles["body"]))
            if sec.get("bullets"):
                blocks.append(bullets(sec.get("bullets", []), styles, max_items=limit_bullets))
        return blocks

    p2_left = section_blocks(page2.get("left_sections", []), 4)
    p2_right = section_blocks(page2.get("right_sections", []), 4)
    page2_table = Table([[p2_left, p2_right]], colWidths=[8.1 * cm, 8.1 * cm])
    page2_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(centered(page2_table))
    story.append(Spacer(1, 0.25 * cm))
    story.append(pbold("Diferenciais competitivos", styles["mini_head"]))
    diffs = page2.get("differentials", [])[:4]
    diff_rows = [[pbold("Diferencial", styles["small"]), pbold("Impacto", styles["small"])]]
    for item in diffs:
        diff_rows.append([p(item.get("differential"), styles["small"]), p(item.get("impact"), styles["small"])])
    diff_table = Table(diff_rows, colWidths=[5.0 * cm, 11.2 * cm])
    diff_table.setStyle(table_style())
    story.append(centered(diff_table))
    story.append(PageBreak())

    # Página 3
    page3 = data.get("page3", {})
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("2. Modelo de negócio, produto e operação", styles["section"]))

    story.append(pbold("Modelo de negócio", styles["mini_head"]))
    bm_rows = [[pbold("Fonte de receita", styles["small"]), pbold("Descrição", styles["small"])]]
    for row in page3.get("business_model", [])[:3]:
        bm_rows.append([p(row.get("source"), styles["small"]), p(row.get("description"), styles["small"])])
    bm_table = Table(bm_rows, colWidths=[4.8 * cm, 11.4 * cm])
    bm_table.setStyle(table_style())
    story.append(centered(bm_table))
    story.append(Spacer(1, 0.2 * cm))

    story.append(pbold("Pacotes sugeridos", styles["mini_head"]))
    pk_rows = [[pbold("Plano", styles["small"]), pbold("Preço", styles["small"]), pbold("Indicado para", styles["small"])]]
    for row in page3.get("pricing_packages", [])[:3]:
        pk_rows.append([p(row.get("plan"), styles["small"]), p(row.get("price"), styles["small"]), p(row.get("fit"), styles["small"])])
    pk_table = Table(pk_rows, colWidths=[3.0 * cm, 5.6 * cm, 7.6 * cm])
    pk_table.setStyle(table_style())
    story.append(centered(pk_table))
    story.append(Spacer(1, 0.25 * cm))

    story.append(pbold("O que já foi consolidado no projeto", styles["mini_head"]))
    story.append(bullets(page3.get("consolidated", []), styles, max_items=3))

    story.append(pbold("Operação e roadmap", styles["mini_head"]))
    rd_rows = [[pbold("Fase", styles["small"]), pbold("Meta", styles["small"])]]
    for row in page3.get("roadmap", [])[:3]:
        rd_rows.append([p(row.get("phase"), styles["small"]), p(row.get("goal"), styles["small"])])
    rd_table = Table(rd_rows, colWidths=[2.7 * cm, 13.1 * cm])
    rd_table.setStyle(table_style())
    story.append(centered(rd_table))
    story.append(PageBreak())

    # Página 4
    page4 = data.get("page4", {})
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("3. Estratégia comercial e projeção financeira", styles["section"]))

    p4_left = section_blocks(page4.get("left_sections", []), 3)

    proj_rows = [[pbold("Item", styles["small"]), pbold("Valor estimado", styles["small"])]]
    highlight_row_indexes: list[int] = []
    for idx, row in enumerate(page4.get("projection", [])[:9], start=1):
        proj_rows.append([pbold(row.get("item"), styles["small"]) if row.get("highlight") else p(row.get("item"), styles["small"]),
                          pbold(row.get("value"), styles["small"]) if row.get("highlight") else p(row.get("value"), styles["small"])])
        if row.get("highlight"):
            highlight_row_indexes.append(idx)
    proj_table = Table(proj_rows, colWidths=[4.6 * cm, 3.4 * cm])
    proj_ops = list(table_style().getCommands())
    for row_index in highlight_row_indexes:
        proj_ops.append(("BACKGROUND", (0, row_index), (-1, row_index), GREEN))
    proj_table.setStyle(TableStyle(proj_ops))

    inv = page4.get("investment", {})
    inv_rows = [
        [pbold("Investimento inicial sugerido", styles["small"]), pbold("Uso", styles["small"])],
        [p(inv.get("amount"), styles["small"]), p(inv.get("use"), styles["small"])],
    ]
    inv_table = Table(inv_rows, colWidths=[2.8 * cm, 5.2 * cm])
    inv_table.setStyle(table_style())

    p4_right = [pbold("Projeção resumida - 12 meses", styles["mini_head"]), proj_table, Spacer(1, 0.18 * cm), pbold("Investimento", styles["mini_head"]), inv_table]
    p4_table = Table([[p4_left, p4_right]], colWidths=[8.1 * cm, 8.1 * cm])
    p4_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(centered(p4_table))
    story.append(Spacer(1, 0.3 * cm))
    story.append(p(page4.get("executive_conclusion", ""), styles["body"]))
    story.append(PageBreak())

    # Página 5
    page5 = data.get("page5", {})
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph(text(page5.get("title", "4. Anexos")), styles["section"]))
    story.append(p(page5.get("intro", ""), styles["body"]))
    story.append(Spacer(1, 0.35 * cm))

    qr_cards = page5.get("qr_cards", [])
    while len(qr_cards) < 2:
        qr_cards.append({"title": f"QR Code {len(qr_cards) + 1}", "subtitle": ""})
    qr_paths = [qr1 or qr_cards[0].get("path"), qr2 or qr_cards[1].get("path")]
    imgs = [qr_image(qr_paths[0], "QR Code 1"), qr_image(qr_paths[1], "QR Code 2")]
    titles = [
        Paragraph(f"{text(qr_cards[0].get('title', 'QR Code 1'))}<br/><font size='8'>{text(qr_cards[0].get('subtitle', ''))}</font>", styles["qr_title"]),
        Paragraph(f"{text(qr_cards[1].get('title', 'QR Code 2'))}<br/><font size='8'>{text(qr_cards[1].get('subtitle', ''))}</font>", styles["qr_title"]),
    ]
    qr_table = Table([imgs, titles], colWidths=[7.5 * cm, 7.5 * cm])
    qr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("ALIGN", (0, 1), (-1, 1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(centered(qr_table))
    story.append(Spacer(1, 0.45 * cm))
    story.append(p(page5.get("sources", ""), styles["small"]))

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )
    doc.build(
        story,
        onFirstPage=lambda c, d: cover_canvas(c, d, data),
        onLaterPages=lambda c, d: inside_canvas(c, d, data),
    )


def assert_page_count(output: str, expected: int = 5) -> None:
    try:
        from pypdf import PdfReader
    except Exception:
        print("Aviso: pypdf não instalado; não foi possível verificar a quantidade de páginas.", file=sys.stderr)
        return
    pages = len(PdfReader(output).pages)
    if pages != expected:
        raise RuntimeError(f"O PDF gerado ficou com {pages} páginas; o padrão exige {expected} páginas. Resuma o conteúdo do JSON e gere novamente.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera PDF de plano de negócios no padrão CIMOL.")
    parser.add_argument("--input", required=True, help="Arquivo JSON com o conteúdo do plano.")
    parser.add_argument("--output", required=True, help="Caminho do PDF final.")
    parser.add_argument("--qr1", default=None, help="Imagem do QR code 1.")
    parser.add_argument("--qr2", default=None, help="Imagem do QR code 2.")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    branding = data.get("branding", {})
    if branding.get("logo_path"):
        logo_path = Path(str(branding["logo_path"]))
        if not logo_path.is_absolute():
            branding["logo_path"] = str((input_path.parent / logo_path).resolve())

    build_pdf(data, args.output, qr1=args.qr1, qr2=args.qr2)

    assert_page_count(args.output, expected=5)

    print(f"PDF criado: {args.output}")


if __name__ == "__main__":
    main()
