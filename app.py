import os
import sys
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
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

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app = FastAPI(title="Doc2MD Personal Optimizer", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Import and attach modular API routers
from routers import converter_router, exporter_router, watcher_router, diff_router

app.include_router(converter_router)
app.include_router(exporter_router)
app.include_router(watcher_router)
app.include_router(diff_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main conversion user interface."""
    return templates.TemplateResponse(request=request, name="index.html")


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