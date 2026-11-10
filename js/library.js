/* Tali's library: a book page. Opens a finished book after an email, and loads the rest of her notes.
   The server decides what can be read (finished books only, and only with an email). */
(function () {
  var cfg = window.TALI_LIBRARY;
  if (!cfg) return;
  var SUPA = 'https://jbyzblwrywgxilhmfyjt.supabase.co';
  var KEY = 'sb_publishable_6boNZk1eRN8-7Z4PIbxB3w_n4VDXf51';
  var PAGE = 6;
  var $ = function (id) { return document.getElementById(id); };

  function rpc(name, body) {
    return fetch(SUPA + '/rest/v1/rpc/' + name, {
      method: 'POST',
      headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {})
    }).then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); });
  }
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  // Book text arrives hard wrapped: join each paragraph's lines, keep the words as written.
  function paragraphs(text) {
    return String(text || '').replace(/\r/g, '').split(/\n\s*\n/).map(function (b) {
      return b.replace(/\s+/g, ' ').trim();
    }).filter(function (l) { return l && !/^produced by/i.test(l); }).map(function (l) {
      return '<p>' + esc(l).replace(/_([^_]+)_/g, '<em>$1</em>') + '</p>';
    });
  }

  // ----- her notes -----
  var notes = $('lib-notes'), all = $('lib-all');
  if (notes && all) {
    all.addEventListener('click', function () {
      notes.classList.add('is-open');
      all.parentNode.hidden = true;
      if (cfg.kept <= cfg.baked) return;
      rpc('library_book', { p_book: cfg.id }).then(function (b) {
        var list = (b && b.notes) || [];
        if (list.length <= cfg.baked) return;
        notes.innerHTML = list.map(function (n) { return '<div class="lib-note">' + esc(n.text) + '</div>'; }).join('');
      }).catch(function () {});
    });
  }

  // ----- reading a finished book -----
  var form = $('lib-form');
  if (!cfg.finished || !form) return;
  var paper = $('lib-paper'), gate = $('lib-gate'), msg = $('lib-msg'), more = $('lib-more'), pos = $('lib-pos'), next = $('lib-next');
  var placeKey = 'tali.library.place.' + cfg.id;
  var from = 1, busy = false;

  function show(passages, replace) {
    var html = passages.map(function (p) {
      var kept = (p.kept || []).map(function (k) { return '<div class="lib-kept"><b>TALI KEPT THIS</b>' + esc(k) + '</div>'; }).join('');
      return '<div class="lib-eyebrow">PASSAGE ' + p.n + ' OF ' + cfg.passages + '</div>' + paragraphs(p.text).join('') + kept;
    }).join('<hr>');
    paper.innerHTML = html;
    var last = passages[passages.length - 1].n;
    from = last + 1;
    set(placeKey, String(passages[0].n));
    gate.hidden = true;
    more.hidden = false;
    pos.textContent = last >= cfg.passages ? 'The end. That is the whole book.' : 'Passages ' + passages[0].n + ' to ' + last + ' of ' + cfg.passages;
    next.textContent = last >= cfg.passages ? 'Back to the start' : 'Next pages';
    if (replace) paper.scrollIntoView({ block: 'start', behavior: 'smooth' });
  }

  function open(email, start, scroll) {
    if (busy) return Promise.resolve();
    busy = true; next.disabled = true;
    return rpc('library_open', { p_email: email, p_book: cfg.id, p_from: start, p_count: PAGE }).then(function (r) {
      busy = false; next.disabled = false;
      if (!r || r.ok === false) { if (msg) { msg.className = 'lib-err'; msg.textContent = 'That email does not look right. Check it and try again.'; } return false; }
      if (!r.passages || !r.passages.length) { if (start > 1) return open(email, 1, scroll); return false; }
      set('tali.library.email', email);
      show(r.passages, scroll);
      return true;
    }).catch(function () {
      busy = false; next.disabled = false;
      if (msg) { msg.className = 'lib-err'; msg.textContent = 'The book would not open just then. Please try again.'; }
      return false;
    });
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var email = (form.elements.email.value || '').trim();
    if (!email) return;
    var btn = form.querySelector('button'); btn.disabled = true;
    open(email, 1, true).then(function () { btn.disabled = false; });
  });
  next.addEventListener('click', function () {
    var email = get('tali.library.email');
    if (!email) { gate.hidden = false; return; }
    open(email, from > cfg.passages ? 1 : from, true);
  });

  // Already has a library card: open at the saved place.
  var saved = get('tali.library.email');
  if (saved) open(saved, Math.max(1, parseInt(get(placeKey) || '1', 10) || 1), false);
})();
