import os
import tempfile
import pytest
import numpy as np
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from app import app
from core.ocr_engine import (
    is_ocr_available,
    extract_text_from_image,
    extract_text_from_image_array,
    ocr_image_file_to_markdown,
    ocr_scanned_pdf,
)
from core.converter import convert_file_to_markdown_with_assets


@pytest.fixture
def client():
    return TestClient(app)


def create_test_image(text: str = "INVOICE DOC2MD 2026") -> Image.Image:
    """Generates a clean synthetic RGB image with text."""
    img = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((25, 35), text, fill="black")
    return img


def test_ocr_availability():
    assert is_ocr_available() is True


def test_extract_text_from_image():
    img = create_test_image("DOC2MD OCR PASS")
    arr = np.array(img)
    text, score = extract_text_from_image_array(arr)
    assert "DOC2MD" in text or "OCR" in text or "PASS" in text
    assert score > 0.0


def test_ocr_image_file_to_markdown():
    img = create_test_image("KWITANSI PEMBAYARAN")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        img.save(tf.name)
        temp_path = tf.name

    try:
        md = ocr_image_file_to_markdown(temp_path, "kwitansi.png")
        assert "Hasil Ekstraksi OCR: kwitansi.png" in md
        assert "Akurasi Deteksi" in md
        assert len(md) > 50
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_convert_file_to_markdown_with_image_ocr():
    img = create_test_image("LAPORAN AUDIT SISTEM")
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
        img.save(tf.name, format="JPEG")
        temp_path = tf.name

    try:
        md, images = convert_file_to_markdown_with_assets(temp_path, "audit_scan.jpg")
        assert "Hasil Ekstraksi OCR: audit_scan.jpg" in md
        assert "LAPORAN" in md or "AUDIT" in md or "SISTEM" in md
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_scanned_pdf_ocr():
    """Generates a PDF where the page only has an image with text and no text layer."""
    import pypdfium2 as pdfium
    img = create_test_image("SCAN PDF DOKUMEN 12345")
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf_pdf:
        pdf_path = tf_pdf.name

    try:
        # Save image directly as a raster PDF page without text layer
        img.save(pdf_path, "PDF")

        ocr_result = ocr_scanned_pdf(pdf_path, min_chars_per_page=20)
        assert ocr_result is not None
        assert "Dokumen PDF Scan Terdeteksi" in ocr_result
        assert "Halaman 1 (Hasil OCR Scan)" in ocr_result
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def test_api_ocr_status_endpoint(client):
    res = client.get("/ocr-status")
    assert res.status_code == 200
    data = res.json()
    assert data["available"] is True
    assert "RapidOCR" in data["engine"]


def test_api_convert_image_with_ocr(client):
    img = create_test_image("TAGIHAN BULANAN OK")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        img.save(tf.name)
        temp_path = tf.name

    try:
        with open(temp_path, "rb") as f:
            res = client.post(
                "/convert",
                files={"files": ("tagihan.png", f, "image/png")}
            )
        assert res.status_code == 200
        data = res.json()
        assert "results" in data
        assert len(data["results"]) == 1
        item = data["results"][0]
        assert item["status"] == "success"
        assert item["is_ocr"] is True
        assert "Hasil Ekstraksi OCR" in item["markdown"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
