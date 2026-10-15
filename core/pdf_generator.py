import os
import re
import sys
import shutil
import tempfile
import logging
import subprocess
from typing import Optional

import markdown
from pygments.formatters import HtmlFormatter

from .themes import get_theme, ThemeConfig

logger = logging.getLogger(__name__)

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

    /* Headings - Never orphan at the bottom of a page */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {cfg.heading_font};
        color: {cfg.secondary_color};
        font-weight: 700;
        line-height: 1.3;
        margin-top: 1.6em;
        margin-bottom: 0.6em;
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
        margin-bottom: 1em;
        text-align: justify;
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
        page-break-inside: auto; /* allow huge multi-page tables if needed */
    }}

    thead {{
        display: table-header-group; /* Repeat table header on every printed page */
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

    /* Code & Syntax Highlighting */
    code {{
        font-family: 'JetBrains Mono', Consolas, 'Courier New', monospace;
        font-size: 9pt;
        background-color: #{cfg.code_bg};
        color: {cfg.accent_color};
        padding: 2px 5px;
        border-radius: 4px;
        border: 1px solid #{cfg.table_border_color};
    }}

    pre, .codehilite {{
        background-color: #{cfg.code_bg};
        border: 1px solid #{cfg.table_border_color};
        border-radius: 8px;
        padding: 12px 16px;
        overflow-x: auto;
        margin: 1.4em 0;
        font-size: 8.5pt;
        line-height: 1.5;
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
        margin-bottom: 1em;
        padding-left: 24px;
    }}

    li {{
        margin-bottom: 0.35em;
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
        .no-print {{
            display: none !important;
        }}
        .document-wrapper {{
            padding: 0;
            max-width: 100%;
        }}
    }}
    """

def markdown_to_html_document(markdown_text: str, title: str = "Dokumen", theme: Optional[str] = None) -> str:
    """
    Converts raw Markdown text into a fully-styled, standalone HTML document
    configured for optimal A4 print rendering and browser viewing with the specified theme.
    """
    clean_title = (title or "Dokumen").strip()
    cfg = get_theme(theme)

    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'pymdownx.superfences',
            'pymdownx.tasklist',
        ],
        extension_configs={
            'markdown.extensions.codehilite': {
                'css_class': 'codehilite',
                'linenums': False,
                'guess_lang': True,
            },
            'pymdownx.tasklist': {
                'custom_checkbox': True,
            }
        }
    )

    body_html = md.convert(markdown_text or "")
    css_content = get_print_css(theme=theme)

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_title} - Doc2MD Print ({cfg.name})</title>
    <style>
        {css_content}
    </style>
</head>
<body>
    <div class="document-wrapper">
        <!-- Floating Interactive Toolbar (Automatically hidden when printed or exported to PDF) -->
        <div class="no-print">
            <div style="font-weight: 600; font-size: 14px; display: flex; align-items: center; gap: 8px;">
                <span style="display:inline-block; width:10px; height:10px; background:{cfg.primary_color}; border-radius:50%;"></span>
                <span>{clean_title}</span>
                <span style="font-size: 11px; opacity: 0.7; font-weight: normal;">• Doc2MD ({cfg.name})</span>
            </div>
            <div style="display: flex; gap: 10px;">
                <button onclick="window.print()" style="background: {cfg.primary_color}; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-weight: 600; font-size: 13px; cursor: pointer;">
                    🖨️ Cetak / Simpan PDF
                </button>
            </div>
        </div>

        <!-- Rendered Content -->
        <main id="main-content">
            {body_html}
        </main>
    </div>
</body>
</html>"""

def markdown_to_pdf_bytes(markdown_text: str, title: str = "Dokumen", theme: Optional[str] = None) -> bytes:
    """
    Renders Markdown to PDF bytes using an isolated headless Chromium/Edge instance.
    Guarantees crisp typography and pagination rules without awkward line/table breaks.
    """
    browser_exe = find_chromium_executable()
    if not browser_exe:
        raise RuntimeError(
            "Tidak ditemukan browser Chromium/Edge/Chrome di sistem untuk merender PDF. "
            "Pastikan Microsoft Edge atau Google Chrome terpasang."
        )

    html_content = markdown_to_html_document(markdown_text, title, theme=theme)

    temp_html = None
    temp_pdf = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f_html:
            f_html.write(html_content)
            temp_html = f_html.name

        temp_pdf = temp_html.replace(".html", ".pdf")

        cmd = [
            browser_exe,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={temp_pdf}",
            temp_html
        ]

        logger.info(f"Generating PDF with command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=25
        )

        if result.returncode != 0:
            logger.error(f"Chromium headless PDF error (code {result.returncode}): {result.stderr}")
            # Try fallback to legacy --headless flag if new flag was rejected
            cmd[1] = "--headless"
            result_fallback = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            if result_fallback.returncode != 0 or not os.path.exists(temp_pdf):
                raise RuntimeError(f"Gagal merender PDF via headless browser: {result.stderr or result_fallback.stderr}")

        if not os.path.exists(temp_pdf) or os.path.getsize(temp_pdf) == 0:
            raise RuntimeError("File PDF hasil render tidak ditemukan atau berukuran 0 byte.")

        with open(temp_pdf, "rb") as f_pdf:
            pdf_bytes = f_pdf.read()

        return pdf_bytes

    finally:
        if temp_html and os.path.exists(temp_html):
            try:
                os.remove(temp_html)
            except Exception:
                pass
        if temp_pdf and os.path.exists(temp_pdf):
            try:
                os.remove(temp_pdf)
            except Exception:
                pass
