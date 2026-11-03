/* Tali next to the top buttons: a small sprite that fades between expressions. */
(function () {
  var poses = ['wave', 'happy', 'wink', 'grin', 'idea', 'proud', 'thinking'];
  var row = document.querySelector('.hm .hero-copy .ctas') || document.querySelector('main .btn-row');
  if (!row) return;
  var top = row.getBoundingClientRect().top + window.scrollY;
  if (top > 1400) return; // only beside the hero buttons
  var box = document.createElement('span');
  box.className = 'tali-live';
  box.setAttribute('aria-hidden', 'true');
  poses.forEach(function (p, i) {
    var img = new Image();
    img.src = '/email/tali/' + p + '.png';
    img.alt = '';
    img.width = 160; img.height = 360;
    if (i === 0) img.className = 'on';
    box.appendChild(img);
  });
  row.classList.add('has-tali-live');
  row.appendChild(box);
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var imgs = box.children, cur = 0;
  function next(step) {
    imgs[cur].className = '';
    cur = (cur + (step || 1)) % imgs.length;
    imgs[cur].className = 'on';
  }
  var timer = setInterval(next, 6000);
  box.addEventListener('click', function () { clearInterval(timer); next(); timer = setInterval(next, 6000); });
  document.addEventListener('visibilitychange', function () {
    clearInterval(timer);
    if (!document.hidden) timer = setInterval(next, 6000);
  });
})();
