// ===================================================================
// Doc2MD - Sample Markdown Documents Preset Library
// ===================================================================

window.DOC2MD_SAMPLES = {
    report: {
        filename: 'Laporan_Analisis_Sistem',
        content: `# Laporan Evaluasi Kinerja Sistem

Berikut adalah ringkasan evaluasi operasional dan matriks pencapaian kuartal ini.

## Ringkasan Eksekutif
Sistem pemrosesan dokumen menunjukkan peningkatan efisiensi sebesar **34%** setelah optimasi pipeline.

> "Preservasi konteks teks dan pemetaan gambar dokumen menjadi kunci utama akurasi pemrosesan AI."

---

## Matriks Evaluasi
| Komponen | Status Sebelum | Status Sesudah | Peningkatan |
|---|---|---|---|
| Ekstraksi PDF | 3.2 detik | 0.8 detik | +75% |
| Pemetaan Gambar | Tidak ada | Terdeteksi Otomatis | 100% |
| Ekspor DOCX | Manual | 1-Klik Rapi | Sangat Cepat |

## Rekomendasi Tindak Lanjut
1. Pertahankan konfigurasi offline agar privasi data terjaga 100%.
2. Gunakan auto-chunking jika ukuran dokumen melebihi 16,000 token.
3. Lakukan verifikasi visual pada dokumen yang memiliki banyak diagram kompleks.

\`\`\`python
# Cuplikan automasi konversi dokumen
import md2docx

docx_bytes = md2docx.markdown_to_docx_bytes(markdown_content)
with open("output.docx", "wb") as f:
    f.write(docx_bytes)
\`\`\`
`
    },
    proposal: {
        filename: 'Proposal_Pengembangan_Fitur',
        content: `# Proposal Pengembangan Modul AI Studio

## 1. Latar Belakang
Pengguna membutuhkan solusi lokal untuk mengonversi dokumen PDF/Word/Excel ke Markdown dan sebaliknya dengan cepat tanpa ketergantungan API pihak ketiga.

## 2. Ruang Lingkup Proyek
- **Konversi Multi-Format**: PDF, Word, Excel, PowerPoint, Gambar
- **Preservasi Konteks**: Deteksi otomatis gambar/diagram dalam PDF
- **Fitur Ekspor Sebaliknya**: Markdown ke file Microsoft Word (.docx) berformat rapi

## 3. Garis Waktu Pelaksanaan
- **Fase 1**: Penataan antarmuka & tombol reset
- **Fase 2**: Integrasi engine konversi dokumen & styling Word
- **Fase 3**: Build PyInstaller standalone eksekutabel
`
    },
    mathDiagram: {
        filename: 'Spesifikasi_Teknis_Diagram_dan_Formula',
        content: `# Spesifikasi Teknis Pipeline & Optimasi Model

Berikut adalah pemetaan alur pemrosesan dokumen dan formula matematika tokenisasi.

## 1. Diagram Alur Konversi Sistem (Mermaid Flowchart)

\`\`\`mermaid
graph TD
    A[📄 Dokumen Asli: PDF / Office] --> B{Ekstraksi Aset Visual}
    B -->|Gambar Ditemukan| C[🖼️ Simpan ke /assets & Auto-link]
    B -->|Hanya Teks| D[🧹 Pembersihan BOM & Zero-Width]
    C --> D
    D --> E[🔢 Tiktoken Chunking cl100k_base]
    E --> F[✨ Output Markdown Bersih & AI-Ready]
    F --> G[📥 Batch Download ZIP / Word / PDF]
\`\`\`

---

## 2. Model Matematika Token & Kompresi Dokumen (KaTeX)

Efisiensi kompresi teks bebas *noise* dinyatakan dengan persamaan:

$$ \\eta = \\left( 1 - \\frac{T_{clean}}{T_{raw}} \\right) \\times 100\\% $$

Untuk distribusi bobot kolom tabel proporsional $W_i$:

$$ W_i = \\frac{L_i^{\\alpha}}{\\sum_{k=1}^{n} L_k^{\\alpha}} \\times W_{total} $$

Di mana $L_i$ adalah panjang maksimum string pada kolom ke-$i$, dan nilai komputasi kuantum $E = mc^2$ tetap konstan dengan batas $\\theta \\le 0.05$.
`
    }
};
