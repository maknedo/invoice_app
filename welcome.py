#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
واجهة البداية للتطبيق - شاشة الترحيب
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import webbrowser
from invoice_gui import InvoiceApp
from qr_generator_gui import QRGeneratorWindow


class AnimatedButton(tk.Canvas):
    """زر متحرك مع تأثيرات Hover"""
    
    def __init__(self, parent, text, command, bg_color, hover_color, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.current_color = bg_color
        
        # Draw button
        self.button_id = self.create_rounded_rect(0, 0, kwargs['width'], kwargs['height'], 
                                                   radius=15, fill=bg_color)
        self.text_id = self.create_text(kwargs['width']/2, kwargs['height']/2, 
                                        text=text, fill='white', 
                                        font=('Segoe UI', 12, 'bold'))
        
        # Bind events
        self.tag_bind(self.button_id, '<Enter>', self.on_enter)
        self.tag_bind(self.button_id, '<Leave>', self.on_leave)
        self.tag_bind(self.button_id, '<Button-1>', self.on_click)
        self.tag_bind(self.text_id, '<Enter>', self.on_enter)
        self.tag_bind(self.text_id, '<Leave>', self.on_leave)
        self.tag_bind(self.text_id, '<Button-1>', self.on_click)
        
        self.configure(cursor='hand2')
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        self.animate_color(self.hover_color)
        self.scale(self.button_id, 0, 0, 1.02, 1.02)
        self.scale(self.text_id, 0, 0, 1.02, 1.02)
        
    def on_leave(self, event):
        self.animate_color(self.bg_color)
        self.scale(self.button_id, 0, 0, 1/1.02, 1/1.02)
        self.scale(self.text_id, 0, 0, 1/1.02, 1/1.02)
        
    def on_click(self, event):
        self.scale(self.button_id, 0, 0, 0.95, 0.95)
        self.scale(self.text_id, 0, 0, 0.95, 0.95)
        self.after(100, lambda: self.scale(self.button_id, 0, 0, 1/0.95, 1/0.95))
        self.after(100, lambda: self.scale(self.text_id, 0, 0, 1/0.95, 1/0.95))
        self.after(150, self.command)
        
    def animate_color(self, target_color):
        self.itemconfig(self.button_id, fill=target_color)


class DeveloperInfoWindow:
    """نافذة معلومات المطور بتصميم احترافي وجذاب"""
    
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("معلومات المطور")
        self.window.geometry("650x800")
        self.window.resizable(False, False)
        
        # Remove window decorations (title bar)
        self.window.overrideredirect(True)
        
        # Center window
        self.center_window()
        
        # Make modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Animation variables
        self.animation_running = True
        self.pulse_direction = 1
        self.pulse_step = 0
        
        # Create gradient canvas
        self.canvas = tk.Canvas(self.window, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw animated gradient background
        self.create_animated_gradient()
        
        # Main content frame with shadow effect
        self.main_frame = tk.Frame(self.canvas, bg='white', bd=0)
        self.canvas.create_window(325, 400, window=self.main_frame, anchor='center')
        
        # Build UI
        self.build_ui()
        
        # Start animations
        self.animate_gradient()
        self.animate_pulse()
        
        # Close button
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
    def center_window(self):
        """توسيط النافذة"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - 650) // 2
        y = (screen_height - 800) // 2
        self.window.geometry(f"650x800+{x}+{y}")
        
    def create_animated_gradient(self):
        """إنشاء خلفية متدرجة متحركة"""
        self.gradient_offset = 0
        colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']
        
        for i in range(len(colors) - 1):
            r1, g1, b1 = self.hex_to_rgb(colors[i])
            r2, g2, b2 = self.hex_to_rgb(colors[i + 1])
            
            steps = 100
            for j in range(steps):
                r = int(r1 + (r2 - r1) * j / steps)
                g = int(g1 + (g2 - g1) * j / steps)
                b = int(b1 + (b2 - b1) * j / steps)
                
                color = f'#{r:02x}{g:02x}{b:02x}'
                y1 = 800 * (i / (len(colors)-1) + j / (steps * (len(colors)-1)))
                y2 = 800 * (i / (len(colors)-1) + (j + 1) / (steps * (len(colors)-1)))
                
                self.canvas.create_rectangle(0, y1, 650, y2, fill=color, outline='', tags='gradient')
                
    def hex_to_rgb(self, hex_color):
        """تحويل من Hex إلى RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def animate_gradient(self):
        """تحريك الخلفية المتدرجة"""
        if self.animation_running:
            self.gradient_offset = (self.gradient_offset + 0.5) % 800
            self.window.after(50, self.animate_gradient)
            
    def animate_pulse(self):
        """تأثير النبض على العناصر"""
        if self.animation_running:
            self.pulse_step += self.pulse_direction * 0.02
            if self.pulse_step >= 1:
                self.pulse_direction = -1
            elif self.pulse_step <= 0:
                self.pulse_direction = 1
            self.window.after(50, self.animate_pulse)
            
    def build_ui(self):
        """بناء واجهة معلومات المطور"""
        # Container with padding
        container = tk.Frame(self.main_frame, bg='white', padx=40, pady=30)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Logo section with animation
        logo_frame = tk.Frame(container, bg='white')
        logo_frame.pack(pady=(0, 20))
        
        try:
            # Load and resize logo
            logo_path = r"C:\Users\Bn_Aljfri\Desktop\برنامج\print_invoice\images\٢٠٢٥١٠١٥_٢١٤٠١٠.png"
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            
            self.logo_label = tk.Label(logo_frame, image=self.logo_photo, bg='white', bd=0)
            self.logo_label.pack()
        except:
            # Fallback emoji if image not found
            self.logo_label = tk.Label(logo_frame, text="👨‍💻", font=('Segoe UI Emoji', 80), bg='white')
            self.logo_label.pack()
            
        # Decorative line
        tk.Canvas(container, height=3, bg='white', highlightthickness=0).pack(fill=tk.X, pady=10)
        line = tk.Canvas(container, height=3, bg='white', highlightthickness=0)
        line.pack(fill=tk.X, pady=(0, 20))
        line.create_rectangle(0, 0, 500, 3, fill='#667eea', outline='')
        
        # Developer name with fancy styling
        name_frame = tk.Frame(container, bg='white')
        name_frame.pack(pady=(0, 10))
        
        tk.Label(
            name_frame,
            text="محمد الجفري",
            font=('Tajawal', 28, 'bold'),
            fg='#2d3436',
            bg='white'
        ).pack()
        
        tk.Label(
            name_frame,
            text="مطور برمجيات وتطبيقات ومواقع ويب",
            font=('Tajawal', 12),
            fg='#667eea',
            bg='white'
        ).pack(pady=(5, 0))
        
        # Decorative separator
        separator = tk.Canvas(container, height=50, bg='white', highlightthickness=0)
        separator.pack(fill=tk.X, pady=15)
        separator.create_text(270, 25, text="⚡ للتواصل ⚡", font=('Tajawal', 14, 'bold'), fill='#764ba2')
        
        # Contact information with icons and interactive buttons
        contact_frame = tk.Frame(container, bg='white')
        contact_frame.pack(pady=10, fill=tk.X)
        
        # Phone
        self.create_contact_item(
            contact_frame,
            "📱",
            "+967 771 107 870",
            lambda: self.copy_to_clipboard("+967 771 107 870", "رقم الهاتف"),
            "#00b894"
        )
        
        # Email
        self.create_contact_item(
            contact_frame,
            "📧",
            "bn.algafri@gmail.com",
            lambda: self.copy_to_clipboard("bn.algafri@gmail.com", "البريد الإلكتروني"),
            "#0984e3"
        )
        
        # Decorative elements
        decorative_frame = tk.Frame(container, bg='white')
        decorative_frame.pack(pady=20)
        
        icons = ["💻", "🚀", "⭐", "🎯", "✨"]
        for icon in icons:
            tk.Label(
                decorative_frame,
                text=icon,
                font=('Segoe UI Emoji', 20),
                bg='white'
            ).pack(side=tk.LEFT, padx=5)
            
        # Close button with animation
        close_btn = AnimatedButton(
            container,
            text="✖ إغلاق",
            command=self.close_window,
            bg_color='#d63031',
            hover_color='#c0392b',
            width=200,
            height=50,
            bg='white'
        )
        close_btn.pack(pady=(20, 0))
        
    def create_contact_item(self, parent, icon, text, command, color):
        """إنشاء عنصر معلومات اتصال تفاعلي"""
        frame = tk.Frame(parent, bg='white', relief=tk.FLAT)
        frame.pack(fill=tk.X, pady=8)
        
        # Create hover effect
        def on_enter(e):
            frame.configure(bg='#f8f9fa')
            icon_label.configure(bg='#f8f9fa')
            text_label.configure(bg='#f8f9fa')
            frame.configure(cursor='hand2')
            
        def on_leave(e):
            frame.configure(bg='white')
            icon_label.configure(bg='white')
            text_label.configure(bg='white')
            
        frame.bind('<Enter>', on_enter)
        frame.bind('<Leave>', on_leave)
        frame.bind('<Button-1>', lambda e: command())
        
        inner = tk.Frame(frame, bg='white', pady=12, padx=20)
        inner.pack(fill=tk.X)
        inner.bind('<Button-1>', lambda e: command())
        
        icon_label = tk.Label(
            inner,
            text=icon,
            font=('Segoe UI Emoji', 24),
            bg='white'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        icon_label.bind('<Button-1>', lambda e: command())
        
        text_label = tk.Label(
            inner,
            text=text,
            font=('Tajawal', 13),
            fg=color,
            bg='white',
            anchor='e'
        )
        text_label.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        text_label.bind('<Button-1>', lambda e: command())
        
        for widget in [frame, inner, icon_label, text_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            
    def copy_to_clipboard(self, text, label):
        """نسخ النص إلى الحافظة"""
        self.window.clipboard_clear()
        self.window.clipboard_append(text)
        
        # Show notification
        notification = tk.Label(
            self.canvas,
            text=f"✓ تم نسخ {label}",
            font=('Tajawal', 11, 'bold'),
            fg='white',
            bg='#00b894',
            padx=20,
            pady=10
        )
        notif_window = self.canvas.create_window(325, 50, window=notification, anchor='center')
        
        # Fade out notification
        self.window.after(2000, lambda: self.canvas.delete(notif_window))
        
    def close_window(self):
        """إغلاق النافذة"""
        self.animation_running = False
        self.window.destroy()


class MainWindow:
    """نافذة البداية للتطبيق"""

    def __init__(self, root):
        self.root = root
        self.root.title("نظام الفواتير الإلكترونية")
        
        # Set window to fullscreen (maximized) - must be done first
        self.root.state('zoomed')  # For Windows
        # Alternative for other systems: self.root.attributes('-zoomed', True)
        
        # Set minimum size to keep window large
        self.root.minsize(1200, 800)
        
        # Configure style
        self.setup_styles()
        
        # Create gradient background
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw gradient
        self.create_gradient()
        
        # Main content frame
        self.content_frame = tk.Frame(self.canvas, bg='#ffffff', bd=0)
        # Create window at 0,0 initially - will be centered after window is fully loaded
        self.canvas_window = self.canvas.create_window(
            0, 0, 
            window=self.content_frame,
            anchor='center'
        )
        
        # Build UI
        self.build_ui()
        
        # Center content after window is fully loaded
        self.root.after(100, self.center_content)
        
        # Animate entrance
        self.root.after(150, self.animate_entrance)
        
        # Bind resize
        self.root.bind('<Configure>', self.on_resize)
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_gradient(self):
        width = self.canvas.winfo_reqwidth()
        height = self.canvas.winfo_reqheight()
        
        # Gradient colors from top to bottom
        colors = [
            '#667eea',  # Purple-blue
            '#764ba2',  # Purple
            '#f093fb',  # Light purple
            '#4facfe'   # Blue
        ]
        
        self.canvas.delete('gradient')
        
        limit = len(colors) - 1
        for i in range(limit):
            r1, g1, b1 = self.hex_to_rgb(colors[i])
            r2, g2, b2 = self.hex_to_rgb(colors[i + 1])
            
            steps = 100
            for j in range(steps):
                r = int(r1 + (r2 - r1) * j / steps)
                g = int(g1 + (g2 - g1) * j / steps)
                b = int(b1 + (b2 - b1) * j / steps)
                
                color = f'#{r:02x}{g:02x}{b:02x}'
                y1 = height * (i / limit + j / (steps * limit))
                y2 = height * (i / limit + (j + 1) / (steps * limit))
                
                self.canvas.create_rectangle(
                    0, y1, 3000, y2,
                    fill=color, outline='', tags='gradient'
                )
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def build_ui(self):
        inner_frame = tk.Frame(self.content_frame, bg='#ffffff', padx=60, pady=50)
        inner_frame = tk.Frame(self.content_frame, bg='#ffffff', padx=60, pady=50)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/Icon (using Unicode)
        icon_label = tk.Label(
            inner_frame,
            text="📋",
            font=('Segoe UI Emoji', 80),
            bg='#ffffff',
            fg='#667eea'
        )
        icon_label.pack(pady=(0, 20))
        self.icon_label = icon_label
        
        # Title
        title_label = tk.Label(
            inner_frame,
            text="نظام الفواتير الإلكترونية",
            font=('Segoe UI', 36, 'bold'),
            fg='#2d3436',
            bg='#ffffff'
        )
        title_label.pack(pady=(0, 10))
        self.title_label = title_label
        
        # Subtitle
        subtitle_label = tk.Label(
            inner_frame,
            text="إنشاء وطباعة الفواتير الضريبية بسهولة واحترافية",
            font=('Segoe UI', 14),
            fg='#636e72',
            bg='#ffffff'
        )
        subtitle_label.pack(pady=(0, 40))
        self.subtitle_label = subtitle_label
        
        # Buttons container
        buttons_frame = tk.Frame(inner_frame, bg='#ffffff')
        buttons_frame.pack(pady=20)
        
        # Main button
        self.main_btn = AnimatedButton(
            buttons_frame,
            text="📄 إنشاء فاتورة جديدة",
            command=self.open_invoice_app,
            bg_color='#667eea',
            hover_color='#5568d3',
            width=320,
            height=60,
            bg='#ffffff'
        )
        self.main_btn.pack(pady=10)
        
        # QR button
        self.qr_btn = AnimatedButton(
            buttons_frame,
            text="🔲 مولد باركود الفاتورة",
            command=self.open_qr_generator,
            bg_color='#00b894',
            hover_color='#00a383',
            width=320,
            height=60,
            bg='#ffffff'
        )
        self.qr_btn.pack(pady=10)
        
        # Features section
        features_frame = tk.Frame(inner_frame, bg='#ffffff')
        features_frame.pack(pady=(40, 0))
        
        features = [
            ("✨", "تصميم احترافي"),
            ("🚀", "سريع وسهل"),
            ("🔒", "آمن ومعتمد")
        ]
        
        self.feature_labels = []
        for icon, text in features:
            feature = tk.Frame(features_frame, bg='#ffffff')
            feature.pack(side=tk.LEFT, padx=20)
            
            icon_lbl = tk.Label(
                feature,
                text=icon,
                font=('Segoe UI Emoji', 24),
                bg='#ffffff'
            )
            icon_lbl.pack()
            
            text_lbl = tk.Label(
                feature,
                text=text,
                font=('Segoe UI', 10),
                fg='#636e72',
                bg='#ffffff'
            )
            text_lbl.pack()
            
            self.feature_labels.append((icon_lbl, text_lbl))
        
        # Developer button (floating button style)
        dev_btn_frame = tk.Frame(inner_frame, bg='#ffffff')
        dev_btn_frame.pack(pady=(20, 0))
        
        self.dev_btn = AnimatedButton(
            dev_btn_frame,
            text="👨‍💻 معلومات المطور",
            command=self.open_developer_info,
            bg_color='#fd79a8',
            hover_color='#e84393',
            width=250,
            height=50,
            bg='#ffffff'
        )
        self.dev_btn.pack()
        
        # Version info
        version_label = tk.Label(
            inner_frame,
            text="الإصدار 1.0 • مطابق لمعايير ZATCA",
            font=('Segoe UI', 9),
            fg='#b2bec3',
            bg='#ffffff'
        )
        version_label.pack(side=tk.BOTTOM, pady=(30, 0))
        self.version_label = version_label
        
    def animate_entrance(self):
        self.icon_label.place_forget()
        self.icon_label.place_forget()
        self.title_label.place_forget()
        self.subtitle_label.place_forget()
        self.main_btn.pack_forget()
        self.qr_btn.pack_forget()
        
        # Animate icon
        self.root.after(100, lambda: self.fade_in(self.icon_label, 0))
        
        # Animate title
        self.root.after(300, lambda: self.slide_in(self.title_label, 'right'))
        
        # Animate subtitle
        self.root.after(500, lambda: self.slide_in(self.subtitle_label, 'left'))
        
        # Animate buttons
        self.root.after(700, lambda: self.main_btn.pack(pady=10))
        self.root.after(900, lambda: self.qr_btn.pack(pady=10))
        
        # Animate features
        for i, (icon_lbl, text_lbl) in enumerate(self.feature_labels):
            self.root.after(1100 + i * 100, lambda l=icon_lbl: self.fade_in(l, 0))
            self.root.after(1100 + i * 100, lambda l=text_lbl: self.fade_in(l, 0))
            
    def fade_in(self, widget, alpha):
        widget.pack()

    def slide_in(self, widget, direction):
        widget.pack()
        
    def center_content(self):
        self.root.update_idletasks()
        self.root.update_idletasks()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.coords(self.canvas_window, width // 2, height // 2)
    
    def on_resize(self, event):
        if event.widget == self.root:
            self.create_gradient()
            # Update canvas window position
            self.center_content()

    def open_invoice_app(self):
        """فتح تطبيق الفواتير"""
        self.root.withdraw()
        new_root = tk.Tk()
        app = InvoiceApp(new_root)
        new_root.protocol("WM_DELETE_WINDOW", lambda: self.on_close_invoice(new_root))
        new_root.mainloop()
        
    def on_close_invoice(self, window):
        window.destroy()
        self.root.deiconify()

    def open_qr_generator(self):
        """فتح مولد باركود الفاتورة"""
        self.root.withdraw()
        self.qr_window = QRGeneratorWindow(self.root)
        self.qr_window.window.protocol("WM_DELETE_WINDOW", self.on_close_qr_generator)
        
    def on_close_qr_generator(self):
        """إغلاق مولد باركود الفاتورة"""
        window = getattr(self, "qr_window", None)
        if window:
            window.window.destroy()
            self.qr_window = None
        self.root.deiconify()
        
    def open_developer_info(self):
        """فتح نافذة معلومات المطور"""
        DeveloperInfoWindow(self.root)
