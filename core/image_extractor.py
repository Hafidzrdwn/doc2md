import io
import os
import re
import zipfile
import base64
import logging
from dataclasses import dataclass
from typing import List, Optional
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class ExtractedImage:
    rel_path: str          # e.g., "assets/doc_p1_img1.png"
    data: bytes            # raw image bytes
    format: str            # "png", "jpeg", etc.
    width: int = 0
    height: int = 0
    page_number: int = 1
    caption: str = ""

    def to_base64(self) -> str:
        """Returns image as base64 data URL for preview in browser."""
        mime = f"image/{self.format.lower()}"
        b64 = base64.b64encode(self.data).decode("ascii")
        return f"data:{mime};base64,{b64}"

    def to_dict(self) -> dict:
        return {
            "path": self.rel_path,
            "format": self.format,
            "width": self.width,
            "height": self.height,
            "page_number": self.page_number,
            "caption": self.caption,
            "base64": self.to_base64(),
        }

def sanitize_slug(name: str) -> str:
    """Create a safe alphanumeric filename slug."""
    stem = os.path.splitext(os.path.basename(name))[0]
    cleaned = re.sub(r'[^a-zA-Z0-9_\-]', '_', stem)
    return cleaned.strip('_') or "doc"

def extract_images_from_pdf(file_path: str, doc_slug: str) -> List[ExtractedImage]:
    """Extract embedded images from PDF pages using pypdfium2."""
    images: List[ExtractedImage] = []
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(file_path)

        for page_idx, page in enumerate(pdf, 1):
            img_in_page = 0
            for obj in page.get_objects():
                # Check if object is an image
                if getattr(obj, "type", None) == pdfium.raw.FPDF_PAGEOBJ_IMAGE:
                    img_in_page += 1
                    try:
                        bmp = obj.get_bitmap()
                        pil_img = bmp.to_pil()
                        
                        # Filter out microscopic 1x1 spacer images or tiny icons
                        if pil_img.width < 16 or pil_img.height < 16:
                            continue

                        buf = io.BytesIO()
                        # Save in PNG for lossless diagrams
                        pil_img.save(buf, format="PNG", optimize=True)
                        img_bytes = buf.getvalue()

                        rel_name = f"assets/{doc_slug}_p{page_idx}_img{img_in_page}.png"
                        caption = f"Diagram/Gambar Terdeteksi (Halaman {page_idx}, #{img_in_page})"

                        images.append(ExtractedImage(
                            rel_path=rel_name,
                            data=img_bytes,
                            format="png",
                            width=pil_img.width,
                            height=pil_img.height,
                            page_number=page_idx,
                            caption=caption
                        ))
                    except Exception as e:
                        logger.warning(f"Gagal mengekstrak objek gambar PDF p{page_idx} #{img_in_page}: {e}")
        pdf.close()
    except Exception as exc:
        logger.error(f"Gagal memproses gambar PDF {file_path}: {exc}")

    return images

def extract_images_from_office_archive(file_path: str, doc_slug: str, media_prefix: str = "word/media/") -> List[ExtractedImage]:
    """Extract media assets from docx, pptx, or xlsx zip containers."""
    images: List[ExtractedImage] = []
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            media_files = [f for f in zf.namelist() if f.startswith(media_prefix)]
            for idx, m_path in enumerate(media_files, 1):
                try:
                    data = zf.read(m_path)
                    ext = os.path.splitext(m_path)[1].lower().strip(".") or "png"
                    
                    # Try to inspect dimension with Pillow
                    width, height = 0, 0
                    try:
                        with Image.open(io.BytesIO(data)) as pil_img:
                            width, height = pil_img.size
                            if width < 16 or height < 16:
                                continue
                    except Exception:
                        pass

                    rel_name = f"assets/{doc_slug}_img{idx}.{ext}"
                    caption = f"Aset Gambar Dokumen #{idx} ({ext.upper()})"

                    images.append(ExtractedImage(
                        rel_path=rel_name,
                        data=data,
                        format=ext,
                        width=width,
                        height=height,
                        page_number=1,
                        caption=caption
                    ))
                except Exception as e:
                    logger.warning(f"Gagal membaca aset media {m_path}: {e}")
    except Exception as exc:
        logger.error(f"Gagal membaca zip office container {file_path}: {exc}")

    return images

def extract_images_from_standalone_image(file_path: str, original_filename: str) -> List[ExtractedImage]:
    """Preserves uploaded standalone image files as an asset."""
    images: List[ExtractedImage] = []
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        doc_slug = sanitize_slug(original_filename)
        ext = os.path.splitext(original_filename)[1].lower().strip(".") or "png"
        width, height = 0, 0
        try:
            with Image.open(io.BytesIO(data)) as pil_img:
                width, height = pil_img.size
        except Exception:
            pass

        rel_name = f"assets/{doc_slug}.{ext}"
        images.append(ExtractedImage(
            rel_path=rel_name,
            data=data,
            format=ext,
            width=width,
            height=height,
            page_number=1,
            caption=f"Berkas Gambar Asli: {original_filename}"
        ))
    except Exception as exc:
        logger.error(f"Gagal membaca file gambar {file_path}: {exc}")

    return images

def extract_document_images(file_path: str, original_filename: str) -> List[ExtractedImage]:
    """Dispatches extraction based on file format."""
    ext = os.path.splitext(original_filename)[1].lower()
    doc_slug = sanitize_slug(original_filename)

    if ext == ".pdf":
        return extract_images_from_pdf(file_path, doc_slug)
    elif ext == ".docx":
        return extract_images_from_office_archive(file_path, doc_slug, media_prefix="word/media/")
    elif ext == ".pptx":
        return extract_images_from_office_archive(file_path, doc_slug, media_prefix="ppt/media/")
    elif ext in {".xlsx", ".xls"}:
        return extract_images_from_office_archive(file_path, doc_slug, media_prefix="xl/media/")
    elif ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        return extract_images_from_standalone_image(file_path, original_filename)

    return []

def append_image_markdown_gallery(markdown_text: str, images: List[ExtractedImage], original_filename: str) -> str:
    """
    Appends an interactive Markdown gallery linking to extracted image assets.
    Ensures complete visual context for both LLM models and markdown viewers.
    """
    if not images:
        return markdown_text

    gallery_lines = [
        "",
        "---",
        "",
        f"### 🖼️ Galeri Aset Visual & Diagram Dokumen ({len(images)} Terdeteksi)",
        "> Seluruh diagram dan gambar di bawah telah diekstrak secara otomatis ke folder aset lokal (`assets/`).",
        "",
    ]

    for img in images:
        dim_str = f" *({img.width}x{img.height} px)*" if img.width and img.height else ""
        gallery_lines.append(f"#### 📌 {img.caption}{dim_str}")
        gallery_lines.append(f"![{img.caption}]({img.rel_path})")
        gallery_lines.append("")

    return markdown_text + "\n" + "\n".join(gallery_lines)
