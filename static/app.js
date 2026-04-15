/* ═══════════════ AI Document Compliance & Risk Analyzer ═══════════════ */

const uploadBox    = document.getElementById('uploadBox');
const fileInput    = document.getElementById('fileInput');
const fileInfo     = document.getElementById('fileInfo');
const fileName     = document.getElementById('fileName');
const clearBtn     = document.getElementById('clearBtn');
const analyzeBtn   = document.getElementById('analyzeBtn');
const loader       = document.getElementById('loader');
const results      = document.getElementById('results');
const errorToast   = document.getElementById('errorToast');

let selectedFile = null;

// ── Upload handlers ─────────────────────────────────────

uploadBox.addEventListener('click', () => fileInput.click());
uploadBox.addEventListener('dragover', e => { e.preventDefault(); uploadBox.classList.add('dragover'); });
uploadBox.addEventListener('dragleave', () => uploadBox.classList.remove('dragover'));
uploadBox.addEventListener('drop', e => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => { if (fileInput.files.length) handleFile(fileInput.files[0]); });
clearBtn.addEventListener('click', clearFile);
analyzeBtn.addEventListener('click', runAnalysis);

function handleFile(file) {
    const ok = ['.pdf','.docx','.doc','.txt'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ok.includes(ext)) { showError('Unsupported file type. Use PDF, DOCX, or TXT.'); return; }
    if (file.size > 20 * 1024 * 1024) { showError('File too large. Max 20 MB.'); return; }
    selectedFile = file;
    fileName.textContent = `${file.name} (${(file.size/1024).toFixed(1)} KB)`;
    fileInfo.style.display = 'flex';
    analyzeBtn.style.display = 'block';
    analyzeBtn.classList.add('visible');
    results.style.display = 'none';
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    analyzeBtn.style.display = 'none';
    results.style.display = 'none';
}

// ── Analysis ────────────────────────────────────────────

async function runAnalysis() {
    if (!selectedFile) return;
    loader.style.display = 'block';
    results.style.display = 'none';
    analyzeBtn.style.display = 'none';

    const fd = new FormData();
    fd.append('file', selectedFile);

    try {
        const res = await fetch('/api/analyze', { method: 'POST', body: fd });
        const data = await res.json();
        if (!res.ok || !data.success) { showError(data.error || 'Analysis failed.'); loader.style.display = 'none'; analyzeBtn.style.display = 'block'; return; }
        renderResults(data);
    } catch (err) {
        showError('Server error. Please try again.');
    }
    loader.style.display = 'none';
}

// ── Render ───────────────────────────────────────────────

function renderResults(data) {
    const { score, document: doc, clauses, risks, explanations, rewrites } = data;

    // Score
    const scoreNum = document.getElementById('scoreNumber');
    const ring = document.getElementById('scoreRing');
    scoreNum.textContent = score.score;
    scoreNum.style.color = score.color;
    ring.style.borderColor = score.color + '40';

    const badge = document.getElementById('gradeBadge');
    badge.textContent = `${score.grade} — ${score.label}`;
    badge.style.background = score.color + '15';
    badge.style.color = score.color;
    badge.style.border = `1px solid ${score.color}30`;

    document.getElementById('narrative').textContent = explanations.overall_assessment.narrative;

    // Breakdown
    const bd = document.getElementById('breakdown');
    bd.innerHTML = '';
    const items = [
        ['Clause Coverage', 'clause_coverage', '#6c63ff'],
        ['Risk Safety', 'risk_density', '#00d4aa'],
        ['Structure', 'structure', '#4fc3f7'],
        ['Clarity', 'clarity', '#ffab40'],
    ];
    items.forEach(([lbl, key, clr]) => {
        const b = score.breakdown[key];
        const pct = b.max ? Math.round((b.score / b.max) * 100) : 0;
        bd.innerHTML += `<div class="bd-item">
            <div class="bd-label" style="color:${clr}">${lbl}</div>
            <div class="bd-bar"><div class="bd-fill" style="width:${pct}%;background:${clr}"></div></div>
            <div class="bd-score" style="color:${clr}">${b.score} / ${b.max}</div>
            <div class="bd-detail">${b.details}</div>
        </div>`;
    });

    // Doc stats
    const stats = document.getElementById('docStats');
    stats.innerHTML = '';
    [['Words', doc.word_count], ['Sentences', doc.sentence_count], ['Paragraphs', doc.paragraph_count],
     ['Sections', doc.section_count], ['Characters', doc.char_count]].forEach(([l, v]) => {
        stats.innerHTML += `<div class="stat-box"><div class="stat-value">${(v||0).toLocaleString()}</div><div class="stat-label">${l}</div></div>`;
    });

    // Critical
    const crits = explanations.critical_findings || [];
    const critCard = document.getElementById('criticalCard');
    const critList = document.getElementById('criticalList');
    if (crits.length) {
        critCard.style.display = 'block';
        critList.innerHTML = crits.map(f => `<div class="risk-item risk-high">
            <div class="risk-cat">[!] ${f.title}</div>
            <div class="risk-desc">${f.explanation}</div>
        </div>`).join('');
    } else { critCard.style.display = 'none'; }

    // Clauses
    document.getElementById('clauseTitle').textContent = `🔎 Clause Detection — ${clauses.summary.found_count}/${clauses.summary.total_clauses}`;
    const cg = document.getElementById('clauseGrid');
    cg.innerHTML = '';
    Object.entries(clauses.detected).forEach(([, c]) => {
        const cls = c.found ? 'clause-found' : 'clause-missing';
        const status = c.found ? `<span style="color:#00e676">✅ ${c.confidence}%</span>` : '<span style="color:#ff5252">❌ Missing</span>';
        cg.innerHTML += `<div class="clause-item ${cls}">
            <span class="clause-name">${c.label}</span><span class="clause-status">${status}</span>
            <div class="clause-desc">${c.description}</div>
        </div>`;
    });

    // Risks
    const rs = risks.summary;
    document.getElementById('riskTitle').textContent = `⚠️ Risk Alerts — ${rs.total_risks} Risks`;
    document.getElementById('sevBadges').innerHTML = `
        <span class="sev-badge sev-HIGH">HIGH: ${rs.high}</span>
        <span class="sev-badge sev-MEDIUM">MEDIUM: ${rs.medium}</span>
        <span class="sev-badge sev-LOW">LOW: ${rs.low}</span>`;
    const rl = document.getElementById('riskList');
    rl.innerHTML = risks.risks.slice(0, 12).map(r => {
        const cls = `risk-${r.severity.toLowerCase()}`;
        return `<div class="risk-item ${cls}">
            <div class="risk-cat">[${r.severity}] ${r.category_label}</div>
            <div class="risk-sent">"${r.sentence.slice(0, 150)}"</div>
            <div class="risk-desc">${r.description}</div>
        </div>`;
    }).join('');

    // Actions
    const acts = explanations.action_items || [];
    const actCard = document.getElementById('actionsCard');
    const actList = document.getElementById('actionList');
    if (acts.length) {
        actCard.style.display = 'block';
        actList.innerHTML = acts.map((a, i) => {
            const clr = a.severity === 'HIGH' ? '#ff5252' : (a.severity === 'MEDIUM' ? '#ffab40' : '#ffd740');
            return `<div class="action-item">
                <div class="action-num" style="background:${clr}20;color:${clr}">${i + 1}</div>
                <div><div class="action-title">${a.action}</div><div class="action-detail">${a.detail}</div></div>
            </div>`;
        }).join('');
    } else { actCard.style.display = 'none'; }

    // Rewrites
    const rwCard = document.getElementById('rewritesCard');
    const rwList = document.getElementById('rewriteList');
    if (rewrites && rewrites.length) {
        rwCard.style.display = 'block';
        rwList.innerHTML = rewrites.slice(0, 8).map(rw => {
            const tags = (rw.changes || []).map(c => `<span class="rewrite-tag">${c}</span>`).join(' ');
            return `<div class="rewrite-box">
                <div class="rewrite-orig"><div class="rewrite-lbl" style="color:#ff5252">Original</div>${rw.original.slice(0, 180)}</div>
                <div class="rewrite-impr"><div class="rewrite-lbl" style="color:#00d4aa">Improved</div>${rw.rewritten.slice(0, 180)}<div style="margin-top:6px">${tags}</div></div>
            </div>`;
        }).join('');
    } else { rwCard.style.display = 'none'; }

    results.style.display = 'block';
}

// ── PDF Download ────────────────────────────────────────

document.getElementById('pdfBtn').addEventListener('click', async () => {
    try {
        const res = await fetch('/api/report', { method: 'POST' });
        if (!res.ok) { const d = await res.json(); showError(d.error || 'PDF failed.'); return; }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `compliance_report_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch { showError('PDF download failed.'); }
});

// ── Error toast ─────────────────────────────────────────

function showError(msg) {
    errorToast.textContent = '⚠️ ' + msg;
    errorToast.classList.add('visible');
    setTimeout(() => errorToast.classList.remove('visible'), 5000);
}
