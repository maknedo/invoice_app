"""Rawayih invoice template - table-based layout matching the exact structure."""

from __future__ import annotations

import os
from typing import Dict

from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .base import BaseInvoiceTemplate, TemplateTheme
from .components import draw_logo


RAWAYIH_THEME = TemplateTheme(
    primary=colors.HexColor("#8B6F47"),
    secondary=colors.HexColor("#A89968"),
    accent=colors.HexColor("#E8DCC8"),
    gold=colors.HexColor("#C9A961"),
    header_bg=colors.HexColor("#F8F6F0"),
    table_header=colors.HexColor("#D4C5AB"),
    table_row1=colors.HexColor("#F5F1E8"),
    table_row2=colors.HexColor("#FFFFFF"),
    border=colors.HexColor("#A89968"),
    text=colors.HexColor("#2C2416"),
    light_text=colors.HexColor("#5D4E3A"),
    total_bg=colors.HexColor("#E8DCC8"),
)


class RawayihInvoiceTemplate(BaseInvoiceTemplate):
    def __init__(self, font_name: str = 'Arial', custom_font_path: str = None) -> None:
        super().__init__(font_name, custom_font_path)
        self.template_name = "فاتورة روائح بيتك"
        self.theme = RAWAYIH_THEME
    
    @staticmethod
    def _to_float(val) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    def generate(self, invoice_data: Dict[str, any], filename: str) -> bool:
        custom_colors = invoice_data.get('custom_colors')
        if custom_colors:
            self.apply_custom_colors(custom_colors)

        document = canvas.Canvas(filename, pagesize=(self.width, self.height))
        document.setTitle(f"Invoice {invoice_data.get('invoice_number', '')}")

        margin = 30
        table_width = self.width - (2 * margin)
        table_x = margin
        y_start = self.height - 40
        
        y = y_start
        
        y = self._draw_row1_header(document, invoice_data, table_x, y, table_width)
        y = self._draw_row2_info(document, invoice_data, table_x, y, table_width)
        y = self._draw_row3_items_table(document, invoice_data, table_x, y, table_width)
        y = self._draw_row4_totals(document, invoice_data, table_x, y, table_width)
        y = self._draw_row5_amount_signature(document, invoice_data, table_x, y, table_width)
        self._draw_row6_footer_bar(document, invoice_data)

        document.save()
        return True

    def _draw_row1_header(self, document: canvas.Canvas, invoice_data: Dict, x: float, y: float, width: float) -> float:
        row_height = 90
        y_bottom = y - row_height
        
        document.setFillColor(self.theme.header_bg)
        document.rect(x, y_bottom, width, row_height, fill=1, stroke=0)
        
        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(2)
        document.rect(x, y_bottom, width, row_height, fill=0, stroke=1)
        
        col_width = width / 3
        
        left_x = x + 10
        center_x = x + col_width
        right_x = x + 2 * col_width
        
        y_text = y - 20
        
        document.setFillColor(self.theme.primary)
        document.setFont("Helvetica-Bold", 14)
        document.drawString(left_x, y_text, invoice_data.get("english_company_name", ""))
        
        y_text -= 18
        document.setFont("Helvetica", 8)
        document.setFillColor(self.theme.light_text)
        document.drawString(left_x, y_text, f"VAT : {invoice_data.get('tax_code', '')}")
        
        logo_path = invoice_data.get("logo_path")
        if logo_path and os.path.exists(logo_path):
            logo_x = center_x + col_width / 2
            logo_y = y_bottom + row_height / 2 + 40
            draw_logo(logo_x, logo_y, 65, logo_path, document)
        
        y_text = y - 20
        right_text_x = x + width - 10
        
        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 18)
        document.drawRightString(right_text_x, y_text, self.reshape_arabic(invoice_data.get("company_name", "")))
        
        y_text -= 18
        document.setFont(self.arabic_font, 9)
        document.setFillColor(self.theme.light_text)
        document.drawRightString(right_text_x, y_text, self.reshape_arabic(f"الرقم الضريبي: {invoice_data.get('tax_code', '')}"))
        
        company_address = invoice_data.get("company_address")
        if company_address:
            y_text -= 16
            document.drawRightString(right_text_x, y_text, self.reshape_arabic(company_address))
        
        return y_bottom

    def _draw_row2_info(self, document: canvas.Canvas, invoice_data: Dict, x: float, y: float, width: float) -> float:
        row_height = 50
        y_bottom = y - row_height
        
        document.setFillColor(self.theme.table_row1)
        document.rect(x, y_bottom, width, row_height, fill=1, stroke=0)
        
        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(1.5)
        document.rect(x, y_bottom, width, row_height, fill=0, stroke=1)
        
        col_width = width / 3
        
        document.setFillColor(self.theme.text)
        
        left_x = x + 10
        left_right = x + col_width - 10
        left_label_x = left_right
        left_value_left = left_x
        left_value_right = max(left_value_left + 1, left_label_x - 60)
        left_value_center = (left_value_left + left_value_right) / 2

        y_text = y - 15
        document.setFont(self.arabic_font, 9)
        invoice_number = invoice_data.get("invoice_number", "")
        document.drawCentredString(left_value_center, y_text, invoice_number)
        document.drawRightString(left_label_x, y_text, self.reshape_arabic("رقم الفاتورة:"))
        
        y_text -= 14
        document.setFont(self.arabic_font, 8)
        date_str = invoice_data.get("date", "")
        time_str = invoice_data.get("time", "")
        document.drawCentredString(left_value_center, y_text, f"{time_str}  {date_str}")
        document.drawRightString(left_label_x, y_text, self.reshape_arabic("التاريخ:"))
        
        warehouse = invoice_data.get("warehouse", "")
        if warehouse:
            y_text -= 14
            document.drawCentredString(left_value_center, y_text, self.reshape_arabic(warehouse))
            document.drawRightString(left_label_x, y_text, self.reshape_arabic("المخزن:"))
        
        center_x = x + col_width + 10
        y_text = y - 15
        document.setFont(self.arabic_font, 12)
        document.drawCentredString(center_x + col_width / 2 - 10, y_text, self.reshape_arabic("فاتورة ضريبية مبسطة"))
        y_text -= 18
        document.setFont(self.arabic_font, 9)
        invoice_type = invoice_data.get("invoice_type", "نقداً")
        document.drawCentredString(center_x + col_width / 2 - 10, y_text, self.reshape_arabic(f"نوع الفاتورة: {invoice_type}"))
        
        right_x = x + 2 * col_width + 10
        right_right = x + width - 10
        right_label_x = right_right
        right_value_left = right_x
        right_value_right = max(right_value_left + 1, right_label_x - 60)
        right_value_center = (right_value_left + right_value_right) / 2

        y_text = y - 15
        document.setFont(self.arabic_font, 9)
        customer_name = invoice_data.get("customer_name", "")
        if customer_name:
            document.drawCentredString(right_value_center, y_text, self.reshape_arabic(customer_name))
            document.drawRightString(right_label_x, y_text, self.reshape_arabic("الاسم:"))
        
        y_text -= 14
        document.setFont(self.arabic_font, 8)
        customer_tax = invoice_data.get("customer_tax_number", "")
        if customer_tax:
            document.drawCentredString(right_value_center, y_text, customer_tax)
            document.drawRightString(right_label_x, y_text, self.reshape_arabic("الرقم الضريبي:"))
        
        customer_phone = invoice_data.get("customer_phone", "")
        if customer_phone:
            y_text -= 14
            document.drawCentredString(right_value_center, y_text, customer_phone)
            document.drawRightString(right_label_x, y_text, self.reshape_arabic("الهاتف:"))
        
        return y_bottom

    def _draw_row3_items_table(self, document: canvas.Canvas, invoice_data: Dict, x: float, y: float, width: float) -> float:
        items = invoice_data.get("items", [])
        header_height = 25
        row_height = 22
        min_rows = 5
        footer_padding = 2  # keep a slight gap before totals section
        
        num_rows = max(len(items), min_rows)
        total_height = header_height + (row_height * num_rows) + footer_padding
        
        y_bottom = y - total_height
        
        document.setFillColor(colors.white)
        document.rect(x, y_bottom, width, total_height, fill=1, stroke=0)
        
        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(1.5)
        document.rect(x, y_bottom, width, total_height, fill=0, stroke=1)
        
        column_ratios = [0.075, 0.15, 0.43, 0.09, 0.125, 0.13]
        col_widths = [width * ratio for ratio in column_ratios]
        width_correction = width - sum(col_widths)
        col_widths[-1] += width_correction
        headers = [
            ("م", "S.No."),
            ("رقم القطعة", "Part Number"),
            ("البيــــــــــان", "Descriptioon"),
            ("الكمية", "Qty."),
            ("سعر البيع", "Sales Price"),
            ("الإجمالي", "Total")
        ]
        
        y_header = y - header_height
        document.setFillColor(self.theme.table_header)
        document.rect(x, y_header, width, header_height, fill=1, stroke=0)
        
        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(1.5)
        document.line(x, y_header, x + width, y_header)
        
        x_pos = x
        for (ar_header, en_header), col_width in zip(headers, col_widths):
            cx = x_pos + col_width / 2
            
            document.setFillColor(self.theme.text)
            document.setFont(self.arabic_font, 8)
            document.drawCentredString(cx, y - 10, self.reshape_arabic(ar_header))
            
            document.setFont("Helvetica", 7)
            document.drawCentredString(cx, y - 20, en_header)
            
            x_pos += col_width
        
        y_row = y_header
        row_positions = []
        for idx in range(num_rows):
            y_row_bottom = y_row - row_height
            row_color = self.theme.table_row1 if idx % 2 == 0 else self.theme.table_row2
            document.setFillColor(row_color)
            document.rect(x, y_row_bottom, width, row_height, fill=1, stroke=0)
            row_positions.append((y_row, y_row_bottom))
            y_row = y_row_bottom

        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(1)
        x_pos = x
        for col_width in col_widths[:-1]:
            x_pos += col_width
            document.line(x_pos, y_bottom, x_pos, y)
        
        document.setLineWidth(0.8)
        for _, boundary in row_positions[:-1]:
            document.line(x, boundary, x + width, boundary)
        
        for idx, (row_top, row_bottom) in enumerate(row_positions):
            if idx >= len(items):
                continue
            
            y_text = row_top - 14
            x_pos = x
            item = items[idx]
            
            document.setFillColor(self.theme.text)
            document.setFont(self.arabic_font, 8)
            
            document.drawCentredString(x_pos + col_widths[0] / 2, y_text, str(idx + 1))
            x_pos += col_widths[0]
            
            item_code = item.get("item_code", "")
            document.drawCentredString(x_pos + col_widths[1] / 2, y_text, str(item_code))
            x_pos += col_widths[1]
            
            description = item.get("description", "")
            document.drawCentredString(x_pos + col_widths[2] / 2, y_text, self.reshape_arabic(description))
            x_pos += col_widths[2]
            
            quantity = self._to_float(item.get("quantity", 0))
            document.drawCentredString(x_pos + col_widths[3] / 2, y_text, f"{quantity:,.2f}")
            x_pos += col_widths[3]
            
            price = self._to_float(item.get("price", 0))
            document.drawCentredString(x_pos + col_widths[4] / 2, y_text, f"{price:,.2f}")
            x_pos += col_widths[4]
            
            total = self._to_float(item.get("total", 0))
            document.drawCentredString(x_pos + col_widths[5] / 2, y_text, f"{total:,.2f}")
        
        return y_bottom

    def _draw_row4_totals(self, document: canvas.Canvas, invoice_data: Dict, x: float, y: float, width: float) -> float:
        row_height = 70
        y_bottom = y - row_height
        
        document.setFillColor(colors.white)
        document.rect(x, y_bottom, width, row_height, fill=1, stroke=0)
        
        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(1.5)
        document.rect(x, y_bottom, width, row_height, fill=0, stroke=1)
        
        split_x = x + width * 0.55
        document.line(split_x, y_bottom, split_x, y)
        
        subtotal = self._to_float(invoice_data.get("subtotal", 0))
        tax_rate = self._to_float(invoice_data.get("tax_rate", 15))
        tax_amount = self._to_float(invoice_data.get("tax", 0))
        total = self._to_float(invoice_data.get("total", 0))
        
        section_left = split_x + 20
        section_right = x + width - 20
        value_center_x = (section_left + section_right) / 2

        y_line = y - 18

        document.setFillColor(self.theme.text)
        document.setFont(self.arabic_font, 9)
        document.drawRightString(section_right, y_line, self.reshape_arabic("الإجمالــــــي"))

        document.setFont("Helvetica", 8)
        document.drawString(section_left, y_line, "Total")

        document.setFont(self.arabic_font, 9)
        document.drawCentredString(value_center_x, y_line, f"{subtotal:,.2f}")

        y_line -= 18
        document.setFont(self.arabic_font, 9)
        document.drawRightString(section_right, y_line, self.reshape_arabic("الضريبة المضافة (15%)"))

        document.setFont("Helvetica", 8)
        document.drawString(section_left, y_line, f"VAT (%{tax_rate:.0f})")

        document.setFont(self.arabic_font, 9)
        document.drawCentredString(value_center_x, y_line, f"{tax_amount:,.2f}")

        y_line -= 18
        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 10)
        document.drawRightString(section_right, y_line, self.reshape_arabic("الاجمالي الكلي"))

        document.setFillColor(self.theme.text)
        document.setFont("Helvetica-Bold", 8)
        document.drawString(section_left, y_line, "Grand Total")

        document.setFillColor(self.theme.primary)
        document.setFont(self.arabic_font, 10)
        document.drawCentredString(value_center_x, y_line, f"{total:,.2f}")

        qr_data = self.generate_qr_code(invoice_data)
        if qr_data:
            qr_size = 60
            qr_x = x + 20
            qr_y = y - 63
            
            document.drawImage(qr_data, qr_x, qr_y, width=qr_size, height=qr_size)
            
            try:
                os.remove(qr_data)
            except Exception:
                pass
            
            document.setStrokeColor(self.theme.border)
            document.setLineWidth(1)
            document.rect(qr_x - 2, qr_y - 2, qr_size + 4, qr_size + 4, fill=0, stroke=1)
        
        return y_bottom

    def _draw_row5_amount_signature(self, document: canvas.Canvas, invoice_data: Dict, x: float, y: float, width: float) -> float:
        row_height = 55
        y_bottom = y - row_height
        
        document.setFillColor(self.theme.table_row1)
        document.rect(x, y_bottom, width, row_height, fill=1, stroke=0)
        
        document.setStrokeColor(self.theme.gold)
        document.setLineWidth(1.5)
        document.rect(x, y_bottom, width, row_height, fill=0, stroke=1)
        
        split_x = x + width * 0.65
        document.line(split_x, y_bottom, split_x, y)
        
        document.setFillColor(self.theme.text)
        
        total = self._to_float(invoice_data.get("total", 0))
        total_words = self.number_to_arabic_words(total)
        
        y_text = y - 25
        document.setFont(self.arabic_font, 9)
        document.drawRightString(x + width * 0.65 - 10, y_text, self.reshape_arabic(f"المبلغ كتابة: {total_words}"))
        
        y_text = y - 15
        sig_x = split_x + 15
        
        document.setFont(self.arabic_font, 9)
        document.drawRightString(sig_x + 50, y_text, self.reshape_arabic("المستلم:"))
        y_text = y - 15
        sig2_x = split_x + width * 0.18
        document.setFont(self.arabic_font, 9)
        document.drawRightString(sig2_x + 50, y_text, self.reshape_arabic("التوقيـــــع:"))
        
        return y_bottom

    def _draw_row6_footer_bar(self, document: canvas.Canvas, invoice_data: Dict) -> None:
        bar_height = 22
        
        document.setFillColor(self.theme.primary)
        document.rect(0, 0, self.width, bar_height, fill=1, stroke=0)
        
        document.setFillColor(colors.white)
        document.setFont(self.arabic_font, 9)
        
        company_address = invoice_data.get('company_address', 'نجران - دحضة')
       
        
        footer_text = f"{company_address}"
        
        document.drawCentredString(self.width / 2, 7, self.reshape_arabic(footer_text))
