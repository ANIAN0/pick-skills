/* guide-layer.js v1.0
 * 固定文件 — 原样内联到每个原型 HTML，不得修改任何一行。
 * LLM 只允许在原型文件中修改 window.GUIDE_STEPS 数组。
 */
(function () {
  var COLORS = {
    new:      { border: '#3e8dff', bg: '#3e8dff', label: '新增' },
    modified: { border: '#ffb71d', bg: '#ffb71d', label: '修改' },
    removed:  { border: '#ff8b78', bg: '#ff8b78', label: '移除' }
  };

  var active = true;
  var cleanups = [];

  function init() {
    if (!window.GUIDE_STEPS || !window.GUIDE_STEPS.length) return;
    injectStyles();
    buildChrome();
    render();
  }

  function injectStyles() {
    if (document.getElementById('guide-layer-styles')) return;
    var s = document.createElement('style');
    s.id = 'guide-layer-styles';
    s.textContent = [
      '.guide-hl-new     { outline: 3px solid #3e8dff !important; outline-offset: 2px; border-radius: 4px; position: relative; z-index: 100; }',
      '.guide-hl-modified{ outline: 3px solid #ffb71d !important; outline-offset: 2px; border-radius: 4px; position: relative; z-index: 100; }',
      '.guide-hl-removed { outline: 3px dashed #ff8b78 !important; outline-offset: 2px; border-radius: 4px; position: relative; z-index: 100; }',
      '#guide-toggle-bar { position: fixed; top: 14px; right: 16px; z-index: 9999; display: flex; align-items: center; gap: 8px; pointer-events: all; }',
      '#guide-toggle-label { background: rgba(0,0,0,.6); color: #fff; font-size: 12px; padding: 4px 10px; border-radius: 12px; letter-spacing: .5px; }',
      '#guide-toggle-btn { background: #3e8dff; color: #fff; border: none; padding: 5px 14px; border-radius: 4px; font-size: 13px; cursor: pointer; box-shadow: 0 2px 6px rgba(62,141,255,.4); transition: background .2s; }',
      '#guide-badge-layer { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9997; }',
      '.guide-badge { position: absolute; width: 20px; height: 20px; border-radius: 50%; color: #fff; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; pointer-events: none; }',
      '#guide-panel { position: fixed; bottom: 24px; left: 240px; z-index: 9998; display: flex; flex-direction: column; gap: 8px; max-width: 360px; pointer-events: all; }',
      '.guide-card { background: #fff; border-radius: 8px; padding: 10px 14px; box-shadow: 0 4px 16px rgba(0,0,0,.14); display: flex; align-items: flex-start; gap: 10px; font-size: 13px; line-height: 1.6; cursor: pointer; transition: box-shadow .15s; }',
      '.guide-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.2); }',
      '.guide-card-label { padding: 1px 7px; border-radius: 3px; color: #fff; font-size: 11px; font-weight: 600; white-space: nowrap; flex-shrink: 0; margin-top: 2px; }',
      '.guide-card-title { font-weight: 600; color: rgba(0,0,0,.85); }',
      '.guide-card-desc { color: rgba(0,0,0,.55); margin-top: 2px; font-size: 12px; }'
    ].join('\n');
    document.head.appendChild(s);
  }

  function buildChrome() {
    if (document.getElementById('guide-toggle-bar')) return;

    var bar = document.createElement('div');
    bar.id = 'guide-toggle-bar';
    bar.innerHTML =
      '<div id="guide-toggle-label">需求改动预览</div>' +
      '<button id="guide-toggle-btn">关闭引导</button>';
    document.body.appendChild(bar);

    document.getElementById('guide-toggle-btn').addEventListener('click', toggleGuide);

    var badgeLayer = document.createElement('div');
    badgeLayer.id = 'guide-badge-layer';
    document.body.appendChild(badgeLayer);

    var panel = document.createElement('div');
    panel.id = 'guide-panel';
    document.body.appendChild(panel);
  }

  function clearHighlights() {
    cleanups.forEach(function (fn) { fn(); });
    cleanups = [];
    var bl = document.getElementById('guide-badge-layer');
    if (bl) bl.innerHTML = '';
    var gp = document.getElementById('guide-panel');
    if (gp) gp.innerHTML = '';
  }

  function render() {
    clearHighlights();
    if (!active) return;

    (window.GUIDE_STEPS || []).forEach(function (step) {
      var el = document.querySelector(step.selector);
      if (!el) return;
      var color = COLORS[step.type] || COLORS.new;

      // 高亮
      var cls = 'guide-hl-' + step.type;
      el.classList.add(cls);
      cleanups.push(function () { el.classList.remove(cls); });

      // 徽标（绝对定位，跟随滚动位置）
      var rect = el.getBoundingClientRect();
      var badge = document.createElement('div');
      badge.className = 'guide-badge';
      badge.style.cssText =
        'background:' + color.bg + ';' +
        'top:' + (window.scrollY + rect.top - 10) + 'px;' +
        'left:' + (window.scrollX + rect.right - 10) + 'px;';
      badge.textContent = step.id;
      document.getElementById('guide-badge-layer').appendChild(badge);

      // 说明卡片
      var card = document.createElement('div');
      card.className = 'guide-card';
      card.innerHTML =
        '<span class="guide-card-label" style="background:' + color.bg + '">' + color.label + '</span>' +
        '<div>' +
          '<div class="guide-card-title">' + step.id + '. ' + escHtml(step.title) + '</div>' +
          '<div class="guide-card-desc">' + escHtml(step.desc) + '</div>' +
        '</div>';
      card.addEventListener('click', (function (target) {
        return function () { target.scrollIntoView({ behavior: 'smooth', block: 'center' }); };
      }(el)));
      document.getElementById('guide-panel').appendChild(card);
    });
  }

  function toggleGuide() {
    active = !active;
    var btn = document.getElementById('guide-toggle-btn');
    btn.textContent = active ? '关闭引导' : '开启引导';
    btn.style.background = active ? '#3e8dff' : '#8c8c8c';
    render();
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function onResize() { if (active) render(); }

  window.addEventListener('DOMContentLoaded', init);
  window.addEventListener('resize', onResize);
  window.addEventListener('scroll', onResize, true);
}());
