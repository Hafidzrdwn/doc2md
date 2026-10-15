import io
import zipfile
from core.batch_exporter import create_batch_zip

def test_create_batch_zip_multiple_files_with_chunks():
    sample_items = [
        {
            "filename": "laporan_keuangan.xlsx",
            "markdown": "# Laporan Keuangan\n\nTotal profit: Rp 150.000.000",
            "token_count": 25,
            "char_count": 55,
            "chunks": []
        },
        {
            "filename": "dokumen_panjang.pdf",
            "markdown": "# Dokumen Panjang\n\nBagian satu.\nBagian dua.",
            "token_count": 40,
            "char_count": 80,
            "chunks": [
                "# Dokumen Panjang (Part 1)\n\nBagian satu.",
                "# Dokumen Panjang (Part 2)\n\nBagian dua."
            ]
        }
    ]

    zip_bytes = create_batch_zip(sample_items)
    assert isinstance(zip_bytes, bytes)
    assert len(zip_bytes) > 0

    with zipfile.ZipFile(io.BytesIO(zip_bytes), mode="r") as zf:
        file_list = zf.namelist()
        
        # Verify main markdown files exist
        assert "laporan_keuangan.md" in file_list
        assert "dokumen_panjang.md" in file_list
        
        # Verify chunk files in subfolder exist
        assert "dokumen_panjang_chunks/part_01.md" in file_list
        assert "dokumen_panjang_chunks/part_02.md" in file_list
        
        # Verify manifest file exists
        assert "SUMMARY.md" in file_list
        
        # Verify content
        summary_text = zf.read("SUMMARY.md").decode("utf-8")
        assert "laporan_keuangan.xlsx" in summary_text
        assert "dokumen_panjang.pdf" in summary_text
        assert "**Total Dokumen**: 2 file" in summary_text
