"""
Folder Watcher and Auto-Conversion Engine for Doc2MD.
Monitors an input directory using Watchdog, automatically detects newly dropped
documents, converts them to AI-ready Markdown, and saves results with image assets
and optional YAML frontmatter to an output directory.
"""

import os
import time
import uuid
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from core.converter import ALLOWED_EXTENSIONS, convert_file_to_markdown_with_assets
from core.chunker import count_tokens, chunk_by_tokens
from core.frontmatter_formatter import attach_frontmatter
from core.image_extractor import sanitize_slug

logger = logging.getLogger(__name__)


def wait_until_file_ready(file_path: str, timeout: float = 10.0, check_interval: float = 0.5) -> bool:
    """
    Waits until a file has finished being written by the operating system,
    ensuring it is no longer locked by another process.
    """
    start_time = time.time()
    last_size = -1

    while time.time() - start_time < timeout:
        if not os.path.exists(file_path):
            return False
        try:
            curr_size = os.path.getsize(file_path)
            if curr_size > 0 and curr_size == last_size:
                # Test opening file for reading to confirm write lock is released
                with open(file_path, "rb") as f:
                    f.read(min(1024, curr_size))
                return True
            last_size = curr_size
        except (OSError, PermissionError):
            pass
        time.sleep(check_interval)

    # Final check
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "rb") as f:
                f.read(1)
            return True
    except Exception:
        pass

    return False


class DocumentDropHandler(FileSystemEventHandler):
    """Event handler for detecting new or moved documents in the watched directory."""

    def __init__(self, watcher: "FolderWatcher"):
        super().__init__()
        self.watcher = watcher

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self.watcher.enqueue_file(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if not event.is_directory and hasattr(event, "dest_path"):
            self.watcher.enqueue_file(event.dest_path)


class FolderWatcher:
    """
    Thread-safe folder watcher managing background filesystem monitoring
    and automated conversion pipeline.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._observer: Optional[Observer] = None
        self._handler: Optional[DocumentDropHandler] = None
        self._is_active: bool = False

        self.input_dir: str = ""
        self.output_dir: str = ""
        self.frontmatter_preset: str = "obsidian"
        self.chunk_tokens: int = 0

        self.total_processed: int = 0
        self.recent_events: List[Dict[str, Any]] = []
        self._recent_files: Dict[str, float] = {}  # Deduplication tracking

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._is_active and (self._observer is not None and self._observer.is_alive())

    def start(
        self,
        input_dir: str,
        output_dir: str,
        frontmatter_preset: str = "obsidian",
        chunk_tokens: int = 0
    ) -> Dict[str, Any]:
        """Starts monitoring the input folder and writing conversions to the output folder."""
        with self._lock:
            if self._is_active and self._observer and self._observer.is_alive():
                return {
                    "status": "already_running",
                    "input_dir": self.input_dir,
                    "output_dir": self.output_dir
                }

            in_path = os.path.abspath(input_dir)
            out_path = os.path.abspath(output_dir)

            os.makedirs(in_path, exist_ok=True)
            os.makedirs(out_path, exist_ok=True)

            self.input_dir = in_path
            self.output_dir = out_path
            self.frontmatter_preset = frontmatter_preset or "none"
            self.chunk_tokens = chunk_tokens

            self._handler = DocumentDropHandler(self)
            self._observer = Observer()
            self._observer.schedule(self._handler, self.input_dir, recursive=False)
            self._observer.daemon = True
            self._observer.start()
            self._is_active = True

            logger.info(f"FolderWatcher started: watching '{self.input_dir}' -> writing to '{self.output_dir}'")
            return {
                "status": "started",
                "input_dir": self.input_dir,
                "output_dir": self.output_dir,
                "frontmatter_preset": self.frontmatter_preset,
                "chunk_tokens": self.chunk_tokens
            }

    def stop(self) -> Dict[str, Any]:
        """Stops the active folder observer safely."""
        with self._lock:
            if not self._is_active or not self._observer:
                return {"status": "not_running"}

            try:
                self._observer.stop()
                self._observer.join(timeout=2.0)
            except Exception as e:
                logger.warning(f"Error stopping observer: {e}")
            finally:
                self._observer = None
                self._handler = None
                self._is_active = False

            logger.info("FolderWatcher stopped successfully.")
            return {"status": "stopped"}

    def enqueue_file(self, file_path: str) -> None:
        """Processes newly detected file in a separate daemon thread to avoid blocking watchdog."""
        thread = threading.Thread(target=self._process_file_worker, args=(file_path,), daemon=True)
        thread.start()

    def _process_file_worker(self, file_path: str) -> None:
        """Worker thread to handle file debounce, conversion, and logging."""
        norm_path = os.path.normpath(file_path)
        filename = os.path.basename(norm_path)

        # Ignore temporary, hidden, or partial files
        if filename.startswith(("~", ".", "tmp_")) or filename.endswith((".tmp", ".crdownload", ".part")):
            return

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return

        # Debounce: avoid duplicate processing within 3 seconds
        now = time.time()
        with self._lock:
            last_time = self._recent_files.get(norm_path, 0)
            if now - last_time < 3.0:
                return
            self._recent_files[norm_path] = now

        # Wait until file writing has completely stabilized
        if not wait_until_file_ready(norm_path, timeout=8.0):
            logger.warning(f"File did not stabilize in time: {norm_path}")
            return

        self.convert_and_save(norm_path)

    def convert_and_save(self, file_path: str) -> Dict[str, Any]:
        """
        Executes document conversion, asset extraction, frontmatter attachment,
        and saves Markdown output to the designated output folder.
        """
        filename = os.path.basename(file_path)
        doc_slug = sanitize_slug(filename)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event_id = str(uuid.uuid4())[:8]

        try:
            markdown_content, extracted_images = convert_file_to_markdown_with_assets(file_path, filename)

            # Save extracted images to <output_dir>/assets/
            assets_dir = os.path.join(self.output_dir, "assets")
            if extracted_images:
                os.makedirs(assets_dir, exist_ok=True)
                for img in extracted_images:
                    target_img_path = os.path.join(self.output_dir, img.rel_path)
                    os.makedirs(os.path.dirname(target_img_path), exist_ok=True)
                    try:
                        with open(target_img_path, "wb") as f_img:
                            f_img.write(img.data)
                    except Exception as img_err:
                        logger.error(f"Failed to write image {img.rel_path}: {img_err}")

            raw_tokens = count_tokens(markdown_content)

            # Attach frontmatter if preset is enabled
            if self.frontmatter_preset and self.frontmatter_preset.lower() != "none":
                markdown_content = attach_frontmatter(
                    markdown_content,
                    filename=filename,
                    token_count=raw_tokens,
                    char_count=len(markdown_content),
                    preset=self.frontmatter_preset
                )

            final_tokens = count_tokens(markdown_content)

            # Write primary Markdown file to output_dir
            out_md_path = os.path.join(self.output_dir, f"{doc_slug}.md")
            with open(out_md_path, "w", encoding="utf-8") as f_out:
                f_out.write(markdown_content)

            # Optional: handle chunking if enabled
            chunks_created = 0
            if self.chunk_tokens > 0 and final_tokens > self.chunk_tokens:
                chunks = chunk_by_tokens(markdown_content, self.chunk_tokens)
                if len(chunks) > 1:
                    chunks_dir = os.path.join(self.output_dir, f"{doc_slug}_chunks")
                    os.makedirs(chunks_dir, exist_ok=True)
                    chunks_created = len(chunks)
                    for c_idx, chunk_text in enumerate(chunks, 1):
                        c_path = os.path.join(chunks_dir, f"part_{c_idx:02d}.md")
                        with open(c_path, "w", encoding="utf-8") as f_c:
                            f_c.write(chunk_text)

            event = {
                "id": event_id,
                "filename": filename,
                "input_path": file_path,
                "output_path": out_md_path,
                "timestamp": timestamp,
                "status": "success",
                "token_count": final_tokens,
                "char_count": len(markdown_content),
                "images_count": len(extracted_images),
                "chunks_count": chunks_created,
                "error": None
            }

            with self._lock:
                self.total_processed += 1
                self.recent_events.insert(0, event)
                if len(self.recent_events) > 50:
                    self.recent_events.pop()

            logger.info(f"Auto-converted: {filename} -> {out_md_path} ({final_tokens} tokens)")
            return event

        except Exception as exc:
            logger.error(f"Auto-conversion failed for {filename}: {exc}", exc_info=True)
            event = {
                "id": event_id,
                "filename": filename,
                "input_path": file_path,
                "output_path": None,
                "timestamp": timestamp,
                "status": "error",
                "token_count": 0,
                "char_count": 0,
                "images_count": 0,
                "chunks_count": 0,
                "error": str(exc)
            }
            with self._lock:
                self.recent_events.insert(0, event)
                if len(self.recent_events) > 50:
                    self.recent_events.pop()
            return event

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state and settings of the folder watcher."""
        with self._lock:
            active = self._is_active and (self._observer is not None and self._observer.is_alive())
            return {
                "is_active": active,
                "input_dir": self.input_dir,
                "output_dir": self.output_dir,
                "frontmatter_preset": self.frontmatter_preset,
                "chunk_tokens": self.chunk_tokens,
                "total_processed": self.total_processed,
                "recent_events": list(self.recent_events)
            }

    def clear_history(self) -> None:
        """Clears the in-memory conversion event history."""
        with self._lock:
            self.recent_events.clear()


# Global singleton instance for application lifetime
global_folder_watcher = FolderWatcher()
