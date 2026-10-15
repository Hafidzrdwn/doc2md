import io
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Doc2Markdown" in response.text

def test_convert_txt_file():
    file_content = b"Baris pertama teks pengujian.\nBaris kedua pengujian."
    response = client.post(
        "/convert",
        files={"files": ("test.txt", file_content, "text/plain")},
        data={"chunk_tokens": 0}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    res = data["results"][0]
    assert res["status"] == "success"
    assert res["filename"] == "test.txt"
    assert "Baris pertama" in res["markdown"]
    assert res["token_count"] > 0

def test_convert_unsupported_extension():
    response = client.post(
        "/convert",
        files={"files": ("script.exe", b"invalid executable", "application/octet-stream")},
        data={"chunk_tokens": 0}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["status"] == "error"
    assert "tidak didukung" in data["results"][0]["error"]

def test_md_to_docx_endpoint():
    markdown_sample = "# Header Pengujian\n\nTeks konten pengujian konversi Word."
    response = client.post(
        "/md-to-docx",
        data={"markdown_text": markdown_sample, "filename": "hasil_uji"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert "attachment; filename=\"hasil_uji.docx\"" in response.headers["content-disposition"]
    assert len(response.content) > 0

def test_md_to_pdf_endpoint():
    markdown_sample = "# Header PDF Pengujian\n\nTeks konten pengujian konversi PDF."
    response = client.post(
        "/md-to-pdf",
        data={"markdown_text": markdown_sample, "filename": "hasil_uji_pdf"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=\"hasil_uji_pdf.pdf\"" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")

def test_md_to_html_endpoint():
    markdown_sample = "# Header HTML Pengujian\n\nTeks konten pengujian konversi HTML."
    # 1. Preview mode
    response = client.post(
        "/md-to-html",
        data={"markdown_text": markdown_sample, "filename": "hasil_uji_html", "download": False}
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<!DOCTYPE html>" in response.text
    assert "Header HTML Pengujian" in response.text

    # 2. Download mode
    response_dl = client.post(
        "/md-to-html",
        data={"markdown_text": markdown_sample, "filename": "hasil_uji_html", "download": True}
    )
    assert response_dl.status_code == 200
    assert "attachment; filename=\"hasil_uji_html.html\"" in response_dl.headers["content-disposition"]
