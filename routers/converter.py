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
)
from core.chunker import count_tokens, chunk_by_tokens
from core.frontmatter_formatter import attach_frontmatter
from core.ocr_engine import is_ocr_available

logger = logging.getLogger("doc2md.converter")
router = APIRouter(tags=["converter"])


@router.post("/convert")
async def convert_endpoint(
    files: List[UploadFile] = File(...),
    chunk_tokens: int = Form(default=0),
    frontmatter_preset: str = Form(default="none")
):
    """Converts uploaded documents into clean, token-counted Markdown."""
    results = []

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
            markdown_content, extracted_images = convert_file_to_markdown_with_assets(temp_path, file.filename)

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
                "is_ocr": is_ocr
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
