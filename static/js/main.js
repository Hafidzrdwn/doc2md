// ===================================================================
// Doc2MD - Main Navigation & Application Lifecycle
// ===================================================================

const tabModeDoc2Md = document.getElementById('tabModeDoc2Md');
const tabModeMd2Doc = document.getElementById('tabModeMd2Doc');
const tabModeWatcher = document.getElementById('tabModeWatcher');
const viewDoc2Md = document.getElementById('viewDoc2Md');
const viewMd2Doc = document.getElementById('viewMd2Doc');
const viewWatcher = document.getElementById('viewWatcher');

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

