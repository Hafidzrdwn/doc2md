import pytest
from fastapi.testclient import TestClient

from app import app
from core.themes import THEMES, DEFAULT_THEME_ID, get_theme, list_themes
from core.docx_generator import markdown_to_docx_bytes
from core.pdf_generator import markdown_to_html_document, get_print_css


@pytest.fixture
def client():
    return TestClient(app)


def test_theme_configs():
    assert len(THEMES) >= 4
    for theme_id in ["modern_slate", "corporate_navy", "classic_academic", "emerald_tech"]:
        assert theme_id in THEMES
        cfg = THEMES[theme_id]
        assert cfg.primary_color.startswith("#")
        assert len(cfg.rgb_primary) == 3
        assert cfg.docx_heading_font
        assert cfg.docx_body_font


def test_get_theme_fallback():
    assert get_theme(None).id == DEFAULT_THEME_ID
    assert get_theme("").id == DEFAULT_THEME_ID
    assert get_theme("non_existent_theme_xyz").id == DEFAULT_THEME_ID
    assert get_theme("corporate_navy").id == "corporate_navy"
    assert get_theme("EMERALD_TECH").id == "emerald_tech"


def test_list_themes():
    themes = list_themes()
    assert len(themes) == len(THEMES)
    ids = [t["id"] for t in themes]
    assert "modern_slate" in ids
    assert "corporate_navy" in ids
    assert "classic_academic" in ids
    assert "emerald_tech" in ids


def test_docx_generation_with_themes():
    md = "# Judul Dokumen\n\n| Kolom A | Kolom B |\n|---|---|\n| Nilai 1 | Nilai 2 |\n\n> Kutipan catatan\n\n```python\nprint('hello')\n```"
    for theme_id in THEMES.keys():
        docx_bytes = markdown_to_docx_bytes(md, theme=theme_id)
        assert isinstance(docx_bytes, bytes)
        assert len(docx_bytes) > 1000


def test_html_generation_with_themes():
    md = "# Laporan Strategis\n\nParagraf konten teks penting."
    for theme_id, cfg in THEMES.items():
        html_doc = markdown_to_html_document(md, title="Laporan", theme=theme_id)
        assert cfg.name in html_doc
        assert cfg.primary_color in html_doc


def test_api_get_themes(client):
    res = client.get("/themes")
    assert res.status_code == 200
    data = res.json()
    assert "themes" in data
    assert len(data["themes"]) >= 4


def test_api_md_to_docx_with_theme(client):
    res = client.post(
        "/md-to-docx",
        data={
            "markdown_text": "# Halo Dunia\n\nIni teks pengujian.",
            "filename": "test_theme",
            "theme": "corporate_navy"
        }
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert len(res.content) > 1000


def test_api_md_to_html_with_theme(client):
    res = client.post(
        "/md-to-html",
        data={
            "markdown_text": "# Dokumen Akademik",
            "filename": "tes_akademik",
            "theme": "classic_academic"
        }
    )
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Classic Academic" in res.text
