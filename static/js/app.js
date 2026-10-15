// Initialize Mermaid.js if present
if (window.mermaid) {
    mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
            darkMode: true,
            background: '#0b0f19',
            primaryColor: '#0284c7',
            primaryTextColor: '#f8fafc',
            lineColor: '#38bdf8'
        }
    });
}

const tabModeDoc2Md = document.getElementById('tabModeDoc2Md');
const tabModeMd2Doc = document.getElementById('tabModeMd2Doc');
const tabModeWatcher = document.getElementById('tabModeWatcher');
const viewDoc2Md = document.getElementById('viewDoc2Md');
const viewMd2Doc = document.getElementById('viewMd2Doc');
const viewWatcher = document.getElementById('viewWatcher');
const watcherHeaderDot = document.getElementById('watcherHeaderDot');
const watcherGlobalPill = document.getElementById('watcherGlobalPill');
const watcherGlobalDot = document.getElementById('watcherGlobalDot');
const watcherGlobalText = document.getElementById('watcherGlobalText');
const watcherStatusPill = document.getElementById('watcherStatusPill');
const btnStartWatcher = document.getElementById('btnStartWatcher');
const btnStopWatcher = document.getElementById('btnStopWatcher');
const watcherInputPath = document.getElementById('watcherInputPath');
const watcherOutputPath = document.getElementById('watcherOutputPath');
const btnResetInputPath = document.getElementById('btnResetInputPath');
const btnResetOutputPath = document.getElementById('btnResetOutputPath');
const watcherFrontmatterSelect = document.getElementById('watcherFrontmatterSelect');
const watcherChunkSelect = document.getElementById('watcherChunkSelect');
const watcherTotalProcessedBadge = document.getElementById('watcherTotalProcessedBadge');
const watcherHistoryCount = document.getElementById('watcherHistoryCount');
const btnRefreshWatcherHistory = document.getElementById('btnRefreshWatcherHistory');
const btnClearWatcherHistory = document.getElementById('btnClearWatcherHistory');
const watcherEmptyState = document.getElementById('watcherEmptyState');
const watcherFeedList = document.getElementById('watcherFeedList');

const tabModeDiff = document.getElementById('tabModeDiff');
const viewDiff = document.getElementById('viewDiff');
const btnLoadDiffSample = document.getElementById('btnLoadDiffSample');
const btnSwapDiff = document.getElementById('btnSwapDiff');
const btnExecuteDiff = document.getElementById('btnExecuteDiff');
const diffTitleA = document.getElementById('diffTitleA');
const diffTitleB = document.getElementById('diffTitleB');
const diffInputA = document.getElementById('diffInputA');
const diffInputB = document.getElementById('diffInputB');
const btnPullFromActiveDoc = document.getElementById('btnPullFromActiveDoc');
const btnPullFromStudioDoc = document.getElementById('btnPullFromStudioDoc');
const diffFileInputA = document.getElementById('diffFileInputA');
const diffFileInputB = document.getElementById('diffFileInputB');
const diffResultsSection = document.getElementById('diffResultsSection');
const diffSimilarityScore = document.getElementById('diffSimilarityScore');
const diffTokenDelta = document.getElementById('diffTokenDelta');
const diffTokenA = document.getElementById('diffTokenA');
const diffTokenB = document.getElementById('diffTokenB');
const diffAddedLines = document.getElementById('diffAddedLines');
const diffRemovedLines = document.getElementById('diffRemovedLines');
const diffModifiedLines = document.getElementById('diffModifiedLines');
const btnDiffSideBySide = document.getElementById('btnDiffSideBySide');
const btnDiffUnified = document.getElementById('btnDiffUnified');
const diffSideBySideContainer = document.getElementById('diffSideBySideContainer');
const diffSideBySideTableBody = document.getElementById('diffSideBySideTableBody');
const diffHeadTitleA = document.getElementById('diffHeadTitleA');
const diffHeadTitleB = document.getElementById('diffHeadTitleB');
const diffUnifiedContainer = document.getElementById('diffUnifiedContainer');
const diffUnifiedTableBody = document.getElementById('diffUnifiedTableBody');

const globalResetBtn = document.getElementById('globalResetBtn');

const dropzone = document.getElementById('dropzone');
const dropzoneNormal = document.getElementById('dropzoneNormal');
const dropzoneLoading = document.getElementById('dropzoneLoading');
const fileInput = document.getElementById('fileInput');
const chunkSelect = document.getElementById('chunkSelect');
const frontmatterSelect = document.getElementById('frontmatterSelect');
const view1FrontmatterPreset = document.getElementById('view1FrontmatterPreset');
const view1ApplyFrontmatterBtn = document.getElementById('view1ApplyFrontmatterBtn');
const quickStatusBadge = document.getElementById('quickStatusBadge');
const uploadStatusText = document.getElementById('uploadStatusText');

const fileDetailsSection = document.getElementById('fileDetailsSection');
const fileDetailsCount = document.getElementById('fileDetailsCount');
const fileCardsGrid = document.getElementById('fileCardsGrid');

const workspace = document.getElementById('workspace');
const tabsContainer = document.getElementById('tabsContainer');
const chunkTabs = document.getElementById('chunkTabs');
const chunkBtnList = document.getElementById('chunkBtnList');
const outputArea = document.getElementById('outputArea');
const activeFileInfo = document.getElementById('activeFileInfo');
const savingStat = document.getElementById('savingStat');
const tokenBadge = document.getElementById('tokenBadge');
const statsSummary = document.getElementById('statsSummary');
const statFiles = document.getElementById('statFiles');
const statTokens = document.getElementById('statTokens');
const promptPreset = document.getElementById('promptPreset');
const copyBtn = document.getElementById('copyBtn');
const mergeBtn = document.getElementById('mergeBtn');
const exportCurrentToDocxBtn = document.getElementById('exportCurrentToDocxBtn');
const exportCurrentToPdfBtn = document.getElementById('exportCurrentToPdfBtn');
const exportCurrentToHtmlBtn = document.getElementById('exportCurrentToHtmlBtn');
const exportAllZipBtn = document.getElementById('exportAllZipBtn');
const exportAllZipBtnText = document.getElementById('exportAllZipBtnText');

const targetDocxName = document.getElementById('targetDocxName');
const mdDropzone = document.getElementById('mdDropzone');
const mdFileInput = document.getElementById('mdFileInput');
const mdFileSelectedName = document.getElementById('mdFileSelectedName');
const mdInputArea = document.getElementById('mdInputArea');
const mdCharCount = document.getElementById('mdCharCount');
const mdLineCount = document.getElementById('mdLineCount');
const generateDocxBtn = document.getElementById('generateDocxBtn');
const generateDocxBtnText = document.getElementById('generateDocxBtnText');
const generatePdfBtn = document.getElementById('generatePdfBtn');
const generatePdfBtnText = document.getElementById('generatePdfBtnText');
const generateHtmlBtn = document.getElementById('generateHtmlBtn');
const generateHtmlBtnText = document.getElementById('generateHtmlBtnText');
const editorFrontmatterPreset = document.getElementById('editorFrontmatterPreset');
const addFrontmatterBtn = document.getElementById('addFrontmatterBtn');
const quickPdfBtn = document.getElementById('quickPdfBtn');
const quickDocxBtn = document.getElementById('quickDocxBtn');
const quickHtmlBtn = document.getElementById('quickHtmlBtn');
const btnViewSplit = document.getElementById('btnViewSplit');
const btnViewEdit = document.getElementById('btnViewEdit');
const btnViewPreview = document.getElementById('btnViewPreview');
const editorLeftPane = document.getElementById('editorLeftPane');
const editorRightPane = document.getElementById('editorRightPane');
const mdLivePreview = document.getElementById('mdLivePreview');
const loadSampleReportBtn = document.getElementById('loadSampleReportBtn');
const loadSampleProposalBtn = document.getElementById('loadSampleProposalBtn');
const loadSampleMathDiagramBtn = document.getElementById('loadSampleMathDiagramBtn');
const exportThemeSelect = document.getElementById('exportThemeSelect');
const themeColorBadge = document.getElementById('themeColorBadge');
const themeDescText = document.getElementById('themeDescText');

const themeMeta = {
    modern_slate: { color: '#0284c7', desc: 'Aksen Sky Blue modern, font sans rapi, cocok untuk laporan umum.' },
    corporate_navy: { color: '#1e3a8a', desc: 'Gaya resmi formal perbankan dan korporat dengan aksen Deep Royal Navy.' },
    classic_academic: { color: '#7f1d1d', desc: 'Format naskah ilmiah, tesis, dan naskah formal dengan tipografi serif tradisional.' },
    emerald_tech: { color: '#059669', desc: 'Nuansa hijau emerald modern untuk dokumentasi sistem, devops, audit, dan teknis.' }
};

if (exportThemeSelect) {
    exportThemeSelect.addEventListener('change', () => {
        const val = exportThemeSelect.value;
        const meta = themeMeta[val] || themeMeta.modern_slate;
        if (themeColorBadge) themeColorBadge.style.backgroundColor = meta.color;
        if (themeDescText) themeDescText.textContent = meta.desc;
    });
}

function getSelectedTheme() {
    return exportThemeSelect ? exportThemeSelect.value : 'modern_slate';
}

let converted = [];
let activeIdx = 0;
let activeChunkIdx = 0;

tabModeDoc2Md.addEventListener('click', () => switchMode('doc2md'));
tabModeMd2Doc.addEventListener('click', () => switchMode('md2doc'));
tabModeWatcher.addEventListener('click', () => switchMode('watcher'));
tabModeDiff.addEventListener('click', () => switchMode('diff'));

function switchMode(mode) {
    viewDoc2Md.classList.add('hidden');
    viewMd2Doc.classList.add('hidden');
    viewWatcher.classList.add('hidden');
    viewDiff.classList.add('hidden');

    tabModeDoc2Md.className = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5";
    tabModeMd2Doc.className = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5";
    tabModeWatcher.className = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5";
    tabModeDiff.className = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5";

    if (mode === 'doc2md') {
        viewDoc2Md.classList.remove('hidden');
        tabModeDoc2Md.className = "px-3.5 py-1.5 rounded-lg bg-sky-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
    } else if (mode === 'md2doc') {
        viewMd2Doc.classList.remove('hidden');
        tabModeMd2Doc.className = "px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
    } else if (mode === 'watcher') {
        viewWatcher.classList.remove('hidden');
        tabModeWatcher.className = "px-3.5 py-1.5 rounded-lg bg-purple-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
        fetchWatcherStatus();
    } else if (mode === 'diff') {
        viewDiff.classList.remove('hidden');
        tabModeDiff.className = "px-3.5 py-1.5 rounded-lg bg-teal-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
    }
}

dropzone.addEventListener('click', () => fileInput.click());
dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-sky-500', 'bg-sky-950/20');
});
dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-sky-500', 'bg-sky-950/20');
});
dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-sky-500', 'bg-sky-950/20');
    if (e.dataTransfer.files.length) upload(e.dataTransfer.files);
});
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) upload(e.target.files);
});

async function upload(files) {
    const fd = new FormData();
    for (let f of files) fd.append('files', f);
    fd.append('chunk_tokens', chunkSelect.value);
    fd.append('frontmatter_preset', frontmatterSelect ? frontmatterSelect.value : 'none');

    dropzoneNormal.classList.add('hidden');
    dropzoneLoading.classList.remove('hidden');
    dropzone.classList.add('pointer-events-none', 'border-sky-500/60');
    quickStatusBadge.textContent = 'Memproses...';
    quickStatusBadge.className = 'text-sky-400 font-medium animate-pulse';
    uploadStatusText.textContent = `Mengonversi ${files.length} dokumen...`;

    try {
        const res = await fetch('/convert', { method: 'POST', body: fd });
        const data = await res.json();
        
        const newSuccess = (data.results || []).filter(r => r.status === 'success');
        const errors = (data.results || []).filter(r => r.status === 'error');

        if (errors.length > 0 && newSuccess.length === 0) {
            alert(`Gagal memproses file:\n${errors.map(e => e.filename + ': ' + e.error).join('\n')}`);
            return;
        }

        if (!newSuccess.length) {
            alert('Gagal memproses file. Pastikan format didukung.');
            return;
        }

        // Append or replace
        converted = [...converted, ...newSuccess];
        activeIdx = converted.length - newSuccess.length;
        activeChunkIdx = 0;

        renderAll();
    } catch (err) {
        alert('Terjadi kesalahan saat mengunggah: ' + err.message);
    } finally {
        dropzoneNormal.classList.remove('hidden');
        dropzoneLoading.classList.add('hidden');
        dropzone.classList.remove('pointer-events-none', 'border-sky-500/60');
        quickStatusBadge.textContent = 'Siap';
        quickStatusBadge.className = 'text-emerald-400 font-medium';
        fileInput.value = '';
    }
}

function renderAll() {
    renderFileCards();
    renderWorkspace();
}

function renderFileCards() {
    if (!converted.length) {
        fileDetailsSection.classList.add('hidden');
        return;
    }
    fileDetailsSection.classList.remove('hidden');
    fileDetailsCount.textContent = converted.length;
    fileCardsGrid.innerHTML = '';

    converted.forEach((item, idx) => {
        const ext = (item.filename.split('.').pop() || '').toUpperCase();
        const card = document.createElement('div');
        const isActive = (idx === activeIdx);
        
        card.className = `p-3.5 rounded-xl border transition cursor-pointer flex flex-col justify-between gap-2.5 ${
            isActive ? 'bg-sky-950/40 border-sky-500/80 shadow-md shadow-sky-500/10' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
        }`;

        card.innerHTML = `
            <div class="flex items-start justify-between gap-2">
                <div class="flex items-center gap-2 overflow-hidden">
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-800 text-sky-400 border border-slate-700 shrink-0 font-mono">${ext}</span>
                    <span class="text-xs font-semibold text-slate-200 truncate" title="${item.filename}">${item.filename}</span>
                </div>
                <button class="remove-btn text-slate-500 hover:text-rose-400 transition p-0.5 rounded" title="Hapus file ini" data-idx="${idx}">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>
            <div class="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>${item.raw_size_kb} KB</span>
                <div class="flex items-center gap-1.5">
                    ${item.is_ocr ? `<span class="bg-purple-950/80 text-purple-300 border border-purple-800/60 px-1.5 py-0.5 rounded text-[10px] flex items-center gap-1 font-sans font-medium" title="Teks diekstrak menggunakan Offline OCR">🔍 OCR</span>` : ''}
                    ${(item.images_count && item.images_count > 0) ? `<span class="bg-amber-950/80 text-amber-300 border border-amber-800/60 px-1.5 py-0.5 rounded text-[10px] flex items-center gap-1 font-sans" title="${item.images_count} gambar diekstrak">🖼️ ${item.images_count}</span>` : ''}
                    <span class="text-emerald-400 font-semibold">${item.token_count.toLocaleString()} tokens</span>
                </div>
            </div>
        `;

        card.onclick = (e) => {
            if (e.target.closest('.remove-btn')) return;
            activeIdx = idx;
            activeChunkIdx = 0;
            renderAll();
        };

        const rmBtn = card.querySelector('.remove-btn');
        rmBtn.onclick = (e) => {
            e.stopPropagation();
            removeFile(idx);
        };

        fileCardsGrid.appendChild(card);
    });
}

function removeFile(index) {
    converted.splice(index, 1);
    if (activeIdx >= converted.length) {
        activeIdx = Math.max(0, converted.length - 1);
    }
    activeChunkIdx = 0;
    if (converted.length === 0) {
        resetAll();
    } else {
        renderAll();
    }
}

function renderWorkspace() {
    if (!converted.length) {
        workspace.classList.add('hidden');
        statsSummary.classList.add('hidden');
        return;
    }

    workspace.classList.remove('hidden');
    statsSummary.classList.remove('hidden');
    statFiles.textContent = converted.length;

    let totalTokens = converted.reduce((acc, cur) => acc + cur.token_count, 0);
    statTokens.textContent = totalTokens.toLocaleString();

    tabsContainer.innerHTML = '';
    converted.forEach((item, idx) => {
        const tab = document.createElement('button');
        const isSelected = (idx === activeIdx);
        tab.className = `px-3 py-1.5 rounded-lg text-xs font-medium truncate max-w-[160px] border transition ${
            isSelected ? 'bg-sky-600 text-white border-sky-500 shadow-sm' : 'bg-slate-950 text-slate-300 border-slate-800 hover:bg-slate-800'
        }`;
        tab.textContent = item.filename;
        tab.onclick = () => {
            activeIdx = idx;
            activeChunkIdx = 0;
            renderAll();
        };
        tabsContainer.appendChild(tab);
    });

    updateActiveView();
}

function updateActiveView() {
    if (!converted.length) return;
    const curr = converted[activeIdx];
    
    if (curr.chunks && curr.chunks.length > 1) {
        chunkTabs.classList.remove('hidden');
        chunkBtnList.innerHTML = '';
        curr.chunks.forEach((_, cIdx) => {
            const cBtn = document.createElement('button');
            cBtn.className = `px-2.5 py-1 rounded-md text-[11px] font-mono border transition ${
                cIdx === activeChunkIdx ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm' : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`;
            cBtn.textContent = `Part ${cIdx + 1}`;
            cBtn.onclick = () => {
                activeChunkIdx = cIdx;
                updateActiveView();
            };
            chunkBtnList.appendChild(cBtn);
        });
    } else {
        chunkTabs.classList.add('hidden');
    }

    const rawText = (curr.chunks && curr.chunks.length > 0) ? curr.chunks[activeChunkIdx] : curr.markdown;
    outputArea.value = applyPromptPreset(rawText, curr.filename);
    
    const imgNote = (curr.images_count && curr.images_count > 0) ? ` • 🖼️ ${curr.images_count} gambar diekstrak` : '';
    activeFileInfo.textContent = `${curr.filename} • ${curr.raw_size_kb} KB raw${imgNote}`;
    savingStat.textContent = `${curr.char_count.toLocaleString()} karakter`;
    tokenBadge.textContent = `${curr.token_count.toLocaleString()} tokens`;
}

function applyPromptPreset(content, filename) {
    const mode = promptPreset.value;
    if (mode === 'summarize') {
        return `Berikut adalah dokumen "${filename}":\n\n\`\`\`markdown\n${content}\n\`\`\`\n\nTolong buat ringkasan komprehensif, poin-poin keputusan terpenting, dan action items dari dokumen di atas.`;
    } else if (mode === 'qa') {
        return `Gunakan dokumen "${filename}" berikut sebagai referensi utama menjawab pertanyaan:\n\n\`\`\`markdown\n${content}\n\`\`\`\n\nJawab pertanyaan berikut hanya berdasarkan data dokumen di atas: [Ketik pertanyaanmu di sini]`;
    } else if (mode === 'audit') {
        return `Audit dan telaah secara kritis dokumen "${filename}" berikut:\n\n\`\`\`markdown\n${content}\n\`\`\`\n\nIdentifikasi potensi celah, inkonsistensi data, atau risiko yang ada di dalamnya.`;
    }
    return content;
}

promptPreset.addEventListener('change', () => {
    if (!converted.length) return;
    const curr = converted[activeIdx];
    const rawText = (curr.chunks && curr.chunks.length > 0) ? curr.chunks[activeChunkIdx] : curr.markdown;
    outputArea.value = applyPromptPreset(rawText, curr.filename);
});

copyBtn.addEventListener('click', async () => {
    if (!outputArea.value) return;
    await navigator.clipboard.writeText(outputArea.value);
    const orig = copyBtn.innerHTML;
    copyBtn.innerHTML = `
        <svg class="w-3.5 h-3.5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
        <span>Tersalin!</span>
    `;
    setTimeout(() => copyBtn.innerHTML = orig, 1500);
});

mergeBtn.addEventListener('click', () => {
    if (!converted.length) return;
    const bundled = converted.map(f => `# FILE: ${f.filename}\n\n${f.markdown}\n\n---\n`).join('\n');
    const blob = new Blob([bundled], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bundle_ai_context_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
});

if (view1ApplyFrontmatterBtn) {
    view1ApplyFrontmatterBtn.addEventListener('click', async () => {
        if (!converted.length) return;
        const curr = converted[activeIdx];
        const preset = view1FrontmatterPreset ? view1FrontmatterPreset.value : 'obsidian';
        const orig = view1ApplyFrontmatterBtn.innerHTML;
        view1ApplyFrontmatterBtn.innerHTML = '<span>...</span>';
        try {
            const fd = new FormData();
            fd.append('markdown_text', curr.markdown);
            fd.append('filename', curr.filename);
            fd.append('preset', preset);
            const res = await fetch('/format-frontmatter', { method: 'POST', body: fd });
            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            if (data && data.markdown) {
                curr.markdown = data.markdown;
                curr.char_count = data.markdown.length;
                updateActiveView();
            }
        } catch (e) {
            alert('Gagal menerapkan frontmatter: ' + e.message);
        } finally {
            view1ApplyFrontmatterBtn.innerHTML = orig;
        }
    });
}

exportCurrentToDocxBtn.addEventListener('click', async () => {
    if (!outputArea.value) return;
    const curr = converted[activeIdx];
    const baseName = curr ? curr.filename.replace(/\.[^/.]+$/, "") : "Dokumen";
    
    exportCurrentToDocxBtn.disabled = true;
    const orig = exportCurrentToDocxBtn.innerHTML;
    exportCurrentToDocxBtn.innerHTML = `<span>Menyiapkan .docx...</span>`;

    try {
        const fd = new FormData();
        fd.append('markdown_text', outputArea.value);
        fd.append('filename', baseName);
        fd.append('theme', getSelectedTheme());

        const res = await fetch('/md-to-docx', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${baseName}.docx`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert('Gagal mengekspor DOCX: ' + err.message);
    } finally {
        exportCurrentToDocxBtn.disabled = false;
        exportCurrentToDocxBtn.innerHTML = orig;
    }
});

exportCurrentToPdfBtn.addEventListener('click', async () => {
    if (!outputArea.value) return;
    const curr = converted[activeIdx];
    const baseName = curr ? curr.filename.replace(/\.[^/.]+$/, "") : "Dokumen";
    
    exportCurrentToPdfBtn.disabled = true;
    const orig = exportCurrentToPdfBtn.innerHTML;
    exportCurrentToPdfBtn.innerHTML = `<span>Merender PDF...</span>`;

    try {
        const fd = new FormData();
        fd.append('markdown_text', outputArea.value);
        fd.append('filename', baseName);
        fd.append('theme', getSelectedTheme());

        const res = await fetch('/md-to-pdf', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${baseName}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert('Gagal mengekspor PDF: ' + err.message);
    } finally {
        exportCurrentToPdfBtn.disabled = false;
        exportCurrentToPdfBtn.innerHTML = orig;
    }
});

exportCurrentToHtmlBtn.addEventListener('click', async () => {
    if (!outputArea.value) return;
    const curr = converted[activeIdx];
    const baseName = curr ? curr.filename.replace(/\.[^/.]+$/, "") : "Dokumen";
    previewOrDownloadHtml(outputArea.value, baseName, false);
});

exportAllZipBtn.addEventListener('click', async () => {
    if (!converted || converted.length === 0) {
        alert('Belum ada dokumen yang terkonversi untuk diunduh.');
        return;
    }

    exportAllZipBtn.disabled = true;
    const orig = exportAllZipBtnText.textContent;
    exportAllZipBtnText.textContent = 'Mengemas ZIP...';

    try {
        const res = await fetch('/download-batch-zip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ items: converted })
        });

        if (!res.ok) throw new Error(await res.text());

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, '_');
        a.download = `doc2md_batch_export_${timestamp}.zip`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert('Gagal mengunduh berkas ZIP: ' + err.message);
    } finally {
        exportAllZipBtn.disabled = false;
        exportAllZipBtnText.textContent = orig;
    }
});

globalResetBtn.addEventListener('click', () => {
    if (confirm('Reset semua file dan kembalikan antarmuka ke kondisi awal?')) {
        resetAll();
    }
});

function resetAll() {
    converted = [];
    activeIdx = 0;
    activeChunkIdx = 0;
    fileInput.value = '';
    outputArea.value = '';
    workspace.classList.add('hidden');
    fileDetailsSection.classList.add('hidden');
    statsSummary.classList.add('hidden');
    chunkTabs.classList.add('hidden');
    fileCardsGrid.innerHTML = '';
    tabsContainer.innerHTML = '';
    statFiles.textContent = '0';
    statTokens.textContent = '0';

    // Also reset MD2Doc inputs
    mdInputArea.value = '';
    mdFileInput.value = '';
    mdFileSelectedName.textContent = 'Belum ada file dipilih';
    targetDocxName.value = 'Dokumen_Hasil_Konversi';
    updateMdStats();
}

mdDropzone.addEventListener('click', () => mdFileInput.click());
mdDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    mdDropzone.classList.add('border-indigo-500');
});
mdDropzone.addEventListener('dragleave', () => {
    mdDropzone.classList.remove('border-indigo-500');
});
mdDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    mdDropzone.classList.remove('border-indigo-500');
    if (e.dataTransfer.files.length) handleMdFile(e.dataTransfer.files[0]);
});
mdFileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleMdFile(e.target.files[0]);
});

function handleMdFile(file) {
    mdFileSelectedName.textContent = `${file.name} (${Math.round(file.size / 1024 * 10) / 10} KB)`;
    targetDocxName.value = file.name.replace(/\.[^/.]+$/, "");
    
    const reader = new FileReader();
    reader.onload = (e) => {
        mdInputArea.value = e.target.result;
        updateMdStats();
    };
    reader.readAsText(file);
}

mdInputArea.addEventListener('input', updateMdStats);
function updateMdStats() {
    const text = mdInputArea.value;
    mdCharCount.textContent = `${text.length.toLocaleString()} karakter`;
    mdLineCount.textContent = `${text ? text.split('\n').length : 0} baris`;
    renderLivePreview();
}

let previewDebounceTimer = null;
function renderLivePreview() {
    clearTimeout(previewDebounceTimer);
    previewDebounceTimer = setTimeout(() => {
        if (!mdLivePreview) return;
        const text = mdInputArea.value;
        if (!text || !text.trim()) {
            mdLivePreview.innerHTML = '<div class="text-slate-500 italic p-6 text-center">Pratinjau visual akan muncul otomatis di sini...</div>';
            return;
        }

        // 1. Parse markdown with Marked
        if (window.marked) {
            try {
                mdLivePreview.innerHTML = marked.parse(text);
            } catch (e) {
                mdLivePreview.innerHTML = `<div class="text-rose-400 p-2">Error parsing Markdown: ${e.message}</div>`;
                return;
            }
        } else {
            mdLivePreview.textContent = text;
        }

        // 2. Render KaTeX Math Expressions ($inline$ and $$block$$)
        if (window.renderMathInElement) {
            try {
                renderMathInElement(mdLivePreview, {
                    delimiters: [
                        { left: '$$', right: '$$', display: true },
                        { left: '$', right: '$', display: false },
                        { left: '\\(', right: '\\)', display: false },
                        { left: '\\[', right: '\\]', display: true }
                    ],
                    throwOnError: false
                });
            } catch (mathErr) {
                console.warn('KaTeX render error:', mathErr);
            }
        }

        // 3. Render Mermaid Flowcharts and Technical Diagrams
        if (window.mermaid) {
            try {
                const codeBlocks = mdLivePreview.querySelectorAll('code.language-mermaid, pre.mermaid');
                codeBlocks.forEach((block) => {
                    const pre = (block.tagName === 'PRE') ? block : block.parentElement;
                    const rawCode = block.textContent.trim();
                    const container = document.createElement('div');
                    container.className = 'mermaid';
                    container.textContent = rawCode;
                    pre.replaceWith(container);
                });

                const nodes = mdLivePreview.querySelectorAll('.mermaid');
                if (nodes.length > 0) {
                    mermaid.run({ nodes: nodes });
                }
            } catch (mErr) {
                console.warn('Mermaid render error:', mErr);
            }
        }
    }, 120);
}

function setEditorViewMode(mode) {
    if (mode === 'split') {
        editorLeftPane.classList.remove('hidden');
        editorRightPane.classList.remove('hidden');
        btnViewSplit.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        btnViewEdit.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
        btnViewPreview.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
        renderLivePreview();
    } else if (mode === 'edit') {
        editorLeftPane.classList.remove('hidden');
        editorRightPane.classList.add('hidden');
        btnViewSplit.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
        btnViewEdit.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        btnViewPreview.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
    } else if (mode === 'preview') {
        editorLeftPane.classList.add('hidden');
        editorRightPane.classList.remove('hidden');
        btnViewSplit.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
        btnViewEdit.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
        btnViewPreview.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        renderLivePreview();
    }
}

btnViewSplit.addEventListener('click', () => setEditorViewMode('split'));
btnViewEdit.addEventListener('click', () => setEditorViewMode('edit'));
btnViewPreview.addEventListener('click', () => setEditorViewMode('preview'));

async function previewOrDownloadHtml(markdownContent, baseName, download = false) {
    if (!markdownContent || !markdownContent.trim()) {
        alert('Silakan masukkan atau upload teks Markdown terlebih dahulu.');
        return;
    }
    try {
        const fd = new FormData();
        fd.append('markdown_text', markdownContent);
        fd.append('filename', baseName || 'dokumen');
        fd.append('download', download ? 'true' : 'false');
        fd.append('theme', getSelectedTheme());

        const res = await fetch('/md-to-html', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());

        if (download) {
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const safeName = (baseName.trim() || 'dokumen').replace(/\.html$/i, '') + '.html';
            a.download = safeName;
            a.click();
            URL.revokeObjectURL(url);
        } else {
            const htmlText = await res.text();
            const blob = new Blob([htmlText], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
        }
    } catch (err) {
        alert('Gagal menyiapkan tampilan cetak / HTML: ' + err.message);
    }
}

// Primary Urgent Action: Generate PDF
generatePdfBtn.addEventListener('click', async () => {
    const text = mdInputArea.value;
    if (!text.trim()) {
        alert('Silakan masukkan atau upload teks Markdown terlebih dahulu.');
        return;
    }

    generatePdfBtn.disabled = true;
    generatePdfBtnText.textContent = 'Merender PDF A4...';

    try {
        const fd = new FormData();
        fd.append('markdown_text', text);
        fd.append('filename', targetDocxName.value || 'dokumen');
        fd.append('theme', getSelectedTheme());

        const res = await fetch('/md-to-pdf', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeName = (targetDocxName.value.trim() || 'dokumen').replace(/\.pdf$/i, '') + '.pdf';
        a.download = safeName;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert('Gagal membuat PDF: ' + err.message);
    } finally {
        generatePdfBtn.disabled = false;
        generatePdfBtnText.textContent = 'Konversi & Unduh .PDF (A4 Rapi)';
    }
});

generateDocxBtn.addEventListener('click', async () => {
    const text = mdInputArea.value;
    if (!text.trim()) {
        alert('Silakan masukkan atau upload teks Markdown terlebih dahulu.');
        return;
    }

    generateDocxBtn.disabled = true;
    generateDocxBtnText.textContent = 'Membuat Dokumen Word...';

    try {
        const fd = new FormData();
        fd.append('markdown_text', text);
        fd.append('filename', targetDocxName.value || 'dokumen');
        fd.append('theme', getSelectedTheme());

        const res = await fetch('/md-to-docx', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const safeName = (targetDocxName.value.trim() || 'dokumen').replace(/\.docx$/i, '') + '.docx';
        a.download = safeName;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert('Gagal membuat DOCX: ' + err.message);
    } finally {
        generateDocxBtn.disabled = false;
        generateDocxBtnText.textContent = 'Konversi & Unduh .DOCX';
    }
});

generateHtmlBtn.addEventListener('click', () => {
    previewOrDownloadHtml(mdInputArea.value, targetDocxName.value || 'dokumen', false);
});

// Quick Editor Action Buttons
quickPdfBtn.addEventListener('click', () => generatePdfBtn.click());
quickDocxBtn.addEventListener('click', () => generateDocxBtn.click());
quickHtmlBtn.addEventListener('click', () => generateHtmlBtn.click());

if (addFrontmatterBtn) {
    addFrontmatterBtn.addEventListener('click', async () => {
        const text = mdInputArea.value;
        if (!text || !text.trim()) {
            alert('Silakan ketik atau unggah naskah Markdown terlebih dahulu.');
            return;
        }
        const preset = editorFrontmatterPreset ? editorFrontmatterPreset.value : 'obsidian';
        const fname = (targetDocxName.value.trim() || 'dokumen') + '.md';
        const orig = addFrontmatterBtn.innerHTML;
        addFrontmatterBtn.innerHTML = '<span>...</span>';
        try {
            const fd = new FormData();
            fd.append('markdown_text', text);
            fd.append('filename', fname);
            fd.append('preset', preset);
            const res = await fetch('/format-frontmatter', { method: 'POST', body: fd });
            if (!res.ok) throw new Error(await res.text());
            const data = await res.json();
            if (data && data.markdown) {
                mdInputArea.value = data.markdown;
                updateMdStats();
            }
        } catch (e) {
            alert('Gagal menyematkan YAML frontmatter: ' + e.message);
        } finally {
            addFrontmatterBtn.innerHTML = orig;
        }
    });
}

// Sample Presets
loadSampleReportBtn.addEventListener('click', () => {
    targetDocxName.value = 'Laporan_Analisis_Sistem';
    mdInputArea.value = `# Laporan Evaluasi Kinerja Sistem

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
`;
    updateMdStats();
});

loadSampleProposalBtn.addEventListener('click', () => {
    targetDocxName.value = 'Proposal_Pengembangan_Fitur';
    mdInputArea.value = `# Proposal Pengembangan Modul AI Studio

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
`;
    updateMdStats();
});

loadSampleMathDiagramBtn.addEventListener('click', () => {
    targetDocxName.value = 'Spesifikasi_Teknis_Diagram_dan_Formula';
    mdInputArea.value = `# Spesifikasi Teknis Pipeline & Optimasi Model

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
`;
    updateMdStats();
});

// ===================================================================
// FOLDER AUTO-WATCHER LOGIC
// ===================================================================
async function fetchWatcherStatus() {
    try {
        const res = await fetch('/watcher/status');
        if (!res.ok) return;
        const data = await res.json();
        updateWatcherUI(data);
    } catch (e) {
        console.warn('Watcher status fetch error:', e);
    }
}

function updateWatcherUI(data) {
    const isActive = data.is_active;

    if (isActive) {
        watcherStatusPill.textContent = 'AKTIF (MEMANTAU)';
        watcherStatusPill.className = 'text-[10px] font-semibold bg-emerald-950/90 text-emerald-300 border border-emerald-700/80 px-2 py-0.5 rounded-full font-mono flex items-center gap-1';
        watcherHeaderDot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
        watcherGlobalDot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
        watcherGlobalText.textContent = 'Watcher: LIVE';
        watcherGlobalText.className = 'text-emerald-400 font-mono text-[11px] font-semibold';
        btnStartWatcher.disabled = true;
        btnStartWatcher.className = 'px-4 py-2 rounded-xl bg-slate-800 text-slate-500 text-xs font-semibold transition flex items-center gap-1.5 border border-slate-700 cursor-not-allowed';
        btnStopWatcher.disabled = false;
        btnStopWatcher.className = 'px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold transition flex items-center gap-1.5 shadow-md shadow-rose-600/20';
    } else {
        watcherStatusPill.textContent = 'NONAKTIF';
        watcherStatusPill.className = 'text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700 px-2 py-0.5 rounded-full font-mono';
        watcherHeaderDot.className = 'w-2 h-2 rounded-full bg-slate-600';
        watcherGlobalDot.className = 'w-2 h-2 rounded-full bg-slate-600';
        watcherGlobalText.textContent = 'Watcher: OFF';
        watcherGlobalText.className = 'text-slate-400 font-mono text-[11px]';
        btnStartWatcher.disabled = false;
        btnStartWatcher.className = 'px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 shadow-md shadow-emerald-600/20';
        btnStopWatcher.disabled = true;
        btnStopWatcher.className = 'px-4 py-2 rounded-xl bg-slate-800 text-slate-500 text-xs font-semibold transition flex items-center gap-1.5 border border-slate-700 cursor-not-allowed';
    }

    if (data.input_dir && !isActive) watcherInputPath.value = data.input_dir;
    if (data.output_dir && !isActive) watcherOutputPath.value = data.output_dir;

    watcherTotalProcessedBadge.textContent = (data.total_processed || 0).toLocaleString();
    watcherHistoryCount.textContent = (data.recent_events || []).length;

    renderWatcherEvents(data.recent_events || []);
}

function renderWatcherEvents(events) {
    if (!events || events.length === 0) {
        watcherEmptyState.classList.remove('hidden');
        watcherFeedList.classList.add('hidden');
        watcherFeedList.innerHTML = '';
        return;
    }

    watcherEmptyState.classList.add('hidden');
    watcherFeedList.classList.remove('hidden');
    watcherFeedList.innerHTML = '';

    events.forEach(ev => {
        const item = document.createElement('div');
        item.className = 'p-3.5 hover:bg-slate-900/60 transition flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs';
        const isSuccess = ev.status === 'success';
        const ext = (ev.filename.split('.').pop() || '').toUpperCase();

        item.innerHTML = `
            <div class="flex items-start gap-2.5 overflow-hidden">
                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-sky-400 border border-slate-700 shrink-0 font-mono">${ext}</span>
                <div class="overflow-hidden">
                    <div class="flex items-center gap-2">
                        <span class="font-semibold text-slate-200 truncate" title="${ev.filename}">${ev.filename}</span>
                        ${isSuccess 
                            ? `<span class="text-[10px] px-1.5 py-0.2 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 font-medium">Auto-Converted</span>`
                            : `<span class="text-[10px] px-1.5 py-0.2 rounded bg-rose-950/80 text-rose-400 border border-rose-800/60 font-medium" title="${ev.error || ''}">Gagal</span>`
                        }
                    </div>
                    <div class="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5 font-mono">
                        <span>${ev.timestamp}</span>
                        <span>•</span>
                        <span class="text-slate-500 truncate" title="${ev.output_path || ''}">${ev.output_path ? ev.output_path.split(/[\\\\/]/).pop() : 'No output'}</span>
                    </div>
                </div>
            </div>
            <div class="flex items-center gap-2 self-end sm:self-center shrink-0 font-mono text-[11px]">
                ${(ev.images_count > 0) ? `<span class="bg-amber-950/80 text-amber-300 border border-amber-800/60 px-2 py-0.5 rounded text-[10px] font-sans">🖼️ ${ev.images_count} aset</span>` : ''}
                ${(ev.chunks_count > 0) ? `<span class="bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 px-2 py-0.5 rounded text-[10px] font-sans">✂️ ${ev.chunks_count} parts</span>` : ''}
                <span class="text-emerald-400 font-bold bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">${(ev.token_count || 0).toLocaleString()} tokens</span>
            </div>
        `;
        watcherFeedList.appendChild(item);
    });
}

btnStartWatcher.addEventListener('click', async () => {
    const inPath = watcherInputPath.value.trim() || 'watch_input';
    const outPath = watcherOutputPath.value.trim() || 'watch_output';
    const fmPreset = watcherFrontmatterSelect.value;
    const chunkTokens = watcherChunkSelect.value;

    btnStartWatcher.disabled = true;
    btnStartWatcher.innerHTML = `<span>Memulai...</span>`;

    try {
        const fd = new FormData();
        fd.append('input_dir', inPath);
        fd.append('output_dir', outPath);
        fd.append('frontmatter_preset', fmPreset);
        fd.append('chunk_tokens', chunkTokens);

        const res = await fetch('/watcher/start', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());
        await res.json();
        fetchWatcherStatus();
    } catch (err) {
        alert('Gagal memulai Folder Watcher: ' + err.message);
        fetchWatcherStatus();
    }
});

btnStopWatcher.addEventListener('click', async () => {
    btnStopWatcher.disabled = true;
    btnStopWatcher.innerHTML = `<span>Menghentikan...</span>`;
    try {
        const res = await fetch('/watcher/stop', { method: 'POST' });
        if (!res.ok) throw new Error(await res.text());
        fetchWatcherStatus();
    } catch (err) {
        alert('Gagal menghentikan Folder Watcher: ' + err.message);
        fetchWatcherStatus();
    }
});

btnResetInputPath.addEventListener('click', () => { watcherInputPath.value = 'watch_input'; });
btnResetOutputPath.addEventListener('click', () => { watcherOutputPath.value = 'watch_output'; });
btnRefreshWatcherHistory.addEventListener('click', fetchWatcherStatus);
btnClearWatcherHistory.addEventListener('click', async () => {
    if (confirm('Bersihkan seluruh log riwayat aktivitas watcher?')) {
        await fetch('/watcher/clear-history', { method: 'POST' });
        fetchWatcherStatus();
    }
});

setInterval(fetchWatcherStatus, 3000);
fetchWatcherStatus();

// ===================================================================
// VISUAL DOCUMENT DIFF VIEWER LOGIC
// ===================================================================
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")
              .replace(/"/g, "&quot;")
              .replace(/'/g, "&#039;");
}

let currentDiffData = null;

async function executeDiff() {
    const textA = diffInputA.value;
    const textB = diffInputB.value;
    const titleA = diffTitleA.value.trim() || 'Dokumen A';
    const titleB = diffTitleB.value.trim() || 'Dokumen B';

    if (!textA.trim() && !textB.trim()) {
        alert('Silakan masukkan atau upload naskah pada Dokumen A dan Dokumen B untuk dibandingkan.');
        return;
    }

    btnExecuteDiff.disabled = true;
    const orig = btnExecuteDiff.innerHTML;
    btnExecuteDiff.innerHTML = `<span>Membandingkan...</span>`;

    try {
        const fd = new FormData();
        fd.append('text_a', textA);
        fd.append('text_b', textB);
        fd.append('title_a', titleA);
        fd.append('title_b', titleB);

        const res = await fetch('/diff', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());
        currentDiffData = await res.json();
        renderDiffResults(currentDiffData);
    } catch (err) {
        alert('Gagal membandingkan dokumen: ' + err.message);
    } finally {
        btnExecuteDiff.disabled = false;
        btnExecuteDiff.innerHTML = orig;
    }
}

function renderDiffResults(data) {
    diffResultsSection.classList.remove('hidden');
    diffSimilarityScore.textContent = `${data.similarity_ratio}%`;
    
    const stats = data.stats;
    const dTokens = stats.delta_tokens;
    if (dTokens > 0) {
        diffTokenDelta.textContent = `+${dTokens.toLocaleString()}`;
        diffTokenDelta.className = 'text-base font-bold font-mono text-emerald-400';
    } else if (dTokens < 0) {
        diffTokenDelta.textContent = dTokens.toLocaleString();
        diffTokenDelta.className = 'text-base font-bold font-mono text-rose-400';
    } else {
        diffTokenDelta.textContent = '0';
        diffTokenDelta.className = 'text-base font-bold font-mono text-slate-300';
    }

    diffTokenA.textContent = stats.tokens_a.toLocaleString();
    diffTokenB.textContent = stats.tokens_b.toLocaleString();

    diffAddedLines.textContent = `+${stats.added_lines}`;
    diffRemovedLines.textContent = `-${stats.removed_lines}`;
    diffModifiedLines.textContent = `~${stats.modified_lines}`;

    diffHeadTitleA.textContent = data.title_a;
    diffHeadTitleB.textContent = data.title_b;

    // Render Side-by-Side
    diffSideBySideTableBody.innerHTML = '';
    (data.side_by_side || []).forEach(row => {
        const tr = document.createElement('tr');
        const rowType = row.type; // equal, replace, delete, insert

        let leftBg = '';
        let rightBg = '';

        if (rowType === 'replace') {
            leftBg = row.left ? 'bg-rose-950/40 text-rose-200 border-l-2 border-rose-500' : 'bg-slate-950/80 text-slate-600';
            rightBg = row.right ? 'bg-emerald-950/40 text-emerald-200 border-l-2 border-emerald-500' : 'bg-slate-950/80 text-slate-600';
        } else if (rowType === 'delete') {
            leftBg = 'bg-rose-950/40 text-rose-200 border-l-2 border-rose-500';
            rightBg = 'bg-slate-950/80 text-slate-600';
        } else if (rowType === 'insert') {
            leftBg = 'bg-slate-950/80 text-slate-600';
            rightBg = 'bg-emerald-950/40 text-emerald-200 border-l-2 border-emerald-500';
        } else {
            leftBg = 'text-slate-300 hover:bg-slate-850/40';
            rightBg = 'text-slate-300 hover:bg-slate-850/40';
        }

        const leftNum = row.left ? row.left.num : '';
        const leftTxt = row.left ? escapeHtml(row.left.text) : '';
        const rightNum = row.right ? row.right.num : '';
        const rightTxt = row.right ? escapeHtml(row.right.text) : '';

        tr.innerHTML = `
            <td class="w-12 py-1 px-2 text-right text-slate-600 select-none bg-slate-950/60 border-r border-slate-800">${leftNum}</td>
            <td class="py-1 px-3 border-r border-slate-800 whitespace-pre-wrap break-all ${leftBg}">${leftTxt}</td>
            <td class="w-12 py-1 px-2 text-right text-slate-600 select-none bg-slate-950/60 border-r border-slate-800">${rightNum}</td>
            <td class="py-1 px-3 whitespace-pre-wrap break-all ${rightBg}">${rightTxt}</td>
        `;
        diffSideBySideTableBody.appendChild(tr);
    });

    // Render Unified
    diffUnifiedTableBody.innerHTML = '';
    (data.unified || []).forEach(u => {
        const tr = document.createElement('tr');
        let symbol = ' ';
        let rowBg = '';
        let symbolClass = 'text-slate-600';

        if (u.type === 'delete') {
            symbol = '-';
            rowBg = 'bg-rose-950/40 text-rose-200 border-l-2 border-rose-500';
            symbolClass = 'text-rose-400 font-bold';
        } else if (u.type === 'insert') {
            symbol = '+';
            rowBg = 'bg-emerald-950/40 text-emerald-200 border-l-2 border-emerald-500';
            symbolClass = 'text-emerald-400 font-bold';
        } else {
            rowBg = 'text-slate-300 hover:bg-slate-850/40';
        }

        const lNum = u.left_num ? u.left_num : '';
        const rNum = u.right_num ? u.right_num : '';

        tr.innerHTML = `
            <td class="w-12 py-1 px-2 text-right text-slate-600 select-none bg-slate-950/60 border-r border-slate-800">${lNum}</td>
            <td class="w-12 py-1 px-2 text-right text-slate-600 select-none bg-slate-950/60 border-r border-slate-800">${rNum}</td>
            <td class="w-8 py-1 px-1 text-center select-none bg-slate-950/60 border-r border-slate-800 ${symbolClass}">${symbol}</td>
            <td class="py-1 px-3 whitespace-pre-wrap break-all ${rowBg}">${escapeHtml(u.text)}</td>
        `;
        diffUnifiedTableBody.appendChild(tr);
    });

    diffResultsSection.scrollIntoView({ behavior: 'smooth' });
}

btnExecuteDiff.addEventListener('click', executeDiff);

btnDiffSideBySide.addEventListener('click', () => {
    diffSideBySideContainer.classList.remove('hidden');
    diffUnifiedContainer.classList.add('hidden');
    btnDiffSideBySide.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
    btnDiffUnified.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
});

btnDiffUnified.addEventListener('click', () => {
    diffSideBySideContainer.classList.add('hidden');
    diffUnifiedContainer.classList.remove('hidden');
    btnDiffUnified.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
    btnDiffSideBySide.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
});

btnSwapDiff.addEventListener('click', () => {
    const tmpTxt = diffInputA.value;
    diffInputA.value = diffInputB.value;
    diffInputB.value = tmpTxt;

    const tmpTitle = diffTitleA.value;
    diffTitleA.value = diffTitleB.value;
    diffTitleB.value = tmpTitle;

    if (diffInputA.value.trim() || diffInputB.value.trim()) {
        executeDiff();
    }
});

btnPullFromActiveDoc.addEventListener('click', () => {
    if (converted.length && converted[activeIdx]) {
        diffInputA.value = converted[activeIdx].markdown;
        diffTitleA.value = converted[activeIdx].filename;
    } else if (outputArea.value.trim()) {
        diffInputA.value = outputArea.value;
        diffTitleA.value = "Dokumen Terkonversi Aktif";
    } else {
        alert('Belum ada dokumen aktif yang terkonversi di View 1.');
    }
});

btnPullFromStudioDoc.addEventListener('click', () => {
    if (mdInputArea.value.trim()) {
        diffInputB.value = mdInputArea.value;
        diffTitleB.value = (targetDocxName.value.trim() || 'Editor Studio') + '.md';
    } else {
        alert('Editor Markdown Studio masih kosong.');
    }
});

function handleDiffFileUpload(file, targetInput, targetTitle) {
    targetTitle.value = file.name;
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    if (ext === 'txt' || ext === 'md') {
        const reader = new FileReader();
        reader.onload = (e) => {
            targetInput.value = e.target.result;
        };
        reader.readAsText(file);
    } else {
        const fd = new FormData();
        fd.append('files', file);
        fd.append('chunk_tokens', '0');
        fetch('/convert', { method: 'POST', body: fd })
            .then(r => r.json())
            .then(d => {
                if (d.results && d.results[0] && d.results[0].status === 'success') {
                    targetInput.value = d.results[0].markdown;
                } else {
                    alert('Gagal mengekstrak teks dokumen.');
                }
            })
            .catch(e => alert('Error upload: ' + e.message));
    }
}

diffFileInputA.addEventListener('change', (e) => {
    if (e.target.files.length) handleDiffFileUpload(e.target.files[0], diffInputA, diffTitleA);
});

diffFileInputB.addEventListener('change', (e) => {
    if (e.target.files.length) handleDiffFileUpload(e.target.files[0], diffInputB, diffTitleB);
});

btnLoadDiffSample.addEventListener('click', () => {
    diffTitleA.value = "Proposal_Sistem_v1.md";
    diffTitleB.value = "Proposal_Sistem_v2_Revisi.md";

    diffInputA.value = `# Proposal Pengembangan Sistem Dokumen AI

Berikut adalah rancangan awal arsitektur sistem konversi dokumen.

## 1. Latar Belakang
Pengguna membutuhkan solusi cepat untuk mengubah file PDF lama ke Markdown.
Sistem saat ini belum memiliki offline OCR.

## 2. Fitur Utama
- Konversi format DOCX dan PDF
- Ekspor kembali ke file Word
- Penyimpanan lokal sementara

## 3. Estimasi Jadwal
- Tahap 1: Analisis kebutuhan (1 minggu)
- Tahap 2: Pengujian performa (2 minggu)
`;

    diffInputB.value = `# Proposal Pengembangan Sistem Dokumen AI (Revisi Kuartal 4)

Berikut adalah rancangan final arsitektur sistem konversi dokumen dengan kemampuan offline penuh.

## 1. Latar Belakang
Pengguna membutuhkan solusi cepat untuk mengubah file PDF lama ke Markdown.
Sistem kini dilengkapi RapidOCR ONNX Runtime 100% offline dan pemantau folder otomatis.

## 2. Fitur Utama
- Konversi multi-format (DOCX, PDF, XLSX, PPTX, Gambar)
- Preservasi gambar asli & auto-linking Markdown
- Ekspor kembali ke file Word (.DOCX) & PDF A4 anti-potong
- Folder Watcher untuk konversi otomatis hands-free
- Visual Document Diff Viewer

## 3. Estimasi Jadwal & Hasil
- Tahap 1: Analisis kebutuhan & arsitektur core (1 minggu)
- Tahap 2: Implementasi 8 fitur unggulan (Selesai)
- Tahap 3: Peluncuran versi rilis produksi
`;

    executeDiff();
});
