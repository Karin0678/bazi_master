/**
 * 四柱排盘渲染模块
 */

const WUXING_COLORS = {
  '木': '#4a8a2a', '火': '#c84a1a', '土': '#9a7a2a', '金': '#9a9a9a', '水': '#1a5aaa'
};

const WUXING_NAMES = ['木', '火', '土', '金', '水'];

function renderPillars(data) {
  const pillars = data.bazi.pillars;
  const cols = ['year', 'month', 'day', 'hour'];
  const labels = ['年柱', '月柱', '日柱', '时柱'];

  const tbody = document.getElementById('pillar-tbody');

  // 天干行
  let tgRow = '<tr>';
  cols.forEach(col => {
    const p = pillars[col];
    const isDay = col === 'day';
    const color = WUXING_COLORS[getTgWuxing(p.tg)] || 'var(--gold)';
    tgRow += `<td>
      <div class="pillar-gz" style="color:${color}">${p.tg}</div>
      ${isDay ? '<div class="pillar-shishen">日主</div>' : `<div class="pillar-shishen">${p.tg_shishen}</div>`}
    </td>`;
  });
  tgRow += '</tr>';

  // 地支行
  let dzRow = '<tr>';
  cols.forEach(col => {
    const p = pillars[col];
    const color = WUXING_COLORS[getDzWuxing(p.dz)] || 'var(--gold)';
    dzRow += `<td>
      <div class="pillar-gz" style="color:${color}">${p.dz}</div>
      <div class="pillar-nayin">${p.nayin}</div>
    </td>`;
  });
  dzRow += '</tr>';

  tbody.innerHTML = tgRow + dzRow;

  document.getElementById('pillar-card').style.display = 'block';
}

function renderWuxing(data) {
  const wuxing = data.wuxing;
  const scores = wuxing.scores;
  const maxScore = Math.max(...Object.values(scores));

  // 基本信息
  const infoEl = document.getElementById('wuxing-info');
  const strength = wuxing.strength;
  const strengthLevel = strength === '身强' ? '强' : strength === '身弱' ? '弱' : '中';
  const dm = data.bazi.day_master;

  infoEl.innerHTML = `
    <div class="info-row">
      <span class="info-key">日主</span>
      <span class="info-val" style="color:${WUXING_COLORS[dm.wuxing]}">${dm.tg}（${dm.yinyang}${dm.wuxing}）</span>
    </div>
    <div class="info-row">
      <span class="info-key">月令</span>
      <span class="info-val">${data.bazi.month_zhi}（${wuxing.month_state}）</span>
    </div>
    <div class="info-row">
      <span class="info-key">身强弱</span>
      <span class="strength-badge strength-${strengthLevel}">${strength}</span>
    </div>
  `;

  // 五行条形图
  const barsEl = document.getElementById('wuxing-bars');
  barsEl.innerHTML = WUXING_NAMES.map(wx => {
    const score = scores[wx] || 0;
    const width = maxScore > 0 ? (score / maxScore * 100).toFixed(1) : 0;
    return `
      <div class="wuxing-row">
        <span class="wuxing-label label-${wx}">${wx}</span>
        <div class="wuxing-bar-wrap">
          <div class="wuxing-bar wuxing-${wx}" style="width:${width}%"></div>
        </div>
        <span class="wuxing-score">${score.toFixed(1)}</span>
      </div>
    `;
  }).join('');

  // 喜用神
  const xiyongEl = document.getElementById('xiyong-info');
  const xiyong = wuxing.xiyong;
  xiyongEl.innerHTML = `
    <div style="font-size:11px;color:var(--text-muted);letter-spacing:1px;margin-bottom:8px">喜用 / 忌神</div>
    <div class="xiyong-tags">
      ${xiyong.xiyong.map(wx => `<span class="tag tag-xiyong">喜 ${wx}</span>`).join('')}
      ${xiyong.jishen.map(wx => `<span class="tag tag-jishen">忌 ${wx}</span>`).join('')}
    </div>
  `;

  document.getElementById('wuxing-card').style.display = 'block';
}

// 天干五行映射
const TG_WUXING = {
  '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
  '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'
};

const DZ_WUXING = {
  '子':'水','丑':'土','寅':'木','卯':'木','辰':'土','巳':'火',
  '午':'火','未':'土','申':'金','酉':'金','戌':'土','亥':'水'
};

function getTgWuxing(tg) { return TG_WUXING[tg] || ''; }
function getDzWuxing(dz) { return DZ_WUXING[dz] || ''; }
