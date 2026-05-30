"""Common utilities and base classes for invoice templates."""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional

import arabic_reshaper
import qrcode
from bidi.algorithm import get_display
from num2words import num2words
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

LOGGER = logging.getLogger(__name__)


@dataclass
class TemplateTheme:
    """Visual configuration shared by templates."""

    primary: colors.Color
    secondary: colors.Color
    accent: colors.Color
    gold: colors.Color
    header_bg: colors.Color
    table_header: colors.Color
    table_row1: colors.Color
    table_row2: colors.Color
    border: colors.Color
    text: colors.Color
    light_text: colors.Color
    total_bg: colors.Color
    white: colors.Color = field(default=colors.white)


ARABIC_FONTS: Iterable[str] = (
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\times.ttf",
    "C:\\Windows\\Fonts\\tahoma.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
)

# خريطة أسماء الخطوط وملفاتها
FONT_MAP = {
    'Arial': 'C:\\Windows\\Fonts\\arial.ttf',
    'Tahoma': 'C:\\Windows\\Fonts\\tahoma.ttf',
    'Simplified Arabic': 'C:\\Windows\\Fonts\\simpfxed.ttf',
    'Traditional Arabic': 'C:\\Windows\\Fonts\\tradbdo.ttf',
}


class BaseInvoiceTemplate:
    """Base class for invoice templates providing shared utilities."""

    template_name: str = ""
    theme: TemplateTheme

    def __init__(self, font_name: str = 'Arial', custom_font_path: str = None) -> None:
        self.width, self.height = A4
        self.font_name = font_name
        self.custom_font_path = custom_font_path
        self.arabic_font = self._setup_arabic_font(font_name, custom_font_path)
        self._qr_file_counter = 0
    
    def apply_custom_colors(self, custom_colors: Dict[str, str]) -> None:
        """Apply custom colors to the theme if provided."""
        if not custom_colors:
            return
        
        # تحويل الألوان المخصصة إلى كائنات colors
        if 'primary' in custom_colors:
            self.theme.primary = colors.HexColor(custom_colors['primary'])
            self.theme.table_header = colors.HexColor(custom_colors['primary'])
            self.theme.total_bg = colors.HexColor(custom_colors['primary'])
        
        if 'secondary' in custom_colors:
            self.theme.secondary = colors.HexColor(custom_colors['secondary'])
        
        if 'accent' in custom_colors:
            self.theme.accent = colors.HexColor(custom_colors['accent'])
        
        if 'gold' in custom_colors:
            self.theme.gold = colors.HexColor(custom_colors['gold'])
        
        if 'header_bg' in custom_colors:
            self.theme.header_bg = colors.HexColor(custom_colors['header_bg'])
        
        if 'border' in custom_colors:
            self.theme.border = colors.HexColor(custom_colors['border'])
        
        if 'text' in custom_colors:
            self.theme.text = colors.HexColor(custom_colors['text'])
        
        if 'light_text' in custom_colors:
            self.theme.light_text = colors.HexColor(custom_colors['light_text'])

    # ------------------------------------------------------------------
    # Arabic & font helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _setup_arabic_font(font_name: str = 'Arial', custom_font_path: str = None) -> str:
        # محاولة تحميل الخط المخصص أولاً إذا كان موجوداً
        if custom_font_path and os.path.exists(custom_font_path):
            try:
                font_key = f"Arabic_Custom_{os.path.splitext(os.path.basename(custom_font_path))[0]}"
                pdfmetrics.registerFont(TTFont(font_key, custom_font_path))
                return font_key
            except Exception as exc:
                LOGGER.debug("Failed to register custom font %s: %s", custom_font_path, exc)

        # محاولة تحميل الخط المحدد من الخريطة
        if font_name in FONT_MAP:
            font_path = FONT_MAP[font_name]
            if os.path.exists(font_path):
                try:
                    font_key = f"Arabic_{font_name.replace(' ', '_')}"
                    pdfmetrics.registerFont(TTFont(font_key, font_path))
                    return font_key
                except Exception as exc:
                    LOGGER.debug("Failed to register font %s: %s", font_path, exc)

        # إذا فشل، استخدم الخطوط الافتراضية
        for font_path in ARABIC_FONTS:
            if os.path.exists(font_path):
                try:
                    font_filename = os.path.splitext(os.path.basename(font_path))[0]
                    font_key = f"Arabic_{font_filename}"
                    pdfmetrics.registerFont(TTFont(font_key, font_path))
                    return font_key
                except Exception as exc:  # pragma: no cover - unlikely
                    LOGGER.debug("Failed to register font %s: %s", font_path, exc)
        return "Helvetica"

    @staticmethod
    def reshape_arabic(text: Optional[str]) -> str:
        if text and any("\u0600" <= c <= "\u06FF" for c in str(text)):
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        return str(text or "")

    # ------------------------------------------------------------------
    # QR Code utilities
    # ------------------------------------------------------------------
    @staticmethod
    def _create_tlv(tag: int, value: str) -> bytes:
        value_bytes = value.encode("UTF-8")
        length = len(value_bytes)
        return bytes([tag]) + bytes([length]) + value_bytes

    @staticmethod
    def _normalize_timestamp_fields(date_str: str, time_str: str) -> str:
        date_str = str(date_str or "").strip()
        time_str = str(time_str or "").strip()

        def normalize_time(raw_time: str) -> str:
            if not raw_time:
                return "00:00:00"
            trimmed = raw_time.strip()
            if trimmed.endswith("Z"):
                trimmed = trimmed[:-1]
            if "T" in trimmed:
                trimmed = trimmed.split("T", 1)[1]
            if not trimmed:
                return "00:00:00"
            if len(trimmed.split(":")) == 2:
                trimmed = f"{trimmed}:00"
            return trimmed

        normalized_time = normalize_time(time_str)

        # "dd/mm/yyyy" format
        if "/" in date_str:
            try:
                day, month, year = [part.zfill(2) for part in date_str.split("/")]
                return f"{year}-{month}-{day}T{normalized_time}"
            except ValueError:
                LOGGER.debug("Date parsing failed for %s", date_str)

        # "yyyy-mm-dd" format
        if "-" in date_str and "T" not in date_str:
            try:
                year, month, day = [part.zfill(2) for part in date_str.split("-")]
                return f"{year}-{month}-{day}T{normalized_time}"
            except ValueError:
                LOGGER.debug("Date parsing failed for %s", date_str)

        # Already ISO
        if "T" in date_str:
            try:
                parsed = datetime.fromisoformat(date_str.replace("Z", ""))
                return f"{parsed.date().isoformat()}T{normalize_time(parsed.time().strftime('%H:%M:%S'))}"
            except ValueError:
                LOGGER.debug("Full ISO parsing failed for %s", date_str)

        # Fallback to current date with provided time (if any)
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{today}T{normalized_time}"

    def build_iso_timestamp(self, invoice_data: Dict[str, any]) -> str:
        """Return ISO timestamp without trailing Z (matching QR generator GUI)."""
        date_str = invoice_data.get("date", "")
        time_str = invoice_data.get("time", "")
        normalized = self._normalize_timestamp_fields(date_str, time_str)
        try:
            parsed = datetime.fromisoformat(normalized)
            return parsed.strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            LOGGER.debug("Unable to parse timestamp %s", normalized)
            return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def generate_qr_code(self, invoice_data: Dict[str, any]) -> str:
        company_name = invoice_data.get("company_name", "")
        vat_number = invoice_data.get("tax_code", "")

        timestamp = self.build_iso_timestamp(invoice_data)

        total_amount = f"{invoice_data.get('total', 0):.2f}"
        vat_amount = f"{invoice_data.get('tax', 0):.2f}"

        tlv_data = b"".join(
            (
                self._create_tlv(0x01, company_name),
                self._create_tlv(0x02, vat_number),
                self._create_tlv(0x03, timestamp),
                self._create_tlv(0x04, total_amount),
                self._create_tlv(0x05, vat_amount),
            )
        )

        qr_code_data = base64.b64encode(tlv_data).decode("UTF-8")

        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(qr_code_data)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")
        temp_file = f"temp_qr_{id(self)}_{self._qr_file_counter}.png"
        self._qr_file_counter += 1
        image.save(temp_file)
        return temp_file

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    @staticmethod
    def number_to_arabic_words(number: float) -> str:
        try:
            words = num2words(int(number), lang="ar")
            return f"{words} ريال سعودي"
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def draw_header(self, c: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        raise NotImplementedError

    def draw_invoice_info(self, c: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        raise NotImplementedError

    def draw_items_table(self, c: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        raise NotImplementedError

    def draw_totals(self, c: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> float:
        raise NotImplementedError

    def draw_footer(self, c: canvas.Canvas, invoice_data: Dict[str, any], y: float) -> None:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def generate(self, invoice_data: Dict[str, any], filename: str) -> bool:
        try:
            # تطبيق الألوان المخصصة إذا كانت موجودة
            custom_colors = invoice_data.get('custom_colors')
            if custom_colors:
                self.apply_custom_colors(custom_colors)
            
            document = canvas.Canvas(filename, pagesize=A4)
            y_position = self.height - 30

            y_position = self.draw_header(document, invoice_data, y_position)
            y_position = self.draw_invoice_info(document, invoice_data, y_position)
            y_position = self.draw_items_table(document, invoice_data, y_position)
            y_position = self.draw_totals(document, invoice_data, y_position)
            
            if hasattr(self, 'draw_notes'):
                y_position = self.draw_notes(document, invoice_data, y_position)
            
            self.draw_footer(document, invoice_data, y_position)

            document.save()
            return True

        except Exception as exc:  # pragma: no cover - broad catch for rendering errors
            LOGGER.exception("Error generating invoice: %s", exc)
            return False
