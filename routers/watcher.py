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
    return global_folder_watcher.get_status()


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
