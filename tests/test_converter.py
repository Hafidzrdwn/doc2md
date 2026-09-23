from core.converter import (
    ALLOWED_EXTENSIONS,
    IMAGE_EXTENSIONS,
    clean_markdown_for_ai,
    annotate_pdf_images,
)

def test_allowed_extensions_contain_primary_formats():
    essential = {".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".csv", ".png", ".jpg"}
    assert essential.issubset(ALLOWED_EXTENSIONS)

def test_clean_markdown_for_ai():
    raw_dirty = "Judul   \n\n\n\nIsi paragraf \u200B\uFEFFdengan spasi liar   \n"
    cleaned = clean_markdown_for_ai(raw_dirty)
    assert "\u200B" not in cleaned
    assert "\uFEFF" not in cleaned
    assert "\n\n\n" not in cleaned
    assert cleaned == "Judul\n\nIsi paragraf dengan spasi liar"

def test_annotate_pdf_images_no_crash_on_missing_file():
    # Should safely return fallback text without raising unhandled exception
    res = annotate_pdf_images("non_existent_file.pdf", "Original Markdown")
    assert res == "Original Markdown"
