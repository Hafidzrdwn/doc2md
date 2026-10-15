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
    convert_file_to_markdown_with_assets,
)
from .image_extractor import (
    ExtractedImage,
    extract_document_images,
    append_image_markdown_gallery,
)
from .docx_generator import markdown_to_docx_bytes, clean_table_cell_text, clean_html_formatting
from .pdf_generator import (
    markdown_to_pdf_bytes,
    markdown_to_html_document,
    find_chromium_executable,
)
from .batch_exporter import create_batch_zip
from .themes import (
    THEMES,
    ThemeConfig,
    DEFAULT_THEME_ID,
    get_theme,
    list_themes,
)
from .ocr_engine import (
    extract_text_from_image,
    extract_text_from_image_array,
    ocr_image_file_to_markdown,
    ocr_scanned_pdf,
    is_ocr_available,
)

__all__ = [
    "count_tokens",
    "chunk_by_tokens",
    "get_encoder",
    "ALLOWED_EXTENSIONS",
    "IMAGE_EXTENSIONS",
    "clean_markdown_for_ai",
    "annotate_pdf_images",
    "convert_file_to_markdown",
    "convert_file_to_markdown_with_assets",
    "ExtractedImage",
    "extract_document_images",
    "append_image_markdown_gallery",
    "markdown_to_docx_bytes",
    "clean_table_cell_text",
    "clean_html_formatting",
    "markdown_to_pdf_bytes",
    "markdown_to_html_document",
    "find_chromium_executable",
    "create_batch_zip",
    "THEMES",
    "ThemeConfig",
    "DEFAULT_THEME_ID",
    "get_theme",
    "list_themes",
    "extract_text_from_image",
    "extract_text_from_image_array",
    "ocr_image_file_to_markdown",
    "ocr_scanned_pdf",
    "is_ocr_available",
]

