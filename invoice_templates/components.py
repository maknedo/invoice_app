from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .base import BaseInvoiceTemplate

# ---------------------------------------------------------------------------
# Generic drawing helpers
# ---------------------------------------------------------------------------

def draw_logo(center_x: float, y: float, size: float, logo_path: str, document: canvas.Canvas) -> None:
    if logo_path:
        try:
            document.drawImage(
                logo_path,
                center_x - size / 2,
                y - size,
                width=size,
                height=size,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            # Ignore logo errors silently to avoid interrupting invoice generation
            pass


def draw_horizontal_separator(document: canvas.Canvas, x_start: float, x_end: float, y: float, color: colors.Color, width: float = 0.5) -> None:
    document.setStrokeColor(color)
    document.setLineWidth(width)
    document.line(x_start, y, x_end, y)


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------

def draw_header_row(
    document: canvas.Canvas,
    template: BaseInvoiceTemplate,
    headers: Iterable[str],
    widths: Iterable[float],
    x_origin: float,
    y: float,
    height: float,
    header_fill: colors.Color | None = None,
    header_stroke: colors.Color | None = None,
    header_text_color: colors.Color | None = None,
    header_font_size: float | None = None,
) -> None:
    fill_color = header_fill if header_fill is not None else template.theme.table_header
    stroke_color = header_stroke if header_stroke is not None else template.theme.gold
    text_color = header_text_color if header_text_color is not None else template.theme.white
    font_size = header_font_size if header_font_size is not None else 9

    total_width = sum(widths)
    document.setFillColor(fill_color)
    document.rect(x_origin, y - height, total_width, height, fill=1, stroke=0)

    document.setStrokeColor(stroke_color)
    document.setLineWidth(2)
    document.rect(x_origin, y - height, total_width, height, fill=0, stroke=1)

    document.setFillColor(text_color)
    document.setFont(template.arabic_font, font_size)

    x_position = x_origin + total_width
    for header, width in zip(headers, widths):
        text_x = x_position - width / 2
        document.drawCentredString(text_x, y - height + 10, template.reshape_arabic(header))
        x_position -= width


def draw_table_rows(
    document: canvas.Canvas,
    template: BaseInvoiceTemplate,
    rows: Iterable[Iterable[str]],
    widths: Iterable[float],
    x_origin: float,
    y: float,
    row_height: float,
    min_y: float,
    max_rows: int | None = None,
    even_row_fill: colors.Color | None = None,
    odd_row_fill: colors.Color | None = None,
    grid_color: colors.Color | None = None,
    row_text_color: colors.Color | None = None,
    row_font_size: float | None = None,
) -> float:
    x_total = sum(widths)
    font_size = row_font_size if row_font_size is not None else 8.5

    default_even_fill = even_row_fill if even_row_fill is not None else template.theme.table_row2
    default_odd_fill = odd_row_fill if odd_row_fill is not None else template.theme.table_row1
    stroke_color = grid_color if grid_color is not None else template.theme.border
    text_color = row_text_color if row_text_color is not None else template.theme.text

    for index, row in enumerate(rows, start=1):
        if max_rows is not None and index > max_rows:
            break

        if y - row_height < min_y:
            document.showPage()
            document.setFont(template.arabic_font, font_size)
            y = template.height - 50

        fill_color = default_even_fill if index % 2 == 0 else default_odd_fill

        document.setFillColor(fill_color)
        document.rect(x_origin, y - row_height, x_total, row_height, fill=1, stroke=0)

        document.setStrokeColor(stroke_color)
        document.setLineWidth(0.3)
        document.rect(x_origin, y - row_height, x_total, row_height, fill=0, stroke=1)

        document.setFillColor(text_color)
        document.setFont(template.arabic_font, font_size)

        x_position = x_origin + x_total
        for value, width in zip(row, widths):
            text_x = x_position - width / 2
            document.drawCentredString(text_x, y - row_height + 8, str(value))
            x_position -= width

        y -= row_height

    return y


# ---------------------------------------------------------------------------
# Totals helpers
# ---------------------------------------------------------------------------

def draw_total_rows(
    document: canvas.Canvas,
    template: BaseInvoiceTemplate,
    totals: List[Dict[str, float]],
    totals_x: float,
    totals_width: float,
    y: float,
) -> float:
    document.setFont(template.arabic_font, 10)

    for total_row in totals:
        label = total_row["label"]
        value = total_row["value"]
        color = total_row.get("color", template.theme.text)

        document.setFillColor(template.theme.white)
        document.rect(totals_x - totals_width, y - 22, totals_width, 22, fill=1, stroke=0)
        draw_horizontal_separator(
            document,
            totals_x - totals_width + 20,
            totals_x - 10,
            y - 2,
            template.theme.border,
        )

        document.setFillColor(color)
        # رسم النص العربي على اليمين والقيمة على اليسار
        document.drawRightString(totals_x - 10, y - 13, template.reshape_arabic(label))
        document.drawString(totals_x - totals_width + 20, y - 13, f"{value:.2f}")
        y -= 22

    return y