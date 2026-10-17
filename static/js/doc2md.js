let converted = window.converted || [];
let activeIdx = window.activeIdx || 0;
let activeChunkIdx = (window.activeChunkIdx !== undefined) ? window.activeChunkIdx : -1;
const globalResetBtn = el('globalResetBtn');
const dropzone = el('dropzone'), dropzoneNormal = el('dropzoneNormal'), dropzoneLoading = el('dropzoneLoading');
const fileInput = el('fileInput'), chunkSelect = el('chunkSelect'), frontmatterSelect = el('frontmatterSelect');
const view1FrontmatterPreset = el('view1FrontmatterPreset'), view1ApplyFrontmatterBtn = el('view1ApplyFrontmatterBtn');
const quickStatusBadge = el('quickStatusBadge'), uploadStatusText = el('uploadStatusText');
const fileDetailsSection = el('fileDetailsSection'), fileDetailsCount = el('fileDetailsCount'), fileCardsGrid = el('fileCardsGrid');
const workspace = el('workspace'), tabsContainer = el('tabsContainer'), chunkTabs = el('chunkTabs'), chunkBtnList = el('chunkBtnList');
const outputArea = el('outputArea'), activeFileInfo = el('activeFileInfo'), savingStat = el('savingStat');
const tokenBadge = el('tokenBadge'), statsSummary = el('statsSummary'), statFiles = el('statFiles'), statTokens = el('statTokens');
const promptPreset = el('promptPreset'), copyBtn = el('copyBtn'), downloadActiveMdBtn = el('downloadActiveMdBtn'), mergeBtn = el('mergeBtn');
const exportCurrentToDocxBtn = el('exportCurrentToDocxBtn'), exportCurrentToPdfBtn = el('exportCurrentToPdfBtn');
const exportCurrentToHtmlBtn = el('exportCurrentToHtmlBtn'), exportAllZipBtn = el('exportAllZipBtn'), exportAllZipBtnText = el('exportAllZipBtnText');

function syncGlobalDocState() {
    window.converted = converted;
    window.activeIdx = activeIdx;
    window.activeChunkIdx = activeChunkIdx;
}

if (dropzone) {
    dropzone.addEventListener('click', () => fileInput && fileInput.click());
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('border-sky-500', 'bg-sky-950/20');
    });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('border-sky-500', 'bg-sky-950/20'));
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('border-sky-500', 'bg-sky-950/20');
        if (e.dataTransfer.files.length) upload(e.dataTransfer.files);
    });
}

if (fileInput) fileInput.addEventListener('change', (e) => { if (e.target.files.length) upload(e.target.files); });

async function upload(files) {
    const fd = new FormData();
    for (let f of files) fd.append('files', f);
    fd.append('chunk_tokens', chunkSelect ? chunkSelect.value : '0');
    fd.append('frontmatter_preset', frontmatterSelect ? frontmatterSelect.value : 'none');

    if (dropzoneNormal) dropzoneNormal.classList.add('hidden');
    if (dropzoneLoading) dropzoneLoading.classList.remove('hidden');
    if (dropzone) dropzone.classList.add('pointer-events-none', 'border-sky-500/60');
    if (quickStatusBadge) { quickStatusBadge.textContent = 'Memproses...'; quickStatusBadge.className = 'text-sky-400 font-medium animate-pulse'; }
    if (uploadStatusText) uploadStatusText.textContent = `Mengonversi ${files.length} dokumen...`;

    try {
        const res = await fetch('/convert', { method: 'POST', body: fd });
        const data = await res.json();
        const newSuccess = (data.results || []).filter(r => r.status === 'success');
        const errors = (data.results || []).filter(r => r.status === 'error');

        if (errors.length > 0 && newSuccess.length === 0) {
            alert(`Gagal memproses file:\n${errors.map(e => e.filename + ': ' + e.error).join('\n')}`);
            return;
        }
        if (!newSuccess.length) { alert('Gagal memproses file. Pastikan format didukung.'); return; }

        converted = [...converted, ...newSuccess];
        activeIdx = converted.length - newSuccess.length;
        activeChunkIdx = -1;
        syncGlobalDocState();
        renderAll();
    } catch (err) {
        alert('Terjadi kesalahan saat mengunggah: ' + err.message);
    } finally {
        if (dropzoneNormal) dropzoneNormal.classList.remove('hidden');
        if (dropzoneLoading) dropzoneLoading.classList.add('hidden');
        if (dropzone) dropzone.classList.remove('pointer-events-none', 'border-sky-500/60');
        if (quickStatusBadge) { quickStatusBadge.textContent = 'Siap'; quickStatusBadge.className = 'text-emerald-400 font-medium'; }
        if (fileInput) fileInput.value = '';
    }
}

function renderAll() {
    renderFileCards();
    renderWorkspace();
}

function renderFileCards() {
    if (!fileDetailsSection || !fileCardsGrid) return;
    if (!converted.length) { fileDetailsSection.classList.add('hidden'); return; }
    fileDetailsSection.classList.remove('hidden');
    if (fileDetailsCount) fileDetailsCount.textContent = converted.length;
    fileCardsGrid.innerHTML = '';

    converted.forEach((item, idx) => {
        const ext = (item.filename.split('.').pop() || '').toUpperCase();
        const card = document.createElement('div');
        const isActive = (idx === activeIdx);
        card.className = `p-3.5 rounded-xl border transition cursor-pointer flex flex-col justify-between gap-2.5 ${
            isActive ? 'bg-sky-950/40 border-sky-500/80 shadow-md shadow-sky-500/10' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
        }`;

        const ocrTag = item.is_ocr ? `<span class="bg-purple-950/80 text-purple-300 border border-purple-800/60 px-1.5 py-0.5 rounded text-[10px] font-sans font-medium">🔍 OCR</span>` : '';
        const imgTag = (item.images_count && item.images_count > 0) ? `<span class="bg-amber-950/80 text-amber-300 border border-amber-800/60 px-1.5 py-0.5 rounded text-[10px] font-sans">🖼️ ${item.images_count}</span>` : '';

        card.innerHTML = `<div class="flex items-start justify-between gap-2">
            <div class="flex items-center gap-2 overflow-hidden">
                <span class="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-800 text-sky-400 border border-slate-700 shrink-0 font-mono">${ext}</span>
                <span class="text-xs font-semibold text-slate-200 truncate" title="${item.filename}">${item.filename}</span>
            </div>
            <button class="remove-btn text-slate-500 hover:text-rose-400 transition p-0.5 rounded" title="Hapus file ini" data-idx="${idx}"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg></button>
        </div>
        <div class="flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>${item.raw_size_kb} KB</span>
            <div class="flex items-center gap-1.5">${ocrTag}${imgTag}<span class="text-emerald-400 font-semibold">${item.token_count.toLocaleString()} tokens</span></div>
        </div>`;

        card.onclick = (e) => {
            if (e.target.closest('.remove-btn')) return;
            activeIdx = idx; activeChunkIdx = -1; syncGlobalDocState(); renderAll();
        };

        const rmBtn = card.querySelector('.remove-btn');
        if (rmBtn) rmBtn.onclick = (e) => { e.stopPropagation(); removeFile(idx); };
        fileCardsGrid.appendChild(card);
    });
}

function removeFile(index) {
    converted.splice(index, 1);
    if (activeIdx >= converted.length) activeIdx = Math.max(0, converted.length - 1);
    activeChunkIdx = -1;
    syncGlobalDocState();
    if (converted.length === 0) resetAll(); else renderAll();
}

function renderWorkspace() {
    if (!workspace || !statsSummary) return;
    if (!converted.length) { workspace.classList.add('hidden'); statsSummary.classList.add('hidden'); return; }

    workspace.classList.remove('hidden');
    statsSummary.classList.remove('hidden');
    if (statFiles) statFiles.textContent = converted.length;
    if (statTokens) statTokens.textContent = converted.reduce((acc, cur) => acc + cur.token_count, 0).toLocaleString();

    if (tabsContainer) {
        tabsContainer.innerHTML = '';
        converted.forEach((item, idx) => {
            const tab = document.createElement('button');
            const isSelected = (idx === activeIdx);
            tab.className = `px-3 py-1.5 rounded-lg text-xs font-medium truncate max-w-[160px] border transition ${
                isSelected ? 'bg-sky-600 text-white border-sky-500 shadow-sm' : 'bg-slate-950 text-slate-300 border-slate-800 hover:bg-slate-800'
            }`;
            tab.textContent = item.filename;
            tab.onclick = () => { activeIdx = idx; activeChunkIdx = -1; syncGlobalDocState(); renderAll(); };
            tabsContainer.appendChild(tab);
        });
    }
    updateActiveView();
}

function updateActiveView() {
    if (!converted.length) return;
    const curr = converted[activeIdx];
    if (!curr) return;
    
    if (curr.chunks && curr.chunks.length > 1 && chunkTabs && chunkBtnList) {
        chunkTabs.classList.remove('hidden');
        chunkBtnList.innerHTML = '';

        // Tab Semua (Utuh)
        const allBtn = document.createElement('button');
        allBtn.className = `px-2.5 py-1 rounded-md text-[11px] font-mono border transition ${
            activeChunkIdx === -1 ? 'bg-sky-600 text-white border-sky-500 shadow-sm font-semibold' : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
        }`;
        allBtn.textContent = `Semua (Utuh)`;
        allBtn.title = `Tampilkan dan ekspor dokumen lengkap tanpa pemotongan chunk`;
        allBtn.onclick = () => { activeChunkIdx = -1; syncGlobalDocState(); updateActiveView(); };
        chunkBtnList.appendChild(allBtn);

        curr.chunks.forEach((_, cIdx) => {
            const cBtn = document.createElement('button');
            cBtn.className = `px-2.5 py-1 rounded-md text-[11px] font-mono border transition ${
                cIdx === activeChunkIdx ? 'bg-indigo-600 text-white border-indigo-500 shadow-sm font-semibold' : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`;
            cBtn.textContent = `Part ${cIdx + 1}`;
            cBtn.onclick = () => { activeChunkIdx = cIdx; syncGlobalDocState(); updateActiveView(); };
            chunkBtnList.appendChild(cBtn);
        });
    } else if (chunkTabs) {
        chunkTabs.classList.add('hidden');
    }

    const rawText = (activeChunkIdx >= 0 && curr.chunks && curr.chunks.length > 0) ? curr.chunks[activeChunkIdx] : curr.markdown;
    if (outputArea) outputArea.value = applyPromptPreset(rawText, curr.filename);
    const imgNote = (curr.images_count && curr.images_count > 0) ? ` • 🖼️ ${curr.images_count} gambar diekstrak` : '';
    if (activeFileInfo) activeFileInfo.textContent = `${curr.filename} • ${curr.raw_size_kb} KB raw${imgNote}`;
    if (savingStat) savingStat.textContent = `${curr.char_count.toLocaleString()} karakter`;
    if (tokenBadge) tokenBadge.textContent = `${curr.token_count.toLocaleString()} tokens`;
}

function applyPromptPreset(content, filename) {
    const mode = promptPreset ? promptPreset.value : 'raw';
    if (mode === 'summarize') return `Berikut adalah dokumen "${filename}":\n\n\`\`\`markdown\n${content}\n\`\`\`\n\nTolong buat ringkasan komprehensif, poin-poin keputusan terpenting, dan action items dari dokumen di atas.`;
    if (mode === 'qa') return `Gunakan dokumen "${filename}" berikut sebagai referensi utama menjawab pertanyaan:\n\n\`\`\`markdown\n${content}\n\`\`\`\n\nJawab pertanyaan berikut hanya berdasarkan data dokumen di atas: [Ketik pertanyaanmu di sini]`;
    if (mode === 'audit') return `Audit dan telaah secara kritis dokumen "${filename}" berikut:\n\n\`\`\`markdown\n${content}\n\`\`\`\n\nIdentifikasi potensi celah, inkonsistensi data, atau risiko yang ada di dalamnya.`;
    return content;
}

if (promptPreset) {
    promptPreset.addEventListener('change', () => {
        if (!converted.length) return;
        const curr = converted[activeIdx];
        if (!curr) return;
        const rawText = (activeChunkIdx >= 0 && curr.chunks && curr.chunks.length > 0) ? curr.chunks[activeChunkIdx] : curr.markdown;
        if (outputArea) outputArea.value = applyPromptPreset(rawText, curr.filename);
    });
}

if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
        if (!outputArea || !outputArea.value) return;
        await navigator.clipboard.writeText(outputArea.value);
        const orig = copyBtn.innerHTML;
        copyBtn.innerHTML = `<svg class="w-3.5 h-3.5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg><span>Tersalin!</span>`;
        setTimeout(() => copyBtn.innerHTML = orig, 1500);
    });
}

if (downloadActiveMdBtn) {
    downloadActiveMdBtn.addEventListener('click', () => {
        if (!converted.length) return;
        const curr = converted[activeIdx];
        if (!curr) return;
        const textToDownload = (activeChunkIdx >= 0 && curr.chunks && curr.chunks.length > 0) ? curr.chunks[activeChunkIdx] : curr.markdown;
        const baseName = curr.filename.replace(/\.[^/.]+$/, "");
        const suffix = (activeChunkIdx >= 0 && curr.chunks && curr.chunks.length > 1) ? `_part_${activeChunkIdx + 1}` : '';
        triggerDownload(new Blob([textToDownload], { type: 'text/markdown;charset=utf-8' }), `${baseName}${suffix}.md`);
    });
}

if (mergeBtn) {
    mergeBtn.addEventListener('click', () => {
        if (!converted.length) return;
        const bundled = converted.map(f => `# FILE: ${f.filename}\n\n${f.markdown}\n\n---\n`).join('\n');
        triggerDownload(new Blob([bundled], { type: 'text/markdown' }), `bundle_ai_context_${Date.now()}.md`);
    });
}

if (view1ApplyFrontmatterBtn) {
    view1ApplyFrontmatterBtn.addEventListener('click', async () => {
        if (!converted.length) return;
        const curr = converted[activeIdx];
        if (!curr) return;
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

async function handleExportCurrent(btn, endpoint, ext, label) {
    if (!outputArea || !outputArea.value) return;
    const curr = converted[activeIdx];
    const baseName = curr ? curr.filename.replace(/\.[^/.]+$/, "") : "Dokumen";
    btn.disabled = true;
    const orig = btn.innerHTML;
    btn.innerHTML = `<span>${label}...</span>`;
    try {
        await exportDocument(endpoint, outputArea.value, baseName, ext);
    } catch (err) {
        alert(`Gagal mengekspor ${ext.toUpperCase()}: ` + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = orig;
    }
}

if (exportCurrentToDocxBtn) exportCurrentToDocxBtn.addEventListener('click', () => handleExportCurrent(exportCurrentToDocxBtn, '/md-to-docx', 'docx', 'Menyiapkan .docx'));
if (exportCurrentToPdfBtn) exportCurrentToPdfBtn.addEventListener('click', () => handleExportCurrent(exportCurrentToPdfBtn, '/md-to-pdf', 'pdf', 'Merender PDF'));

if (exportCurrentToHtmlBtn) {
    exportCurrentToHtmlBtn.addEventListener('click', () => {
        if (!outputArea || !outputArea.value) return;
        const curr = converted[activeIdx];
        const baseName = curr ? curr.filename.replace(/\.[^/.]+$/, "") : "Dokumen";
        if (typeof previewOrDownloadHtml === 'function') {
            previewOrDownloadHtml(outputArea.value, baseName, true);
        } else {
            exportDocument('/md-to-html', outputArea.value, baseName, 'html');
        }
    });
}

if (exportAllZipBtn) {
    exportAllZipBtn.addEventListener('click', async () => {
        if (!converted || converted.length === 0) {
            alert('Belum ada dokumen yang terkonversi untuk diunduh.');
            return;
        }
        exportAllZipBtn.disabled = true;
        const orig = exportAllZipBtnText ? exportAllZipBtnText.textContent : 'Batch Unduh (.ZIP)';
        if (exportAllZipBtnText) exportAllZipBtnText.textContent = 'Mengemas ZIP...';
        try {
            const res = await fetch('/download-batch-zip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ items: converted })
            });
            if (!res.ok) throw new Error(await res.text());
            const blob = await res.blob();
            const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:T]/g, '_');
            triggerDownload(blob, `doc2md_batch_export_${timestamp}.zip`);
        } catch (err) {
            alert('Gagal mengunduh berkas ZIP: ' + err.message);
        } finally {
            exportAllZipBtn.disabled = false;
            if (exportAllZipBtnText) exportAllZipBtnText.textContent = orig;
        }
    });
}

window.resetDoc2Md = function() {
    converted = [];
    activeIdx = 0;
    activeChunkIdx = -1;
    syncGlobalDocState();
    ['fileInput', 'outputArea'].forEach(id => { const i = el(id); if (i) i.value = ''; });
    ['workspace', 'fileDetailsSection', 'chunkTabs'].forEach(id => { const c = el(id); if (c) c.classList.add('hidden'); });
    ['fileCardsGrid', 'tabsContainer', 'chunkBtnList'].forEach(id => { const g = el(id); if (g) g.innerHTML = ''; });
    if (statFiles) statFiles.textContent = '0';
    if (statTokens) statTokens.textContent = '0';
    if (chunkSelect) chunkSelect.value = '0';
    if (frontmatterSelect) frontmatterSelect.value = 'none';
    if (promptPreset) promptPreset.value = 'raw';
};

function resetAll() {
    window.resetDoc2Md();
}
