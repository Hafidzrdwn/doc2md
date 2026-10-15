if (window.mermaid) {
    mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
            darkMode: true,
            background: '#0b0f19',
            primaryColor: '#0284c7',
            primaryTextColor: '#f8fafc',
            lineColor: '#38bdf8'
        }
    });
}

window.converted = [];
window.uploadedFiles = window.converted;
window.activeIdx = 0;
window.activeChunkIdx = 0;

function el(id) {
    return document.getElementById(id);
}

const exportThemeSelect = document.getElementById('exportThemeSelect');
const themeColorBadge = document.getElementById('themeColorBadge');
const themeDescText = document.getElementById('themeDescText');

function getSelectedTheme() {
    return exportThemeSelect ? exportThemeSelect.value : 'modern_slate';
}

if (exportThemeSelect) {
    exportThemeSelect.addEventListener('change', () => {
        const selected = exportThemeSelect.options[exportThemeSelect.selectedIndex];
        const color = selected.getAttribute('data-color') || '#0284c7';
        const desc = selected.getAttribute('data-desc') || '';
        if (themeColorBadge) themeColorBadge.style.backgroundColor = color;
        if (themeDescText) themeDescText.textContent = desc;
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function triggerDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

async function exportDocument(endpoint, markdown, filename, ext) {
    const safeName = (filename.trim() || 'dokumen').replace(new RegExp(`\\.${ext}$`, 'i'), '') + `.${ext}`;
    const fd = new FormData();
    fd.append('markdown_text', markdown);
    fd.append('filename', safeName);
    fd.append('theme', getSelectedTheme());

    const res = await fetch(endpoint, { method: 'POST', body: fd });
    if (!res.ok) throw new Error(await res.text());
    const blob = await res.blob();
    triggerDownload(blob, safeName);
}
