const btnLoadDiffSample = el('btnLoadDiffSample');
const btnSwapDiff = el('btnSwapDiff');
const btnExecuteDiff = el('btnExecuteDiff');
const diffTitleA = el('diffTitleA');
const diffTitleB = el('diffTitleB');
const diffInputA = el('diffInputA');
const diffInputB = el('diffInputB');
const btnPullFromActiveDoc = el('btnPullFromActiveDoc');
const btnPullFromStudioDoc = el('btnPullFromStudioDoc');
const diffFileInputA = el('diffFileInputA');
const diffFileInputB = el('diffFileInputB');
const diffResultsSection = el('diffResultsSection');
const diffSimilarityScore = el('diffSimilarityScore');
const diffTokenDelta = el('diffTokenDelta');
const diffTokenA = el('diffTokenA');
const diffTokenB = el('diffTokenB');
const diffAddedLines = el('diffAddedLines');
const diffRemovedLines = el('diffRemovedLines');
const diffModifiedLines = el('diffModifiedLines');
const btnDiffSideBySide = el('btnDiffSideBySide');
const btnDiffUnified = el('btnDiffUnified');
const diffSideBySideContainer = el('diffSideBySideContainer');
const diffSideBySideTableBody = el('diffSideBySideTableBody');
const diffUnifiedContainer = el('diffUnifiedContainer');
const diffUnifiedTableBody = el('diffUnifiedTableBody');
const diffHeadTitleA = el('diffHeadTitleA');
const diffHeadTitleB = el('diffHeadTitleB');
const diffStatsA = el('diffStatsA');
const diffStatsB = el('diffStatsB');

let currentDiffData = null;

function updateDiffStats() {
    if (diffStatsA && diffInputA) {
        const lenA = diffInputA.value ? diffInputA.value.length : 0;
        const linesA = diffInputA.value ? diffInputA.value.split('\n').length : 0;
        diffStatsA.textContent = `${lenA.toLocaleString()} kar • ${linesA.toLocaleString()} baris`;
    }
    if (diffStatsB && diffInputB) {
        const lenB = diffInputB.value ? diffInputB.value.length : 0;
        const linesB = diffInputB.value ? diffInputB.value.split('\n').length : 0;
        diffStatsB.textContent = `${lenB.toLocaleString()} kar • ${linesB.toLocaleString()} baris`;
    }
}

if (diffInputA) diffInputA.addEventListener('input', updateDiffStats);
if (diffInputB) diffInputB.addEventListener('input', updateDiffStats);

async function executeDiff() {
    if (!diffInputA || !diffInputB) return;
    const textA = diffInputA.value;
    const textB = diffInputB.value;
    const titleA = (diffTitleA && diffTitleA.value.trim()) || 'Dokumen A';
    const titleB = (diffTitleB && diffTitleB.value.trim()) || 'Dokumen B';

    if (!textA.trim() && !textB.trim()) {
        alert('Silakan masukkan atau upload naskah pada Dokumen A dan Dokumen B untuk dibandingkan.');
        return;
    }

    if (btnExecuteDiff) {
        btnExecuteDiff.disabled = true;
        btnExecuteDiff.innerHTML = `<span>Membandingkan...</span>`;
    }

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
        if (btnExecuteDiff) {
            btnExecuteDiff.disabled = false;
            btnExecuteDiff.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg><span>Bandingkan Dokumen</span>`;
        }
    }
}

function renderDiffResults(data) {
    if (!data || !diffResultsSection) return;
    diffResultsSection.classList.remove('hidden');
    if (diffSimilarityScore) diffSimilarityScore.textContent = `${data.similarity_ratio}%`;
    
    const stats = data.stats || {};
    const dTokens = stats.delta_tokens || 0;
    if (diffTokenDelta) {
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
    }

    if (diffTokenA) diffTokenA.textContent = (stats.tokens_a || 0).toLocaleString();
    if (diffTokenB) diffTokenB.textContent = (stats.tokens_b || 0).toLocaleString();

    if (diffAddedLines) diffAddedLines.textContent = `+${stats.added_lines || 0}`;
    if (diffRemovedLines) diffRemovedLines.textContent = `-${stats.removed_lines || 0}`;
    if (diffModifiedLines) diffModifiedLines.textContent = `~${stats.modified_lines || 0}`;

    if (diffHeadTitleA) diffHeadTitleA.textContent = data.title_a || 'Dokumen A';
    if (diffHeadTitleB) diffHeadTitleB.textContent = data.title_b || 'Dokumen B';

    if (diffSideBySideTableBody) {
        diffSideBySideTableBody.innerHTML = '';
        (data.side_by_side || []).forEach(row => {
            const tr = document.createElement('tr');
            const rowType = row.type;

            let leftBg = '', rightBg = '';
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
    }

    if (diffUnifiedTableBody) {
        diffUnifiedTableBody.innerHTML = '';
        (data.unified || []).forEach(u => {
            const tr = document.createElement('tr');
            let symbol = ' ', rowBg = '', symbolClass = 'text-slate-600';

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
    }

    diffResultsSection.scrollIntoView({ behavior: 'smooth' });
}

if (btnExecuteDiff) btnExecuteDiff.addEventListener('click', executeDiff);

if (btnDiffSideBySide && btnDiffUnified) {
    btnDiffSideBySide.addEventListener('click', () => {
        if (diffSideBySideContainer) diffSideBySideContainer.classList.remove('hidden');
        if (diffUnifiedContainer) diffUnifiedContainer.classList.add('hidden');
        btnDiffSideBySide.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        btnDiffUnified.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
    });

    btnDiffUnified.addEventListener('click', () => {
        if (diffSideBySideContainer) diffSideBySideContainer.classList.add('hidden');
        if (diffUnifiedContainer) diffUnifiedContainer.classList.remove('hidden');
        btnDiffUnified.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-medium transition flex items-center gap-1 shadow-sm";
        btnDiffSideBySide.className = "px-2.5 py-1 rounded-md text-slate-400 hover:text-slate-200 transition flex items-center gap-1";
    });
}

if (btnSwapDiff) {
    btnSwapDiff.addEventListener('click', () => {
        if (!diffInputA || !diffInputB) return;
        const tmpTxt = diffInputA.value;
        diffInputA.value = diffInputB.value;
        diffInputB.value = tmpTxt;

        if (diffTitleA && diffTitleB) {
            const tmpTitle = diffTitleA.value;
            diffTitleA.value = diffTitleB.value;
            diffTitleB.value = tmpTitle;
        }

        updateDiffStats();

        if (diffInputA.value.trim() || diffInputB.value.trim()) {
            executeDiff();
        }
    });
}

if (btnPullFromActiveDoc) {
    btnPullFromActiveDoc.addEventListener('click', () => {
        const outArea = el('outputArea');
        if (window.converted && window.converted.length && window.converted[window.activeIdx]) {
            const doc = window.converted[window.activeIdx];
            if (diffInputA) diffInputA.value = doc.markdown || '';
            if (diffTitleA) diffTitleA.value = doc.filename || 'Dokumen Aktif';
            updateDiffStats();
        } else if (outArea && outArea.value.trim()) {
            if (diffInputA) diffInputA.value = outArea.value;
            if (diffTitleA) diffTitleA.value = "Dokumen Terkonversi Aktif";
            updateDiffStats();
        } else {
            alert('Belum ada dokumen aktif yang terkonversi di Tab Doc to Markdown.');
        }
    });
}

if (btnPullFromStudioDoc) {
    btnPullFromStudioDoc.addEventListener('click', () => {
        const mdArea = el('mdInputArea');
        const docName = el('targetDocxName');
        if (mdArea && mdArea.value.trim()) {
            if (diffInputB) diffInputB.value = mdArea.value;
            if (diffTitleB) diffTitleB.value = ((docName && docName.value.trim()) || 'Editor Studio') + '.md';
            updateDiffStats();
        } else {
            alert('Editor Markdown Studio masih kosong.');
        }
    });
}

function handleDiffFileUpload(file, targetInput, targetTitle) {
    if (!file || !targetInput) return;
    if (targetTitle) targetTitle.value = file.name;
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    if (ext === 'txt' || ext === 'md' || ext === 'markdown') {
        const reader = new FileReader();
        reader.onload = (e) => { 
            targetInput.value = e.target.result; 
            updateDiffStats();
        };
        reader.readAsText(file, 'utf-8');
    } else {
        const fd = new FormData();
        fd.append('files', file);
        fd.append('chunk_tokens', '0');
        fetch('/convert', { method: 'POST', body: fd })
            .then(r => r.json())
            .then(d => {
                if (d.results && d.results[0] && d.results[0].status === 'success') {
                    targetInput.value = d.results[0].markdown;
                    updateDiffStats();
                } else {
                    alert('Gagal mengekstrak teks dokumen.');
                }
            })
            .catch(e => alert('Error upload: ' + e.message));
    }
}

if (diffFileInputA) {
    diffFileInputA.addEventListener('change', (e) => {
        if (e.target.files.length) handleDiffFileUpload(e.target.files[0], diffInputA, diffTitleA);
    });
}

if (diffFileInputB) {
    diffFileInputB.addEventListener('change', (e) => {
        if (e.target.files.length) handleDiffFileUpload(e.target.files[0], diffInputB, diffTitleB);
    });
}

if (btnLoadDiffSample) {
    btnLoadDiffSample.addEventListener('click', () => {
        if (diffTitleA) diffTitleA.value = "Proposal_Sistem_v1.md";
        if (diffTitleB) diffTitleB.value = "Proposal_Sistem_v2_Revisi.md";

        if (diffInputA) {
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
        }

        if (diffInputB) {
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
        }

        updateDiffStats();
        executeDiff();
    });
}

window.resetDiff = function() {
    if (diffTitleA) diffTitleA.value = 'Draft Dokumen Versi 1';
    if (diffTitleB) diffTitleB.value = 'Revisi Dokumen Versi 2';
    if (diffInputA) diffInputA.value = '';
    if (diffInputB) diffInputB.value = '';
    if (diffFileInputA) diffFileInputA.value = '';
    if (diffFileInputB) diffFileInputB.value = '';
    if (diffResultsSection) diffResultsSection.classList.add('hidden');
    if (diffSideBySideTableBody) diffSideBySideTableBody.innerHTML = '';
    if (diffUnifiedTableBody) diffUnifiedTableBody.innerHTML = '';
    currentDiffData = null;
    updateDiffStats();
};