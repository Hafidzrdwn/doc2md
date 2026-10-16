"""
PDF and Print Stylesheet definitions and Chromium executable locator.
Contains CSS Paged Media rules ensuring professional anti-cutoff document layout.
"""

import os
import shutil
import sys
from typing import Optional
from pygments.formatters import HtmlFormatter

from .themes import get_theme, ThemeConfig


def find_chromium_executable() -> Optional[str]:
    """Locate Microsoft Edge or Google Chrome on Windows, macOS, or Linux."""
    # 1. Check PATH
    for name in ["msedge", "chrome", "google-chrome", "chromium-browser", "chromium"]:
        found = shutil.which(name)
        if found and os.path.exists(found):
            return found

    # 2. Check Windows well-known paths
    if sys.platform == "win32":
        candidates = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path

    # 3. Check macOS paths
    elif sys.platform == "darwin":
        candidates = [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path

    # 4. Check Linux paths
    else:
        candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
            "/usr/bin/microsoft-edge",
        ]
        for path in candidates:
            if os.path.exists(path):
                return path

    return None


def get_pygments_css() -> str:
    """Return clean syntax highlighting CSS for code blocks."""
    formatter = HtmlFormatter(style="default")
    return formatter.get_style_defs('.codehilite')


def get_print_css(theme: Optional[str] = None) -> str:
    """
    CSS Paged Media styling designed to ensure clean, professional PDF output
    without awkward page cutoffs, orphan headings, or broken tables.
    Customized according to the selected ThemeConfig.
    """
    cfg = get_theme(theme)
    pygments_css = get_pygments_css()
    return f"""
    /* ==========================================================================
       Doc2MD Print-Ready & PDF Paged Media Styles ({cfg.name})
       ========================================================================== */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    @page {{
        size: A4 portrait;
        margin: 18mm 16mm 20mm 16mm;
        @bottom-right {{
            content: "Halaman " counter(page) " dari " counter(pages);
            font-family: {cfg.body_font};
            font-size: 8.5pt;
            color: #64748b;
        }}
    }}

    *, *::before, *::after {{
        box-sizing: border-box;
    }}

    body {{
        font-family: {cfg.body_font};
        font-size: 10.5pt;
        line-height: 1.65;
        color: {cfg.text_color};
        background-color: #ffffff;
        margin: 0;
        padding: 0;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    }}

    /* Container */
    .document-wrapper {{
        max-width: 820px;
        margin: 0 auto;
        padding: 20px 0;
    }}

    ::-webkit-scrollbar {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }}

    /* Headings - Never orphan at the bottom of a page */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {cfg.heading_font};
        color: {cfg.secondary_color};
        font-weight: 700;
        line-height: 1.35;
        margin-top: 1.8em;
        margin-bottom: 0.65em;
        page-break-after: avoid !important;
        break-after: avoid !important;
    }}

    h1 {{
        font-size: 20pt;
        border-bottom: 2px solid {cfg.primary_color};
        padding-bottom: 6px;
        margin-top: 0;
        color: {cfg.primary_color};
    }}

    h2 {{
        font-size: 15pt;
        border-bottom: 1px solid #{cfg.table_border_color};
        padding-bottom: 4px;
        color: {cfg.secondary_color};
    }}

    h3 {{
        font-size: 12.5pt;
        color: {cfg.secondary_color};
    }}

    h4, h5, h6 {{
        font-size: 11pt;
        color: #334155;
    }}

    p {{
        margin-top: 0;
        margin-bottom: 1.1em;
        line-height: 1.7;
        text-align: left;
    }}

    /* Unbreakable Blocks: Tables, Code Blocks, Admonitions, Blockquotes */
    table, pre, .codehilite, blockquote, .admonition, figure, img {{
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }}

    /* Dynamic Proportional Tables */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1.4em 0;
        font-size: 9.5pt;
        page-break-inside: auto;
    }}

    thead {{
        display: table-header-group;
    }}

    tr {{
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }}

    th {{
        background-color: #{cfg.table_header_bg};
        color: #{cfg.table_header_text};
        font-weight: 700;
        text-align: left;
        padding: 8px 12px;
        border: 1px solid #{cfg.table_border_color};
        font-size: 9pt;
        letter-spacing: 0.02em;
    }}

    td {{
        padding: 8px 12px;
        border: 1px solid #{cfg.table_border_color};
        color: {cfg.text_color};
        vertical-align: top;
    }}

    tbody tr:nth-child(even) {{
        background-color: #{cfg.code_bg};
    }}

    /* Blockquotes & Callouts */
    blockquote {{
        margin: 1.4em 0;
        padding: 10px 16px;
        background-color: #{cfg.code_bg};
        border-left: 4px solid {cfg.primary_color};
        color: {cfg.text_color};
        border-radius: 0 8px 8px 0;
    }}

    blockquote p:last-child {{
        margin-bottom: 0;
    }}

    /* Code & Syntax Highlighting - Soft Wrap & No Dead Scrollbars */
    code {{
        font-family: 'JetBrains Mono', Consolas, 'Courier New', monospace;
        font-size: 8.8pt;
        background-color: #{cfg.code_bg};
        color: {cfg.accent_color};
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #{cfg.table_border_color};
    }}

    pre, .codehilite, pre code, .codehilite pre {{
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
        overflow: visible !important;
        overflow-x: visible !important;
    }}

    pre, .codehilite {{
        background-color: #{cfg.code_bg};
        border: 1px solid #{cfg.table_border_color};
        border-radius: 8px;
        padding: 12px 16px;
        margin: 1.5em 0 1.8em 0;
        font-size: 8.5pt;
        line-height: 1.55;
    }}

    pre code {{
        background-color: transparent;
        padding: 0;
        border: none;
        color: {cfg.secondary_color};
    }}

    {pygments_css}

    /* Lists */
    ul, ol {{
        margin-top: 0;
        margin-bottom: 1.2em;
        padding-left: 24px;
    }}

    li {{
        margin-bottom: 0.4em;
        line-height: 1.6;
    }}

    li::marker {{
        color: {cfg.primary_color};
        font-weight: 600;
    }}

    /* Horizontal Rules */
    hr {{
        border: 0;
        height: 1px;
        background-color: #{cfg.table_border_color};
        margin: 2em 0;
    }}

    /* Links */
    a {{
        color: {cfg.primary_color};
        text-decoration: none;
    }}

    /* Action Toolbar for Browser View (Hidden during Print) */
    .no-print {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0f172a;
        color: #ffffff;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }}

    @media print {{
        ::-webkit-scrollbar {{
            display: none !important;
        }}
        pre, .codehilite, pre code, .codehilite pre {{
            white-space: pre-wrap !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            overflow: visible !important;
        }}
        .no-print {{
            display: none !important;
        }}
        .document-wrapper {{
            padding: 0;
            max-width: 100%;
        }}
    }}
    """

