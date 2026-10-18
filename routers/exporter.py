"""
Exporter endpoints for Word (.docx), PDF, HTML, and Batch ZIP packaging.
"""

import logging
import os
import re
from datetime import datetime

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import HTMLResponse, Response
from starlette.requests import Request

from core.docx_generator import markdown_to_docx_bytes
from core.pdf_generator import markdown_to_pdf_bytes, markdown_to_html_document
from core.batch_exporter import create_batch_zip
from core.themes import list_themes

logger = logging.getLogger("doc2md.exporter")
router = APIRouter(tags=["exporter"])


@router.get("/themes")
async def get_themes_endpoint():
    """Returns available document styling presets for Doc2MD."""
    return {"themes": list_themes()}


@router.post("/md-to-docx")
async def md_to_docx_endpoint(
    file: UploadFile = File(None),
    markdown_text: str = Form(None),
    filename: str = Form("dokumen"),
    theme: str = Form("modern_slate")
):
    """Converts Markdown text or an uploaded .md file into a styled Word .docx file."""
    try:
        content = ""
        target_name = (filename or "dokumen").strip()

        if file and file.filename:
            raw_bytes = await file.read()
            content = raw_bytes.decode("utf-8", errors="replace")
            if not filename or filename == "dokumen":
                target_name = os.path.splitext(file.filename)[0]
        elif markdown_text:
            content = markdown_text

        if not content.strip():
            return Response(content="Konten Markdown kosong atau tidak valid.", status_code=400)

        docx_bytes = markdown_to_docx_bytes(content, theme=theme)
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', target_name) or "dokumen"
        if not clean_name.lower().endswith(".docx"):
            clean_name += ".docx"

        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{clean_name}"'}
        )
    except Exception as exc:
        logger.error(f"Gagal membuat file DOCX: {exc}", exc_info=True)
        return Response(content=f"Terjadi kesalahan saat membuat DOCX: {str(exc)}", status_code=500)


@router.post("/md-to-pdf")
async def md_to_pdf_endpoint(
    file: UploadFile = File(None),
    markdown_text: str = Form(None),
    filename: str = Form("dokumen"),
    theme: str = Form("modern_slate")
):
    """Converts Markdown text or an uploaded .md file into a professional PDF with CSS Paged Media."""
    try:
        content = ""
        target_name = (filename or "dokumen").strip()

        if file and file.filename:
            raw_bytes = await file.read()
            content = raw_bytes.decode("utf-8", errors="replace")
            if not filename or filename == "dokumen":
                target_name = os.path.splitext(file.filename)[0]
        elif markdown_text:
            content = markdown_text

        if not content.strip():
            return Response(content="Konten Markdown kosong atau tidak valid.", status_code=400)

        pdf_bytes = markdown_to_pdf_bytes(content, title=target_name, theme=theme)
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', target_name) or "dokumen"
        if not clean_name.lower().endswith(".pdf"):
            clean_name += ".pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{clean_name}"'}
        )
    except Exception as exc:
        logger.error(f"Gagal membuat file PDF: {exc}", exc_info=True)
        return Response(content=f"Terjadi kesalahan saat membuat PDF: {str(exc)}", status_code=500)


@router.post("/md-to-html")
async def md_to_html_endpoint(
    file: UploadFile = File(None),
    markdown_text: str = Form(None),
    filename: str = Form("dokumen"),
    download: bool = Form(False),
    theme: str = Form("modern_slate")
):
    """Renders Markdown as a standalone styled HTML print-ready document."""
    try:
        content = ""
        target_name = (filename or "dokumen").strip()

        if file and file.filename:
            raw_bytes = await file.read()
            content = raw_bytes.decode("utf-8", errors="replace")
            if not filename or filename == "dokumen":
                target_name = os.path.splitext(file.filename)[0]
        elif markdown_text:
            content = markdown_text

        if not content.strip():
            return Response(content="Konten Markdown kosong atau tidak valid.", status_code=400)

        html_doc = markdown_to_html_document(content, title=target_name, theme=theme)
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', target_name) or "dokumen"
        if not clean_name.lower().endswith(".html"):
            clean_name += ".html"

        if download:
            return Response(
                content=html_doc.encode("utf-8"),
                media_type="text/html",
                headers={"Content-Disposition": f'attachment; filename="{clean_name}"'}
            )
        else:
            return HTMLResponse(content=html_doc)
    except Exception as exc:
        logger.error(f"Gagal membuat file HTML: {exc}", exc_info=True)
        return Response(content=f"Terjadi kesalahan saat membuat HTML: {str(exc)}", status_code=500)


@router.post("/download-batch-zip")
async def download_batch_zip_endpoint(request: Request):
    """Packages all converted documents, chunks, and a manifest into an in-memory ZIP archive."""
    try:
        body = await request.json()
        items = body.get("items", [])
        if not items:
            return Response(content="Tidak ada berkas yang dipilih untuk diunduh.", status_code=400)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_bytes = create_batch_zip(items, archive_title=f"doc2md_export_{timestamp_str}")

        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="doc2md_batch_{timestamp_str}.zip"'}
        )
    except Exception as exc:
        logger.error(f"Gagal membuat arsip ZIP: {exc}", exc_info=True)
        return Response(content=f"Terjadi kesalahan saat membuat arsip ZIP: {str(exc)}", status_code=500)


@router.post("/batch-md-export-zip")
@router.post("/batch-md-to-docx-zip")
async def batch_md_export_zip_endpoint(request: Request):
    """Converts a batch of markdown texts into styled DOCX and/or PDF files bundled in a single ZIP."""
    import io
    import zipfile

    try:
        body = await request.json()
        items = body.get("items", [])
        export_format = (body.get("format") or "docx").lower().strip()
        if not items:
            return Response(content="Tidak ada berkas yang dipilih untuk dikonversi.", status_code=400)

        zip_buffer = io.BytesIO()
        file_count = 0
        error_messages = []
        used_filenames = set()

        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for idx, item in enumerate(items, 1):
                raw_filename = item.get("filename", f"dokumen_{idx}")
                md_content = item.get("markdown", "")
                th = item.get("theme", "modern_slate")
                if not md_content.strip():
                    continue

                base_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_filename.rsplit('.', 1)[0]) or f"dokumen_{idx}"

                if export_format in ("docx", "both", "all"):
                    candidate_docx = f"{base_name}.docx"
                    c = 1
                    while candidate_docx in used_filenames:
                        candidate_docx = f"{base_name}_{c}.docx"
                        c += 1
                    try:
                        docx_bytes = markdown_to_docx_bytes(md_content, theme=th)
                        zf.writestr(candidate_docx, docx_bytes)
                        used_filenames.add(candidate_docx)
                        file_count += 1
                    except Exception as err:
                        logger.error(f"Gagal render DOCX untuk {raw_filename}: {err}")
                        error_messages.append(f"{raw_filename} (DOCX): {err}")

                if export_format in ("pdf", "both", "all"):
                    candidate_pdf = f"{base_name}.pdf"
                    c = 1
                    while candidate_pdf in used_filenames:
                        candidate_pdf = f"{base_name}_{c}.pdf"
                        c += 1
                    try:
                        pdf_bytes = markdown_to_pdf_bytes(md_content, title=base_name, theme=th)
                        zf.writestr(candidate_pdf, pdf_bytes)
                        used_filenames.add(candidate_pdf)
                        file_count += 1
                    except Exception as err:
                        logger.error(f"Gagal render PDF untuk {raw_filename}: {err}")
                        error_messages.append(f"{raw_filename} (PDF): {err}")

            if error_messages:
                warning_report = (
                    "Doc2MD - Laporan Catatan Konversi Berkas\n"
                    "========================================\n\n"
                    f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Total berkas dalam antrean: {len(items)}\n"
                    f"Total dokumen berhasil dikemas: {file_count}\n\n"
                    "Rincian berkas yang mengalami kendala:\n"
                    + "\n".join(f"- {msg}" for msg in error_messages)
                    + "\n\nSilakan periksa naskah Markdown di atas atau log server."
                )
                zf.writestr("CATATAN_KENDALA_KONVERSI.txt", warning_report.encode("utf-8"))

        if file_count == 0:
            err_detail = "; ".join(error_messages) if error_messages else "Naskah Markdown kosong atau tidak valid."
            return Response(
                content=f"Gagal membuat arsip ZIP: tidak ada dokumen yang berhasil dirender. Rincian: {err_detail}",
                status_code=500
            )

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "batch_export" if export_format in ("both", "all") else f"batch_{export_format}"
        headers = {
            "Content-Disposition": f'attachment; filename="{prefix}_{timestamp_str}.zip"'
        }
        if error_messages:
            headers["X-Conversion-Warnings"] = "; ".join(error_messages)

        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers=headers
        )
    except Exception as exc:
        logger.error(f"Gagal membuat batch arsip: {exc}", exc_info=True)
        return Response(content=f"Terjadi kesalahan saat membuat batch arsip: {str(exc)}", status_code=500)


