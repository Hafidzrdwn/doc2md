"""
Converter and frontmatter API endpoints.
"""

import logging
import os
import shutil
import tempfile
from typing import List

from fastapi import APIRouter, File, Form, UploadFile
from core.converter import (
    ALLOWED_EXTENSIONS,
    convert_file_to_markdown_with_assets,
    inspect_excel_sheets,
)
from core.chunker import count_tokens, chunk_by_tokens
from core.frontmatter_formatter import attach_frontmatter
from core.ocr_engine import is_ocr_available

logger = logging.getLogger("doc2md.converter")
router = APIRouter(tags=["converter"])


@router.post("/inspect-excel-sheets")
async def inspect_excel_sheets_endpoint(file: UploadFile = File(...)):
    """Inspects an uploaded Excel file and returns the list of worksheets and dimensions."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".xlsx", ".xls"]:
        return {"filename": file.filename, "is_excel": False, "sheets": []}

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        sheets = inspect_excel_sheets(temp_path)
        return {
            "filename": file.filename,
            "is_excel": True,
            "sheet_count": len(sheets),
            "sheets": sheets
        }
    except Exception as exc:
        logger.error(f"Gagal memeriksa sheet Excel {file.filename}: {exc}")
        return {
            "filename": file.filename,
            "is_excel": True,
            "sheet_count": 0,
            "sheets": [],
            "error": str(exc)
        }
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


@router.post("/convert")
async def convert_endpoint(
    files: List[UploadFile] = File(...),
    chunk_tokens: int = Form(default=0),
    frontmatter_preset: str = Form(default="none"),
    selected_sheets: str = Form(default="all")
):
    """Converts uploaded documents into clean, token-counted Markdown."""
    results = []

    parsed_sheets = None
    if selected_sheets and selected_sheets.strip().lower() != "all":
        try:
            import json
            if selected_sheets.strip().startswith("["):
                parsed_sheets = json.loads(selected_sheets)
            else:
                parsed_sheets = [s.strip() for s in selected_sheets.split(",") if s.strip()]
        except Exception:
            parsed_sheets = [s.strip() for s in selected_sheets.split(",") if s.strip()]


    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": f"Ekstensi {ext} tidak didukung."
            })
            continue

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name

            raw_size = os.path.getsize(temp_path)
            markdown_content, extracted_images = convert_file_to_markdown_with_assets(
                temp_path, file.filename, selected_sheets=parsed_sheets
            )

            if frontmatter_preset and frontmatter_preset.strip().lower() != "none":
                raw_tokens = count_tokens(markdown_content)
                markdown_content = attach_frontmatter(
                    markdown_content,
                    filename=file.filename,
                    token_count=raw_tokens,
                    char_count=len(markdown_content),
                    preset=frontmatter_preset
                )

            tokens = count_tokens(markdown_content)
            chunks = []
            if chunk_tokens > 0 and tokens > chunk_tokens:
                chunks = chunk_by_tokens(markdown_content, chunk_tokens)

            is_ocr = ("[Hasil Ekstraksi OCR:" in markdown_content) or ("[Dokumen PDF Scan Terdeteksi" in markdown_content)

            results.append({
                "filename": file.filename,
                "status": "success",
                "markdown": markdown_content,
                "char_count": len(markdown_content),
                "token_count": tokens,
                "raw_size_kb": round(raw_size / 1024, 1),
                "chunks": chunks,
                "images_count": len(extracted_images),
                "images": [img.to_dict() for img in extracted_images],
                "is_ocr": is_ocr,
                "selected_sheets": parsed_sheets if parsed_sheets else ["all"]
            })
        except Exception as exc:
            logger.error(f"Gagal mengonversi file {file.filename}: {exc}", exc_info=True)
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": f"Gagal konversi: {str(exc)}"
            })
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    return {"results": results}


@router.get("/ocr-status")
async def get_ocr_status_endpoint():
    """Returns whether the offline OCR engine is active and ready."""
    return {"available": is_ocr_available(), "engine": "RapidOCR (ONNX Local)"}


@router.post("/format-frontmatter")
async def format_frontmatter_endpoint(
    markdown_text: str = Form(...),
    filename: str = Form("dokumen.md"),
    preset: str = Form("obsidian")
):
    """Attaches or updates structured YAML frontmatter for Obsidian/Notion."""
    tokens = count_tokens(markdown_text)
    formatted = attach_frontmatter(
        markdown_text=markdown_text,
        filename=filename,
        token_count=tokens,
        char_count=len(markdown_text),
        preset=preset
    )
    return {"markdown": formatted, "preset": preset}
