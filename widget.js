/*! Totality exercise library widget. https://totality360.com.au/api#websites
 * <div id="totality-exercises"></div>
 * <script src="https://totality360.com.au/widget.js" data-site="ws_..." async></script>
 * Options on the script tag:
 *   data-view    "library" (default) | "exercise" (with data-id) | "list" (with data-ids)
 *   data-id      one exercise id, for example "goblet-squat"
 *   data-ids     your own list, comma separated, in your order
 *   data-accent  brand colour, for example "#1F6F5C"
 *   data-theme   "light" (default) | "dark"
 *   data-filter  only show these muscle groups, for example "Glutes,Quads,Hamstrings"
 *   data-target  CSS selector of the element to fill (default #totality-exercises, or right after the script)
 */
(function () {
  'use strict';
  var API = 'https://spqazfyxxhzizbtmxklr.supabase.co/functions/v1/exercise-api/v1/widget';
  var POSTERS = 'https://totality360.com.au/widget/posters/';
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function title(t) { return String(t).split('-').map(function (w) { return w.charAt(0).toUpperCase() + w.slice(1); }).join(' '); }
  function cap(t) { return t ? t.charAt(0).toUpperCase() + t.slice(1) : ''; }
  // Inside a website builder's frame (Wix), tell the API which website the frame is on.
  var TOP = '';
  try { if (window.top !== window.self) { TOP = (location.ancestorOrigins && location.ancestorOrigins.length ? location.ancestorOrigins[location.ancestorOrigins.length - 1] : document.referrer) || ''; TOP = TOP ? new URL(TOP).hostname : ''; } } catch (e) { TOP = ''; }
  function get(path, o) {
    var sep = path.indexOf('?') >= 0 ? '&' : '?';
    return fetch(API + path + sep + 'site=' + encodeURIComponent(o.site) + (TOP ? '&h=' + encodeURIComponent(TOP) : '')).then(function (r) {
      return r.json().then(function (j) { if (!r.ok) throw j; return j; });
    });
  }

  var CSS = [
    ':host{all:initial;display:block;font-family:inherit;font-size:15px;line-height:1.5;color:var(--tx);--tx:#1d1a20;--mu:#6b6570;--bg:#fff;--sf:#f6f5f7;--ln:#e7e4ea;--chip:#f1eff3}',
    ':host(.dark){--tx:#efedf1;--mu:#a8a1ae;--bg:#141215;--sf:#1d1a20;--ln:#2e2a32;--chip:#28242c}',
    '*{box-sizing:border-box}button,input,select{font:inherit;color:inherit}',
    '.w{background:var(--bg);border:1px solid var(--ln);border-radius:16px;padding:14px;color:var(--tx);font-family:inherit}',
    '.tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:12px}',
    '.q{flex:1 1 220px;min-width:0;border:1px solid var(--ln);background:var(--bg);border-radius:10px;padding:9px 12px}',
    '.chips{display:flex;gap:6px;flex-wrap:wrap}.chip{border:1px solid var(--ln);background:var(--bg);border-radius:99px;padding:5px 12px;font-size:13px;cursor:pointer}',
    '.chip.on{background:var(--acc);border-color:var(--acc);color:#fff}',
    'select{border:1px solid var(--ln);background:var(--bg);border-radius:10px;padding:8px 10px;font-size:13px}',
    '.body{display:grid;grid-template-columns:minmax(0,1fr);gap:14px}.body.open{grid-template-columns:minmax(0,1fr) minmax(0,360px)}',
    '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;align-content:start}',
    '.card{border:1px solid var(--ln);border-radius:12px;overflow:hidden;background:var(--bg);cursor:pointer;text-align:left;padding:0;display:block;width:100%}',
    '.card:hover{border-color:var(--acc)}.card.on{border-color:var(--acc);box-shadow:0 0 0 2px var(--acc)}',
    '.m{position:relative;aspect-ratio:1;background:#eef0f2;overflow:hidden}.m img,.m video{position:relative;z-index:1;width:100%;height:100%;object-fit:cover;display:block}',
    '.ph{position:absolute;inset:0;display:grid;place-items:center;font-size:12px;color:#8f8996;background:repeating-linear-gradient(135deg,#f3f2f5,#f3f2f5 10px,#ecebef 10px,#ecebef 20px)}',
    ':host(.dark) .ph{background:repeating-linear-gradient(135deg,#1d1a20,#1d1a20 10px,#222026 10px,#222026 20px);color:#7d7783}',
    '.bd{position:absolute;z-index:2;left:8px;bottom:8px;background:rgba(18,13,23,.78);color:#fff;font-size:10.5px;padding:2px 7px;border-radius:6px}',
    '.cb{padding:8px 10px 10px}.cb b{display:block;font-size:13.5px;line-height:1.25}',
    '.tags{display:flex;gap:4px;flex-wrap:wrap;margin-top:6px}.tags span{font-size:10.5px;background:var(--chip);border-radius:99px;padding:2px 7px;color:var(--mu)}',
    '.tags .beginner{background:#e2f3ea;color:#1e6b45}.tags .intermediate{background:#fdf0dc;color:#8a5410}.tags .advanced{background:#fbe3e1;color:#9a2b22}',
    '.det{border:1px solid var(--ln);border-radius:14px;overflow:hidden;align-self:start;background:var(--bg)}',
    '.det .m{aspect-ratio:1.1}.dx{padding:14px 15px 16px}.dx h3{margin:0 0 4px;font-size:19px;line-height:1.25}.dx p{margin:0 0 10px;color:var(--mu);font-size:13.5px}',
    '.dx h4{margin:13px 0 4px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--acc)}',
    '.dx ol,.dx ul{margin:0;padding-left:18px;font-size:13.5px}.dx li{margin:2px 0}',
    '.sw{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}.sw button{flex:1 1 100px;border:1px solid var(--ln);background:var(--bg);border-radius:9px;padding:6px 8px;font-size:12.5px;text-align:left;cursor:pointer}.sw small{display:block;color:var(--mu);font-size:10.5px}',
    '.x{float:right;border:0;background:var(--chip);border-radius:99px;width:28px;height:28px;cursor:pointer;font-size:16px;line-height:1}',
    '.more{margin:12px auto 0;display:block;border:1px solid var(--ln);background:var(--bg);border-radius:10px;padding:8px 16px;cursor:pointer}',
    '.note{font-size:12px;color:var(--mu);margin-top:6px}.empty{padding:24px;text-align:center;color:var(--mu)}',
    '.cr{text-align:right;font-size:11px;color:var(--mu);margin-top:10px}.cr a{color:inherit}',
    '@media (max-width:720px){.body.open{grid-template-columns:minmax(0,1fr)}.det{position:fixed;inset:auto 0 0 0;max-height:88vh;overflow:auto;z-index:2147483000;border-radius:16px 16px 0 0;box-shadow:0 -10px 40px rgba(0,0,0,.25)}}',
  ].join('\n');

  function mount(el, o) {
    var root = el.attachShadow ? el.attachShadow({ mode: 'open' }) : el;
    var host = el;
    if (o.dark) host.classList.add('dark');
    root.innerHTML = '<style>' + CSS + ':host{--acc:' + o.accent + '}</style><div class="w"><div class="empty">Loading exercises...</div></div>';
    var w = root.querySelector('.w');
    var st = { q: '', muscle: '', equipment: '', offset: 0, items: [], open: '', videos: true, total: 0 };

    // Own lists, muscle filters and the dark theme come with Pro and Multi-site.
    function plan(init) {
      if (init.extras) return;
      o.filter = []; if (o.view === 'list') o.view = 'library';
      if (o.dark) { o.dark = false; host.classList.remove('dark'); }
    }
    function credit() { return '<div class="cr">Exercise content by <a href="https://totality360.com.au/api" target="_blank" rel="noopener">Totality</a></div>'; }
    function fail(e) {
      var msg = e && e.error && e.error.code === 'not_allowed' ? 'This exercise library is not set up for this website yet.' : 'The exercise library could not load. Please refresh the page.';
      w.innerHTML = '<div class="empty">' + esc(msg) + '</div>' + credit();
    }

    function media(x, big) {
      if (big && x.video && x.video.mp4) return '<div class="m"><video src="' + esc(x.video.mp4) + '" autoplay muted loop playsinline></video><span class="bd">&#9654; Plays on a loop</span></div>';
      if (x.has_video) return '<div class="m"><span class="ph">' + (big && x.video_paused ? 'Video paused until next month' : '') + '</span><img src="' + POSTERS + esc(x.id) + '.jpg" alt="" loading="lazy" onerror="this.remove()"><span class="bd">&#9654; Animated</span></div>';
      return '<div class="m"><span class="ph">Video coming soon</span></div>';
    }
    function tags(x) {
      var mus = (x.muscles && x.muscles.primary) || x.muscles || [];
      return '<div class="tags"><span class="' + esc(x.difficulty) + '">' + esc(cap(x.difficulty)) + '</span>' +
        mus.slice(0, 2).map(function (m) { return '<span>' + esc(m) + '</span>'; }).join('') +
        (x.equipment || []).slice(0, 1).map(function (m) { return '<span>' + esc(m) + '</span>'; }).join('') + '</div>';
    }
    function cardHtml(x) {
      return '<button class="card' + (st.open === x.id ? ' on' : '') + '" data-id="' + esc(x.id) + '">' + media(x) + '<div class="cb"><b>' + esc(x.name) + '</b>' + tags(x) + '</div></button>';
    }
    function list(items, t) { return items.length ? '<' + t + '>' + items.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</' + t + '>' : ''; }
    function detailHtml(x, closable) {
      var sw = (x.easier || []).slice(0, 1).map(function (s) { return '<button data-id="' + esc(s) + '"><small>Easier</small>' + esc(title(s)) + '</button>'; }).join('') +
        (x.harder || []).slice(0, 1).map(function (s) { return '<button data-id="' + esc(s) + '"><small>Harder</small>' + esc(title(s)) + '</button>'; }).join('');
      return media(x, true) + '<div class="dx">' + (closable ? '<button class="x" aria-label="Close">&times;</button>' : '') +
        '<h3>' + esc(x.name) + '</h3><p>' + esc(x.description) + '</p>' + tags(x) +
        (x.setup_steps && x.setup_steps.length ? '<h4>Set up</h4>' + list(x.setup_steps, 'ol') : '') +
        (x.coaching_cues && x.coaching_cues.length ? '<h4>Coaching cues</h4>' + list(x.coaching_cues, 'ul') : '') +
        (x.common_mistakes && x.common_mistakes.length ? '<h4>Common mistakes</h4>' + list(x.common_mistakes, 'ul') : '') +
        (x.rep_ranges ? '<h4>Reps</h4><p>' + esc(x.rep_ranges) + '</p>' : '') +
        (sw ? '<div class="sw">' + sw + '</div>' : '') + '</div>';
    }

    // One exercise on its own (a blog post or programme page).
    if (o.view === 'exercise') {
      get('/init', o).then(function (init) { plan(init); return get('/exercises/' + encodeURIComponent(o.id), o); }).then(function (j) {
        w.innerHTML = '<div class="det" style="position:static;max-height:none;box-shadow:none;border:0">' + detailHtml(j.data, false) + '</div>' + credit();
        w.querySelector('.det').style.border = '0';
        w.addEventListener('click', function (e) {
          var b = e.target.closest && e.target.closest('.sw button');
          if (b) { o.id = b.getAttribute('data-id'); get('/exercises/' + encodeURIComponent(o.id), o).then(function (j2) { w.querySelector('.det').innerHTML = detailHtml(j2.data, false); }); }
        });
      }).catch(fail);
      return;
    }

    function load(reset) {
      if (reset) { st.offset = 0; st.items = []; }
      var p = '/exercises?limit=24&offset=' + st.offset;
      if (o.view === 'list') p += '&ids=' + encodeURIComponent(o.ids) + '&limit=60';
      if (st.q) p += '&q=' + encodeURIComponent(st.q);
      var m = st.muscle || (o.filter.length ? o.filter.join(',') : '');
      if (m) p += '&muscle=' + encodeURIComponent(m);
      if (st.equipment) p += '&equipment=' + encodeURIComponent(st.equipment);
      return get(p, o).then(function (j) { st.items = st.items.concat(j.data); st.more = o.view !== 'list' && j.count === 24; render(); });
    }
    function openDetail(id) {
      st.open = id;
      var box = w.querySelector('.det');
      w.querySelector('.body').classList.add('open');
      box.hidden = false; box.innerHTML = '<div class="empty">Loading...</div>';
      w.querySelectorAll('.card').forEach(function (c) { c.classList.toggle('on', c.getAttribute('data-id') === id); });
      get('/exercises/' + encodeURIComponent(id), o).then(function (j) { box.innerHTML = detailHtml(j.data, true); }).catch(function () { box.innerHTML = '<div class="empty">Could not load that exercise.</div>'; });
    }
    function render() {
      var g = w.querySelector('.grid');
      g.innerHTML = st.items.length ? st.items.map(cardHtml).join('') : '<div class="empty">No exercises match. Try another search.</div>';
      w.querySelector('.more').hidden = !st.more;
    }

    get('/init', o).then(function (init) {
      plan(init);
      st.videos = init.videos; st.total = init.total;
      var groups = o.filter.length ? o.filter : ['Glutes', 'Quads', 'Hamstrings', 'Chest', 'Back', 'Shoulders', 'Core', 'Biceps', 'Triceps'].filter(function (g) { return init.muscles.indexOf(g) >= 0; });
      var tools = o.view === 'list' ? '' : '<div class="tools"><input class="q" type="search" placeholder="Search ' + (o.filter.length ? '' : init.total + ' ') + 'exercises" aria-label="Search exercises">' +
        '<select class="eq" aria-label="Equipment"><option value="">All equipment</option>' + init.equipment.map(function (e) { return '<option>' + esc(e) + '</option>'; }).join('') + '</select>' +
        '<div class="chips"><button class="chip on" data-m="">All</button>' + groups.map(function (g) { return '<button class="chip" data-m="' + esc(g) + '">' + esc(g) + '</button>'; }).join('') + '</div></div>';
      w.innerHTML = tools + '<div class="body"><div><div class="grid"></div><button class="more" hidden>Show more</button></div><div class="det" hidden></div></div>' +
        (init.videos ? '' : '<div class="note">Videos are paused for the rest of this month.</div>') + credit();
      var t;
      var q = w.querySelector('.q');
      if (q) q.addEventListener('input', function () { clearTimeout(t); t = setTimeout(function () { st.q = q.value.trim(); load(true).catch(fail); }, 300); });
      var eq = w.querySelector('.eq');
      if (eq) eq.addEventListener('change', function () { st.equipment = eq.value; load(true).catch(fail); });
      w.addEventListener('click', function (e) {
        var c = e.target.closest ? e.target : null; if (!c) return;
        var chip = c.closest('.chip');
        if (chip) { w.querySelectorAll('.chip').forEach(function (x) { x.classList.toggle('on', x === chip); }); st.muscle = chip.getAttribute('data-m'); load(true).catch(fail); return; }
        var card = c.closest('.card, .sw button');
        if (card) { openDetail(card.getAttribute('data-id')); return; }
        if (c.closest('.x')) { st.open = ''; w.querySelector('.det').hidden = true; w.querySelector('.body').classList.remove('open'); w.querySelectorAll('.card').forEach(function (x) { x.classList.remove('on'); }); return; }
        if (c.closest('.more')) { st.offset += 24; load(false).catch(fail); }
      });
      return load(true);
    }).catch(fail);
  }

  var scripts = [];
  if (document.currentScript) scripts.push(document.currentScript);
  else scripts = Array.prototype.slice.call(document.querySelectorAll('script[src*="widget.js"][data-site]'));

  scripts.forEach(function (s) {
    if (!s || s.__totality) return;
    s.__totality = true;
    var d = s.dataset || {};
    var target = d.target ? document.querySelector(d.target) : null;
    if (!target) { var def = document.getElementById('totality-exercises'); if (def && !def.__totality) target = def; }
    if (!target) { target = document.createElement('div'); s.parentNode.insertBefore(target, s.nextSibling); }
    target.__totality = true;
    mount(target, {
      site: d.site || '', view: d.view || (d.id ? 'exercise' : d.ids ? 'list' : 'library'), id: d.id || '', ids: d.ids || '',
      accent: /^#[0-9a-fA-F]{3,8}$/.test(d.accent || '') ? d.accent : '#ED8008', dark: d.theme === 'dark',
      filter: (d.filter || '').split(',').map(function (x) { return x.trim(); }).filter(Boolean),
    });
  });
})();
