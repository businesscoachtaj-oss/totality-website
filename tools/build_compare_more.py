#!/usr/bin/env python3
"""Build the Totality Nutrition comparisons and the extra Totality comparisons from data/compare-more.json.

    python3 tools/build_compare_more.py
    python3 tools/apply_chrome.py
    python3 tools/build_sitemap.py

Our side of each table comes from OURS below (Totality figures render from /data/plans.js, like the
original comparison pages). Competitor facts come only from their own pages, listed as sources.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build_tali_pages import ROOT, cards, e, faq_block, head, hero, section  # noqa: E402

FAMILIES = {
    "totality": {
        "ours": "Totality",
        "crumb": "Totality and {name}",
        "rows": [
            ("Who it is for", "who"), ("Starting price", "price"), ("Currency", "currency"), ("Free trial", "trial"),
            ("Yearly billing", "yearly"), ("Taking payments", "payments"), ("Classes and check-in", "classes"),
            ("Nutrition", "nutrition"), ("Custom branded app", "branded_app"),
        ],
        "offer": """<section class="section">
  <div class="container">
    <div class="offer">
      <p><strong>Try Totality:</strong> <span data-p="offers.newAccount.text"></span></p>
      <div class="btn-row">
        <a class="btn btn--white" href="/get-totality.html">Start your 7 day free trial</a>
        <a class="btn btn--ghost-light" href="/pricing.html">See pricing</a>
      </div>
    </div>
    <p class="mt-5"><a class="text-link" href="/compare/">Compare Totality with other apps</a></p>
  </div>
</section>
""",
    },
    "nutrition": {
        "ours": "Totality Nutrition",
        "crumb": "Totality Nutrition and {name}",
        "rows": [
            ("Who it is for", "who"), ("Price", "price"), ("Free version", "free"), ("Food database", "food_database"),
            ("Barcode scanning", "barcode"), ("AI logging", "ai_logging"), ("Vitamins and minerals", "micronutrients"),
            ("Targets and coaching", "coaching"), ("Apps", "apps"), ("Currency", "currency"),
        ],
        "offer": """<section class="section">
  <div class="container">
    <div class="offer">
      <p><strong>Try Totality Nutrition:</strong> every new account gets 7 days of the full Nutrition plan, no card. If you don't pick a plan, you move to Free.</p>
      <div class="btn-row">
        <a class="btn btn--white" href="/get-nutrition.html">Start 7 days free</a>
        <a class="btn btn--ghost-light" href="/nutrition-features.html">See every feature</a>
      </div>
    </div>
    <p class="mt-5"><a class="text-link" href="/compare/#nutrition">Compare Totality Nutrition with other apps</a></p>
  </div>
</section>
""",
    },
}

OURS = {
    "totality": {
        "who": "Solo personal trainers, gyms and studios. A separate Totality Nutrition app for individuals.",
        "price": 'Solo plans from <span data-p="tiers.solo_5.monthly"></span> a month (5 clients) to <span data-p="tiers.solo_200.monthly"></span> (200 clients). Studio <span data-p="tiers.studio.monthly"></span> a month for up to 500 clients and unlimited trainers. Club <span data-p="tiers.club.monthly"></span> for up to 1,500 clients. Enterprise <span data-p="tiers.enterprise.monthly"></span> for up to 5,000 clients.',
        "currency": "Australian dollars",
        "trial": '<span data-p="offers.newAccount.text"></span>',
        "yearly": '<span data-p="yearlyDiscountPercent"></span>% off when billed yearly',
        "payments": 'POS add-on on Solo plans (<span data-p="addons.pos.price"></span> a month), included on gym plans. Payments go to your own Stripe account. <span data-p="fees.text"></span>',
        "classes": "On gym plans: classes with rosters and waitlists, front desk check-in, member billing, payroll with Xero export, leads CRM, compliance.",
        "nutrition": "Food logging for clients included, with a full vitamin and mineral breakdown against Australian recommended intakes.",
        "branded_app": "Your logo, name and colour in the Totality app, member emails and push: A$4.99 a month on Solo, A$9.99 on Studio, included on Club and Enterprise. The App Store app stays Totality.",
    },
    "nutrition": {
        "who": "People in Australia who want to track food, macros and nutrients, on their own or alongside a coach.",
        "price": 'Free A$0 forever. Nutrition <span data-p="nutrition.plans.nutrition.monthly"></span> a month or <span data-p="nutrition.plans.nutrition.yearly"></span> a year. Nutrition + AI <span data-p="nutrition.plans.nutrition_ai.monthly"></span> a month or <span data-p="nutrition.plans.nutrition_ai.yearly"></span> a year.',
        "free": "Free forever, no card and no ads: food logging with full history, macro targets, water, weight and progress, 10 saved meals, 7 barcode scans a week and Tell Tali 3 times a day. New accounts get 7 days of the full Nutrition plan first.",
        "food_database": "Foods from the Australian Food Composition Database (AFCD) come first, then packaged foods from Open Food Facts. Every result shows where its numbers come from.",
        "barcode": "Yes. 7 scans a week on Free, unlimited on Nutrition.",
        "ai_logging": "Type what you ate and Tali splits it into foods and amounts for you to check, with numbers from the food database. 3 a day on Free and Nutrition, more with Tali AI credits on Nutrition + AI. No photo logging.",
        "micronutrients": "Vitamins and minerals for the day, measured against Australian recommended intakes.",
        "coaching": "A targets calculator from your details and goal, or set your own. Trend insights, and a weekly summary from Tali on Nutrition + AI.",
        "apps": "Android and the web app now. The iPhone app is coming soon.",
        "currency": "Australian dollars. Made by Totality 360 in Australia.",
    },
}


def build(fam, c, checked):
    cfg = FAMILIES[fam]
    ours = OURS[fam]
    slug, name = c["slug"], c["name"]
    url = f"/compare/{slug}.html"
    crumbs = [("Home", "/"), ("Compare", "/compare/"), (name, url)]
    rows = "\n".join(
        f'          <tr><th scope="row">{e(label)}</th><td>{e(c.get(k, "Not confirmed"))}</td><td>{ours[k]}</td></tr>'
        for label, k in cfg["rows"]
    )
    srcs = " ".join(f'<a href="{e(u)}" rel="nofollow noopener">{e(u)}</a>' for u in c["sources"])
    table = f"""    <div class="table-wrap">
      <table class="table cmp-table">
        <caption class="visually-hidden">{e(name)} and {cfg['ours']} side by side</caption>
        <thead><tr><th scope="col">&nbsp;</th><th scope="col">{e(name)}</th><th scope="col">{cfg['ours']}</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p class="cmp-src mt-4">{e(name)} sources (checked {e(checked)}): {srcs}</p>"""
    faq = c.get("faq", [])
    parts = [
        head(c["title"], c["desc"], url, crumbs, faq).replace("color: #6C3483; }", "color: var(--orange-700); }", 1)
        if fam == "totality" else head(c["title"], c["desc"], url, crumbs, faq).replace("color: #6C3483; }", "color: #1565A0; }", 1),
        hero(crumbs, c["h1"], e(c["lead"]), f"Checked {e(checked)}. Prices change, so check {e(name)}'s site before you decide."),
        section(table),
        cards(f"{name} may suit you better if you want", [e(x) for x in c["them_better"]],
              f"{cfg['ours']} may suit you better if", [e(x) for x in c["us_better"]]),
    ]
    if faq:
        parts.append(section(faq_block(faq)))
    parts.append(cfg["offer"])
    parts.append("""</main>
<!-- chrome:footer -->
<!-- /chrome:footer -->
<script src="/data/plans.js"></script>
<script src="/js/plans-ui.js"></script>
<script src="/js/nav.js" defer></script>
</body>
</html>
""")
    html = "".join(parts)
    if fam == "nutrition":
        html = html.replace("<body>", '<body data-brand="nutrition">', 1)
    (ROOT / "compare" / f"{slug}.html").write_text(html, encoding="utf-8")
    return url


def main():
    data = json.loads((ROOT / "data" / "compare-more.json").read_text())
    for fam in ("totality", "nutrition"):
        for c in data.get(fam, []):
            print(build(fam, c, data["checked"]))


if __name__ == "__main__":
    main()
