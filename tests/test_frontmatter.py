import io
import pytest
from fastapi.testclient import TestClient
from app import app
from core.frontmatter_formatter import (
    has_frontmatter,
    extract_frontmatter,
    strip_frontmatter,
    build_frontmatter_dict,
    attach_frontmatter,
    SUPPORTED_PRESETS,
)

client = TestClient(app)


def test_has_frontmatter():
    assert not has_frontmatter("")
    assert not has_frontmatter("Just simple text without frontmatter")
    assert not has_frontmatter("# Header 1\nSome paragraph")
    
    valid_fm = "---\ntitle: Test\ntags: [a, b]\n---\n# Content"
    assert has_frontmatter(valid_fm)

    valid_fm_crlf = "---\r\ntitle: Test\r\ntags: [a, b]\r\n---\r\n# Content"
    assert has_frontmatter(valid_fm_crlf)


def test_extract_and_strip_frontmatter():
    sample = """---
title: Catatan Arsitektur
tags:
  - doc2md
  - backend
---

# Isi Dokumen
Ini adalah isi naskah asli."""

    data, body = extract_frontmatter(sample)
    assert data is not None
    assert data["title"] == "Catatan Arsitektur"
    assert data["tags"] == ["doc2md", "backend"]
    assert body.startswith("# Isi Dokumen")

    stripped = strip_frontmatter(sample)
    assert not has_frontmatter(stripped)
    assert stripped.startswith("# Isi Dokumen")

    # When no frontmatter exists
    no_fm_text = "# Header\nParagraph here."
    no_data, no_body = extract_frontmatter(no_fm_text)
    assert no_data is None
    assert no_body == no_fm_text
    assert strip_frontmatter(no_fm_text) == no_fm_text


def test_build_frontmatter_presets():
    # Obsidian preset
    obs = build_frontmatter_dict("Laporan_Keuangan_2024.pdf", token_count=150, char_count=800, preset="obsidian")
    assert obs["title"] == "Laporan Keuangan 2024"
    assert obs["source"] == "Laporan_Keuangan_2024.pdf"
    assert "pdf" in obs["tags"]
    assert "aliases" in obs
    assert obs["tokens"] == 150

    # Notion preset
    notion = build_frontmatter_dict("Rencana_Bisnis.docx", token_count=200, char_count=1200, preset="notion")
    assert notion["Title"] == "Rencana Bisnis"
    assert notion["Source File"] == "Rencana_Bisnis.docx"
    assert notion["Status"] == "Converted"
    assert "Doc2Md" in notion["Tags"]

    # Minimal preset
    mini = build_frontmatter_dict("Draft_Pribadi.txt", token_count=50, char_count=300, preset="minimal")
    assert mini["title"] == "Draft Pribadi"
    assert mini["source"] == "Draft_Pribadi.txt"
    assert "date" in mini
    assert "tags" not in mini


def test_attach_frontmatter_replace_and_none():
    original = "# Judul Awal\nIsi paragraf."
    
    # Preset none should leave content intact
    none_res = attach_frontmatter(original, "doc.md", preset="none")
    assert none_res == original

    # Attach Obsidian frontmatter
    fm_text = attach_frontmatter(original, "catatan_harian.md", token_count=100, preset="obsidian")
    assert has_frontmatter(fm_text)
    assert "title: catatan harian" in fm_text
    assert "# Judul Awal" in fm_text

    # Re-attaching with Notion preset should replace, not duplicate
    re_fm_text = attach_frontmatter(fm_text, "catatan_harian.md", token_count=100, preset="notion")
    assert has_frontmatter(re_fm_text)
    assert "Title: catatan harian" in re_fm_text
    assert "Status: Converted" in re_fm_text
    assert fm_text.count("---") == 2
    assert re_fm_text.count("---") == 2


def test_api_format_frontmatter_endpoint():
    raw_md = "# Analisis Pasar\nData pertumbuhan q3."
    response = client.post(
        "/format-frontmatter",
        data={
            "markdown_text": raw_md,
            "filename": "analisis_pasar.md",
            "preset": "obsidian"
        }
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "markdown" in json_data
    assert has_frontmatter(json_data["markdown"])
    assert "title: analisis pasar" in json_data["markdown"]
    assert json_data["preset"] == "obsidian"


def test_api_convert_with_frontmatter_preset():
    txt_content = b"Dokumen penting tentang strategi ekspansi AI offline."
    files = [("files", ("strategi.txt", io.BytesIO(txt_content), "text/plain"))]
    
    # 1. Convert with frontmatter preset = obsidian
    res = client.post(
        "/convert",
        files=files,
        data={"frontmatter_preset": "obsidian"}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 1
    md_result = data["results"][0]["markdown"]
    assert has_frontmatter(md_result)
    assert "title: strategi" in md_result
    assert "aliases:" in md_result

    # 2. Convert with frontmatter preset = none (default)
    files2 = [("files", ("strategi2.txt", io.BytesIO(txt_content), "text/plain"))]
    res2 = client.post(
        "/convert",
        files=files2,
        data={"frontmatter_preset": "none"}
    )
    assert res2.status_code == 200
    data2 = res2.json()
    md_result2 = data2["results"][0]["markdown"]
    assert not has_frontmatter(md_result2)
