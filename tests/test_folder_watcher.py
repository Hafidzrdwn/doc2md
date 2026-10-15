import os
import time
import shutil
import tempfile
import pytest
from fastapi.testclient import TestClient

from app import app
from core.folder_watcher import FolderWatcher, wait_until_file_ready

client = TestClient(app)


@pytest.fixture
def temp_dirs():
    base_tmp = tempfile.mkdtemp(prefix="doc2md_test_watcher_")
    in_dir = os.path.join(base_tmp, "input")
    out_dir = os.path.join(base_tmp, "output")
    yield in_dir, out_dir
    if os.path.exists(base_tmp):
        try:
            shutil.rmtree(base_tmp, ignore_errors=True)
        except Exception:
            pass


def test_watcher_lifecycle(temp_dirs):
    in_dir, out_dir = temp_dirs
    watcher = FolderWatcher()

    assert not watcher.is_active

    # Start watcher
    res = watcher.start(input_dir=in_dir, output_dir=out_dir, frontmatter_preset="obsidian")
    assert res["status"] == "started"
    assert watcher.is_active
    assert os.path.exists(in_dir)
    assert os.path.exists(out_dir)

    # Idempotent start
    dup_res = watcher.start(input_dir=in_dir, output_dir=out_dir)
    assert dup_res["status"] == "already_running"

    # Stop watcher
    stop_res = watcher.stop()
    assert stop_res["status"] == "stopped"
    assert not watcher.is_active

    # Idempotent stop
    stop_dup = watcher.stop()
    assert stop_dup["status"] == "not_running"


def test_convert_and_save_direct(temp_dirs):
    in_dir, out_dir = temp_dirs
    watcher = FolderWatcher()
    watcher.start(input_dir=in_dir, output_dir=out_dir, frontmatter_preset="obsidian")

    try:
        sample_file = os.path.join(in_dir, "laporan_analisis.txt")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("Laporan mingguan sistem AI offline Doc2MD.")

        event = watcher.convert_and_save(sample_file)
        assert event["status"] == "success"
        assert event["token_count"] > 0
        assert event["filename"] == "laporan_analisis.txt"
        assert os.path.exists(event["output_path"])

        # Check output content
        with open(event["output_path"], "r", encoding="utf-8") as f:
            content = f.read()

        assert content.startswith("---")
        assert "title: laporan analisis" in content
        assert "Doc2MD" in content

        # Check history
        status = watcher.get_status()
        assert status["total_processed"] == 1
        assert len(status["recent_events"]) == 1

        watcher.clear_history()
        assert len(watcher.get_status()["recent_events"]) == 0

    finally:
        watcher.stop()


def test_watcher_auto_detection_event(temp_dirs):
    in_dir, out_dir = temp_dirs
    watcher = FolderWatcher()
    watcher.start(input_dir=in_dir, output_dir=out_dir, frontmatter_preset="minimal")

    try:
        target_file = os.path.join(in_dir, "auto_drop_doc.txt")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("Konten dokumen otomatis terdeteksi via Watchdog filesystem event.")

        # Allow watchdog thread to detect and process the file
        expected_out = os.path.join(out_dir, "auto_drop_doc.md")
        success = False
        for _ in range(40):  # poll up to 4 seconds
            if os.path.exists(expected_out):
                success = True
                break
            time.sleep(0.1)

        assert success, f"File {expected_out} was not generated within timeout."

        with open(expected_out, "r", encoding="utf-8") as f:
            output_content = f.read()

        assert "auto drop doc" in output_content
        assert "Konten dokumen otomatis" in output_content

    finally:
        watcher.stop()


def test_api_watcher_endpoints(temp_dirs):
    in_dir, out_dir = temp_dirs

    # 1. Check initial status
    res = client.get("/watcher/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_active" in data
    assert "recent_events" in data

    # 2. Start watcher via API
    start_res = client.post(
        "/watcher/start",
        data={
            "input_dir": in_dir,
            "output_dir": out_dir,
            "frontmatter_preset": "notion",
            "chunk_tokens": "0"
        }
    )
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert start_data["status"] in ("started", "already_running")

    # 3. Check status is active
    status_res = client.get("/watcher/status")
    assert status_res.status_code == 200
    assert status_res.json()["is_active"] is True

    # 4. Check history endpoint
    hist_res = client.get("/watcher/history")
    assert hist_res.status_code == 200
    assert "history" in hist_res.json()

    # 5. Clear history endpoint
    clear_res = client.post("/watcher/clear-history")
    assert clear_res.status_code == 200
    assert clear_res.json()["status"] == "cleared"

    # 6. Stop watcher via API
    stop_res = client.post("/watcher/stop")
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] in ("stopped", "not_running")

    # Verify stopped
    final_status = client.get("/watcher/status")
    assert final_status.json()["is_active"] is False
