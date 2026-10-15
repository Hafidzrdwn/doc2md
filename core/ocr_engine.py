"""
Offline Optical Character Recognition (OCR) Engine for Doc2MD.
Extracts printed and handwritten text from standalone image files (.png, .jpg, etc.)
and scanned raster PDF documents without active text layers.
"""

import os
import re
import io
import logging
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Cached OCR Engine instance
_rapid_ocr = None
_rapid_ocr_initialized = False


def get_rapid_ocr():
    """Lazily initialize the RapidOCR engine."""
    global _rapid_ocr, _rapid_ocr_initialized
    if not _rapid_ocr_initialized:
        try:
            from rapidocr_onnxruntime import RapidOCR
            _rapid_ocr = RapidOCR()
            logger.info("RapidOCR engine initialized successfully.")
        except Exception as exc:
            logger.warning(f"Could not initialize RapidOCR: {exc}")
            _rapid_ocr = None
        _rapid_ocr_initialized = True
    return _rapid_ocr


def is_ocr_available() -> bool:
    """Check if any offline OCR engine is available."""
    if get_rapid_ocr() is not None:
        return True
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_from_image_array(img_array: np.ndarray) -> Tuple[str, float]:
    """
    Extracts text from a numpy image array using RapidOCR or pytesseract.
    Returns (extracted_text, average_confidence).
    """
    engine = get_rapid_ocr()
    if engine is not None:
        try:
            results, _ = engine(img_array)
            if not results:
                return "", 0.0

            lines = []
            scores = []
            for item in results:
                # item structure: [box_points, text, confidence_str]
                if len(item) >= 3:
                    text = item[1].strip()
                    try:
                        conf = float(item[2])
                    except (ValueError, TypeError):
                        conf = 0.8
                    if text:
                        lines.append(text)
                        scores.append(conf)

            avg_score = (sum(scores) / len(scores)) if scores else 0.0
            return "\n".join(lines), avg_score
        except Exception as exc:
            logger.warning(f"RapidOCR processing failed: {exc}")

    # Fallback to pytesseract
    try:
        import pytesseract
        pil_img = Image.fromarray(img_array)
        text = pytesseract.image_to_string(pil_img)
        return text.strip(), 0.85
    except Exception as exc:
        logger.warning(f"pytesseract processing failed: {exc}")

    return "", 0.0


def extract_text_from_image(image_input: Union[str, bytes, Image.Image, np.ndarray]) -> Tuple[str, float]:
    """
    Accepts a filepath, bytes, PIL Image, or numpy array and performs OCR.
    Returns (cleaned_text, average_confidence).
    """
    if isinstance(image_input, np.ndarray):
        arr = image_input
    elif isinstance(image_input, Image.Image):
        arr = np.array(image_input.convert("RGB"))
    elif isinstance(image_input, (str, Path)):
        if not os.path.exists(str(image_input)):
            return "", 0.0
        with Image.open(image_input) as img:
            arr = np.array(img.convert("RGB"))
    elif isinstance(image_input, bytes):
        with Image.open(io.BytesIO(image_input)) as img:
            arr = np.array(img.convert("RGB"))
    else:
        return "", 0.0

    return extract_text_from_image_array(arr)


def ocr_image_file_to_markdown(file_path: str, filename: str) -> str:
    """
    Converts a standalone image file (.png, .jpg, .webp, etc.) into an AI-ready
    Markdown document containing the extracted OCR text and contextual metadata.
    """
    raw_text, score = extract_text_from_image(file_path)
    file_size_kb = round(os.path.getsize(file_path) / 1024, 1)

    clean_text = raw_text.strip()
    if clean_text:
        score_pct = round(score * 100, 1)
        word_count = len(clean_text.split())
        return (
            f"> 🔍 **[Hasil Ekstraksi OCR: {filename}]** *(Ukuran: {file_size_kb} KB • Akurasi Deteksi: ~{score_pct}% • {word_count} kata)*\n"
            f"> *(Catatan untuk AI: Konten berikut diekstrak dari gambar visual menggunakan Offline OCR lokal)*\n\n"
            f"{clean_text}"
        )
    else:
        return (
            f"> 🖼️ **[File Gambar: {filename}]** *(Ukuran: {file_size_kb} KB)*\n"
            f"> *(Catatan untuk AI: File ini merupakan gambar visual asli. Tidak ada teks yang terdeteksi oleh OCR lokal)*"
        )


def ocr_scanned_pdf(file_path: str, min_chars_per_page: int = 40) -> Optional[str]:
    """
    Scans a PDF file. If pages have missing or very little text layer (less than min_chars_per_page),
    renders each scan page to a high-resolution bitmap and performs OCR.
    Returns combined markdown text if OCR was performed on any scanned page, or None if native text is sufficient.
    """
    pdf = None
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(file_path)
        total_pages = len(pdf)
        if total_pages == 0:
            return None

        # Check which pages need OCR
        pages_to_ocr = []
        page_native_texts = {}

        for p_idx in range(total_pages):
            page = pdf[p_idx]
            text_page = page.get_textpage()
            native_text = text_page.get_text_range().strip()
            page_native_texts[p_idx + 1] = native_text
            if len(native_text) < min_chars_per_page:
                pages_to_ocr.append(p_idx + 1)

        # If no pages need OCR, return None to use standard MarkItDown extraction
        if not pages_to_ocr:
            return None

        logger.info(f"PDF {file_path} contains {len(pages_to_ocr)}/{total_pages} scanned pages requiring OCR.")

        output_sections = []
        for p_idx in range(total_pages):
            p_num = p_idx + 1
            if p_num in pages_to_ocr:
                page = pdf[p_idx]
                # Render page at 2.0 scale (approx 150-200 DPI) for crisp OCR
                bitmap = page.render(scale=2.0)
                pil_image = bitmap.to_pil()
                arr = np.array(pil_image.convert("RGB"))
                ocr_text, conf = extract_text_from_image_array(arr)
                if ocr_text.strip():
                    output_sections.append(
                        f"## Halaman {p_num} (Hasil OCR Scan)\n\n"
                        f"{ocr_text.strip()}"
                    )
                else:
                    output_sections.append(
                        f"## Halaman {p_num}\n\n*(Halaman berupa grafik/gambar visual tanpa teks terbaca)*"
                    )
            else:
                native_text = page_native_texts.get(p_num, "")
                output_sections.append(
                    f"## Halaman {p_num}\n\n{native_text}"
                )

        combined = "\n\n---\n\n".join(output_sections)
        header = (
            f"> 🔍 **[Dokumen PDF Scan Terdeteksi: OCR Otomatis Diterapkan]**\n"
            f"> Dokumen PDF ini memuat **{len(pages_to_ocr)} dari {total_pages} halaman hasil scan** yang berhasil diekstrak via Offline OCR.\n\n"
        )
        return header + combined
    except Exception as exc:
        logger.warning(f"Failed scanning PDF with OCR: {exc}")
        return None
    finally:
        if pdf is not None:
            try:
                pdf.close()
            except Exception:
                pass

