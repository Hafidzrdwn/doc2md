import pytest
from core.pdf_generator import (
    find_chromium_executable,
    markdown_to_html_document,
    markdown_to_pdf_bytes,
)

def test_find_chromium_executable():
    exe = find_chromium_executable()
    assert exe is not None
    assert ("edge" in exe.lower() or "chrome" in exe.lower() or "chromium" in exe.lower())

def test_markdown_to_html_document():
    md = """# Judul Laporan
Ini adalah pengantar dokumen.

| No | Komponen | Status |
|---|---|---|
| 1 | Database | Siap |
| 2 | Backend API | Berjalan |

```python
def check_status():
    return True
```
"""
    html = markdown_to_html_document(md, title="Laporan Status")
    assert "<!DOCTYPE html>" in html
    assert "Laporan Status" in html
    assert "<table" in html
    assert "codehilite" in html or "<code" in html
    assert "break-inside: avoid" in html
    assert "break-after: avoid" in html

def test_markdown_to_pdf_bytes():
    md = """# Ringkasan Eksekutif
Dokumen ini menguji konversi Markdown ke PDF dengan tata letak rapi dan pencegahan pemotongan baris/tabel.

## Tabel Evaluasi
| Metrik | Kuartal 1 | Kuartal 2 |
|---|---|---|
| Performa | 98.4% | 99.1% |
| Efisiensi | 92.0% | 95.5% |

> **Catatan Penting**: Sistem bekerja dengan baik tanpa error.
"""
    pdf_bytes = markdown_to_pdf_bytes(md, title="Evaluasi Performa")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF magic header
    assert pdf_bytes.startswith(b"%PDF")
