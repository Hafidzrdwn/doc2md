// Doc2MD - Main Application Orchestration, Sidebar Navigation & Smart Reset

let currentActiveMode = 'doc2md';

const navMeta = {
    'doc2md': {
        title: 'Dokumen ➔ Markdown',
        desc: '• Konversi dokumen multi-format ke Markdown AI',
        dotColor: 'bg-sky-500 shadow-sky-500/50',
        activeBtnClass: 'w-full text-left px-3 py-2.5 rounded-xl bg-sky-600 text-white font-semibold transition flex items-center gap-3 shadow-md shadow-sky-600/20 group',
        iconWrapActive: 'w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0',
        subActive: 'text-[10px] text-sky-200/90 font-normal truncate mt-0.5',
        resetLabel: 'Reset Doc ➔ MD',
        resetHint: 'Hapus berkas & hasil konversi aktif'
    },
    'md2doc': {
        title: 'Markdown ➔ Dokumen Word (.docx) & PDF',
        desc: '• Studio penulisan & ekspor dokumen berformat rapi',
        dotColor: 'bg-indigo-500 shadow-indigo-500/50',
        activeBtnClass: 'w-full text-left px-3 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold transition flex items-center gap-3 shadow-md shadow-indigo-600/20 group',
        iconWrapActive: 'w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0',
        subActive: 'text-[10px] text-indigo-200/90 font-normal truncate mt-0.5',
        resetLabel: 'Reset Editor MD',
        resetHint: 'Kosongkan editor & pratinjau dokumen'
    },
    'watcher': {
        title: 'Auto-Watcher Folder',
        desc: '• Pemantauan folder & konversi otomatis di latar belakang',
        dotColor: 'bg-purple-500 shadow-purple-500/50',
        activeBtnClass: 'w-full text-left px-3 py-2.5 rounded-xl bg-purple-600 text-white font-semibold transition flex items-center gap-3 shadow-md shadow-purple-600/20 group',
        iconWrapActive: 'w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0',
        subActive: 'text-[10px] text-purple-200/90 font-normal truncate mt-0.5',
        resetLabel: 'Reset Watcher',
        resetHint: 'Hentikan pemantau & kosongkan log'
    },
    'diff': {
        title: 'Diff Viewer Markdown',
        desc: '• Pembanding perbedaan visual antar versi dokumen',
        dotColor: 'bg-teal-500 shadow-teal-500/50',
        activeBtnClass: 'w-full text-left px-3 py-2.5 rounded-xl bg-teal-600 text-white font-semibold transition flex items-center gap-3 shadow-md shadow-teal-600/20 group',
        iconWrapActive: 'w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0',
        subActive: 'text-[10px] text-teal-200/90 font-normal truncate mt-0.5',
        resetLabel: 'Reset Diff',
        resetHint: 'Bersihkan naskah perbandingan'
    }
};

const inactiveBtnClass = 'w-full text-left px-3 py-2.5 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition flex items-center gap-3 group';
const iconWrapInactive = 'w-8 h-8 rounded-lg bg-slate-800/80 group-hover:bg-slate-700/80 flex items-center justify-center flex-shrink-0 transition';
const subInactive = 'text-[10px] text-slate-500 font-normal truncate mt-0.5';

function switchMode(mode) {
    currentActiveMode = mode;
    window.currentActiveMode = mode;

    const viewDoc2Md = document.getElementById('viewDoc2Md');
    const viewMd2Doc = document.getElementById('viewMd2Doc');
    const viewWatcher = document.getElementById('viewWatcher');
    const viewDiff = document.getElementById('viewDiff');

    const tabDoc2Md = document.getElementById('tabModeDoc2Md');
    const tabMd2Doc = document.getElementById('tabModeMd2Doc');
    const tabWatcher = document.getElementById('tabModeWatcher');
    const tabDiff = document.getElementById('tabModeDiff');

    const activePageTitle = document.getElementById('activePageTitle');
    const activePageDesc = document.getElementById('activePageDesc');
    const activePageDot = document.getElementById('activePageDot');
    const resetBtnLabel = document.getElementById('resetBtnLabel');
    const resetActivePageHint = document.getElementById('resetActivePageHint');

    // Hide all views
    if (viewDoc2Md) viewDoc2Md.classList.add('hidden');
    if (viewMd2Doc) viewMd2Doc.classList.add('hidden');
    if (viewWatcher) viewWatcher.classList.add('hidden');
    if (viewDiff) viewDiff.classList.add('hidden');

    // Reset tab button styles to inactive
    const tabs = [
        { el: tabDoc2Md, key: 'doc2md' },
        { el: tabMd2Doc, key: 'md2doc' },
        { el: tabWatcher, key: 'watcher' },
        { el: tabDiff, key: 'diff' }
    ];

    tabs.forEach(({ el: btn }) => {
        if (!btn) return;
        btn.className = inactiveBtnClass;
        const iconDiv = btn.querySelector('div:first-child');
        if (iconDiv) iconDiv.className = iconWrapInactive;
        const sub = btn.querySelector('span:last-child');
        if (sub) sub.className = subInactive;
    });

    // Notify watcher tab state
    if (typeof window.setWatcherTabActive === 'function') {
        window.setWatcherTabActive(mode === 'watcher');
    }

    // Activate the selected view
    const meta = navMeta[mode] || navMeta['doc2md'];
    let targetView = viewDoc2Md;
    let targetTab = tabDoc2Md;

    if (mode === 'doc2md') {
        targetView = viewDoc2Md;
        targetTab = tabDoc2Md;
    } else if (mode === 'md2doc') {
        targetView = viewMd2Doc;
        targetTab = tabMd2Doc;
    } else if (mode === 'watcher') {
        targetView = viewWatcher;
        targetTab = tabWatcher;
    } else if (mode === 'diff') {
        targetView = viewDiff;
        targetTab = tabDiff;
    }

    if (targetView) targetView.classList.remove('hidden');
    if (targetTab) {
        targetTab.className = meta.activeBtnClass;
        const iconDiv = targetTab.querySelector('div:first-child');
        if (iconDiv) iconDiv.className = meta.iconWrapActive;
        const sub = targetTab.querySelector('span:last-child');
        if (sub) sub.className = meta.subActive;
    }

    // Update Header breadcrumb
    if (activePageTitle) activePageTitle.textContent = meta.title;
    if (activePageDesc) activePageDesc.textContent = meta.desc;
    if (activePageDot) activePageDot.className = `w-2.5 h-2.5 rounded-full ${meta.dotColor}`;

    // Update Reset button label & hint
    if (resetBtnLabel) resetBtnLabel.textContent = meta.resetLabel;
    if (resetActivePageHint) resetActivePageHint.textContent = meta.resetHint;
}

// ── Smart Contextual Reset System ───────────────────────────────────────────

function resetCurrentPage() {
    const meta = navMeta[currentActiveMode] || navMeta['doc2md'];
    const confirmed = confirm(`Reset semua data dan form pada "${meta.title}"?`);
    if (!confirmed) return;

    if (currentActiveMode === 'doc2md' && typeof window.resetDoc2Md === 'function') {
        window.resetDoc2Md();
    } else if (currentActiveMode === 'md2doc' && typeof window.resetMd2Doc === 'function') {
        window.resetMd2Doc();
    } else if (currentActiveMode === 'watcher' && typeof window.resetWatcher === 'function') {
        window.resetWatcher();
    } else if (currentActiveMode === 'diff' && typeof window.resetDiff === 'function') {
        window.resetDiff();
    }
}

function resetAllPages() {
    const confirmed = confirm('Reset seluruh sesi aplikasi?\nSemua dokumen terunggah, editor naskah, watcher, dan diff akan dikosongkan.');
    if (!confirmed) return;

    if (typeof window.resetDoc2Md === 'function') window.resetDoc2Md();
    if (typeof window.resetMd2Doc === 'function') window.resetMd2Doc();
    if (typeof window.resetWatcher === 'function') window.resetWatcher();
    if (typeof window.resetDiff === 'function') window.resetDiff();

    switchMode('doc2md');
}

function initResetControls() {
    const globalResetBtn = document.getElementById('globalResetBtn');
    const toggleResetMenuBtn = document.getElementById('toggleResetMenuBtn');
    const resetDropupMenu = document.getElementById('resetDropupMenu');
    const btnResetActivePage = document.getElementById('btnResetActivePage');
    const btnResetAllPages = document.getElementById('btnResetAllPages');

    if (globalResetBtn) {
        globalResetBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            resetCurrentPage();
        });
    }

    if (toggleResetMenuBtn && resetDropupMenu) {
        toggleResetMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            resetDropupMenu.classList.toggle('hidden');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!resetDropupMenu.contains(e.target) && e.target !== toggleResetMenuBtn) {
                resetDropupMenu.classList.add('hidden');
            }
        });
    }

    if (btnResetActivePage && resetDropupMenu) {
        btnResetActivePage.addEventListener('click', (e) => {
            e.stopPropagation();
            resetDropupMenu.classList.add('hidden');
            resetCurrentPage();
        });
    }

    if (btnResetAllPages && resetDropupMenu) {
        btnResetAllPages.addEventListener('click', (e) => {
            e.stopPropagation();
            resetDropupMenu.classList.add('hidden');
            resetAllPages();
        });
    }
}

function initNavigation() {
    const tabDoc2Md = document.getElementById('tabModeDoc2Md');
    const tabMd2Doc = document.getElementById('tabModeMd2Doc');
    const tabWatcher = document.getElementById('tabModeWatcher');
    const tabDiff = document.getElementById('tabModeDiff');
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (tabDoc2Md) tabDoc2Md.onclick = () => switchMode('doc2md');
    if (tabMd2Doc) tabMd2Doc.onclick = () => switchMode('md2doc');
    if (tabWatcher) tabWatcher.onclick = () => switchMode('watcher');
    if (tabDiff) tabDiff.onclick = () => switchMode('diff');

    if (mobileSidebarToggle && sidebar) {
        mobileSidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full');
            sidebar.classList.toggle('fixed');
            sidebar.classList.toggle('inset-y-0');
            sidebar.classList.toggle('left-0');
        });
    }

    initResetControls();
    switchMode('doc2md');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
} else {
    initNavigation();
}
