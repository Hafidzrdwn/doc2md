import io
import re
import zipfile
import json
from datetime import datetime
from typing import List, Dict, Any

def create_batch_zip(items: List[Dict[str, Any]], archive_title: str = "doc2md_batch_export") -> bytes:
    """
    Creates an in-memory ZIP archive bundling all converted documents,
    their token chunks (if any), and an informative SUMMARY.md manifest.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        summary_rows = []
        total_tokens = 0
        total_chars = 0
        file_count = 0

        for idx, item in enumerate(items, 1):
            raw_filename = item.get("filename", f"dokumen_{idx}")
            base_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_filename.rsplit('.', 1)[0]) or f"dokumen_{idx}"
            markdown_text = item.get("markdown", "")
            tokens = item.get("token_count", 0)
            chars = item.get("char_count", len(markdown_text))
            chunks = item.get("chunks", []) or []

            total_tokens += tokens
            total_chars += chars
            file_count += 1

            # 1. Write the main Markdown document
            md_entry_name = f"{base_name}.md"
            zf.writestr(md_entry_name, markdown_text)

            # 2. Write individual chunks if the document was split
            chunk_info = "Tidak ada (dokumen utuh)"
            if chunks and len(chunks) > 1:
                chunk_folder = f"{base_name}_chunks"
                chunk_info = f"{len(chunks)} bagian (folder /{chunk_folder})"
                for c_idx, chunk_text in enumerate(chunks, 1):
                    chunk_path = f"{chunk_folder}/part_{c_idx:02d}.md"
                    zf.writestr(chunk_path, chunk_text)

            summary_rows.append(
                f"| {idx} | `{raw_filename}` | `{md_entry_name}` | {tokens:,} | {chars:,} | {chunk_info} |"
            )

        # 3. Create a comprehensive SUMMARY.md manifest inside the ZIP
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        summary_content = f"""# 📦 Manifest Ekspor Arsip Dokumen Doc2MD

- **Tanggal Ekspor**: {now_str}
- **Total Dokumen**: {file_count} file
- **Total Token Akumulatif**: {total_tokens:,} tokens
- **Total Karakter**: {total_chars:,} karakter

---

## 📑 Rincian Berkas dalam Arsip

| No | File Asli | File Markdown Utama | Estimasi Token | Karakter | Status Pembagian (Chunking) |
|---|---|---|---|---|---|
""" + "\n".join(summary_rows) + f"""

---

### 💡 Catatan Penggunaan untuk AI / LLM:
1. File `.md` di root arsip merupakan dokumen lengkap yang telah disanitasi bebas karakter tersembunyi (BOM, zero-width space).
2. Jika dokumen memiliki subfolder `_chunks`, gunakan file-file pecahan di dalamnya jika jendela konteks LLM memiliki batasan token tertentu.

*Dihasilkan secara otomatis oleh Doc2MD Studio v2.0.*
"""
        zf.writestr("SUMMARY.md", summary_content)

    return zip_buffer.getvalue()
