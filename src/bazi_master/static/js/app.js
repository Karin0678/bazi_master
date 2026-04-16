/**
 * 主应用逻辑
 * Tab 切换、表单提交、模式切换
 */

let currentData = null;
let currentSection = 'overview';
let isClaudeMode = false;
let streamController = null; // 用于取消进行中的 SSE 流
let analysisCache = {};       // 分析结果缓存，key 为 section，值为原始文本

// ── 模式切换 ─────────────────────────────────────────────────────────────────

document.getElementById('mode-toggle-input').addEventListener('change', function() {
  isClaudeMode = this.checked;
  updateModeLabel();
  if (currentData) {
    // 模式切换后缓存失效（规则引擎与 Claude 内容不同）
    analysisCache = {};
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
    if (currentData) {
      loadAnalysis(currentSection);
    }
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
      // 新起卦时清空缓存
      analysisCache = {};

      renderPillars(currentData);
      renderWuxing(currentData);
      renderDayun(currentData);

      if (isClaudeMode) {
        initChat(currentData);
      } else {
        document.getElementById('chat-card').style.display = 'none';
      }

      await loadAnalysis(currentSection);
    } else {
      showError('计算失败：' + (result.detail || '未知错误'));
    }
  } catch (err) {
    showError('网络错误：' + err.message);
  }
}

// ── 分析加载（带缓存）────────────────────────────────────────────────────────

async function loadAnalysis(section) {
  if (!currentData) return;

  // 命中缓存：直接展示，不发请求
  if (analysisCache[section] !== undefined) {
    showCachedAnalysis(analysisCache[section]);
    return;
  }

  showLoading();

  if (isClaudeMode) {
    initChat(currentData);
    await loadClaudeAnalysis(section);
  } else {
    await loadRulesAnalysis(section);
  }
}

function showCachedAnalysis(text) {
  document.getElementById('analysis-placeholder').style.display = 'none';
  document.getElementById('analysis-loading').style.display = 'none';
  const textEl = document.getElementById('analysis-text');
  if (isClaudeMode) {
    textEl.innerHTML = marked.parse(text);
  } else {
    textEl.textContent = text;
  }
  textEl.style.display = 'block';
}

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
        section: section
      })
    });

    const result = await response.json();
    if (result.success) {
      analysisCache[section] = result.text; // 写入缓存
      showAnalysisText(result.text);
    } else {
      showError('分析失败');
    }
  } catch (err) {
    showError('错误：' + err.message);
  }
}

async function loadClaudeAnalysis(section) {
  // 取消上一个正在进行的流式请求
  if (streamController) {
    streamController.abort();
  }
  streamController = new AbortController();
  const signal = streamController.signal;

  showAnalysisText('', true); // 先清空，准备流式填充
  const textEl = document.getElementById('analysis-text');
  textEl.classList.add('typing-cursor');

  try {
    const response = await fetch('/api/analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        bazi_data: currentData.bazi,
        wuxing_analysis: currentData.wuxing,
        dayun_data: currentData.dayun,
        mode: 'claude',
        section: section
      }),
      signal
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            textEl.classList.remove('typing-cursor');
            analysisCache[section] = fullText; // 流结束后写入缓存
            break;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.text) {
              fullText += parsed.text;
              textEl.innerHTML = marked.parse(fullText);
            }
            if (parsed.error) {
              showError(parsed.error);
            }
          } catch (e) {}
        }
      }
    }
  } catch (err) {
    textEl.classList.remove('typing-cursor');
    // AbortError 是主动取消，不属于错误，静默处理
    if (err.name !== 'AbortError') {
      showError('流式传输错误：' + err.message);
    }
  }
}

// ── UI 工具函数 ───────────────────────────────────────────────────────────────

function showLoading() {
  document.getElementById('analysis-placeholder').style.display = 'none';
  document.getElementById('analysis-text').style.display = 'none';
  document.getElementById('analysis-loading').style.display = 'block';
}

function showAnalysisText(text, streaming = false) {
  document.getElementById('analysis-placeholder').style.display = 'none';
  document.getElementById('analysis-loading').style.display = 'none';
  const textEl = document.getElementById('analysis-text');
  textEl.textContent = text;
  textEl.style.display = 'block';
  if (!streaming) {
    textEl.classList.add('fade-in');
  }
}

function showError(msg) {
  document.getElementById('analysis-loading').style.display = 'none';
  document.getElementById('analysis-placeholder').style.display = 'none';
  const textEl = document.getElementById('analysis-text');
  textEl.textContent = '⚠ ' + msg;
  textEl.style.display = 'block';
  textEl.style.color = 'var(--red-accent)';
}
