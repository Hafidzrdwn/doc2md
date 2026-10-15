import os
import re
import sys
import shutil
import tempfile
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from flaskwebgui import FlaskUI

# Base application path resolution for frozen (PyInstaller) and standard runtimes
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
    log_path = Path(sys.executable).parent / "app-error.log"
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    if hasattr(os, 'add_dll_directory'):
        try:
            os.add_dll_directory(str(BASE_DIR))
            os.add_dll_directory(str(Path(sys.executable).parent))
        except Exception:
            pass
else:
    BASE_DIR = Path(__file__).resolve().parent
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

logger = logging.getLogger("doc2md")

from core.converter import (
    ALLOWED_EXTENSIONS,
    convert_file_to_markdown,
    convert_file_to_markdown_with_assets,
)
from core.chunker import count_tokens, chunk_by_tokens
from core.docx_generator import markdown_to_docx_bytes
from core.pdf_generator import markdown_to_pdf_bytes, markdown_to_html_document
from core.batch_exporter import create_batch_zip
from core.themes import list_themes
from core.ocr_engine import is_ocr_available

TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app = FastAPI(title="Doc2MD Personal Optimizer", docs_url=None, redoc_url=None)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main conversion user interface."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/convert")
async def convert_endpoint(
    files: List[UploadFile] = File(...),
    chunk_tokens: int = Form(default=0)
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

@app.get("/ocr-status")
async def get_ocr_status_endpoint():
    """Returns whether the offline OCR engine is active and ready."""
    return {"available": is_ocr_available(), "engine": "RapidOCR (ONNX Local)"}

@app.get("/themes")
async def get_themes_endpoint():
    """Returns available document styling presets for Doc2MD."""
    return {"themes": list_themes()}

@app.post("/md-to-docx")
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

@app.post("/md-to-pdf")
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

@app.post("/md-to-html")
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

@app.post("/download-batch-zip")
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

def run_uvicorn_server(**kwargs):
    """Runs the internal ASGI server for Desktop UI."""
    import uvicorn
    server_app = kwargs.get("app") or app
    port = kwargs.get("port") or 8473
    config = uvicorn.Config(
        app=server_app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        log_config=None,
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.run()

class CustomFlaskUI(FlaskUI):
    """Customized desktop webview wrapper with port readiness polling."""
    def start_browser(self, server_process):
        import socket
        import time
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.2):
                    break
            except (OSError, ConnectionRefusedError):
                time.sleep(0.2)
        super().start_browser(server_process)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    try:
        gui = CustomFlaskUI(
            server=run_uvicorn_server,
            server_kwargs={"app": app, "port": 8473},
            app=app,
            port=8473,
            width=1100,
            height=800,
        )
        gui.run()
    except Exception as e:
        logger.error(f"Fatal GUI error: {e}", exc_info=True)
    finally:
        sys.exit()