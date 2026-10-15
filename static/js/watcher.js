const watcherHeaderDot = el('watcherHeaderDot');
const watcherGlobalPill = el('watcherGlobalPill');
const watcherGlobalDot = el('watcherGlobalDot');
const watcherGlobalText = el('watcherGlobalText');
const watcherStatusPill = el('watcherStatusPill');
const btnStartWatcher = el('btnStartWatcher');
const btnStopWatcher = el('btnStopWatcher');
const watcherInputPath = el('watcherInputPath');
const watcherOutputPath = el('watcherOutputPath');
const btnResetInputPath = el('btnResetInputPath');
const btnResetOutputPath = el('btnResetOutputPath');
const watcherFrontmatterSelect = el('watcherFrontmatterSelect');
const watcherChunkSelect = el('watcherChunkSelect');
const watcherTotalProcessedBadge = el('watcherTotalProcessedBadge');
const watcherHistoryCount = el('watcherHistoryCount');
const btnRefreshWatcherHistory = el('btnRefreshWatcherHistory');
const btnClearWatcherHistory = el('btnClearWatcherHistory');
const watcherEmptyState = el('watcherEmptyState');
const watcherFeedList = el('watcherFeedList');

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
    if (!data) return;
    const isActive = data.is_active;

    if (watcherStatusPill) {
        if (isActive) {
            watcherStatusPill.textContent = 'AKTIF (MEMANTAU)';
            watcherStatusPill.className = 'text-[10px] font-semibold bg-emerald-950/90 text-emerald-300 border border-emerald-700/80 px-2 py-0.5 rounded-full font-mono flex items-center gap-1';
        } else {
            watcherStatusPill.textContent = 'NONAKTIF';
            watcherStatusPill.className = 'text-[10px] font-semibold bg-slate-800 text-slate-400 border border-slate-700 px-2 py-0.5 rounded-full font-mono';
        }
    }

    if (watcherHeaderDot) {
        watcherHeaderDot.className = isActive ? 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse' : 'w-2 h-2 rounded-full bg-slate-600';
    }
    if (watcherGlobalDot) {
        watcherGlobalDot.className = isActive ? 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse' : 'w-2 h-2 rounded-full bg-slate-600';
    }
    if (watcherGlobalText) {
        watcherGlobalText.textContent = isActive ? 'Watcher: LIVE' : 'Watcher: OFF';
        watcherGlobalText.className = isActive ? 'text-emerald-400 font-mono text-[11px] font-semibold' : 'text-slate-400 font-mono text-[11px]';
    }

    if (btnStartWatcher) {
        btnStartWatcher.disabled = isActive;
        btnStartWatcher.className = isActive 
            ? 'px-4 py-2 rounded-xl bg-slate-800 text-slate-500 text-xs font-semibold transition flex items-center gap-1.5 border border-slate-700 cursor-not-allowed'
            : 'px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-1.5 shadow-md shadow-emerald-600/20';
    }

    if (btnStopWatcher) {
        btnStopWatcher.disabled = !isActive;
        btnStopWatcher.className = !isActive
            ? 'px-4 py-2 rounded-xl bg-slate-800 text-slate-500 text-xs font-semibold transition flex items-center gap-1.5 border border-slate-700 cursor-not-allowed'
            : 'px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold transition flex items-center gap-1.5 shadow-md shadow-rose-600/20';
    }

    if (data.input_dir && !isActive && watcherInputPath) watcherInputPath.value = data.input_dir;
    if (data.output_dir && !isActive && watcherOutputPath) watcherOutputPath.value = data.output_dir;

    if (watcherTotalProcessedBadge) watcherTotalProcessedBadge.textContent = (data.total_processed || 0).toLocaleString();
    if (watcherHistoryCount) watcherHistoryCount.textContent = (data.recent_events || []).length;

    renderWatcherEvents(data.recent_events || []);
}

function renderWatcherEvents(events) {
    if (!watcherEmptyState || !watcherFeedList) return;
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

if (btnStartWatcher) {
    btnStartWatcher.addEventListener('click', async () => {
        const inPath = (watcherInputPath && watcherInputPath.value.trim()) || 'watch_input';
        const outPath = (watcherOutputPath && watcherOutputPath.value.trim()) || 'watch_output';
        const fmPreset = (watcherFrontmatterSelect && watcherFrontmatterSelect.value) || 'none';
        const chunkTokens = (watcherChunkSelect && watcherChunkSelect.value) || '0';

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
}

if (btnStopWatcher) {
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
}

if (btnResetInputPath && watcherInputPath) {
    btnResetInputPath.addEventListener('click', () => { watcherInputPath.value = 'watch_input'; });
}
if (btnResetOutputPath && watcherOutputPath) {
    btnResetOutputPath.addEventListener('click', () => { watcherOutputPath.value = 'watch_output'; });
}
if (btnRefreshWatcherHistory) {
    btnRefreshWatcherHistory.addEventListener('click', fetchWatcherStatus);
}
if (btnClearWatcherHistory) {
    btnClearWatcherHistory.addEventListener('click', async () => {
        if (confirm('Bersihkan seluruh log riwayat aktivitas watcher?')) {
            await fetch('/watcher/clear-history', { method: 'POST' });
            fetchWatcherStatus();
        }
    });
}

setInterval(fetchWatcherStatus, 3000);
fetchWatcherStatus();
