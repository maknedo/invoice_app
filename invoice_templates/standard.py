"""Standard invoice template implementation."""

from __future__ import annotations

import os
from typing import Dict

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .base import BaseInvoiceTemplate
from .components import (
    draw_header_row,
    draw_logo,
    draw_table_rows,
    draw_total_rows,
)
from .themes import STANDARD_THEME


class StandardInvoiceTemplate(BaseInvoiceTemplate):
    def __init__(self, font_name: str = 'Arial', custom_font_path: str = None) -> None:
        super().__init__(font_name, custom_font_path)
        self.template_name = "فاتورة ضريبية مبسطة"
        self.theme = STANDARD_THEME

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    def draw_header(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        document.setFillColor(self.theme.header_bg)
        document.rect(0, y - 120, self.width, 120, fill=1, stroke=0)

        document.setFillColor(self.theme.primary)
        document.rect(0, y, self.width, 12, fill=1, stroke=0)

        document.setFillColor(self.theme.gold)
        document.rect(0, y - 15, self.width, 3, fill=1, stroke=0)

        y -= 25

        logo_path = invoice_data.get("logo_path")
        if logo_path:
            draw_logo(self.width / 2, y - 0, 70, logo_path, document)

        company_x_right = self.width - 50
        company_y = y - 10

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 18)
        document.drawRightString(company_x_right, company_y, self.reshape_arabic(invoice_data.get("company_name", "")))

        company_y -= 18
        document.setFont(self.arabic_font, 10)
        document.drawRightString(
            company_x_right,
            company_y,
            self.reshape_arabic(f"الرقم الضريبي: {invoice_data.get('tax_code', '')}"),
        )

        company_y -= 16
        document.setFont(self.arabic_font, 9)
        document.setFillColor(self.theme.light_text)
        company_address = invoice_data.get('company_address', 'المملكة العربية السعودية')
        document.drawRightString(company_x_right, company_y, self.reshape_arabic(company_address))

        company_x_left = 50
        company_y_left = y - 10

        document.setFillColor(self.theme.text)
        document.setFont("Helvetica", 12)
        document.drawString(company_x_left, company_y_left, invoice_data.get("english_company_name", ""))

        company_y_left -= 18
        document.setFont("Helvetica", 10)
        document.drawString(company_x_left, company_y_left, f"VAT No.: {invoice_data.get('tax_code', '')}")

        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(2)
        document.line(40, y - 100, self.width - 40, y - 100)

        return y - 120

    # ------------------------------------------------------------------
    # Invoice info & QR
    # ------------------------------------------------------------------
    def draw_invoice_info(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        title_spacing = 15

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 16)
        document.drawCentredString(self.width / 2, y - title_spacing, self.reshape_arabic(self.template_name))

        document.setFillColor(self.theme.light_text)
        document.setFont(self.arabic_font, 10)
        document.drawCentredString(self.width / 2, y - title_spacing - 15, "Simplified Tax Invoice")

        box_y = y - title_spacing - 30
        box_height = 110

        document.setStrokeColor(self.theme.border)
        document.setFillColor(self.theme.white)
        document.setLineWidth(1)
        document.rect(40, box_y - box_height, self.width - 80, box_height, fill=1, stroke=1)

        document.setStrokeColor(self.theme.border)
        document.setLineWidth(0.5)
        document.line(self.width * 0.65, box_y - 5, self.width * 0.65, box_y - box_height + 5)
        document.line(170, box_y - 5, 170, box_y - box_height + 5)

        right_x = self.width - 50
        info_y = box_y - 18

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 11)
        document.drawRightString(right_x, info_y, self.reshape_arabic("بيانات الفاتورة"))

        info_y -= 20
        document.setFillColor(self.theme.text)
        document.setFont(self.arabic_font, 9)

        invoice_info = [
            f"رقم الفاتورة: {invoice_data['invoice_number']}",
            f"التاريخ: {invoice_data.get('date', '')}",
            f"الوقت: {invoice_data.get('time', '')}",
            f"نوع الفاتورة: {invoice_data.get('invoice_type', '')}",
            f"المخزن: {invoice_data.get('warehouse', '')}",
        ]

        if invoice_data.get("cost_center"):
            invoice_info.append(f"مركز التكلفة: {invoice_data['cost_center']}")

        for info in invoice_info:
            document.drawRightString(right_x, info_y, self.reshape_arabic(info))
            info_y -= 14

        middle_right = self.width * 0.63
        middle_y = box_y - 18

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 11)
        document.drawRightString(middle_right, middle_y, self.reshape_arabic("بيانات العميل"))

        middle_y -= 20
        document.setFillColor(self.theme.text)
        document.setFont(self.arabic_font, 9)

        customer_info = [f"الاسم: {invoice_data.get('customer_name', '')}"]
        if invoice_data.get("customer_phone"):
            customer_info.append(f"الهاتف: {invoice_data['customer_phone']}")
        if invoice_data.get("customer_tax_number"):
            customer_info.append(f"الرقم الضريبي: {invoice_data['customer_tax_number']}")
        if invoice_data.get("customer_address"):
            customer_info.append(f"العنوان: {invoice_data['customer_address']}")

        for info in customer_info:
            document.drawRightString(middle_right, middle_y, self.reshape_arabic(info))
            middle_y -= 14

        qr_file = self.generate_qr_code(invoice_data)
        try:
            document.drawImage(qr_file, 50, box_y - 93, width=90, height=90)

            document.setFont(self.arabic_font, 8)
            document.setFillColor(self.theme.light_text)
            document.drawCentredString(95, box_y - 101, self.reshape_arabic("رمز التحقق"))
        finally:
            try:
                os.remove(qr_file)  # pragma: no cover - OS specific
            except Exception:
                pass

        return box_y - box_height - 15

    # ------------------------------------------------------------------
    # Items table
    # ------------------------------------------------------------------
    def draw_items_table(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        headers = [
            "م",
            "الكود",
            "اسم الصنف",
            "الوحدة",
            "الكمية",
            "السعر",
            "الخصم",
            "الضريبة",
            "الإجمالي",
        ]
        column_widths = [25, 50, 140, 40, 40, 50, 45, 50, 60]
        table_width = sum(column_widths)
        table_x = self.width - 40 - table_width

        draw_header_row(document, self, headers, column_widths, table_x, y, 26)
        y -= 26

        rows = []
        def _to_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        for index, item in enumerate(invoice_data.get("items", []), start=1):
            quantity = _to_float(item.get("quantity", 0))
            price = _to_float(item.get("price", 0))
            discount_amount = _to_float(item.get("discount_amount", 0))
            discount_per_unit = _to_float(item.get("discount_per_unit", 0))

            if not discount_amount and discount_per_unit and quantity:
                discount_amount = discount_per_unit * quantity

            tax_amount = _to_float(item.get("tax_amount", 0))
            total_amount = _to_float(item.get("total", 0))

            quantity_display = f"{quantity:.0f}" if quantity.is_integer() else f"{quantity:.2f}"

            rows.append(
                (
                    str(index),
                    item.get("item_code", ""),
                    self.reshape_arabic(item.get("description", "")),
                    self.reshape_arabic(item.get("unit", "")),
                    quantity_display,
                    f"{price:.2f}",
                    f"{discount_amount:.2f}",
                    f"{tax_amount:.2f}",
                    f"{total_amount:.2f}",
                )
            )

        y = draw_table_rows(document, self, rows, column_widths, table_x, y, 24, 200)
        return y - 15

    # ------------------------------------------------------------------
    # Totals & footer
    # ------------------------------------------------------------------
    def draw_totals(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        totals_x = self.width - 60
        totals_width = 230

        totals = [
            {"label": "الإجمالي غير شامل الضريبة", "value": invoice_data.get("subtotal_before_discount", 0)},
            {"label": "مجموع الخصم", "value": invoice_data.get("total_discount", 0)},
            {"label": "الإجمالي الخاضع للضريبة", "value": invoice_data.get("subtotal", 0)},
            {"label": "مجموع ضريبة القيمة المضافة 15%", "value": invoice_data.get("tax", 0)},
        ]

        y = draw_total_rows(document, self, totals, totals_x, totals_width, y)

        total_box_height = 35
        document.setFillColor(self.theme.total_bg)
        document.roundRect(totals_x - totals_width, y - total_box_height, totals_width, total_box_height, 5, fill=1, stroke=0)

        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(2.5)
        document.roundRect(totals_x - totals_width, y - total_box_height, totals_width, total_box_height, 5, fill=0, stroke=1)

        document.setFillColor(self.theme.white)
        label_x = totals_x - 15  # محاذاة النص إلى يمين الإطار مع ترك مسافة بسيطة
        value_x = totals_x - totals_width + 20  # محاذاة القيمة إلى يسار الإطار مع ترك مسافة داخلية
        text_y = y - 22

        document.setFont(self.arabic_font, 13)
        document.drawRightString(label_x, text_y, self.reshape_arabic("الإجمالي:"))

        document.setFont(self.arabic_font, 15)
        document.drawString(
            value_x,
            text_y,
            f"{invoice_data.get('total', 0):.2f} {invoice_data.get('currency', 'SAR')}",
        )

        y -= total_box_height + 12
        document.setFillColor(self.theme.text)
        document.setFont(self.arabic_font, 9)
        document.drawRightString(
            totals_x - 10,
            y - 5,
            self.reshape_arabic(f"فقط: {self.number_to_arabic_words(invoice_data.get('total', 0))}"),
        )

        return y - 25

    def draw_footer(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> None:
        if invoice_data.get("notes"):
            notes_height = 40
            document.setStrokeColor(self.theme.border)
            document.setFillColor(colors.HexColor("#FFFEF7"))
            document.setLineWidth(0.5)
            document.rect(40, y - notes_height, self.width - 80, notes_height, fill=1, stroke=1)

            document.setFillColor(self.theme.primary)
            document.setFont(self.arabic_font, 9)
            document.drawRightString(self.width - 50, y - 15, self.reshape_arabic("ملاحظات:"))

            # الحصول على محاذاة النص المختارة
            notes_alignment = invoice_data.get("notes_alignment", "right")
            
            document.setFillColor(self.theme.text)
            document.setFont(self.arabic_font, 8)
            notes_text = self.reshape_arabic(invoice_data["notes"][:120])
            text_x = self.width - 50  # المركز الافتراضي
            text_y = y - 30
            
            # تطبيق المحاذاة حسب الاختيار
            if notes_alignment == "center":
                # محاذاة لوسط
                document.drawCentredString(self.width / 2, text_y, notes_text)
            elif notes_alignment == "left":
                # محاذاة لليسار
                document.drawString(50, text_y, notes_text)
            else:  # "right" - المحاذاة الافتراضية
                # محاذاة لليمين
                document.drawRightString(self.width - 50, text_y, notes_text)

            y -= notes_height + 10

        signature_y = 90
        document.setStrokeColor(self.theme.border)
        document.setLineWidth(0.5)

        signature_width = 120
        # Warehouse
        document.line(self.width - 60 - signature_width, signature_y + 20, self.width - 60, signature_y + 20)
        document.setFillColor(self.theme.light_text)
        document.setFont(self.arabic_font, 8)
        document.drawCentredString(self.width - 60 - signature_width / 2, signature_y + 5, self.reshape_arabic("المخازن"))

        # Receiver
        document.line(self.width / 2 - 60, signature_y + 20, self.width / 2 + 60, signature_y + 20)
        document.drawCentredString(self.width / 2, signature_y + 5, self.reshape_arabic("المستلم"))

        # Accountant
        document.line(60, signature_y + 20, 60 + signature_width, signature_y + 20)
        document.drawCentredString(60 + signature_width / 2, signature_y + 5, self.reshape_arabic("المحاسب"))

        footer_height = 45
        document.setFillColor(self.theme.primary)
        document.rect(0, 0, self.width, footer_height, fill=1, stroke=0)

        document.setFillColor(self.theme.gold)
        document.rect(0, footer_height - 3, self.width, 3, fill=1, stroke=0)

        document.setFillColor(self.theme.white)
        document.setFont(self.arabic_font, 10)
        document.drawCentredString(self.width / 2, 25, self.reshape_arabic("نسعد بخدمتكم دائماً • نحن في خدمتكم"))
        
        company_address = invoice_data.get("company_address")
        if company_address:
            document.setFont(self.arabic_font, 8)
            address_text = f"العنوان: {company_address}"
            document.drawCentredString(self.width / 2, 12, self.reshape_arabic(address_text))