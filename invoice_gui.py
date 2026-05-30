#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة إنشاء الفواتير - الواجهة الرئيسية للتطبيق
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from invoice_templates import AVAILABLE_TEMPLATES
import os

# استيراد الوحدات المنفصلة
from ui_components import AnimatedButton
from invoice_validation import InvoiceValidator
from invoice_calculator import InvoiceCalculator
from invoice_settings import InvoiceSettings

DEFAULT_TEMPLATE_COLORS = {
    'standard': {
        'primary': '#1B5E20',      # اللون الأساسي
        'secondary': '#2E7D32',    # اللون الثانوي
        'accent': '#4CAF50',       # لون التمييز
        'gold': '#FFB300',         # اللون الذهبي
        'header_bg': '#F1F8E9',    # خلفية الرأس
        'border': '#A5D6A7',       # لون الحدود
        'text': '#1B5E20',         # لون النص
        'light_text': '#558B2F'    # لون النص الفاتح
    },
    'simple': {
        'primary': '#0277BD',
        'secondary': '#0288D1',
        'accent': '#03A9F4',
        'gold': '#FF6F00',
        'header_bg': '#E1F5FE',
        'border': '#B3E5FC',
        'text': '#01579B',
        'light_text': '#039BE5'
    },
    'professional': {
        'primary': '#455A64',
        'secondary': '#607D8B',
        'accent': '#90A4AE',
        'gold': '#8D6E63',
        'header_bg': '#FAFAFA',
        'border': '#B0BEC5',
        'text': '#263238',
        'light_text': '#455A64'
    },
    'rawayih': {
        'primary': '#8B6F47',
        'secondary': '#A0826D',
        'accent': '#D4C5B9',
        'gold': '#C19A6B',
        'header_bg': '#F5F0E8',
        'border': '#8B6F47',
        'text': '#3E2723',
        'light_text': '#5D4037'
    }
}

class InvoiceApp:
    """تطبيق إنشاء الفواتير"""

    def __init__(self, root):
        self.root = root
        self.root.title("إنشاء فاتورة جديدة - نظام الفواتير")

        # Set window to fullscreen (maximized)
        self.root.state('zoomed')
        self.root.minsize(1100, 800)

        # المتغيرات الأساسية
        self.items = []
        self.item_counter = 0
        self.next_item_code = None
        self.logo_path = ""
        self.selected_template = 'standard'
        self.selected_font = 'Arial'  # الخط الافتراضي
        self._settings_save_job = None

        # ألوان مخصصة للنماذج - نسخة قابلة للتعديل من القيم الافتراضية
        self.template_colors = {template: colors.copy() for template, colors in DEFAULT_TEMPLATE_COLORS.items()}

        # إنشاء الوحدات المساعدة
        self.validator = InvoiceValidator()
        self.calculator = InvoiceCalculator()
        self.settings_manager = InvoiceSettings()
        self.last_loaded_settings = {}

        # إنشاء الواجهة
        self.create_widgets()
        self.settings_manager.load(self)
        self._restore_invoice_info_from_settings()

        # تهيئة المجاميع برسالة ترحيب
        self.root.after(50, self._initialize_totals)
        # تحديث المجاميع عند البدء
        self.root.after(150, self.calculate_totals)

        # حفظ الإعدادات عند الإغلاق
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_context_menu(self, widget):
        """إنشاء قائمة سياق للنسخ واللصق"""
        context_menu = tk.Menu(widget, tearoff=0)
        context_menu.add_command(label="نسخ (Ctrl+C)", command=lambda: widget.event_generate("<<Copy>>"))
        context_menu.add_command(label="لصق (Ctrl+V)", command=lambda: widget.event_generate("<<Paste>>"))
        context_menu.add_separator()
        context_menu.add_command(label="قص (Ctrl+X)", command=lambda: widget.event_generate("<<Cut>>"))
        context_menu.add_command(label="تحديد الكل (Ctrl+A)", command=lambda: widget.select_range(0, tk.END))

        def show_context_menu(event):
            context_menu.post(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_context_menu)  # كليك يمين
        return context_menu

    def create_widgets(self):
        """إنشاء جميع عناصر الواجهة"""
        # نظام الألوان الحديث
        BG_COLOR = '#f5f7fa'
        CARD_BG = '#ffffff'
        TEXT_COLOR = '#2c3e50'
        PRIMARY_COLOR = '#3498db'
        ACCENT_COLOR = '#2ecc71'
        HEADER_GRADIENT_START = '#667eea'
        HEADER_GRADIENT_END = '#764ba2'
        
        # حفظ الألوان للاستخدام في الدوال الأخرى
        self.BG_COLOR = BG_COLOR
        self.CARD_BG = CARD_BG
        self.TEXT_COLOR = TEXT_COLOR
        self.PRIMARY_COLOR = PRIMARY_COLOR

        # إعداد الأنماط
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background=BG_COLOR)
        style.configure('Card.TFrame', background=CARD_BG, relief='flat')
        style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        style.configure('CardLabel.TLabel', background=CARD_BG, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=CARD_BG, foreground=PRIMARY_COLOR, font=('Segoe UI', 11, 'bold'))
        style.configure('TEntry', fieldbackground='white', font=('Segoe UI', 10), borderwidth=1, relief='solid')
        style.configure('Error.TEntry', fieldbackground='#ffebee', font=('Segoe UI', 10), borderwidth=2, relief='solid')
        style.configure('TCombobox', fieldbackground='white', font=('Segoe UI', 10))
        style.configure('Card.TLabelframe', background=CARD_BG, borderwidth=0, relief='flat')
        style.configure('Card.TLabelframe.Label', background=CARD_BG, foreground=PRIMARY_COLOR, 
                       font=('Segoe UI', 12, 'bold'))
        style.configure("Modern.Treeview.Heading", font=('Segoe UI', 10, 'bold'), 
                       background=PRIMARY_COLOR, foreground='white')
        style.configure("Modern.Treeview", rowheight=35, font=('Segoe UI', 10), 
                       fieldbackground='white', background='white')
        style.map("Modern.Treeview", background=[('selected', '#e3f2fd')])

        # إنشاء Canvas مع Scrollbar
        canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self.canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=BG_COLOR)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_canvas_configure(event):
            canvas.itemconfig(self.canvas_window, width=event.width)

        canvas.bind('<Configure>', on_canvas_configure)

        # تفعيل التمرير بالعجلة
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        main_frame = scrollable_frame

        # الرأس
        self._create_header(main_frame, HEADER_GRADIENT_START)
        
        # بطاقة معلومات الشركة
        self._create_company_section(main_frame)
        
        # بطاقة اختيار النموذج
        self._create_template_section(main_frame)
        
        # بطاقة معلومات الفاتورة
        self._create_invoice_info_section(main_frame)
        
        # بطاقة معلومات العميل
        self._create_customer_section(main_frame)
        
        # بطاقة الأصناف
        self._create_items_section(main_frame)
        
        # بطاقة المجاميع
        self._create_totals_section(main_frame)
        
        # بطاقة الملاحظات
        self._create_notes_section(main_frame)
        
        # أزرار الإجراءات
        self._create_action_buttons(main_frame)

    def _create_header(self, parent, bg_color):
        """إنشاء رأس الصفحة"""
        header_frame = tk.Frame(parent, bg=bg_color, height=100)
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(header_frame, text="📄 إنشاء فاتورة ضريبية مبسطة",
                               font=('Segoe UI', 22, 'bold'), foreground='white', bg=bg_color)
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(header_frame, text="نظام متكامل لإدارة الفواتير الإلكترونية",
                                 font=('Segoe UI', 11), foreground='#ecf0f1', bg=bg_color)
        subtitle_label.pack(pady=(0, 15))

    def _create_company_section(self, parent):
        """إنشاء قسم معلومات الشركة"""
        company_card = self.create_card(parent, "🏢 معلومات الشركة")
        company_frame = company_card['content']
        for i in range(5):
            company_frame.columnconfigure(i, weight=1)

        ttk.Label(company_frame, text="اسم الشركة:", style='CardLabel.TLabel').grid(row=0, column=4, sticky='w', padx=5, pady=8)
        self.company_name_var = tk.StringVar(value="اسمان التجاريه")
        self.company_name_entry = ttk.Entry(company_frame, textvariable=self.company_name_var, width=30, font=('Segoe UI', 10))
        self.company_name_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=8)
        self.company_name_entry.bind('<KeyRelease>', lambda e: self.validator.validate_field(self, 'company_name'))
        self.create_context_menu(self.company_name_entry)

        ttk.Label(company_frame, text="اسم الشركة بالإنجليزية:", style='CardLabel.TLabel').grid(row=1, column=4, sticky='w', padx=5, pady=8)
        self.english_company_name_var = tk.StringVar(value="Esman Altgareah")
        self.english_company_name_entry = ttk.Entry(company_frame, textvariable=self.english_company_name_var, width=30, font=('Segoe UI', 10))
        self.english_company_name_entry.grid(row=1, column=3, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.english_company_name_entry)

        ttk.Label(company_frame, text="الرقم الضريبي:", style='CardLabel.TLabel').grid(row=0, column=2, sticky='w', padx=5, pady=8)
        self.tax_code_var = tk.StringVar(value="310480120300003")
        self.tax_code_entry = ttk.Entry(company_frame, textvariable=self.tax_code_var, width=30, font=('Segoe UI', 10))
        self.tax_code_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=8)
        self.tax_code_entry.bind('<KeyRelease>', lambda e: self.validator.validate_field(self, 'tax_code'))
        self.create_context_menu(self.tax_code_entry)

        # إضافة عنوان الشركة
        ttk.Label(company_frame, text="عنوان الشركة:", style='CardLabel.TLabel').grid(row=1, column=2, sticky='w', padx=5, pady=8)
        self.company_address_var = tk.StringVar(value="المملكة العربية السعودية")
        self.company_address_entry = ttk.Entry(company_frame, textvariable=self.company_address_var, width=30, font=('Segoe UI', 10))
        self.company_address_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.company_address_entry)

        ttk.Label(company_frame, text="شعار الشركة:", style='CardLabel.TLabel').grid(row=2, column=4, sticky='w', padx=5, pady=8)
        logo_frame = tk.Frame(company_frame, bg=self.CARD_BG)
        logo_frame.grid(row=2, column=1, columnspan=3, sticky='ew', padx=5, pady=8)
        self.logo_label = tk.Label(logo_frame, text="لم يتم اختيار شعار", foreground='#95a5a6', 
                                   bg=self.CARD_BG, font=('Segoe UI', 9, 'italic'))
        self.logo_label.pack(side='right', padx=5)
        
        AnimatedButton(logo_frame, "🗑️ مسح", self.clear_logo, 
                      bg_color='#e74c3c', hover_color='#c0392b', width=100, height=35).pack(side='left', padx=3)
        AnimatedButton(logo_frame, "📁 اختر الشعار", self.select_logo, 
                      bg_color='#3498db', hover_color='#2980b9', width=120, height=35).pack(side='left', padx=3)

    def _create_template_section(self, parent):
        """إنشاء قسم اختيار النموذج"""
        template_card = self.create_card(parent, "📋 نموذج الفاتورة")
        template_frame = template_card['content']

        # قسم اختيار الخط
        font_section = tk.Frame(template_frame, bg=self.CARD_BG)
        font_section.pack(fill='x', pady=10, padx=20)
        
        tk.Label(
            font_section,
            text="اختر الخط:",
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR,
            font=('Segoe UI', 11, 'bold')
        ).pack(side='right', padx=10)
        
        # قائمة الخطوط العربية المتوفرة في Windows
        arabic_fonts = [
            'Arial',           # خط عربي واضح ومقروء
            'Tahoma',          # خط Microsoft العربي الكلاسيكي
            'Simplified Arabic',  # خط عربي مبسط وجميل
            'Traditional Arabic'  # خط عربي تقليدي أنيق
        ]
        
        self.font_var = tk.StringVar(value='Arial')
        self.custom_font_path = None  # مسار الخط المخصص
        
        font_combo = ttk.Combobox(
            font_section,
            textvariable=self.font_var,
            values=arabic_fonts,
            width=25,
            state='readonly',
            font=('Segoe UI', 10)
        )
        font_combo.pack(side='right', padx=10)
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.on_font_change())
        
        # زر لاختيار خط مخصص
        AnimatedButton(
            font_section,
            "📁 خط مخصص",
            self.select_custom_font,
            bg_color='#9b59b6',
            hover_color='#8e44ad',
            width=120,
            height=35
        ).pack(side='right', padx=10)

        self.template_var = tk.StringVar(value='standard')
        
        # أسماء مختصرة للنماذج
        template_names = {
            'standard': 'نموذج 1',
            'simple': 'نموذج 2',
            'professional': 'نموذج 3',
            'rawayih': ' نموذج 4'
        }
        
        # إنشاء أزرار أنيقة للنماذج
        buttons_container = tk.Frame(template_frame, bg=self.CARD_BG)
        buttons_container.pack(fill='x', pady=10, padx=20)
        
        for template_id, template_info in AVAILABLE_TEMPLATES.items():
            # إنشاء حاوية لكل نموذج (زر + زر إعدادات)
            template_container = tk.Frame(buttons_container, bg=self.CARD_BG)
            template_container.pack(side='right', padx=10, expand=True, fill='x')
            
            # إنشاء زر مخصص لكل نموذج
            btn_frame = tk.Frame(template_container, bg=self.CARD_BG)
            btn_frame.pack(fill='x')
            
            # تحديد الألوان حسب النموذج
            if template_id == 'standard':
                btn_color = '#3498db'
                hover_color = '#2980b9'
            elif template_id == 'simple':
                btn_color = '#2ecc71'
                hover_color = '#27ae60'
            elif template_id == 'rawayih':
                btn_color = '#8B6F47'
                hover_color = '#A0826D'
            else:  # professional
                btn_color = '#9b59b6'
                hover_color = '#8e44ad'
            
            # إنشاء زر مخصص بدلاً من Radiobutton
            def create_select_command(tid):
                return lambda: self.select_template(tid)
            
            AnimatedButton(
                btn_frame,
                template_names[template_id],
                create_select_command(template_id),
                bg_color=btn_color,
                hover_color=hover_color,
                width=180,
                height=45
            ).pack(expand=True, fill='x')
            
            # زر إعدادات الألوان
            settings_btn_frame = tk.Frame(template_container, bg=self.CARD_BG)
            settings_btn_frame.pack(fill='x', pady=(5, 0))
            
            def create_settings_command(tid):
                return lambda: self.open_template_color_settings(tid)
            
            AnimatedButton(
                settings_btn_frame,
                "⚙️ إعدادات الألوان",
                create_settings_command(template_id),
                bg_color='#95a5a6',
                hover_color='#7f8c8d',
                width=180,
                height=35
            ).pack(expand=True, fill='x')
        
        # عرض النموذج المختار
        self.selected_template_label = tk.Label(
            template_frame,
            text=f"المختار: {template_names['standard']}",
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR,
            font=('Segoe UI', 10, 'bold')
        )
        self.selected_template_label.pack(pady=10)

    def _create_invoice_info_section(self, parent):
        """إنشاء قسم معلومات الفاتورة"""
        invoice_card = self.create_card(parent, "📝 معلومات الفاتورة")
        invoice_info_frame = invoice_card['content']
        for i in range(5):
            invoice_info_frame.columnconfigure(i, weight=1)

        ttk.Label(invoice_info_frame, text="رقم الفاتورة:", style='CardLabel.TLabel').grid(row=0, column=4, sticky='w', padx=5, pady=8)
        self.invoice_number_var = tk.StringVar()
        self.invoice_number_entry = ttk.Entry(invoice_info_frame, textvariable=self.invoice_number_var, width=25, font=('Segoe UI', 10))
        self.invoice_number_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=8)
        self.invoice_number_entry.bind('<KeyRelease>', lambda e: self._handle_field_change('invoice_number', self.validator.validate_field))
        self.create_context_menu(self.invoice_number_entry)

        ttk.Label(invoice_info_frame, text="نوع الفاتورة:", style='CardLabel.TLabel').grid(row=0, column=2, sticky='w', padx=5, pady=8)
        self.invoice_type_var = tk.StringVar(value="نقداً")
        invoice_type_combo = ttk.Combobox(invoice_info_frame, textvariable=self.invoice_type_var,
                                          values=["نقداً", "آجل", "شيك"], width=22, state='readonly', font=('Segoe UI', 10))
        invoice_type_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=8)
        def on_invoice_type_change(event=None):
            self._save_settings_immediately()

        def on_combo_change(event=None):
            selected_value = invoice_type_combo.get()
            self.invoice_type_var.set(selected_value)
            self._save_settings_immediately()

        invoice_type_combo.bind('<<ComboboxSelected>>', on_combo_change)

        ttk.Label(invoice_info_frame, text="التاريخ:", style='CardLabel.TLabel').grid(row=1, column=4, sticky='w', padx=5, pady=8)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(invoice_info_frame, textvariable=self.date_var, width=25, font=('Segoe UI', 10))
        self.date_entry.grid(row=1, column=3, sticky='ew', padx=5, pady=8)
        self.date_entry.bind('<KeyRelease>', lambda e: self._handle_field_change('date', self.validator.validate_field))
        self.create_context_menu(self.date_entry)

        ttk.Label(invoice_info_frame, text="الوقت:", style='CardLabel.TLabel').grid(row=1, column=2, sticky='w', padx=5, pady=8)
        self.time_var = tk.StringVar()
        self.time_entry = ttk.Entry(invoice_info_frame, textvariable=self.time_var, width=22, font=('Segoe UI', 10))
        self.time_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=8)
        self.time_entry.bind('<KeyRelease>', lambda e: self._handle_field_change('time', self.validator.validate_field))
        self.create_context_menu(self.time_entry)

        ttk.Label(invoice_info_frame, text="العملة:", style='CardLabel.TLabel').grid(row=2, column=4, sticky='w', padx=5, pady=8)
        self.currency_var = tk.StringVar(value="SAR")
        self.currency_entry = ttk.Entry(invoice_info_frame, textvariable=self.currency_var, width=25, font=('Segoe UI', 10))
        self.currency_entry.grid(row=2, column=3, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.currency_entry)

        ttk.Label(invoice_info_frame, text="المخزن:", style='CardLabel.TLabel').grid(row=2, column=2, sticky='w', padx=5, pady=8)
        self.warehouse_var = tk.StringVar(value="المخزن الرئيسي")
        self.warehouse_entry = ttk.Entry(invoice_info_frame, textvariable=self.warehouse_var, width=22, font=('Segoe UI', 10))
        self.warehouse_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.warehouse_entry)

        ttk.Label(invoice_info_frame, text="مركز التكلفة:", style='CardLabel.TLabel').grid(row=3, column=4, sticky='w', padx=5, pady=8)
        self.cost_center_var = tk.StringVar()
        self.cost_center_entry = ttk.Entry(invoice_info_frame, textvariable=self.cost_center_var, width=25, font=('Segoe UI', 10))
        self.cost_center_entry.grid(row=3, column=3, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.cost_center_entry)

    def _create_customer_section(self, parent):
        """إنشاء قسم معلومات العميل"""
        customer_card = self.create_card(parent, "👤 معلومات العميل")
        customer_frame = customer_card['content']
        for i in range(5):
            customer_frame.columnconfigure(i, weight=1)

        ttk.Label(customer_frame, text="اسم العميل:", style='CardLabel.TLabel').grid(row=0, column=4, sticky='w', padx=5, pady=8)
        self.customer_name_var = tk.StringVar()
        self.customer_name_entry = ttk.Entry(customer_frame, textvariable=self.customer_name_var, width=30, font=('Segoe UI', 10))
        self.customer_name_entry.grid(row=0, column=3, sticky='ew', padx=5, pady=8)
        self.customer_name_entry.bind('<KeyRelease>', lambda e: self.validator.validate_field(self, 'customer_name'))
        self.create_context_menu(self.customer_name_entry)

        ttk.Label(customer_frame, text="رقم الهاتف:", style='CardLabel.TLabel').grid(row=0, column=2, sticky='w', padx=5, pady=8)
        self.customer_phone_var = tk.StringVar()
        self.customer_phone_entry = ttk.Entry(customer_frame, textvariable=self.customer_phone_var, width=25, font=('Segoe UI', 10))
        self.customer_phone_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.customer_phone_entry)

        ttk.Label(customer_frame, text="الرقم الضريبي:", style='CardLabel.TLabel').grid(row=1, column=4, sticky='w', padx=5, pady=8)
        self.customer_tax_number_var = tk.StringVar()
        self.customer_tax_number_entry = ttk.Entry(customer_frame, textvariable=self.customer_tax_number_var, width=30, font=('Segoe UI', 10))
        self.customer_tax_number_entry.grid(row=1, column=3, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.customer_tax_number_entry)

        ttk.Label(customer_frame, text="العنوان:", style='CardLabel.TLabel').grid(row=1, column=2, sticky='w', padx=5, pady=8)
        self.customer_address_var = tk.StringVar()
        self.customer_address_entry = ttk.Entry(customer_frame, textvariable=self.customer_address_var, width=25, font=('Segoe UI', 10))
        self.customer_address_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=8)
        self.create_context_menu(self.customer_address_entry)

    def _create_items_section(self, parent):
        """إنشاء قسم الأصناف"""
        items_card = self.create_card(parent, "🛒 الأصناف")
        items_frame = items_card['content']

        # قسم إضافة الأصناف
        add_item_frame = tk.Frame(items_frame, bg=self.CARD_BG)
        add_item_frame.pack(fill='x', pady=10, padx=5)

        # الصف الأول
        row1 = tk.Frame(add_item_frame, bg=self.CARD_BG)
        row1.pack(fill='x', pady=5)

        tk.Label(row1, text="رقم الصنف:", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=('Segoe UI', 9)).pack(side='right', padx=5)
        self.item_code_var = tk.StringVar(value="1")
        self.item_code_entry = ttk.Entry(row1, textvariable=self.item_code_var, width=15, font=('Segoe UI', 10))
        self.item_code_entry.pack(side='right', padx=5)
        self.create_context_menu(self.item_code_entry)
        self._initialize_next_item_code()

        tk.Label(row1, text="اسم الصنف:", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=('Segoe UI', 9)).pack(side='right', padx=5)
        self.item_desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(row1, textvariable=self.item_desc_var, width=30, font=('Segoe UI', 10))
        self.desc_entry.pack(side='right', padx=5)
        self.create_context_menu(self.desc_entry)

        tk.Label(row1, text="الوحدة:", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=('Segoe UI', 9)).pack(side='right', padx=5)
        self.item_unit_var = tk.StringVar(value="حبة")
        self.item_unit_entry = ttk.Entry(row1, textvariable=self.item_unit_var, width=10, font=('Segoe UI', 10))
        self.item_unit_entry.pack(side='right', padx=5)
        self.create_context_menu(self.item_unit_entry)

        # الصف الثاني
        row2 = tk.Frame(add_item_frame, bg=self.CARD_BG)
        row2.pack(fill='x', pady=5)

        tk.Label(row2, text="الكمية:", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=('Segoe UI', 9)).pack(side='right', padx=5)
        self.item_qty_var = tk.StringVar(value="1")
        self.item_qty_entry = ttk.Entry(row2, textvariable=self.item_qty_var, width=10, font=('Segoe UI', 10))
        self.item_qty_entry.pack(side='right', padx=5)
        self.create_context_menu(self.item_qty_entry)

        tk.Label(row2, text="السعر:", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=('Segoe UI', 9)).pack(side='right', padx=5)
        self.item_price_var = tk.StringVar(value="0")
        self.item_price_entry = ttk.Entry(row2, textvariable=self.item_price_var, width=10, font=('Segoe UI', 10))
        self.item_price_entry.pack(side='right', padx=5)
        self.create_context_menu(self.item_price_entry)

        tk.Label(row2, text="الخصم (لكل صنف):", bg=self.CARD_BG, fg=self.TEXT_COLOR, font=('Segoe UI', 9)).pack(side='right', padx=5)
        self.item_discount_var = tk.StringVar(value="0")
        self.item_discount_entry = ttk.Entry(row2, textvariable=self.item_discount_var, width=10, font=('Segoe UI', 10))
        self.item_discount_entry.pack(side='right', padx=5)
        self.create_context_menu(self.item_discount_entry)

        AnimatedButton(row2, "➕ إضافة صنف", self.add_item, 
                      bg_color='#2ecc71', hover_color='#27ae60', width=150, height=40).pack(side='right', padx=20)

        # جدول الأصناف
        tree_container = tk.Frame(items_frame, bg=self.CARD_BG)
        tree_container.pack(fill='both', expand=True, pady=10)
        
        tree_scroll = ttk.Scrollbar(tree_container, orient='vertical')
        tree_scroll.pack(side='right', fill='y')

        columns = ('code', 'desc', 'unit', 'qty', 'price', 'discount', 'total')
        self.items_tree = ttk.Treeview(tree_container, columns=columns, height=8, 
                                       style='Modern.Treeview', yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.items_tree.yview)

        self.items_tree.tag_configure('oddrow', background='#ffffff')
        self.items_tree.tag_configure('evenrow', background='#f8f9fa')
        
        self.items_tree.heading('#0', text='#')
        self.items_tree.heading('code', text='رقم الصنف')
        self.items_tree.heading('desc', text='اسم الصنف')
        self.items_tree.heading('unit', text='الوحدة')
        self.items_tree.heading('qty', text='الكمية')
        self.items_tree.heading('price', text='السعر')
        self.items_tree.heading('discount', text='الخصم')
        self.items_tree.heading('total', text='الإجمالي')

        self.items_tree.column('#0', width=40, anchor='center')
        self.items_tree.column('code', width=90, anchor='center')
        self.items_tree.column('desc', width=300)
        self.items_tree.column('unit', width=70, anchor='center')
        self.items_tree.column('qty', width=70, anchor='center')
        self.items_tree.column('price', width=90, anchor='e')
        self.items_tree.column('discount', width=70, anchor='center')
        self.items_tree.column('total', width=110, anchor='e')

        self.items_tree.pack(side='left', fill='both', expand=True)

        # زر الحذف
        delete_btn_frame = tk.Frame(items_frame, bg=self.CARD_BG)
        delete_btn_frame.pack(pady=10)
        AnimatedButton(delete_btn_frame, "🗑️ حذف الصنف ", self.remove_item, 
                      bg_color='#e74c3c', hover_color='#c0392b', width=180, height=40).pack()

    def _create_totals_section(self, parent):
        """إنشاء قسم المجاميع مع عرض محدث تلقائياً للحسابات"""
        totals_card = self.create_card(parent, "💰 المجاميع")
        totals_frame = totals_card['content']

        base_bg = '#f6fbf7'
        value_bg = '#ecf9f1'
        border_color = '#cde8d7'
        title_color = '#2f3d33'

        main_totals_frame = tk.Frame(
            totals_frame,
            bg=base_bg,
            highlightbackground=border_color,
            highlightthickness=1,
            bd=0
        )
        main_totals_frame.pack(fill='both', expand=True, padx=0, pady=5)

        for i in range(4):
            main_totals_frame.columnconfigure(i, weight=1)
        for i in range(5):
            main_totals_frame.rowconfigure(i, minsize=55)

        def create_title_label(row, column, text):
            tk.Label(
                main_totals_frame,
                text=text,
                bg=base_bg,
                fg=title_color,
                font=('Segoe UI', 11, 'bold')
            ).grid(row=row, column=column, sticky='w', padx=12, pady=10)

        def create_value_chip(row, column, text, fg_color, columnspan=1):
            value_container = tk.Frame(
                main_totals_frame,
                bg=value_bg,
                highlightbackground=border_color,
                highlightthickness=1,
                bd=0
            )
            value_container.grid(row=row, column=column, columnspan=columnspan, sticky='ew', padx=12, pady=8)
            value_container.columnconfigure(0, weight=1)

            value_label = tk.Label(
                value_container,
                text=text,
                bg=value_bg,
                fg=fg_color,
                font=('Segoe UI', 14, 'bold'),
                anchor='e'
            )
            value_label.grid(row=0, column=0, sticky='ew', padx=10, pady=6)
            return value_label

        # === الصف الأول: المجموع قبل الخصم + نسبة الضريبة ===
        create_title_label(0, 3, "المجموع قبل الخصم:")
        self.subtotal_before_discount_label = create_value_chip(0, 2, "0.00", '#1b5e20')

        create_title_label(0, 1, "نسبة الضريبة (%):")

        self.tax_rate_var = tk.StringVar(value="15")
        tax_entry_container = tk.Frame(
            main_totals_frame,
            bg=value_bg,
            highlightbackground=border_color,
            highlightthickness=1,
            bd=0
        )
        tax_entry_container.grid(row=0, column=0, sticky='ew', padx=12, pady=8)
        tax_entry_container.columnconfigure(0, weight=1)

        self.tax_rate_entry = ttk.Entry(
            tax_entry_container,
            textvariable=self.tax_rate_var,
            font=('Segoe UI', 12, 'bold'),
            justify='center'
        )
        self.tax_rate_entry.grid(row=0, column=0, sticky='ew', padx=8, pady=6)
        self.tax_rate_entry.bind('<KeyRelease>', self._on_tax_rate_change)
        self.create_context_menu(self.tax_rate_entry)

        # === الصف الثاني: الخصم الكلي + الضريبة ===
        create_title_label(1, 3, "الخصم الكلي:")
        self.total_discount_label = create_value_chip(1, 2, "0.00", '#c0392b')

        create_title_label(1, 1, "قيمة الضريبة:")
        self.tax_label = create_value_chip(1, 0, "0.00", '#d35400')

        # === الصف الثالث: المجموع بعد الخصم ===
        create_title_label(2, 3, "المجموع بعد الخصم:")
        self.subtotal_label = create_value_chip(2, 0, "0.00", '#1f618d', columnspan=3)

        # === فاصل بصري ===
        separator = tk.Frame(main_totals_frame, bg=border_color, height=1)
        separator.grid(row=3, column=0, columnspan=4, sticky='ew', padx=12, pady=15)

        # === الإجمالي الكلي ===
        grand_total_container = tk.Frame(
            main_totals_frame,
            bg='#1b5e20',
            highlightbackground='#0f3d16',
            highlightthickness=1,
            bd=0
        )
        grand_total_container.grid(row=4, column=0, columnspan=4, sticky='ew', padx=12, pady=(0, 12))
        grand_total_container.columnconfigure(0, weight=1)
        grand_total_container.columnconfigure(1, weight=1)

        tk.Label(
            grand_total_container,
            text="الإجمالي الكلي:",
            bg='#1b5e20',
            fg='white',
            font=('Segoe UI', 13, 'bold')
        ).grid(row=0, column=1, sticky='w', padx=18, pady=14)

        self.total_label = tk.Label(
            grand_total_container,
            text="0.00",
            bg='#1b5e20',
            fg='white',
            font=('Segoe UI', 18, 'bold'),
            anchor='e'
        )
        self.total_label.grid(row=0, column=0, sticky='ew', padx=18, pady=14)

    def _create_notes_section(self, parent):
        """إنشاء قسم الملاحظات"""
        notes_card = self.create_card(parent, "📝 ملاحظات")
        notes_frame = notes_card['content']

        self.notes_text = tk.Text(
            notes_frame,
            height=3,
            width=80,
            font=('Segoe UI', 10),
            relief='solid',
            bd=1,
            bg='#fafafa'
        )
        self.notes_text.pack(fill='x', padx=5, pady=5)

        # إضافة قائمة سياق للـ Text widget
        def create_text_context_menu(widget):
            context_menu = tk.Menu(widget, tearoff=0)
            context_menu.add_command(label="نسخ (Ctrl+C)", command=lambda: widget.event_generate("<<Copy>>"))
            context_menu.add_command(label="لصق (Ctrl+V)", command=lambda: widget.event_generate("<<Paste>>"))
            context_menu.add_separator()
            context_menu.add_command(label="قص (Ctrl+X)", command=lambda: widget.event_generate("<<Cut>>"))
            context_menu.add_command(label="تحديد الكل (Ctrl+A)", command=lambda: widget.tag_add("sel", "1.0", "end"))

            def show_context_menu(event):
                context_menu.post(event.x_root, event.y_root)

            widget.bind("<Button-3>", show_context_menu)  # كليك يمين
            return context_menu

        create_text_context_menu(self.notes_text)

        self.notes_alignment_var = tk.StringVar(value='right')

        alignment_frame = tk.Frame(notes_frame, bg=self.CARD_BG)
        alignment_frame.pack(fill='x', padx=5, pady=(0, 5))

        alignment_options = [
            ("يمين", 'right'),
            ("وسط", 'center'),
            ("يسار", 'left')
        ]

        self.notes_alignment_styles = ttk.Style()
        self.notes_alignment_styles.configure('Notes.TRadiobutton', background=self.CARD_BG, font=('Segoe UI', 10))

        for option_label, option_value in alignment_options:
            ttk.Radiobutton(
                alignment_frame,
                text=option_label,
                value=option_value,
                variable=self.notes_alignment_var,
                command=lambda v=option_value: self._on_notes_alignment_change(v),
                style='Notes.TRadiobutton'
            ).pack(side='right', padx=5)

        tk.Label(
            alignment_frame,
            text="محاذاة النص:",
            bg=self.CARD_BG,
            fg=self.TEXT_COLOR,
            font=('Segoe UI', 10, 'bold')
        ).pack(side='right', padx=8)

        self.notes_text.bind('<<Modified>>', self._on_notes_modified)
        self._apply_notes_alignment()

    def _on_notes_alignment_change(self, alignment):
        """تحديث المحاذاة المختارة وتطبيقها مع الحفظ."""
        if self.notes_alignment_var.get() != alignment:
            self.notes_alignment_var.set(alignment)
        self._apply_notes_alignment()
        self._schedule_settings_save()

    def _on_notes_modified(self, event=None):
        """إعادة تطبيق المحاذاة عند تعديل النص"""
        if self.notes_text.edit_modified():
            self._apply_notes_alignment()
            self.notes_text.edit_modified(False)
            self._schedule_settings_save()

    def _apply_notes_alignment(self):
        """تطبيق محاذاة النص المحددة"""
        alignment = self.notes_alignment_var.get()

        # إزالة العلامات السابقة
        for tag in ('left', 'center', 'right'):
            self.notes_text.tag_remove(tag, '1.0', 'end')

        justify = 'right'
        if alignment == 'center':
            justify = 'center'
        elif alignment == 'left':
            justify = 'left'

        self.notes_text.tag_configure('left', justify='left')
        self.notes_text.tag_configure('center', justify='center')
        self.notes_text.tag_configure('right', justify='right')

        self.notes_text.tag_add(alignment, '1.0', 'end')
        self.notes_text.configure(wrap='word')

    def _create_action_buttons(self, parent):
        """إنشاء أزرار الإجراءات"""
        buttons_frame = tk.Frame(parent, bg=self.BG_COLOR)
        buttons_frame.pack(fill='x', pady=20, padx=10)

        button_container = tk.Frame(buttons_frame, bg=self.BG_COLOR)
        button_container.pack(expand=True)

        AnimatedButton(button_container, "🖨️ طباعة الفاتورة", self.print_invoice, 
                      bg_color='#f39c12', hover_color='#e67e22', width=200, height=50).pack(side='left', padx=10)
        AnimatedButton(button_container, "📄 فاتورة جديدة", self.clear_form, 
                      bg_color='#3498db', hover_color='#2980b9', width=200, height=50).pack(side='left', padx=10)

    def create_card(self, parent, title):
        """إنشاء بطاقة حديثة مع ظل وحواف مستديرة"""
        shadow_frame = tk.Frame(parent, bg='#d0d0d0', bd=0)
        shadow_frame.pack(fill='x', pady=(5, 8), padx=(12, 10))
        
        card_frame = tk.Frame(shadow_frame, bg=self.CARD_BG, bd=0, relief='flat')
        card_frame.pack(fill='x', padx=(0, 2), pady=(0, 2))
        
        title_frame = tk.Frame(card_frame, bg=self.CARD_BG, height=45)
        title_frame.pack(fill='x', padx=15, pady=(15, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text=title, bg=self.CARD_BG, 
                              fg=self.PRIMARY_COLOR, font=('Segoe UI', 13, 'bold'))
        title_label.pack(side='right', pady=5)
        
        separator = tk.Frame(card_frame, bg='#e0e0e0', height=1)
        separator.pack(fill='x', padx=15)
        
        content_frame = tk.Frame(card_frame, bg=self.CARD_BG)
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        return {'frame': card_frame, 'content': content_frame}

    def _wrap_text(self, text, length=40):
        """تقسيم النص الطويل"""
        if len(text) > length:
            words = text.split(' ')
            wrapped_text = ''
            line = ''
            for word in words:
                if len(line) + len(word) + 1 > length:
                    wrapped_text += line + '\n'
                    line = ''
                line += word + ' '
            wrapped_text += line
            return wrapped_text.strip()
        return text

    def add_item(self):
        """إضافة صنف جديد إلى الفاتورة مع تحديث فوري للحسابات"""
        try:
            # قراءة القيم مباشرة من Entry widgets
            code_entry_value = self.item_code_entry.get().strip()
            desc = self.desc_entry.get().strip()
            unit = self.item_unit_entry.get().strip()
            qty_str = self.item_qty_entry.get().strip()
            price_str = self.item_price_entry.get().strip()
            discount_str = self.item_discount_entry.get().strip()
            
            # التحقق من اسم الصنف قبل المتابعة
            if not desc:
                messagebox.showerror("خطأ", "يرجى إدخال اسم الصنف")
                self.desc_entry.focus_set()
                return

            # قبول رقم الصنف كما هو (أرقام، رموز، أو نصوص)
            # إذا لم يتم إدخال قيمة، استخدم الترقيم التلقائي
            if code_entry_value:
                display_code = code_entry_value
            else:
                if self.next_item_code is None:
                    self._initialize_next_item_code()
                current_code = self.next_item_code if self.next_item_code is not None else 1
                display_code = str(current_code)
                self.next_item_code = current_code + 1
            
            # قيم افتراضية محسّنة لبقية الحقول
            unit = unit if unit else "حبة"
            qty_str = qty_str if qty_str else "1"
            price_str = price_str if price_str else "0"
            discount_str = discount_str if discount_str else "0"
            
            # تحويل القيم إلى أرقام مع معالجة الأخطاء
            try:
                qty = float(qty_str)
                price = float(price_str)
                discount_amount = float(discount_str)
            except ValueError:
                messagebox.showerror("خطأ", "يرجى إدخال قيم صحيحة للكمية والسعر والخصم")
                return

            # الحصول على نسبة الضريبة بشكل آمن
            try:
                tax_rate = float(self.tax_rate_var.get()) / 100
            except ValueError:
                tax_rate = 0.15

            # حساب تفاصيل الصنف
            calc_result = self.calculator.calculate_item_total(price, qty, discount_amount, tax_rate)

            # إنشاء كائن الصنف
            item = {
                'item_code': display_code,
                'description': desc,
                'unit': unit,
                'quantity': qty,
                'price': price,
                'discount_per_unit': calc_result['discount_per_unit'],
                'discount_amount': calc_result['discount_amount'],
                'price_after_discount': calc_result['price_after_discount'],
                'tax_amount': calc_result['tax_amount'],
                'tax_exempt': 0,
                'total': calc_result['total']
            }

            # إضافة الصنف إلى القائمة
            self.items.append(item)
            self.item_counter += 1

            # إضافة الصنف إلى جدول الأصناف مع تنسيق الأرقام
            tag = 'oddrow' if self.item_counter % 2 != 0 else 'evenrow'
            idx = len(self.items)
            
            self.items_tree.insert('', 'end', text=str(idx),
                                  values=(display_code, desc, unit, 
                                         f"{qty:.2f}", 
                                         f"{price:.2f}",
                                         f"{calc_result['discount_amount']:.2f}", 
                                         f"{calc_result['total']:.2f}"),
                                  tags=(tag,))

            # تحديث حقول الإدخال للصنف التالي
            # إذا كان رقم الصنف رقمياً، قم بزيادة الترقيم التلقائي
            if code_entry_value and code_entry_value.isdigit():
                try:
                    next_num = int(code_entry_value) + 1
                    self.item_code_var.set(str(next_num))
                except (ValueError, TypeError):
                    self.item_code_var.set('')
            else:
                # إذا كان غير رقمي، اترك الحقل فارغاً ليختار المستخدم
                self.item_code_var.set('')
            
            self.item_desc_var.set('')
            self.item_unit_var.set('حبة')
            self.item_qty_var.set('1')
            self.item_price_var.set('0')
            self.item_discount_var.set('0')

            # تحديث المجاميع فوراً بعد إضافة الصنف
            self.calculate_totals()
            
            # إرجاع التركيز إلى حقل الوصف لإضافة صنف جديد
            self.desc_entry.focus_set()

        except Exception as e:
            messagebox.showerror("خطأ غير متوقع", f"حدث خطأ: {str(e)}")

    def _initialize_next_item_code(self):
        """تحديد بداية الترقيم التلقائي استناداً إلى المدخل الحالي"""
        try:
            current_value = self.item_code_entry.get().strip()
            self.next_item_code = int(current_value) if current_value else 1
        except ValueError:
            self.next_item_code = 1

    def remove_item(self):
        """حذف الصنف المحدد"""
        selected = self.items_tree.selection()
        if not selected:
            messagebox.showwarning("تحذير", "يرجى تحديد صنف للحذف")
            return

        selected_item_iid = selected[0]
        item_index = self.items_tree.index(selected_item_iid)

        self.items_tree.delete(selected_item_iid)

        if 0 <= item_index < len(self.items):
            del self.items[item_index]
        else:
            messagebox.showerror("خطأ", "فهرس الصنف خارج النطاق")
            return

        # إعادة بناء الجدول
        for i in self.items_tree.get_children():
            self.items_tree.delete(i)

        self.item_counter = 0
        next_code_seed = 1
        for item_data in self.items:
            self.item_counter += 1
            tag = 'oddrow' if self.item_counter % 2 != 0 else 'evenrow'
            wrapped_desc = self._wrap_text(item_data['description'])
            idx = self.item_counter
            item_code_display = str(item_data['item_code'])
            self.items_tree.insert('', 'end', text=str(idx),
                                   values=(item_code_display, wrapped_desc, item_data['unit'],
                                           item_data['quantity'], f"{item_data['price']:.2f}",
                                           f"{item_data['discount_amount']:.2f}", f"{item_data['total']:.2f}"),
                                   tags=(tag,))
            try:
                next_code_seed = max(next_code_seed, int(item_code_display) + 1)
            except ValueError:
                next_code_seed = self.item_counter + 1

        if self.items:
            self.next_item_code = next_code_seed
            self.item_code_var.set(str(self.next_item_code))
        else:
            self.next_item_code = None
            self.item_code_var.set('1')
        
        self.calculate_totals()

    def _on_tax_rate_change(self, event=None):
        """معالج تغيير نسبة الضريبة - يقوم بتحديث الحسابات فوراً"""
        try:
            float(self.tax_rate_var.get())
            self.calculate_totals()
        except ValueError:
            pass  # تجاهل الأخطاء أثناء الكتابة

    def select_template(self, template_id):
        """اختيار نموذج الفاتورة"""
        self.template_var.set(template_id)
        self.selected_template = template_id
        
        # أسماء مختصرة للعرض
        template_names = {
            'standard': 'نموذج 1',
            'simple': 'نموذج 2',
            'professional': 'نموذج 3',
            'rawayih': 'نموذج 4 '
        }
        
        # تحديث النص المختار
        display_name = template_names.get(template_id, template_id)
        self.selected_template_label.config(text=f"المختار: {display_name}")
    
    def on_template_change(self):
        """عند تغيير النموذج المختار - للتوافق مع الكود القديم"""
        self.selected_template = self.template_var.get()
    
    def on_font_change(self):
        """عند تغيير الخط المختار"""
        self.selected_font = self.font_var.get()
        self.custom_font_path = None  # إلغاء الخط المخصص عند اختيار خط افتراضي
        self.settings_manager.save(self)  # حفظ الخط المختار
    
    def select_custom_font(self):
        """اختيار خط مخصص من الحاسوب"""
        font_file = filedialog.askopenfilename(
            title="اختر ملف الخط",
            filetypes=[
                ("ملفات الخطوط", "*.ttf *.otf"),
                ("TrueType Font", "*.ttf"),
                ("OpenType Font", "*.otf"),
                ("جميع الملفات", "*.*")
            ]
        )
        
        if font_file and os.path.exists(font_file):
            self.custom_font_path = font_file
            font_name = os.path.splitext(os.path.basename(font_file))[0]
            
            # تحديث القائمة المنسدلة لعرض اسم الخط المخصص
            self.font_var.set(f"مخصص: {font_name}")
            self.selected_font = f"مخصص: {font_name}"
            
            messagebox.showinfo("نجح", f"تم اختيار الخط:\n{font_name}")
            self.settings_manager.save(self)

    def _initialize_totals(self):
        """تهيئة حقول المجاميع بقيم افتراضية عند بدء التطبيق"""
        self._update_totals_display("0.00", "0.00", "0.00", "0.00", "0.00")

    def _format_number(self, value):
        """تنسيق الأرقام مع فاصل الآلاف"""
        try:
            num = float(value)
            return f"{num:,.2f}".replace(',', '،')
        except (ValueError, TypeError):
            return "0.00"

    def _update_totals_display(self, before_discount, discount, subtotal, tax, total):
        """تحديث عرض المجاميع في الواجهة"""
        self.subtotal_before_discount_label.config(text=before_discount)
        self.total_discount_label.config(text=discount)
        self.subtotal_label.config(text=subtotal)
        self.tax_label.config(text=tax)
        self.total_label.config(text=total)

    def calculate_totals(self):
        """حساب المجاميع والضرائب مع عرض فوري للقيم المحدثة"""
        try:
            # الحصول على نسبة الضريبة
            try:
                tax_rate = float(self.tax_rate_var.get()) / 100
            except (ValueError, AttributeError):
                tax_rate = 0.15
            
            # حساب المجاميع
            totals = self.calculator.calculate_invoice_totals(self.items, tax_rate)
            
            # تنسيق الأرقام
            formatted_values = {
                'before': self._format_number(totals['subtotal_before_discount']),
                'discount': self._format_number(totals['total_discount']),
                'subtotal': self._format_number(totals['subtotal']),
                'tax': self._format_number(totals['tax']),
                'total': self._format_number(totals['total'])
            }
            
            # تحديث العرض
            self._update_totals_display(
                formatted_values['before'],
                formatted_values['discount'],
                formatted_values['subtotal'],
                formatted_values['tax'],
                formatted_values['total']
            )
            
        except Exception as e:
            self._update_totals_display("0.00", "0.00", "0.00", "0.00", "0.00")

    def print_invoice(self):
        """طباعة الفاتورة كملف PDF"""
        errors = self.validator.validate_all_fields(self)

        if errors:
            error_message = "يرجى تصحيح الأخطاء التالية:\n\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("خطأ في التحقق", error_message)

            for field_key in self.validator.required_fields.keys():
                if field_key in self.validator.validation_errors:
                    getattr(self, f"{field_key}_entry").focus_set()
                    break
            return

        if not self.items:
            messagebox.showerror("خطأ", "يرجى إضافة أصناف للفاتورة")
            return

        try:
            tax_rate = float(self.tax_rate_entry.get())
        except ValueError:
            tax_rate = 15.0
        
        # استخراج القيم المحسوبة من المجاميع
        def extract_number(text):
            """استخراج الرقم من النص المنسق"""
            try:
                return float(text.replace('،', '').strip())
            except (ValueError, AttributeError):
                return 0.0
        
        # قراءة البيانات مباشرة من Entry widgets
        current_invoice_type = self.invoice_type_var.get()
        print(f"Current invoice_type from var: {current_invoice_type}")
        invoice_data = {
            'invoice_number': self.invoice_number_entry.get(),
            'invoice_type': current_invoice_type,  # Combobox
            'company_name': self.company_name_entry.get(),
            'english_company_name': self.english_company_name_entry.get(),
            'tax_code': self.tax_code_entry.get(),
            'company_address': self.company_address_entry.get(),  # عنوان الشركة
            'logo_path': self.logo_path,
            'customer_name': self.customer_name_entry.get(),
            'customer_phone': self.customer_phone_entry.get(),
            'customer_tax_number': self.customer_tax_number_entry.get(),
            'customer_address': self.customer_address_entry.get(),
            'cost_center': self.cost_center_entry.get(),
            'warehouse': self.warehouse_entry.get(),
            'currency': self.currency_entry.get(),
            'date': self.date_entry.get(),
            'time': self.time_entry.get(),
            'items': self.items,
            'subtotal_before_discount': extract_number(self.subtotal_before_discount_label.cget('text')),
            'total_discount': extract_number(self.total_discount_label.cget('text')),
            'subtotal': extract_number(self.subtotal_label.cget('text')),
            'tax_rate': tax_rate,
            'tax': extract_number(self.tax_label.cget('text')),
            'total': extract_number(self.total_label.cget('text')),
            'notes': self.notes_text.get('1.0', 'end-1c'),
            'notes_alignment': self.notes_alignment_var.get()
        }

        if not os.path.exists('invoices'):
            os.makedirs('invoices')

        template_id = self.template_var.get()
        template_class = AVAILABLE_TEMPLATES[template_id]['class']
        
        # إنشاء النموذج مع الخط المختار
        font_to_use = self.selected_font
        custom_font_path = self.custom_font_path if self.custom_font_path and os.path.exists(self.custom_font_path) else None
        
        template_generator = template_class(font_name=font_to_use, custom_font_path=custom_font_path)
        
        invoice_data['custom_colors'] = self.template_colors[template_id]
        invoice_data['selected_font'] = self.selected_font  # إضافة الخط المختار
        invoice_data['custom_font_path'] = custom_font_path  # إضافة مسار الخط المخصص

        raw_name = invoice_data['invoice_number'].strip()
        base_name = raw_name if raw_name else datetime.now().strftime("invoice_%Y%m%d_%H%M%S")
        safe_name = ''.join(c for c in base_name if c not in '\\/:*?"<>|').strip()
        if not safe_name:
            safe_name = datetime.now().strftime("invoice_%Y%m%d_%H%M%S")
        default_filename = f"{safe_name}_{template_id}.pdf"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("ملفات PDF", "*.pdf")],
            initialdir=os.path.abspath('invoices'),
            initialfile=default_filename
        )

        if not save_path:
            return

        if template_generator.generate(invoice_data, save_path):
            self.settings_manager.save(self)
            
            abs_filename = os.path.abspath(save_path)
            template_name = AVAILABLE_TEMPLATES[template_id]['name']
            messagebox.showinfo("نجح", f"تم إنشاء {template_name} بنجاح!\n{abs_filename}")

            try:
                os.startfile(abs_filename)
            except Exception as e:
                print(f"Error opening file: {e}")

            if messagebox.askyesno("مستند جديد", "هل تريد إنشاء مستند جديد؟"):
                self.clear_form()
        else:
            messagebox.showerror("خطأ", "حدث خطأ أثناء إنشاء ملف PDF")

    def select_logo(self):
        """اختيار شعار الشركة"""
        filename = filedialog.askopenfilename(
            title="اختر شعار الشركة",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.logo_path = filename
            self.logo_label.config(text=os.path.basename(filename), foreground='#2ecc71', 
                                  font=('Segoe UI', 9, 'bold'))

    def clear_logo(self):
        """مسح شعار الشركة"""
        self.logo_path = ""
        self.logo_label.config(text="لم يتم اختيار شعار", foreground='#95a5a6',
                              font=('Segoe UI', 9, 'italic'))

    def clear_form(self):
        """مسح النموذج لإنشاء فاتورة جديدة"""
        self._restore_invoice_info_from_settings()
        self.customer_name_var.set('')
        self.customer_phone_var.set('')
        self.customer_tax_number_var.set('')
        self.customer_address_var.set('')
        self.cost_center_var.set('')
        self.items = []
        self.item_counter = 0
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        self.next_item_code = None
        self.item_code_var.set('1')
        self._initialize_next_item_code()
        self.notes_text.delete('1.0', 'end')
        self.tax_rate_var.set('15')
        self.calculate_totals()

    def open_template_color_settings(self, template_id):
        """فتح نافذة إعدادات ألوان النموذج"""
        # إنشاء نافذة منبثقة
        color_window = tk.Toplevel(self.root)
        color_window.title(f"إعدادات ألوان {template_id}")
        color_window.geometry("500x600")
        color_window.resizable(False, False)
        color_window.configure(bg=self.BG_COLOR)
        
        # توسيط النافذة
        color_window.transient(self.root)
        color_window.grab_set()
        
        # العنوان
        title_frame = tk.Frame(color_window, bg=self.PRIMARY_COLOR, height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        template_names = {
            'standard': 'النموذج القياسي',
            'simple': 'النموذج البسيط',
            'professional': 'النموذج الاحترافي'
        }
        
        tk.Label(
            title_frame, 
            text=f"⚙️ تخصيص ألوان {template_names.get(template_id, template_id)}",
            bg=self.PRIMARY_COLOR,
            fg='white',
            font=('Segoe UI', 14, 'bold')
        ).pack(expand=True)
        
        # إنشاء Canvas مع Scrollbar للمحتوى
        canvas_frame = tk.Frame(color_window, bg=self.BG_COLOR)
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        canvas = tk.Canvas(canvas_frame, bg=self.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        # محتوى النافذة
        content_frame = tk.Frame(canvas, bg=self.CARD_BG)
        
        content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=460)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # الألوان الحالية
        current_colors = self.template_colors[template_id]
        
        # متغيرات الألوان
        color_vars = {}
        
        # تعريفات الألوان
        color_labels = {
            'primary': 'اللون الأساسي',
            'secondary': 'اللون الثانوي',
            'accent': 'لون التمييز',
            'gold': 'اللون الذهبي',
            'header_bg': 'خلفية الرأس',
            'border': 'لون الحدود',
            'text': 'لون النص',
            'light_text': 'لون النص الفاتح'
        }
        
        row = 0
        color_previews = {}
        
        for color_key, color_label in color_labels.items():
            # إطار كل لون
            color_frame = tk.Frame(content_frame, bg=self.CARD_BG)
            color_frame.pack(fill='x', pady=10)
            
            # التسمية
            tk.Label(
                color_frame,
                text=color_label + ":",
                bg=self.CARD_BG,
                fg=self.TEXT_COLOR,
                font=('Segoe UI', 11)
            ).pack(side='right', padx=10)
            
            # حقل إدخال اللون
            color_var = tk.StringVar(value=current_colors[color_key])
            color_vars[color_key] = color_var
            
            color_entry = ttk.Entry(
                color_frame,
                textvariable=color_var,
                width=12,
                font=('Segoe UI', 10)
            )
            color_entry.pack(side='left', padx=10)
            self.create_context_menu(color_entry)
            
            # عرض اللون
            color_preview = tk.Canvas(
                color_frame,
                width=40,
                height=30,
                bg=current_colors[color_key],
                highlightthickness=1,
                highlightbackground='#cccccc'
            )
            color_preview.pack(side='left', padx=5)
            color_previews[color_key] = color_preview
            
            # تحديث معاينة اللون عند التغيير
            def create_update_preview(cvar, cpreview):
                def update_preview(*args):
                    try:
                        color_value = cvar.get()
                        if color_value.startswith('#') and len(color_value) in [4, 7]:
                            cpreview.configure(bg=color_value)
                    except:
                        pass
                return update_preview
            
            color_var.trace('w', create_update_preview(color_var, color_preview))
            
            # زر اختيار اللون
            def create_pick_color_command(cvar, cpreview):
                return lambda: self.pick_color(cvar, cpreview)
            
            AnimatedButton(
                color_frame,
                "🎨",
                create_pick_color_command(color_var, color_preview),
                bg_color='#3498db',
                hover_color='#2980b9',
                width=50,
                height=30
            ).pack(side='left', padx=5)
            
            row += 1
        
        # أزرار الإجراءات (خارج الـ canvas)
        buttons_frame = tk.Frame(color_window, bg=self.BG_COLOR)
        buttons_frame.pack(side='bottom', fill='x', pady=10, padx=10)
        
        def save_colors():
            """تحديث الألوان المختارة وحفظ الإعدادات فورًا"""
            for color_key, color_var in color_vars.items():
                self.template_colors[template_id][color_key] = color_var.get()

            # حفظ الإعدادات لضمان الاسترجاع التلقائي عند إعادة تشغيل التطبيق
            if not self.settings_manager.save(self):
                messagebox.showerror("خطأ", "تعذر حفظ الإعدادات. يرجى المحاولة مرة أخرى.")
                return

            messagebox.showinfo("نجح", "تم حفظ الألوان بنجاح!")
            color_window.destroy()
        
        def reset_colors():
            """إرجاع الألوان إلى القيم الافتراضية للنموذج"""
            default_template_colors = DEFAULT_TEMPLATE_COLORS.get(template_id, {})
            
            for color_key, color_var in color_vars.items():
                new_color = default_template_colors.get(color_key, color_var.get())
                color_var.set(new_color)
                color_previews[color_key].configure(bg=new_color)
        
        AnimatedButton(
            buttons_frame,
            "💾 حفظ",
            save_colors,
            bg_color='#2ecc71',
            hover_color='#27ae60',
            width=150,
            height=40
        ).pack(side='left', padx=10)
        
        AnimatedButton(
            buttons_frame,
            "🔄 إعادة تعيين",
            reset_colors,
            bg_color='#e74c3c',
            hover_color='#c0392b',
            width=150,
            height=40
        ).pack(side='left', padx=10)
        
        AnimatedButton(
            buttons_frame,
            "❌ إلغاء",
            color_window.destroy,
            bg_color='#95a5a6',
            hover_color='#7f8c8d',
            width=100,
            height=40
        ).pack(side='left', padx=10)
    
    def _restore_invoice_info_from_settings(self):
        """استعادة معلومات الفاتورة الأساسية من الإعدادات المحفوظة"""
        settings = self.settings_manager.last_settings or getattr(self, 'last_loaded_settings', {})
        if not settings:
            return

        def restore_entry(entry_widget, value):
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, value)

        if 'invoice_number' in settings:
            restore_entry(self.invoice_number_entry, settings['invoice_number'])
        if 'date' in settings:
            restore_entry(self.date_entry, settings['date'])
        if 'time' in settings:
            restore_entry(self.time_entry, settings['time'])

    def _handle_field_change(self, field_name, validator_callback=None):
        """معالجة تغييرات الحقول مع حفظ تلقائي للإعدادات"""
        if validator_callback is not None:
            validator_callback(self, field_name)

        if self._settings_save_job is not None:
            self.root.after_cancel(self._settings_save_job)

        self._settings_save_job = self.root.after(800, self._save_settings)

    def _schedule_settings_save(self):
        """جدولة حفظ الإعدادات مع تأخير لتجنب الحفظ المتكرر"""
        if self._settings_save_job is not None:
            self.root.after_cancel(self._settings_save_job)
        self._settings_save_job = self.root.after(800, self._save_settings)

    def _save_settings(self):
        """تنفيذ عملية حفظ الإعدادات المؤجلة"""
        try:
            self.settings_manager.save(self)
        finally:
            self._settings_save_job = None

    def _save_settings_immediately(self):
        """حفظ الإعدادات فوراً"""
        try:
            result = self.settings_manager.save(self)
            print(f"Settings saved immediately: {result}, invoice_type: {self.invoice_type_var.get()}")
        except Exception as e:
            print(f"Error saving settings immediately: {e}")

    def pick_color(self, color_var, color_preview):
        """اختيار لون من منتقي الألوان"""
        from tkinter import colorchooser
        
        # فتح منتقي الألوان
        color = colorchooser.askcolor(
            initialcolor=color_var.get(),
            title="اختر اللون"
        )
        
        if color[1]:  # إذا تم اختيار لون
            color_var.set(color[1])
            color_preview.configure(bg=color[1])

    def on_closing(self):
        """حفظ الإعدادات عند الإغلاق"""
        if self._settings_save_job is not None:
            self.root.after_cancel(self._settings_save_job)
            self._settings_save_job = None

        self.settings_manager.save(self)
        self.root.destroy()
