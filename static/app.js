/**
 * AI Document Compliance & Risk Analyzer — Frontend App Logic
 * Handles file upload, API communication, and dynamic result rendering.
 */

// ══════════════════════ DOM REFERENCES ══════════════════════
const $ = (id) => document.getElementById(id);
const uploadZone = $('upload-zone');
const fileInput = $('file-input');
const browseBtn = $('browse-btn');
const fileInfo = $('file-info');
const fileName = $('file-name');
const fileSize = $('file-size');
const analyzeBtn = $('analyze-btn');
const loading = $('loading');
const loadingSub = $('loading-sub');
const results = $('results');
const errorToast = $('error-toast');

let selectedFile = null;

// ══════════════════════ FILE UPLOAD ══════════════════════
browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

uploadZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

// Drag & Drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

function handleFile(file) {
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'application/msword', 'text/plain'];
    const ext = file.name.split('.').pop().toLowerCase();
    const allowedExt = ['pdf', 'docx', 'doc', 'txt'];
    
    if (!allowedExt.includes(ext)) {
        showError('Unsupported file type. Please upload PDF, DOCX, or TXT files.');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatSize(file.size);
    fileInfo.classList.add('visible');
    analyzeBtn.classList.add('visible');
    results.classList.remove('visible');
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

// ══════════════════════ ANALYZE ══════════════════════
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.disabled = true;
    loading.classList.add('visible');
    results.classList.remove('visible');

    const steps = [
        'Extracting text from document...',
        'Running NLP sentence segmentation...',
        'Detecting clause patterns...',
        'Analyzing risk indicators...',
        'Calculating compliance score...',
        'Generating AI explanations...',
        'Building recommendations...'
    ];

    let step = 0;
    const stepInterval = setInterval(() => {
        step = (step + 1) % steps.length;
        loadingSub.textContent = steps[step];
    }, 1500);

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const res = await fetch('/api/analyze', { method: 'POST', body: formData });
        const data = await res.json();

        clearInterval(stepInterval);
        loading.classList.remove('visible');
        analyzeBtn.disabled = false;

        if (!res.ok || data.error) {
            showError(data.error || 'Analysis failed. Please try again.');
            return;
        }

        renderResults(data);

    } catch (err) {
        clearInterval(stepInterval);
        loading.classList.remove('visible');
        analyzeBtn.disabled = false;
        showError('Connection failed. Make sure the server is running.');
    }
});

// ══════════════════════ RENDER RESULTS ══════════════════════
function renderResults(data) {
    renderScore(data.score, data.explanations);
    renderDocInfo(data.document);
    renderCritical(data.explanations.critical_findings);
    renderClauses(data.clauses);
    renderRisks(data.risks);
    renderActions(data.explanations.action_items);
    renderRewrites(data.rewrites);

    results.classList.add('visible');
    setTimeout(() => {
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// ── Score Gauge ──
function renderScore(score, explanations) {
    const card = $('score-card');
    const pct = score.score / 100;
    const circumference = 2 * Math.PI * 90;
    const offset = circumference * (1 - pct);
    const overall = explanations.overall_assessment;

    card.innerHTML = `
        <div class="card-header">
            <div class="card-icon">📊</div>
            <h2>Compliance Score</h2>
            <span class="card-badge" style="background:${score.color}22;color:${score.color};border:1px solid ${score.color}44">${score.grade}</span>
        </div>
        <div class="score-gauge-container">
            <svg class="score-gauge" viewBox="0 0 200 200">
                <circle class="score-gauge-bg" cx="100" cy="100" r="90"/>
                <circle class="score-gauge-fill" cx="100" cy="100" r="90"
                    style="stroke:${score.color};stroke-dasharray:${circumference};stroke-dashoffset:${circumference}"
                    id="gauge-fill"/>
            </svg>
            <div class="score-center">
                <div class="score-number" style="color:${score.color}" id="score-num">0</div>
                <div class="score-label">out of 100</div>
            </div>
        </div>
        <div class="score-grade" style="background:${score.color}15;color:${score.color};border:1px solid ${score.color}30">${score.label}</div>
        <div class="score-assessment">${overall.narrative}</div>
        <div class="score-breakdown">
            ${renderBreakdown(score.breakdown)}
        </div>
        <button class="analyze-btn visible" style="margin-top:24px;background:linear-gradient(135deg,#6c63ff,#00d4aa)" onclick="downloadPDF()">
            📄 Download PDF Report
        </button>
    `;

    // Animate gauge
    setTimeout(() => {
        const fill = document.getElementById('gauge-fill');
        if (fill) fill.style.strokeDashoffset = offset;
        animateNumber('score-num', 0, score.score, 1500);
    }, 300);

    // Animate breakdown bars
    setTimeout(() => {
        document.querySelectorAll('.breakdown-bar-fill').forEach(bar => {
            bar.style.width = bar.dataset.width;
        });
    }, 600);
}

function renderBreakdown(breakdown) {
    const items = [
        { key: 'clause_coverage', label: 'Clause Coverage', color: '#6c63ff' },
        { key: 'risk_density', label: 'Risk Safety', color: '#00d4aa' },
        { key: 'structure', label: 'Structure', color: '#4fc3f7' },
        { key: 'clarity', label: 'Language Clarity', color: '#ffab40' },
    ];
    return items.map(item => {
        const b = breakdown[item.key];
        const pct = ((b.score / b.max) * 100).toFixed(0);
        return `
            <div class="breakdown-item">
                <div class="breakdown-label">${item.label}</div>
                <div class="breakdown-bar">
                    <div class="breakdown-bar-fill" data-width="${pct}%" style="background:${item.color}"></div>
                </div>
                <div class="breakdown-score" style="color:${item.color}">${b.score} / ${b.max}</div>
                <div class="breakdown-detail">${b.details}</div>
            </div>
        `;
    }).join('');
}

function animateNumber(id, start, end, duration) {
    const el = document.getElementById(id);
    if (!el) return;
    const range = end - start;
    const startTime = performance.now();
    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + range * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ── Document Info ──
function renderDocInfo(doc) {
    const card = $('doc-info-card');
    card.innerHTML = `
        <div class="card-header">
            <div class="card-icon">📋</div>
            <h2>Document Overview</h2>
            <span class="card-badge" style="background:rgba(79,195,247,0.1);color:#4fc3f7;border:1px solid rgba(79,195,247,0.2)">${doc.file_type}</span>
        </div>
        <div class="doc-stats">
            <div class="doc-stat"><div class="stat-value">${doc.word_count.toLocaleString()}</div><div class="stat-label">Words</div></div>
            <div class="doc-stat"><div class="stat-value">${doc.sentence_count}</div><div class="stat-label">Sentences</div></div>
            <div class="doc-stat"><div class="stat-value">${doc.paragraph_count}</div><div class="stat-label">Paragraphs</div></div>
            <div class="doc-stat"><div class="stat-value">${doc.section_count}</div><div class="stat-label">Sections</div></div>
            ${doc.page_count ? `<div class="doc-stat"><div class="stat-value">${doc.page_count}</div><div class="stat-label">Pages</div></div>` : ''}
            <div class="doc-stat"><div class="stat-value">${doc.char_count.toLocaleString()}</div><div class="stat-label">Characters</div></div>
        </div>
    `;
}

// ── Critical Findings ──
function renderCritical(findings) {
    const card = $('critical-card');
    if (!findings || findings.length === 0) {
        card.innerHTML = `
            <div class="card-header">
                <div class="card-icon" style="background:rgba(0,230,118,0.1)">✅</div>
                <h2>Critical Findings</h2>
                <span class="card-badge" style="background:rgba(0,230,118,0.1);color:#00e676;border:1px solid rgba(0,230,118,0.2)">NONE</span>
            </div>
            <p style="color:var(--text-secondary)">No critical issues detected. The document meets basic compliance requirements.</p>
        `;
        return;
    }
    card.innerHTML = `
        <div class="card-header">
            <div class="card-icon" style="background:rgba(255,23,68,0.1)">🚨</div>
            <h2>Critical Findings</h2>
            <span class="card-badge" style="background:rgba(255,23,68,0.1);color:#ff5252;border:1px solid rgba(255,23,68,0.2)">${findings.length} FOUND</span>
        </div>
        <div class="risk-list">
            ${findings.map(f => `
                <div class="risk-item severity-HIGH">
                    <div class="risk-item-header">
                        <span>${f.icon}</span>
                        <span class="risk-category">${f.title}</span>
                        <span class="risk-severity-badge HIGH">CRITICAL</span>
                    </div>
                    <div class="risk-explanation">${f.explanation}</div>
                    ${f.evidence ? `<div class="risk-sentence" style="margin-top:8px">"${escHtml(f.evidence)}"</div>` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

// ── Clauses ──
function renderClauses(clauses) {
    const card = $('clauses-card');
    const items = Object.values(clauses.detected);
    const s = clauses.summary;

    card.innerHTML = `
        <div class="card-header">
            <div class="card-icon">🔎</div>
            <h2>Clause Detection</h2>
            <span class="card-badge" style="background:rgba(108,99,255,0.1);color:#6c63ff;border:1px solid rgba(108,99,255,0.2)">${s.found_count}/${s.total_clauses}</span>
        </div>
        <div class="clause-grid">
            ${items.map(c => `
                <div class="clause-item ${c.found ? 'found' : 'missing'}">
                    <span class="clause-icon">${c.icon}</span>
                    <div class="clause-info">
                        <div class="clause-name">${c.label}</div>
                        <div class="clause-desc">${c.description}</div>
                        ${c.found ? `<div class="clause-confidence">${c.confidence}% confidence</div>` : ''}
                    </div>
                    <span class="clause-status">${c.found ? '✅' : '❌'}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// ── Risks ──
function renderRisks(risks) {
    const card = $('risks-card');
    const s = risks.summary;
    const riskList = risks.risks;
    const showCount = 8;
    const hasMore = riskList.length > showCount;

    card.innerHTML = `
        <div class="card-header">
            <div class="card-icon" style="background:rgba(255,171,64,0.1)">⚠️</div>
            <h2>Risk Alerts</h2>
            <span class="card-badge" style="background:rgba(255,171,64,0.1);color:#ffab40;border:1px solid rgba(255,171,64,0.2)">${s.total_risks} RISKS</span>
        </div>
        <div class="risk-summary-bar">
            <div class="risk-count-badge high">🔴 ${s.high} High</div>
            <div class="risk-count-badge medium">🔶 ${s.medium} Medium</div>
            <div class="risk-count-badge low">🟡 ${s.low} Low</div>
        </div>
        <div class="risk-list" id="risk-list">
            ${riskList.slice(0, showCount).map(renderRiskItem).join('')}
        </div>
        ${hasMore ? `<button class="show-more-btn" onclick="toggleRisks(this)" data-expanded="false">Show ${riskList.length - showCount} more risks ▼</button>` : ''}
    `;

    // Store full risks for toggle
    if (hasMore) window._allRisks = riskList;
}

function renderRiskItem(r) {
    let sentenceHtml = escHtml(r.sentence);
    if (r.trigger) {
        const escaped = escHtml(r.trigger);
        sentenceHtml = sentenceHtml.replace(
            new RegExp(escRegex(escaped), 'i'),
            `<span class="trigger">${escaped}</span>`
        );
    }
    return `
        <div class="risk-item severity-${r.severity}">
            <div class="risk-item-header">
                <span>${r.icon}</span>
                <span class="risk-category">${r.category_label}</span>
                <span class="risk-severity-badge ${r.severity}">${r.severity}</span>
            </div>
            <div class="risk-sentence">"${sentenceHtml}"</div>
            <div class="risk-explanation">${r.description}</div>
        </div>
    `;
}

function toggleRisks(btn) {
    const list = document.getElementById('risk-list');
    const expanded = btn.dataset.expanded === 'true';
    const risks = window._allRisks || [];
    if (expanded) {
        list.innerHTML = risks.slice(0, 8).map(renderRiskItem).join('');
        btn.textContent = `Show ${risks.length - 8} more risks ▼`;
        btn.dataset.expanded = 'false';
    } else {
        list.innerHTML = risks.map(renderRiskItem).join('');
        btn.textContent = 'Show less ▲';
        btn.dataset.expanded = 'true';
    }
}

// ── Action Items ──
function renderActions(actions) {
    const card = $('actions-card');
    if (!actions || actions.length === 0) {
        card.style.display = 'none';
        return;
    }
    card.style.display = '';
    card.innerHTML = `
        <div class="card-header">
            <div class="card-icon" style="background:rgba(0,212,170,0.1)">💡</div>
            <h2>Recommended Actions</h2>
            <span class="card-badge" style="background:rgba(0,212,170,0.1);color:#00d4aa;border:1px solid rgba(0,212,170,0.2)">${actions.length} ITEMS</span>
        </div>
        <div class="action-list">
            ${actions.map((a, i) => `
                <div class="action-item">
                    <div class="action-priority ${a.severity}">${i + 1}</div>
                    <div class="action-content">
                        <div class="action-title">${a.icon} ${a.action}</div>
                        <div class="action-detail">${a.detail}</div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// ── Rewrites ──
function renderRewrites(rewrites) {
    const card = $('rewrites-card');
    if (!rewrites || rewrites.length === 0) {
        card.style.display = 'none';
        return;
    }
    card.style.display = '';
    const showCount = 5;
    const hasMore = rewrites.length > showCount;

    card.innerHTML = `
        <div class="card-header">
            <div class="card-icon" style="background:rgba(108,99,255,0.1)">✍️</div>
            <h2>Suggested Rewrites</h2>
            <span class="card-badge" style="background:rgba(108,99,255,0.1);color:#6c63ff;border:1px solid rgba(108,99,255,0.2)">${rewrites.length}</span>
        </div>
        <div class="rewrite-list" id="rewrite-list">
            ${rewrites.slice(0, showCount).map(renderRewriteItem).join('')}
        </div>
        ${hasMore ? `<button class="show-more-btn" onclick="toggleRewrites(this)" data-expanded="false">Show ${rewrites.length - showCount} more ▼</button>` : ''}
    `;
    if (hasMore) window._allRewrites = rewrites;
}

function renderRewriteItem(rw) {
    return `
        <div class="rewrite-item">
            <div class="rewrite-original">
                <span class="rewrite-label original">✗ Original</span>
                ${escHtml(rw.original)}
            </div>
            <div class="rewrite-improved">
                <span class="rewrite-label improved">✓ Improved</span>
                ${escHtml(rw.rewritten)}
                ${rw.changes.length ? `
                    <div class="rewrite-changes">
                        ${rw.changes.map(c => `<span class="rewrite-change">${escHtml(c)}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function toggleRewrites(btn) {
    const list = document.getElementById('rewrite-list');
    const expanded = btn.dataset.expanded === 'true';
    const items = window._allRewrites || [];
    if (expanded) {
        list.innerHTML = items.slice(0, 5).map(renderRewriteItem).join('');
        btn.textContent = `Show ${items.length - 5} more ▼`;
        btn.dataset.expanded = 'false';
    } else {
        list.innerHTML = items.map(renderRewriteItem).join('');
        btn.textContent = 'Show less ▲';
        btn.dataset.expanded = 'true';
    }
}

// ══════════════════════ UTILS ══════════════════════
function escHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function escRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function showError(msg) {
    errorToast.textContent = '⚠️ ' + msg;
    errorToast.classList.add('visible');
    setTimeout(() => errorToast.classList.remove('visible'), 5000);
}

// ══════════════════════ PDF DOWNLOAD ══════════════════════
async function downloadPDF() {
    try {
        const res = await fetch('/api/report', { method: 'POST' });
        if (!res.ok) {
            const data = await res.json();
            showError(data.error || 'PDF generation failed.');
            return;
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `compliance_report_${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch (err) {
        showError('Failed to download PDF report.');
    }
}
