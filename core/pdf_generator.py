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


def get_markdown_converter() -> markdown.Markdown:
    """
    Creates and configures a Markdown converter with robust fallback handling.
    If optional extensions (like pymdownx.superfences, pymdownx.tasklist, or pymdownx.arithmatex) fail to load,
    it falls back cleanly to standard built-in extensions without crashing.
    """
    extensions = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
    ]
    extension_configs = {
        'markdown.extensions.codehilite': {
            'css_class': 'codehilite',
            'linenums': False,
            'guess_lang': True,
        }
    }

    # Safely probe and add pymdownx extensions if available
    try:
        import pymdownx.arithmatex
        extensions.append('pymdownx.arithmatex')
        extension_configs['pymdownx.arithmatex'] = {'generic': True}
    except Exception as exc:
        logger.debug(f"pymdownx.arithmatex not available: {exc}")

    try:
        import pymdownx.highlight
        import pymdownx.superfences
        extensions.append('pymdownx.superfences')
    except Exception as exc:
        logger.debug(f"pymdownx.superfences not available, using standard fenced_code: {exc}")

    try:
        import pymdownx.tasklist
        extensions.append('pymdownx.tasklist')
        extension_configs['pymdownx.tasklist'] = {'custom_checkbox': True}
    except Exception as exc:
        logger.debug(f"pymdownx.tasklist not available: {exc}")

    try:
        return markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
    except Exception as exc:
        logger.warning(f"Failed to initialize enhanced Markdown parser, falling back to minimal: {exc}")
        return markdown.Markdown(extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code'])


def _get_base_dir() -> str:
    import sys
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


_katex_assets_cache = None


def _get_katex_html_head() -> str:
    global _katex_assets_cache
    if _katex_assets_cache is not None:
        return _katex_assets_cache

    base_dir = _get_base_dir()
    vendor_dir = os.path.join(base_dir, "static", "vendor", "katex")
    css_path = os.path.join(vendor_dir, "katex.min.css")
    js_path = os.path.join(vendor_dir, "katex.min.js")
    auto_js_path = os.path.join(vendor_dir, "auto-render.min.js")

    if os.path.exists(css_path) and os.path.exists(js_path) and os.path.exists(auto_js_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_data = f.read()
            with open(js_path, "r", encoding="utf-8") as f:
                js_data = f.read()
            with open(auto_js_path, "r", encoding="utf-8") as f:
                auto_js_data = f.read()
            _katex_assets_cache = f"""
    <style>{css_data}</style>
    <script>{js_data}</script>
    <script>{auto_js_data}</script>
            """
            return _katex_assets_cache
        except Exception as exc:
            logger.warning(f"Failed to load local KaTeX files: {exc}")

    # Fallback to CDN
    _katex_assets_cache = """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    """
    return _katex_assets_cache


def markdown_to_html_document(markdown_text: str, title: str = "Dokumen", theme: Optional[str] = None) -> str:
    """
    Converts raw Markdown text into a fully-styled, standalone HTML document
    configured for optimal A4 print rendering and browser viewing with the specified theme.
    """
    clean_title = (title or "Dokumen").strip()
    cfg = get_theme(theme)
    md = get_markdown_converter()

    try:
        body_html = md.convert(markdown_text or "")
    except Exception as exc:
        logger.warning(f"Conversion with enhanced parser failed: {exc}. Retrying with minimal parser...")
        fallback_md = markdown.Markdown(extensions=['markdown.extensions.tables', 'markdown.extensions.fenced_code'])
        body_html = fallback_md.convert(markdown_text or "")
    css_content = get_print_css(theme=theme)
    katex_head = _get_katex_html_head()

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{clean_title} - Doc2MD Print ({cfg.name})</title>
    <style>
        {css_content}
    </style>
    {katex_head}
    <script>
        document.addEventListener("DOMContentLoaded", function () {{
            if (window.renderMathInElement) {{
                renderMathInElement(document.body, {{
                    delimiters: [
                        {{ left: "$$", right: "$$", display: true }},
                        {{ left: "$", right: "$", display: false }},
                        {{ left: "\\\\(", right: "\\\\)", display: false }},
                        {{ left: "\\\\[", right: "\\\\]", display: true }}
                    ],
                    throwOnError: false
                }});
            }}
        }});
    </script>
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
        with tempfile.TemporaryDirectory() as user_data_dir:
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f_html:
                f_html.write(html_content)
                temp_html = f_html.name

            temp_pdf = temp_html.replace(".html", ".pdf")

            cmd = [
                browser_exe,
                "--headless=new",
                "--disable-gpu",
                f"--user-data-dir={user_data_dir}",
                "--no-pdf-header-footer",
                f"--print-to-pdf={temp_pdf}",
                temp_html
            ]

            logger.info(f"Generating PDF with command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Chromium headless PDF error (code {result.returncode}): {result.stderr}")
                cmd[1] = "--headless"
                result_fallback = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
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
