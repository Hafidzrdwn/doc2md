import io
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Doc2Markdown" in response.text
    assert "/static/css/style.css" in response.text
    assert "/static/js/main.js" in response.text
    assert "/static/js/common.js" in response.text

def test_static_files():
    css_res = client.get("/static/css/style.css")
    assert css_res.status_code == 200
    assert "Plus Jakarta Sans" in css_res.text

    main_res = client.get("/static/js/main.js")
    assert main_res.status_code == 200
    assert "tabModeDoc2Md" in main_res.text

    common_res = client.get("/static/js/common.js")
    assert common_res.status_code == 200
    assert "uploadedFiles" in common_res.text

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

def test_download_batch_zip_endpoint():
    items = [
        {"filename": "doc1.txt", "markdown": "# Doc 1", "token_count": 10, "char_count": 10},
        {"filename": "doc2.pdf", "markdown": "# Doc 2", "token_count": 20, "char_count": 20}
    ]
    response = client.post(
        "/download-batch-zip",
        json={"items": items}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "attachment; filename=\"doc2md_batch_" in response.headers["content-disposition"]
    assert len(response.content) > 0


def test_batch_md_to_docx_zip_endpoint():
    items = [
        {"filename": "bab1.md", "markdown": "# Bab 1\nPendahuluan", "theme": "modern_slate"},
        {"filename": "bab2.md", "markdown": "# Bab 2\nMetode Penelitian", "theme": "modern_slate"}
    ]
    response = client.post(
        "/batch-md-to-docx-zip",
        json={"items": items}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "attachment; filename=\"batch_docx_" in response.headers["content-disposition"]
    assert len(response.content) > 0

