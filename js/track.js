/* Meta Pixel conversion events for totality360.com.au.
 *
 * The base pixel (3550080485153029, PageView) is loaded separately in each page's <head>.
 * This file only adds conversion events on top of it, and does nothing if fbq is missing
 * (ad blockers, pages without the pixel such as the legal pages).
 *
 * Events:
 *   Lead          when a Formspree submit (calculator, commission calculator, guide gate,
 *                 newsletter) comes back OK. Detected by wrapping window.fetch, so pages
 *                 need no extra code. content_name says which form it was.
 *   StartTrial    on clicks to the app stores, the web apps (totalityapp.com.au,
 *                 totalitynutrition.com.au) or the get-totality / get-nutrition pages.
 *                 Params: content_name (totality | nutrition), placement, page.
 *                 Fires once per app per browser session, so a click to get-totality.html
 *                 followed by a click to the App Store counts once.
 *   ViewContent   on pricing.html.
 *
 * Optional attributes on a link:
 *   data-track-app="totality|nutrition"   override the app
 *   data-track-placement="hero"           override the placement label
 *   data-track="off"                      skip tracking for this link
 */
(function () {
  'use strict';

  var FORMSPREE_RE = /formspree\.io\//i;

  function hasPixel() { return typeof window.fbq === 'function'; }

  function send(eventName, params) {
    if (!hasPixel()) return;
    try { window.fbq('track', eventName, params || {}); } catch (e) { /* no-op */ }
  }

  function pagePath() {
    var p = (location.pathname || '/').replace(/index\.html$/, '');
    return p || '/';
  }

  // ---- Lead: Formspree submits that succeed --------------------------------

  function leadName(bodyObj) {
    var path = pagePath();
    if (bodyObj && bodyObj.guide) return 'guide: ' + bodyObj.guide;
    if (/commission-calculator/.test(path)) return 'commission_calculator';
    if (/calculator/.test(path)) return 'macro_calculator';
    if (/resources/.test(path)) return 'guide';
    if (bodyObj && bodyObj.source) return String(bodyObj.source);
    return 'newsletter';
  }

  function parseBody(body) {
    if (!body) return null;
    if (typeof body === 'string') {
      try { return JSON.parse(body); } catch (e) { return null; }
    }
    if (typeof FormData !== 'undefined' && body instanceof FormData) {
      var o = {};
      try { body.forEach(function (v, k) { o[k] = v; }); } catch (e) { /* no-op */ }
      return o;
    }
    return null;
  }

  function fireLead(bodyObj) {
    var params = { content_name: leadName(bodyObj), page: pagePath() };
    if (bodyObj && bodyObj.is_coach) params.content_category = String(bodyObj.is_coach);
    send('Lead', params);
  }

  if (typeof window.fetch === 'function' && !window.fetch.__totalityTracked) {
    var origFetch = window.fetch;
    var wrapped = function (input, init) {
      var url = typeof input === 'string' ? input : (input && input.url) || '';
      var p = origFetch.apply(this, arguments);
      if (FORMSPREE_RE.test(url)) {
        var bodyObj = parseBody(init && init.body);
        p.then(function (res) { if (res && res.ok) fireLead(bodyObj); }, function () {});
      }
      return p;
    };
    wrapped.__totalityTracked = true;
    window.fetch = wrapped;
  }

  // Plain HTML forms that post straight to Formspree (no fetch): count the submit.
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.getAttribute) return;
    var action = form.getAttribute('action') || '';
    if (FORMSPREE_RE.test(action) && !e.defaultPrevented) {
      var o = {};
      try { new FormData(form).forEach(function (v, k) { o[k] = v; }); } catch (err) { /* no-op */ }
      fireLead(o);
    }
  }, true);

  // ---- StartTrial: clicks to the apps ---------------------------------------

  function appFor(href) {
    var h = href.toLowerCase();
    if (/totalitynutrition\.com\.au|get-nutrition\.html|app\.totality\.nutrition|totality-nutrition/.test(h)) return 'nutrition';
    if (/totalityapp\.com\.au|get-totality\.html|app\.livewell|id6798809525|totality-for-gyms/.test(h)) return 'totality';
    if (/apps\.apple\.com|play\.google\.com/.test(h)) {
      // Unknown store listing: fall back to the page it sits on.
      return /nutrition/.test(pagePath()) ? 'nutrition' : 'totality';
    }
    return null;
  }

  function placementFor(a) {
    var tagged = a.closest('[data-track-placement]');
    if (tagged) return tagged.getAttribute('data-track-placement');
    if (a.closest('header, nav')) return 'nav';
    if (a.closest('footer')) return 'footer';
    var section = a.closest('section[id], div[id], article[id], section[class]');
    if (section) return section.id || String(section.className).split(' ')[0];
    return 'body';
  }

  var sentThisLoad = {};
  function alreadySent(app) {
    if (sentThisLoad[app]) return true;
    try { if (window.sessionStorage.getItem('tt_start_' + app)) return true; } catch (e) { /* no-op */ }
    return false;
  }
  function markSent(app) {
    sentThisLoad[app] = true;
    try { window.sessionStorage.setItem('tt_start_' + app, '1'); } catch (e) { /* no-op */ }
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a || a.getAttribute('data-track') === 'off') return;
    var app = a.getAttribute('data-track-app') || appFor(a.getAttribute('href') || '');
    if (!app || alreadySent(app)) return;
    markSent(app);
    send('StartTrial', { content_name: app, placement: placementFor(a), page: pagePath() });
  }, true);

  // ---- ViewContent: pricing page -------------------------------------------

  if (/\/pricing(\.html)?\/?$/.test(location.pathname)) {
    send('ViewContent', { content_name: 'pricing', content_category: 'pricing', page: pagePath() });
  }
})();
