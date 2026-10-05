/* =====================================================================
   IDRM RBAC Showcase — display controls (font face / size / theme / search)
   Inlined into idrm-rbac-showcase.html by _build-showcase.ps1.
   Preferences persist to localStorage; "System" theme tracks the OS.
   ===================================================================== */
(function () {
  'use strict';
  var DOC = document.documentElement;
  var LS = { hf: 'idrm-sc-hfont', bf: 'idrm-sc-bfont', sz: 'idrm-sc-size', th: 'idrm-sc-theme' };
  function get(k, d) { try { return localStorage.getItem(k) || d; } catch (e) { return d; } }
  function put(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function el(id) { return document.getElementById(id); }

  var FONT_NAMES = {
    "'Inter', sans-serif": "Inter",
    "'DM Sans', sans-serif": "DM Sans",
    "'Work Sans', sans-serif": "Work Sans",
    "'Source Sans 3', sans-serif": "Source Sans Pro",
    "'Lato', sans-serif": "Lato",
    "'Lexend', sans-serif": "Lexend",
    "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif": "System Default"
  };
  var SIZES = { xs: '13px', s: '14px', m: '15px', l: '16.5px', xl: '18px' };
  var SIZE_LABEL = { xs: 'XS', s: 'S', m: 'M', l: 'L', xl: 'XL' };

  function updatePreview() {
    var hf = el('sc-hfont'), bf = el('sc-bfont'), sz = el('sc-size'), p = el('sc-preview');
    if (!p || !hf || !bf || !sz) return;
    p.textContent = (FONT_NAMES[hf.value] || '?') + ' / ' + (FONT_NAMES[bf.value] || '?') + ' · ' + (SIZE_LABEL[sz.value] || 'M');
  }
  function applyFont(target, value) {
    DOC.style.setProperty(target === 'heading' ? '--font-heading' : '--font-body', value);
    put(target === 'heading' ? LS.hf : LS.bf, value);
    updatePreview();
  }
  function applySize(key) {
    DOC.style.fontSize = SIZES[key] || SIZES.m;
    put(LS.sz, key);
    updatePreview();
  }

  /* ---- theme: System resolves to light/dark via matchMedia ---- */
  var THEME_ICONS = {
    system: '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"></rect><path d="M2 17h20"></path><path d="M6 20h12"></path></svg>',
    light: '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="5"></circle><path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m5.08 5.08l4.24 4.24M1 12h6m6 0h6M4.22 19.78l4.24-4.24m5.08-5.08l4.24-4.24"></path></svg>',
    dark: '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>'
  };
  var THEME_LABEL = { system: 'System', light: 'Light', dark: 'Dark' };
  var CYCLE = ['system', 'light', 'dark'];
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  var themeMode = 'system';
  function effective(mode) { return mode === 'system' ? (mq && mq.matches ? 'dark' : 'light') : mode; }
  function applyTheme(mode) {
    themeMode = mode; put(LS.th, mode);
    DOC.setAttribute('data-theme', effective(mode));
    var btn = el('sc-theme');
    if (btn) {
      btn.setAttribute('data-mode', mode);
      el('sc-theme-icon').innerHTML = THEME_ICONS[mode];
      el('sc-theme-label').textContent = THEME_LABEL[mode];
    }
  }
  if (mq && mq.addEventListener) { mq.addEventListener('change', function () { if (themeMode === 'system') applyTheme('system'); }); }

  /* ---- search (Ctrl/Cmd + K) ---- */
  var idx = [], results = [], active = -1;
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function context(node) {
    var f = node.closest('.tpl-frame');
    if (f) { var n = f.querySelector('.tpl-name'); if (n && n !== node) return n.textContent.trim(); }
    var s = node.closest('#overview, #workflows, .doc-band');
    if (s) { var h = s.querySelector('h2'); if (h && h !== node) return h.textContent.trim(); }
    return (document.title || 'This page').replace(/^IDRM\s*[—-]\s*/, '');
  }
  function buildIndex() {
    document.querySelectorAll('.tpl-name, h1, h2, h3, h4, .scope-tag, .wf-card h4, .nav-col a, .api-note').forEach(function (node) {
      if (node.closest('.sc-bar') || node.closest('.sc-modal')) return;
      var text = (node.textContent || '').replace(/\s+/g, ' ').trim();
      if (text.length < 4 || text.length > 240) return;
      idx.push({ el: node, text: text, low: text.toLowerCase(), ctx: context(node) });
    });
  }
  function openModal() { var m = el('sc-modal'); if (!m) return; m.classList.add('open'); var i = el('sc-input'); i.value = ''; i.focus(); run(''); }
  function closeModal() { var m = el('sc-modal'); if (m) m.classList.remove('open'); }
  function run(q) {
    var box = el('sc-results'); if (!box) return; active = -1;
    if (!q.trim()) { box.innerHTML = '<div class="sc-none">Type to search roles, pages &amp; workflows…</div>'; results = []; return; }
    var ql = q.toLowerCase();
    results = idx.filter(function (r) { return r.low.indexOf(ql) !== -1; }).slice(0, 14);
    if (!results.length) { box.innerHTML = '<div class="sc-none">No matches for “' + esc(q) + '”</div>'; return; }
    box.innerHTML = '';
    results.forEach(function (m, i) {
      var pos = m.low.indexOf(ql), start = Math.max(0, pos - 30);
      var raw = (start > 0 ? '…' : '') + m.text.substring(start, start + 110) + (m.text.length > start + 110 ? '…' : '');
      var hl;
      try { hl = esc(raw).replace(new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<span class="hl">$1</span>'); }
      catch (e) { hl = esc(raw); }
      var row = document.createElement('div');
      row.className = 'sc-result';
      row.innerHTML = '<div class="sc-bc">' + esc(m.ctx) + '</div><div class="sc-excerpt">' + hl + '</div>';
      row.addEventListener('click', function () { choose(i); });
      box.appendChild(row);
    });
  }
  function move(d) {
    if (!results.length) return;
    active = (active + d + results.length) % results.length;
    var rows = document.querySelectorAll('.sc-result');
    rows.forEach(function (r) { r.classList.remove('active'); });
    if (rows[active]) { rows[active].classList.add('active'); rows[active].scrollIntoView({ block: 'nearest' }); }
  }
  function choose(i) {
    var m = results[i != null ? i : (active < 0 ? 0 : active)];
    if (!m) return;
    closeModal();
    m.el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    m.el.classList.add('sc-flash');
    setTimeout(function () { m.el.classList.remove('sc-flash'); }, 1600);
  }

  function init() {
    var hf = get(LS.hf, "'Inter', sans-serif"), bf = get(LS.bf, "'Inter', sans-serif"),
        sz = get(LS.sz, 'm'), th = get(LS.th, 'system');
    if (!SIZES[sz]) sz = 'm';
    if (el('sc-hfont')) el('sc-hfont').value = FONT_NAMES[hf] ? hf : "'Inter', sans-serif";
    if (el('sc-bfont')) el('sc-bfont').value = FONT_NAMES[bf] ? bf : "'Inter', sans-serif";
    if (el('sc-size')) el('sc-size').value = sz;
    DOC.style.setProperty('--font-heading', FONT_NAMES[hf] ? hf : "'Inter', sans-serif");
    DOC.style.setProperty('--font-body', FONT_NAMES[bf] ? bf : "'Inter', sans-serif");
    DOC.style.fontSize = SIZES[sz];
    applyTheme(CYCLE.indexOf(th) !== -1 ? th : 'system');
    updatePreview();

    if (el('sc-hfont')) el('sc-hfont').addEventListener('change', function () { applyFont('heading', this.value); });
    if (el('sc-bfont')) el('sc-bfont').addEventListener('change', function () { applyFont('body', this.value); });
    if (el('sc-size')) el('sc-size').addEventListener('change', function () { applySize(this.value); });
    if (el('sc-theme')) el('sc-theme').addEventListener('click', function () { applyTheme(CYCLE[(CYCLE.indexOf(themeMode) + 1) % CYCLE.length]); });

    var bar = document.querySelector('.sc-bar');
    function measure() { if (bar) DOC.style.setProperty('--sc-bar-h', bar.offsetHeight + 'px'); }
    measure(); window.addEventListener('resize', measure);

    buildIndex();
    if (el('sc-search-trigger')) el('sc-search-trigger').addEventListener('click', openModal);
    if (el('sc-input')) el('sc-input').addEventListener('input', function (e) { run(e.target.value); });
    var modal = el('sc-modal');
    if (modal) modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) { e.preventDefault(); openModal(); }
      else if (e.key === 'Escape') { closeModal(); }
      else if (modal && modal.classList.contains('open')) {
        if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
        else if (e.key === 'Enter') { e.preventDefault(); choose(); }
      }
    });
  }
  if (document.readyState !== 'loading') init();
  else document.addEventListener('DOMContentLoaded', init);
})();
