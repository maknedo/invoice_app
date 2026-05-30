#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة إدارة إعدادات الفاتورة
"""

import json
import os

class InvoiceSettings:
    """فئة لإدارة حفظ وتحميل الإعدادات"""
    
    def __init__(self, settings_file="settings.json"):
        self.settings_file = settings_file
        self.last_settings = None
    
    def save(self, app):
        """حفظ الإعدادات الحالية - القراءة من Entry مباشرة"""
        settings = {
            'company_name': app.company_name_entry.get(),
            'english_company_name': app.english_company_name_entry.get(),
            'tax_code': app.tax_code_entry.get(),
            'company_address': app.company_address_entry.get(),  # عنوان الشركة
            'logo_path': app.logo_path,
            'invoice_type': app.invoice_type_var.get(),  # Combobox
            'currency': app.currency_entry.get(),
            'warehouse': app.warehouse_entry.get(),
            'cost_center': app.cost_center_entry.get(),
            'tax_rate': app.tax_rate_entry.get(),
            'item_unit': app.item_unit_entry.get(),
            'customer_name': app.customer_name_entry.get(),
            'customer_phone': app.customer_phone_entry.get(),
            'customer_tax_number': app.customer_tax_number_entry.get(),
            'customer_address': app.customer_address_entry.get(),
            'notes': app.notes_text.get('1.0', 'end-1c'),
            'template': app.template_var.get(),
            # حفظ رقم الفاتورة والتاريخ والوقت
            'invoice_number': app.invoice_number_entry.get(),
            'date': app.date_entry.get(),
            'time': app.time_entry.get(),
            # حفظ الألوان المخصصة
            'template_colors': app.template_colors,
            # حفظ الخط المختار
            'selected_font': app.selected_font,
            'notes_alignment': app.notes_alignment_var.get() if hasattr(app, 'notes_alignment_var') else 'right',
        }
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.last_settings = settings
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load(self, app):
        """تحميل الإعدادات المحفوظة"""
        if not os.path.exists(self.settings_file):
            return False
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            self.last_settings = settings
            
            # استعادة إعدادات الشركة - نستخدم Entry.insert() بدلاً من StringVar.set()
            if 'company_name' in settings:
                app.company_name_entry.delete(0, 'end')
                app.company_name_entry.insert(0, settings['company_name'])
            if 'english_company_name' in settings:
                app.english_company_name_entry.delete(0, 'end')
                app.english_company_name_entry.insert(0, settings['english_company_name'])
            if 'tax_code' in settings:
                app.tax_code_entry.delete(0, 'end')
                app.tax_code_entry.insert(0, settings['tax_code'])
            if 'company_address' in settings:
                app.company_address_entry.delete(0, 'end')
                app.company_address_entry.insert(0, settings['company_address'])
            if 'logo_path' in settings and settings['logo_path']:
                app.logo_path = settings['logo_path']
                if os.path.exists(app.logo_path):
                    app.logo_label.config(text=os.path.basename(app.logo_path), foreground='#2ecc71',
                                         font=('Segoe UI', 9, 'bold'))
            
            # استعادة الإعدادات الافتراضية
            if 'invoice_type' in settings:
                app.invoice_type_var.set(settings['invoice_type'])  # Combobox يعمل مع StringVar
            if 'currency' in settings:
                app.currency_entry.delete(0, 'end')
                app.currency_entry.insert(0, settings['currency'])
            if 'warehouse' in settings:
                app.warehouse_entry.delete(0, 'end')
                app.warehouse_entry.insert(0, settings['warehouse'])
            if 'cost_center' in settings:
                app.cost_center_entry.delete(0, 'end')
                app.cost_center_entry.insert(0, settings['cost_center'])
            if 'tax_rate' in settings:
                app.tax_rate_entry.delete(0, 'end')
                app.tax_rate_entry.insert(0, settings['tax_rate'])
            if 'item_unit' in settings:
                app.item_unit_entry.delete(0, 'end')
                app.item_unit_entry.insert(0, settings['item_unit'])
            
            # استعادة معلومات العميل
            if 'customer_name' in settings:
                app.customer_name_entry.delete(0, 'end')
                app.customer_name_entry.insert(0, settings['customer_name'])
            if 'customer_phone' in settings:
                app.customer_phone_entry.delete(0, 'end')
                app.customer_phone_entry.insert(0, settings['customer_phone'])
            if 'customer_tax_number' in settings:
                app.customer_tax_number_entry.delete(0, 'end')
                app.customer_tax_number_entry.insert(0, settings['customer_tax_number'])
            if 'customer_address' in settings:
                app.customer_address_entry.delete(0, 'end')
                app.customer_address_entry.insert(0, settings['customer_address'])
            
            # استعادة الملاحظات
            if 'notes' in settings:
                app.notes_text.delete('1.0', 'end')
                app.notes_text.insert('1.0', settings['notes'])
            
            if 'notes_alignment' in settings and hasattr(app, 'notes_alignment_var'):
                app.notes_alignment_var.set(settings['notes_alignment'])
                if hasattr(app, '_apply_notes_alignment'):
                    app._apply_notes_alignment()
            
            # استعادة اختيار النموذج
            if 'template' in settings:
                app.select_template(settings['template'])
            
            # استعادة رقم الفاتورة والتاريخ والوقت
            if 'invoice_number' in settings:
                app.invoice_number_entry.delete(0, 'end')
                app.invoice_number_entry.insert(0, settings['invoice_number'])
            if 'date' in settings:
                app.date_entry.delete(0, 'end')
                app.date_entry.insert(0, settings['date'])
            if 'time' in settings:
                app.time_entry.delete(0, 'end')
                app.time_entry.insert(0, settings['time'])
            
            # استعادة الألوان المخصصة
            if 'template_colors' in settings:
                app.template_colors = settings['template_colors']
            
            # استعادة الخط المختار
            if 'selected_font' in settings:
                app.selected_font = settings['selected_font']
                if hasattr(app, 'font_var'):
                    app.font_var.set(settings['selected_font'])
            
            # حفظ نسخة للاستخدام اللاحق داخل التطبيق
            if hasattr(app, 'last_loaded_settings'):
                app.last_loaded_settings.update(settings)
            else:
                app.last_loaded_settings = dict(settings)
            
            return True
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
