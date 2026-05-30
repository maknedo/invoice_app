"""Professional invoice template implementation."""

from __future__ import annotations

import os
from typing import Dict

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .base import BaseInvoiceTemplate
from .components import draw_header_row, draw_logo, draw_table_rows, draw_total_rows
from .themes import PROFESSIONAL_THEME


class ProfessionalInvoiceTemplate(BaseInvoiceTemplate):
    def __init__(self, font_name: str = 'Arial', custom_font_path: str = None) -> None:
        super().__init__(font_name, custom_font_path)
        self.template_name = "فاتورة ضريبية "
        self.theme = PROFESSIONAL_THEME

    def draw_header(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        document.setFillColor(self.theme.header_bg)
        document.rect(0, y - 130, self.width, 130, fill=1, stroke=0)

        document.setFillColor(self.theme.primary)
        document.rect(0, y, self.width, 14, fill=1, stroke=0)

        document.setFillColor(self.theme.accent)
        document.rect(0, y - 18, self.width, 4, fill=1, stroke=0)

        y -= 30
        logo_path = invoice_data.get("logo_path")
        if logo_path:
            # الشعار في الوسط
            draw_logo(self.width / 2, y - 0, 70, logo_path, document)

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 20)
        document.drawRightString(self.width - 60, y - 10, self.reshape_arabic(invoice_data.get("company_name", "")))

        document.setFont(self.arabic_font, 10)
        document.drawRightString(
            self.width - 60,
            y - 28,
            self.reshape_arabic(f"الرقم الضريبي: {invoice_data.get('tax_code', '')}"),
        )
        
        # إضافة عنوان الشركة
        document.setFont(self.arabic_font, 10)
        document.setFillColor(self.theme.light_text)
        company_address = invoice_data.get('company_address', 'المملكة العربية السعودية')
        document.drawRightString(self.width - 60, y - 44, self.reshape_arabic(company_address))

        document.setFillColor(self.theme.text)
        document.setFont("Helvetica", 12)
        document.drawString(60, y - 12, invoice_data.get("english_company_name", ""))

        document.setFont("Helvetica", 10)
        document.drawString(60, y - 30, f"VAT No.: {invoice_data.get('tax_code', '')}")

        document.setStrokeColor(self.theme.border)
        document.setLineWidth(1.5)
        document.line(50, y - 80, self.width - 50, y - 80)

        return y - 100

    def draw_qr_code(self, document: canvas.Canvas, invoice_data: Dict[str, any], x: float, y: float, size: float = 70) -> None:
        """Draw QR Code at specified position without frame for elegant look."""
        qr_image_path = ""
        try:
            qr_image_path = self.generate_qr_code(invoice_data)
            if qr_image_path and os.path.exists(qr_image_path):
                # Draw the QR code image directly without frame for clean look
                document.drawImage(
                    qr_image_path,
                    x,
                    y - size,
                    width=size,
                    height=size,
                    preserveAspectRatio=True,
                    mask="auto",
                )

        except Exception as e:
            print(f"QR Code generation error: {e}")
            # Continue without QR code if there's an error
        finally:
            if qr_image_path and os.path.exists(qr_image_path):
                try:
                    os.remove(qr_image_path)
                except Exception:
                    pass

    def draw_invoice_info(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        # Draw the title centered
        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 18)
        document.drawCentredString(self.width / 2, y - 10, self.reshape_arabic(self.template_name))

        document.setFillColor(self.theme.light_text)
        document.setFont("Helvetica", 10)
        document.drawCentredString(self.width / 2, y - 30, "Tax Invoice")

        # Remove the border around the invoice info section

        # Remove divider lines between sections for cleaner look

        # Left section: QR Code
        qr_x_position = 70  # Left position
        qr_y_position = y - 70  # Center in the box
        self.draw_qr_code(document, invoice_data, qr_x_position, qr_y_position, size=80)

        # Center section: Customer Info
        customer_x = self.width * 0.6  # Center position
        customer_y = y - 70

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 11)
        document.drawRightString(customer_x, customer_y, self.reshape_arabic("بيانات العميل"))

        customer_y -= 20
        document.setFillColor(self.theme.text)
        document.setFont(self.arabic_font, 9)

        customer_info = [
            f"الاسم: {invoice_data.get('customer_name', '')}",
            f"الهاتف: {invoice_data.get('customer_phone', '')}",
            f"العنوان: {invoice_data.get('customer_address', '')}",
            f"الرقم الضريبي: {invoice_data.get('customer_tax_number', '-')}",
        ]

        for info in customer_info:
            document.drawRightString(customer_x, customer_y, self.reshape_arabic(info))
            customer_y -= 14

        # Right section: Invoice Info
        right_x = self.width - 60
        info_y = y - 70

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
        ]

        for info in invoice_info:
            document.drawRightString(right_x, info_y, self.reshape_arabic(info))
            info_y -= 14

        # Add appropriate spacing between invoice info section and items table
        return y -170

    def draw_items_table(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        headers = [
            "رقم",
            "كود الصنف",
            "وصف الصنف",
            "وحدة",
            "الكمية",
            "سعر الوحدة",
            "الخصم",
            "مبلغ الضريبة",
            "المجموع",
        ]
        column_widths = [25, 65, 140, 40, 40, 60, 45, 60, 70]
        table_width = sum(column_widths)
        table_x = (self.width - table_width) / 2  # توسيط الجدول

        # إضافة عنوان الجدول الرئيسي في الوسط
        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 14)
        document.drawCentredString(self.width / 2, y + 10, self.reshape_arabic("أصناف الفاتورة"))
        document.setFillColor(self.theme.border)
        document.setLineWidth(1)
        document.line(40, y + 5, self.width - 40, y + 5)

        draw_header_row(document, self, headers, column_widths, table_x, y, 32)
        y -= 32

        rows = []
        def _to_float(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        for index, item in enumerate(invoice_data.get("items", []), start=1):
            quantity = _to_float(item.get("quantity", 0))
            price = _to_float(item.get("price", 0))
            discount_amount_total = _to_float(item.get("discount_amount", 0))
            discount_per_unit = _to_float(item.get("discount_per_unit", 0))
            tax_amount = _to_float(item.get("tax_amount", 0))
            total = _to_float(item.get("total", 0))

            if not discount_amount_total and discount_per_unit and quantity:
                discount_amount_total = discount_per_unit * quantity

            quantity_display = f"{quantity:.0f}" if quantity.is_integer() else f"{quantity:.2f}"

            rows.append(
                (
                    str(index),
                    item.get("item_code", "").strip(),
                    self.reshape_arabic(item.get("description", "").strip()),
                    self.reshape_arabic(item.get("unit", "").strip()),
                    quantity_display,
                    f"{price:.2f}",
                    f"{discount_amount_total:.2f}",
                    f"{tax_amount:.2f}",
                    f"{total:.2f}",
                )
            )

        y = draw_table_rows(document, self, rows, column_widths, table_x, y, 28, 180)
        return y - 15

    def _calculate_totals_from_items(self, invoice_data: Dict[str, any]) -> Dict[str, float]:
        """Calculate totals directly from items data for consistency."""
        subtotal_before_discount = 0.0
        total_discount = 0.0
        total_tax = 0.0
        subtotal_after_discount = 0.0

        try:
            tax_rate = invoice_data.get('tax_rate', 15) / 100
        except Exception:
            tax_rate = 0.15

        for item in invoice_data.get("items", []):
            try:
                quantity = float(item.get("quantity", 0) or 0)
            except (TypeError, ValueError):
                quantity = 0.0
            try:
                price = float(item.get("price", 0) or 0)
            except (TypeError, ValueError):
                price = 0.0
            try:
                discount_amount = float(item.get("discount_amount", 0) or 0)
            except (TypeError, ValueError):
                discount_amount = 0.0
            try:
                discount_per_unit = float(item.get("discount_per_unit", 0) or 0)
            except (TypeError, ValueError):
                discount_per_unit = 0.0

            if not discount_amount and discount_per_unit and quantity:
                discount_amount = discount_per_unit * quantity

            item_subtotal = price * quantity
            subtotal_before_discount += item_subtotal

            total_discount += discount_amount

            net_price_per_unit = max(price - discount_per_unit, 0)
            price_after_discount = net_price_per_unit * quantity

            tax_amount = price_after_discount * tax_rate
            total_tax += tax_amount

            subtotal_after_discount = subtotal_before_discount - total_discount

        grand_total = subtotal_after_discount + total_tax

        return {
            'subtotal_before_discount': subtotal_before_discount,
            'total_discount': total_discount,
            'subtotal': subtotal_after_discount,
            'tax': total_tax,
            'total': grand_total
        }

    def draw_totals(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        totals_x = self.width - 60
        totals_width = 250

        # Calculate totals directly from items data for accuracy
        calculated_totals = self._calculate_totals_from_items(invoice_data)

        totals = [
            {"label": "الإجمالي غير شامل الضريبة ", "value": calculated_totals["subtotal_before_discount"]},
            {"label": "قيمة الخصم", "value": calculated_totals["total_discount"]},
            {"label": "قيمة الضريبة", "value": calculated_totals["tax"]},
        ]

        y = draw_total_rows(document, self, totals, totals_x, totals_width, y)

        final_height = 35
        document.setFillColor(self.theme.total_bg)
        document.roundRect(totals_x - totals_width, y - final_height, totals_width, final_height, 5, fill=1, stroke=0)

        document.setStrokeColor(self.theme.accent)
        document.setLineWidth(2)
        document.roundRect(totals_x - totals_width, y - final_height, totals_width, final_height, 5, fill=0, stroke=1)

        document.setFillColor(self.theme.white)
        document.setFont(self.arabic_font, 13)
        document.drawRightString(totals_x - 160, y - 23, self.reshape_arabic("الإجمالي المستحق"))
        document.setFont(self.arabic_font, 16)
        document.drawRightString(
            totals_x - 15,
            y - 24,
            f"{calculated_totals['total']:.2f} {invoice_data.get('currency', 'SAR')}",
        )

        y -= final_height + 12
        document.setFillColor(self.theme.text)
        document.setFont(self.arabic_font, 9)
        document.drawRightString(
            totals_x - 10,
            y - 5,
            self.reshape_arabic(f"فقط: {self.number_to_arabic_words(calculated_totals['total'])}"),
        )

        return y - 25

    def draw_footer(self, document: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> None:
        notes = invoice_data.get("notes")
        if notes:
            notes_height = 60
            document.setStrokeColor(self.theme.border)
            document.setFillColor(colors.HexColor("#F8FBFF"))
            document.rect(40, y - notes_height, self.width - 80, notes_height, fill=1, stroke=1)

            document.setFillColor(self.theme.primary)
            document.setFont(self.arabic_font, 9)
            document.drawRightString(self.width - 50, y - 15, self.reshape_arabic("ملاحظات:"))

            # الحصول على محاذاة النص المختارة
            notes_alignment = invoice_data.get("notes_alignment", "right")
            
            document.setFillColor(self.theme.text)
            document.setFont(self.arabic_font, 8)
            notes_text = self.reshape_arabic(notes[:200])
            text_y = y - 35
            
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

        footer_height = 40
        document.setFillColor(self.theme.primary)
        document.rect(0, 0, self.width, footer_height, fill=1, stroke=0)

        document.setFillColor(self.theme.gold)
        document.rect(0, footer_height - 3, self.width, 3, fill=1, stroke=0)

        document.setFillColor(self.theme.white)
        document.setFont(self.arabic_font, 10)
        document.drawCentredString(self.width / 2, 22, self.reshape_arabic("نحن في خدمتكم دائماً"))

        company_address = invoice_data.get("company_address")
        if company_address:
            document.setFont(self.arabic_font, 8)
            address_text = f"العنوان: {company_address}"
            document.drawCentredString(self.width / 2, 10, self.reshape_arabic(address_text))
