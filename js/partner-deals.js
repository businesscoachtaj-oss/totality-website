/* Partner deals page (20 Nov 2026). Lists the partner meal and protein brands that are switched
   on in Totality's partner_brands table (only those with a Commission Factory link are
   readable), and counts each tap on a Shop button (brand and time only, no personal details). */
(function () {
  var SUPA = 'https://spqazfyxxhzizbtmxklr.supabase.co';
  var KEY = 'sb_publishable_zlny2kAAjetWEHlrFR_i3A_RrKixrSt';
  var H = { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' };
  var $ = function (id) { return document.getElementById(id); };
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  var visitor;
  try { visitor = sessionStorage.getItem('pd_v'); } catch (e) {}
  if (!visitor) { visitor = Math.random().toString(36).slice(2) + Date.now().toString(36); try { sessionStorage.setItem('pd_v', visitor); } catch (e) {} }

  function card(p) {
    var url = /^https:\/\//.test(p.link_url) ? p.link_url : '#';
    return '<div class="card deal-card"><div class="deal-card__top"><div class="deal-logo" aria-hidden="true">' + esc(p.initials) + '</div><h3>' + esc(p.name) + '</h3></div>' +
      '<p>' + esc(p.blurb) + '.</p>' +
      (p.in_food_search ? '<div class="deal-tags"><span class="pill pill--blue">In food search</span></div>' : '') +
      '<a class="btn btn--totality btn--sm" href="' + esc(url) + '" target="_blank" rel="sponsored noopener" data-track="off" data-partner="' + esc(p.key) + '">Shop ' + esc(p.short_name) + '</a></div>';
  }

  function render(rows) {
    var meals = rows.filter(function (p) { return p.kind !== 'protein'; });
    var protein = rows.filter(function (p) { return p.kind === 'protein'; });
    $('pd-meals').innerHTML = meals.map(card).join('');
    $('pd-protein').innerHTML = protein.map(card).join('');
    $('pd-meals-wrap').hidden = !meals.length;
    $('pd-protein-wrap').hidden = !protein.length;
    $('pd-none').hidden = rows.length > 0;
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-partner]');
    if (!a) return;
    try {
      fetch(SUPA + '/rest/v1/rpc/log_partner_click', {
        method: 'POST', headers: H, keepalive: true,
        body: JSON.stringify({ p_key: a.getAttribute('data-partner'), p_place: 'website', p_visitor: visitor })
      }).catch(function () {});
    } catch (err) {}
  });

  fetch(SUPA + '/rest/v1/partner_brands?select=key,name,short_name,blurb,kind,initials,link_url,in_food_search&order=sort', { headers: H })
    .then(function (r) { if (!r.ok) throw new Error('http ' + r.status); return r.json(); })
    .then(function (rows) { render((rows || []).filter(function (p) { return p.link_url; })); })
    .catch(function () { render([]); });
})();
