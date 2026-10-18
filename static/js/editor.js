// DOM Element References
const targetDocxName = document.getElementById('targetDocxName');
const mdDropzone = document.getElementById('mdDropzone');
const mdFileInput = document.getElementById('mdFileInput');
const mdFileSelectedName = document.getElementById('mdFileSelectedName');
const mdQueueContainer = document.getElementById('mdQueueContainer');
const mdQueueList = document.getElementById('mdQueueList');
const mdQueueCount = document.getElementById('mdQueueCount');
const clearQueueBtn = document.getElementById('clearQueueBtn');
const batchConvertQueueBtn = document.getElementById('batchConvertQueueBtn');
const batchConvertQueueBtnText = document.getElementById('batchConvertQueueBtnText');
const restoreUserFileBtn = document.getElementById('restoreUserFileBtn');
const templateActiveBadge = document.getElementById('templateActiveBadge');
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
const editorDualContainer = document.getElementById('editorDualContainer');
const editorLeftPane = document.getElementById('editorLeftPane');
const editorRightPane = document.getElementById('editorRightPane');
const mdLivePreview = document.getElementById('mdLivePreview');
const loadSampleReportBtn = document.getElementById('loadSampleReportBtn');
const loadSampleProposalBtn = document.getElementById('loadSampleProposalBtn');
const loadSampleMathDiagramBtn = document.getElementById('loadSampleMathDiagramBtn');
// State Variables
let mdFileQueue = [];
let activeQueueId = null;
let userOriginalFile = null; // Backup for "Kembali ke Berkas Saya"
let isTemplateActive = false;

// Theme configuration presets
const THEME_INFO = {
    'modern_slate': { color: '#0ea5e9', desc: 'Aksen Sky Blue modern, font sans rapi, cocok untuk laporan umum.' },
    'corporate_navy': { color: '#1e3a8a', desc: 'Aksen Royal Navy formal, border solid berbobot, cocok untuk proposal & MoU resmi.' },
    'classic_academic': { color: '#475569', desc: 'Tipografi Georgia serif klasik, spasi formal, cocok untuk jurnal ilmiah & makalah.' },
    'emerald_tech': { color: '#059669', desc: 'Aksen Emerald Green kontemporer & font teknis, ideal untuk dokumentasi teknis & API.' }
};

// Helper to read File as Text with Promise
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result || '');
        reader.onerror = (e) => reject(e);
        reader.readAsText(file, 'utf-8');
    });
}

// Queue Management
function renderQueue() {
    if (!mdQueueContainer || !mdQueueList) return;
    
    if (mdQueueCount) mdQueueCount.textContent = mdFileQueue.length;
    
    if (mdFileQueue.length > 0) {
        mdQueueContainer.classList.remove('hidden');
        mdQueueContainer.classList.add('flex');
    } else {
        mdQueueContainer.classList.add('hidden');
        mdQueueContainer.classList.remove('flex');
    }

    const batchQueueOptions = document.getElementById('batchQueueOptions');
    if (batchQueueOptions) {
        if (mdFileQueue.length > 0) {
            batchQueueOptions.classList.remove('hidden');
        } else {
            batchQueueOptions.classList.add('hidden');
        }
    } else if (batchConvertQueueBtn) {
        if (mdFileQueue.length > 0) {
            batchConvertQueueBtn.classList.remove('hidden');
        } else {
            batchConvertQueueBtn.classList.add('hidden');
        }
    }

    mdQueueList.innerHTML = '';
    mdFileQueue.forEach((item) => {
        const isActive = (item.id === activeQueueId);
        const row = document.createElement('div');
        row.className = `flex items-center justify-between p-2 rounded-lg border text-xs transition cursor-pointer ${
            isActive ? 'bg-sky-950/50 border-sky-600/60 shadow-sm' : 'bg-slate-900/60 border-slate-800 hover:bg-slate-900 hover:border-slate-700'
        }`;

        let statusDot = `<span class="w-2 h-2 rounded-full bg-slate-500 shrink-0"></span>`;
        if (isActive) {
            statusDot = `<span class="w-2 h-2 rounded-full bg-sky-400 animate-pulse shrink-0"></span>`;
        } else if (item.status === 'done') {
            statusDot = `<span class="w-2 h-2 rounded-full bg-emerald-400 shrink-0" title="Selesai dikonversi"></span>`;
        }

        row.innerHTML = `
            <div class="flex items-center gap-2 min-w-0 flex-1 overflow-hidden">
                ${statusDot}
                <span class="truncate font-mono ${isActive ? 'text-sky-300 font-semibold' : 'text-slate-300'}" title="${item.name}">${item.name}</span>
                <span class="text-[10px] text-slate-500 font-mono shrink-0">${item.sizeKb} KB</span>
            </div>
            <div class="flex items-center gap-1.5 shrink-0 ml-2">
                <button class="export-single-docx px-1.5 py-0.5 rounded text-[10px] font-semibold bg-indigo-950/80 hover:bg-indigo-900 text-indigo-300 border border-indigo-800/60 transition" title="Unduh DOCX file ini">DOCX</button>
                <button class="export-single-pdf px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-800/60 transition" title="Unduh PDF file ini">PDF</button>
                <button class="remove-queue-item p-1 text-slate-500 hover:text-rose-400 rounded transition" title="Hapus dari antrean">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>
        `;

        row.onclick = (e) => {
            if (e.target.closest('button')) return;
            selectQueueItem(item.id);
        };

        const singleDocxBtn = row.querySelector('.export-single-docx');
        if (singleDocxBtn) {
            singleDocxBtn.onclick = (e) => {
                e.stopPropagation();
                exportDocument('/md-to-docx', item.content, item.name.replace(/\.[^/.]+$/, ""), 'docx');
            };
        }

        const singlePdfBtn = row.querySelector('.export-single-pdf');
        if (singlePdfBtn) {
            singlePdfBtn.onclick = (e) => {
                e.stopPropagation();
                exportDocument('/md-to-pdf', item.content, item.name.replace(/\.[^/.]+$/, ""), 'pdf');
            };
        }

        const rmBtn = row.querySelector('.remove-queue-item');
        if (rmBtn) {
            rmBtn.onclick = (e) => {
                e.stopPropagation();
                removeQueueItem(item.id);
            };
        }

        mdQueueList.appendChild(row);
    });
}

function selectQueueItem(id) {
    // Before switching, sync current item with editor text and target name
    if (activeQueueId && activeQueueId !== id) {
        const curActive = mdFileQueue.find(q => q.id === activeQueueId);
        if (curActive) {
            if (mdInputArea) curActive.content = mdInputArea.value;
            if (targetDocxName && targetDocxName.value.trim()) {
                const customName = targetDocxName.value.trim();
                curActive.name = customName.endsWith('.md') ? customName : `${customName}.md`;
            }
        }
    }

    const item = mdFileQueue.find(q => q.id === id);
    if (!item) return;

    activeQueueId = id;
    if (mdInputArea) mdInputArea.value = item.content;
    if (targetDocxName) targetDocxName.value = item.name.replace(/\.[^/.]+$/, "");
    if (mdFileSelectedName) {
        mdFileSelectedName.textContent = `${item.name} (${item.sizeKb} KB)`;
        mdFileSelectedName.title = `${item.name} (${item.sizeKb} KB)`;
    }

    userOriginalFile = {
        name: item.name,
        content: item.content,
        sizeKb: item.sizeKb
    };
    isTemplateActive = false;
    if (templateActiveBadge) templateActiveBadge.classList.add('hidden');
    if (restoreUserFileBtn) restoreUserFileBtn.classList.add('hidden');

    updateMdStats();
    renderQueue();
}

function removeQueueItem(id) {
    mdFileQueue = mdFileQueue.filter(q => q.id !== id);
    if (activeQueueId === id) {
        if (mdFileQueue.length > 0) {
            selectQueueItem(mdFileQueue[0].id);
        } else {
            activeQueueId = null;
            if (mdFileInput) mdFileInput.value = '';
            if (mdFileSelectedName) mdFileSelectedName.textContent = 'Belum ada file dipilih';
            if (mdInputArea) mdInputArea.value = '';
            if (targetDocxName) targetDocxName.value = 'Dokumen_Hasil_Konversi';
            userOriginalFile = null;
            updateMdStats();
        }
    }
    renderQueue();
}

if (clearQueueBtn) {
    clearQueueBtn.addEventListener('click', () => {
        mdFileQueue = [];
        activeQueueId = null;
        if (mdFileInput) mdFileInput.value = '';
        if (mdFileSelectedName) mdFileSelectedName.textContent = 'Belum ada file dipilih';
        userOriginalFile = null;
        renderQueue();
    });
}

async function handleMdFiles(fileList) {
    if (!fileList || fileList.length === 0) return;
    const files = Array.from(fileList).filter(f => /\.(md|markdown|txt)$/i.test(f.name));
    
    if (files.length === 0) {
        alert('Format file tidak didukung. Harap pilih berkas .md, .markdown, atau .txt');
        return;
    }

    // Preserve existing editor content as item 1 if queue is currently empty and editor has text
    if (mdFileQueue.length === 0 && !activeQueueId && mdInputArea && mdInputArea.value.trim().length > 0) {
        const existingName = (targetDocxName && targetDocxName.value.trim()) ? targetDocxName.value.trim() : 'Naskah_Awal';
        const docName = existingName.endsWith('.md') ? existingName : `${existingName}.md`;
        const existingContent = mdInputArea.value;
        const existingSizeKb = Math.round(existingContent.length / 1024 * 10) / 10;
        mdFileQueue.push({
            id: 'queue_' + Date.now() + '_init',
            file: null,
            name: docName,
            sizeKb: existingSizeKb,
            content: existingContent,
            status: 'ready'
        });
        activeQueueId = mdFileQueue[0].id;
    }

    const availableSlots = 10 - mdFileQueue.length;
    if (availableSlots <= 0) {
        alert('Antrean sudah mencapai batas maksimum (10 berkas). Hapus berkas sebelum menambahkan yang baru.');
        return;
    }

    let filesToAdd = files;
    if (files.length > availableSlots) {
        alert(`Batas maksimum antrean adalah 10 berkas. Hanya ${availableSlots} berkas pertama yang dimasukkan ke antrean.`);
        filesToAdd = files.slice(0, availableSlots);
    }

    for (const file of filesToAdd) {
        try {
            const content = await readFileAsText(file);
            const sizeKb = Math.round(file.size / 1024 * 10) / 10;
            const item = {
                id: 'queue_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
                file: file,
                name: file.name,
                sizeKb: sizeKb,
                content: content,
                status: 'ready'
            };
            mdFileQueue.push(item);
        } catch (err) {
            console.error('Gagal membaca berkas:', file.name, err);
        }
    }

    if (!activeQueueId && mdFileQueue.length > 0) {
        selectQueueItem(mdFileQueue[0].id);
    } else {
        renderQueue();
    }
}

// Live Input & Statistics
if (mdInputArea) {
    mdInputArea.addEventListener('input', () => {
        // If user modifies text in active queue item, keep in-memory queue synced
        if (activeQueueId) {
            const curItem = mdFileQueue.find(q => q.id === activeQueueId);
            if (curItem) curItem.content = mdInputArea.value;
        }
        updateMdStats();
    });
}

if (targetDocxName) {
    targetDocxName.addEventListener('input', () => {
        if (activeQueueId) {
            const curItem = mdFileQueue.find(q => q.id === activeQueueId);
            if (curItem) {
                const val = targetDocxName.value.trim();
                if (val) {
                    curItem.name = val.endsWith('.md') ? val : `${val}.md`;
                    if (mdFileSelectedName) {
                        mdFileSelectedName.textContent = `${curItem.name} (${curItem.sizeKb} KB)`;
                        mdFileSelectedName.title = `${curItem.name} (${curItem.sizeKb} KB)`;
                    }
                    renderQueue();
                }
            }
        }
    });
}

function updateMdStats() {
    const text = mdInputArea ? mdInputArea.value : '';
    if (mdCharCount) mdCharCount.textContent = `${text.length.toLocaleString()} kar`;
    if (mdLineCount) mdLineCount.textContent = `${text ? text.split('\n').length : 0} baris`;
    renderLivePreview();
}

let previewDebounceTimer = null;
function renderLivePreview() {
    clearTimeout(previewDebounceTimer);
    const text = mdInputArea ? mdInputArea.value : '';
    const delay = text.length > 30000 ? 250 : 120;

    previewDebounceTimer = setTimeout(() => {
        if (!mdLivePreview) return;
        if (!text || !text.trim()) {
            mdLivePreview.innerHTML = '<div class="text-slate-500 italic p-6 text-center">Pratinjau visual akan muncul otomatis di sini...</div>';
            return;
        }

        requestAnimationFrame(() => {
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

            const hasMath = text.includes('$') || text.includes('\\(') || text.includes('\\[');
            if (hasMath && window.renderMathInElement) {
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
                } catch (e) {
                    console.warn("KaTeX render error:", e);
                }
            }

            const hasMermaid = text.includes('mermaid');
            if (hasMermaid && window.mermaid) {
                try {
                    const codeBlocks = mdLivePreview.querySelectorAll('pre code.language-mermaid, pre code.lang-mermaid');
                    codeBlocks.forEach((codeBlock, idx) => {
                        const pre = codeBlock.parentElement;
                        const container = document.createElement('div');
                        container.className = 'mermaid my-4 flex justify-center bg-slate-900/40 p-4 rounded-xl border border-slate-800 overflow-x-auto';
                        container.id = `mermaid-render-${Date.now()}-${idx}`;
                        container.textContent = codeBlock.textContent.trim();
                        pre.parentNode.replaceChild(container, pre);
                    });
                    if (codeBlocks.length > 0) {
                        mermaid.run({ nodes: mdLivePreview.querySelectorAll('.mermaid') });
                    }
                } catch (e) {
                    console.warn("Mermaid execution error:", e);
                }
            }
        });
    }, delay);
}

// Layout Switcher (Split / Edit / Preview)
function setEditorLayout(mode) {
    if (!btnViewSplit || !btnViewEdit || !btnViewPreview) return;
    
    // Reset all buttons styling
    [btnViewSplit, btnViewEdit, btnViewPreview].forEach(btn => {
        btn.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
    });

    if (mode === 'split') {
        btnViewSplit.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        if (editorLeftPane) editorLeftPane.classList.remove('hidden');
        if (editorRightPane) editorRightPane.classList.remove('hidden');
    } else if (mode === 'edit') {
        btnViewEdit.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        if (editorLeftPane) editorLeftPane.classList.remove('hidden');
        if (editorRightPane) editorRightPane.classList.add('hidden');
    } else if (mode === 'preview') {
        btnViewPreview.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        if (editorLeftPane) editorLeftPane.classList.add('hidden');
        if (editorRightPane) editorRightPane.classList.remove('hidden');
        renderLivePreview();
    }
}

if (btnViewSplit) btnViewSplit.addEventListener('click', () => setEditorLayout('split'));
if (btnViewEdit) btnViewEdit.addEventListener('click', () => setEditorLayout('edit'));
if (btnViewPreview) btnViewPreview.addEventListener('click', () => setEditorLayout('preview'));

// HTML Preview or Download Helper
async function previewOrDownloadHtml(text, rawName, openInTab = false) {
    if (!text || !text.trim()) {
        alert('Silakan sediakan naskah Markdown terlebih dahulu.');
        return;
    }
    const safeName = (rawName.trim() || 'dokumen').replace(/\.html?$/i, '');

    if (window.Doc2MDProgress) {
        window.Doc2MDProgress.show({
            title: openInTab ? 'Membuka Pratinjau HTML' : 'Membuat Dokumen HTML',
            subtitle: 'Menyusun naskah HTML standalone dengan KaTeX & Mermaid...',
            badge: 'HTML',
            tip: 'Engine merender sintaks Markdown ke struktur HTML siap cetak.',
            simulated: true,
            targetPercent: 90,
            duration: 1000,
            step: 'Mengirim naskah ke server...'
        });
    }

    try {
        const fd = new FormData();
        fd.append('markdown_text', text);
        fd.append('filename', safeName);
        fd.append('theme', getSelectedTheme());

        const res = await fetch('/md-to-html', { method: 'POST', body: fd });
        if (!res.ok) throw new Error(await res.text());

        const htmlBlob = await res.blob();
        if (openInTab) {
            window.open(URL.createObjectURL(htmlBlob), '_blank');
        } else {
            triggerDownload(htmlBlob, `${safeName}.html`);
        }

        if (window.Doc2MDProgress) {
            window.Doc2MDProgress.complete({
                title: openInTab ? 'Pratinjau HTML Terbuka!' : 'HTML Berhasil Diunduh!',
                subtitle: `${safeName}.html`,
                message: openInTab ? 'Dokumen HTML telah dibuka pada tab peramban baru.' : 'Dokumen HTML berhasil diunduh.',
                autoHideMs: 1200
            });
        }
    } catch (e) {
        if (window.Doc2MDProgress) {
            window.Doc2MDProgress.error({
                title: 'Gagal Memproses HTML',
                message: e.message
            });
            setTimeout(() => window.Doc2MDProgress.hide(), 2500);
        }
        alert('Gagal menghasilkan dokumen HTML: ' + e.message);
    }
}


// Export PDF Button
if (generatePdfBtn) {
    generatePdfBtn.addEventListener('click', async () => {
        const text = mdInputArea ? mdInputArea.value : '';
        if (!text.trim()) {
            alert('Silakan masukkan atau upload teks Markdown terlebih dahulu.');
            return;
        }
        generatePdfBtn.disabled = true;
        if (generatePdfBtnText) generatePdfBtnText.textContent = 'Merender PDF A4...';
        try {
            await exportDocument('/md-to-pdf', text, targetDocxName.value || 'dokumen', 'pdf');
            if (activeQueueId) {
                const qItem = mdFileQueue.find(q => q.id === activeQueueId);
                if (qItem) { qItem.status = 'done'; renderQueue(); }
            }
        } catch (err) {
            alert('Gagal membuat PDF: ' + err.message);
        } finally {
            generatePdfBtn.disabled = false;
            if (generatePdfBtnText) generatePdfBtnText.textContent = 'Konversi & Unduh .PDF (A4 Rapi)';
        }
    });
}

// Export DOCX Button
if (generateDocxBtn) {
    generateDocxBtn.addEventListener('click', async () => {
        const text = mdInputArea ? mdInputArea.value : '';
        if (!text.trim()) {
            alert('Silakan masukkan atau upload teks Markdown terlebih dahulu.');
            return;
        }
        generateDocxBtn.disabled = true;
        if (generateDocxBtnText) generateDocxBtnText.textContent = 'Membuat Dokumen Word...';
        try {
            await exportDocument('/md-to-docx', text, targetDocxName.value || 'dokumen', 'docx');
            if (activeQueueId) {
                const qItem = mdFileQueue.find(q => q.id === activeQueueId);
                if (qItem) { qItem.status = 'done'; renderQueue(); }
            }
        } catch (err) {
            alert('Gagal membuat DOCX: ' + err.message);
        } finally {
            generateDocxBtn.disabled = false;
            if (generateDocxBtnText) generateDocxBtnText.textContent = 'Konversi & Unduh .DOCX';
        }
    });
}

// HTML Print Preview Button
if (generateHtmlBtn) {
    generateHtmlBtn.addEventListener('click', () => {
        const text = mdInputArea ? mdInputArea.value : '';
        previewOrDownloadHtml(text, targetDocxName.value || 'dokumen', true);
    });
}

// Quick action buttons in editor header
if (quickPdfBtn) quickPdfBtn.addEventListener('click', () => generatePdfBtn && generatePdfBtn.click());
if (quickDocxBtn) quickDocxBtn.addEventListener('click', () => generateDocxBtn && generateDocxBtn.click());
if (quickHtmlBtn) quickHtmlBtn.addEventListener('click', () => generateHtmlBtn && generateHtmlBtn.click());

// Batch Convert Queue Button (.ZIP)
if (batchConvertQueueBtn) {
    batchConvertQueueBtn.addEventListener('click', async () => {
        if (!mdFileQueue || mdFileQueue.length === 0) {
            alert('Belum ada berkas dalam antrean untuk dikonversi.');
            return;
        }

        const formatSelect = document.getElementById('batchZipFormatSelect');
        const selectedFormat = (formatSelect ? formatSelect.value : 'docx').toLowerCase();

        let formatLabel = '.DOCX';
        if (selectedFormat === 'pdf') formatLabel = '.PDF';
        else if (selectedFormat === 'both') formatLabel = '.DOCX + .PDF';

        batchConvertQueueBtn.disabled = true;
        const origText = batchConvertQueueBtnText ? batchConvertQueueBtnText.textContent : 'Konversi Seluruh Antrean Berkas (.ZIP)';
        if (batchConvertQueueBtnText) batchConvertQueueBtnText.textContent = `Mengonversi ${mdFileQueue.length} Berkas ke ${formatLabel}...`;

        // Sync active item before building payload
        if (activeQueueId && mdInputArea) {
            const curItem = mdFileQueue.find(q => q.id === activeQueueId);
            if (curItem) {
                curItem.content = mdInputArea.value;
                if (targetDocxName && targetDocxName.value.trim()) {
                    const val = targetDocxName.value.trim();
                    curItem.name = val.endsWith('.md') ? val : `${val}.md`;
                }
            }
        }

        // Show live progress modal with item checklist
        if (window.Doc2MDProgress) {
            window.Doc2MDProgress.show({
                title: `Batch Konversi ${mdFileQueue.length} Berkas (.ZIP)`,
                subtitle: `Mengonversi antrean ke format ${formatLabel}...`,
                badge: formatLabel,
                tip: 'Setiap berkas diproses secara independen dan dikemas ke dalam arsip ZIP.',
                items: mdFileQueue.map(q => q.name || 'Dokumen'),
                step: `Menghubungkan ke engine konversi ${formatLabel}...`
            });
        }

        try {
            const payload = {
                format: selectedFormat,
                items: mdFileQueue.map((q, idx) => ({
                    filename: q.name || `dokumen_${idx + 1}.md`,
                    markdown: q.content,
                    theme: getSelectedTheme()
                }))
            };

            const res = await fetch('/batch-md-export-stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error(await res.text());

            const reader = res.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';
            let completeData = null;

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // keep trailing incomplete line

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const event = JSON.parse(line);
                        if (event.type === 'start') {
                            if (window.Doc2MDProgress) {
                                window.Doc2MDProgress.update({
                                    percent: event.percent || 5,
                                    step: event.message
                                });
                            }
                        } else if (event.type === 'item_start') {
                            if (window.Doc2MDProgress) {
                                window.Doc2MDProgress.update({
                                    percent: event.percent,
                                    step: event.message
                                });
                                window.Doc2MDProgress.updateItem(event.index, {
                                    status: 'processing',
                                    message: 'Merender...'
                                });
                            }
                        } else if (event.type === 'item_skip') {
                            if (window.Doc2MDProgress) {
                                window.Doc2MDProgress.updateItem(event.index, {
                                    status: 'skip',
                                    message: 'Kosong'
                                });
                            }
                        } else if (event.type === 'item_done') {
                            if (window.Doc2MDProgress) {
                                window.Doc2MDProgress.update({
                                    percent: event.percent,
                                    step: event.message
                                });
                                window.Doc2MDProgress.updateItem(event.index, {
                                    status: event.status === 'error' ? 'error' : 'success',
                                    message: event.status === 'error' ? '⚠ Kendala' : '✓ Selesai'
                                });
                            }
                            if (mdFileQueue[event.index]) {
                                mdFileQueue[event.index].status = event.status === 'error' ? 'error' : 'done';
                                renderQueue();
                            }
                        } else if (event.type === 'packaging') {
                            if (window.Doc2MDProgress) {
                                window.Doc2MDProgress.update({
                                    percent: event.percent || 96,
                                    step: event.message
                                });
                            }
                        } else if (event.type === 'complete') {
                            completeData = event;
                        } else if (event.type === 'error') {
                            throw new Error(event.message || 'Gagal memproses batch');
                        }
                    } catch (pe) {
                        if (pe.message && pe.message.includes('Gagal memproses batch')) throw pe;
                        console.warn('Gagal mem-parse NDJSON stream:', line, pe);
                    }
                }
            }

            if (completeData && completeData.download_url) {
                // Trigger download from the temporary tokenized download endpoint
                const downloadLink = document.createElement('a');
                downloadLink.href = completeData.download_url;
                downloadLink.download = completeData.filename || 'batch_export.zip';
                downloadLink.click();

                if (window.Doc2MDProgress) {
                    window.Doc2MDProgress.complete({
                        title: 'Batch Konversi Selesai!',
                        subtitle: `${completeData.file_count} dokumen berhasil dikemas ke dalam ZIP.`,
                        message: 'Arsip .ZIP telah berhasil diunduh ke perangkat.',
                        autoHideMs: 1600
                    });
                }

                if (completeData.warnings) {
                    setTimeout(() => {
                        alert(`Arsip ZIP berhasil diunduh, namun terdapat catatan kendala pada sebagian berkas:\n\n${completeData.warnings}\n\nPeriksa berkas CATATAN_KENDALA_KONVERSI.txt di dalam ZIP untuk rincian.`);
                    }, 1200);
                }
            } else {
                throw new Error('Tidak menerima informasi penyelesaian arsip dari server.');
            }
        } catch (err) {
            if (window.Doc2MDProgress) {
                window.Doc2MDProgress.error({
                    title: 'Gagal Konversi Batch',
                    subtitle: 'Terjadi kendala saat memproses antrean berkas',
                    message: err.message
                });
                setTimeout(() => window.Doc2MDProgress.hide(), 3000);
            }
            alert('Gagal mengonversi antrean berkas: ' + err.message);
        } finally {
            batchConvertQueueBtn.disabled = false;
            if (batchConvertQueueBtnText) batchConvertQueueBtnText.textContent = origText;
        }
    });
}

// YAML Frontmatter Helper
if (addFrontmatterBtn) {
    addFrontmatterBtn.addEventListener('click', async () => {
        const text = mdInputArea ? mdInputArea.value : '';
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
                if (activeQueueId) {
                    const qItem = mdFileQueue.find(q => q.id === activeQueueId);
                    if (qItem) qItem.content = data.markdown;
                }
                updateMdStats();
            }
        } catch (e) {
            alert('Gagal menyematkan YAML frontmatter: ' + e.message);
        } finally {
            addFrontmatterBtn.innerHTML = orig;
        }
    });
}

// Internal Fallback Presets if samples.js is delayed
const INTERNAL_SAMPLE_PRESETS = {
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

function updateSampleButtonStyles(activeKey) {
    const btnMap = {
        'report': loadSampleReportBtn,
        'proposal': loadSampleProposalBtn,
        'mathDiagram': loadSampleMathDiagramBtn
    };
    const activeClass = "flex-1 py-1.5 px-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg text-xs transition border border-indigo-500 shadow-md ring-1 ring-indigo-400/50";
    const inactiveClass = "flex-1 py-1.5 px-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition border border-slate-700 shadow-sm";

    Object.entries(btnMap).forEach(([key, btn]) => {
        if (!btn) return;
        if (key === activeKey) {
            btn.className = activeClass;
        } else {
            btn.className = inactiveClass;
        }
    });
}

// Template Preset Helper
function applySampleTemplate(sampleKey) {
    const samplesLib = (window.DOC2MD_SAMPLES && window.DOC2MD_SAMPLES[sampleKey])
        ? window.DOC2MD_SAMPLES
        : INTERNAL_SAMPLE_PRESETS;
    const sample = samplesLib[sampleKey];
    if (!sample) {
        console.warn('Template tidak ditemukan:', sampleKey);
        return;
    }

    // If user currently has active uploaded/edited content and no backup exists yet, stash it!
    const curText = mdInputArea ? mdInputArea.value : '';
    if (!userOriginalFile && curText.trim()) {
        userOriginalFile = {
            name: (targetDocxName ? targetDocxName.value.trim() : '') || 'Naskah_Saya.md',
            content: curText,
            sizeKb: Math.round(curText.length / 1024 * 10) / 10
        };
    }

    // Deselect file queue active item so template doesn't collide
    activeQueueId = null;
    renderQueue();

    isTemplateActive = true;
    if (templateActiveBadge) templateActiveBadge.classList.remove('hidden');
    if (restoreUserFileBtn) restoreUserFileBtn.classList.remove('hidden');

    if (targetDocxName) targetDocxName.value = sample.filename;
    if (mdInputArea) {
        mdInputArea.value = sample.content;
    }
    if (mdFileSelectedName) {
        mdFileSelectedName.textContent = `[Template: ${sample.filename}]`;
        mdFileSelectedName.title = `Template aktif: ${sample.filename}`;
    }

    updateSampleButtonStyles(sampleKey);
    updateMdStats();
}

if (loadSampleReportBtn) {
    loadSampleReportBtn.addEventListener('click', (e) => {
        e.preventDefault();
        applySampleTemplate('report');
    });
}
if (loadSampleProposalBtn) {
    loadSampleProposalBtn.addEventListener('click', (e) => {
        e.preventDefault();
        applySampleTemplate('proposal');
    });
}
if (loadSampleMathDiagramBtn) {
    loadSampleMathDiagramBtn.addEventListener('click', (e) => {
        e.preventDefault();
        applySampleTemplate('mathDiagram');
    });
}

// Restore Original User File
if (restoreUserFileBtn) {
    restoreUserFileBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (!userOriginalFile) return;

        if (mdInputArea) mdInputArea.value = userOriginalFile.content;
        if (targetDocxName) targetDocxName.value = userOriginalFile.name.replace(/\.[^/.]+$/, "");
        if (mdFileSelectedName) {
            mdFileSelectedName.textContent = `${userOriginalFile.name} (${userOriginalFile.sizeKb} KB)`;
            mdFileSelectedName.title = `${userOriginalFile.name} (${userOriginalFile.sizeKb} KB)`;
        }

        isTemplateActive = false;
        if (templateActiveBadge) templateActiveBadge.classList.add('hidden');
        if (restoreUserFileBtn) restoreUserFileBtn.classList.add('hidden');

        updateSampleButtonStyles(null);
        updateMdStats();
    });
}

// Dropzone & File Input Events
if (mdDropzone) {
    mdDropzone.addEventListener('click', (e) => {
        if (e.target.closest('input')) return;
        if (mdFileInput) mdFileInput.click();
    });
    mdDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        mdDropzone.classList.add('border-indigo-500', 'bg-indigo-950/20');
    });
    mdDropzone.addEventListener('dragleave', () => {
        mdDropzone.classList.remove('border-indigo-500', 'bg-indigo-950/20');
    });
    mdDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        mdDropzone.classList.remove('border-indigo-500', 'bg-indigo-950/20');
        if (e.dataTransfer && e.dataTransfer.files.length) {
            handleMdFiles(e.dataTransfer.files);
        }
    });
}

if (mdFileInput) {
    mdFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length) {
            handleMdFiles(e.target.files);
        }
    });
}

// Reset md2doc view state
window.resetMd2Doc = function() {
    mdFileQueue = [];
    activeQueueId = null;
    userOriginalFile = null;
    isTemplateActive = false;

    if (mdFileInput) mdFileInput.value = '';
    if (mdFileSelectedName) {
        mdFileSelectedName.textContent = 'Belum ada file dipilih';
        mdFileSelectedName.title = 'Belum ada file dipilih';
    }
    if (templateActiveBadge) templateActiveBadge.classList.add('hidden');
    if (restoreUserFileBtn) restoreUserFileBtn.classList.add('hidden');
    if (mdInputArea) mdInputArea.value = '';
    if (targetDocxName) targetDocxName.value = 'Dokumen_Hasil_Konversi';
    if (mdCharCount) mdCharCount.textContent = '0 kar';
    if (mdLineCount) mdLineCount.textContent = '0 baris';
    if (exportThemeSelect) exportThemeSelect.value = 'modern_slate';
    if (themeColorBadge) themeColorBadge.style.backgroundColor = THEME_INFO['modern_slate'].color;
    if (themeDescText) themeDescText.textContent = THEME_INFO['modern_slate'].desc;

    updateSampleButtonStyles(null);
    renderQueue();

    if (mdLivePreview) {
        mdLivePreview.innerHTML = `
            <div class="h-full flex flex-col items-center justify-center text-center text-slate-500 py-20">
                <div class="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-600 mb-3">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                </div>
                <p class="text-xs font-semibold text-slate-400">Pratinjau Hasil Dokumen</p>
                <p class="text-[11px] text-slate-600 mt-1 max-w-xs">Ketik atau upload teks Markdown di panel editor sebelah kiri untuk melihat render langsung.</p>
            </div>
        `;
    }
};
