/* ═══════════════════════════════════════════════════════════════
   CCAR-F Labs — Frontend Application  (v2)
   ═══════════════════════════════════════════════════════════════ */

const App = (() => {
  // ── State ────────────────────────────────────────────────────
  let labs = [];
  let currentLab = null;
  let currentStep = 0;
  let editor = null;
  let dryRunMode = true;
  let challengeMode = false;
  let completedSteps = {};
  let apiKeyConfigured = false;

  // Load saved progress
  try { completedSteps = JSON.parse(localStorage.getItem('ccar_completed') || '{}'); } catch(e) {}

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ── Markdown renderer ────────────────────────────────────────
  function renderMd(text) {
    if (!text) return '';
    return text
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/^- (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
      .replace(/<\/ul>\s*<ul>/g, '')
      .replace(/\n{2,}/g, '</p><p>');
  }

  // ── Init ─────────────────────────────────────────────────────
  async function init() {
    await loadLabs();
    await checkHealth();
    renderSidebar();
    renderWelcome();
    setupResizer();
    setupSidebarToggle();
  }

  async function loadLabs() {
    try {
      const res = await fetch('/api/labs');
      labs = await res.json();
    } catch (e) { console.error('Failed to load labs:', e); }
  }

  async function checkHealth() {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      apiKeyConfigured = data.api_key_configured;
      if (apiKeyConfigured) dryRunMode = false;
    } catch (e) { apiKeyConfigured = false; }
  }

  // ── Sidebar ──────────────────────────────────────────────────
  function renderSidebar() {
    const labList = $('.lab-list');
    const grouped = {};
    labs.forEach(lab => {
      const key = `D${lab.domain}`;
      if (!grouped[key]) grouped[key] = { name: lab.domain_name, labs: [] };
      grouped[key].labs.push(lab);
    });

    let html = '';
    Object.entries(grouped).forEach(([key, group]) => {
      html += `<div class="domain-group">
        <div class="domain-header">${key} — ${group.name}</div>`;
      group.labs.forEach(lab => {
        const done = isLabComplete(lab.id);
        html += `
          <div class="lab-item ${done ? 'completed' : ''} ${currentLab?.id === lab.id ? 'active' : ''}"
               data-id="${lab.id}" onclick="App.selectLab('${lab.id}')">
            <span class="lab-num">${lab.id}</span>
            <span class="lab-name" title="${lab.title}">${lab.title}</span>
            <span class="lab-check">✓</span>
            <span class="lab-time">${lab.estimated_time}</span>
          </div>`;
      });
      html += `</div>`;
    });
    labList.innerHTML = html;
    updateProgress();
    updateKeyBtn();
  }

  function isLabComplete(labId) {
    const lab = labs.find(l => l.id === labId);
    if (!lab) return false;
    for (let i = 1; i <= lab.step_count; i++) {
      if (!completedSteps[`${labId}-${i}`]) return false;
    }
    return true;
  }

  function updateProgress() {
    let total = 0, done = 0;
    labs.forEach(lab => {
      for (let i = 1; i <= lab.step_count; i++) {
        total++;
        if (completedSteps[`${lab.id}-${i}`]) done++;
      }
    });
    const pct = total ? Math.round((done / total) * 100) : 0;
    const fill = $('.progress-fill');
    const label = $('.progress-count');
    if (fill) fill.style.width = pct + '%';
    if (label) label.textContent = `${done}/${total} steps`;
  }

  function updateKeyBtn() {
    const btn = $('.sidebar-footer-btn');
    if (!btn) return;
    if (apiKeyConfigured) {
      btn.className = 'sidebar-footer-btn key-ok';
      btn.innerHTML = '🟢 API Key Active';
    } else {
      btn.className = 'sidebar-footer-btn';
      btn.innerHTML = '🔑 Set API Key';
    }
  }

  // ── Welcome Screen ───────────────────────────────────────────
  function getDomainProgress() {
    const domains = [
      { key: 1, name: 'Agentic Architecture', weight: '27%' },
      { key: 2, name: 'Tool Design & MCP',    weight: '18%' },
      { key: 3, name: 'Claude Code',           weight: '20%' },
      { key: 4, name: 'Prompt Engineering',    weight: '20%' },
      { key: 5, name: 'Context Management',    weight: '15%' },
    ];
    let totalAll = 0, doneAll = 0;
    const result = domains.map(d => {
      const domainLabs = labs.filter(l => l.domain === d.key);
      let total = 0, done = 0;
      domainLabs.forEach(lab => {
        for (let i = 1; i <= lab.step_count; i++) {
          total++;
          if (completedSteps[`${lab.id}-${i}`]) done++;
        }
      });
      totalAll += total;
      doneAll += done;
      return { ...d, total, done, pct: total ? Math.round((done / total) * 100) : 0 };
    });
    return { domains: result, totalAll, doneAll, pctAll: totalAll ? Math.round((doneAll / totalAll) * 100) : 0 };
  }

  function renderWelcome() {
    const main = $('.main');
    const totalSteps = labs.reduce((s, l) => s + l.step_count, 0);
    const firstLab = labs.length > 0 ? labs[0].id : null;
    const prog = getDomainProgress();

    // SVG ring math
    const R = 38, C = 2 * Math.PI * R;
    const offset = C - (prog.pctAll / 100) * C;

    // Find the best next lab to resume
    let resumeLab = firstLab;
    for (const lab of labs) {
      if (!isLabComplete(lab.id)) { resumeLab = lab.id; break; }
    }
    const resumeLabel = prog.doneAll === 0 ? 'Start Lab 1.1 →'
      : prog.pctAll === 100 ? '🎉 All Labs Complete!'
      : `Continue ${resumeLab} →`;

    main.innerHTML = `
      <div class="welcome">
        <div class="welcome-inner">
          <div class="welcome-icon">🧪</div>
          <h2>CCAR-F Interactive Labs</h2>
          <p>Hands-on coding labs covering all 5 exam domains.
             Write real Claude API code, run it live, and learn
             the patterns the exam actually tests.</p>
          <div class="stats">
            <div class="stat">
              <div class="stat-num">${labs.length}</div>
              <div class="stat-label">Labs</div>
            </div>
            <div class="stat">
              <div class="stat-num">${totalSteps}</div>
              <div class="stat-label">Steps</div>
            </div>
            <div class="stat">
              <div class="stat-num">5</div>
              <div class="stat-label">Domains</div>
            </div>
          </div>

          <!-- Progress Dashboard -->
          <div class="progress-dashboard">
            <div class="progress-dashboard-header">
              <span class="progress-dashboard-title">Your Progress</span>
            </div>

            <div class="progress-ring-wrap">
              <div class="progress-ring-container">
                <svg width="90" height="90" viewBox="0 0 90 90">
                  <defs>
                    <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#8b5cf6"/>
                      <stop offset="100%" stop-color="#c084fc"/>
                    </linearGradient>
                  </defs>
                  <circle class="progress-ring-bg" cx="45" cy="45" r="${R}"/>
                  <circle class="progress-ring-fill" cx="45" cy="45" r="${R}"
                    stroke-dasharray="${C}"
                    stroke-dashoffset="${C}"
                    data-target="${offset}"/>
                </svg>
                <div class="progress-ring-text">
                  <span class="progress-ring-pct">${prog.pctAll}%</span>
                  <span class="progress-ring-label">complete</span>
                </div>
              </div>
              <div class="progress-ring-info">
                <h3>${prog.doneAll} of ${prog.totalAll} steps done</h3>
                <p>${prog.pctAll === 0 ? 'Ready to begin your exam prep journey!'
                   : prog.pctAll === 100 ? 'Outstanding — every lab complete! 🎉'
                   : prog.pctAll >= 50 ? 'Great momentum — keep going!'
                   : 'Good start — keep building!'}</p>
              </div>
            </div>

            <div class="domain-bars">
              ${prog.domains.map((d, i) => `
                <div class="domain-bar-row">
                  <span class="domain-bar-label" title="${d.name}">D${d.key} ${d.name}</span>
                  <div class="domain-bar-track">
                    <div class="domain-bar-fill d${d.key}" data-pct="${d.pct}"></div>
                  </div>
                  <span class="domain-bar-count">${d.done}/${d.total}</span>
                </div>`).join('')}
            </div>

            <div class="session-actions">
              <button class="session-btn" onclick="App.exportSession()" title="Save your progress to a file">
                ⬇ Export Progress
              </button>
              <button class="session-btn" onclick="document.getElementById('importFile').click()" title="Restore progress from a file">
                ⬆ Import Progress
                <input type="file" id="importFile" accept=".json" onchange="App.importSession(event)">
              </button>
              <button class="session-btn danger" onclick="App.resetProgress()" title="Clear all progress">
                ✕ Reset
              </button>
            </div>
          </div>

          <div class="health-badge ${apiKeyConfigured ? 'ok' : 'no-key'}"
               onclick="App.openSettings()">
            <span class="health-dot"></span>
            ${apiKeyConfigured
              ? 'API Key configured — Live mode ready'
              : 'No API key — click to configure'}
          </div>
          <div class="welcome-cta">
            ${resumeLab && prog.pctAll < 100
              ? `<button class="btn-start" onclick="App.selectLab('${resumeLab}')">${resumeLabel}</button>`
              : (prog.pctAll === 100 ? `<div style="font-size:14px;color:var(--green);font-weight:700;margin-top:8px">${resumeLabel}</div>` : '')}
          </div>
        </div>
      </div>`;

    // Animate the ring and bars after paint
    requestAnimationFrame(() => {
      setTimeout(() => {
        const ring = main.querySelector('.progress-ring-fill');
        if (ring) ring.style.strokeDashoffset = ring.dataset.target;
        main.querySelectorAll('.domain-bar-fill').forEach(bar => {
          bar.style.width = bar.dataset.pct + '%';
        });
      }, 60);
    });
  }

  // ── Session Export / Import ──────────────────────────────────
  function exportSession() {
    const data = {
      version: 1,
      app: 'ccar-f-labs',
      exportedAt: new Date().toISOString(),
      completedSteps,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const date = new Date().toISOString().slice(0, 10);
    a.download = `ccar-f-progress-${date}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function importSession(event) {
    const file = event?.target?.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        if (!data.completedSteps || typeof data.completedSteps !== 'object') {
          alert('Invalid session file — no progress data found.');
          return;
        }
        // Merge: imported steps override (union)
        Object.assign(completedSteps, data.completedSteps);
        try { localStorage.setItem('ccar_completed', JSON.stringify(completedSteps)); } catch(err) {}
        updateProgress();
        renderSidebar();
        renderWelcome();
      } catch (err) {
        alert('Could not read the file. Make sure it is a valid CCAR-F progress JSON file.');
      }
    };
    reader.readAsText(file);
    // Reset file input so the same file can be re-imported
    event.target.value = '';
  }

  function resetProgress() {
    if (!confirm('This will clear all your progress. Are you sure?')) return;
    completedSteps = {};
    try { localStorage.setItem('ccar_completed', JSON.stringify(completedSteps)); } catch(e) {}
    updateProgress();
    renderSidebar();
    renderWelcome();
  }

  function goHome() {
    currentLab = null;
    currentStep = 0;
    // Clear active state in sidebar
    $$('.lab-item').forEach(el => el.classList.remove('active'));
    renderWelcome();
  }

  // ── Load Lab ─────────────────────────────────────────────────
  async function selectLab(labId) {
    $('.sidebar')?.classList.remove('open');
    try {
      const res = await fetch(`/api/labs/${labId}`);
      currentLab = await res.json();
      currentStep = 0;
      renderLabView();
      // Update sidebar active state
      $$('.lab-item').forEach(el => {
        el.classList.toggle('active', el.dataset.id === labId);
      });
    } catch (e) { console.error('Failed to load lab:', e); }
  }

  // ── Lab View ─────────────────────────────────────────────────
  function renderLabView() {
    const main = $('.main');
    const step = currentLab.steps[currentStep];

    main.innerHTML = `
      <div class="topbar">
        <div class="topbar-row-1">
          <div class="lab-title">
            <span class="lab-id">${currentLab.id}</span> ${currentLab.title}
          </div>
        </div>
        <div class="topbar-row-2">
          <div class="step-pills">
            ${currentLab.steps.map((s, i) => {
              const done = completedSteps[`${currentLab.id}-${s.id}`];
              return `<div class="step-pill ${i === currentStep ? 'active' : ''} ${done ? 'done' : ''}"
                           onclick="App.goStep(${i})">${s.id}</div>`;
            }).join('')}
          </div>
          <div class="topbar-sep"></div>
          <div class="mode-toggles">
            <button class="mode-btn ${dryRunMode ? 'active' : ''}"
                    onclick="App.toggleDryRun()" title="Use pre-built output (no API cost)">
              🛡️ Dry Run
            </button>
            <button class="mode-btn challenge-btn ${challengeMode ? 'active' : ''}"
                    onclick="App.toggleChallenge()" title="Hide starter code">
              ⚡ Challenge
            </button>
          </div>
          <span class="step-label">Step ${step.id} of ${currentLab.steps.length}</span>
        </div>
      </div>

      <div class="content-split">
        <div class="panel-instructions">
          <div class="panel-header">
            <span class="icon">📖</span>
            <span class="label">Instructions</span>
          </div>
          <div class="instructions-body">
            <div class="md">${renderMd(step.instruction)}</div>
            ${renderExamTips(step.exam_tips)}
            ${renderHints(step.hints)}
          </div>
        </div>

        <div class="panel-editor">
          <div class="editor-toolbar">
            <span class="lang-badge">${step.language || 'python'}</span>
            <div class="spacer"></div>
            <button class="btn btn-reset" onclick="App.resetCode()" title="Reset to starter code">↺ Reset</button>
            <button class="btn btn-solution" onclick="App.showSolution()" title="Show solution">💡 Solution</button>
            <button class="btn btn-run" id="runBtn" onclick="App.runCode()" title="Ctrl+Enter">
              ▶ ${dryRunMode ? 'Dry Run' : 'Run'}
            </button>
          </div>
          <div class="editor-container" id="editorContainer"></div>
          <div class="resize-handle" id="resizeHandle"></div>
          <div class="output-panel" id="outputPanel">
            <div class="output-header">
              <span class="label">Output</span>
              <span class="status-badge" id="statusBadge" style="display:none"></span>
              <div style="flex:1"></div>
              ${currentStep < currentLab.steps.length - 1 ? `
              <button class="btn btn-next" onclick="App.nextStep()">Next Step →</button>`
              : `<button class="btn btn-next" onclick="App.markComplete()">✓ Complete Lab</button>`}
            </div>
            <div class="output-body" id="outputBody">Click ▶ ${dryRunMode ? 'Dry Run' : 'Run'} to execute your code — or press Ctrl+Enter</div>
          </div>
        </div>
      </div>`;

    initEditor(step);
  }

  function renderExamTips(tips) {
    if (!tips?.length) return '';
    return tips.map(t => `
      <div class="exam-tip">
        <div class="tip-label">🎯 Exam Tip</div>
        ${t}
      </div>`).join('');
  }

  function renderHints(hints) {
    if (!hints?.length) return '';
    return hints.map((h, i) => `
      <div class="hint-box" onclick="this.classList.toggle('open')">
        <div class="hint-toggle">💡 Hint ${i + 1} — Click to reveal</div>
        <div class="hint-content">${h}</div>
      </div>`).join('');
  }

  // ── Monaco Editor ────────────────────────────────────────────
  function initEditor(step) {
    const container = $('#editorContainer');
    if (!container) return;

    const code = challengeMode
      ? `# Challenge mode — write your solution from scratch!\n# Refer to the instructions on the left.\n\n`
      : (step.starter_code || '');

    if (window.monaco) {
      createEditor(container, code, step.language || 'python');
    } else {
      container.innerHTML = '<div style="padding:20px;color:var(--text-muted)">Loading editor...</div>';
      const check = setInterval(() => {
        if (window.monaco) {
          clearInterval(check);
          container.innerHTML = '';
          createEditor(container, code, step.language || 'python');
        }
      }, 100);
    }
  }

  function createEditor(container, code, language) {
    editor = monaco.editor.create(container, {
      value: code,
      language,
      theme: 'ccar-dark',
      fontFamily: "'JetBrains Mono', monospace",
      fontSize: 13,
      lineHeight: 22,
      padding: { top: 12, bottom: 12 },
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 4,
      wordWrap: 'on',
      renderLineHighlight: 'line',
      cursorBlinking: 'smooth',
      smoothScrolling: true,
      bracketPairColorization: { enabled: true },
      scrollbar: { verticalScrollbarSize: 6, horizontalScrollbarSize: 6 },
    });

    editor.addAction({
      id: 'run-code',
      label: 'Run Code',
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
      run: () => runCode(),
    });
  }

  // ── Run Code ─────────────────────────────────────────────────
  async function runCode() {
    if (!editor) return;
    const code = editor.getValue();
    const step = currentLab.steps[currentStep];
    const runBtn = $('#runBtn');
    const outputBody = $('#outputBody');
    const badge = $('#statusBadge');

    runBtn.disabled = true;
    runBtn.innerHTML = '<span class="spinner"></span> Running...';
    badge.style.display = 'inline';
    badge.className = 'status-badge running';
    badge.textContent = dryRunMode ? 'DRY RUN' : 'RUNNING';
    outputBody.textContent = dryRunMode ? 'Fetching dry-run output...' : 'Executing code...';

    try {
      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          dry_run: dryRunMode,
          lab_id: currentLab.id,
          step_id: step.id,
        }),
      });
      const data = await res.json();

      if (data.dry_run) {
        badge.className = 'status-badge dry-run';
        badge.textContent = 'DRY RUN';
        outputBody.innerHTML = `<span class="dry-run-text">${escHtml(data.stdout || data.stderr || '(no output)')}</span>`;
      } else if (data.returncode === 0) {
        badge.className = 'status-badge success';
        badge.textContent = 'SUCCESS';
        outputBody.textContent = data.stdout || '(no output)';
        markStepDone(currentLab.id, step.id);
      } else {
        badge.className = 'status-badge error';
        badge.textContent = data.timed_out ? 'TIMEOUT' : 'ERROR';
        let out = '';
        if (data.stdout) out += data.stdout;
        if (data.stderr) out += (out ? '\n' : '') + data.stderr;
        outputBody.innerHTML = `<span class="error-text">${escHtml(out || '(no output)')}</span>`;
      }
    } catch (e) {
      badge.className = 'status-badge error';
      badge.textContent = 'ERROR';
      outputBody.innerHTML = `<span class="error-text">Network error: ${escHtml(e.message)}</span>`;
    }

    runBtn.disabled = false;
    runBtn.innerHTML = `▶ ${dryRunMode ? 'Dry Run' : 'Run'}`;
  }

  function escHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  // ── Navigation ───────────────────────────────────────────────
  function goStep(idx) {
    if (idx < 0 || idx >= currentLab.steps.length) return;
    currentStep = idx;
    renderLabView();
  }

  function nextStep() {
    markStepDone(currentLab.id, currentLab.steps[currentStep].id);
    goStep(currentStep + 1);
  }

  function markStepDone(labId, stepId) {
    completedSteps[`${labId}-${stepId}`] = true;
    try { localStorage.setItem('ccar_completed', JSON.stringify(completedSteps)); } catch(e) {}
    updateProgress();
    // Refresh sidebar completion state
    $$('.lab-item').forEach(el => {
      if (el.dataset.id) {
        el.classList.toggle('completed', isLabComplete(el.dataset.id));
      }
    });
    // Update step pills in topbar
    $$('.step-pill').forEach((pill, i) => {
      const s = currentLab.steps[i];
      if (s && completedSteps[`${labId}-${s.id}`]) pill.classList.add('done');
    });
  }

  function markComplete() {
    markStepDone(currentLab.id, currentLab.steps[currentStep].id);
    const idx = labs.findIndex(l => l.id === currentLab.id);
    if (idx < labs.length - 1) {
      selectLab(labs[idx + 1].id);
    } else {
      renderWelcome();
    }
  }

  // ── Code Actions ─────────────────────────────────────────────
  function resetCode() {
    if (!editor || !currentLab) return;
    const step = currentLab.steps[currentStep];
    editor.setValue(challengeMode
      ? `# Challenge mode — write your solution from scratch!\n# Refer to the instructions on the left.\n\n`
      : (step.starter_code || ''));
  }

  function showSolution() {
    if (!editor || !currentLab) return;
    const step = currentLab.steps[currentStep];
    if (step.solution_code) editor.setValue(step.solution_code);
  }

  // ── Mode Toggles ─────────────────────────────────────────────
  function toggleDryRun() {
    if (!dryRunMode && !apiKeyConfigured) {
      // Already in dry-run, trying to leave it without key
    }
    if (dryRunMode && !apiKeyConfigured) {
      // Turning dry-run OFF but no key — prompt for key
      openSettings();
      return;
    }
    dryRunMode = !dryRunMode;
    if (currentLab) renderLabView();
  }

  function toggleChallenge() {
    challengeMode = !challengeMode;
    if (currentLab) renderLabView();
  }

  // ── Settings Modal ───────────────────────────────────────────
  function openSettings() {
    // Don't create duplicates
    if ($('.modal-overlay')) {
      $('.modal-overlay').classList.add('open');
      return;
    }

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal">
        <div class="modal-header">
          <h3>🔑 API Key Settings</h3>
          <button class="modal-close" onclick="App.closeSettings()">✕</button>
        </div>
        <div class="modal-body">
          <p>Enter your Anthropic API key to enable <strong>Live Run mode</strong>.
             Your key is stored locally in the Docker container and never leaves your machine.</p>
          <div class="input-group">
            <label>Anthropic API Key</label>
            <input type="password" id="apiKeyInput"
                   placeholder="sk-ant-api03-..."
                   value="" autocomplete="off" spellcheck="false">
            <div class="input-hint">
              Get your key from
              <a href="https://console.anthropic.com/settings/keys"
                 target="_blank" rel="noopener"
                 style="color:var(--accent)">console.anthropic.com</a>
            </div>
          </div>
          <div class="modal-feedback" id="keyFeedback"></div>
        </div>
        <div class="modal-footer">
          <button class="btn-modal-cancel" onclick="App.closeSettings()">Cancel</button>
          <button class="btn-modal-save" id="saveKeyBtn" onclick="App.saveKey()">Save Key</button>
        </div>
      </div>`;

    document.body.appendChild(overlay);

    // Click outside to close
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeSettings();
    });

    // Enter key to save
    setTimeout(() => {
      const input = $('#apiKeyInput');
      if (input) {
        input.focus();
        input.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') saveKey();
        });
      }
      overlay.classList.add('open');
    }, 10);
  }

  function closeSettings() {
    const overlay = $('.modal-overlay');
    if (overlay) {
      overlay.classList.remove('open');
      setTimeout(() => overlay.remove(), 200);
    }
  }

  async function saveKey() {
    const input = $('#apiKeyInput');
    const feedback = $('#keyFeedback');
    const btn = $('#saveKeyBtn');
    if (!input) return;

    const key = input.value.trim();

    if (!key) {
      feedback.className = 'modal-feedback error';
      feedback.textContent = 'Please enter your API key.';
      return;
    }
    if (!key.startsWith('sk-ant-')) {
      feedback.className = 'modal-feedback error';
      feedback.textContent = 'Key must start with sk-ant-';
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Saving...';

    try {
      const res = await fetch('/api/key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key }),
      });

      if (res.ok) {
        apiKeyConfigured = true;
        dryRunMode = false;
        feedback.className = 'modal-feedback success';
        feedback.textContent = '✓ API key saved! Live mode is now active.';
        updateKeyBtn();

        setTimeout(() => {
          closeSettings();
          if (currentLab) renderLabView();
          else renderWelcome();
        }, 1000);
      } else {
        const err = await res.json();
        feedback.className = 'modal-feedback error';
        feedback.textContent = err.detail || 'Failed to save key.';
      }
    } catch (e) {
      feedback.className = 'modal-feedback error';
      feedback.textContent = 'Network error — is the server running?';
    }

    btn.disabled = false;
    btn.textContent = 'Save Key';
  }

  // ── Output Resizer ───────────────────────────────────────────
  function setupResizer() {
    document.addEventListener('mousedown', (e) => {
      const handle = e.target.closest('.resize-handle');
      if (!handle) return;
      const panel = handle.nextElementSibling;
      if (!panel) return;

      handle.classList.add('active');
      const startY = e.clientY;
      const startH = panel.offsetHeight;

      function onMove(e2) {
        panel.style.height = Math.max(80, startH + (startY - e2.clientY)) + 'px';
      }
      function onUp() {
        handle.classList.remove('active');
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
      }
      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  }

  function setupSidebarToggle() {
    const btn = $('.sidebar-toggle');
    if (btn) btn.addEventListener('click', () => $('.sidebar')?.classList.toggle('open'));
  }

  // ── Public API ───────────────────────────────────────────────
  return {
    init, selectLab, goStep, nextStep, runCode, resetCode,
    showSolution, toggleDryRun, toggleChallenge, markComplete,
    openSettings, closeSettings, saveKey,
    exportSession, importSession, resetProgress, goHome,
  };
})();

// ── Monaco Theme ───────────────────────────────────────────────
function registerMonacoTheme() {
  monaco.editor.defineTheme('ccar-dark', {
    base: 'vs-dark', inherit: true,
    rules: [
      { token: 'comment',   foreground: '555568', fontStyle: 'italic' },
      { token: 'keyword',   foreground: 'c084fc' },
      { token: 'string',    foreground: '34d399' },
      { token: 'number',    foreground: 'fbbf24' },
      { token: 'type',      foreground: '60a5fa' },
      { token: 'function',  foreground: '8b5cf6' },
      { token: 'variable',  foreground: 'e8e8f0' },
      { token: 'operator',  foreground: 'f87171' },
      { token: 'delimiter', foreground: '8888a0' },
    ],
    colors: {
      'editor.background':                '#0a0a0f',
      'editor.foreground':                '#e8e8f0',
      'editor.lineHighlightBackground':   '#16161f',
      'editor.selectionBackground':       '#8b5cf633',
      'editorCursor.foreground':          '#8b5cf6',
      'editorLineNumber.foreground':      '#333345',
      'editorLineNumber.activeForeground':'#8b5cf6',
      'editorIndentGuide.background1':    '#1a1a24',
      'editorIndentGuide.activeBackground1':'#333345',
      'editorBracketMatch.background':    '#8b5cf630',
      'editorBracketMatch.border':        '#8b5cf680',
      'scrollbarSlider.background':       '#22222e80',
      'scrollbarSlider.hoverBackground':  '#333345',
    },
  });
}

// ── Boot ────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  function boot() {
    require.config({
      paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }
    });
    require(['vs/editor/editor.main'], () => {
      registerMonacoTheme();
      App.init();
    });
  }

  if (window.require) { boot(); }
  else {
    const check = setInterval(() => {
      if (window.require) { clearInterval(check); boot(); }
    }, 50);
  }
});
