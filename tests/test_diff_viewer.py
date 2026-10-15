import io
import pytest
from fastapi.testclient import TestClient
from app import app
from core.diff_viewer import compute_document_diff

client = TestClient(app)


def test_compute_document_diff_identical():
    text = "# Pendahuluan\nIni adalah teks dokumen asli.\nSelesai."
    res = compute_document_diff(text, text, title_a="V1", title_b="V2")

    assert res["similarity_ratio"] == 100.0
    stats = res["stats"]
    assert stats["delta_tokens"] == 0
    assert stats["delta_chars"] == 0
    assert stats["added_lines"] == 0
    assert stats["removed_lines"] == 0
    assert stats["modified_lines"] == 0
    assert stats["unchanged_lines"] == 3
    assert stats["total_lines_a"] == 3
    assert stats["total_lines_b"] == 3

    assert len(res["side_by_side"]) == 3
    for row in res["side_by_side"]:
        assert row["type"] == "equal"
        assert row["left"]["text"] == row["right"]["text"]

    assert len(res["unified"]) == 3
    for row in res["unified"]:
        assert row["type"] == "equal"


def test_compute_document_diff_insertions_and_deletions():
    text_a = "Baris 1\nBaris 2\nBaris 3"
    text_b = "Baris 1\nBaris Tambahan\nBaris 3\nBaris Akhir"

    res = compute_document_diff(text_a, text_b)
    stats = res["stats"]

    assert res["similarity_ratio"] < 100.0
    assert stats["unchanged_lines"] == 2  # Baris 1 and Baris 3
    assert stats["added_lines"] > 0
    assert len(res["side_by_side"]) >= 3
    assert len(res["unified"]) >= 3


def test_compute_document_diff_modifications():
    text_a = "Sistem Arsitektur V1: Python FastAPI"
    text_b = "Sistem Arsitektur V2: Python FastAPI + RapidOCR + Chromium"

    res = compute_document_diff(text_a, text_b)
    stats = res["stats"]

    assert stats["delta_chars"] > 0
    assert stats["delta_tokens"] > 0
    assert stats["modified_lines"] >= 1


def test_compute_document_diff_empty_inputs():
    res = compute_document_diff("", "")
    assert res["similarity_ratio"] == 100.0
    assert res["stats"]["tokens_a"] == 0
    assert res["stats"]["tokens_b"] == 0
    assert res["stats"]["total_lines_a"] == 0
    assert res["stats"]["total_lines_b"] == 0
    assert len(res["side_by_side"]) == 0
    assert len(res["unified"]) == 0


def test_api_diff_endpoint():
    payload = {
        "text_a": "# Judul Dokumen\nParagraf pertama versi 1.",
        "text_b": "# Judul Dokumen\nParagraf pertama versi 2 yang diperbarui.",
        "title_a": "Draft 1",
        "title_b": "Draft 2",
    }
    response = client.post("/diff", data=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["title_a"] == "Draft 1"
    assert data["title_b"] == "Draft 2"
    assert "similarity_ratio" in data
    assert "stats" in data
    assert "side_by_side" in data
    assert "unified" in data
    assert data["stats"]["delta_chars"] > 0


def test_api_diff_files_endpoint():
    file_a_content = b"# Laporan Q1\nTarget penjualan 100 unit."
    file_b_content = b"# Laporan Q1\nTarget penjualan 150 unit revisi."

    files = {
        "file_a": ("laporan_v1.txt", io.BytesIO(file_a_content), "text/plain"),
        "file_b": ("laporan_v2.txt", io.BytesIO(file_b_content), "text/plain"),
    }
    response = client.post("/diff/files", files=files)
    assert response.status_code == 200

    data = response.json()
    assert data["title_a"] == "laporan_v1.txt"
    assert data["title_b"] == "laporan_v2.txt"
    assert "similarity_ratio" in data
    assert len(data["side_by_side"]) > 0


def test_api_diff_files_unsupported_extension():
    files = {
        "file_a": ("doc.bin", io.BytesIO(b"dummy binary"), "application/octet-stream"),
        "file_b": ("laporan_v2.txt", io.BytesIO(b"plain text"), "text/plain"),
    }
    response = client.post("/diff/files", files=files)
    assert response.status_code == 400
    assert "tidak didukung" in response.text
