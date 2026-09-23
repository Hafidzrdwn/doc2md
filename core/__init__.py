"""
Core package for doc-to-markdown and markdown-to-docx conversions.
"""

from .chunker import count_tokens, chunk_by_tokens, get_encoder
from .converter import (
    ALLOWED_EXTENSIONS,
    IMAGE_EXTENSIONS,
    clean_markdown_for_ai,
    annotate_pdf_images,
    convert_file_to_markdown,
)
from .docx_generator import markdown_to_docx_bytes, clean_table_cell_text, clean_html_formatting

__all__ = [
    "count_tokens",
    "chunk_by_tokens",
    "get_encoder",
    "ALLOWED_EXTENSIONS",
    "IMAGE_EXTENSIONS",
    "clean_markdown_for_ai",
    "annotate_pdf_images",
    "convert_file_to_markdown",
    "markdown_to_docx_bytes",
    "clean_table_cell_text",
    "clean_html_formatting",
]
