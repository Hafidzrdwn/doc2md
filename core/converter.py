import os
import re
import types
import sys
import logging
from typing import Set

logger = logging.getLogger(__name__)

# Ensure dummy magika module is available to prevent crashes in stripped/frozen environments
if "magika" not in sys.modules:
    class DummyMagikaResult:
        status = "failed"

    class DummyMagika:
        def __init__(self, *args, **kwargs):
            pass
        def identify_stream(self, *args, **kwargs):
            return DummyMagikaResult()
        def identify_bytes(self, *args, **kwargs):
            return DummyMagikaResult()
        def identify_path(self, *args, **kwargs):
            return DummyMagikaResult()

    dummy_magika = types.ModuleType("magika")
    dummy_magika.Magika = DummyMagika
    sys.modules["magika"] = dummy_magika

from markitdown import MarkItDown

_md_converter = None

def get_markitdown() -> MarkItDown:
    """Retrieve or initialize the MarkItDown converter instance."""
    global _md_converter
    if _md_converter is None:
        _md_converter = MarkItDown()
    return _md_converter

ALLOWED_EXTENSIONS: Set[str] = {
    ".pdf", ".docx", ".xlsx", ".xls", ".pptx",
    ".csv", ".txt", ".json", ".xml", ".html", ".md",
    ".png", ".jpg", ".jpeg", ".webp", ".bmp"
}

IMAGE_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".webp", ".bmp"
}

def clean_markdown_for_ai(text: str) -> str:
    """Normalize markdown text by trimming trailing spaces and invisible Unicode chars."""
    if not text:
        return ""
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    return text.strip()

def annotate_pdf_images(file_path: str, markdown_text: str) -> str:
    """Inspect a PDF file for embedded images and prepend contextual metadata for AI."""
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            total_images = 0
            page_images = {}
            for idx, page in enumerate(pdf.pages, 1):
                imgs = getattr(page, 'images', None)
                if imgs:
                    count = len(imgs)
                    total_images += count
                    page_images[idx] = count

            if total_images == 0:
                return markdown_text

            header_lines = [
                "> 🖼️ **[Konteks Visual Dokumen: Gambar/Diagram Terdeteksi]**",
                f"> Dokumen PDF asli memuat total **{total_images} gambar/diagram visual**:",
            ]
            for p_num, cnt in page_images.items():
                header_lines.append(f"> - **Halaman {p_num}**: Terdeteksi {cnt} gambar/diagram visual.")
            header_lines.append(
                "> *(Catatan untuk AI: Konten visual/grafik tidak dapat dirender langsung sebagai teks ASCII. "
                "Rujuk halaman terkait jika pertanyaan pengguna berkaitan dengan visual dokumen)*\n"
            )
            return "\n".join(header_lines) + "\n" + markdown_text
    except Exception as exc:
        logger.warning(f"Gagal memeriksa gambar PDF: {exc}")
        return markdown_text

from core.image_extractor import (
    extract_document_images,
    append_image_markdown_gallery,
    ExtractedImage,
)
from core.ocr_engine import (
    ocr_image_file_to_markdown,
    ocr_scanned_pdf,
    extract_text_from_image,
)

def convert_file_to_markdown_with_assets(file_path: str, original_filename: str) -> tuple[str, list[ExtractedImage]]:
    """
    Converts a supported file into clean, AI-optimized Markdown,
    applies OCR on images/scanned PDFs, and extracts real visual assets.
    Returns (markdown_text, list_of_extracted_images).
    """
    ext = os.path.splitext(original_filename)[1].lower()
    raw_size = os.path.getsize(file_path)

    images = extract_document_images(file_path, original_filename)

    if ext in IMAGE_EXTENSIONS:
        # Perform Offline OCR extraction for standalone images
        cleaned = ocr_image_file_to_markdown(file_path, original_filename)
        cleaned = clean_markdown_for_ai(cleaned)
    elif ext == ".pdf":
        # Check if PDF is a scan without text layer
        scanned_ocr_text = ocr_scanned_pdf(file_path)
        if scanned_ocr_text:
            cleaned = clean_markdown_for_ai(scanned_ocr_text)
        else:
            converter = get_markitdown()
            converted = converter.convert(file_path)
            cleaned = clean_markdown_for_ai(converted.text_content)
        cleaned = annotate_pdf_images(file_path, cleaned)
    else:
        converter = get_markitdown()
        converted = converter.convert(file_path)
        cleaned = clean_markdown_for_ai(converted.text_content)

    if images:
        cleaned = append_image_markdown_gallery(cleaned, images, original_filename)

    return cleaned, images

def convert_file_to_markdown(file_path: str, original_filename: str) -> str:
    """
    Converts a supported file into clean, AI-optimized Markdown.
    Includes contextual image annotations and visual asset links.
    """
    cleaned, _ = convert_file_to_markdown_with_assets(file_path, original_filename)
    return cleaned
