"""
PDF Report Generator — produces a 7-page CSRD/ESRS DMA report using ReportLab.

Pages:
    1. Cover
    2. Executive Summary
    3–4. Full IRO table
    5. Materiality matrix image
    6. ESRS heatmap image
    7. Methodology appendix
"""

import os
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, PageBreak, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable

from src import __version__

# ── Colours ──────────────────────────────────────────────────────────────────
C_DARK_BLUE = colors.HexColor("#1F4E79")
C_MID_BLUE = colors.HexColor("#2E75B6")
C_GREEN_HEADER = colors.HexColor("#C6EFCE")
C_GREEN_TEXT = colors.HexColor("#375623")
C_RED_ROW = colors.HexColor("#FFCDD2")
C_ORANGE_ROW = colors.HexColor("#FFE0B2")
C_LIGHT_GREY = colors.HexColor("#F2F2F2")
C_BORDER = colors.HexColor("#BFBFBF")
C_WHITE = colors.white
C_BLACK = colors.black

# ── Font helper ───────────────────────────────────────────────────────────────
def _try_font() -> str:
    """Return 'Helvetica' (always available in ReportLab as fallback)."""
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        for path in [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/liberation/LiberationSerif-Regular.ttf",
        ]:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont("LiberationSerif", path))
                return "LiberationSerif"
    except Exception:
        pass
    return "Helvetica"


# ── Styles ────────────────────────────────────────────────────────────────────
def _build_styles(font: str) -> dict:
    base = getSampleStyleSheet()
    bold = font + "-Bold" if font == "Helvetica" else font

    styles = {
        "cover_title": ParagraphStyle(
            "cover_title", fontName=font, fontSize=24,
            textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=8,
            leading=30,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontName=font, fontSize=13,
            textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", fontName=font, fontSize=10,
            textColor=colors.HexColor("#DDDDDD"), alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "h1", fontName=font, fontSize=16,
            textColor=C_DARK_BLUE, spaceAfter=10, spaceBefore=6,
        ),
        "h2": ParagraphStyle(
            "h2", fontName=font, fontSize=12,
            textColor=C_MID_BLUE, spaceAfter=6, spaceBefore=4,
        ),
        "body": ParagraphStyle(
            "body", fontName=font, fontSize=9,
            textColor=C_BLACK, leading=14, alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "body_small": ParagraphStyle(
            "body_small", fontName=font, fontSize=8,
            textColor=colors.HexColor("#555555"), leading=12,
        ),
        "cell": ParagraphStyle(
            "cell", fontName=font, fontSize=7.5,
            textColor=C_BLACK, leading=10,
        ),
        "cell_bold": ParagraphStyle(
            "cell_bold", fontName=bold, fontSize=7.5,
            textColor=C_GREEN_TEXT, leading=10,
        ),
        "caption": ParagraphStyle(
            "caption", fontName=font, fontSize=8,
            textColor=colors.HexColor("#777777"), alignment=TA_CENTER,
            spaceAfter=4, spaceBefore=4,
        ),
        "footer": ParagraphStyle(
            "footer", fontName=font, fontSize=7,
            textColor=colors.HexColor("#999999"), alignment=TA_CENTER,
        ),
    }
    return styles


# ── Page template helpers ─────────────────────────────────────────────────────
def _make_doc(output_path: str) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id="main",
    )
    doc.addPageTemplates([PageTemplate(id="main", frames=frame)])
    return doc


# ── Cover page ────────────────────────────────────────────────────────────────
def _cover(company: str, year: int, styles: dict) -> list:
    story = []
    story.append(Spacer(1, 3 * cm))

    # Blue banner background via a table with background colour
    cover_data = [
        [Paragraph("Doppelte Wesentlichkeitsanalyse", styles["cover_title"])],
        [Paragraph(f"nach CSRD / ESRS &amp; EFRAG-Methodik", styles["cover_sub"])],
        [Spacer(1, 0.4 * cm)],
        [Paragraph(f"<b>{company}</b>", styles["cover_sub"])],
        [Paragraph(f"Berichtsjahr {year}", styles["cover_meta"])],
        [Spacer(1, 0.4 * cm)],
        [Paragraph(f"Erstellt am: {date.today().strftime('%d.%m.%Y')}", styles["cover_meta"])],
        [Paragraph(f"Tool-Version: v{__version__}", styles["cover_meta"])],
    ]
    t = Table(cover_data, colWidths=[15 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_DARK_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(t)
    story.append(Spacer(1, 1 * cm))

    story.append(Paragraph(
        "Dieses Dokument wurde automatisch mit dem Open-Source-Tool "
        "<i>Double Materiality Assessment Tool</i> (GPL v3) generiert.",
        styles["body_small"]
    ))
    story.append(PageBreak())
    return story


# ── Executive Summary ─────────────────────────────────────────────────────────
def _executive_summary(scored_iros: list[dict], styles: dict) -> list:
    story = []
    story.append(Paragraph("Zusammenfassung", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID_BLUE))
    story.append(Spacer(1, 0.3 * cm))

    n_total = len(scored_iros)
    n_impact = sum(1 for i in scored_iros if i["is_impact_material"])
    n_financial = sum(1 for i in scored_iros if i["is_financial_material"])
    n_doubly = sum(1 for i in scored_iros if i["is_doubly_material"])

    summary_data = [
        ["Kennzahl", "Anzahl IROs", "Anteil"],
        ["Gesamt bewertet", str(n_total), "100 %"],
        ["Auswirkungswesentlich (Score ≥ 3,0)", str(n_impact),
         f"{n_impact / n_total * 100:.0f} %"],
        ["Finanziell wesentlich (Score ≥ 3,0)", str(n_financial),
         f"{n_financial / n_total * 100:.0f} %"],
        ["Doppelt wesentlich (beide Kriterien)", str(n_doubly),
         f"{n_doubly / n_total * 100:.0f} %"],
    ]

    t = Table(summary_data, colWidths=[10 * cm, 2.5 * cm, 2.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_LIGHT_GREY]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph("Methodischer Hinweis", styles["h2"]))
    story.append(Paragraph(
        "Die vorliegende Analyse folgt der EFRAG-Methodik zur Doppelten Wesentlichkeit "
        "(Double Materiality Assessment, DMA) gemäß CSRD/ESRS-Anforderungen. "
        "Auswirkungswesentlichkeit (Inside-out) wird als gewichteter Durchschnitt aus "
        "Ausmaß (40 %), Reichweite (30 %) und Behebbarkeit (30 %) berechnet. "
        "Finanzielle Wesentlichkeit (Outside-in) ergibt sich aus dem Produkt von "
        "Eintrittswahrscheinlichkeit und finanzieller Auswirkung, normiert auf eine "
        "Skala von 1–5. Ein ESRS-Thema gilt als wesentlich, sobald mindestens eine "
        "zugeordnete IRO den Schwellenwert von 3,0 erreicht oder überschreitet.",
        styles["body"]
    ))
    story.append(PageBreak())
    return story


# ── IRO table ─────────────────────────────────────────────────────────────────
def _iro_table(scored_iros: list[dict], styles: dict) -> list:
    story = []
    story.append(Paragraph("Vollständige IRO-Bewertung", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID_BLUE))
    story.append(Spacer(1, 0.3 * cm))

    # Legend
    legend_data = [[
        Paragraph("■ Doppelt wesentlich", styles["body_small"]),
        Paragraph("■ Einfach wesentlich", styles["body_small"]),
        Paragraph("□ Nicht wesentlich", styles["body_small"]),
    ]]
    legend_t = Table(legend_data, colWidths=[5*cm, 5*cm, 5*cm])
    legend_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), C_RED_ROW),
        ("BACKGROUND", (1, 0), (1, 0), C_ORANGE_ROW),
        ("BACKGROUND", (2, 0), (2, 0), C_LIGHT_GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, C_BORDER),
    ]))
    story.append(legend_t)
    story.append(Spacer(1, 0.3 * cm))

    headers = [
        "IRO-ID", "Thema", "Typ", "Beschreibung",
        "Auswirk.-\nScore", "Fin.-\nScore", "A-Mat.", "F-Mat.", "D-Mat."
    ]
    col_widths = [1.4*cm, 1.0*cm, 1.5*cm, 6.0*cm, 1.5*cm, 1.3*cm, 1.0*cm, 1.0*cm, 1.0*cm]

    table_data = [headers]
    row_styles = []

    for row_idx, iro in enumerate(scored_iros, start=1):
        row = [
            Paragraph(iro["iro_id"], styles["cell"]),
            Paragraph(iro["esrs_topic"], styles["cell"]),
            Paragraph(iro["iro_type"], styles["cell"]),
            Paragraph(iro["description"][:120], styles["cell"]),
            Paragraph(f"{iro['impact_score']:.2f}", styles["cell"]),
            Paragraph(f"{iro['financial_score']:.2f}", styles["cell"]),
            Paragraph("✓" if iro["is_impact_material"] else "–", styles["cell"]),
            Paragraph("✓" if iro["is_financial_material"] else "–", styles["cell"]),
            Paragraph("✓" if iro["is_doubly_material"] else "–", styles["cell"]),
        ]
        table_data.append(row)

        if iro["is_doubly_material"]:
            row_styles.append(("BACKGROUND", (0, row_idx), (-1, row_idx), C_RED_ROW))
        elif iro["is_impact_material"] or iro["is_financial_material"]:
            row_styles.append(("BACKGROUND", (0, row_idx), (-1, row_idx), C_ORANGE_ROW))

    base_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), C_DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7.5),
        ("ALIGN", (4, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, C_BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_LIGHT_GREY]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ] + row_styles)

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(base_style)
    story.append(t)
    story.append(PageBreak())
    return story


# ── Image pages ───────────────────────────────────────────────────────────────
def _image_page(image_path: str, caption: str, styles: dict) -> list:
    story = []
    if os.path.exists(image_path):
        img = Image(image_path, width=16 * cm, height=12 * cm, kind="proportional")
        story.append(img)
        story.append(Paragraph(caption, styles["caption"]))
    else:
        story.append(Paragraph(
            f"[Bild nicht gefunden: {image_path}]", styles["body_small"]
        ))
    story.append(PageBreak())
    return story


# ── Methodology appendix ──────────────────────────────────────────────────────
def _methodology(styles: dict) -> list:
    story = []
    story.append(Paragraph("Anhang: Methodik (EFRAG DMA)", styles["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=C_MID_BLUE))
    story.append(Spacer(1, 0.3 * cm))

    sections = [
        ("Auswirkungswesentlichkeit (Inside-out)",
         "Die Auswirkungswesentlichkeit bewertet, welchen Einfluss das Unternehmen auf "
         "Mensch und Umwelt hat. Der Score ergibt sich als gewichteter Durchschnitt aus "
         "drei Subdimensionen:\n\n"
         "• Ausmaß (Magnitude): Schwere der Auswirkung — Gewichtung 40 %\n"
         "• Reichweite (Scope): Anzahl betroffener Personen / Fläche — Gewichtung 30 %\n"
         "• Behebbarkeit (Irremediability): Reversibilität — Gewichtung 30 %\n\n"
         "Formel: Auswirkungsscore = (Ausmaß × 0,4) + (Reichweite × 0,3) + (Behebbarkeit × 0,3)\n"
         "Schwellenwert: ≥ 3,0"),
        ("Finanzielle Wesentlichkeit (Outside-in)",
         "Die finanzielle Wesentlichkeit bewertet, welche Nachhaltigkeitsthemen "
         "finanzielle Risiken oder Chancen für das Unternehmen darstellen. Der Score "
         "ergibt sich aus:\n\n"
         "• Eintrittswahrscheinlichkeit (Likelihood): 1–5\n"
         "• Finanzielle Auswirkung (Financial Magnitude): 1–5\n\n"
         "Formel: Finanzscore = (Eintrittswahrscheinlichkeit × Finanzielle Auswirkung) ÷ 5\n"
         "Schwellenwert: ≥ 3,0"),
        ("Doppelte Wesentlichkeit",
         "Ein IRO gilt als doppelt wesentlich, wenn sowohl der Auswirkungsscore als auch "
         "der finanzielle Score den Schwellenwert von 3,0 erreichen oder überschreiten. "
         "In diesem Fall muss das Unternehmen gemäß CSRD sowohl über Auswirkungen als "
         "auch über finanzielle Risiken und Chancen berichten."),
        ("Rechtlicher Rahmen",
         "Die Analyse basiert auf:\n"
         "• Corporate Sustainability Reporting Directive (CSRD, EU 2022/2464)\n"
         "• European Sustainability Reporting Standards (ESRS, Delegierte Verordnung EU 2023/2772)\n"
         "• EFRAG IG 1: Materiality Assessment Implementation Guidance (Nov. 2023)"),
    ]

    for heading, text in sections:
        story.append(Paragraph(heading, styles["h2"]))
        for line in text.split("\n"):
            story.append(Paragraph(line if line.strip() else "&nbsp;", styles["body"]))
        story.append(Spacer(1, 0.3 * cm))

    return story


# ── Entry point ───────────────────────────────────────────────────────────────
def generate_report(
    scored_iros: list[dict],
    topic_aggregates: dict,
    company: str,
    year: int,
    matrix_path: str,
    heatmap_path: str,
    output_path: str,
) -> None:
    """
    Generate the full PDF DMA report.

    Args:
        scored_iros: Output of scoring_engine.score_iros().
        topic_aggregates: Output of scoring_engine.aggregate_by_topic().
        company: Company name (appears on cover and headers).
        year: Reporting year.
        matrix_path: Path to materiality_matrix.png.
        heatmap_path: Path to esrs_heatmap.png.
        output_path: Destination path for the PDF.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    font = _try_font()
    styles = _build_styles(font)
    doc = _make_doc(output_path)

    story = []
    story += _cover(company, year, styles)
    story += _executive_summary(scored_iros, styles)
    story += _iro_table(scored_iros, styles)
    story += _image_page(
        matrix_path,
        "Abbildung 1: Doppelte Wesentlichkeitsmatrix (Auswirkungs- vs. Finanzieller Score)",
        styles,
    )
    story += _image_page(
        heatmap_path,
        "Abbildung 2: ESRS-Themenübersicht — maximale Scores je Thema",
        styles,
    )
    story += _methodology(styles)

    try:
        doc.build(story)
    except OSError as e:
        raise OSError(f"Could not save PDF to '{output_path}': {e}") from e

    print(f"[OK] PDF-Bericht gespeichert: {output_path}")
