"""
Folder Watcher API endpoints.
"""

import os
from pathlib import Path
from fastapi import APIRouter, Form
from core.folder_watcher import global_folder_watcher

router = APIRouter(prefix="/watcher", tags=["watcher"])


@router.get("/status")
async def get_watcher_status_endpoint():
    """Returns the live status, watched directory, and event history of the folder watcher."""
    # Ensure default folders exist so they can be browsed immediately
    os.makedirs(os.path.abspath("watch_input"), exist_ok=True)
    os.makedirs(os.path.abspath("watch_output"), exist_ok=True)
    return global_folder_watcher.get_status()


@router.post("/open-folder")
async def open_folder_endpoint(
    folder_path: str = Form(None),
    folder_type: str = Form("input")
):
    """Opens the requested directory in the native OS File Explorer (Windows Explorer)."""
    import sys
    import subprocess

    if folder_path and folder_path.strip():
        target = folder_path.strip()
    elif folder_type == "output":
        target = global_folder_watcher.output_dir or "watch_output"
    else:
        target = global_folder_watcher.input_dir or "watch_input"

    abs_path = os.path.abspath(target)
    os.makedirs(abs_path, exist_ok=True)

    try:
        if sys.platform == "win32":
            os.startfile(abs_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", abs_path])
        else:
            subprocess.Popen(["xdg-open", abs_path])
        return {"status": "opened", "path": abs_path}
    except Exception as exc:
        return {"status": "error", "error": str(exc), "path": abs_path}


@router.post("/start")
async def start_watcher_endpoint(
    input_dir: str = Form("watch_input"),
    output_dir: str = Form("watch_output"),
    frontmatter_preset: str = Form("obsidian"),
    chunk_tokens: int = Form(0)
):
    """Starts the background folder watcher."""
    in_path = os.path.abspath(input_dir)
    out_path = os.path.abspath(output_dir)
    return global_folder_watcher.start(
        input_dir=in_path,
        output_dir=out_path,
        frontmatter_preset=frontmatter_preset,
        chunk_tokens=chunk_tokens
    )


@router.post("/stop")
async def stop_watcher_endpoint():
    """Stops the active folder watcher."""
    return global_folder_watcher.stop()


@router.get("/history")
async def get_watcher_history_endpoint():
    """Returns the list of recently processed file events."""
    return {"history": global_folder_watcher.recent_events}


@router.post("/clear-history")
async def clear_watcher_history_endpoint():
    """Clears the watcher event history."""
    global_folder_watcher.clear_history()
    return {"status": "cleared"}

