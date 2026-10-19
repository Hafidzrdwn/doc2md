import io
import tempfile
import openpyxl
from fastapi.testclient import TestClient
from app import app
from core.converter import (
    inspect_excel_sheets,
    excel_to_markdown,
    structure_markdown_text,
    convert_file_to_markdown,
)

client = TestClient(app)

def create_sample_excel():
    wb = openpyxl.Workbook()
    # Sheet 1: Data Utama
    ws1 = wb.active
    ws1.title = "Data Penjualan"
    ws1.append(["Bulan", "Target", "Realisasi"])
    ws1.append(["Januari", 1000, 1200])
    ws1.append(["Februari", 1500, 1400])

    # Sheet 2: Ringkasan
    ws2 = wb.create_sheet(title="Ringkasan")
    ws2.append(["Kategori", "Total"])
    ws2.append(["Produk A", 5000])
    ws2.append(["Produk B", 7500])

    buf = io.BytesIO()
    wb.save(buf)
    wb.close()
    buf.seek(0)
    return buf

def test_inspect_excel_sheets():
    buf = create_sample_excel()
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        tf.write(buf.getvalue())
        tf_path = tf.name

    sheets = inspect_excel_sheets(tf_path)
    assert len(sheets) == 2
    assert sheets[0]["name"] == "Data Penjualan"
    assert sheets[0]["index"] == 0
    assert sheets[0]["max_row"] >= 3
    assert sheets[1]["name"] == "Ringkasan"
    assert sheets[1]["index"] == 1

def test_excel_to_markdown_all_sheets():
    buf = create_sample_excel()
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        tf.write(buf.getvalue())
        tf_path = tf.name

    md = excel_to_markdown(tf_path, selected_sheets="all")
    assert "## Sheet: Data Penjualan" in md
    assert "## Sheet: Ringkasan" in md
    assert "| Bulan | Target | Realisasi |" in md
    assert "| Kategori | Total |" in md

def test_excel_to_markdown_single_selected_sheet():
    buf = create_sample_excel()
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
        tf.write(buf.getvalue())
        tf_path = tf.name

    md = excel_to_markdown(tf_path, selected_sheets=["Ringkasan"])
    assert "## Sheet: Ringkasan" in md
    assert "## Sheet: Data Penjualan" not in md
    assert "| Kategori | Total |" in md
    assert "Produk A" in md

def test_structure_markdown_text_headings_and_sections():
    raw_text = (
        "BAB I PENDAHULUAN\n"
        "1.1 Latar Belakang Masalah\n"
        "Dokumen ini membahas arsitektur konversi.\n"
        "1.1.1 Ruang Lingkup\n"
        "Lingkup pengujian mencakup semua format.\n"
        "KESIMPULAN\n"
        "Semua fitur berfungsi dengan baik.\n"
    )
    structured = structure_markdown_text(raw_text, "dokumen.pdf")
    assert "# BAB I: PENDAHULUAN" in structured
    assert "## 1.1 Latar Belakang Masalah" in structured
    assert "### 1.1.1 Ruang Lingkup" in structured
    assert "## Kesimpulan" in structured

def test_structure_markdown_text_code_and_bullets():
    raw_text = (
        "Berikut adalah kode sumber yang digunakan:\n"
        "def hitung_total(a, b):\n"
        "    return a + b\n\n"
        "Daftar catatan penting:\n"
        "• Poin pertama harus dicek\n"
        "• Poin kedua selesai\n"
    )
    structured = structure_markdown_text(raw_text, "skrip.py")
    assert "```python" in structured
    assert "def hitung_total(a, b):" in structured
    assert "```" in structured
    assert "- Poin pertama harus dicek" in structured
    assert "- Poin kedua selesai" in structured

def test_inspect_excel_sheets_api():
    buf = create_sample_excel()
    files = {"file": ("laporan_keuangan.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = client.post("/inspect-excel-sheets", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["sheet_count"] == 2
    assert data["sheets"][0]["name"] == "Data Penjualan"
    assert data["sheets"][1]["name"] == "Ringkasan"

def test_convert_excel_with_sheet_selection_api():
    buf = create_sample_excel()
    files = [("files", ("laporan_keuangan.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))]
    
    # 1. Convert with selected sheet: "Ringkasan"
    response = client.post(
        "/convert",
        files=files,
        data={"selected_sheets": '["Ringkasan"]', "chunk_tokens": "0", "frontmatter_preset": "none"}
    )
    assert response.status_code == 200
    res_data = response.json()["results"][0]
    assert res_data["status"] == "success"
    assert "## Sheet: Ringkasan" in res_data["markdown"]
    assert "## Sheet: Data Penjualan" not in res_data["markdown"]
    assert res_data["selected_sheets"] == ["Ringkasan"]

    # 2. Convert with "all" sheets
    buf.seek(0)
    files_all = [("files", ("laporan_keuangan.xlsx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))]
    response_all = client.post(
        "/convert",
        files=files_all,
        data={"selected_sheets": "all", "chunk_tokens": "0", "frontmatter_preset": "none"}
    )
    assert response_all.status_code == 200
    res_all_data = response_all.json()["results"][0]
    assert "## Sheet: Data Penjualan" in res_all_data["markdown"]
    assert "## Sheet: Ringkasan" in res_all_data["markdown"]
