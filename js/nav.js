/* Shared header behaviour: mobile menu, dropdowns, current-page link.
   Works with the static header written by tools/apply_chrome.py and with
   the runtime fallback in js/site-chrome.js (listens for chrome:ready). */
(function () {
  var bound = false;

  function init() {
    var toggle = document.getElementById('navToggle');
    var menu = document.getElementById('navMenu');
    if (!toggle || !menu || bound) return;
    bound = true;
    document.documentElement.classList.add('js');

    function setOpen(open) {
      menu.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      document.body.style.overflow = open && window.innerWidth <= 1020 ? 'hidden' : '';
    }
    toggle.addEventListener('click', function () {
      setOpen(!menu.classList.contains('is-open'));
    });
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });

    // Dropdowns are <details>: keep one open at a time, close on outside click / Escape.
    var dds = Array.prototype.slice.call(document.querySelectorAll('.nav-dd'));
    dds.forEach(function (d) {
      d.addEventListener('toggle', function () {
        if (d.open) dds.forEach(function (o) { if (o !== d) o.open = false; });
      });
    });
    document.addEventListener('click', function (e) {
      if (window.innerWidth <= 1020) return;
      dds.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var openDd = dds.filter(function (d) { return d.open; })[0];
      dds.forEach(function (d) { d.open = false; });
      if (openDd) openDd.querySelector('summary').focus();
      if (menu.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 1020) setOpen(false);
    });

    // Current page (static pages already carry aria-current; this covers the JS fallback).
    function normalize(p) {
      p = p.replace(/index\.html$/, '');
      return p.charAt(p.length - 1) === '/' || /\.html$/.test(p) ? p : p + '/';
    }
    var here = normalize(location.pathname);
    menu.querySelectorAll('a[href^="/"]').forEach(function (a) {
      if (normalize(new URL(a.getAttribute('href'), location.href).pathname) === here) {
        a.setAttribute('aria-current', 'page');
      }
    });
  }

  document.addEventListener('chrome:ready', init);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
