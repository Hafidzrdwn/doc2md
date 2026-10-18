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
window.activeChunkIdx = -1;

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

// Global Progress & Loading Modal Controller
window.Doc2MDProgress = {
    timerInterval: null,
    simInterval: null,
    startTime: 0,
    currentPercent: 0,

    getElements() {
        return {
            modal: document.getElementById('globalProgressModal'),
            spinner: document.getElementById('progressModalSpinner'),
            successIcon: document.getElementById('progressModalSuccessIcon'),
            iconContainer: document.getElementById('progressModalIconContainer'),
            title: document.getElementById('progressModalTitle'),
            subtitle: document.getElementById('progressModalSubtitle'),
            badge: document.getElementById('progressModalBadge'),
            stepText: document.getElementById('progressModalStepText'),
            percentText: document.getElementById('progressModalPercentText'),
            bar: document.getElementById('progressModalBar'),
            itemSection: document.getElementById('progressModalItemSection'),
            itemList: document.getElementById('progressModalItemList'),
            footerTip: document.getElementById('progressModalFooterTip'),
            timer: document.getElementById('progressModalTimer')
        };
    },

    show(options = {}) {
        const els = this.getElements();
        if (!els.modal) return;

        // Clear existing intervals
        this.stopTimers();

        // Reset visual state
        this.currentPercent = 0;
        if (els.bar) els.bar.style.width = '0%';
        if (els.percentText) els.percentText.textContent = '0%';
        if (els.spinner) els.spinner.classList.remove('hidden');
        if (els.successIcon) els.successIcon.classList.add('hidden');
        
        if (els.iconContainer) {
            els.iconContainer.className = 'w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400 flex-shrink-0 relative';
        }

        if (els.title) els.title.textContent = options.title || 'Memproses Permintaan...';
        if (els.subtitle) els.subtitle.textContent = options.subtitle || 'Menyiapkan naskah dan aset rendering...';
        if (els.badge) {
            els.badge.textContent = options.badge || 'PROSES';
            els.badge.className = 'px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase bg-sky-500/15 text-sky-300 border border-sky-500/30';
        }

        if (els.stepText) {
            els.stepText.innerHTML = `
                <span class="inline-block w-2 h-2 rounded-full bg-sky-400 animate-ping shrink-0 mt-1"></span>
                <span class="break-words leading-relaxed">${escapeHtml(options.step || 'Menghubungkan ke engine...')}</span>
            `;
        }

        if (els.footerTip) {
            els.footerTip.innerHTML = `
                <span class="shrink-0 mt-0.5">⚡</span>
                <span class="break-words leading-relaxed">${escapeHtml(options.tip || 'Engine headless Chromium & KaTeX sedang memproses dokumen offline.')}</span>
            `;
        }

        // Render item checklist if provided
        if (options.items && Array.isArray(options.items) && options.items.length > 0 && els.itemList && els.itemSection) {
            els.itemSection.classList.remove('hidden');
            els.itemList.innerHTML = '';
            options.items.forEach((item, idx) => {
                const name = typeof item === 'string' ? item : (item.name || `Berkas ${idx + 1}`);
                const row = document.createElement('div');
                row.id = `progressModalItemRow_${idx}`;
                row.className = 'flex items-start justify-between gap-2.5 p-2 rounded-lg bg-slate-950/70 border border-slate-800/80 text-[11px]';
                row.innerHTML = `
                    <div class="flex items-start gap-2 min-w-0 flex-1">
                        <span id="progressItemIcon_${idx}" class="w-2 h-2 rounded-full bg-slate-600 shrink-0 mt-1"></span>
                        <span class="break-all font-mono text-slate-300 leading-snug" title="${escapeHtml(name)}">${escapeHtml(name)}</span>
                    </div>
                    <span id="progressItemBadge_${idx}" class="text-[10px] font-mono px-1.5 py-0.5 rounded text-slate-500 bg-slate-900 border border-slate-800 shrink-0 ml-2 mt-0.5">
                        Menunggu
                    </span>
                `;
                els.itemList.appendChild(row);
            });
        } else if (els.itemSection) {
            els.itemSection.classList.add('hidden');
        }

        // Timer ticker
        this.startTime = Date.now();
        if (els.timer) els.timer.textContent = '00:00';
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const m = String(Math.floor(elapsed / 60)).padStart(2, '0');
            const s = String(elapsed % 60).padStart(2, '0');
            if (els.timer) els.timer.textContent = `${m}:${s}`;
        }, 1000);

        // Simulated smooth progress if requested (for non-streaming single downloads)
        if (options.simulated) {
            const target = options.targetPercent || 92;
            const dur = options.duration || 3000;
            const stepMs = 80;
            const totalSteps = Math.max(1, Math.floor(dur / stepMs));
            let currentStep = 0;

            this.simInterval = setInterval(() => {
                currentStep++;
                // Easing curve: faster at first, slowing down near target
                const progressRatio = currentStep / totalSteps;
                const eased = 1 - Math.pow(1 - Math.min(progressRatio, 1), 2.5);
                const nextPercent = Math.min(target, Math.round(eased * target));
                
                if (nextPercent > this.currentPercent) {
                    this.updatePercent(nextPercent);
                }

                if (currentStep >= totalSteps) {
                    clearInterval(this.simInterval);
                    this.simInterval = null;
                }
            }, stepMs);
        }

        els.modal.classList.remove('hidden');
    },

    update({ percent, step, subtitle, badge }) {
        const els = this.getElements();
        if (typeof percent === 'number') {
            this.updatePercent(percent);
        }

        if (step && els.stepText) {
            els.stepText.innerHTML = `
                <span class="inline-block w-2 h-2 rounded-full bg-sky-400 animate-ping shrink-0 mt-1"></span>
                <span class="break-words leading-relaxed">${escapeHtml(step)}</span>
            `;
        }

        if (subtitle && els.subtitle) {
            els.subtitle.textContent = subtitle;
        }

        if (badge && els.badge) {
            els.badge.textContent = badge;
        }
    },

    updatePercent(p) {
        const els = this.getElements();
        const clamped = Math.max(0, Math.min(100, p));
        this.currentPercent = clamped;
        if (els.bar) els.bar.style.width = `${clamped}%`;
        if (els.percentText) els.percentText.textContent = `${Math.round(clamped)}%`;
    },

    updateItem(index, { status, message }) {
        const row = document.getElementById(`progressModalItemRow_${index}`);
        const icon = document.getElementById(`progressItemIcon_${index}`);
        const badge = document.getElementById(`progressItemBadge_${index}`);
        if (!row || !badge) return;

        if (status === 'processing') {
            row.className = 'flex items-start justify-between gap-2.5 p-2 rounded-lg bg-sky-950/40 border border-sky-500/40 text-[11px] shadow-sm';
            if (icon) icon.className = 'w-2 h-2 rounded-full bg-sky-400 animate-pulse shrink-0 mt-1';
            badge.className = 'text-[10px] font-mono px-1.5 py-0.5 rounded text-sky-300 bg-sky-950/80 border border-sky-800/80 shrink-0 ml-2 mt-0.5 animate-pulse';
            badge.textContent = message || 'Merender...';
        } else if (status === 'success') {
            row.className = 'flex items-start justify-between gap-2.5 p-2 rounded-lg bg-emerald-950/20 border border-emerald-600/30 text-[11px]';
            if (icon) icon.className = 'w-2 h-2 rounded-full bg-emerald-400 shrink-0 mt-1';
            badge.className = 'text-[10px] font-mono px-1.5 py-0.5 rounded text-emerald-300 bg-emerald-950/80 border border-emerald-800/80 shrink-0 ml-2 mt-0.5';
            badge.textContent = message || '✓ Selesai';
        } else if (status === 'error') {
            row.className = 'flex items-start justify-between gap-2.5 p-2 rounded-lg bg-rose-950/20 border border-rose-600/30 text-[11px]';
            if (icon) icon.className = 'w-2 h-2 rounded-full bg-rose-400 shrink-0 mt-1';
            badge.className = 'text-[10px] font-mono px-1.5 py-0.5 rounded text-rose-300 bg-rose-950/80 border border-rose-800/80 shrink-0 ml-2 mt-0.5';
            badge.textContent = message || '⚠ Kendala';
        } else if (status === 'skip') {
            row.className = 'flex items-start justify-between gap-2.5 p-2 rounded-lg bg-slate-900/40 border border-slate-800 text-[11px] opacity-60';
            if (icon) icon.className = 'w-2 h-2 rounded-full bg-slate-500 shrink-0 mt-1';
            badge.className = 'text-[10px] font-mono px-1.5 py-0.5 rounded text-slate-400 bg-slate-900 border border-slate-800 shrink-0 ml-2 mt-0.5';
            badge.textContent = message || 'Dilewati';
        }
    },

    complete(options = {}) {
        const els = this.getElements();
        this.stopTimers();
        this.updatePercent(100);

        if (els.spinner) els.spinner.classList.add('hidden');
        if (els.successIcon) els.successIcon.classList.remove('hidden');

        if (els.iconContainer) {
            els.iconContainer.className = 'w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 flex-shrink-0 relative';
        }

        if (els.badge) {
            els.badge.textContent = 'SELESAI';
            els.badge.className = 'px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase bg-emerald-500/15 text-emerald-300 border border-emerald-500/30';
        }

        if (options.title && els.title) els.title.textContent = options.title;
        if (options.subtitle && els.subtitle) els.subtitle.textContent = options.subtitle;

        if (els.stepText) {
            els.stepText.innerHTML = `
                <span class="inline-block w-2 h-2 rounded-full bg-emerald-400 shrink-0 mt-1"></span>
                <span class="text-emerald-300 font-semibold break-words leading-relaxed">${escapeHtml(options.message || 'Proses selesai! Berkas berhasil diunduh.')}</span>
            `;
        }

        const autoHide = (typeof options.autoHideMs === 'number') ? options.autoHideMs : 1400;
        if (autoHide > 0) {
            setTimeout(() => this.hide(), autoHide);
        }
    },

    error(options = {}) {
        const els = this.getElements();
        this.stopTimers();

        if (els.iconContainer) {
            els.iconContainer.className = 'w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 flex-shrink-0 relative';
        }

        if (els.badge) {
            els.badge.textContent = 'GAGAL';
            els.badge.className = 'px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase bg-rose-500/15 text-rose-300 border border-rose-500/30';
        }

        if (options.title && els.title) els.title.textContent = options.title;
        if (options.subtitle && els.subtitle) els.subtitle.textContent = options.subtitle;

        if (els.stepText) {
            els.stepText.innerHTML = `
                <span class="inline-block w-2 h-2 rounded-full bg-rose-400 shrink-0 mt-1"></span>
                <span class="text-rose-300 font-semibold break-words leading-relaxed">${escapeHtml(options.message || 'Terjadi kesalahan saat memproses.')}</span>
            `;
        }
    },

    stopTimers() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        if (this.simInterval) {
            clearInterval(this.simInterval);
            this.simInterval = null;
        }
    },

    hide() {
        this.stopTimers();
        const els = this.getElements();
        if (els.modal) {
            els.modal.classList.add('hidden');
        }
    }
};

async function exportDocument(endpoint, markdown, filename, ext) {
    const safeName = (filename.trim() || 'dokumen').replace(new RegExp(`\\.${ext}$`, 'i'), '') + `.${ext}`;
    const extUpper = ext.toUpperCase();

    let docType = extUpper;
    let subtitle = `Menyiapkan format dokumen ${extUpper}...`;
    let tip = `Engine offline sedang mengonversi dokumen ke format .${ext}...`;
    let simulatedDuration = 1800;

    if (ext === 'pdf') {
        docType = 'PDF A4';
        subtitle = 'Merender tipografi A4, KaTeX, dan diagram visual via Chromium headless...';
        tip = 'Chromium headless sedang mencetak layout A4 dengan resolusi tajam.';
        simulatedDuration = 3200;
    } else if (ext === 'docx') {
        docType = 'DOCX Word';
        subtitle = 'Mengompilasi tabel, hierarki heading, dan formula ke dokumen Word...';
        tip = 'Engine python-docx sedang menyusun struktur berkas Word berformat rapi.';
        simulatedDuration = 1600;
    } else if (ext === 'html') {
        docType = 'HTML Web';
        subtitle = 'Menyusun naskah HTML standalone dengan KaTeX & Mermaid...';
        simulatedDuration = 1000;
    }

    if (window.Doc2MDProgress) {
        window.Doc2MDProgress.show({
            title: `Membuat Dokumen ${docType}`,
            subtitle: subtitle,
            badge: extUpper,
            tip: tip,
            simulated: true,
            targetPercent: 92,
            duration: simulatedDuration,
            step: `Mengirim naskah ${safeName} ke server...`
        });
        window.Doc2MDProgress.update({
            percent: 15,
            step: `Mengirim naskah ${safeName} ke engine ${extUpper}...`
        });
    }

    try {
        const fd = new FormData();
        fd.append('markdown_text', markdown);
        fd.append('filename', safeName);
        fd.append('theme', getSelectedTheme());

        if (window.Doc2MDProgress) {
            window.Doc2MDProgress.update({
                percent: 40,
                step: `Merender dokumen ${docType} di server...`
            });
        }

        const res = await fetch(endpoint, { method: 'POST', body: fd });
        if (!res.ok) {
            const errText = await res.text();
            throw new Error(errText || `Server mengembalikan status ${res.status}`);
        }

        if (window.Doc2MDProgress) {
            window.Doc2MDProgress.update({
                percent: 96,
                step: 'Mengunduh hasil konversi ke perangkat...'
            });
        }

        const blob = await res.blob();
        triggerDownload(blob, safeName);

        if (window.Doc2MDProgress) {
            window.Doc2MDProgress.complete({
                title: `Dokumen ${docType} Berhasil Diunduh!`,
                subtitle: `Tersimpan sebagai ${safeName}`,
                message: `Berkas ${safeName} telah berhasil disimpan ke perangkat.`,
                autoHideMs: 1400
            });
        }
    } catch (err) {
        if (window.Doc2MDProgress) {
            window.Doc2MDProgress.error({
                title: `Gagal Mengekspor ${docType}`,
                subtitle: `Gagal memproses berkas ${safeName}`,
                message: err.message
            });
            setTimeout(() => window.Doc2MDProgress.hide(), 2800);
        }
        throw err;
    }
}

