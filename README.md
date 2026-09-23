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

### 3. 🖼️ Visual Context Annotator (PDF & Image Detection)
- Memindai dokumen PDF untuk mendeteksi keberadaan gambar dan diagram teknis.
- Menyematkan blok anotasi konteks di awal output Markdown yang memberitahukan AI mengenai jumlah gambar dan halaman tempat gambar tersebut berada, sehingga model AI memiliki konteks visual yang utuh.

### 4. 🔢 Token Counting & Smart Chunking
- Terintegrasi langsung dengan tokenizer resmi OpenAI `tiktoken` (`cl100k_base`).
- Menampilkan estimasi jumlah token secara instan dan menyediakan opsi *token chunking* otomatis (misal: 15.000 token) untuk memecah dokumen panjang agar pas dalam *context window* LLM.

### 5. 📄 Beautiful Word (.DOCX) Layout Engine
- **Tabel Dinamis Proporsional**: Mengukur bobot panjang teks setiap kolom dan mengalokasikan lebar kolom secara cerdas (misal: kolom angka/IPK tetap ringkas, sedangkan kolom deskripsi/kriteria memperoleh ruang leluasa).
- **Pembersihan Fragmen Kata**: Otomatis menyambungkan kembali kata yang terputus oleh `<br>` sempit dari ekstraksi PDF (misal: `Pengalama<br>n<br>(tahun)` -> `Pengalaman (tahun)`).
- **Code Block Modern**: Kode pemrograman berpagar (```` ``` ````) dirender dalam tabel berlatar abu-abu Slate 50 (`#F8FAFC`), font monospace Consolas, dan badge bahasa pemrograman (seperti `[PYTHON]`).
- **Penomoran Soal Bebas-Bug**: Format *hanging indent* mandiri yang mencegah penomoran daftar berurutan meloncat atau menyatu dengan tabel sebelumnya.
- **Tabel Multi-Halaman Rapi**: Mendukung `tblHeader` (judul tabel otomatis berulang di halaman baru) dan `cantSplit` (mencegah baris terbelah canggung di pergantian halaman).

### 6. 💻 Desktop Native & Offline
- Dapat dijalankan sebagai aplikasi desktop native tanpa internet menggunakan `flaskwebgui` dan Chromium/Chrome.

---

## 📂 Struktur Repositori

```text
doc-to-markdown/
├── core/                       # Logika inti (Core business logic)
│   ├── __init__.py             # Public API export
│   ├── chunker.py              # Tokenisasi tiktoken & text chunking
│   ├── converter.py            # MarkItDown conversion, image annotator, sanitization
│   └── docx_generator.py       # Markdown-to-DOCX engine & table styling
├── templates/                  # Frontend UI templates
│   └── index.html              # Modern responsive web & desktop interface
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── test_api.py             # FastAPI endpoint integration tests
│   ├── test_chunker.py         # Unit tests untuk token count & chunking
│   ├── test_converter.py       # Unit tests untuk sanitasi & deteksi ekstensi
│   └── test_docx_generator.py  # Unit tests untuk Word layout, tabel & lists
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
