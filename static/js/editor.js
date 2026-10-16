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

function handleMdFile(file) {
    if (!file) return;
    mdFileSelectedName.textContent = `${file.name} (${Math.round(file.size / 1024 * 10) / 10} KB)`;
    targetDocxName.value = file.name.replace(/\.[^/.]+$/, "");
    const reader = new FileReader();
    reader.onload = (e) => {
        mdInputArea.value = e.target.result;
        updateMdStats();
    };
    reader.readAsText(file);
}

if (mdInputArea) {
    mdInputArea.addEventListener('input', updateMdStats);
}

function updateMdStats() {
    const text = mdInputArea.value;
    if (mdCharCount) mdCharCount.textContent = `${text.length.toLocaleString()} karakter`;
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

function setEditorLayout(mode) {
    if (!btnViewSplit || !btnViewEdit || !btnViewPreview) return;
    btnViewSplit.className = "px-2.5 py-1 rounded-md text-xs transition border flex items-center gap-1.5 border-slate-800 text-slate-400 hover:text-slate-200";
    btnViewEdit.className = "px-2.5 py-1 rounded-md text-xs transition border flex items-center gap-1.5 border-slate-800 text-slate-400 hover:text-slate-200";
    btnViewPreview.className = "px-2.5 py-1 rounded-md text-xs transition border flex items-center gap-1.5 border-slate-800 text-slate-400 hover:text-slate-200";

    if (mode === 'split') {
        btnViewSplit.className = "px-2.5 py-1 rounded-md text-xs transition border flex items-center gap-1.5 bg-slate-800 text-sky-400 border-sky-500/50 shadow-sm";
        editorLeftPane.className = "w-full md:w-1/2 flex flex-col bg-slate-900/60 rounded-2xl border border-slate-800 p-4 shadow-sm";
        editorRightPane.className = "w-full md:w-1/2 flex flex-col bg-slate-900/60 rounded-2xl border border-slate-800 p-4 shadow-sm";
    } else if (mode === 'edit') {
        btnViewEdit.className = "px-2.5 py-1 rounded-md text-xs transition border flex items-center gap-1.5 bg-slate-800 text-sky-400 border-sky-500/50 shadow-sm";
        editorLeftPane.className = "w-full flex flex-col bg-slate-900/60 rounded-2xl border border-slate-800 p-4 shadow-sm";
        editorRightPane.className = "hidden";
    } else if (mode === 'preview') {
        btnViewPreview.className = "px-2.5 py-1 rounded-md text-xs transition border flex items-center gap-1.5 bg-slate-800 text-sky-400 border-sky-500/50 shadow-sm";
        editorLeftPane.className = "hidden";
        editorRightPane.className = "w-full flex flex-col bg-slate-900/60 rounded-2xl border border-slate-800 p-4 shadow-sm";
        renderLivePreview();
    }
}

if (btnViewSplit) btnViewSplit.addEventListener('click', () => setEditorLayout('split'));
if (btnViewEdit) btnViewEdit.addEventListener('click', () => setEditorLayout('edit'));
if (btnViewPreview) btnViewPreview.addEventListener('click', () => setEditorLayout('preview'));

async function previewOrDownloadHtml(text, rawName, openInTab = false) {
    if (!text || !text.trim()) {
        alert('Silakan sediakan naskah Markdown terlebih dahulu.');
        return;
    }
    const safeName = (rawName.trim() || 'dokumen').replace(/\.html?$/i, '');
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
    } catch (e) {
        alert('Gagal menghasilkan dokumen HTML: ' + e.message);
    }
}

if (generatePdfBtn) {
    generatePdfBtn.addEventListener('click', async () => {
        const text = mdInputArea.value;
        if (!text.trim()) {
            alert('Silakan masukkan atau upload teks Markdown terlebih dahulu.');
            return;
        }
        generatePdfBtn.disabled = true;
        generatePdfBtnText.textContent = 'Merender PDF A4...';
        try {
            await exportDocument('/md-to-pdf', text, targetDocxName.value || 'dokumen', 'pdf');
        } catch (err) {
            alert('Gagal membuat PDF: ' + err.message);
        } finally {
            generatePdfBtn.disabled = false;
            generatePdfBtnText.textContent = 'Konversi & Unduh .PDF (A4 Rapi)';
        }
    });
}

if (generateDocxBtn) {
    generateDocxBtn.addEventListener('click', async () => {
        const text = mdInputArea.value;
        if (!text.trim()) {
            alert('Silakan masukkan atau upload teks Markdown terlebih dahulu.');
            return;
        }
        generateDocxBtn.disabled = true;
        generateDocxBtnText.textContent = 'Membuat Dokumen Word...';
        try {
            await exportDocument('/md-to-docx', text, targetDocxName.value || 'dokumen', 'docx');
        } catch (err) {
            alert('Gagal membuat DOCX: ' + err.message);
        } finally {
            generateDocxBtn.disabled = false;
            generateDocxBtnText.textContent = 'Konversi & Unduh .DOCX';
        }
    });
}

if (generateHtmlBtn) {
    generateHtmlBtn.addEventListener('click', () => {
        previewOrDownloadHtml(mdInputArea.value, targetDocxName.value || 'dokumen', false);
    });
}

if (quickPdfBtn) quickPdfBtn.addEventListener('click', () => generatePdfBtn && generatePdfBtn.click());
if (quickDocxBtn) quickDocxBtn.addEventListener('click', () => generateDocxBtn && generateDocxBtn.click());
if (quickHtmlBtn) quickHtmlBtn.addEventListener('click', () => generateHtmlBtn && generateHtmlBtn.click());

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

if (loadSampleReportBtn) {
    loadSampleReportBtn.addEventListener('click', () => {
        const sample = window.DOC2MD_SAMPLES && window.DOC2MD_SAMPLES.report;
        if (!sample) return;
        targetDocxName.value = sample.filename;
        mdInputArea.value = sample.content;
        updateMdStats();
    });
}

if (loadSampleProposalBtn) {
    loadSampleProposalBtn.addEventListener('click', () => {
        const sample = window.DOC2MD_SAMPLES && window.DOC2MD_SAMPLES.proposal;
        if (!sample) return;
        targetDocxName.value = sample.filename;
        mdInputArea.value = sample.content;
        updateMdStats();
    });
}

if (loadSampleMathDiagramBtn) {
    loadSampleMathDiagramBtn.addEventListener('click', () => {
        const sample = window.DOC2MD_SAMPLES && window.DOC2MD_SAMPLES.mathDiagram;
        if (!sample) return;
        targetDocxName.value = sample.filename;
        mdInputArea.value = sample.content;
        updateMdStats();
    });
}

if (mdDropzone) {
    mdDropzone.addEventListener('click', () => mdFileInput && mdFileInput.click());
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
}

if (mdFileInput) {
    mdFileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleMdFile(e.target.files[0]);
    });
}

window.resetMd2Doc = function() {
    if (mdFileInput) mdFileInput.value = '';
    if (mdFileSelectedName) mdFileSelectedName.textContent = 'Pilih atau seret berkas Markdown (.md)';
    if (mdInputArea) mdInputArea.value = '';
    if (targetDocxName) targetDocxName.value = 'dokumen';
    if (mdCharCount) mdCharCount.textContent = '0 karakter';
    if (mdLineCount) mdLineCount.textContent = '0 baris';
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
