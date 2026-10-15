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
from core.frontmatter_formatter import attach_frontmatter
from core.folder_watcher import global_folder_watcher
from core.diff_viewer import compute_document_diff

from starlette.staticfiles import StaticFiles

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app = FastAPI(title="Doc2MD Personal Optimizer", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main conversion user interface."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/convert")
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

@app.get("/ocr-status")
async def get_ocr_status_endpoint():
    """Returns whether the offline OCR engine is active and ready."""
    return {"available": is_ocr_available(), "engine": "RapidOCR (ONNX Local)"}

@app.get("/themes")
async def get_themes_endpoint():
    """Returns available document styling presets for Doc2MD."""
    return {"themes": list_themes()}

@app.post("/format-frontmatter")
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

@app.get("/watcher/status")
async def get_watcher_status_endpoint():
    """Returns the live status, watched directory, and event history of the folder watcher."""
    return global_folder_watcher.get_status()

@app.post("/watcher/start")
async def start_watcher_endpoint(
    input_dir: str = Form("watch_input"),
    output_dir: str = Form("watch_output"),
    frontmatter_preset: str = Form("obsidian"),
    chunk_tokens: int = Form(0)
):
    """Starts the background folder watcher."""
    in_path = os.path.abspath(input_dir if os.path.isabs(input_dir) else str(BASE_DIR / input_dir))
    out_path = os.path.abspath(output_dir if os.path.isabs(output_dir) else str(BASE_DIR / output_dir))
    res = global_folder_watcher.start(
        input_dir=in_path,
        output_dir=out_path,
        frontmatter_preset=frontmatter_preset,
        chunk_tokens=chunk_tokens
    )
    return res

@app.post("/watcher/stop")
async def stop_watcher_endpoint():
    """Stops the active folder watcher."""
    return global_folder_watcher.stop()

@app.get("/watcher/history")
async def get_watcher_history_endpoint():
    """Returns the list of recently processed file events."""
    return {"history": global_folder_watcher.recent_events}

@app.post("/watcher/clear-history")
async def clear_watcher_history_endpoint():
    """Clears the watcher event history."""
    global_folder_watcher.clear_history()
    return {"status": "cleared"}

@app.post("/diff")
async def diff_endpoint(
    text_a: str = Form(""),
    text_b: str = Form(""),
    title_a: str = Form("Dokumen A"),
    title_b: str = Form("Dokumen B")
):
    """Computes side-by-side and unified differences between two Markdown strings."""
    return compute_document_diff(text_a, text_b, title_a=title_a, title_b=title_b)

@app.post("/diff/files")
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