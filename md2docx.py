"""
Compatibility proxy for core.docx_generator.
"""

from core.docx_generator import (
    markdown_to_docx_bytes,
    clean_table_cell_text,
    clean_html_formatting,
    add_inline_runs,
    set_cell_margins,
    set_cell_shading,
)

__all__ = [
    "markdown_to_docx_bytes",
    "clean_table_cell_text",
    "clean_html_formatting",
    "add_inline_runs",
    "set_cell_margins",
    "set_cell_shading",
]
