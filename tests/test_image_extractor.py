import io
import tempfile
import os
import zipfile
from PIL import Image
from core.image_extractor import (
    ExtractedImage,
    sanitize_slug,
    extract_document_images,
    append_image_markdown_gallery,
)
from core.converter import convert_file_to_markdown_with_assets

def test_sanitize_slug():
    assert sanitize_slug("Laporan Keuangan 2026!.pdf") == "Laporan_Keuangan_2026"
    assert sanitize_slug("document.test.docx") == "document_test"

def test_extracted_image_dataclass_and_base64():
    raw = b"\x89PNG\r\n\x1a\nfakeimagebytes"
    img = ExtractedImage(
        rel_path="assets/doc_p1_img1.png",
        data=raw,
        format="png",
        width=100,
        height=100,
        page_number=1,
        caption="Test Diagram"
    )
    assert img.rel_path == "assets/doc_p1_img1.png"
    assert img.to_base64().startswith("data:image/png;base64,")
    d = img.to_dict()
    assert d["width"] == 100
    assert d["caption"] == "Test Diagram"

def test_append_image_markdown_gallery():
    img = ExtractedImage(
        rel_path="assets/doc_p1_img1.png",
        data=b"dummy",
        format="png",
        width=200,
        height=100,
        page_number=1,
        caption="Diagram Alur"
    )
    original_md = "# Konten Utama\n\nPenjelasan alur kerja."
    result = append_image_markdown_gallery(original_md, [img], "doc.pdf")
    assert "# Konten Utama" in result
    assert "Galeri Aset Visual & Diagram Dokumen" in result
    assert "![Diagram Alur](assets/doc_p1_img1.png)" in result
    assert "*(200x100 px)*" in result

def test_extract_images_from_standalone_image():
    # Create a small valid test PNG in memory
    buf = io.BytesIO()
    im = Image.new("RGB", (50, 50), color="blue")
    im.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tf.write(png_bytes)
        temp_png = tf.name

    try:
        images = extract_document_images(temp_png, "logo_perusahaan.png")
        assert len(images) == 1
        assert images[0].format == "png"
        assert images[0].width == 50
        assert images[0].height == 50
        assert "assets/logo_perusahaan.png" == images[0].rel_path
    finally:
        if os.path.exists(temp_png):
            os.remove(temp_png)

def test_extract_images_from_docx_container():
    # Build a minimal docx container zip with word/media/image1.png
    buf = io.BytesIO()
    im = Image.new("RGB", (80, 40), color="red")
    im.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    docx_buf = io.BytesIO()
    with zipfile.ZipFile(docx_buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types></Types>")
        zf.writestr("word/media/image1.png", png_bytes)

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
        tf.write(docx_buf.getvalue())
        temp_docx = tf.name

    try:
        images = extract_document_images(temp_docx, "proposal_desain.docx")
        assert len(images) == 1
        assert images[0].width == 80
        assert images[0].height == 40
        assert images[0].rel_path == "assets/proposal_desain_img1.png"
    finally:
        if os.path.exists(temp_docx):
            os.remove(temp_docx)
