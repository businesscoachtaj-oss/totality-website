// Totality Training offers (21 Nov 2026). The pages carry the standing offer in plain HTML
// (50% off the first 2 months). While Black Friday runs, this swaps in the sale wording, using
// the dates and numbers in data/plans.js (TOTALITY_PLANS.training). After the end time the page
// shows the standing offer again with no change needed.
(function () {
  var tr = window.TOTALITY_PLANS && window.TOTALITY_PLANS.training;
  if (!tr) return;
  function swap(kind, offer, text) {
    if (!offer || !offer.blackFridayEnds || Date.now() >= Date.parse(offer.blackFridayEnds)) return;
    var els = document.querySelectorAll('[data-tr-offer="' + kind + '"]');
    for (var i = 0; i < els.length; i++) els[i].textContent = text(offer);
  }
  swap('plan', tr.offer, function (o) {
    return 'Black Friday: ' + o.blackFridayPercentOff + '% off your first ' + o.months + ' months on a monthly plan, the first time you pay for Training. Ends Monday 30 November.';
  });
  swap('team', tr.teams && tr.teams.offer, function (o) {
    return 'Black Friday: ' + o.blackFridayPercentOff + '% off your team’s first ' + o.months + ' months on a monthly team. Applied at checkout, no code needed. Ends Monday 30 November.';
  });
})();
