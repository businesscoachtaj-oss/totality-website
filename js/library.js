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

  // Book text arrives hard wrapped, with headings, verse and footnotes as plain lines. Work out what
  // each block is so the page can set it like a printed book. The words are kept as written.
  function blocks(text) {
    var out = [], lead = false;
    String(text || '').replace(/\r/g, '').split(/\n\s*\n+/).forEach(function (raw) {
      var lines = raw.split('\n').map(function (l) { return l.replace(/\s+$/, ''); }).filter(function (l) { return l.trim(); });
      if (!lines.length) return;
      var flat = lines.map(function (l) { return l.trim(); }).join(' ').replace(/\s{2,}/g, ' ');
      if (/^(produced by|e-text prepared by|transcribed by)\b/i.test(flat)) return;
      var letters = flat.replace(/[^A-Za-zÀ-ɏ]/g, '');
      var upper = letters.replace(/[^A-ZÀ-Þ]/g, '').length;
      var caps = letters.length > 0 && upper / letters.length >= 0.8;
      if (/^\[illustration/i.test(flat)) {
        var cap = flat.replace(/^\[illustration:?\s*/i, '').replace(/\]$/, '');
        if (cap) out.push({ kind: 'caption', text: cap });
      } else if (/^\[(\d+|footnote)/i.test(flat)) {
        out.push({ kind: 'footnote', text: flat });
      } else if (lines.every(function (l) { return /\s{3,}\d+$/.test(l); })) {
        out.push({ kind: 'contents', lines: lines.map(function (l) { return l.replace(/\s{3,}\d+$/, '').trim(); }) });
      } else if (caps && (flat.length <= 90 || (flat.length <= 240 && /^(CHAPTER|LECTURE|BOOK|PART|SECTION)\s+[IVXLC\d]+\.?$/.test(lines[0].trim())))) {
        var first = lines[0].trim();
        if (flat.length <= 14 && /\.$/.test(flat) && /\.\s*[A-Z]/.test(flat) && !/^(CHAPTER|LECTURE|BOOK|PART)\b/.test(flat)) out.push({ kind: 'sign', text: flat });
        else if (/^[IVXLC]+\.?$/.test(flat)) { out.push({ kind: 'number', text: flat.replace(/\.$/, '') }); lead = true; }
        else if (/^(CHAPTER|LECTURE|BOOK|PART|SECTION)\s+[IVXLC\d]+\.?$/.test(first)) {
          out.push({ kind: 'number', text: first.replace(/\.$/, '') });
          var rest = lines.slice(1).map(function (l) { return l.trim(); }).join(' ');
          if (rest) out.push({ kind: 'heading', text: rest });
          lead = true;
        } else { out.push({ kind: 'heading', text: flat }); lead = true; }
      } else if (lines.length >= 2 && lines.every(function (l) { return l.trim().length < 56; })) {
        out.push({ kind: 'verse', lines: lines.map(function (l) { return l.trim(); }) });
      } else {
        out.push({ kind: 'p', text: flat, lead: lead });
        lead = false;
      }
    });
    return out;
  }
  function ink(s) { return esc(s).replace(/_([^_]+)_/g, '<em>$1</em>'); }
  // "CHAPTER IV." reads "Chapter IV", and a title set in capitals reads in ordinary title case.
  var SMALL = { a: 1, an: 1, and: 1, as: 1, at: 1, by: 1, 'for': 1, from: 1, 'in': 1, into: 1, of: 1, on: 1, or: 1, the: 1, to: 1, 'with': 1 };
  function softCaps(t) {
    t = String(t).replace(/\.$/, '');
    var letters = t.replace(/[^A-Za-z]/g, '');
    if (!letters || letters.replace(/[^A-Z]/g, '').length / letters.length < 0.8) return t;
    return t.toLowerCase().split(' ').map(function (w, i) {
      if (/^[ivxlc]+\.?$/.test(w)) return w.toUpperCase();
      if (i && SMALL[w]) return w;
      return w.charAt(0).toUpperCase() + w.slice(1);
    }).join(' ');
  }
  // A new chapter after some of the book's words gets an end mark and a page break,
  // so every chapter opens on a fresh page.
  function setType(text) {
    var words = false, prev = null;
    return blocks(text).map(function (b) {
      var out = '';
      if ((b.kind === 'number' || (b.kind === 'heading' && prev !== 'number')) && words) {
        out += '<div class="lib-t-end" aria-hidden="true">&#10086;</div><div class="lib-t-break" aria-hidden="true"></div>';
        words = false;
      }
      prev = b.kind;
      if (b.kind === 'number') return out + '<div class="lib-t-num">' + ink(softCaps(b.text)) + '</div>';
      if (b.kind === 'heading') return out + '<h3 class="lib-t-head">' + ink(softCaps(b.text)) + '</h3>';
      if (b.kind === 'sign') return out + '<p class="lib-t-sign">' + ink(b.text) + '</p>';
      if (b.kind === 'caption') return out + '<p class="lib-t-cap">' + ink(b.text) + '</p>';
      if (b.kind === 'footnote') return out + '<p class="lib-t-foot">' + ink(b.text) + '</p>';
      if (b.kind === 'contents') return out + '<ul class="lib-t-toc">' + b.lines.map(function (l) { return '<li>' + ink(l) + '</li>'; }).join('') + '</ul>';
      words = true;
      if (b.kind === 'verse') return out + '<p class="lib-t-verse">' + b.lines.map(ink).join('<br>') + '</p>';
      return out + '<p' + (b.lead ? ' class="lib-t-lead"' : '') + '>' + ink(b.text) + '</p>';
    }).join('');
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
      var kept = (p.kept || []).map(function (k) { return '<div class="lib-kept"><b>TALI\'S NOTE</b>' + esc(k) + '</div>'; }).join('');
      return setType(p.text) + kept + '<div class="lib-folio">page ' + p.n + ' of ' + cfg.passages + '</div>';
    }).join('');
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
