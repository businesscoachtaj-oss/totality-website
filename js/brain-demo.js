// Tali's brain, demo version for the Tali HQ page (6 Nov 2026, asked for by Taj).
// Same shape as the 3D brain in the app (components/BrainGlobe.tsx in tali-hq), drawn on a canvas.
// Drag to spin, tap a part (or a chip) to see what Tali keeps there. The memories are made up examples.
(function () {
  var root = document.getElementById('brain-demo');
  if (!root) return;
  var canvas = root.querySelector('canvas');
  var ctx = canvas.getContext('2d');
  var panel = root.querySelector('.bd-panel');
  var chipsEl = root.querySelector('.bd-chips');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var REGIONS = {
    hippocampus: { name: 'Hippocampus', human: 'Memory', tali: 'Facts and events she remembers', colour: '#9FB7FF', eg: ['Sam’s café opens at 6am', 'Invoice 104 was paid on 3 Nov'] },
    temporal: { name: 'Temporal lobe', human: 'Language and who is who', tali: 'The people in your world', colour: '#FFC37A', eg: ['Priya does Sam’s books', 'Jordan likes a text, not an email'] },
    cerebellum: { name: 'Cerebellum', human: 'Fixing mistakes and fine tuning', tali: 'Lessons and mistakes. Lessons that keep holding become proven', colour: '#FF9EC4', eg: ['Morning emails get faster replies (proven)', 'Don’t book anyone before 7am'] },
    frontal: { name: 'Frontal lobe', human: 'Self-control and judgement', tali: 'Rules and preferences she sticks to, and nothing goes out without your yes', colour: '#B9A6FF', eg: ['Keep replies short and friendly', 'Never send without a yes'] },
    prefrontal: { name: 'Prefrontal cortex', human: 'Planning ahead', tali: 'Plans, ideas, your live goals and open decisions', colour: '#D7B5FF', eg: ['Goal: 20 new clients by March', 'Deciding: a second location?'] },
    amygdala: { name: 'Amygdala', human: 'Urgency and threat', tali: 'Anything urgent, and contradictions for you to settle', colour: '#FF7A6E', eg: ['Lease renewal due Friday', 'Two prices on file for the large tray'] },
    occipital: { name: 'Occipital lobe', human: 'Vision', tali: 'What she saw in photos and screenshots you sent, and the images she made for you', colour: '#8EF0C8', eg: ['The new menu photo from Tuesday', 'A flyer she made for the open day'] },
    parietal: { name: 'Parietal lobe', human: 'The senses', tali: 'What she can feel: your connected Gmail and Calendar', colour: '#7FD1FF', eg: ['3 emails need a reply', 'Free from 2pm to 4pm today'] },
    thalamus: { name: 'Thalamus', human: 'The relay station', tali: 'The router that files every new memory into the right part', colour: '#FFE38A', eg: ['Filed 12 new memories today', 'Sent “Priya” to people'] },
    hypothalamus: { name: 'Hypothalamus', human: 'The body clock', tali: 'Her schedule: morning brief, health checks, shutdown, night school', colour: '#FFB38A', eg: ['Morning brief at 7am', 'Shutdown at 6pm'] },
    basal_ganglia: { name: 'Basal ganglia', human: 'Habits', tali: 'Skills and routines she has learned', colour: '#C6F28A', eg: ['Fridays: chase unpaid invoices', 'Mondays: plan the week'] },
    brainstem: { name: 'Brainstem', human: 'Keeps you alive', tali: 'The core that keeps every memory searchable', colour: '#A6B0C8', eg: ['Finds a memory by what it means, not just the words'] },
    corpus_callosum: { name: 'Corpus callosum', human: 'Joins the two halves', tali: 'The shared brain every Tali learns from, with no personal details', colour: '#E9E4FF', eg: ['Cafés get more reviews when they ask the same day'] }
  };
  var ORDER = ['hippocampus', 'temporal', 'cerebellum', 'frontal', 'prefrontal', 'amygdala', 'occipital', 'parietal', 'thalamus', 'hypothalamus', 'basal_ganglia', 'brainstem', 'corpus_callosum'];

  // ---- The shape (same maths as the app) ----
  function rng(seed) { var s = seed; return function () { s = (s * 1664525 + 1013904223) % 4294967296; return s / 4294967296; }; }
  function cortexRegion(p) {
    if (p.z > 0.62 && p.y > -0.2) return 'prefrontal';
    if (p.z < -0.58) return 'occipital';
    if (p.y < 0.22 && Math.abs(p.x) > 0.28 && p.z > -0.58 && p.z < 0.62) return 'temporal';
    if (p.z > 0.12) return 'frontal';
    return 'parietal';
  }
  var r = rng(42), dots = [];
  [-1, 1].forEach(function (side) {
    var made = 0;
    for (var i = 0; made < 190 && i < 420; i++) {
      var t = (i + 0.5) / 420, phi = Math.acos(1 - 2 * t), th = i * 2.399963 + side * 0.7;
      var nx = Math.sin(phi) * Math.cos(th), ny = Math.cos(phi), nz = Math.sin(phi) * Math.sin(th);
      if (nx * side < -0.45) continue;
      var fold = 1 + 0.035 * Math.sin(11 * phi + 5 * th) + 0.025 * Math.sin(17 * th + 3 * phi);
      var y = ny * 0.58 * fold, z = nz * 0.95 * fold;
      if (y < -0.18) y = -0.18 + (y + 0.18) * 0.45;
      var temporal = Math.max(0, -ny) * Math.max(0, 1 - Math.abs(nz - 0.15) * 1.6) * Math.max(0, nx * side);
      y -= temporal * 0.22;
      var p = { x: side * 0.27 + nx * 0.38 * fold + side * temporal * 0.05, y: 0.15 + y, z: z };
      p.region = cortexRegion(p); p.size = 3.6 + r() * 1.4; dots.push(p); made++;
    }
  });
  for (var i = 0; i < 46; i++) {
    var a = r() * Math.PI * 2, b = Math.acos(2 * r() - 1), ridge = 1 + 0.08 * Math.sin(10 * b);
    dots.push({ x: Math.sin(b) * Math.cos(a) * 0.56 * ridge, y: -0.5 + Math.cos(b) * 0.24, z: -0.62 + Math.sin(b) * Math.sin(a) * 0.3 * ridge, region: 'cerebellum', size: 4.5 + r() * 1.5 });
  }
  for (i = 0; i < 18; i++) {
    var a2 = r() * Math.PI * 2, h = r();
    dots.push({ x: Math.cos(a2) * 0.12, y: -0.38 - h * 0.62, z: -0.22 - h * 0.12 + Math.sin(a2) * 0.12, region: 'brainstem', size: 4.5 });
  }
  function cluster(region, c, sp, n, size, mirror) {
    (mirror === false ? [1] : [-1, 1]).forEach(function (side) {
      for (var k = 0; k < n; k++) dots.push({ x: side * c.x + (r() - 0.5) * sp.x, y: c.y + (r() - 0.5) * sp.y, z: c.z + (r() - 0.5) * sp.z, region: region, size: size });
    });
  }
  cluster('hippocampus', { x: 0.32, y: -0.18, z: -0.2 }, { x: 0.12, y: 0.12, z: 0.42 }, 9, 6);
  cluster('amygdala', { x: 0.3, y: -0.24, z: 0.16 }, { x: 0.1, y: 0.1, z: 0.1 }, 5, 7);
  cluster('thalamus', { x: 0.12, y: 0.02, z: -0.08 }, { x: 0.1, y: 0.12, z: 0.18 }, 5, 6.5);
  cluster('hypothalamus', { x: 0, y: -0.2, z: 0.08 }, { x: 0.1, y: 0.08, z: 0.1 }, 6, 6.5, false);
  cluster('basal_ganglia', { x: 0.27, y: 0.06, z: 0.14 }, { x: 0.1, y: 0.18, z: 0.24 }, 6, 6);
  for (i = 0; i < 14; i++) {
    var tt = i / 13;
    dots.push({ x: (r() - 0.5) * 0.14, y: 0.2 + Math.sin(tt * Math.PI) * 0.16, z: 0.5 - tt * 1.0, region: 'corpus_callosum', size: 5.5 });
  }
  var deep = { hippocampus: 1, amygdala: 1, thalamus: 1, hypothalamus: 1, basal_ganglia: 1, corpus_callosum: 1 };

  // A soft glowing dot per colour, drawn once.
  var sprites = {};
  ORDER.forEach(function (id) {
    var c = document.createElement('canvas'); c.width = c.height = 64;
    var g = c.getContext('2d'), grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grd.addColorStop(0, '#ffffffcc'); grd.addColorStop(0.1, REGIONS[id].colour); grd.addColorStop(0.26, REGIONS[id].colour); grd.addColorStop(0.34, REGIONS[id].colour + '55'); grd.addColorStop(1, REGIONS[id].colour + '00');
    g.fillStyle = grd; g.fillRect(0, 0, 64, 64); sprites[id] = c;
  });

  // ---- State ----
  var ry = 0.6, rx = 0.18, vy = reduce ? 0 : 0.0035, size = 400, dpr = 1;
  var selected = null, hover = null, touring = !reduce, tourAt = 0, tourIdx = 0, lastInput = 0, lastTouch = 0;
  var dragging = false, lastX = 0, lastY = 0, moved = 0;
  var proj = [];

  function resize() {
    var w = canvas.clientWidth; size = w; dpr = Math.min(3, window.devicePixelRatio || 1);
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(w * dpr);
  }
  function project(p) {
    var cy = Math.cos(ry), sy = Math.sin(ry), x1 = p.x * cy + p.z * sy, z1 = -p.x * sy + p.z * cy;
    var cx = Math.cos(rx), sx = Math.sin(rx), y2 = p.y * cx - z1 * sx, z2 = p.y * sx + z1 * cx;
    var k = 3.2 / (3.2 - z2), half = size / 2, sc = half * 0.88 * k;
    return { sx: half + x1 * sc, sy: half - y2 * sc + size * 0.02, k: k, z: z2 };
  }
  function draw() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, size, size);
    proj = dots.map(function (d) { var p = project(d); p.d = d; return p; });
    proj.sort(function (a, b) { return a.z - b.z; });
    var focus = hover || selected, scale = size / 400;
    // 6 Nov 2026 (Taj: too blurry on phones): every dot is a crisp circle; only the part you picked
    // gets a soft glow behind it.
    for (var i = 0; i < proj.length; i++) {
      var p = proj[i], d = p.d, on = focus === d.region;
      var depth = (p.z + 1.1) / 2.2;
      var base = focus ? (on ? 1 : 0.22) : (deep[d.region] ? 1 : 0.85);
      var a = Math.max(0.06, Math.min(1, base * (0.3 + depth * 0.8)));
      var rad = d.size * p.k * scale * (on ? 0.95 : 0.78);
      if (on) {
        var g = rad * 6;
        ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = a * 0.5;
        ctx.drawImage(sprites[d.region], p.sx - g / 2, p.sy - g / 2, g, g);
        ctx.globalCompositeOperation = 'source-over';
      }
      ctx.globalAlpha = a;
      ctx.fillStyle = REGIONS[d.region].colour;
      ctx.beginPath(); ctx.arc(p.sx, p.sy, rad, 0, Math.PI * 2); ctx.fill();
      if (on) { ctx.globalAlpha = a * 0.8; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(p.sx, p.sy, rad * 0.45, 0, Math.PI * 2); ctx.fill(); }
    }
    ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  }

  // 6 Nov 2026 (Taj): tap the part again, tap empty space or "Whole brain" to see every part lit up.
  function show(id) {
    selected = id;
    if (!id) {
      panel.innerHTML =
        '<p class="bd-kicker" style="color:#B9A6FF">13 parts</p>' +
        '<h3>The whole brain</h3>' +
        '<p class="bd-tali">Every part lit up at once. Each one holds a different kind of memory, and the more Tali learns, the brighter it glows.</p>' +
        '<p class="bd-tali" style="margin:0">Tap a part, or a name below, to see what she keeps there.</p>';
    } else {
    var R = REGIONS[id];
    panel.innerHTML =
      '<p class="bd-kicker" style="color:' + R.colour + '">' + R.human + ' in you</p>' +
      '<h3>' + R.name + '</h3>' +
      '<p class="bd-tali"><b>In Tali:</b> ' + R.tali + '.</p>' +
      '<p class="bd-eg-h">Example memories</p>' +
      '<ul class="bd-eg">' + R.eg.map(function (e) { return '<li style="--c:' + R.colour + '">' + e + '</li>'; }).join('') + '</ul>';
    }
    Array.prototype.forEach.call(chipsEl.children, function (b) { b.setAttribute('aria-pressed', (b.dataset.id || null) === id ? 'true' : 'false'); });
  }
  function stopTour() { touring = false; lastTouch = performance.now(); }

  var all = document.createElement('button');
  all.type = 'button'; all.textContent = 'Whole brain'; all.style.setProperty('--c', '#fff'); all.setAttribute('aria-pressed', 'false');
  all.addEventListener('click', function () { stopTour(); show(null); });
  chipsEl.appendChild(all);
  ORDER.forEach(function (id) {
    var b = document.createElement('button');
    b.type = 'button'; b.dataset.id = id; b.textContent = REGIONS[id].name; b.style.setProperty('--c', REGIONS[id].colour);
    b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', function () { stopTour(); show(selected === id ? null : id); });
    chipsEl.appendChild(b);
  });

  function pick(x, y) {
    var best = null, bd = 22 * 22;
    for (var i = proj.length - 1; i >= 0; i--) {
      var p = proj[i], dx = p.sx - x, dy = p.sy - y, dd = dx * dx + dy * dy;
      if (dd < bd) { bd = dd; best = p.d.region; }
    }
    return best;
  }
  function pos(e) { var rc = canvas.getBoundingClientRect(); return { x: e.clientX - rc.left, y: e.clientY - rc.top }; }
  canvas.addEventListener('pointerdown', function (e) { dragging = true; moved = 0; lastX = e.clientX; lastY = e.clientY; canvas.setPointerCapture(e.pointerId); stopTour(); });
  canvas.addEventListener('pointermove', function (e) {
    if (dragging) {
      var dx = e.clientX - lastX, dy = e.clientY - lastY; moved += Math.abs(dx) + Math.abs(dy);
      ry += dx * 0.01; rx = Math.max(-0.8, Math.min(0.8, rx + dy * 0.008)); lastX = e.clientX; lastY = e.clientY; lastInput = performance.now();
    } else if (e.pointerType === 'mouse') {
      var q = pos(e); hover = pick(q.x, q.y); canvas.style.cursor = hover ? 'pointer' : 'grab';
    }
  });
  canvas.addEventListener('pointerup', function (e) {
    dragging = false;
    if (moved < 6) { var q = pos(e), hit = pick(q.x, q.y); show(hit && hit !== selected ? hit : null); }
  });
  canvas.addEventListener('pointerleave', function () { hover = null; });

  var visible = true;
  if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(root);
  function frame(now) {
    if (visible) {
      if (!dragging && !reduce && now - lastInput > 2500) ry += vy;
      if (touring && now - tourAt > 4200) { show(ORDER[tourIdx % ORDER.length]); tourIdx++; tourAt = now; }
      if (!touring && !reduce && now - lastTouch > 20000) { touring = true; tourAt = 0; }
      draw();
    }
    requestAnimationFrame(frame);
  }
  window.addEventListener('resize', resize);
  resize(); show(ORDER[0]); tourIdx = 1; tourAt = performance.now();
  requestAnimationFrame(frame);
})();
