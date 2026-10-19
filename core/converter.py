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

def inspect_excel_sheets(file_path: str) -> list[dict]:
    """Inspects an Excel workbook (.xlsx / .xls) and returns metadata about all worksheets."""
    sheets = []
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        for idx, name in enumerate(wb.sheetnames):
            max_r = 0
            max_c = 0
            try:
                ws = wb[name]
                max_r = ws.max_row or 0
                max_c = ws.max_column or 0
            except Exception:
                pass
            sheets.append({
                "index": idx,
                "name": name,
                "max_row": max_r,
                "max_column": max_c
            })
        wb.close()
    except Exception as exc:
        logger.warning(f"Gagal memeriksa sheet Excel {file_path}: {exc}")
    return sheets

def excel_to_markdown(file_path: str, selected_sheets: list[str] | None = None) -> str:
    """
    Converts an Excel workbook into clean, properly formatted Markdown tables.
    Supports filtering by selected sheet names or converting all sheets.
    """
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        available_sheets = wb.sheetnames

        # Filter target sheets
        if selected_sheets and "all" not in [str(s).lower().strip() for s in selected_sheets]:
            target_sheet_names = [s for s in available_sheets if s in selected_sheets]
            if not target_sheet_names:
                target_sheet_names = available_sheets
        else:
            target_sheet_names = available_sheets

        output_sections = []

        for sheet_name in target_sheet_names:
            ws = wb[sheet_name]
            raw_rows = []
            for row in ws.iter_rows(values_only=True):
                if any(cell is not None and str(cell).strip() != "" for cell in row):
                    formatted_row = []
                    for cell in row:
                        if cell is None:
                            formatted_row.append("")
                        else:
                            val = str(cell).strip()
                            val = val.replace("\r\n", "<br>").replace("\n", "<br>")
                            val = val.replace("|", "&#124;")
                            formatted_row.append(val)
                    raw_rows.append(formatted_row)

            if not raw_rows:
                output_sections.append(f"## Sheet: {sheet_name}\n\n*(Sheet kosong)*")
                continue

            max_cols = max(len(r) for r in raw_rows)
            padded_rows = [r + [""] * (max_cols - len(r)) for r in raw_rows]

            active_col_indices = [
                col_idx for col_idx in range(max_cols)
                if any(r[col_idx] != "" for r in padded_rows)
            ]
            if not active_col_indices:
                output_sections.append(f"## Sheet: {sheet_name}\n\n*(Sheet kosong)*")
                continue

            trimmed_rows = [
                [r[c] for c in active_col_indices]
                for r in padded_rows
            ]

            table_lines = [f"## Sheet: {sheet_name}\n"]
            header_row = trimmed_rows[0]
            header_rendered = [
                cell if cell != "" else f"Kolom {idx + 1}"
                for idx, cell in enumerate(header_row)
            ]
            table_lines.append("| " + " | ".join(header_rendered) + " |")
            table_lines.append("| " + " | ".join(["---"] * len(header_rendered)) + " |")

            for data_row in trimmed_rows[1:]:
                table_lines.append("| " + " | ".join(data_row) + " |")

            output_sections.append("\n".join(table_lines))

        wb.close()
        return "\n\n---\n\n".join(output_sections)
    except Exception as exc:
        logger.error(f"Gagal konversi Excel via openpyxl: {exc}", exc_info=True)
        # Fallback to standard markitdown
        converter = get_markitdown()
        converted = converter.convert(file_path)
        return converted.text_content

COMMON_SECTION_TITLES = {
    "DAFTAR ISI", "TABLE OF CONTENTS",
    "RINGKASAN EKSEKUTIF", "EXECUTIVE SUMMARY",
    "LATAR BELAKANG", "BACKGROUND",
    "RUMUSAN MASALAH", "PROBLEM STATEMENT",
    "TUJUAN PENELITIAN", "RESEARCH OBJECTIVES",
    "TUJUAN DAN MANFAAT", "OBJECTIVES AND BENEFITS",
    "METODOLOGI", "METODOLOGI PENELITIAN", "METHODOLOGY",
    "LANDASAN TEORI", "TINJAUAN PUSTAKA", "LITERATURE REVIEW",
    "HASIL DAN PEMBAHASAN", "PEMBAHASAN", "RESULTS AND DISCUSSION",
    "KESIMPULAN", "KESIMPULAN DAN SARAN", "CONCLUSION", "CONCLUSIONS",
    "SARAN", "RECOMMENDATIONS",
    "DAFTAR PUSTAKA", "REFERENCES", "BIBLIOGRAPHY",
    "LAMPIRAN", "APPENDIX", "APPENDICES",
    "PENDAHULUAN", "INTRODUCTION",
    "ABSTRAK", "ABSTRACT",
    "SPESIFIKASI TEKNIS", "TECHNICAL SPECIFICATIONS",
}

def structure_markdown_text(text: str, filename: str = "") -> str:
    """
    Intelligently enriches raw extracted document text into clean, structured Markdown:
    - Automatically formats chapter headings, numbered subheadings, and common titles (#, ##, ###).
    - Normalizes raw bullet points (•, ·, o, –, —) to Markdown list items (- ).
    - Groups programming code patterns into fenced code blocks (```python, etc.).
    - Detects tabular rows separated by multiple spaces or tabs into Markdown tables.
    """
    if not text or not text.strip():
        return ""

    lines = text.split("\n")
    processed_lines = []
    in_code_block = False
    code_buffer = []

    def flush_code_buffer():
        nonlocal code_buffer
        if code_buffer:
            first_line = code_buffer[0].lower()
            lang = ""
            if any(k in first_line for k in ["def ", "import ", "class ", "print("]):
                lang = "python"
            elif any(k in first_line for k in ["function ", "const ", "let ", "console.log"]):
                lang = "javascript"
            elif any(k in first_line for k in ["select ", "insert into", "create table"]):
                lang = "sql"
            elif any(k in first_line for k in ["curl ", "npm ", "pip ", "docker"]):
                lang = "bash"
            processed_lines.append(f"```{lang}")
            processed_lines.extend(code_buffer)
            processed_lines.append("```")
            code_buffer = []

    for idx, raw_line in enumerate(lines):
        line = raw_line.rstrip()
        stripped = line.strip()

        # Track existing fenced code blocks
        if stripped.startswith("```"):
            flush_code_buffer()
            in_code_block = not in_code_block
            processed_lines.append(line)
            continue

        if in_code_block:
            processed_lines.append(line)
            continue

        if not stripped:
            flush_code_buffer()
            processed_lines.append("")
            continue

        # If already formatted with markdown heading, table, list, or blockquote
        if re.match(r'^(#{1,6}\s|\|\s*---|[-*+]\s|\d+\.\s|>|\*\*|!\[)', stripped):
            flush_code_buffer()
            processed_lines.append(line)
            continue

        # Check for code line signatures
        is_code_line = bool(re.match(
            r'^\s*(def\s+\w+\(|import\s+\w+|from\s+\w+\s+import|class\s+\w+[:\(]|return\s+|if\s+__name__|console\.log\(|const\s+\w+\s*=|let\s+\w+\s*=|function\s+\w+\(|SELECT\s+.+\s+FROM\s+|INSERT\s+INTO\s+|CREATE\s+TABLE\s+)',
            line,
            re.IGNORECASE
        ))

        if is_code_line:
            code_buffer.append(line)
            continue
        elif len(code_buffer) >= 2:
            flush_code_buffer()
        elif code_buffer:
            # Single non-sustained code line, output normally
            processed_lines.extend(code_buffer)
            code_buffer = []

        # 1. Chapter / Module / Bab headings
        bab_match = re.match(r'^(?:BAB|CHAPTER|MODUL|BAGIAN)\s+([IVXLCDM0-9]+)\b[:\.\-\s]*(.*)$', stripped, re.IGNORECASE)
        if bab_match:
            ch_num = bab_match.group(1).upper()
            ch_title = bab_match.group(2).strip()
            title_part = f": {ch_title}" if ch_title else ""
            prefix = stripped.split()[0].upper()
            processed_lines.append(f"# {prefix} {ch_num}{title_part}")
            continue

        # 2. Numbered subheadings (e.g. 1.1 Latar Belakang, 2.3.1 Analisis Data)
        subsub_match = re.match(r'^(\d+\.\d+\.\d+)\s+([A-Za-z0-9].*)$', stripped)
        if subsub_match:
            processed_lines.append(f"### {subsub_match.group(1)} {subsub_match.group(2).strip()}")
            continue

        sub_match = re.match(r'^(\d+\.\d+)\s+([A-Za-z0-9].*)$', stripped)
        if sub_match:
            processed_lines.append(f"## {sub_match.group(1)} {sub_match.group(2).strip()}")
            continue

        num_sec_match = re.match(r'^(\d+)\.\s+([A-Z][A-Za-z0-9\s]{2,60})$', stripped)
        if num_sec_match and len(stripped) <= 65:
            processed_lines.append(f"## {num_sec_match.group(1)}. {num_sec_match.group(2).strip()}")
            continue

        # 3. Known standard section titles
        cleaned_upper = stripped.upper()
        if cleaned_upper in COMMON_SECTION_TITLES and len(stripped) <= 60:
            processed_lines.append(f"## {stripped.title()}")
            continue

        # 4. Standalone ALL-CAPS titles (4 - 55 chars, letters & spaces, no trailing punctuation)
        if (
            len(stripped) >= 4 and len(stripped) <= 55
            and re.match(r'^[A-Z0-9\s\-_/\(\)]+$', stripped)
            and not re.search(r'[\.,:;]$', stripped)
            and not any(char.islower() for char in stripped)
        ):
            # Check if next or prev line is empty (standalone title)
            prev_empty = (idx == 0) or not lines[idx - 1].strip()
            next_empty = (idx == len(lines) - 1) or not lines[idx + 1].strip()
            if prev_empty or next_empty:
                processed_lines.append(f"## {stripped}")
                continue

        # 5. Raw bullet points normalization (•, ·, o, –, —)
        bullet_match = re.match(r'^[•·o\u2022\u25cf\u25cb\u2013\u2014]\s+(.*)$', stripped)
        if bullet_match:
            processed_lines.append(f"- {bullet_match.group(1).strip()}")
            continue

        # 6. Tabular lines detection (lines with multiple tabs or large gap separators)
        if "\t" in line and len(line.split("\t")) >= 2:
            cols = [c.strip().replace("|", "&#124;") for c in line.split("\t") if c.strip() != ""]
            if len(cols) >= 2:
                processed_lines.append("| " + " | ".join(cols) + " |")
                continue

        processed_lines.append(line)

    flush_code_buffer()
    return clean_markdown_for_ai("\n".join(processed_lines))

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

def convert_file_to_markdown_with_assets(
    file_path: str,
    original_filename: str,
    selected_sheets: list[str] | None = None
) -> tuple[str, list[ExtractedImage]]:
    """
    Converts a supported file into clean, AI-optimized, structured Markdown.
    Applies OCR on images/scanned PDFs, supports Excel sheet selection,
    extracts real visual assets, and formats headings, code, and lists.
    Returns (markdown_text, list_of_extracted_images).
    """
    ext = os.path.splitext(original_filename)[1].lower()
    raw_size = os.path.getsize(file_path)

    images = extract_document_images(file_path, original_filename)

    if ext in IMAGE_EXTENSIONS:
        cleaned = ocr_image_file_to_markdown(file_path, original_filename)
        cleaned = clean_markdown_for_ai(cleaned)
    elif ext in [".xlsx", ".xls"]:
        cleaned = excel_to_markdown(file_path, selected_sheets=selected_sheets)
        cleaned = clean_markdown_for_ai(cleaned)
    elif ext == ".pdf":
        scanned_ocr_text = ocr_scanned_pdf(file_path)
        if scanned_ocr_text:
            cleaned = clean_markdown_for_ai(scanned_ocr_text)
        else:
            converter = get_markitdown()
            converted = converter.convert(file_path)
            cleaned = clean_markdown_for_ai(converted.text_content)
        cleaned = structure_markdown_text(cleaned, original_filename)
        cleaned = annotate_pdf_images(file_path, cleaned)
    else:
        converter = get_markitdown()
        converted = converter.convert(file_path)
        cleaned = clean_markdown_for_ai(converted.text_content)
        cleaned = structure_markdown_text(cleaned, original_filename)

    if images:
        cleaned = append_image_markdown_gallery(cleaned, images, original_filename)

    return cleaned, images

def convert_file_to_markdown(
    file_path: str,
    original_filename: str,
    selected_sheets: list[str] | None = None
) -> str:
    """
    Converts a supported file into clean, AI-optimized Markdown.
    Includes contextual image annotations and visual asset links.
    """
    cleaned, _ = convert_file_to_markdown_with_assets(
        file_path,
        original_filename,
        selected_sheets=selected_sheets
    )
    return cleaned

