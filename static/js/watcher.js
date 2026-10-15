// ===================================================================
// Doc2MD - Folder Auto-Watcher Module
// ===================================================================

const watcherHeaderDot = document.getElementById('watcherHeaderDot');
const watcherGlobalPill = document.getElementById('watcherGlobalPill');
const watcherGlobalDot = document.getElementById('watcherGlobalDot');
const watcherGlobalText = document.getElementById('watcherGlobalText');
const watcherStatusPill = document.getElementById('watcherStatusPill');
const btnStartWatcher = document.getElementById('btnStartWatcher');
const btnStopWatcher = document.getElementById('btnStopWatcher');
const watcherInputPath = document.getElementById('watcherInputPath');
const watcherOutputPath = document.getElementById('watcherOutputPath');

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
