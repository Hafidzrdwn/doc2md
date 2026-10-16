function switchMode(mode) {
    const viewDoc2Md = document.getElementById('viewDoc2Md');
    const viewMd2Doc = document.getElementById('viewMd2Doc');
    const viewWatcher = document.getElementById('viewWatcher');
    const viewDiff = document.getElementById('viewDiff');

    const tabDoc2Md = document.getElementById('tabModeDoc2Md');
    const tabMd2Doc = document.getElementById('tabModeMd2Doc');
    const tabWatcher = document.getElementById('tabModeWatcher');
    const tabDiff = document.getElementById('tabModeDiff');

    if (viewDoc2Md) viewDoc2Md.classList.add('hidden');
    if (viewMd2Doc) viewMd2Doc.classList.add('hidden');
    if (viewWatcher) viewWatcher.classList.add('hidden');
    if (viewDiff) viewDiff.classList.add('hidden');

    const inactiveClass = "px-3.5 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 transition flex items-center gap-1.5";
    if (tabDoc2Md) tabDoc2Md.className = inactiveClass;
    if (tabMd2Doc) tabMd2Doc.className = inactiveClass;
    if (tabWatcher) tabWatcher.className = inactiveClass;
    if (tabDiff) tabDiff.className = inactiveClass;

    if (typeof window.setWatcherTabActive === 'function') {
        window.setWatcherTabActive(mode === 'watcher');
    }

    if (mode === 'doc2md') {
        if (viewDoc2Md) viewDoc2Md.classList.remove('hidden');
        if (tabDoc2Md) tabDoc2Md.className = "px-3.5 py-1.5 rounded-lg bg-sky-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
    } else if (mode === 'md2doc') {
        if (viewMd2Doc) viewMd2Doc.classList.remove('hidden');
        if (tabMd2Doc) tabMd2Doc.className = "px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
    } else if (mode === 'watcher') {
        if (viewWatcher) viewWatcher.classList.remove('hidden');
        if (tabWatcher) tabWatcher.className = "px-3.5 py-1.5 rounded-lg bg-purple-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
    } else if (mode === 'diff') {
        if (viewDiff) viewDiff.classList.remove('hidden');
        if (tabDiff) tabDiff.className = "px-3.5 py-1.5 rounded-lg bg-teal-600 text-white font-semibold transition flex items-center gap-1.5 shadow-sm";
    }
}

function initNavigation() {
    const tabDoc2Md = document.getElementById('tabModeDoc2Md');
    const tabMd2Doc = document.getElementById('tabModeMd2Doc');
    const tabWatcher = document.getElementById('tabModeWatcher');
    const tabDiff = document.getElementById('tabModeDiff');

    if (tabDoc2Md) tabDoc2Md.onclick = () => switchMode('doc2md');
    if (tabMd2Doc) tabMd2Doc.onclick = () => switchMode('md2doc');
    if (tabWatcher) tabWatcher.onclick = () => switchMode('watcher');
    if (tabDiff) tabDiff.onclick = () => switchMode('diff');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
} else {
    initNavigation();
}
