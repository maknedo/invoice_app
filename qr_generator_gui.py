import base64
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
import qrcode
from PIL import Image, ImageTk


class ModernEntry(tk.Frame):
    def __init__(self, parent, label_text, default_value="", **kwargs):
        super().__init__(parent, bg='#ffffff')
        
        self.label_text = label_text
        
        # Label
        self.label = tk.Label(
            self,
            text=label_text,
            font=('Segoe UI', 10),
            fg='#667eea',
            bg='#ffffff',
            anchor='w'
        )
        self.label.pack(fill=tk.X, pady=(0, 6))
        
        # Entry with border frame
        entry_frame = tk.Frame(self, bg='#e1e8ed', bd=0)
        entry_frame.pack(fill=tk.X)
        
        self.entry = tk.Entry(
            entry_frame,
            font=('Segoe UI', 12),
            bg='#ffffff',
            fg='#2d3436',
            relief=tk.FLAT,
            bd=0,
            **kwargs
        )
        self.entry.pack(fill=tk.BOTH, padx=3, pady=3)
        self.entry.insert(0, default_value)
        
        # Bind events for animation
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        
    def on_focus_in(self, event):
        self.label.configure(fg='#667eea', font=('Segoe UI', 10, 'bold'))
        self.entry.master.configure(bg='#667eea')
        
    def on_focus_out(self, event):
        self.label.configure(fg='#636e72', font=('Segoe UI', 10))
        self.entry.master.configure(bg='#e1e8ed')
        
    def get(self):
        return self.entry.get()
        
    def set(self, value):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)


class ModernButton(tk.Button):
    def __init__(self, parent, text, command, icon="", bg_color='#667eea', **kwargs):
        self.default_bg = bg_color
        self.hover_bg = self.adjust_color(bg_color, -20)
        
        display_text = f"{icon} {text}" if icon else text
        
        super().__init__(
            parent,
            text=display_text,
            command=command,
            font=('Segoe UI', 12, 'bold'),
            bg=bg_color,
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10,
            **kwargs
        )
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def adjust_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def on_enter(self, event):
        if self['state'] != 'disabled':
            self.configure(bg=self.hover_bg)
            
    def on_leave(self, event):
        if self['state'] != 'disabled':
            self.configure(bg=self.default_bg)


class QRGeneratorWindow:
    def __init__(self, parent=None):
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("مولد باركود الفاتورة الإلكترونية - ZATCA")
        
        # Set window to fullscreen (maximized)
        self.window.state('zoomed')  # For Windows
        # Alternative for other systems: self.window.attributes('-zoomed', True)
        
        # Set minimum size
        self.window.minsize(900, 700)
        self.window.configure(bg='#f5f6fa')
        
        self.qr_image = None
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with canvas for scrolling
        main_container = tk.Frame(self.window, bg='#f5f6fa')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_container, bg='#f5f6fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f6fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create window with center anchor for horizontal centering
        self.canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill=tk.BOTH, expand=True, padx=30, pady=30)
        scrollbar.pack(side="right", fill="y", pady=30)
        
        # Center content horizontally when canvas is resized
        def center_content(event=None):
            canvas_width = canvas.winfo_width()
            canvas.coords(self.canvas_window, canvas_width // 2, 0)
            canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', center_content)
        self.window.after(100, center_content)
        
        # Bind mouse wheel
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.window.bind_all("<MouseWheel>", on_mousewheel)
        
        # Header
        header_frame = tk.Frame(scrollable_frame, bg='#667eea', height=120)
        header_frame.pack(fill=tk.X, pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg='#667eea')
        header_content.place(relx=0.5, rely=0.5, anchor='center')
        
        icon_label = tk.Label(
            header_content,
            text="🔲",
            font=('Segoe UI Emoji', 50),
            bg='#667eea',
            fg='white'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 20))
        
        title_frame = tk.Frame(header_content, bg='#667eea')
        title_frame.pack(side=tk.LEFT)
        
        title_label = tk.Label(
            title_frame,
            text="مولد باركود الفاتورة الإلكترونية",
            font=('Segoe UI', 24, 'bold'),
            bg='#667eea',
            fg='white'
        )
        title_label.pack(anchor='w')
        
        subtitle_label = tk.Label(
            title_frame,
            text="متوافق مع معايير ZATCA السعودية",
            font=('Segoe UI', 13),
            bg='#667eea',
            fg='#e3e8f0'
        )
        subtitle_label.pack(anchor='w')
        
        # Content frame
        content_frame = tk.Frame(scrollable_frame, bg='#ffffff', relief=tk.FLAT)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add padding
        inner_content = tk.Frame(content_frame, bg='#ffffff', padx=50, pady=40)
        inner_content.pack(fill=tk.BOTH, expand=True)
        self.inner_content = inner_content
        
        # Input section
        input_label = tk.Label(
            inner_content,
            text="📝 بيانات الفاتورة",
            font=('Segoe UI', 16, 'bold'),
            fg='#2d3436',
            bg='#ffffff',
            anchor='w'
        )
        input_label.pack(fill=tk.X, pady=(0, 20))
        
        # Company Name
        self.company_name = ModernEntry(
            inner_content,
            "اسم المورد / Company Name",
            "شركة السواحل الجنوبية تجارية"
        )
        self.company_name.pack(fill=tk.X, pady=10)
        
        # VAT Number
        self.vat_number = ModernEntry(
            inner_content,
            "الرقم الضريبي / VAT Number",
            "311071470800003"
        )
        self.vat_number.pack(fill=tk.X, pady=10)
        
        # DateTime with button
        datetime_container = tk.Frame(inner_content, bg='#ffffff')
        datetime_container.pack(fill=tk.X, pady=10)
        
        self.invoice_datetime = ModernEntry(
            datetime_container,
            "تاريخ ووقت الفاتورة / Invoice DateTime (ISO 8601)",
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        self.invoice_datetime.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        now_btn = ModernButton(
            datetime_container,
            "الآن",
            self.set_current_datetime,
            icon="🕐",
            bg_color='#00b894',
            width=14
        )
        now_btn.pack(side=tk.LEFT, pady=(20, 0))
        
        # Total Amount
        self.total_amount = ModernEntry(
            inner_content,
            "المبلغ الإجمالي / Total Amount",
            "16617.5"
        )
        self.total_amount.pack(fill=tk.X, pady=10)
        
        # VAT Amount
        self.vat_amount = ModernEntry(
            inner_content,
            "ضريبة القيمة المضافة / VAT Amount",
            "2167.5"
        )
        self.vat_amount.pack(fill=tk.X, pady=10)
        
        # Generate Button
        generate_btn = ModernButton(
            inner_content,
            "توليد الباركود",
            self.generate_qr,
            icon="⚡",
            bg_color='#667eea',
            width=45
        )
        generate_btn.pack(pady=25)
        
        # Separator
        separator = tk.Frame(inner_content, height=2, bg='#e1e8ed')
        separator.pack(fill=tk.X, pady=20)
        
        # Output section
        output_label = tk.Label(
            inner_content,
            text="📊 النتيجة",
            font=('Segoe UI', 16, 'bold'),
            fg='#2d3436',
            bg='#ffffff',
            anchor='w'
        )
        output_label.pack(fill=tk.X, pady=(0, 20))
        
        # Base64 output
        base64_frame = tk.Frame(inner_content, bg='#ffffff')
        base64_frame.pack(fill=tk.X, pady=15)
        
        base64_label = tk.Label(
            base64_frame,
            text="النص المشفر (Base64):",
            font=('Segoe UI', 11, 'bold'),
            fg='#636e72',
            bg='#ffffff',
            anchor='w'
        )
        base64_label.pack(fill=tk.X, pady=(0, 8))
        
        text_frame = tk.Frame(base64_frame, bg='#e1e8ed', bd=0)
        text_frame.pack(fill=tk.X)
        
        self.base64_output = tk.Text(
            text_frame,
            height=5,
            font=('Consolas', 10),
            bg='#f8f9fa',
            fg='#2d3436',
            relief=tk.FLAT,
            wrap=tk.WORD,
            bd=0
        )
        self.base64_output.pack(fill=tk.X, padx=3, pady=3)
        
        # QR Code display
        qr_frame = tk.Frame(inner_content, bg='#ffffff')
        qr_frame.pack(fill=tk.X, pady=25)
        
        qr_label = tk.Label(
            qr_frame,
            text="رمز الاستجابة السريع (QR Code):",
            font=('Segoe UI', 11, 'bold'),
            fg='#636e72',
            bg='#ffffff'
        )
        qr_label.pack(pady=(0, 15))
        
        # QR display with border
        qr_container = tk.Frame(qr_frame, bg='#e1e8ed', bd=0)
        qr_container.pack()
        
        self.qr_display = tk.Label(qr_container, bg='#ffffff', bd=0, width=40, height=18)
        self.qr_display.pack(padx=15, pady=15)
        
        # Placeholder text
        placeholder = tk.Label(
            self.qr_display,
            text="سيظهر الباركود هنا بعد الضغط على زر التوليد\n⬆️",
            font=('Segoe UI', 12),
            fg='#b2bec3',
            bg='#ffffff',
            justify='center'
        )
        placeholder.pack(expand=True)
        self.qr_placeholder = placeholder
        
        # Save button section - ALWAYS VISIBLE
        save_section = tk.Frame(inner_content, bg='#ffffff')
        save_section.pack(fill=tk.X, pady=25)
        
        # Info label
        self.info_label = tk.Label(
            save_section,
            text="💡 سيتم تفعيل زر الحفظ بعد توليد الباركود",
            font=('Segoe UI', 10),
            fg='#636e72',
            bg='#ffffff'
        )
        self.info_label.pack(pady=(0, 15))
        
        # Save button
        self.save_btn = ModernButton(
            save_section,
            "حفظ الباركود",
            self.save_qr,
            icon="💾",
            bg_color='#00b894',
            width=35,
            state='disabled'
        )
        self.save_btn.pack()
        
        # Bottom spacing
        tk.Frame(inner_content, bg='#ffffff', height=60).pack()
        
    def set_current_datetime(self):
        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.invoice_datetime.set(current_time)
        
    def generate_tlv(self, tag, value):
        value_bytes = value.encode('utf-8')
        length = len(value_bytes)
        
        if length > 255:
            messagebox.showerror("خطأ", f"قيمة الحقل طويلة جداً (الحد الأقصى 255 بايت)")
            return None
            
        return bytes([tag, length]) + value_bytes
        
    def generate_qr(self):
        try:
            # Get values
            company_name = self.company_name.get().strip()
            vat_number = self.vat_number.get().strip()
            invoice_datetime = self.invoice_datetime.get().strip()
            total_amount = self.total_amount.get().strip()
            vat_amount = self.vat_amount.get().strip()
            
            # Validate
            if not all([company_name, vat_number, invoice_datetime, total_amount, vat_amount]):
                messagebox.showerror("خطأ", "يرجى ملء جميع الحقول")
                return
                
            # Generate TLV for each field
            tlv_data = b''
            
            # Tag 0x01: Company Name
            tlv = self.generate_tlv(0x01, company_name)
            if tlv is None:
                return
            tlv_data += tlv
            
            # Tag 0x02: VAT Number
            tlv = self.generate_tlv(0x02, vat_number)
            if tlv is None:
                return
            tlv_data += tlv
            
            # Tag 0x03: Invoice DateTime
            tlv = self.generate_tlv(0x03, invoice_datetime)
            if tlv is None:
                return
            tlv_data += tlv
            
            # Tag 0x04: Total Amount
            tlv = self.generate_tlv(0x04, total_amount)
            if tlv is None:
                return
            tlv_data += tlv
            
            # Tag 0x05: VAT Amount
            tlv = self.generate_tlv(0x05, vat_amount)
            if tlv is None:
                return
            tlv_data += tlv
            
            # Encode to Base64
            base64_encoded = base64.b64encode(tlv_data).decode('utf-8')
            
            # Display Base64
            self.base64_output.delete(1.0, tk.END)
            self.base64_output.insert(1.0, base64_encoded)
            
            # Generate QR Code
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(base64_encoded)
            qr.make(fit=True)
            
            # Create QR image
            self.qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Resize for display
            display_size = (300, 300)
            qr_display = self.qr_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # Hide placeholder
            self.qr_placeholder.pack_forget()
            
            # Display QR Code
            qr_photo = ImageTk.PhotoImage(qr_display)
            self.qr_display.configure(image=qr_photo)
            self.qr_display.image = qr_photo
            
            # Enable save button
            self.save_btn.configure(state='normal')
            
            # Update info label
            self.info_label.configure(
                text="✅ الباركود جاهز! يمكنك الآن حفظه",
                fg='#00b894',
                font=('Segoe UI', 10, 'bold')
            )
            
            messagebox.showinfo("✅ نجح", "تم توليد الباركود بنجاح!")
            
        except Exception as e:
            messagebox.showerror("❌ خطأ", f"حدث خطأ أثناء توليد الباركود:\n{str(e)}")
            
    def save_qr(self):
        if self.qr_image is None:
            messagebox.showwarning("⚠️ تحذير", "لا يوجد باركود لحفظه")
            return
            
        try:
            # Get user's Documents folder
            if os.name == 'nt':  # Windows
                default_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Documents')
                if not os.path.exists(default_dir):
                    default_dir = os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop')
            else:  # Linux/Mac
                default_dir = os.path.join(Path.home(), 'Documents')
                if not os.path.exists(default_dir):
                    default_dir = str(Path.home())
            
            # Create default filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"invoice_qr_{timestamp}.png"
            
            file_path = filedialog.asksaveasfilename(
                title="حفظ صورة الباركود",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ],
                initialdir=default_dir,
                initialfile=default_filename
            )
            
            if file_path:
                self.qr_image.save(file_path)
                
                if messagebox.askyesno("✅ تم الحفظ", 
                                      f"تم حفظ الباركود بنجاح!\n\n{file_path}\n\nهل تريد فتح المجلد؟"):
                    folder_path = os.path.dirname(file_path)
                    if os.name == 'nt':  # Windows
                        os.startfile(folder_path)
                    elif os.name == 'posix':  # Linux/Mac
                        import subprocess
                        if os.uname().sysname == 'Linux':
                            subprocess.run(['xdg-open', folder_path])
                        else:
                            subprocess.run(['open', folder_path])
                
        except Exception as e:
            messagebox.showerror("❌ خطأ", f"حدث خطأ أثناء حفظ الباركود:\n{str(e)}")
            
    def run(self):
        self.window.mainloop()


def main():
    app = QRGeneratorWindow()
    app.run()


if __name__ == "__main__":
    main()
