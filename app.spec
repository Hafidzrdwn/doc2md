# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

pdfminer_datas, pdfminer_binaries, pdfminer_hiddenimports = collect_all('pdfminer')
pypdfium2_datas, pypdfium2_binaries, pypdfium2_hiddenimports = collect_all('pypdfium2')
pdfplumber_datas, pdfplumber_binaries, pdfplumber_hiddenimports = collect_all('pdfplumber')
docx_datas, docx_binaries, docx_hiddenimports = collect_all('docx')
lxml_datas, lxml_binaries, lxml_hiddenimports = collect_all('lxml')
mammoth_datas, mammoth_binaries, mammoth_hiddenimports = collect_all('mammoth')
cobble_datas, cobble_binaries, cobble_hiddenimports = collect_all('cobble')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=pdfminer_binaries + pypdfium2_binaries + pdfplumber_binaries + docx_binaries + lxml_binaries + mammoth_binaries + cobble_binaries,
    datas=[
        ('templates', 'templates'),
    ] + pdfminer_datas + pypdfium2_datas + pdfplumber_datas + docx_datas + lxml_datas + mammoth_datas + cobble_datas,
    hiddenimports=[
        # ── tiktoken ─────────────────────────────────────────────────────────
        'tiktoken',
        'tiktoken.core',
        'tiktoken.load',
        'tiktoken.model',
        'tiktoken.registry',
        'tiktoken._tiktoken',
        'tiktoken_ext',
        'tiktoken_ext.openai_public',
        # ── uvicorn ──────────────────────────────────────────────────────────
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # ── fastapi / starlette ───────────────────────────────────────────────
        'fastapi',
        'starlette',
        'starlette.templating',
        'starlette.staticfiles',
        'starlette.middleware',
        'starlette.middleware.cors',
        # ── multipart ────────────────────────────────────────────────────────
        'multipart',
        'python_multipart',
        # ── jinja2 ───────────────────────────────────────────────────────────
        'jinja2',
        'jinja2.ext',
        # ── markitdown & data processing ─────────────────────────────────────
        'markitdown',
        'numpy',
        'pandas',
        # ── PDF libraries ─────────────────────────────────────────────────────
        'pdfminer',
        'pdfminer.six',
        'pdfminer.high_level',
        'pdfplumber',
        'pypdfium2',
        'cryptography',
        'PIL',
        'PIL.Image',
        # ── Word DOCX import & export ─────────────────────────────────────────
        'docx',
        'docx.shared',
        'docx.oxml',
        'docx.enum.text',
        'docx.enum.table',
        'lxml',
        'mammoth',
        'cobble',
        'core',
        'core.converter',
        'core.chunker',
        'core.docx_generator',
        'md2docx',
        # ── flaskwebgui + psutil ──────────────────────────────────────────────
        'flaskwebgui',
        'psutil',
        # ── misc ─────────────────────────────────────────────────────────────
        'logging.handlers',
    ] + pdfminer_hiddenimports + pypdfium2_hiddenimports + pdfplumber_hiddenimports + docx_hiddenimports + lxml_hiddenimports + mammoth_hiddenimports + cobble_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude pywebview and pythonnet — not needed
        'webview',
        'clr',
        'clr_loader',
        'pythonnet',
        # onnxruntime causes 0xC0000005 Access Violation when frozen.
        # magika is mocked in app.py so onnxruntime is completely unneeded.
        'onnxruntime',
        'onnxruntime.capi',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
