/* Shared helpers for pages that show plan data.
   Every price, limit and credit number comes from data/plans.js
   (window.TOTALITY_PLANS). Do not type prices into pages.

   Markup hooks:
     <span data-p="tiers.solo_10.monthly"></span>     text from a path
     <span data-p="addons.pos.price"></span>           arrays are looked up by id
     <span data-p="nutrition.plans.nutrition_ai.yearly"></span>
   PlansUI.fill(root) fills every [data-p] inside root. */
(function () {
  var P = window.TOTALITY_PLANS;
  if (!P) return;

  function get(path) {
    var parts = path.split('.');
    var cur = P;
    for (var i = 0; i < parts.length; i++) {
      if (cur == null) return '';
      var key = parts[i];
      if (Array.isArray(cur)) {
        var found = null;
        for (var j = 0; j < cur.length; j++) { if (cur[j] && cur[j].id === key) { found = cur[j]; break; } }
        cur = found;
      } else {
        cur = cur[key];
      }
    }
    return cur == null ? '' : cur;
  }

  function tier(id) { return get('tiers.' + id); }
  function tiersFor(audience) { return P.tiers.filter(function (t) { return t.audience === audience; }); }

  // "A$1,009.69" -> 1009.69
  function num(s) { return parseFloat(String(s).replace(/[^0-9.]/g, '')) || 0; }
  function money(n) {
    var fixed = (Math.round(n * 100) / 100).toFixed(2);
    var parts = fixed.split('.');
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return 'A$' + parts.join('.');
  }
  // A yearly price shown as a per month figure
  function perMonthOfYear(yearlyStr) { return money(num(yearlyStr) / 12); }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }

  function fill(root) {
    (root || document).querySelectorAll('[data-p]').forEach(function (el) {
      var v = get(el.getAttribute('data-p'));
      if (typeof v === 'number') v = v.toLocaleString('en-AU');
      el.textContent = v;
    });
  }

  function statusPill(status) {
    if (status === 'addon') return ' <span class="pill pill--soon">Add-on</span>';
    if (status === 'coming_soon') return ' <span class="pill pill--soon">Coming soon</span>';
    return '';
  }

  window.PlansUI = {
    data: P, get: get, tier: tier, tiersFor: tiersFor, num: num, money: money,
    perMonthOfYear: perMonthOfYear, esc: esc, fill: fill, statusPill: statusPill
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { fill(document); });
  } else {
    fill(document);
  }
})();
