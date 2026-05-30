"""Simple invoice template implementation redesigned for clarity and compliance."""

from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, Tuple

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .base import BaseInvoiceTemplate
from .components import draw_logo
from .themes import SIMPLE_THEME


class SimpleInvoiceTemplate(BaseInvoiceTemplate):
    """Modernised simple invoice with structured layout inspired by reference design."""

    def __init__(self, font_name: str = 'Arial', custom_font_path: str = None) -> None:
        super().__init__(font_name, custom_font_path)
        self.template_name = "فاتورة ضريبية"
        self.theme = SIMPLE_THEME

        # Layout constants (millimetres converted to points) - reduced spacing
        self.margin_x = self._mm_to_pt(18)
        self.margin_top = self._mm_to_pt(15)
        self.margin_bottom = self._mm_to_pt(15)
        self.content_width = self.width - (2 * self.margin_x)

        # Colour palette based on provided description
        self.title_bg = colors.HexColor("#E9F3F8")
        self.border_color = colors.HexColor("#DADADA")
        self.text_muted = colors.HexColor("#777777")
        self.table_header_bg = colors.HexColor("#E9F3F8")
        self.table_row_even = colors.HexColor("#F8FBFD")
        self.table_row_odd = colors.whitesmoke

        # Reusable bilingual label layout for compact detail rows
        self.detail_label_gap = self._mm_to_pt(1.0)
        self.detail_value_gap = self._mm_to_pt(1.0)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _mm_to_pt(value: float) -> float:
        """Convert millimetres to points."""
        return value * 72 / 25.4

    @staticmethod
    def _format_amount(value: float | Decimal | str, currency: str | None = None) -> str:
        """Format numeric values with thousands separators and two decimals."""
        try:
            number = Decimal(str(value))
        except (InvalidOperation, TypeError):
            number = Decimal("0")
        formatted = f"{number:,.2f}"
        if currency:
            return f"{formatted} {currency}"
        return formatted

    def _draw_bilingual_label(
        self,
        document: canvas.Canvas,
        right_x: float,
        y: float,
        arabic_text: str,
        english_text: str,
        arabic_font_size: float = 9,
        english_font_size: float = 7.5,
        color: colors.Color | None = None,
    ) -> None:
        """Render two-line label (Arabic above English) aligned to the right."""
        if color:
            document.setFillColor(color)
        document.setFont(self.arabic_font, arabic_font_size)
        document.drawRightString(right_x, y, self.reshape_arabic(arabic_text))

        document.setFont("Helvetica", english_font_size)
        document.drawRightString(right_x, y - 10, english_text)

    # ------------------------------------------------------------------
    # Header & title
    # ------------------------------------------------------------------
    def draw_header(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        top_y = self.height - self.margin_top
        content_left = self.margin_x
        content_right = self.width - self.margin_x

        # Company information (right aligned for RTL)
        company_y = top_y - 5
        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 14)
        document.drawRightString(content_right, company_y, self.reshape_arabic(invoice_data.get("company_name", "")))

        company_y -= 12
        document.setFillColor(self.text_muted)
        document.setFont("Helvetica", 8.5)
        document.drawRightString(content_right, company_y, invoice_data.get("english_company_name", ""))

        company_y -= 10
        document.setFillColor(self.text_muted)
        document.setFont(self.arabic_font, 8)
        address = invoice_data.get("company_address", "")
        if address:
            document.drawRightString(content_right, company_y, self.reshape_arabic(address))

        company_y -= 10
        tax_code = invoice_data.get("tax_code")
        if tax_code:
            document.drawRightString(
                content_right,
                company_y,
                self.reshape_arabic(f"الرقم الضريبي: {tax_code}"),
            )

        # Logo on the left side opposite to company info
        logo_path = invoice_data.get("logo_path")
        logo_size = self._mm_to_pt(28)
        if logo_path:
            draw_logo(content_left + logo_size / 2, top_y + self._mm_to_pt(7), logo_size, logo_path, document)

        # Divider line under header
        divider_y = top_y - self._mm_to_pt(26)
        document.setStrokeColor(self.border_color)
        document.setLineWidth(0.5)
        document.line(content_left, divider_y, content_right, divider_y)

        # Title band (Tax Invoice)
        band_height = self._mm_to_pt(12)
        band_top = divider_y - self._mm_to_pt(3)
        document.setFillColor(self.title_bg)
        document.roundRect(content_left, band_top - band_height, self.content_width, band_height, 6, fill=1, stroke=0)

        band_middle = band_top - (band_height / 2)
        document.setFillColor(self.theme.primary)
        document.setFont("Helvetica-Bold", 11)
        document.drawCentredString(self.width / 2, band_middle + 5, "Tax Invoice")

        document.setFont(self.arabic_font, 11)
        document.drawCentredString(self.width / 2, band_middle - 5, self.reshape_arabic("فاتورة ضريبية"))

        return band_top - band_height - self._mm_to_pt(4)

    # ------------------------------------------------------------------
    # Invoice details & customer blocks
    # ------------------------------------------------------------------
    def draw_invoice_info(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        content_left = self.margin_x
        content_right = self.width - self.margin_x
        currency = invoice_data.get("currency", "SR")

        # --------------------------- Invoice details block ------------------
        block_padding = self._mm_to_pt(2)
        qr_size = self._mm_to_pt(26)
        qr_gap = self._mm_to_pt(4)
        block_height = self._mm_to_pt(34)

        document.setLineWidth(1)
        document.setStrokeColor(self.border_color)
        document.setFillColor(colors.white)
        document.roundRect(
            content_left,
            y - block_height,
            self.content_width,
            block_height,
            8,
            fill=1,
            stroke=1,
        )

        text_right = content_right - block_padding - qr_size - qr_gap
        value_x = content_left + block_padding
        row_y = y - block_padding - 10

        # Narrower columns for tighter spacing
        english_label_x = value_x
        arabic_label_x = text_right
        
        # Calculate center position with tighter spacing
        available_width = text_right - value_x
        # Use 70% of available width, centered
        used_width = available_width * 0.70
        left_margin = (available_width - used_width) / 2
        value_center_x = value_x + left_margin + (used_width / 2)

        invoice_rows: Iterable[Tuple[str, str, str]] = (
            ("رقم الفاتورة", "Invoice No.", str(invoice_data.get("invoice_number", ""))),
            ("التاريخ", "Date", str(invoice_data.get("date", ""))),
            ("الوقت", "Time", str(invoice_data.get("time", ""))),
            ("نوع الفاتورة", "Invoice Type", str(invoice_data.get("invoice_type", ""))),
            ("المستودع", "Warehouse", str(invoice_data.get("warehouse", "-"))),
            ("مركز التكلفة", "Cost Center", str(invoice_data.get("cost_center", "-"))),
        )

        for arabic_label, english_label, value in invoice_rows:
            baseline = row_y - 2.5
            document.setFillColor(self.theme.primary)
            document.setFont(self.arabic_font, 7.5)
            document.drawRightString(arabic_label_x, baseline, self.reshape_arabic(arabic_label))

            document.setFillColor(self.theme.text)
            document.setFont(self.arabic_font, 7.5)
            document.drawCentredString(value_center_x, baseline, self.reshape_arabic(value))

            document.setFillColor(self.text_muted)
            document.setFont("Helvetica", 6.5)
            document.drawString(english_label_x, baseline, english_label)

            row_y -= 12.5

        # QR code in the upper-right corner
        qr_file = None
        try:
            qr_file = self.generate_qr_code(invoice_data)
            document.drawImage(
                qr_file,
                content_right - block_padding - qr_size,
                y - block_padding - qr_size,
                width=qr_size,
                height=qr_size,
            )
        finally:
            if qr_file and os.path.exists(qr_file):
                try:
                    os.remove(qr_file)
                except OSError:
                    pass

        y -= block_height + self._mm_to_pt(3)

        # --------------------------- Customer block ------------------------
        buyer_height = self._mm_to_pt(26)
        document.setStrokeColor(self.border_color)
        document.setFillColor(colors.white)
        document.roundRect(
            content_left,
            y - buyer_height,
            self.content_width,
            buyer_height,
            8,
            fill=1,
            stroke=1,
        )

        header_height = self._mm_to_pt(7)
        document.setFillColor(self.title_bg)
        document.roundRect(
            content_left,
            y - header_height,
            self.content_width,
            header_height,
            8,
            fill=1,
            stroke=0,
        )

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 8)
        document.drawRightString(content_right - self._mm_to_pt(2), y - 12, self.reshape_arabic("بيانات العميل"))
        document.setFont("Helvetica", 6.5)
        document.drawString(content_left + self._mm_to_pt(2), y - 12, "Buyer Information")

        info_y = y - header_height - 10
        customer_rows: Iterable[Tuple[str, str, str]] = (
            ("الاسم", "Name", str(invoice_data.get("customer_name", ""))),
            ("الرقم الضريبي", "Tax No.", str(invoice_data.get("customer_tax_number", "-"))),
            ("رقم الهاتف", "Phone", str(invoice_data.get("customer_phone", "-"))),
            ("العنوان", "Address", str(invoice_data.get("customer_address", "-"))),
        )

        # Calculate positions for three columns layout
        label_width = self._mm_to_pt(25)
        arabic_label_x = content_right - self._mm_to_pt(2)
        english_label_x = content_left + self._mm_to_pt(2)
        
        # Center area for values - narrower to bring columns closer
        value_center_x = content_left + self.content_width / 2
        
        for arabic_label, english_label, value in customer_rows:
            # Arabic label on the right
            document.setFillColor(self.theme.primary)
            document.setFont(self.arabic_font, 7.5)
            document.drawRightString(arabic_label_x, info_y, self.reshape_arabic(arabic_label + ":"))

            # Value in the center
            document.setFillColor(self.theme.text)
            document.setFont(self.arabic_font, 7.5)
            document.drawCentredString(value_center_x, info_y, self.reshape_arabic(value))

            # English label on the left
            document.setFillColor(self.text_muted)
            document.setFont("Helvetica", 6.5)
            document.drawString(english_label_x, info_y, english_label)
            
            info_y -= 10

        return y - buyer_height - self._mm_to_pt(4)

    # ------------------------------------------------------------------
    # Items table
    # ------------------------------------------------------------------
    def draw_items_table(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        content_left = self.margin_x
        content_right = self.width - self.margin_x
        # Columns from RIGHT to LEFT (RTL): Total, VAT, Discount, Price, Qty, Unit, Description, Item Code, #
        headers = (
            ("الإجمالي", "Total"),
            ("قيمة الضريبة", "VAT Amount"),
            ("الخصم", "Discount"),
            ("سعر الوحدة", "Unit Price"),
            ("الكمية", "Qty"),
            ("الوحدة", "Unit"),
            ("الوصف", "Description"),
            ("رقم الصنف", "Item Code"),
            ("#", "#"),
        )

        # RTL: Start from right to left - 9 columns with optimized widths
        # Because we insert(0,...), ratios are REVERSED: #, Item Code, Description, Unit, Qty, Price, Discount, VAT, Total
        column_ratios = (0.03, 0.11, 0.30, 0.06, 0.08, 0.12, 0.08, 0.10, 0.11)
        column_widths = [self.content_width * ratio for ratio in column_ratios]
        
        # Build columns from RIGHT to LEFT
        column_edges = [content_right]
        for width in column_widths:
            column_edges.insert(0, column_edges[0] - width)

        header_height = self._mm_to_pt(8.5)
        document.setFillColor(self.table_header_bg)
        document.roundRect(content_left, y - header_height, self.content_width, header_height, 6, fill=1, stroke=0)

        document.setStrokeColor(self.border_color)
        document.setLineWidth(0.8)
        document.roundRect(content_left, y - header_height, self.content_width, header_height, 6, fill=0, stroke=1)

        for edge in column_edges[1:-1]:
            document.line(edge, y - header_height, edge, y)

        header_text_y = y - 7.5
        for (arabic_text, english_text), col_left, col_right in zip(headers, column_edges[:-1], column_edges[1:]):
            centre_x = col_left + (col_right - col_left) / 2
            document.setFillColor(self.theme.primary)
            document.setFont(self.arabic_font, 7.5)
            document.drawCentredString(centre_x, header_text_y, self.reshape_arabic(arabic_text))

            document.setFont("Helvetica", 5.5)
            document.drawCentredString(centre_x, header_text_y - 8.5, english_text)

        y -= header_height

        rows = invoice_data.get("items", [])
        row_height = self._mm_to_pt(8)
        min_y = self.margin_bottom + self._mm_to_pt(40)
        currency = invoice_data.get("currency", "SR")

        def redraw_header(start_y: float) -> float:
            document.setFillColor(self.table_header_bg)
            document.roundRect(content_left, start_y - header_height, self.content_width, header_height, 6, fill=1, stroke=0)
            document.setStrokeColor(self.border_color)
            document.setLineWidth(0.8)
            document.roundRect(content_left, start_y - header_height, self.content_width, header_height, 6, fill=0, stroke=1)
            for edge in column_edges[1:-1]:
                document.line(edge, start_y - header_height, edge, start_y)
            header_text_y = start_y - 6
            for (arabic_text, english_text), col_left, col_right in zip(headers, column_edges[:-1], column_edges[1:]):
                centre_x = col_left + (col_right - col_left) / 2
                document.setFillColor(self.theme.primary)
                document.setFont(self.arabic_font, 7.5)
                document.drawCentredString(centre_x, header_text_y, self.reshape_arabic(arabic_text))
                document.setFont("Helvetica", 5.5)
                document.drawCentredString(centre_x, header_text_y - 7.5, english_text)
            return start_y - header_height

        totals_gap_height = self._mm_to_pt(60)

        def ensure_space(required_space: float) -> float:
            nonlocal y, column_edges
            if y - required_space < min_y:
                document.showPage()
                self.__init__()  # Reset fonts on new page
                column_edges = [self.margin_x]
                for width in column_widths:
                    column_edges.append(column_edges[-1] + width)
                y = redraw_header(self.height - self.margin_top)
            return y

        for index, item in enumerate(rows, start=1):
            y = ensure_space(row_height + totals_gap_height)

            fill_color = self.table_row_even if index % 2 == 0 else self.table_row_odd
            document.setFillColor(fill_color)
            document.rect(content_left, y - row_height, self.content_width, row_height, fill=1, stroke=0)

            document.setStrokeColor(self.border_color)
            document.setLineWidth(0.4)
            document.rect(content_left, y - row_height, self.content_width, row_height, fill=0, stroke=1)
            for edge in column_edges[1:-1]:
                document.line(edge, y - row_height, edge, y)

            cell_padding = self._mm_to_pt(1.5)
            center_y = y - row_height / 2

            # Column 0: Total (الإجمالي)
            total = Decimal(str(item.get("total", 0)))
            taxable = Decimal(str(item.get("taxable", item.get("taxable_amount", item.get("subtotal", 0)))))
            tax_amount = Decimal(str(item.get("tax_amount", 0) or 0))
            if not total:
                total = taxable + tax_amount
            total_text = self._format_amount(total, currency="")
            col_left, col_right = column_edges[0], column_edges[1]
            centre_x = col_left + (col_right - col_left) / 2
            document.setFillColor(self.theme.text)
            document.setFont("Helvetica", 7)
            document.drawCentredString(centre_x, center_y, total_text)

            # Column 1: VAT Amount (قيمة الضريبة)
            vat_text = self._format_amount(tax_amount, currency="")
            col_left, col_right = column_edges[1], column_edges[2]
            centre_x = col_left + (col_right - col_left) / 2
            document.drawCentredString(centre_x, center_y, vat_text)

            # Column 2: Discount (الخصم)
            discount_amount = Decimal(str(item.get("discount_amount", 0) or 0))
            discount_per_unit = Decimal(str(item.get("discount_per_unit", 0) or 0))
            quantity = Decimal(str(item.get("quantity", 0) or 0))

            if not discount_amount and discount_per_unit and quantity:
                discount_amount = discount_per_unit * quantity

            discount_text = self._format_amount(discount_amount)
            col_left, col_right = column_edges[2], column_edges[3]
            centre_x = col_left + (col_right - col_left) / 2
            document.drawCentredString(centre_x, center_y, discount_text)

            # Column 3: Unit Price (سعر الوحدة)
            price_text = self._format_amount(item.get("price", 0), currency="")
            col_left, col_right = column_edges[3], column_edges[4]
            centre_x = col_left + (col_right - col_left) / 2
            document.drawCentredString(centre_x, center_y, price_text)

            # Column 4: Quantity (الكمية)
            qty_text = self._format_amount(item.get("quantity", 0))
            col_left, col_right = column_edges[4], column_edges[5]
            centre_x = col_left + (col_right - col_left) / 2
            document.drawCentredString(centre_x, center_y, qty_text)

            # Column 5: Unit (الوحدة)
            unit_text = self.reshape_arabic(item.get("unit", ""))
            col_left, col_right = column_edges[5], column_edges[6]
            centre_x = col_left + (col_right - col_left) / 2
            document.setFont(self.arabic_font, 7)
            document.drawCentredString(centre_x, center_y, unit_text)

            # Column 6: Description (الوصف)
            arabic_description = self.reshape_arabic(item.get("description", ""))
            col_left, col_right = column_edges[6], column_edges[7]
            centre_x = col_left + (col_right - col_left) / 2
            document.setFont(self.arabic_font, 7.5)
            document.drawCentredString(centre_x, center_y, arabic_description)

            # Column 7: Item Code (رقم الصنف)
            item_code = item.get("item_code", "")
            col_left, col_right = column_edges[7], column_edges[8]
            centre_x = col_left + (col_right - col_left) / 2
            document.setFont("Helvetica", 6.5)
            document.drawCentredString(centre_x, center_y, str(item_code) if item_code else "-")

            # Column 8: Auto number (#)
            col_left, col_right = column_edges[8], column_edges[9]
            centre_x = col_left + (col_right - col_left) / 2
            document.setFont("Helvetica", 7)
            document.drawCentredString(centre_x, center_y, str(index))

            y -= row_height

        document.setStrokeColor(self.border_color)
        document.setLineWidth(0.6)
        document.line(content_left, y, content_right, y)

        return y - self._mm_to_pt(3.5)

    # ------------------------------------------------------------------
    # Totals area
    # ------------------------------------------------------------------
    def draw_totals(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        currency = invoice_data.get("currency", "SR")
        totals_width = self.content_width * 0.38
        totals_x_right = self.width - self.margin_x
        panel_padding = self._mm_to_pt(3)
        row_height = self._mm_to_pt(8)

        tax_rate_value = invoice_data.get("tax_rate", 15)
        try:
            tax_rate_decimal = Decimal(str(tax_rate_value))
            if tax_rate_decimal == tax_rate_decimal.to_integral():
                tax_rate_display = str(int(tax_rate_decimal))
            else:
                tax_rate_display = tax_rate_decimal.normalize().to_eng_string()
        except (InvalidOperation, TypeError):
            tax_rate_display = str(tax_rate_value)

        totals_data = [
            ("الإجمالي (غير شامل الضريبة)", "Total (Excl. VAT)", invoice_data.get("subtotal_before_discount", 0)),
            ("الخصم", "Discount", invoice_data.get("total_discount", 0)),
            ("الإجمالي الخاضع للضريبة", "Taxable Amount", invoice_data.get("subtotal", 0)),
            (
                f"ضريبة القيمة المضافة ({tax_rate_display}%)",
                "VAT Amount",
                invoice_data.get("tax", 0),
            ),
        ]

        total_due = invoice_data.get("total", 0)
        # Calculate actual height needed
        total_band_height = self._mm_to_pt(9)
        panel_height = (len(totals_data) * row_height) + panel_padding * 2 + total_band_height + self._mm_to_pt(2)

        document.setStrokeColor(self.border_color)
        document.setFillColor(colors.white)
        document.roundRect(
            totals_x_right - totals_width,
            y - panel_height,
            totals_width,
            panel_height,
            8,
            fill=1,
            stroke=1,
        )

        current_y = y - panel_padding - 3
        for arabic_label, english_label, value in totals_data:
            # Arabic label
            document.setFillColor(self.theme.primary)
            document.setFont(self.arabic_font, 7.5)
            document.drawRightString(
                totals_x_right - panel_padding - 1,
                current_y,
                self.reshape_arabic(arabic_label)
            )
            
            # English label
            document.setFillColor(self.text_muted)
            document.setFont("Helvetica", 5.5)
            document.drawRightString(
                totals_x_right - panel_padding - 1,
                current_y - 9,
                english_label
            )
            
            # Value
            document.setFillColor(self.theme.text)
            document.setFont("Helvetica", 7)
            document.drawString(
                totals_x_right - totals_width + panel_padding + 1,
                current_y - 3,
                self._format_amount(value, currency),
            )
            current_y -= row_height

        # Highlight total due row
        current_y -= self._mm_to_pt(1.5)
        document.setFillColor(self.theme.primary)
        document.roundRect(
            totals_x_right - totals_width + panel_padding,
            current_y - total_band_height,
            totals_width - (2 * panel_padding),
            total_band_height,
            6,
            fill=1,
            stroke=0,
        )

        # Arabic label for total due
        document.setFillColor(colors.white)
        document.setFont(self.arabic_font, 8.5)
        document.drawRightString(
            totals_x_right - panel_padding - 1,
            current_y - total_band_height / 2 + 1,
            self.reshape_arabic("الإجمالي المستحق"),
        )

        # Total due value
        document.setFont("Helvetica-Bold", 9)
        document.drawString(
            totals_x_right - totals_width + panel_padding + 1,
            current_y - total_band_height / 2 + 1,
            self._format_amount(total_due, currency),
        )

        return current_y - total_band_height - self._mm_to_pt(5)

    # ------------------------------------------------------------------
    # Notes block
    # ------------------------------------------------------------------
    def draw_notes(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        notes = invoice_data.get("notes")
        if not notes:
            return y

        content_left = self.margin_x
        content_right = self.width - self.margin_x
        notes_height = self._mm_to_pt(20)
        document.setStrokeColor(self.border_color)
        document.setFillColor(colors.white)
        document.roundRect(
            content_left,
            y - notes_height,
            self.content_width,
            notes_height,
            8,
            fill=1,
            stroke=1,
        )

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 8.5)
        document.drawRightString(content_right - self._mm_to_pt(2.5), y - 8, self.reshape_arabic("ملاحظات"))

        # الحصول على محاذاة النص المختارة
        notes_alignment = invoice_data.get("notes_alignment", "right")
        
        document.setFillColor(self.theme.text)
        document.setFont(self.arabic_font, 7)
        
        notes_text = self.reshape_arabic(notes[:200])
        text_y = y - 14
        
        # تطبيق المحاذاة حسب الاختيار
        if notes_alignment == "center":
            # محاذاة لوسط
            text_center = (content_left + content_right) / 2
            document.drawCentredString(text_center, text_y, notes_text)
        elif notes_alignment == "left":
            # محاذاة لليسار
            document.drawString(content_left + self._mm_to_pt(2.5), text_y, notes_text)
        else:  # "right" - المحاذاة الافتراضية
            # محاذاة لليمين
            document.drawRightString(content_right - self._mm_to_pt(2.5), text_y, notes_text)

        return y - notes_height - self._mm_to_pt(6)

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    def draw_footer(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> None:
        footer_height = self._mm_to_pt(12)
        content_left = self.margin_x
        content_right = self.width - self.margin_x

        document.setFillColor(self.title_bg)
        document.rect(content_left, 0, self.content_width, footer_height, fill=1, stroke=0)

        document.setFillColor(self.theme.primary)
        document.setFont("Helvetica", 7)

        footer_info = []
        cr_number = invoice_data.get("commercial_register") or invoice_data.get("cr_number")
        tax_code = invoice_data.get("tax_code")
        email = invoice_data.get("company_email")
        phone = invoice_data.get("company_phone")

        if cr_number:
            footer_info.append(f"CR: {cr_number}")
        if tax_code:
            footer_info.append(f"VAT: {tax_code}")
        if email:
            footer_info.append(f"Email: {email}")
        if phone:
            footer_info.append(f"Phone: {phone}")

        if footer_info:
            spacing = self.content_width / max(len(footer_info), 1)
            for index, text in enumerate(footer_info):
                x_pos = content_left + spacing * index + spacing / 2
                document.drawCentredString(x_pos, footer_height / 2 + 1, text)

        document.setFillColor(self.text_muted)
        page_text = f"الصفحة {document.getPageNumber()} / {document.getPageNumber()}"
        document.setFont(self.arabic_font, 7)
        document.drawCentredString(self.width / 2, 3, self.reshape_arabic(page_text))
