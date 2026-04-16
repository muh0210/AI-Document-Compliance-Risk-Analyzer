/* ═══════════════════════════════════════════════════
   Compliance Analyzer v2.0 — Frontend Logic
   Upload progress, structured errors, export
   ═══════════════════════════════════════════════════ */

const $ = id => document.getElementById(id);

const uploadArea     = $('uploadArea');
const fileInput      = $('fileInput');
const fileRow        = $('fileRow');
const analyzeBtn     = $('analyzeBtn');
const progressSec    = $('progressSection');
const progressFill   = $('progressFill');
const progressLabel  = $('progressLabel');
const errorSec       = $('errorSection');
const results        = $('results');

let selectedFile = null;

/* ── Upload ────────────────────────────────────── */

uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', e => {
    e.preventDefault(); uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files.length) pickFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => { if (fileInput.files.length) pickFile(fileInput.files[0]); });
$('clearBtn').addEventListener('click', clearFile);
analyzeBtn.addEventListener('click', analyze);
$('errorDismiss').addEventListener('click', () => { errorSec.style.display = 'none'; });

function pickFile(file) {
    const ok = ['.pdf','.docx','.doc','.txt'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ok.includes(ext)) return showError('INVALID_FILE', 'Unsupported file. Use PDF, DOCX, or TXT.');
    if (file.size > 5 * 1024 * 1024) return showError('FILE_TOO_LARGE', 'File exceeds 5 MB limit.');
    selectedFile = file;
    $('fileName').textContent = file.name;
    $('fileSize').textContent = formatSize(file.size);
    fileRow.style.display = 'block';
    analyzeBtn.style.display = 'inline-flex';
    results.style.display = 'none';
    errorSec.style.display = 'none';
}

function clearFile() {
    selectedFile = null; fileInput.value = '';
    fileRow.style.display = 'none';
    analyzeBtn.style.display = 'none';
    results.style.display = 'none';
}

function formatSize(b) {
    if (b < 1024) return b + ' B';
    if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1048576).toFixed(1) + ' MB';
}

/* ── Analysis ──────────────────────────────────── */

async function analyze() {
    if (!selectedFile) return;
    progressSec.style.display = 'block';
    results.style.display = 'none';
    errorSec.style.display = 'none';
    analyzeBtn.style.display = 'none';
    animateProgress();

    const fd = new FormData();
    fd.append('file', selectedFile);

    try {
        const res = await fetch('/api/analyze', { method: 'POST', body: fd });
        const data = await res.json();
        if (!data.success) {
            const e = data.error || {};
            showError(e.code || 'UNKNOWN', e.message || 'Analysis failed.');
            progressSec.style.display = 'none';
            analyzeBtn.style.display = 'inline-flex';
            return;
        }
        finishProgress();
        setTimeout(() => {
            progressSec.style.display = 'none';
            render(data);
        }, 600);
    } catch {
        showError('NETWORK', 'Could not reach the server. Is it running?');
        progressSec.style.display = 'none';
        analyzeBtn.style.display = 'inline-flex';
    }
}

/* ── Progress Animation ────────────────────────── */

const STEPS = [
    [15, 'Extracting text…'], [35, 'Running NLP pipeline…'],
    [55, 'Detecting clauses…'], [70, 'Analyzing risks…'],
    [85, 'Calculating score…'], [95, 'Generating report…'],
];
let stepIdx = 0, animTimer;

function animateProgress() {
    stepIdx = 0;
    progressFill.style.width = '0%';
    animTimer = setInterval(() => {
        if (stepIdx < STEPS.length) {
            const [pct, label] = STEPS[stepIdx];
            progressFill.style.width = pct + '%';
            progressLabel.textContent = label;
            stepIdx++;
        }
    }, 700);
}

function finishProgress() {
    clearInterval(animTimer);
    progressFill.style.width = '100%';
    progressLabel.textContent = 'Analysis complete.';
}

/* ── Error ──────────────────────────────────────── */

function showError(code, message) {
    $('errorMessage').textContent = `[${code}] ${message}`;
    errorSec.style.display = 'block';
    errorSec.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/* ── Render Results ────────────────────────────── */

function render(data) {
    const { score, document: doc, clauses, risks, explanations, rewrites } = data;

    // Score hero
    const sn = $('scoreNum');
    sn.textContent = score.score;
    sn.style.color = score.color;
    const badge = $('scoreBadge');
    badge.textContent = `${score.grade} — ${score.label}`;
    badge.style.background = score.color + '12';
    badge.style.color = score.color;
    badge.style.border = `1px solid ${score.color}25`;

    $('narrative').textContent = explanations.overall_assessment.narrative;

    // Doc type + meta
    const dt = doc.document_type || {};
    $('docTypeChip').textContent = (dt.label || 'Document') + (dt.confidence ? ` · ${dt.confidence}%` : '');
    $('metaWords').textContent = `${(doc.word_count || 0).toLocaleString()} words`;
    $('metaSents').textContent = `${doc.sentence_count || 0} sentences`;

    // Breakdown
    const grid = $('breakdownGrid');
    grid.innerHTML = '';
    const cols = { clause_coverage: '#637dff', risk_density: '#3dd6a5', structure: '#4fc3f7', clarity: '#e8a33d' };
    const labels = { clause_coverage: 'Clause Coverage', risk_density: 'Risk Safety', structure: 'Structure', clarity: 'Clarity' };
    for (const [key, clr] of Object.entries(cols)) {
        const b = score.breakdown[key];
        if (!b) continue;
        const pct = b.max ? Math.round((b.score / b.max) * 100) : 0;
        grid.innerHTML += `<div class="bd-card">
            <div class="bd-label" style="color:${clr}">${labels[key]}</div>
            <div class="bd-bar"><div class="bd-bar-fill" style="width:${pct}%;background:${clr}"></div></div>
            <div class="bd-score" style="color:${clr}">${b.score} / ${b.max}</div>
            <div class="bd-detail">${b.details}</div>
        </div>`;
    }

    // Score reduction reasons
    const reasons = explanations.score_reduction_reasons || [];
    const rc = $('reductionCard');
    const rl = $('reductionList');
    if (reasons.length) {
        rc.style.display = 'block';
        rl.innerHTML = reasons.map(r =>
            `<div class="reduction-item">
                <span class="reduction-pts">-${r.points_lost}</span>
                <span class="reduction-text">${r.reason}</span>
            </div>`
        ).join('');
    } else rc.style.display = 'none';

    // Critical findings
    const crits = explanations.critical_findings || [];
    const cc = $('criticalCard');
    if (crits.length) {
        cc.style.display = 'block';
        $('criticalList').innerHTML = crits.map(f =>
            `<div class="risk risk-high">
                <div class="risk-top"><span class="risk-cat">${f.title}</span></div>
                <div class="risk-desc">${f.explanation}</div>
                ${f.if_ignored ? `<div class="action-impact">If ignored: ${f.if_ignored}</div>` : ''}
            </div>`
        ).join('');
    } else cc.style.display = 'none';

    // Clauses
    $('clauseTitle').textContent = `Clause Coverage — ${clauses.summary.found_count}/${clauses.summary.total_clauses}`;
    const cg = $('clauseGrid');
    cg.innerHTML = Object.values(clauses.detected).map(c => {
        const cls = c.found ? 'clause-found' : 'clause-missing';
        const st = c.found
            ? `<span class="clause-status found">${c.confidence}%</span>`
            : `<span class="clause-status missing">Missing</span>`;
        return `<div class="clause ${cls}">
            <div><div class="clause-name">${c.label}</div><div class="clause-sub">${c.description}</div></div>
            ${st}
        </div>`;
    }).join('');

    // Risks
    const rs = risks.summary;
    $('riskTitle').textContent = `Risk Alerts — ${rs.total_risks} found`;
    $('sevBadges').innerHTML = `
        <span class="sev-tag sev-HIGH">HIGH ${rs.high}</span>
        <span class="sev-tag sev-MEDIUM">MEDIUM ${rs.medium}</span>
        <span class="sev-tag sev-LOW">LOW ${rs.low}</span>`;
    $('riskList').innerHTML = risks.risks.slice(0, 15).map(r => {
        const cls = `risk-${r.severity.toLowerCase()}`;
        return `<div class="risk ${cls}">
            <div class="risk-top">
                <span class="risk-cat">${r.category_label}</span>
                <span class="risk-sev sev-${r.severity}">${r.severity}</span>
            </div>
            ${r.sentence ? `<div class="risk-quote">"${r.sentence.slice(0, 150)}"</div>` : ''}
            <div class="risk-desc">${r.description}</div>
        </div>`;
    }).join('');

    // Actions
    const acts = explanations.action_items || [];
    const ac = $('actionsCard');
    if (acts.length) {
        ac.style.display = 'block';
        $('actionList').innerHTML = acts.map((a, i) => {
            const clr = a.severity === 'HIGH' ? 'var(--danger)' : (a.severity === 'MEDIUM' ? 'var(--warn)' : '#ffd740');
            return `<div class="action">
                <div class="action-idx" style="background:${clr}18;color:${clr}">${i + 1}</div>
                <div class="action-body">
                    <h4>${a.action}</h4>
                    <p>${a.detail}</p>
                    ${a.if_ignored ? `<div class="action-impact">If ignored: ${a.if_ignored}</div>` : ''}
                </div>
            </div>`;
        }).join('');
    } else ac.style.display = 'none';

    // Rewrites
    const rwc = $('rewritesCard');
    if (rewrites && rewrites.length) {
        rwc.style.display = 'block';
        $('rewriteList').innerHTML = rewrites.slice(0, 8).map(rw => {
            const tags = (rw.changes || []).map(c => `<span class="rw-tag">${c}</span>`).join('');
            return `<div class="rewrite">
                <div class="rw-orig"><div class="rw-label" style="color:var(--danger)">Original</div>${rw.original.slice(0, 200)}</div>
                <div class="rw-impr"><div class="rw-label" style="color:var(--accent2)">Improved</div>${rw.rewritten.slice(0, 200)}<div class="rw-tags">${tags}</div></div>
            </div>`;
        }).join('');
    } else rwc.style.display = 'none';

    results.style.display = 'block';
    $('scoreHero').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ── Export ─────────────────────────────────────── */

$('pdfBtn').addEventListener('click', async () => {
    try {
        const res = await fetch('/api/report', { method: 'POST' });
        if (!res.ok) { const d = await res.json(); showError(d.error?.code || 'PDF', d.error?.message || 'Download failed.'); return; }
        download(await res.blob(), `compliance_report_${Date.now()}.pdf`);
    } catch { showError('NETWORK', 'PDF download failed.'); }
});

$('csvBtn').addEventListener('click', () => exportAs('csv'));
$('jsonBtn').addEventListener('click', () => exportAs('json'));

async function exportAs(fmt) {
    try {
        const res = await fetch(`/api/export/${fmt}`, { method: 'POST' });
        if (!res.ok) { const d = await res.json(); showError(d.error?.code || 'EXPORT', d.error?.message || 'Export failed.'); return; }
        download(await res.blob(), `compliance_export_${Date.now()}.${fmt}`);
    } catch { showError('NETWORK', 'Export failed.'); }
}

function download(blob, name) {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
}
