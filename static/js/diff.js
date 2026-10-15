// ===================================================================
// Doc2MD - Visual Document Diff Viewer Module
// ===================================================================

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