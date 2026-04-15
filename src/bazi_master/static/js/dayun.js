/**
 * 大运流年时间轴渲染
 */

const WUXING_COLORS_DY = {
  '木': '#4a8a2a', '火': '#c84a1a', '土': '#9a7a2a', '金': '#9a9a9a', '水': '#1a5aaa'
};

const TG_WUXING_DY = {
  '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
  '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'
};

function renderDayun(data) {
  const dayun = data.dayun;
  const xiyong = data.wuxing.xiyong.xiyong;

  // 方向信息
  const dirEl = document.getElementById('dayun-direction');
  dirEl.textContent = `${dayun.direction} · 起运${dayun.start_age}`;

  // 大运时间轴
  const timelineEl = document.getElementById('dayun-timeline');
  const currentYear = new Date().getFullYear();
  const birthYear = data.bazi.birth.year;
  const currentAge = currentYear - birthYear;

  const itemsHtml = dayun.dayuns.map(d => {
    const isCurrent = d.age_start <= currentAge && currentAge <= d.age_end;
    const tgWx = TG_WUXING_DY[d.tg] || '';
    const isFavorable = xiyong.includes(tgWx);

    return `
      <div class="dayun-item ${isCurrent ? 'current' : ''}" title="${d.gz}大运 ${d.year_start}-${d.year_end}">
        <div class="dayun-gz" style="color:${WUXING_COLORS_DY[tgWx] || 'var(--gold-light)'}">${d.gz}</div>
        <div class="dayun-age">${d.age_start}-${d.age_end}岁</div>
        <div class="dayun-year">${d.year_start}-${d.year_end}</div>
        <div class="dayun-quality ${isFavorable ? 'quality-good' : 'quality-bad'}">${isFavorable ? '▲ 顺' : '▽ 缓'}</div>
        ${isCurrent ? '<div style="font-size:9px;color:var(--gold);margin-top:2px">当前</div>' : ''}
      </div>
    `;
  }).join('');

  timelineEl.innerHTML = `<div class="dayun-items">${itemsHtml}</div>`;

  // 流年
  const liunianEl = document.getElementById('liunian-grid');
  liunianEl.innerHTML = dayun.liunian.map(ly => {
    const tgWx = TG_WUXING_DY[ly.tg] || '';
    return `
      <div class="liunian-item ${ly.is_current ? 'current' : ''}">
        <div class="liunian-year">${ly.year}</div>
        <div class="liunian-gz" style="color:${WUXING_COLORS_DY[tgWx] || 'var(--gold-light)'}">${ly.gz}</div>
        <div class="liunian-age">${ly.age}岁</div>
      </div>
    `;
  }).join('');

  document.getElementById('dayun-card').style.display = 'block';
}
