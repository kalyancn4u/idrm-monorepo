/* =====================================================================
   IDRM Templates — shared interactions (vanilla JS, no dependencies)
   ---------------------------------------------------------------------
   Mockup-only behaviors: mobile nav, tabs, toasts, dismissible alerts,
   copy-code, star rating, password show/strength, "use my location"
   stub, filter chips, and showcase table-of-contents scroll-spy.

   Real API wiring is documented in each page's .api-note / comments.
   Uses event delegation so it works identically in the standalone
   showcase (everything inlined) and the individual pages/ files.
   ===================================================================== */
(function () {
  'use strict';

  /* ---- Toast host + helper (also referenced by inline onclick demos) ---- */
  function ensureToastHost() {
    let host = document.getElementById('toast-host');
    if (!host) {
      host = document.createElement('div');
      host.id = 'toast-host';
      document.body.appendChild(host);
    }
    return host;
  }
  function showToast(message, type) {
    type = type || 'info';
    const host = ensureToastHost();
    const t = document.createElement('div');
    t.className = 'toast ' + type;
    t.setAttribute('role', type === 'error' ? 'alert' : 'status');
    t.textContent = message;
    host.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => {
      t.classList.remove('show');
      setTimeout(() => t.remove(), 300);
    }, 3600);
  }
  window.idrmToast = showToast; // expose for inline demo buttons

  /* ---- Copy code blocks ---- */
  function copyCode(btn) {
    const block = btn.closest('.code-block');
    const code = block && block.querySelector('pre code');
    if (!code) return;
    navigator.clipboard.writeText(code.innerText).then(
      () => { btn.innerText = '✓ Copied!'; setTimeout(() => (btn.innerText = '📋 Copy'), 1800); },
      () => { btn.innerText = '❌ Failed'; setTimeout(() => (btn.innerText = '📋 Copy'), 1800); }
    );
  }
  window.idrmCopyCode = copyCode;

  /* ---- Global click delegation ---- */
  document.addEventListener('click', function (e) {
    const t = e.target;

    // Mobile nav toggle (scope to this navbar first so repeated IDs in the
    // concatenated showcase don't toggle the wrong menu)
    const toggle = t.closest('[data-nav-toggle]');
    if (toggle) {
      const navbar = toggle.closest('.navbar');
      const nav = (navbar && navbar.querySelector('.nav-links')) ||
                  document.getElementById(toggle.getAttribute('data-nav-toggle')) ||
                  document.querySelector('.nav-links');
      if (nav) {
        const open = nav.classList.toggle('open');
        toggle.setAttribute('aria-expanded', String(open));
      }
      return;
    }

    // Copy code
    if (t.closest('.copy-btn')) { copyCode(t.closest('.copy-btn')); return; }

    // Dismiss alert
    if (t.closest('.alert-close')) {
      const a = t.closest('.alert'); if (a) a.style.display = 'none'; return;
    }

    // Tabs (scoped to nearest [data-tabs])
    const tabBtn = t.closest('.tab');
    if (tabBtn && tabBtn.closest('[data-tabs]')) {
      const scope = tabBtn.closest('[data-tabs]');
      scope.querySelectorAll('.tab').forEach((b) => {
        b.classList.remove('active'); b.setAttribute('aria-selected', 'false');
      });
      tabBtn.classList.add('active'); tabBtn.setAttribute('aria-selected', 'true');
      const target = tabBtn.getAttribute('data-tab');
      if (target) {
        scope.querySelectorAll('[data-tab-panel]').forEach((p) => {
          p.classList.toggle('hidden', p.getAttribute('data-tab-panel') !== target);
        });
      }
      return;
    }

    // Filter chips (multi-select within a [data-chips] group)
    const chip = t.closest('.chip');
    if (chip && chip.closest('[data-chips]')) { chip.classList.toggle('active'); return; }

    // Star rating
    const star = t.closest('.rating .star');
    if (star) {
      const group = star.parentElement;
      const value = Number(star.getAttribute('data-value'));
      group.querySelectorAll('.star').forEach((s) => {
        s.classList.toggle('on', Number(s.getAttribute('data-value')) <= value);
      });
      const out = group.getAttribute('data-output') && document.getElementById(group.getAttribute('data-output'));
      if (out) out.textContent = value + ' / 5';
      group.setAttribute('data-selected', String(value));
      return;
    }

    // Password visibility toggle (scope to this input-group first)
    const pw = t.closest('[data-toggle-password]');
    if (pw) {
      const group = pw.closest('.input-group');
      const input = (group && group.querySelector('input')) ||
                    document.getElementById(pw.getAttribute('data-toggle-password'));
      if (input) { const show = input.type === 'password'; input.type = show ? 'text' : 'password'; pw.textContent = show ? '🙈' : '👁'; }
      return;
    }

    // "Use my location" stub (GPS)
    const geo = t.closest('[data-use-location]');
    if (geo) {
      e.preventDefault();
      const targetId = geo.getAttribute('data-use-location');
      if (!navigator.geolocation) { showToast('Geolocation not supported — pin it on the map.', 'warning'); return; }
      geo.classList.add('loading'); geo.disabled = true;
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          geo.classList.remove('loading'); geo.disabled = false;
          const out = targetId && document.getElementById(targetId);
          if (out) out.value = pos.coords.latitude.toFixed(4) + ', ' + pos.coords.longitude.toFixed(4);
          showToast('Location captured. (GeoJSON sends [lng, lat] to the API.)', 'success');
        },
        () => { geo.classList.remove('loading'); geo.disabled = false; showToast('Could not get location — pin it on the map.', 'warning'); },
        { enableHighAccuracy: true, timeout: 5000 }
      );
      return;
    }

    // Mark-notification-read demo
    const readBtn = t.closest('[data-mark-read]');
    if (readBtn) { const row = readBtn.closest('.list-row'); if (row) row.classList.remove('unread'); showToast('Marked as read', 'success'); return; }
  });

  /* ---- Demo form submit guard + simple validation ---- */
  const validate = {
    email: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v),
    password: (v) => /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(v),
    phone: (v) => /^\+?[1-9]\d{9,14}$/.test(v),
  };
  window.idrmValidate = validate;

  document.addEventListener('submit', function (e) {
    const form = e.target;
    if (!form.matches('[data-demo-form]')) return;
    e.preventDefault(); // mockup: never actually navigate
    let ok = true;
    form.querySelectorAll('[data-validate]').forEach((input) => {
      const kind = input.getAttribute('data-validate');
      const errEl = input.parentElement.querySelector('.form-error');
      const valid = !input.value || (validate[kind] ? validate[kind](input.value) : true);
      input.classList.toggle('input-invalid', !valid && !!input.value);
      if (errEl) errEl.style.display = (!valid && input.value) ? 'block' : 'none';
      if (!valid && input.value) ok = false;
      if (input.hasAttribute('required') && !input.value) { ok = false; input.classList.add('input-invalid'); }
    });
    showToast(ok ? 'Looks good! (Mockup — no request sent.)' : 'Please fix the highlighted fields.', ok ? 'success' : 'error');
  });

  /* ---- Password strength meter ---- */
  document.addEventListener('input', function (e) {
    const input = e.target;
    if (!input.matches('[data-strength]')) return;
    const bar = document.getElementById(input.getAttribute('data-strength'));
    if (!bar) return;
    const v = input.value;
    let score = 0;
    if (v.length >= 8) score++;
    if (/[A-Z]/.test(v)) score++;
    if (/[a-z]/.test(v)) score++;
    if (/\d/.test(v)) score++;
    if (/[^A-Za-z0-9]/.test(v)) score++;
    const pct = (score / 5) * 100;
    const colors = ['#ef4444', '#ef4444', '#f59e0b', '#f59e0b', '#10b981', '#047857'];
    const labels = ['Too short', 'Weak', 'Fair', 'Good', 'Strong', 'Excellent'];
    bar.style.width = pct + '%';
    bar.style.background = colors[score];
    const lbl = document.getElementById(bar.getAttribute('data-label'));
    if (lbl) lbl.textContent = v ? labels[score] : '';
  });

  /* ---- Showcase: scroll-spy for the table of contents (if present) ---- */
  function initScrollSpy() {
    const toc = document.querySelector('[data-toc]');
    if (!toc) return;
    const links = Array.prototype.slice.call(toc.querySelectorAll('a[href^="#"]'));
    const map = {};
    links.forEach((l) => { const id = l.getAttribute('href').slice(1); const sec = document.getElementById(id); if (sec) map[id] = l; });
    const sections = Object.keys(map).map((id) => document.getElementById(id));
    if (!('IntersectionObserver' in window) || !sections.length) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          links.forEach((l) => l.classList.remove('active'));
          if (map[en.target.id]) map[en.target.id].classList.add('active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach((s) => obs.observe(s));
  }

  /* ---- Live maps (Leaflet) — graceful: stays a placeholder if the CDN/tiles are unavailable ---- */
  function initOneMap(el) {
    if (!window.L || el._mapInit) return;
    el._mapInit = true;
    var lat = parseFloat(el.getAttribute('data-lat'));
    var lng = parseFloat(el.getAttribute('data-lng'));
    var zoom = parseInt(el.getAttribute('data-zoom') || '12', 10);
    el.innerHTML = ''; // remove the static placeholder fallback before mounting
    var map = L.map(el, { scrollWheelZoom: false })
      .setView([isNaN(lat) ? 17.385 : lat, isNaN(lng) ? 78.4867 : lng], zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      { attribution: '&copy; OpenStreetMap contributors', maxZoom: 19 }).addTo(map);
    var COLORS = { CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#f59e0b', LOW: '#22c55e' };
    var markers = [];
    try { markers = JSON.parse(el.getAttribute('data-markers') || '[]'); } catch (e) {}
    // popup detail link resolves correctly in both standalone pages and the concatenated showcase
    var detailHref = document.getElementById('tpl-07-service-detail') ? '#tpl-07-service-detail' : '07-service-detail.html';
    var pts = [];
    markers.forEach(function (m) {
      var color = COLORS[m.priority] || '#64748b';
      var icon = L.divIcon({ className: '', iconSize: [18, 18],
        html: '<div style="width:16px;height:16px;border-radius:50%;background:' + color +
              ';border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.45)"></div>' });
      var mk = L.marker([m.lat, m.lng], { icon: icon, title: m.title || '' }).addTo(map);
      mk.bindPopup('<strong>' + (m.title || 'Request') + '</strong>' +
        (m.priority ? '<br><span style="color:' + color + '">&#9679; ' + m.priority + '</span>' : '') +
        (m.link === false ? '' : '<br><a href="' + detailHref + '">View detail &rarr;</a>'));
      pts.push([m.lat, m.lng]);
    });
    if (pts.length > 1) map.fitBounds(pts, { padding: [30, 30], maxZoom: 14 });
    setTimeout(function () { map.invalidateSize(); }, 150);
  }
  function lazy(els, fn) {
    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (entries, o) {
        entries.forEach(function (en) { if (en.isIntersecting) { fn(en.target); o.unobserve(en.target); } });
      }, { rootMargin: '150px' });
      els.forEach(function (el) { obs.observe(el); });
    } else { els.forEach(fn); }
  }
  function initMaps() {
    var els = document.querySelectorAll('[data-map]');
    if (els.length && window.L) lazy(els, initOneMap);
  }

  /* ---- Charts (Chart.js) — graceful: keeps the CSS-bar fallback if unavailable ---- */
  function initOneChart(canvas) {
    if (!window.Chart || canvas._chartInit) return;
    canvas._chartInit = true;
    var cfg;
    try { cfg = JSON.parse(canvas.getAttribute('data-chart') || '{}'); } catch (e) { return; }
    var box = canvas.closest('.chart-box');
    var fb = box && box.querySelector('.chart-fallback');
    if (fb) fb.style.display = 'none';
    canvas.style.display = 'block';
    new Chart(canvas.getContext('2d'), cfg);
  }
  function initCharts() {
    // Init directly (not via IntersectionObserver): the canvases start display:none,
    // and IO never fires for zero-box elements. There are only a couple of charts.
    var els = document.querySelectorAll('canvas[data-chart]');
    if (els.length && window.Chart) els.forEach(initOneChart);
  }

  function initAll() { initScrollSpy(); initMaps(); initCharts(); }
  if (document.readyState !== 'loading') initAll();
  else document.addEventListener('DOMContentLoaded', initAll);
})();
