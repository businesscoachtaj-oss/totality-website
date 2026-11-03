/* Tali next to the top buttons. Her expressions are handled by tali-sprites.js. */
(function () {
  var row = document.querySelector('.hm .hero2 .ctas') || document.querySelector('main .btn-row');
  if (!row) return;
  if (row.getBoundingClientRect().top + window.scrollY > 1400) return;
  var box = document.createElement('span');
  box.className = 'tali-live';
  box.setAttribute('aria-hidden', 'true');
  var img = new Image();
  img.src = '/email/tali/all/094_Wave.png'; img.alt = ''; img.width = 160; img.height = 360;
  box.appendChild(img);
  row.classList.add('has-tali-live');
  row.appendChild(box);
})();
