from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import qrcode
import os
from num2words import num2words
import base64
from datetime import datetime

class BaseInvoiceTemplate:
    """القالب الأساسي لجميع النماذج"""

    def __init__(self):
        self.width, self.height = A4
        self.setup_arabic_font()
        self.colors = {
            'primary': colors.HexColor('#1B5E20'),
            'secondary': colors.HexColor('#2E7D32'),
            'accent': colors.HexColor('#4CAF50'),
            'gold': colors.HexColor('#FFB300'),
            'header_bg': colors.HexColor('#F1F8E9'),
            'table_header': colors.HexColor('#2E7D32'),
            'table_row1': colors.white,
            'table_row2': colors.HexColor('#F9FBF8'),
            'border': colors.HexColor('#A5D6A7'),
            'text': colors.HexColor('#1B5E20'),
            'light_text': colors.HexColor('#558B2F'),
            'total_bg': colors.HexColor('#2E7D32'),
            'white': colors.white
        }

    def get_template(self, template_id):
        """Factory method to get template instance by ID"""
        if template_id in AVAILABLE_TEMPLATES:
            return AVAILABLE_TEMPLATES[template_id]['class']()
        return StandardInvoiceTemplate()  # Default fallback
    
    def setup_arabic_font(self):
        font_path = self.find_arabic_font()
        if font_path:
            try:
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                self.arabic_font = 'Arabic'
            except:
                self.arabic_font = 'Helvetica'
        else:
            self.arabic_font = 'Helvetica'
    
    def find_arabic_font(self):
        possible_fonts = [
            'C:\\Windows\\Fonts\\arial.ttf',
            'C:\\Windows\\Fonts\\times.ttf',
            'C:\\Windows\\Fonts\\tahoma.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Supplemental/Arial.ttf'
        ]
        
        for font in possible_fonts:
            if os.path.exists(font):
                return font
        return None
    
    def reshape_arabic(self, text):
        if text and any('\u0600' <= c <= '\u06FF' for c in str(text)):
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        return str(text)
    
    def generate_qr_code(self, invoice_data):
        """توليد QR Code"""
        def create_tlv(tag, value):
            value_bytes = value.encode('UTF-8')
            length = len(value_bytes)
            return bytes([tag]) + bytes([length]) + value_bytes
        
        company_name = invoice_data.get('company_name', '')
        vat_number = invoice_data.get('tax_code', '')
        date_str = invoice_data['date']
        time_str = invoice_data['time']
        
        try:
            date_parts = date_str.split('/')
            if len(date_parts) == 3:
                day, month, year = date_parts
                timestamp = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{time_str}Z"
            else:
                timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        total_amount = f"{invoice_data['total']:.2f}"
        vat_amount = f"{invoice_data['tax']:.2f}"
        
        tlv_data = b''
        tlv_data += create_tlv(1, company_name)
        tlv_data += create_tlv(2, vat_number)
        tlv_data += create_tlv(3, timestamp)
        tlv_data += create_tlv(4, total_amount)
        tlv_data += create_tlv(5, vat_amount)
        
        qr_code_data = base64.b64encode(tlv_data).decode('UTF-8')
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(qr_code_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        temp_file = 'temp_qr.png'
        img.save(temp_file)
        
        return temp_file
    
    def number_to_arabic_words(self, number):
        try:
            words = num2words(int(number), lang='ar')
            return f"{words} ريال سعودي"
        except:
            return ""


class StandardInvoiceTemplate(BaseInvoiceTemplate):
    """النموذج الأساسي - الفاتورة الضريبية الكاملة (الحالي)"""
    
    def __init__(self):
        super().__init__()
        self.template_name = "فاتورة ضريبية مبسطة"
    
    def draw_header(self, c, invoice_data, y):
        """رسم ترويسة الفاتورة"""
        c.setFillColor(self.colors['header_bg'])
        c.rect(0, y - 120, self.width, 120, fill=1, stroke=0)

        c.setFillColor(self.colors['primary'])
        c.rect(0, y, self.width, 12, fill=1, stroke=0)

        c.setFillColor(self.colors['gold'])
        c.rect(0, y - 15, self.width, 3, fill=1, stroke=0)

        y -= 25

        # الشعار في الوسط
        logo_y = y - 55
        logo_x = self.width / 2 - 35  # 70/2 = 35
        if invoice_data.get('logo_path') and os.path.exists(invoice_data['logo_path']):
            try:
                logo_size = 70
                c.drawImage(invoice_data['logo_path'], logo_x, logo_y,
                           width=logo_size, height=logo_size,
                           preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Error loading logo: {e}")

        # معلومات الشركة على اليمين
        company_x_right = self.width - 50
        company_y = y - 10

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 18)
        c.drawRightString(company_x_right, company_y, self.reshape_arabic(invoice_data.get('company_name', '')))

        company_y -= 18
        c.setFont(self.arabic_font, 10)
        c.drawRightString(company_x_right, company_y, self.reshape_arabic(f"الرقم الضريبي: {invoice_data.get('tax_code', '')}"))

        company_y -= 16
        c.setFont(self.arabic_font, 9)
        c.setFillColor(self.colors['light_text'])
        c.drawRightString(company_x_right, company_y, self.reshape_arabic("المملكة العربية السعودية"))

        # الاسم الإنجليزي على اليسار
        company_x_left = 50
        company_y_left = y - 10

        c.setFillColor(self.colors['text'])
        c.setFont('Helvetica', 12)
        c.drawString(company_x_left, company_y_left, invoice_data.get('english_company_name', ''))
        
        # الرقم الضريبي بالإنجليزي تحت اسم الشركة
        company_y_left -= 18
        c.setFont('Helvetica', 10)
        c.drawString(company_x_left, company_y_left, f"VAT No.: {invoice_data.get('tax_code', '')}")

        c.setStrokeColor(self.colors['gold'])
        c.setLineWidth(2)
        c.line(40, y - 100, self.width - 40, y - 100)

        return y - 120
    
    def draw_invoice_info_with_qr(self, c, invoice_data, y):
        """رسم معلومات الفاتورة مع QR"""
        # إضافة مسافة بسيطة بين الترويسة وعنوان الفاتورة
        title_spacing = 15  # مسافة بسيطة بين الترويسة والعنوان
        
        # عنوان الفاتورة في الوسط
        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 16)
        c.drawCentredString(self.width / 2, y - title_spacing, self.reshape_arabic(self.template_name))

        # النص الإنجليزي تحت العنوان العربي
        c.setFillColor(self.colors['light_text'])
        c.setFont(self.arabic_font, 10)
        c.drawCentredString(self.width / 2, y - title_spacing - 15, "Simplified Tax Invoice")

        # المسافة بين العنوان والمربع - نجعلها قريبة من العنوان
        box_y = y - title_spacing - 30  # مسافة قصيرة بين العنوان والمربع
        box_height = 110

        c.setStrokeColor(self.colors['border'])
        c.setFillColor(self.colors['white'])
        c.setLineWidth(1)
        c.rect(40, box_y - box_height, self.width - 80, box_height, fill=1, stroke=1)

        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(0.5)
        # تعديل موضع الخطوط الفاصلة داخل المربع
        c.line(self.width * 0.65, box_y - 5, self.width * 0.65, box_y - box_height + 5)
        c.line(170, box_y - 5, 170, box_y - box_height + 5)

        right_x = self.width - 50
        info_y = box_y - 18  # تعديل موضع النص ليتناسب مع المربع الجديد

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 11)
        c.drawRightString(right_x, info_y, self.reshape_arabic("بيانات الفاتورة"))

        info_y -= 20
        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)

        invoice_info = [
            f"رقم الفاتورة: {invoice_data['invoice_number']}",
            f"التاريخ: {invoice_data.get('date', '')}",
            f"الوقت: {invoice_data.get('time', '')}",
            f"نوع الفاتورة: {invoice_data.get('invoice_type', '')}",
            f"المخزن: {invoice_data.get('warehouse', '')}",
        ]

        if invoice_data.get('cost_center'):
            invoice_info.append(f"مركز التكلفة: {invoice_data['cost_center']}")

        for info in invoice_info:
            c.drawRightString(right_x, info_y, self.reshape_arabic(info))
            info_y -= 14

        middle_right = self.width * 0.63
        middle_y = box_y - 18  # تعديل موضع النص ليتناسب مع المربع الجديد

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 11)
        c.drawRightString(middle_right, middle_y, self.reshape_arabic("بيانات العميل"))

        middle_y -= 20
        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)

        customer_info = [f"الاسم: {invoice_data.get('customer_name', '')}"]

        if invoice_data.get('customer_phone'):
            customer_info.append(f"الهاتف: {invoice_data['customer_phone']}")
        if invoice_data.get('customer_tax_number'):
            customer_info.append(f"الرقم الضريبي: {invoice_data['customer_tax_number']}")
        if invoice_data.get('customer_address'):
            customer_info.append(f"العنوان: {invoice_data['customer_address']}")

        for info in customer_info:
            c.drawRightString(middle_right, middle_y, self.reshape_arabic(info))
            middle_y -= 14

        qr_file = self.generate_qr_code(invoice_data)
        qr_size = 90
        qr_x = 50
        qr_y = box_y - 93  # تعديل موضع QR ليتناسب مع المربع الجديد

        c.drawImage(qr_file, qr_x, qr_y, width=qr_size, height=qr_size)

        c.setFont(self.arabic_font, 8)  # زيادة حجم الخط قليلاً
        c.setFillColor(self.colors['light_text'])
        c.drawCentredString(qr_x + qr_size/2, qr_y - 8, self.reshape_arabic("رمز التحقق"))

        try:
            os.remove(qr_file)
        except:
            pass

        # تعديل قيمة الإرجاع لتتناسب مع التغييرات التي أجريناها
        return box_y - box_height - 15
    
    def draw_items_table(self, c, invoice_data, y):
        """رسم جدول الأصناف"""
        headers = [
            "م", "الكود", "اسم الصنف", "الوحدة", "الكمية", 
            "السعر", "الخصم", "الضريبة", "الإجمالي"
        ]
        
        headers_ar = [self.reshape_arabic(h) for h in headers]
        col_widths = [25, 50, 140, 40, 40, 50, 45, 50, 60]
        table_width = sum(col_widths)
        table_x = self.width - 40 - table_width
        
        c.setFillColor(self.colors['table_header'])
        c.rect(table_x, y - 26, table_width, 26, fill=1, stroke=0)
        
        c.setStrokeColor(self.colors['gold'])
        c.setLineWidth(2)
        c.rect(table_x, y - 26, table_width, 26, fill=0, stroke=1)
        
        c.setFillColor(self.colors['white'])
        c.setFont(self.arabic_font, 9)
        
        x_pos = self.width - 40
        for i, header in enumerate(headers_ar):
            text_x = x_pos - col_widths[i] / 2
            c.drawCentredString(text_x, y - 16, header)
            
            if i < len(headers) - 1:
                c.setStrokeColor(colors.HexColor('#FFFFFF40'))
                c.setLineWidth(0.5)
                c.line(x_pos - col_widths[i], y - 26, x_pos - col_widths[i], y)
            
            x_pos -= col_widths[i]
        
        y -= 26
        
        row_height = 24
        c.setFont(self.arabic_font, 8.5)
        
        for idx, item in enumerate(invoice_data['items'], 1):
            if y - row_height < 200:
                c.showPage()
                c.setFont(self.arabic_font, 8.5)
                y = self.height - 50
            
            if idx % 2 == 0:
                c.setFillColor(self.colors['table_row2'])
            else:
                c.setFillColor(self.colors['table_row1'])
            
            c.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=0)
            
            c.setStrokeColor(self.colors['border'])
            c.setLineWidth(0.3)
            c.rect(table_x, y - row_height, table_width, row_height, fill=0, stroke=1)
            
            c.setFillColor(self.colors['text'])
            
            item_values = [
                str(idx),
                item.get('item_code', ''),
                self.reshape_arabic(item.get('description', '')),
                self.reshape_arabic(item.get('unit', '')),
                str(int(item.get('quantity', 0))),
                f"{item.get('price', 0):.2f}",
                f"{item.get('discount_percent', 0):.0f}%",
                f"{item.get('tax_amount', 0):.2f}",
                f"{item.get('total', 0):.2f}"
            ]
            
            x_pos = self.width - 40
            for i, value in enumerate(item_values):
                text_x = x_pos - col_widths[i] / 2
                if i in [2, 3]:
                    c.drawRightString(x_pos - 10, y - 13, str(value))
                else:
                    c.drawCentredString(text_x, y - 13, str(value))
                x_pos -= col_widths[i]
            
            y -= row_height
        
        return y - 15
    
    def draw_totals(self, c, invoice_data, y):
        """رسم مجاميع الفاتورة"""
        totals_width = 240
        totals_x = self.width - 50
        
        c.setFont(self.arabic_font, 10)
        
        totals_info = [
            ("إجمالي قبل الضريبة", invoice_data.get('subtotal', 0), self.colors['text']),
            ("إجمالي الخصم", invoice_data.get('discount', 0), colors.HexColor('#D32F2F')),
            ("إجمالي الضريبة", invoice_data.get('tax', 0), colors.HexColor('#388E3C')),
        ]
        
        for label, value, color in totals_info:
            c.setFillColor(self.colors['white'])
            c.rect(totals_x - totals_width, y - 22, totals_width, 22, fill=1, stroke=0)
            
            c.setStrokeColor(self.colors['border'])
            c.setLineWidth(0.5)
            c.line(totals_x - totals_width + 20, y - 2, totals_x - 10, y - 2)
            
            c.setFillColor(color)
            c.drawRightString(totals_x - 180, y - 13, self.reshape_arabic(label))
            c.drawRightString(totals_x - 15, y - 13, f"{value:.2f}")
            y -= 22
        
        total_box_height = 35
        c.setFillColor(self.colors['total_bg'])
        c.roundRect(totals_x - totals_width, y - total_box_height, totals_width, total_box_height, 5, fill=1, stroke=0)
        
        c.setStrokeColor(self.colors['gold'])
        c.setLineWidth(2.5)
        c.roundRect(totals_x - totals_width, y - total_box_height, totals_width, total_box_height, 5, fill=0, stroke=1)
        
        c.setFillColor(self.colors['white'])
        c.setFont(self.arabic_font, 13)
        c.drawRightString(totals_x - 180, y - 22, self.reshape_arabic("الإجمالي النهائي:"))
        c.setFont(self.arabic_font, 15)
        c.drawRightString(totals_x - 15, y - 23, f"{invoice_data.get('total', 0):.2f} {invoice_data.get('currency', 'SAR')}")
        
        y -= total_box_height + 12
        
        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)
        amount_words = self.number_to_arabic_words(invoice_data.get('total', 0))
        c.drawRightString(totals_x - 10, y - 5, self.reshape_arabic(f"فقط: {amount_words}"))
        
        return y - 25
    
    def draw_footer(self, c, invoice_data, y):
        """رسم التذييل"""
        if invoice_data.get('notes'):
            notes_height = 40
            c.setStrokeColor(self.colors['border'])
            c.setFillColor(colors.HexColor('#FFFEF7'))
            c.setLineWidth(0.5)
            c.rect(40, y - notes_height, self.width - 80, notes_height, fill=1, stroke=1)
            
            c.setFillColor(self.colors['primary'])
            c.setFont(self.arabic_font, 9)
            c.drawRightString(self.width - 50, y - 15, self.reshape_arabic("ملاحظات:"))
            
            c.setFillColor(self.colors['text'])
            c.setFont(self.arabic_font, 8)
            c.drawRightString(self.width - 50, y - 30, self.reshape_arabic(invoice_data['notes'][:120]))
            
            y -= notes_height + 10
        
        signature_y = 90
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(0.5)
        
        sig_width = 120
        
        sig_x = self.width - 60
        c.line(sig_x - sig_width, signature_y + 20, sig_x, signature_y + 20)
        c.setFillColor(self.colors['light_text'])
        c.setFont(self.arabic_font, 8)
        c.drawCentredString(sig_x - sig_width/2, signature_y + 5, self.reshape_arabic("المخازن"))
        
        sig_x = self.width/2 + 60
        c.line(sig_x - sig_width, signature_y + 20, sig_x, signature_y + 20)
        c.drawCentredString(sig_x - sig_width/2, signature_y + 5, self.reshape_arabic("المستلم"))
        
        sig_x = 180
        c.line(sig_x - sig_width, signature_y + 20, sig_x, signature_y + 20)
        c.drawCentredString(sig_x - sig_width/2, signature_y + 5, self.reshape_arabic("المحاسب"))
        
        footer_height = 45
        c.setFillColor(self.colors['primary'])
        c.rect(0, 0, self.width, footer_height, fill=1, stroke=0)
        
        c.setFillColor(self.colors['gold'])
        c.rect(0, footer_height - 3, self.width, 3, fill=1, stroke=0)
        
        c.setFillColor(self.colors['white'])
        c.setFont(self.arabic_font, 10)
        c.drawCentredString(self.width / 2, 25, self.reshape_arabic("شكراً لتعاملكم معنا"))
        c.setFont(self.arabic_font, 8)
        c.drawCentredString(self.width / 2, 12, self.reshape_arabic("نسعد بخدمتكم دائماً • نحن في خدمتكم"))
    
    def generate(self, invoice_data, filename):
        """إنشاء الفاتورة"""
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            
            y = self.height - 30
            
            y = self.draw_header(c, invoice_data, y)
            y = self.draw_invoice_info_with_qr(c, invoice_data, y)
            y = self.draw_items_table(c, invoice_data, y)
            y = self.draw_totals(c, invoice_data, y)
            self.draw_footer(c, invoice_data, y)
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Error generating invoice: {e}")
            return False


class SimpleInvoiceTemplate(BaseInvoiceTemplate):
    """نموذج فاتورة بسيطة - بدون QR وتفاصيل أقل"""
    
    def __init__(self):
        super().__init__()
        self.template_name = "فاتورة بسيطة"
        # ألوان أفتح للفاتورة البسيطة
        self.colors['primary'] = colors.HexColor('#0277BD')
        self.colors['secondary'] = colors.HexColor('#0288D1')
        self.colors['table_header'] = colors.HexColor('#0288D1')
        self.colors['total_bg'] = colors.HexColor('#0277BD')
        self.colors['gold'] = colors.HexColor('#FF6F00')
    
    def draw_simple_header(self, c, invoice_data, y):
        """ترويسة بسيطة"""
        c.setFillColor(self.colors['primary'])
        c.rect(0, y - 5, self.width, 5, fill=1, stroke=0)

        y -= 20

        # الشعار في الوسط
        if invoice_data.get('logo_path') and os.path.exists(invoice_data['logo_path']):
            try:
                c.drawImage(invoice_data['logo_path'], self.width / 2 - 25, y - 40,
                           width=50, height=50, preserveAspectRatio=True, mask='auto')
            except:
                pass

        # معلومات الشركة على اليمين
        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 16)
        c.drawRightString(self.width - 50, y - 10, self.reshape_arabic(invoice_data.get('company_name', '')))

        c.setFont(self.arabic_font, 9)
        c.drawRightString(self.width - 50, y - 27, self.reshape_arabic(f"الرقم الضريبي: {invoice_data.get('tax_code', '')}"))

        # الاسم الإنجليزي على اليسار
        c.setFillColor(self.colors['text'])
        c.setFont('Helvetica', 12)
        c.drawString(50, y - 10, invoice_data.get('english_company_name', ''))
        
        # الرقم الضريبي بالإنجليزي تحت اسم الشركة
        c.setFont('Helvetica', 9)
        c.drawString(50, y - 27, f"VAT No.: {invoice_data.get('tax_code', '')}")

        return y - 75
    
    def draw_simple_info(self, c, invoice_data, y):
        """معلومات بسيطة بدون QR"""
        # عنوان الفاتورة في الوسط فوق جدول بيانات العميل
        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 14)
        c.drawCentredString(self.width / 2, y + 10, self.reshape_arabic(self.template_name))

        box_height = 80

        c.setStrokeColor(self.colors['border'])
        c.setFillColor(colors.HexColor('#F5F5F5'))
        c.setLineWidth(1)
        c.rect(40, y - box_height, self.width - 80, box_height, fill=1, stroke=1)

        # فاصل عمودي
        c.line(self.width / 2, y - 5, self.width / 2, y - box_height + 5)

        # معلومات الفاتورة (يمين)
        right_x = self.width - 50
        info_y = y - 20

        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)

        invoice_info = [
            f"رقم: {invoice_data['invoice_number']}",
            f"التاريخ: {invoice_data.get('date', '')}",
            f"النوع: {invoice_data.get('invoice_type', '')}"
        ]

        for info in invoice_info:
            c.drawRightString(right_x, info_y, self.reshape_arabic(info))
            info_y -= 16

        # معلومات العميل (يسار)
        left_x = self.width / 2 - 10
        info_y = y - 20

        customer_info = [
            f"العميل: {invoice_data.get('customer_name', '')}",
            f"الهاتف: {invoice_data.get('customer_phone', '-')}"
        ]

        for info in customer_info:
            c.drawRightString(left_x, info_y, self.reshape_arabic(info))
            info_y -= 16

        return y - box_height - 15
    
    def draw_simple_table(self, c, invoice_data, y):
        """جدول مبسط بدون ضريبة وخصم"""
        headers = ["م", "الصنف", "الكمية", "السعر", "الإجمالي"]
        headers_ar = [self.reshape_arabic(h) for h in headers]
        col_widths = [30, 280, 60, 80, 80]
        table_width = sum(col_widths)
        table_x = (self.width - table_width) / 2
        
        # رأس الجدول
        c.setFillColor(self.colors['table_header'])
        c.rect(table_x, y - 24, table_width, 24, fill=1, stroke=0)
        
        c.setFillColor(self.colors['white'])
        c.setFont(self.arabic_font, 10)
        
        x_pos = table_x + table_width
        for i, header in enumerate(headers_ar):
            text_x = x_pos - col_widths[i] / 2
            c.drawCentredString(text_x, y - 14, header)
            x_pos -= col_widths[i]
        
        y -= 24
        
        # الصفوف
        row_height = 22
        c.setFont(self.arabic_font, 9)
        
        for idx, item in enumerate(invoice_data['items'], 1):
            if y - row_height < 150:
                c.showPage()
                y = self.height - 50
            
            c.setFillColor(self.colors['table_row1'] if idx % 2 != 0 else self.colors['table_row2'])
            c.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=0)
            
            c.setStrokeColor(self.colors['border'])
            c.setLineWidth(0.3)
            c.rect(table_x, y - row_height, table_width, row_height, fill=0, stroke=1)
            
            c.setFillColor(self.colors['text'])
            
            item_values = [
                str(idx),
                self.reshape_arabic(item.get('description', '')),
                str(int(item.get('quantity', 0))),
                f"{item.get('price', 0):.2f}",
                f"{item.get('total', 0):.2f}"
            ]
            
            x_pos = table_x + table_width
            for i, value in enumerate(item_values):
                text_x = x_pos - col_widths[i] / 2
                if i == 1:
                    c.drawRightString(x_pos - 10, y - 13, str(value))
                else:
                    c.drawCentredString(text_x, y - 13, str(value))
                x_pos -= col_widths[i]
            
            y -= row_height
        
        return y - 10
    
    def draw_simple_totals(self, c, invoice_data, y):
        """مجاميع بسيطة"""
        totals_width = 250
        totals_x = self.width - 60
        
        c.setFont(self.arabic_font, 10)
        
        # الإجمالي فقط
        total_box_height = 30
        c.setFillColor(self.colors['total_bg'])
        c.rect(totals_x - totals_width, y - total_box_height, totals_width, total_box_height, fill=1, stroke=1)
        
        c.setFillColor(self.colors['white'])
        c.setFont(self.arabic_font, 12)
        c.drawRightString(totals_x - 130, y - 20, self.reshape_arabic("الإجمالي:"))
        c.setFont(self.arabic_font, 14)
        c.drawRightString(totals_x - 10, y - 20, f"{invoice_data.get('total', 0):.2f} {invoice_data.get('currency', 'SAR')}")
        
        return y - total_box_height - 15
    
    def draw_simple_footer(self, c):
        """تذييل بسيط"""
        c.setFillColor(self.colors['primary'])
        c.rect(0, 0, self.width, 30, fill=1, stroke=0)
        
        c.setFillColor(self.colors['white'])
        c.setFont(self.arabic_font, 9)
        c.drawCentredString(self.width / 2, 15, self.reshape_arabic("شكراً لزيارتكم"))
    
    def generate(self, invoice_data, filename):
        """إنشاء فاتورة بسيطة"""
        try:
            c = canvas.Canvas(filename, pagesize=A4)
            
            y = self.height - 30
            
            y = self.draw_simple_header(c, invoice_data, y)
            y = self.draw_simple_info(c, invoice_data, y)
            y = self.draw_simple_table(c, invoice_data, y)
            y = self.draw_simple_totals(c, invoice_data, y)
            self.draw_simple_footer(c)
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Error generating simple invoice: {e}")
            return False


class ProfessionalInvoiceTemplate(BaseInvoiceTemplate):
    """نموذج فاتورة ضريبية كاملة بتصميم احترافي مختلف"""

    def __init__(self):
        super().__init__()
        self.template_name = "فاتورة ضريبية كاملة"
        # ألوان احترافية مختلفة - أزرق داكن وفضي
        self.colors['primary'] = colors.HexColor('#0D47A1')      # أزرق داكن احترافي
        self.colors['secondary'] = colors.HexColor('#1976D2')    # أزرق متوسط
        self.colors['accent'] = colors.HexColor('#42A5F5')       # أزرق فاتح
        self.colors['gold'] = colors.HexColor('#B0BEC5')         # فضي
        self.colors['header_bg'] = colors.HexColor('#E3F2FD')    # أزرق فاتح جداً
        self.colors['table_header'] = colors.HexColor('#1976D2') # أزرق متوسط للجدول
        self.colors['table_row1'] = colors.white
        self.colors['table_row2'] = colors.HexColor('#F5F5F5')   # رمادي فاتح
        self.colors['border'] = colors.HexColor('#90CAF9')       # أزرق للحدود
        self.colors['text'] = colors.HexColor('#0D47A1')         # أزرق داكن للنص
        self.colors['light_text'] = colors.HexColor('#1565C0')   # أزرق متوسط للنص الخفيف
        self.colors['total_bg'] = colors.HexColor('#0D47A1')     # أزرق داكن للمجاميع
        self.colors['white'] = colors.white

    def draw_header(self, c, invoice_data, y):
        """ترويسة الفاتورة الاحترافية"""
        # خلفية متدرجة أزرق
        c.setFillColor(colors.HexColor('#E3F2FD'))
        c.rect(0, y - 130, self.width, 130, fill=1, stroke=0)

        # شريط علوي أزرق داكن
        c.setFillColor(self.colors['primary'])
        c.rect(0, y, self.width, 14, fill=1, stroke=0)

        # شريط مميز قصير
        c.setFillColor(self.colors['accent'])
        c.rect(0, y - 18, self.width, 4, fill=1, stroke=0)

        y -= 30

        # شعار صغير في الجهة اليسرى
        if invoice_data.get('logo_path') and os.path.exists(invoice_data['logo_path']):
            try:
                c.drawImage(invoice_data['logo_path'], self.width / 2 - 150, y - 40,
                           width=60, height=60, preserveAspectRatio=True, mask='auto')
            except:
                pass

        # معلومات الشركة على اليمين
        company_x_right = self.width - 60
        company_y = y - 10

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 20)
        c.drawRightString(company_x_right, company_y, self.reshape_arabic(invoice_data.get('company_name', '')))

        company_y -= 20
        c.setFont(self.arabic_font, 10)
        c.drawRightString(company_x_right, company_y, self.reshape_arabic(f"الرقم الضريبي: {invoice_data.get('tax_code', '')}"))

        # الاسم الإنجليزي على اليسار مع خط بسيط أسفله
        c.setFillColor(self.colors['text'])
        c.setFont('Helvetica', 12)
        c.drawString(60, y - 12, invoice_data.get('english_company_name', ''))
        
        c.setFont('Helvetica', 10)
        c.drawString(60, y - 30, f"VAT No.: {invoice_data.get('tax_code', '')}")

        # خط زخرفي أسفل الترويسة
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(1.5)
        c.line(50, y - 90, self.width - 50, y - 90)

        return y - 130

    def draw_invoice_info(self, c, invoice_data, y):
        """مربع معلومات الفاتورة الإحترافية"""
        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 18)
        c.drawCentredString(self.width / 2, y - 10, self.reshape_arabic(self.template_name))

        c.setFillColor(self.colors['light_text'])
        c.setFont('Helvetica', 10)
        c.drawCentredString(self.width / 2, y - 30, "Professional Tax Invoice")

        box_height = 120

        c.setStrokeColor(self.colors['border'])
        c.setFillColor(colors.white)
        c.rect(40, y - 50 - box_height, self.width - 80, box_height, fill=1, stroke=1)

        # تقسيم المربع إلى ثلاثة أعمدة
        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(1)
        c.line(self.width * 0.6, y - 55, self.width * 0.6, y - 50 - box_height + 5)
        c.line(self.width * 0.35, y - 55, self.width * 0.35, y - 50 - box_height + 5)

        # بيانات الفاتورة على اليمين
        right_x = self.width - 50
        info_y = y - 70

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 11)
        c.drawRightString(right_x, info_y, self.reshape_arabic("بيانات الفاتورة"))

        info_y -= 20
        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)

        invoice_info = [
            f"رقم الفاتورة: {invoice_data['invoice_number']}",
            f"التاريخ: {invoice_data.get('date', '')}",
            f"الوقت: {invoice_data.get('time', '')}",
            f"نوع الفاتورة: {invoice_data.get('invoice_type', '')}",
        ]

        for info in invoice_info:
            c.drawRightString(right_x, info_y, self.reshape_arabic(info))
            info_y -= 14

        # بيانات العميل في الوسط
        middle_x = self.width * 0.58
        middle_y = y - 70

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 11)
        c.drawRightString(middle_x, middle_y, self.reshape_arabic("بيانات العميل"))

        middle_y -= 20
        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)

        customer_info = [
            f"الاسم: {invoice_data.get('customer_name', '')}",
            f"الهاتف: {invoice_data.get('customer_phone', '')}",
            f"العنوان: {invoice_data.get('customer_address', '')}",
        ]

        for info in customer_info:
            c.drawRightString(middle_x, middle_y, self.reshape_arabic(info))
            middle_y -= 14

        # تفاصيل إضافية على اليسار
        left_x = self.width * 0.33
        left_y = y - 70

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 11)
        c.drawRightString(left_x, left_y, self.reshape_arabic("تفاصيل إضافية"))

        left_y -= 20
        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)

        additional_info = [
            f"الفرع: {invoice_data.get('branch', '-')}",
            f"المخزن: {invoice_data.get('warehouse', '-')}",
            f"مركز التكلفة: {invoice_data.get('cost_center', '-')}",
        ]

        for info in additional_info:
            c.drawRightString(left_x, left_y, self.reshape_arabic(info))
            left_y -= 14

        return y - 50 - box_height - 10

    def draw_items_table(self, c, invoice_data, y):
        """جدول الأصناف الاحترافي"""
        headers = [
            "م",
            "كود الصنف",
            "اسم الصنف",
            "الوحدة",
            "الكمية",
            "السعر",
            "الخصم",
            "الضريبة",
            "الإجمالي",
        ]
        headers_ar = [self.reshape_arabic(h) for h in headers]
        col_widths = [25, 60, 160, 40, 40, 55, 50, 55, 65]
        table_width = sum(col_widths)
        table_x = self.width - 50 - table_width

        # رأس الجدول
        c.setFillColor(self.colors['table_header'])
        c.rect(table_x, y - 28, table_width, 28, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setFont(self.arabic_font, 10)

        x_pos = table_x + table_width
        for i, header in enumerate(headers_ar):
            text_x = x_pos - col_widths[i] / 2
            c.drawCentredString(text_x, y - 16, header)
            x_pos -= col_widths[i]

        y -= 28

        # الصفوف
        row_height = 24
        c.setFont(self.arabic_font, 9)

        for idx, item in enumerate(invoice_data['items'], 1):
            if y - row_height < 220:
                c.showPage()
                c.setFont(self.arabic_font, 9)
                y = self.height - 60

            c.setFillColor(self.colors['table_row1'] if idx % 2 != 0 else self.colors['table_row2'])
            c.rect(table_x, y - row_height, table_width, row_height, fill=1, stroke=0)

            c.setStrokeColor(self.colors['border'])
            c.setLineWidth(0.4)
            c.rect(table_x, y - row_height, table_width, row_height, fill=0, stroke=1)

            c.setFillColor(self.colors['text'])

            item_values = [
                str(idx),
                item.get('item_code', ''),
                self.reshape_arabic(item.get('description', '')),
                self.reshape_arabic(item.get('unit', '')),
                str(int(item.get('quantity', 0))),
                f"{item.get('price', 0):.2f}",
                f"{item.get('discount_percent', 0):.0f}%",
                f"{item.get('tax_amount', 0):.2f}",
                f"{item.get('total', 0):.2f}",
            ]

            x_pos = table_x + table_width
            for i, value in enumerate(item_values):
                text_x = x_pos - col_widths[i] / 2
                if i in (2, 3):
                    c.drawRightString(x_pos - 10, y - 13, str(value))
                else:
                    c.drawCentredString(text_x, y - 13, str(value))
                x_pos -= col_widths[i]

            y -= row_height

        return y - 15

    def draw_totals(self, c, invoice_data, y):
        """مجاميع احترافية"""
        totals_width = 250
        totals_x = self.width - 60

        c.setFont(self.arabic_font, 10)

        totals = [
            ("إجمالي المشتريات", invoice_data.get('subtotal', 0), self.colors['text']),
            ("قيمة الخصم", invoice_data.get('discount', 0), colors.HexColor('#D84315')),
            ("قيمة الضريبة", invoice_data.get('tax', 0), colors.HexColor('#1B5E20')),
        ]

        for label, value, color in totals:
            c.setFillColor(self.colors['white'])
            c.rect(totals_x - totals_width, y - 22, totals_width, 22, fill=1, stroke=0)

            c.setStrokeColor(self.colors['border'])
            c.setLineWidth(0.5)
            c.line(totals_x - totals_width + 20, y - 2, totals_x - 10, y - 2)

            c.setFillColor(color)
            c.drawRightString(totals_x - 190, y - 13, self.reshape_arabic(label))
            c.drawRightString(totals_x - 15, y - 13, f"{value:.2f}")
            y -= 22

        final_height = 40
        c.setFillColor(self.colors['total_bg'])
        c.rect(totals_x - totals_width, y - final_height, totals_width, final_height, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setFont(self.arabic_font, 14)
        c.drawRightString(totals_x - 160, y - 25, self.reshape_arabic("الإجمالي المستحق"))
        c.setFont(self.arabic_font, 16)
        c.drawRightString(totals_x - 15, y - 26, f"{invoice_data.get('total', 0):.2f} {invoice_data.get('currency', 'SAR')}")

        y -= final_height + 12

        c.setFillColor(self.colors['text'])
        c.setFont(self.arabic_font, 9)
        amount_words = self.number_to_arabic_words(invoice_data.get('total', 0))
        c.drawRightString(totals_x - 10, y - 5, self.reshape_arabic(f"فقط: {amount_words}"))

        return y - 25

    def draw_footer(self, c, invoice_data, y):
        """التذييل الاحترافي"""
        if invoice_data.get('notes'):
            notes_height = 60
            c.setStrokeColor(self.colors['border'])
            c.setFillColor(colors.HexColor('#F8FBFF'))
            c.rect(40, y - notes_height, self.width - 80, notes_height, fill=1, stroke=1)

            c.setFillColor(self.colors['primary'])
            c.setFont(self.arabic_font, 9)
            c.drawRightString(self.width - 50, y - 15, self.reshape_arabic("ملاحظات:"))

            c.setFillColor(self.colors['text'])
            c.setFont(self.arabic_font, 8)
            c.drawRightString(self.width - 50, y - 35, self.reshape_arabic(invoice_data['notes'][:200]))

            y -= notes_height + 10

        c.setStrokeColor(self.colors['border'])
        c.setLineWidth(0.5)
        c.line(60, 110, self.width - 60, 110)

        c.setFillColor(self.colors['primary'])
        c.setFont(self.arabic_font, 10)
        c.drawCentredString(self.width / 2, 90, self.reshape_arabic("تفاصيل الاتصال"))

        contact_lines = [
            "هاتف: 9200 00000",
            "بريد إلكتروني: info@example.com",
            "العنوان: الرياض - المملكة العربية السعودية",
        ]

        c.setFont(self.arabic_font, 8)
        for idx, line in enumerate(contact_lines):
            c.drawCentredString(self.width / 2, 70 - idx * 12, self.reshape_arabic(line))

        footer_height = 40
        c.setFillColor(self.colors['primary'])
        c.rect(0, 0, self.width, footer_height, fill=1, stroke=0)

        c.setFillColor(self.colors['gold'])
        c.rect(0, footer_height - 3, self.width, 3, fill=1, stroke=0)

        c.setFillColor(self.colors['white'])
        c.setFont(self.arabic_font, 10)
        c.drawCentredString(self.width / 2, 22, self.reshape_arabic("نحن في خدمتكم دائماً"))
        c.setFont('Helvetica', 8)
        c.drawCentredString(self.width / 2, 10, "www.example.com")

    def generate(self, invoice_data, filename):
        """إنشاء الفاتورة الاحترافية"""
        try:
            c = canvas.Canvas(filename, pagesize=A4)

            y = self.height - 25

            y = self.draw_header(c, invoice_data, y)
            y = self.draw_invoice_info(c, invoice_data, y)
            y = self.draw_items_table(c, invoice_data, y)
            y = self.draw_totals(c, invoice_data, y)
            self.draw_footer(c, invoice_data, y)

            c.save()
            return True

        except Exception as e:
            print(f"Error generating professional invoice: {e}")
            return False

AVAILABLE_TEMPLATES = {
    'standard': {
        'name': 'فاتورة ضريبية مبسطة',
        'description': 'نموذج كامل مع QR Code وتفاصيل ضريبية كاملة',
        'class': StandardInvoiceTemplate
    },
    'simple': {
        'name': 'فاتورة بسيطة',
        'description': 'نموذج سريع بدون QR مع تفاصيل بسيطة',
        'class': SimpleInvoiceTemplate
    },
    'professional': {
        'name': 'فاتورة ضريبية كاملة',
        'description': 'نموذج احترافي بتصميم متطور ومعلومات إضافية',
        'class': ProfessionalInvoiceTemplate
    }
}