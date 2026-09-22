/* Shared mobile nav (hamburger) behaviour for every page. */
(function () {
  function init() {
    var toggle = document.getElementById('navToggle');
    var menu = document.getElementById('navMenu');
    if (!toggle || !menu) return;

    function closeMenu() {
      menu.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-label', 'Open menu');
    }
    function openMenu() {
      menu.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      toggle.setAttribute('aria-label', 'Close menu');
    }

    toggle.addEventListener('click', function () {
      var isOpen = menu.classList.contains('is-open');
      if (isOpen) { closeMenu(); } else { openMenu(); }
    });

    // Close after tapping a link (mobile in-page anchors too)
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', closeMenu);
    });

    // Close on Escape, and when resizing back to desktop width
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 860) closeMenu();
    });

    // Mark the current page's nav link. The homepage ("/") is handled as a
    // special case; every other link is matched by its own last non-empty
    // path segment, so a section link like "blog/" never gets confused
    // with the site root.
    var hereSegments = location.pathname.split('/').filter(Boolean);
    var here = hereSegments.length ? hereSegments[hereSegments.length - 1] : 'index.html';
    var onHome = here === 'index.html' || here === '';

    menu.querySelectorAll('a[href]').forEach(function (a) {
      var raw = a.getAttribute('href');
      if (raw === '/' || raw === '/index.html' || raw === 'index.html') {
        if (onHome) a.classList.add('is-current');
        return;
      }
      var segments = raw.split('/').filter(Boolean);
      var seg = segments.length ? segments[segments.length - 1] : '';
      if (seg && seg === here) {
        a.classList.add('is-current');
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
