// Affiliate kit page (14 Nov 2026). Puts the affiliate's code on every image in the browser,
// fills it into the scripts, and handles downloads (single files and zips with JSZip).
(function () {
  var NBASE = 'https://totalitynutrition.com.au/signup?ref=';
  var TBASE = 'https://totalityapp.com.au/signup?ref=';
  var params = new URLSearchParams(location.search);
  function clean(s) { return (s || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 24); }
  var code = clean(params.get('code'));
  try { if (!code) code = clean(localStorage.getItem('ak_code')); } catch (e) {}
  var app = params.get('app') === 'totality' ? 'totality' : 'nutrition';

  // ---------- scripts ----------
  var pres = Array.prototype.slice.call(document.querySelectorAll('.ak-copy pre'));
  var originals = pres.map(function (p) { return p.innerHTML; });
  function fillText() {
    var c = code || 'YOURCODE', n = NBASE + c, t = TBASE + c;
    pres.forEach(function (p, i) {
      p.innerHTML = originals[i].split('{CODE}').join('<b>' + c + '</b>').split('{NLINK}').join(n).split('{TLINK}').join(t);
    });
  }

  // ---------- images with the code drawn in ----------
  var layouts = {}, made = {};
  function loadLayout(a) {
    if (layouts[a]) return Promise.resolve(layouts[a]);
    return fetch('/affiliate-kit/' + a + '/layout.json').then(function (r) { return r.json(); }).then(function (j) { layouts[a] = j; return j; });
  }
  function loadImg(src) {
    return new Promise(function (res, rej) { var im = new Image(); im.onload = function () { res(im); }; im.onerror = rej; im.src = src; });
  }
  var fontReady = (document.fonts && document.fonts.load) ? document.fonts.load('700 46px KitCode').catch(function () {}) : Promise.resolve();
  function render(key) { // key like "nutrition/carousel_1"
    var c = code || 'YOURCODE';
    var id = key + '|' + c;
    if (made[id]) return made[id];
    var parts = key.split('/'), a = parts[0], name = parts[1];
    made[id] = Promise.all([loadLayout(a), loadImg('/affiliate-kit/' + key + '.jpg'), fontReady]).then(function (r) {
      var lay = r[0][name] || {}, im = r[1];
      var cv = document.createElement('canvas'); cv.width = im.naturalWidth; cv.height = im.naturalHeight;
      var ctx = cv.getContext('2d'); ctx.drawImage(im, 0, 0);
      var k = im.naturalWidth / (lay.w || im.naturalWidth);
      if (lay.code) {
        var s = lay.code.size;
        ctx.fillStyle = lay.code.colour; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
        do { ctx.font = '700 ' + (s * k) + 'px KitCode, sans-serif'; s -= 2; } while (ctx.measureText(c).width > lay.code.w * k && s > 18);
        ctx.fillText(c, lay.code.x * k, lay.code.y * k + 2 * k);
      }
      return new Promise(function (res) { cv.toBlob(function (b) { res(b); }, 'image/jpeg', 0.92); });
    });
    return made[id];
  }
  function paintPreviews() {
    document.querySelectorAll('img[data-asset]').forEach(function (img) {
      var key = img.getAttribute('data-asset');
      if (!img.closest('.ak-panel') || img.closest('.ak-panel').hidden) return;
      render(key).then(function (b) { var u = URL.createObjectURL(b); var old = img.src; img.src = u; if (old && old.indexOf('blob:') === 0) URL.revokeObjectURL(old); });
    });
  }
  function fileName(key) { return 'totality-' + key.replace('/', '-').replace(/_/g, '-') + '-' + (code || 'yourcode').toLowerCase() + '.jpg'; }
  function saveBlob(b, name) {
    var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 5000);
  }
  function busy(btn, text) { var o = btn.textContent; btn.textContent = text; btn.disabled = true; return function (doneText) { btn.textContent = doneText || o; btn.disabled = false; btn.classList.add('is-done'); setTimeout(function () { btn.textContent = o; btn.classList.remove('is-done'); }, 1600); }; }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-dl]');
    if (b) { var key = b.getAttribute('data-dl'); var end = busy(b, 'Getting it...'); render(key).then(function (blob) { saveBlob(blob, fileName(key)); end('Saved'); }); return; }
    var z = e.target.closest('[data-zip]');
    if (z) { zipKeys(['carousel_1', 'carousel_2', 'carousel_3', 'carousel_4'].map(function (n) { return app + '/' + n; }), [], 'carousel', z); return; }
    var cp = e.target.closest('.ak-copy .ak-btn');
    if (cp) { copyText(cp.parentElement.querySelector('pre').innerText.trim(), cp); }
  });

  function zipKeys(keys, extras, label, btn) {
    if (!window.JSZip) { alertBox(btn, 'Zip unavailable, download one at a time'); return; }
    var end = busy(btn, 'Packing it up...');
    var zip = new JSZip(); var folder = zip.folder('totality-' + app + '-' + label + '-' + (code || 'yourcode').toLowerCase());
    var jobs = keys.map(function (k) { return render(k).then(function (b) { folder.file(fileName(k), b); }); });
    extras.forEach(function (p) { jobs.push(fetch('/affiliate-kit/' + p).then(function (r) { return r.blob(); }).then(function (b) { folder.file(p.split('/').slice(1).join('/'), b); })); });
    Promise.all(jobs).then(function () {
      var words = Array.prototype.map.call(document.querySelectorAll('.ak-panel:not([hidden]) .ak-copy'), function (d) { return '## ' + d.querySelector('h3').textContent + '\n\n' + d.querySelector('pre').textContent.trim(); }).join('\n\n\n');
      if (label === 'everything') folder.file('scripts-and-captions.txt', words);
      return zip.generateAsync({ type: 'blob' });
    }).then(function (b) { saveBlob(b, 'totality-' + app + '-' + label + '.zip'); end('Saved'); });
  }
  function alertBox(btn, t) { btn.textContent = t; }

  var ALL = {
    nutrition: {
      keys: ['carousel_1', 'carousel_2', 'carousel_3', 'carousel_4', 'square_1', 'story_1', 'story_2'],
      extras: ['reel.mp4', 'reel_cover.jpg', 'brand/totality-nutrition-app-icon.png', 'brand/tali-3d-peace.jpg', 'brand/tali-3d-wink-hip.jpg', 'brand/tali-3d-thumbs-full.jpg', 'brand/tali-3d-point-close.jpg', 'brand/tali-wave.png', 'brand/tali-thumbs.png', 'brand/tali-point.png', 'screens/home.png', 'screens/food-search.png', 'screens/nutrient-breakdown.png', 'screens/grocery-list.png', 'screens/food-log.png', 'screens/insights.png']
    },
    totality: { keys: [], extras: [] }
  };
  document.getElementById('kAll').addEventListener('click', function () {
    var set = ALL[app];
    zipKeys(set.keys.map(function (n) { return app + '/' + n; }), set.extras.map(function (p) { return app + '/' + p; }), 'everything', this);
  });

  // ---------- copy ----------
  function copyText(text, btn) {
    function done() { var o = btn.textContent; btn.textContent = 'Copied'; btn.classList.add('is-done'); setTimeout(function () { btn.textContent = o; btn.classList.remove('is-done'); }, 1500); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { fallback(text); done(); });
    else { fallback(text); done(); }
  }
  function fallback(text) { var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); } catch (e) {} ta.remove(); }

  // ---------- code box ----------
  function showCode() {
    document.getElementById('kCode').textContent = code || 'YOURCODE';
    document.getElementById('kCodeShow').hidden = !code;
    document.getElementById('kCodeAsk').hidden = !!code;
    fillText(); paintPreviews();
  }
  document.getElementById('kCodeChange').addEventListener('click', function () {
    document.getElementById('kCodeShow').hidden = true; document.getElementById('kCodeAsk').hidden = false;
    var i = document.getElementById('kCodeInput'); i.value = code; i.focus();
  });
  function setCode() {
    var v = clean(document.getElementById('kCodeInput').value); if (!v) return;
    code = v; try { localStorage.setItem('ak_code', v); } catch (e) {}
    showCode();
  }
  document.getElementById('kCodeSet').addEventListener('click', setCode);
  document.getElementById('kCodeInput').addEventListener('keydown', function (e) { if (e.key === 'Enter') setCode(); });

  // ---------- app switch ----------
  var MENU = { nutrition: { posts: 'posts', stories: 'stories', video: 'video', brand: 'brand', words: 'words' },
               totality: { posts: 'posts-t', stories: 'posts-t', video: 'posts-t', brand: 'posts-t', words: 'words-t' } };
  function show(a) {
    app = a;
    document.querySelectorAll('.kapp').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.app === a ? 'true' : 'false'); });
    document.querySelectorAll('.ak-panel').forEach(function (p) { p.hidden = p.dataset.panel !== a; });
    document.querySelectorAll('.kmenu a[data-n]').forEach(function (l) { l.setAttribute('href', '#' + MENU[a][l.dataset.n]); });
    document.getElementById('kAll').hidden = !ALL[a].keys.length;
    paintPreviews();
  }
  document.querySelectorAll('.kapp').forEach(function (b) { b.addEventListener('click', function () { show(b.dataset.app); }); });

  show(app); showCode();
})();
