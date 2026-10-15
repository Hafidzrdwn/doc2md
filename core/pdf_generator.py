"""
Markdown to PDF and Standalone HTML Generator Engine for Doc2MD.
Delegates styling and Chromium discovery to .pdf_styles.
"""

import logging
import os
import subprocess
import tempfile
from typing import Optional

import markdown
from .themes import get_theme, ThemeConfig
from .pdf_styles import find_chromium_executable, get_pygments_css, get_print_css

logger = logging.getLogger(__name__)


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
