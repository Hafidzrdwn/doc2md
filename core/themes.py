"""
Centralized styling presets and theme engine for Doc2MD.
Provides professional color palettes, typography, and layout styling
for both Microsoft Word (.DOCX) and Precision PDF / HTML exports.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class ThemeConfig:
    id: str
    name: str
    description: str
    # Color hex values (with leading # for CSS/HTML)
    primary_color: str
    secondary_color: str
    accent_color: str
    text_color: str
    # Fonts
    heading_font: str
    body_font: str
    # Word docx specific font names
    docx_heading_font: str
    docx_body_font: str
    # Table & Container styling (Hex without # for Word oxml)
    table_header_bg: str
    table_header_text: str
    table_border_color: str
    code_bg: str
    # UI badge styling
    badge_bg: str
    badge_text: str
    # RGB tuples (0-255) for Word docx RGBColor
    rgb_primary: Tuple[int, int, int]
    rgb_secondary: Tuple[int, int, int]
    rgb_heading: Tuple[int, int, int]
    rgb_text: Tuple[int, int, int]


THEMES: Dict[str, ThemeConfig] = {
    "modern_slate": ThemeConfig(
        id="modern_slate",
        name="Modern Slate",
        description="Gaya modern minimalis dengan aksen Sky Blue dan kontras Slate elegan.",
        primary_color="#0284c7",
        secondary_color="#0f172a",
        accent_color="#0369a1",
        text_color="#1e293b",
        heading_font="'Plus Jakarta Sans', system-ui, -apple-system, sans-serif",
        body_font="'Plus Jakarta Sans', system-ui, -apple-system, sans-serif",
        docx_heading_font="Calibri",
        docx_body_font="Calibri",
        table_header_bg="F1F5F9",
        table_header_text="0F172A",
        table_border_color="CBD5E1",
        code_bg="F8FAFC",
        badge_bg="#e0f2fe",
        badge_text="#0369a1",
        rgb_primary=(2, 132, 199),
        rgb_secondary=(15, 23, 42),
        rgb_heading=(15, 23, 42),
        rgb_text=(30, 41, 59),
    ),
    "corporate_navy": ThemeConfig(
        id="corporate_navy",
        name="Corporate Navy",
        description="Gaya resmi formal perbankan dan korporasi dengan aksen Deep Royal Navy.",
        primary_color="#1e3a8a",
        secondary_color="#0f172a",
        accent_color="#1d4ed8",
        text_color="#1e293b",
        heading_font="'Segoe UI', 'Plus Jakarta Sans', sans-serif",
        body_font="'Segoe UI', 'Plus Jakarta Sans', sans-serif",
        docx_heading_font="Segoe UI",
        docx_body_font="Segoe UI",
        table_header_bg="EEF2FF",
        table_header_text="1E3A8A",
        table_border_color="C7D2FE",
        code_bg="F8FAFC",
        badge_bg="#e0e7ff",
        badge_text="#1e3a8a",
        rgb_primary=(30, 58, 138),
        rgb_secondary=(15, 23, 42),
        rgb_heading=(30, 58, 138),
        rgb_text=(30, 41, 59),
    ),
    "classic_academic": ThemeConfig(
        id="classic_academic",
        name="Classic Academic",
        description="Format naskah ilmiah, tesis, dan naskah formal dengan tipografi serif tradisional.",
        primary_color="#7f1d1d",
        secondary_color="#111827",
        accent_color="#991b1b",
        text_color="#111827",
        heading_font="'Georgia', 'Times New Roman', serif",
        body_font="'Georgia', 'Times New Roman', serif",
        docx_heading_font="Times New Roman",
        docx_body_font="Times New Roman",
        table_header_bg="F3F4F6",
        table_header_text="111827",
        table_border_color="9CA3AF",
        code_bg="F9FAFB",
        badge_bg="#fee2e2",
        badge_text="#991b1b",
        rgb_primary=(127, 29, 29),
        rgb_secondary=(17, 24, 39),
        rgb_heading=(127, 29, 29),
        rgb_text=(17, 24, 39),
    ),
    "emerald_tech": ThemeConfig(
        id="emerald_tech",
        name="Emerald Tech",
        description="Nuansa hijau emerald modern untuk dokumentasi sistem, devops, audit, dan panduan teknis.",
        primary_color="#059669",
        secondary_color="#064e3b",
        accent_color="#047857",
        text_color="#1e293b",
        heading_font="'Plus Jakarta Sans', system-ui, sans-serif",
        body_font="'Plus Jakarta Sans', system-ui, sans-serif",
        docx_heading_font="Arial",
        docx_body_font="Calibri",
        table_header_bg="D1FAE5",
        table_header_text="064E3B",
        table_border_color="A7F3D0",
        code_bg="F0FDF4",
        badge_bg="#d1fae5",
        badge_text="#065f46",
        rgb_primary=(5, 150, 105),
        rgb_secondary=(6, 78, 59),
        rgb_heading=(6, 78, 59),
        rgb_text=(30, 41, 59),
    ),
}

DEFAULT_THEME_ID = "modern_slate"


def get_theme(theme_id: Optional[str] = None) -> ThemeConfig:
    """
    Retrieve the ThemeConfig for a given theme_id.
    Falls back gracefully to DEFAULT_THEME_ID if the requested theme is missing or invalid.
    """
    if not theme_id:
        return THEMES[DEFAULT_THEME_ID]
    clean_id = theme_id.strip().lower()
    return THEMES.get(clean_id, THEMES[DEFAULT_THEME_ID])


def list_themes() -> List[Dict]:
    """Returns a list of all available themes formatted for UI dropdowns or API responses."""
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "primary_color": t.primary_color,
            "accent_color": t.accent_color,
            "docx_heading_font": t.docx_heading_font,
            "heading_font": t.heading_font,
        }
        for t in THEMES.values()
    ]
