"""Theme definitions for invoice templates."""

from __future__ import annotations

from reportlab.lib import colors

from .base import TemplateTheme


STANDARD_THEME = TemplateTheme(
    primary=colors.HexColor("#1B5E20"),
    secondary=colors.HexColor("#2E7D32"),
    accent=colors.HexColor("#4CAF50"),
    gold=colors.HexColor("#FFB300"),
    header_bg=colors.HexColor("#F1F8E9"),
    table_header=colors.HexColor("#2E7D32"),
    table_row1=colors.white,
    table_row2=colors.HexColor("#F9FBF8"),
    border=colors.HexColor("#A5D6A7"),
    text=colors.HexColor("#1B5E20"),
    light_text=colors.HexColor("#558B2F"),
    total_bg=colors.HexColor("#2E7D32"),
)


SIMPLE_THEME = TemplateTheme(
    primary=colors.HexColor("#0277BD"),
    secondary=colors.HexColor("#0288D1"),
    accent=colors.HexColor("#03A9F4"),
    gold=colors.HexColor("#FF6F00"),
    header_bg=colors.HexColor("#E1F5FE"),
    table_header=colors.HexColor("#0288D1"),
    table_row1=colors.white,
    table_row2=colors.HexColor("#F1F8FF"),
    border=colors.HexColor("#B3E5FC"),
    text=colors.HexColor("#01579B"),
    light_text=colors.HexColor("#039BE5"),
    total_bg=colors.HexColor("#0277BD"),
)


PROFESSIONAL_THEME = TemplateTheme(
    primary=colors.HexColor("#455A64"),      # أزرق رمادي هادئ
    secondary=colors.HexColor("#607D8B"),     # رمادي أزرق متوسط
    accent=colors.HexColor("#90A4AE"),       # رمادي ضبابي
    gold=colors.HexColor("#8D6E63"),         # بني هادئ للزخرفة
    header_bg=colors.HexColor("#FAFAFA"),    # رمادي جداً هادئ
    table_header=colors.HexColor("#37474F"), # رمادي داكن للعناوين
    table_row1=colors.white,
    table_row2=colors.HexColor("#F5F5F5"),   # رمادي فاتح جداً
    border=colors.HexColor("#B0BEC5"),       # رمادي مائي
    text=colors.HexColor("#263238"),         # رمادي أسود
    light_text=colors.HexColor("#455A64"),   # رمادي متوسط
    total_bg=colors.HexColor("#34495E"),     # أزرق داكن هادئ
)

__all__ = ["STANDARD_THEME", "SIMPLE_THEME", "PROFESSIONAL_THEME"]
