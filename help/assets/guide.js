// Help guides: contents drawer on phones, and search across the whole guide (search.json).
(function () {
  var body = document.body, btn = document.querySelector('.topbar__menu');
  if (btn) btn.addEventListener('click', function () {
    var open = body.classList.toggle('toc-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  document.querySelectorAll('.toc a').forEach(function (a) { a.addEventListener('click', function () { body.classList.remove('toc-open'); }); });
  // open an FAQ answer when its link is followed
  function openHash() { var el = location.hash && document.getElementById(location.hash.slice(1)); if (el && el.tagName === 'DETAILS') el.open = true; }
  window.addEventListener('hashchange', openHash); openHash();

  var input = document.querySelector('.search input'), box = document.querySelector('.search-results');
  if (!input || !box) return;
  var data = null, key = input.getAttribute('data-guide');
  function load() {
    if (data) return Promise.resolve(data);
    return fetch('/help/' + key + '/search.json').then(function (r) { return r.json(); }).then(function (d) { data = d; return d; }).catch(function () { data = []; return data; });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function run() {
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) { box.hidden = true; return; }
    load().then(function (d) {
      var words = q.split(/\s+/);
      var hits = d.map(function (e) {
        var s = (e.s + ' ' + e.p).toLowerCase(), t = (e.t || '').toLowerCase(), score = 0;
        words.forEach(function (w) { if (s.indexOf(w) > -1) score += 5; if (t.indexOf(w) > -1) score += 1; });
        if (words.some(function (w) { return s.indexOf(w) < 0 && t.indexOf(w) < 0; })) score = 0;
        return { e: e, score: score };
      }).filter(function (h) { return h.score > 0; }).sort(function (a, b) { return b.score - a.score; }).slice(0, 12);
      box.innerHTML = hits.length ? hits.map(function (h) {
        return '<a href="' + esc(h.e.u) + '"><b>' + esc(h.e.s) + '</b><small>' + esc(h.e.p) + '</small></a>';
      }).join('') : '<p class="none">Nothing found. Try another word, or email admintotality@gmail.com.</p>';
      box.hidden = false;
    });
  }
  input.addEventListener('input', run);
  input.addEventListener('focus', function () { load(); if (input.value.trim().length > 1) run(); });
  document.addEventListener('click', function (e) { if (!box.contains(e.target) && e.target !== input) box.hidden = true; });
  input.addEventListener('keydown', function (e) { if (e.key === 'Escape') { box.hidden = true; input.blur(); } if (e.key === 'Enter') { var f = box.querySelector('a'); if (f) location.href = f.href; } });
})();
