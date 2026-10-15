"""
Visual Document Diff API endpoints.
"""

import logging
import os
import shutil
import tempfile

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import Response

from core.converter import ALLOWED_EXTENSIONS, convert_file_to_markdown
from core.diff_viewer import compute_document_diff

logger = logging.getLogger("doc2md.diff")
router = APIRouter(tags=["diff"])


@router.post("/diff")
async def diff_endpoint(
    text_a: str = Form(""),
    text_b: str = Form(""),
    title_a: str = Form("Dokumen A"),
    title_b: str = Form("Dokumen B")
):
    """Computes side-by-side and unified differences between two Markdown strings."""
    return compute_document_diff(text_a, text_b, title_a=title_a, title_b=title_b)


@router.post("/diff/files")
async def diff_files_endpoint(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...)
):
    """Converts two uploaded documents and computes their visual differences."""
    temp_a = None
    temp_b = None
    try:
        ext_a = os.path.splitext(file_a.filename)[1].lower()
        ext_b = os.path.splitext(file_b.filename)[1].lower()

        if ext_a not in ALLOWED_EXTENSIONS or ext_b not in ALLOWED_EXTENSIONS:
            return Response(content="Format salah satu file tidak didukung untuk komparasi.", status_code=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext_a) as t_a:
            shutil.copyfileobj(file_a.file, t_a)
            temp_a = t_a.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext_b) as t_b:
            shutil.copyfileobj(file_b.file, t_b)
            temp_b = t_b.name

        text_a = convert_file_to_markdown(temp_a, file_a.filename)
        text_b = convert_file_to_markdown(temp_b, file_b.filename)

        return compute_document_diff(text_a, text_b, title_a=file_a.filename, title_b=file_b.filename)
    except Exception as exc:
        logger.error(f"Gagal melakukan diff file: {exc}", exc_info=True)
        return Response(content=f"Terjadi kesalahan saat komparasi file: {str(exc)}", status_code=500)
    finally:
        for p in (temp_a, temp_b):
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass
