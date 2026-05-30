#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
وحدة التحقق من صحة المدخلات
"""

from datetime import datetime

class InvoiceValidator:
    """فئة للتحقق من صحة بيانات الفاتورة"""
    
    def __init__(self):
        self.validation_errors = {}
        self.required_fields = {
            'company_name': 'اسم الشركة',
            'tax_code': 'الرقم الضريبي',
            'customer_name': 'اسم العميل',
            'invoice_number': 'رقم الفاتورة',
            'date': 'التاريخ',
            'tax_rate': 'نسبة الضريبة'
        }
    
    def validate_all_fields(self, app):
        """التحقق من صحة جميع الحقول المطلوبة"""
        errors = []
        
        # التحقق من الحقول المطلوبة
        for field_key, field_name in self.required_fields.items():
            try:
                # قراءة القيمة مباشرة من Entry widget بدلاً من StringVar
                entry_widget = getattr(app, f"{field_key}_entry")
                value = entry_widget.get().strip()
            except AttributeError as e:
                print(f"ERROR: Cannot find {field_key}_entry - {e}")
                errors.append(f"خطأ داخلي: لا يمكن العثور على حقل {field_name}")
                continue
                
            if not value:
                errors.append(f"يرجى إدخال {field_name}")
                self.set_field_error(app, field_key, True)
            else:
                self.set_field_error(app, field_key, False)
        
        # التحقق من صحة التاريخ
        if app.date_var.get().strip():
            try:
                datetime.strptime(app.date_var.get(), '%d/%m/%Y')
                self.set_field_error(app, 'date', False)
            except ValueError:
                errors.append("يرجى إدخال تاريخ صحيح بالصيغة dd/mm/yyyy")
                self.set_field_error(app, 'date', True)
        
        # التحقق من صحة نسبة الضريبة
        if app.tax_rate_var.get().strip():
            try:
                tax_rate = float(app.tax_rate_var.get())
                if tax_rate < 0 or tax_rate > 100:
                    errors.append("نسبة الضريبة يجب أن تكون بين 0 و 100")
                    self.set_field_error(app, 'tax_rate', True)
                else:
                    self.set_field_error(app, 'tax_rate', False)
            except ValueError:
                errors.append("يرجى إدخال نسبة ضريبة صحيحة")
                self.set_field_error(app, 'tax_rate', True)
        
        # التحقق من وجود أصناف
        if not app.items:
            errors.append("يرجى إضافة أصناف للفاتورة")
        
        return errors
    
    def validate_field(self, app, field_key):
        """التحقق من صحة حقل معين"""
        try:
            entry_widget = getattr(app, f"{field_key}_entry")
            value = entry_widget.get().strip()
        except AttributeError:
            return True  # إذا لم يوجد الحقل، نعتبره صحيحاً
        
        if field_key in self.required_fields and not value:
            self.set_field_error(app, field_key, True)
            return False
        elif field_key == 'date' and value:
            try:
                datetime.strptime(value, '%d/%m/%Y')
                self.set_field_error(app, field_key, False)
                return True
            except ValueError:
                self.set_field_error(app, field_key, True)
                return False
        elif field_key == 'tax_rate' and value:
            try:
                tax_rate = float(value)
                if tax_rate < 0 or tax_rate > 100:
                    self.set_field_error(app, field_key, True)
                    return False
                else:
                    self.set_field_error(app, field_key, False)
                    return True
            except ValueError:
                self.set_field_error(app, field_key, True)
                return False
        else:
            self.set_field_error(app, field_key, False)
            return True
    
    def set_field_error(self, app, field_key, has_error):
        """تعيين حالة الخطأ لحقل معين"""
        entry_widget = getattr(app, f"{field_key}_entry")
        
        if has_error:
            entry_widget.configure(style='Error.TEntry')
            self.validation_errors[field_key] = True
        else:
            entry_widget.configure(style='TEntry')
            if field_key in self.validation_errors:
                del self.validation_errors[field_key]
