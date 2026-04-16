/**
 * 主应用逻辑
 * Tab 切换、表单提交、模式切换
 */

let currentData = null;
let currentSection = 'overview';
let isClaudeMode = false;

// 分析状态
let analysisCache = {};   // { section: fullText } 已完成的分析
let sectionTexts = {};    // { section: partialText } 进行中的流式文本
let pendingStreams = {};   // { section: AbortController } 进行中的流

// ── 状态重置（起卦 / 模式切换时调用）────────────────────────────────────────

function resetAnalysisState() {
  Object.values(pendingStreams).forEach(c => c.abort());
  pendingStreams = {};
  analysisCache = {};
  sectionTexts = {};
}

// ── 模式切换 ──────────────────────────────────────────────────────────────────

document.getElementById('mode-toggle-input').addEventListener('change', function() {
  isClaudeMode = this.checked;
  updateModeLabel();
  if (currentData) {
    resetAnalysisState();
    loadAnalysis(currentSection);
    document.getElementById('chat-card').style.display = isClaudeMode ? 'block' : 'none';
  }
});

function updateModeLabel() {
  const leftLabel = document.getElementById('mode-label-left');
  const rightLabel = document.getElementById('mode-label-right');
  if (isClaudeMode) {
    leftLabel.style.opacity = '0.5';
    rightLabel.style.opacity = '1';
    rightLabel.style.color = 'var(--gold)';
    leftLabel.style.color = 'var(--text-muted)';
  } else {
    leftLabel.style.opacity = '1';
    rightLabel.style.opacity = '0.5';
    leftLabel.style.color = 'var(--gold)';
    rightLabel.style.color = 'var(--text-muted)';
  }
}
updateModeLabel();

// ── Tab 切换 ──────────────────────────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    currentSection = this.dataset.section;
    if (currentData) loadAnalysis(currentSection);
  });
});

// ── 表单提交（起卦）──────────────────────────────────────────────────────────

document.getElementById('birth-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  await calculateBazi();
});

async function calculateBazi() {
  const year   = parseInt(document.getElementById('birth-year').value);
  const month  = parseInt(document.getElementById('birth-month').value);
  const day    = parseInt(document.getElementById('birth-day').value);
  const hour   = parseInt(document.getElementById('birth-hour').value);
  const minute = parseInt(document.getElementById('birth-minute').value) || 0;
  const gender = document.getElementById('birth-gender').value;

  showLoading();

  try {
    const response = await fetch('/api/bazi/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ year, month, day, hour, minute, gender })
    });

    const result = await response.json();

    if (result.success) {
      currentData = result.data;
      resetAnalysisState(); // 新起卦，清空所有缓存和流

      renderPillars(currentData);
      renderWuxing(currentData);
      renderDayun(currentData);

      if (isClaudeMode) {
        initChat(currentData);
      } else {
        document.getElementById('chat-card').style.display = 'none';
      }

      loadAnalysis(currentSection);
    } else {
      showError('计算失败：' + (result.detail || '未知错误'));
    }
  } catch (err) {
    showError('网络错误：' + err.message);
  }
}

// ── 分析加载（带缓存 + 流式状态感知）────────────────────────────────────────

function loadAnalysis(section) {
  if (!currentData) return;

  // 1. 已完成：直接从缓存渲染
  if (analysisCache[section] !== undefined) {
    renderContent(section, analysisCache[section], false);
    return;
  }

  // 2. 正在流式加载：显示已积累的部分内容 + 光标
  if (pendingStreams[section]) {
    const textEl = document.getElementById('analysis-text');
    document.getElementById('analysis-loading').style.display = 'none';
    document.getElementById('analysis-placeholder').style.display = 'none';
    const partial = sectionTexts[section] || '';
    textEl.innerHTML = isClaudeMode ? marked.parse(partial) : partial;
    textEl.style.display = 'block';
    textEl.classList.add('typing-cursor');
    return;
  }

  // 3. 尚未加载：发起请求
  showLoading();
  if (isClaudeMode) {
    initChat(currentData);
    loadClaudeAnalysis(section); // 不 await，后台运行
  } else {
    loadRulesAnalysis(section);
  }
}

// ── 规则引擎加载 ──────────────────────────────────────────────────────────────

async function loadRulesAnalysis(section) {
  try {
    const response = await fetch('/api/analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bazi_data: currentData.bazi,
        wuxing_analysis: currentData.wuxing,
        dayun_data: currentData.dayun,
        mode: 'rules',
        section
      })
    });

    const result = await response.json();
    if (result.success) {
      analysisCache[section] = result.text;
      if (currentSection === section) renderContent(section, result.text, false);
    } else {
      if (currentSection === section) showError('分析失败');
    }
  } catch (err) {
    if (currentSection === section) showError('错误：' + err.message);
  }
}

// ── Claude 流式加载（后台运行，不阻塞 Tab 切换）──────────────────────────────

async function loadClaudeAnalysis(section) {
  const controller = new AbortController();
  pendingStreams[section] = controller;
  sectionTexts[section] = '';

  // 如果当前正在看这个 Tab，切换到流式展示状态
  if (currentSection === section) {
    const textEl = document.getElementById('analysis-text');
    document.getElementById('analysis-loading').style.display = 'none';
    document.getElementById('analysis-placeholder').style.display = 'none';
    textEl.textContent = '';
    textEl.style.display = 'block';
    textEl.classList.add('typing-cursor');
  }

  try {
    const response = await fetch('/api/analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bazi_data: currentData.bazi,
        wuxing_analysis: currentData.wuxing,
        dayun_data: currentData.dayun,
        mode: 'claude',
        section
      }),
      signal: controller.signal
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    outer: while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (controller.signal.aborted) break outer;
        if (!line.startsWith('data: ')) continue;

        const data = line.slice(6);

        if (data === '[DONE]') {
          // 流结束：写入缓存，更新 DOM（如果用户当前在此 Tab）
          analysisCache[section] = fullText;
          delete pendingStreams[section];
          delete sectionTexts[section];
          if (currentSection === section) {
            renderContent(section, fullText, false);
          }
          break outer;
        }

        try {
          const parsed = JSON.parse(data);
          if (parsed.text) {
            fullText += parsed.text;
            sectionTexts[section] = fullText;
            // 只在用户当前查看此 Tab 时更新 DOM
            if (currentSection === section) {
              document.getElementById('analysis-text').innerHTML = marked.parse(fullText);
            }
          }
          if (parsed.error && currentSection === section) {
            showError(parsed.error);
          }
        } catch (e) {}
      }
    }
  } catch (err) {
    delete pendingStreams[section];
    delete sectionTexts[section];
    if (err.name !== 'AbortError' && currentSection === section) {
      document.getElementById('analysis-text').classList.remove('typing-cursor');
      showError('流式传输错误：' + err.message);
    }
  }
}

// ── UI 工具函数 ───────────────────────────────────────────────────────────────

function renderContent(section, text, streaming) {
  const textEl = document.getElementById('analysis-text');
  document.getElementById('analysis-placeholder').style.display = 'none';
  document.getElementById('analysis-loading').style.display = 'none';
  textEl.classList.remove('typing-cursor');
  if (isClaudeMode) {
    textEl.innerHTML = marked.parse(text);
  } else {
    textEl.textContent = text;
  }
  textEl.style.display = 'block';
}

function showLoading() {
  document.getElementById('analysis-placeholder').style.display = 'none';
  document.getElementById('analysis-text').style.display = 'none';
  document.getElementById('analysis-loading').style.display = 'block';
}

function showError(msg) {
  document.getElementById('analysis-loading').style.display = 'none';
  document.getElementById('analysis-placeholder').style.display = 'none';
  const textEl = document.getElementById('analysis-text');
  textEl.textContent = '⚠ ' + msg;
  textEl.style.display = 'block';
  textEl.style.color = 'var(--red-accent)';
}
