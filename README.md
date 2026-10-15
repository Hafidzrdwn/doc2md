# Doc2MD: Personal Document to AI-Ready Markdown & Word (.DOCX) Studio

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Pytest](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Doc2MD** adalah aplikasi desktop dan web mandiri yang dirancang untuk melakukan konversi dua arah (*two-way conversion*) antara berbagai format dokumen populer ke format **Markdown yang optimal untuk AI**, serta konversi sebaliknya dari **Markdown ke Microsoft Word (.DOCX)** dengan tipografi dan tata letak modern.

---

## 🌟 Fitur Utama

### 1. 🔄 Two-Way Conversion (Dua Arah)
- **Document to Markdown**: Mengonversi PDF, Word (`.docx`), Excel (`.xlsx`, `.xls`), PowerPoint (`.pptx`), CSV, Gambar (`.png`, `.jpg`, dll.), dan teks biasa menjadi Markdown bersih.
- **Markdown to Word (.DOCX)**: Mengonversi Markdown mentah atau file `.md` kembali ke dokumen Microsoft Word berformat indah secara instan.

### 2. 🤖 AI-Ready Text Sanitization
- Membersihkan spasi liar di akhir baris, enter berlebih, dan karakter tersembunyi (*zero-width spaces*, BOM: `\u200B-\u200D`, `\uFEFF`) yang sering mengaburkan pemrosesan Large Language Model (LLM).

### 3. 🖼️ Real Image Asset Extraction & Markdown Auto-Linking
- **Ekstraksi Gambar Nyata**: Mengekstrak diagram, infografis, dan gambar biner asli dari dokumen PDF (via `pypdfium2`), DOCX, PPTX, dan XLSX ke folder aset lokal (`assets/`).
- **Penyematan Link Otomatis**: Otomatis menyisipkan galeri visual dan tautan Markdown `![Caption](assets/<nama_gambar>.png)` langsung di output teks sehingga gambar langsung tampil di Obsidian, VS Code, atau Markdown previewer mana pun.
- **Visual Context Annotator**: Tetap menyertakan metadata jumlah dan lokasi halaman gambar untuk membantu penalaran LLM/AI.

### 4. 🔢 Token Counting & Smart Chunking
- Terintegrasi langsung dengan tokenizer resmi OpenAI `tiktoken` (`cl100k_base`).
- Menampilkan estimasi jumlah token secara instan dan menyediakan opsi *token chunking* otomatis (misal: 15.000 token) untuk memecah dokumen panjang agar pas dalam *context window* LLM.

### 5. 📄 Beautiful Word (.DOCX) Layout Engine
- **Tabel Dinamis Proporsional**: Mengukur bobot panjang teks setiap kolom dan mengalokasikan lebar kolom secara cerdas (misal: kolom angka/IPK tetap ringkas, sedangkan kolom deskripsi/kriteria memperoleh ruang leluasa).
- **Pembersihan Fragmen Kata**: Otomatis menyambungkan kembali kata yang terputus oleh `<br>` sempit dari ekstraksi PDF (misal: `Pengalama<br>n<br>(tahun)` -> `Pengalaman (tahun)`).
- **Code Block Modern**: Kode pemrograman berpagar (```` ``` ````) dirender dalam tabel berlatar abu-abu Slate 50 (`#F8FAFC`), font monospace Consolas, dan badge bahasa pemrograman (seperti `[PYTHON]`).
- **Penomoran Soal Bebas-Bug**: Format *hanging indent* mandiri yang mencegah penomoran daftar berurutan meloncat atau menyatu dengan tabel sebelumnya.
- **Tabel Multi-Halaman Rapi**: Mendukung `tblHeader` (judul tabel otomatis berulang di halaman baru) dan `cantSplit` (mencegah baris terbelah canggung di pergantian halaman).

### 6. 🖨️ Precision PDF & Standalone HTML Paged Media Engine
- **Cegah Terpotong (Anti-Cutoff & Smart Page Breaks)**: Didesain dengan aturan CSS Paged Media (`break-inside: avoid` pada tabel, blockquote, callout, dan code block; `break-after: avoid` pada heading H1-H6) agar struktur dokumen tidak pernah terbelah janggal di batas halaman.
- **Header Tabel Berulang**: Judul tabel otomatis berulang di setiap halaman cetak baru (`thead { display: table-header-group; }`).
- **Sintaks Highlighting Elegan**: Blok kode diformat dengan pewarnaan sintaks Pygments profesional.
- **Format Siap Cetak (A4 Standard)**: Dilengkapi nomor halaman otomatis (*Halaman X dari Y*) dan tombol cetak instan.

### 7. 📦 Batch ZIP Archive Exporter & Manifest
- **1-Klik Ekspor Massal**: Mengemas seluruh dokumen hasil konversi menjadi satu arsip `.zip` yang rapi.
- **Inklusi Folder Assets**: Seluruh aset gambar hasil ekstraksi dikemas utuh ke dalam folder `assets/` di dalam ZIP.
- **Hierarki Folder Chunks**: Jika dokumen dipecah oleh fitur chunking token, masing-masing part dokumen ditempatkan secara otomatis dalam subfolder khusus (`<nama_dokumen>_chunks/part_XX.md`).
- **Manifest SUMMARY.md Otomatis**: Memuat ringkasan waktu konversi, daftar file, serta metrik token dan karakter per dokumen.

### 8. 🌓 Live Split-Screen Markdown Editor + KaTeX & Mermaid
- **Editor & Live Preview Interaktif**: Mode tampilan fleksibel (*Split*, *Edit Saja*, *Preview Saja*) dengan sinkronisasi karakter dan baris secara real-time.
- **Formula Matematika KaTeX**: Mendukung render persamaan matematika baik *inline* (`$E = mc^2$`) maupun *block/display* (`$$\sum ...$$`).
- **Diagram Alur Mermaid.js**: Merender diagram alur grafis (*flowchart*, *sequence*, dll.) dari blok ` ```mermaid ` langsung di layar.
- **Preset Template Praktis**: Tersedia tombol preset dokumen cepat (Laporan Eksekutif, Proposal Fitur, dan Spesifikasi Teknis Diagram/Formula).

### 9. 🎨 Professional Styling Presets & Theme Engine
- **4 Preset Tema Standar Industri**:
  - 🎨 **Modern Slate** (Default): Aksen Sky Blue (`#0284C7`), font Plus Jakarta Sans / Calibri, layout minimalis elegan untuk kebutuhan umum.
  - 🏢 **Corporate Navy**: Aksen Deep Royal Navy (`#1E3A8A`), font Segoe UI, gaya formal berwibawa untuk laporan bisnis, perbankan, dan dokumen resmi.
  - 🎓 **Classic Academic**: Aksen Formal Crimson (`#7F1D1D`), font serif tradisional Times New Roman & Georgia, ideal untuk naskah ilmiah, tesis, dan format akademis.
  - 🌿 **Emerald Tech**: Aksen Emerald Green (`#059669`), font modern berkarakter teknis, cocok untuk dokumentasi sistem, devops, dan audit teknis.
- **Konsistensi Visual Lintas-Format**: Token tema (warna heading H1-H4, background tabel, border sel, blockquote, dan bullet list) diterapkan secara seragam baik pada ekspor Microsoft Word (`.docx`) maupun PDF/HTML cetak (`.pdf` / `.html`).
- **Theme Selector Interaktif**: Pemilih tema visual dengan indikator warna dinamis dan deskripsi instan langsung di toolbar editor studio.

### 10. 🔍 Offline OCR (Optical Character Recognition) untuk Gambar & PDF Scan
- **Engine OCR Mandiri & 100% Offline**: Mengintegrasikan engine RapidOCR berbasis ONNX Runtime yang ringan dan berjalan sepenuhnya di mesin lokal tanpa koneksi internet atau dependensi binary eksternal yang rumit.
- **Ekstraksi Gambar Visual Nyata**: Mengonversi file gambar (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`) menjadi teks Markdown lengkap dengan indikator skor akurasi deteksi dan metrik kata.
- **Deteksi Otomatis PDF Scan**: Memindai halaman PDF yang tidak memiliki *text layer* (hasil scan scanner atau foto dokumen fisik), merender bitmap resolusi tinggi via `pypdfium2`, dan mengekstrak teks halaman demi halaman ke Markdown terstruktur.
- **Indikator Visual di Antarmuka**: Kartu dokumen menampilkan badge `🔍 OCR` ungu pada file gambar maupun scan PDF yang berhasil diproses.

### 11. 📑 Obsidian & Notion Frontmatter YAML Formatter
- **Metadata Siap Impor Catatan Digital**: Mengonfigurasi header metadata YAML di awal dokumen Markdown (`--- ... ---`) agar kompatibel penuh dengan Obsidian Vault, Notion Workspace, Logseq, dan static site generators (Hugo, Astro, Jekyll).
- **Tiga Preset Standar Industri**:
  - 🔮 **Obsidian Preset**: Menyertakan `title`, `source`, `created` timestamp, metrik `tokens` dan `characters`, `tags` (termasuk ekstensi dokumen asli), dan `aliases` untuk navigasi graph view.
  - 🗂️ **Notion Preset**: Format database properties dengan `Title`, `Source File`, `Created Date`, `Tokens`, `Characters`, `Status: Converted`, dan `Tags`.
  - ⚡ **Minimal Preset**: Format bersih dan ringkas berisi `title`, `source`, dan `date`.
- **Integrasi Dua Arah & Pembersihan Otomatis**: Dilengkapi fungsi `strip_frontmatter` untuk mencegah duplikasi tag header saat beralih preset atau mengonversi kembali ke DOCX/PDF.
- **Kontrol Fleksibel**: Dapat dipilih langsung sebelum upload dokumen pada View 1 atau diterapkan secara interaktif pada naskah aktif di toolbar Markdown Studio (View 1 & View 2) lewat tombol `+ YAML`.

### 12. 📁 Folder Watcher / Auto-Convert Dropped Files
- **Pemantau Latar Belakang Hands-Free**: Memanfaatkan library `watchdog` untuk memantau folder input (default: `watch_input/` atau path kustom) dan mendeteksi dokumen baru yang diletakkan secara instan.
- **Deteksi Kestabilan File (Anti-Lock & Debounce)**: Memastikan file yang sedang disalin telah selesai ditulis 100% oleh sistem operasi sebelum proses konversi dimulai untuk mencegah kesalahan *file lock*.
- **Otomasi Pipeline Penuh**: Mengekstrak teks, tabel, gambar biner (ke subfolder `<output_dir>/assets/`), menyematkan header Frontmatter YAML pilihan, dan menyimpan Markdown bersih langsung ke `<output_dir>/`.
- **Feed Riwayat Real-Time**: Antarmuka studio menyediakan dashboard pemantau live dengan indikator status aktif/nonaktif, log konversi per dokumen, dan metrik token.
- **REST API Kontrol**: Dilengkapi endpoint `GET /watcher/status`, `POST /watcher/start`, `POST /watcher/stop`, `GET /watcher/history`, dan `POST /watcher/clear-history`.

### 13. 💻 Desktop Native & Offline
- Dapat dijalankan sebagai aplikasi desktop native tanpa internet menggunakan `flaskwebgui` dan Chromium/Chrome/Edge.

---

## 📂 Struktur Repositori

```text
doc-to-markdown/
├── core/                       # Logika inti (Core business logic)
│   ├── __init__.py             # Public API export
│   ├── batch_exporter.py       # In-memory batch ZIP packaging & manifest generator
│   ├── chunker.py              # Tokenisasi tiktoken & text chunking
│   ├── converter.py            # MarkItDown conversion & text sanitization
│   ├── docx_generator.py       # Markdown-to-DOCX engine & table styling
│   ├── folder_watcher.py       # Background folder watcher & auto-convert engine
│   ├── frontmatter_formatter.py# Obsidian / Notion YAML frontmatter engine
│   ├── image_extractor.py      # Real image asset extractor for PDF & Office formats
│   ├── ocr_engine.py           # Offline OCR engine (RapidOCR / ONNX)
│   ├── pdf_generator.py        # Markdown-to-PDF & standalone HTML engine
│   └── themes.py               # Centralized styling presets & theme engine
├── templates/                  # Frontend UI templates
│   └── index.html              # Modern responsive web & desktop interface
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── test_api.py             # FastAPI endpoint integration tests
│   ├── test_batch_export.py    # Unit tests untuk pembuatan arsip ZIP & manifest
│   ├── test_chunker.py         # Unit tests untuk token count & chunking
│   ├── test_converter.py       # Unit tests untuk sanitasi & deteksi ekstensi
│   ├── test_docx_generator.py  # Unit tests untuk Word layout, tabel & lists
│   ├── test_folder_watcher.py  # Unit tests untuk folder watcher & auto-convert
│   ├── test_frontmatter.py     # Unit tests untuk format YAML frontmatter & API
│   ├── test_image_extractor.py # Unit tests untuk ekstraksi aset gambar nyata
│   ├── test_ocr.py             # Unit tests untuk offline OCR gambar & PDF scan
│   ├── test_pdf_generator.py   # Unit tests untuk PDF & HTML layout generation
│   └── test_themes.py          # Unit tests untuk preset tema Word, PDF & HTML
├── app.py                      # Application entrypoint & Desktop GUI runner
├── app.spec                    # PyInstaller standalone build configuration
├── md2docx.py                  # Backward-compatible proxy module
├── requirements.txt            # Daftar dependensi terstandar
├── .gitignore                  # Git ignore rules untuk Python & build artifacts
└── README.md                   # Dokumentasi proyek
```

---

## 🚀 Panduan Instalasi & Penggunaan

### Prasyarat
- Python 3.10 atau versi yang lebih baru
- Google Chrome atau Microsoft Edge (untuk mode Desktop GUI)

### 1. Kloning Repositori
```bash
git clone https://github.com/username/doc-to-markdown.git
cd doc-to-markdown
```

### 2. Buat dan Aktifkan Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instal Dependensi
```bash
pip install -r requirements.txt
```

---

## 🖥️ Menjalankan Aplikasi

### Mode Desktop GUI (Rekomendasi)
Jalankan aplikasi desktop dengan jendela antarmuka mandiri:
```bash
python app.py
```
Aplikasi akan otomatis menginisialisasi server lokal di latar belakang (`http://127.0.0.1:8473`) dan membuka jendela aplikasi desktop.

### Mode Web Server (Headless / Browser Manual)
Jika ingin menjalankan murni sebagai backend / web server:
```bash
uvicorn app:app --host 127.0.0.1 --port 8473 --reload
```
Buka browser dan navigasikan ke `http://127.0.0.1:8473`.

---

## 🧪 Menjalankan Automated Testing

Proyek ini dilengkapi dengan *automated testing suite* menggunakan `pytest`:
```bash
pytest tests/ -v
```

Semua pengujian memvalidasi:
- Akurasi penghitungan token dan pemotongan chunk.
- Ekstraksi dokumen, sanitasi teks Unicode, dan toleransi format file.
- Kerapian tata letak DOCX, rekonstruksi kata `<br>`, dan isolasi nomor daftar.
- Integritas endpoint API `/convert` dan `/md-to-docx`.

---

## 📦 Membangun File Eksekutabel Mandiri (.EXE)

Aplikasi dapat dikompilasi menjadi paket aplikasi desktop mandiri tanpa memerlukan instalasi Python di komputer target:

```bash
pyinstaller --noconfirm app.spec
```

Hasil file binary eksekutabel akan berada di:
```text
dist/app/app.exe
```

---

## 📋 Format Dokumen yang Didukung

| Format | Ekstensi | Keterangan |
| :--- | :--- | :--- |
| **PDF** | `.pdf` | Ekstraksi teks lengkap + Deteksi konteks gambar |
| **Microsoft Word** | `.docx` | Dukungan konversi dua arah (baca & buat DOCX) |
| **Microsoft Excel** | `.xlsx`, `.xls` | Ekstraksi tabel data ke format tabel Markdown |
| **PowerPoint** | `.pptx` | Ekstraksi teks per slide presentasi |
| **Delimited / Text** | `.csv`, `.txt`, `.md` | Konversi teks mentah & tabel data |
| **Data Terstruktur** | `.json`, `.xml`, `.html` | Ekstraksi konten semantik |
| **Gambar** | `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp` | Metadata teknis gambar |

---

## 📄 Lisensi

Didistribusikan di bawah lisensi MIT. Silakan gunakan, modifikasi, dan kembangkan secara bebas untuk keperluan pribadi maupun komersial.
