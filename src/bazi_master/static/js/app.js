/**
 * 主应用逻辑
 * Tab 切换、表单提交、模式切换
 */

let currentData = null;
let currentSection = 'overview';
let isClaudeMode = false;
let streamController = null; // 用于取消进行中的 SSE 流

// 模式切换
document.getElementById('mode-toggle-input').addEventListener('change', function() {
  isClaudeMode = this.checked;
  updateModeLabel();
  // 如果已有数据，刷新当前分析
  if (currentData) {
    loadAnalysis(currentSection);
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

// Tab 切换
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

// 表单提交
document.getElementById('birth-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  await calculateBazi();
});

async function calculateBazi() {
  const year = parseInt(document.getElementById('birth-year').value);
  const month = parseInt(document.getElementById('birth-month').value);
  const day = parseInt(document.getElementById('birth-day').value);
  const hour = parseInt(document.getElementById('birth-hour').value);
  const minute = parseInt(document.getElementById('birth-minute').value) || 0;
  const gender = document.getElementById('birth-gender').value;

  // 显示加载状态
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

      // 渲染四柱
      renderPillars(currentData);
      // 渲染五行
      renderWuxing(currentData);
      // 渲染大运
      renderDayun(currentData);
      // 初始化对话（只在 Claude 模式下显示）
      if (isClaudeMode) {
        initChat(currentData);
      } else {
        document.getElementById('chat-card').style.display = 'none';
      }

      // 加载分析文本
      await loadAnalysis(currentSection);
    } else {
      showError('计算失败：' + (result.detail || '未知错误'));
    }
  } catch (err) {
    showError('网络错误：' + err.message);
  }
}

async function loadAnalysis(section) {
  if (!currentData) return;

  showLoading();

  if (isClaudeMode) {
    // Claude 流式模式
    initChat(currentData);
    await loadClaudeAnalysis(section);
  } else {
    // 规则引擎模式
    await loadRulesAnalysis(section);
  }
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

  showAnalysisText('', true); // 流式模式，先清空
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
            break;
          }
          try {
            const parsed = JSON.parse(data);
            if (parsed.text) {
              fullText += parsed.text;
              textEl.textContent = fullText;
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
  textEl.classList.add('fade-in');
}

function showError(msg) {
  document.getElementById('analysis-loading').style.display = 'none';
  document.getElementById('analysis-placeholder').style.display = 'none';
  const textEl = document.getElementById('analysis-text');
  textEl.textContent = '⚠ ' + msg;
  textEl.style.display = 'block';
  textEl.style.color = 'var(--red-accent)';
}

// 监听 Claude 模式下显示对话框
document.getElementById('mode-toggle-input').addEventListener('change', function() {
  if (currentData) {
    if (isClaudeMode) {
      document.getElementById('chat-card').style.display = 'block';
    } else {
      document.getElementById('chat-card').style.display = 'none';
    }
  }
});
