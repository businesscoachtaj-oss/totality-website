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

    // Mark the current page's nav link. Every href is resolved to an
    // absolute path and normalized (trailing "index.html" stripped, a
    // trailing slash added) before comparing, so "/blog/index.html" and
    // "/blog/" are recognised as the same page as "/blog/" in the nav,
    // and neither is ever confused with the site root "/".
    function normalize(pathname) {
      var p = pathname.replace(/index\.html$/, '');
      if (p.charAt(p.length - 1) !== '/') p += '/';
      return p;
    }
    var herePath = normalize(location.pathname);

    menu.querySelectorAll('a[href]').forEach(function (a) {
      var raw = a.getAttribute('href');
      var resolved;
      try {
        resolved = new URL(raw, location.href).pathname;
      } catch (e) {
        return;
      }
      if (normalize(resolved) === herePath) {
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
