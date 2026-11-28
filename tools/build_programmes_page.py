#!/usr/bin/env python3
"""Builds programmes.html, the programme shop (28 Nov 2026), from data/programmes.json.

Each programme is a zip of PDFs and spreadsheets (every version: days a week x level), sold for
A$29.99 through a Stripe payment link. After paying, Stripe sends the buyer to
/programmes/thanks.html, which asks the guide-delivery edge function (Livewell Supabase) for a
download link. The same function emails a 7 day link from the Stripe webhook.

The shared header and footer are filled in afterwards by tools/apply_chrome.py.

Usage: python3 tools/build_programmes_page.py && python3 tools/apply_chrome.py programmes.html
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "programmes.json").read_text())
URL = "https://totality360.com.au/programmes.html"
UPDATED = ("2026-11-28", "28 November 2026")
e = html.escape

PRICE = DATA["price"]                       # "A$29.99"
AMOUNT = PRICE.replace("A$", "")
ITEMS = [i for g in DATA["groups"] for i in g["items"]]
VERSIONS = sum(i["versions"] for i in ITEMS)

TITLE = "Training programmes to download: PDFs and spreadsheets"
DESC = (f"{len(ITEMS)} programmes from Totality Training as PDFs and spreadsheets. Each comes with every "
        f"version, 2 to 6 days a week at three levels. {PRICE} each, ready to download as soon as you pay.")

PIXEL = """<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '3550080485153029');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=3550080485153029&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->"""

FAQ = [
    ("How do I get my programme?",
     "Pay with Stripe and you come straight back to a page with your download button. We also email you a "
     "link that works for 7 days. Save the zip to your phone, tablet or computer once it finishes."),
    ("What is in the zip?",
     "Two folders, PDF and Spreadsheets, with one PDF and one spreadsheet for every version of that programme. "
     "The file names say which version is which, for example full-body-3-intermediate is 3 days a week at "
     "Intermediate."),
    ("Which version should I use?",
     "You get them all, so start with the days you can train most weeks. Beginner suits you if you are new to "
     "lifting or coming back after a long break. You can move to another version later without buying again."),
    ("How long does each one run?",
     "8 weeks at Beginner and Advanced, and 10 weeks at Intermediate. Each runs in 2 or 3 blocks and finishes "
     "with a lighter week, so you recover before your next programme."),
    ("Do I need a gym?",
     "Each card says the kit. The home programmes need dumbbells and a bench, or nothing at all. Every exercise "
     "also has two swaps, often with less kit, so you can work around a busy gym or a missing machine."),
    ("Will the spreadsheets work on my phone or Mac?",
     "Yes. They open in Excel, Google Sheets and Numbers. On an iPhone, open the zip in the Files app first. "
     "The PDFs open on any phone, tablet or computer, and print on A4."),
    ("I lost my download link",
     "Reply to the email we sent you, or write to admintotality@gmail.com from the email you paid with, and we "
     "will send you a new link."),
    ("Can I get a refund?",
     "The download is yours as soon as you pay, so purchases are generally non-refundable. If a file does not "
     "work or you were charged twice, email admintotality@gmail.com and we will fix it or refund you. Nothing "
     "here limits your rights under the Australian Consumer Law."),
    ("Who sells them?",
     "Totality 360 Pty Ltd (ABN 58 698 902 975), the team behind Totality Training. Payments are taken by Stripe "
     "in Australian dollars."),
]


def card(i):
    days = e(i["days"])
    return f"""      <article class="card card--accent prog" id="{e(i['key'])}">
        <p class="prog-tags"><span class="pill">{e(i['kit'])}</span><span class="pill pill--quiet">{i['versions']} versions</span></p>
        <h3>{e(i['name'])}</h3>
        <p>{e(i['blurb'])}</p>
        <p class="card-meta">{days} · Beginner, Intermediate and Advanced</p>
        <div class="card-foot prog-buy">
          <span class="prog-price">{e(PRICE)}</span>
          <a class="btn btn--training" href="{e(i['link'])}" rel="noopener" aria-label="Buy {e(i['name'])} for {e(PRICE)}">Buy</a>
        </div>
      </article>"""


def group(g):
    cards = "\n".join(card(i) for i in g["items"])
    return f"""<section class="section{' section--tint' if g['id'] == 'home' else ''}" id="{e(g['id'])}">
  <div class="container">
    <div class="section-head">
      <h2>{e(g['title'])}</h2>
      <p class="section-sub">{e(g['sub'])}</p>
    </div>
    <div class="grid-3">
{cards}
    </div>
  </div>
</section>"""


def schema():
    crumbs = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://totality360.com.au/"},
            {"@type": "ListItem", "position": 2, "name": "Totality Training", "item": "https://totality360.com.au/training.html"},
            {"@type": "ListItem", "position": 3, "name": "Programmes", "item": URL},
        ],
    }
    products = {
        "@context": "https://schema.org", "@type": "ItemList", "name": "Totality Training programmes",
        "numberOfItems": len(ITEMS),
        "itemListElement": [
            {"@type": "ListItem", "position": n + 1, "item": {
                "@type": "Product", "name": f"{i['name']} programme (PDF and spreadsheet)",
                "description": f"{i['blurb']} {i['versions']} versions, {i['days']}, at Beginner, Intermediate and Advanced.",
                "brand": {"@type": "Brand", "name": "Totality Training"},
                "image": "https://totality360.com.au/img/programmes/full-body-cover.webp",
                "offers": {"@type": "Offer", "price": AMOUNT, "priceCurrency": "AUD",
                           "availability": "https://schema.org/InStock", "url": f"{URL}#{i['key']}"},
            }} for n, i in enumerate(ITEMS)
        ],
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
    }
    return "\n".join(f'<script type="application/ld+json">\n{json.dumps(s, indent=1, ensure_ascii=False)}\n</script>' for s in (crumbs, products, faq))


def page():
    faq = "\n".join(f"      <details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)
    groups = "\n\n".join(group(g) for g in DATA["groups"])
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
{PIXEL}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(TITLE)}</title>
<meta name="description" content="{e(DESC)}">
<link rel="canonical" href="{URL}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Totality 360">
<meta property="og:locale" content="en_AU">
<meta property="og:title" content="{e(TITLE)}">
<meta property="og:description" content="{e(DESC)}">
<meta property="og:url" content="{URL}">
<meta property="og:image" content="https://totality360.com.au/img/programmes/full-body-cover.webp">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(TITLE)}">
<meta name="twitter:description" content="{e(DESC)}">
<meta name="twitter:image" content="https://totality360.com.au/img/programmes/full-body-cover.webp">
<link rel="icon" href="/favicon-96.png" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
<!-- Built by tools/build_programmes_page.py from data/programmes.json. Edit those, not this file. -->
<!-- chrome:head -->
<!-- /chrome:head -->
<link rel="stylesheet" href="/css/site.css">
{schema()}
<style>
/* Training red for this page */
body[data-brand="training"] {{ --accent: #D92B2B; --accent-strong: #D92B2B; --accent-ink: #B32020; --accent-tint: #FCEBEA; --accent-tint-2: #F5C9C6; }}
body[data-brand="training"] p.kicker {{ color: #B32020 !important; }}
.pg-hero {{ display: grid; grid-template-columns: 1fr 1.05fr; gap: var(--s-7); align-items: center; }}
.pg-hero > * {{ min-width: 0; }}
.pg-hero h1 {{ max-width: 16ch; }}
.pg-facts {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: var(--s-5); padding: 0; list-style: none; }}
.pg-facts li {{ padding: 8px 12px; border-radius: 12px; background: #fff; border: 1.5px solid var(--line); font-weight: 700; font-size: var(--fs-sm); }}
.pg-shot {{ margin: 0; position: relative; }}
.pg-shot img {{ display: block; width: 100%; height: auto; border-radius: 10px; box-shadow: 0 18px 44px rgba(39,38,38,0.20); border: 1px solid var(--line); }}
.pg-shot .pg-back {{ width: 78%; }}
.pg-shot .pg-front {{ width: 78%; margin: -46% 0 0 auto; position: relative; }}
.pg-peek {{ display: grid; gap: var(--s-5); grid-template-columns: repeat(3, minmax(0, 1fr)); }}
.pg-peek figure {{ margin: 0; min-width: 0; }}
.pg-peek img {{ display: block; width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--line); box-shadow: var(--shadow); }}
.pg-peek figcaption {{ margin-top: var(--s-3); font-size: var(--fs-sm); color: var(--ink-2); }}
.pg-peek figcaption b {{ display: block; color: var(--ink); }}
.prog h3 {{ font-size: 1.25rem; }}
.prog-tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
.prog .pill {{ background: var(--accent-tint); color: var(--accent-ink); padding: 6px 10px; border-radius: 999px; }}
.prog .pill--quiet {{ background: var(--surface); color: var(--ink-2); }}
.prog-buy {{ display: flex; align-items: center; justify-content: space-between; gap: var(--s-3); }}
.prog-price {{ font-family: var(--font-display); font-weight: 700; font-size: 1.25rem; }}
.prog-buy .btn {{ min-width: 96px; }}
.pg-jump {{ display: flex; flex-wrap: wrap; gap: var(--s-3); margin-top: var(--s-5); }}
.pg-app {{ display: grid; grid-template-columns: 1.3fr 1fr; gap: var(--s-6); align-items: center; }}
.pg-app > * {{ min-width: 0; }}
.pg-app img {{ display: block; width: 100%; max-width: 260px; height: auto; margin-inline: auto; border-radius: 20px; box-shadow: var(--shadow-lg); }}
@media (max-width: 960px) {{ .pg-peek {{ grid-template-columns: 1fr 1fr; }} }}
@media (max-width: 860px) {{ .pg-hero, .pg-app {{ grid-template-columns: 1fr; gap: var(--s-6); }} }}
@media (max-width: 600px) {{ .pg-peek {{ grid-template-columns: 1fr; }} }}
</style>
<link rel="stylesheet" href="/css/hybrid.css?v=5">
</head>
<body data-brand="training">
<!-- chrome:header -->
<!-- /chrome:header -->
<main id="main">
<section class="page-hero page-hero--tint">
  <div class="container pg-hero">
    <div>
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/training.html">Totality Training</a> / Programmes</nav>
      <p class="kicker">Totality Training programmes</p>
      <h1>Programmes to print, or track in a spreadsheet</h1>
      <p class="lead">The programmes from Totality Training as PDFs and spreadsheets you keep. Each one comes with every version, from 2 to 6 days a week at Beginner, Intermediate and Advanced. {e(PRICE)} each, paid once.</p>
      <ul class="pg-facts">
        <li>{len(ITEMS)} programmes</li>
        <li>{VERSIONS} versions in all</li>
        <li>Two swaps for every exercise</li>
      </ul>
      <div class="btn-row">
        <a class="btn btn--training btn--lg" href="#gym">Pick a programme</a>
        <a class="btn btn--ghost" href="/training.html">Or follow them in the app</a>
      </div>
      <p class="small muted mt-5">Last updated <time datetime="{UPDATED[0]}">{UPDATED[1]}</time></p>
    </div>
    <figure class="pg-shot">
      <img class="pg-back" src="/img/programmes/full-body-cover.webp" alt="Cover of the Full Body programme PDF: 3 days a week, Intermediate, 10 weeks" width="1287" height="909">
      <img class="pg-front" src="/img/programmes/full-body-week-1.webp" alt="Week 1 of the Full Body PDF, with sets, reps, rest, two swaps and a note for each exercise" width="1287" height="909">
    </figure>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <h2>What you get</h2>
      <p class="section-sub">One zip per programme, ready to download as soon as you pay.</p>
    </div>
    <div class="grid-3">
      <article class="card"><h3>Every version</h3><p>The zip has every version of that programme. Upper Lower, for example, has 15: 2, 3, 4, 5 and 6 days a week at each of the three levels.</p></article>
      <article class="card"><h3>A PDF for each version</h3><p>Week by week tables with sets, reps, rest, two swaps for every exercise and a coaching note for each one. Plus your week at a glance, how the blocks run, how to progress and how to warm up.</p></article>
      <article class="card"><h3>A spreadsheet for each version</h3><p>Every week on its own tab. Pick your swap from a drop down, write in your weights and reps, and the Progress tab shows your heaviest weight each week. Opens in Excel, Google Sheets or Numbers.</p></article>
      <article class="card"><h3>Blocks that change</h3><p>8 weeks at Beginner and Advanced, 10 at Intermediate, in 2 or 3 blocks with a lighter week at the end. In the second half most exercises change to a different variation, and the staple lifts stay and get heavier.</p></article>
      <article class="card"><h3>Volume checked</h3><p>We checked the weekly sets for each muscle in every version against the research on training volume, and set them for each level, with sessions kept to a sensible length.</p></article>
      <article class="card"><h3>Yours to keep</h3><p>Paid once, no subscription. We also email you a download link that works for 7 days, so you can get it on another device.</p></article>
    </div>
  </div>
</section>

<section class="section section--tint">
  <div class="container">
    <div class="section-head">
      <h2>See inside</h2>
      <p class="section-sub">Real pages from the Full Body PDF, 3 days a week at Intermediate.</p>
    </div>
    <div class="pg-peek">
      <figure><img src="/img/programmes/full-body-cover.webp" alt="The cover, with days a week, weeks, workout length and kit" width="1287" height="909" loading="lazy"><figcaption><b>The cover</b>Days a week, how many weeks, how long a workout takes and the kit you need.</figcaption></figure>
      <figure><img src="/img/programmes/full-body-how-to.webp" alt="The how to use it page: warm up, swaps, reading the tables and the spreadsheet" width="1287" height="909" loading="lazy"><figcaption><b>How to use it</b>Warming up, picking a swap, reading the tables and tracking in the spreadsheet.</figcaption></figure>
      <figure><img src="/img/programmes/full-body-week-1.webp" alt="Week 1 with each exercise, sets, reps, rest, two swaps and a note" width="1287" height="909" loading="lazy"><figcaption><b>Every week</b>Each workout with sets, reps, rest, two swaps and a note on how to do it.</figcaption></figure>
    </div>
  </div>
</section>

<section class="section section--tight" id="shop">
  <div class="container">
    <div class="section-head">
      <h2>Pick your programme</h2>
      <p class="section-sub">{e(PRICE)} each. Checkout is with Stripe, and you come straight back here to download.</p>
    </div>
    <nav class="pg-jump" aria-label="Programme groups">
{chr(10).join(f'      <a class="btn btn--ghost btn--sm" href="#{e(g["id"])}">{e(g["title"])}</a>' for g in DATA["groups"])}
    </nav>
  </div>
</section>

{groups}

<section class="section section--accent">
  <div class="container pg-app">
    <div>
      <h2>Rather train from your phone?</h2>
      <p class="section-sub">These programmes are also in Totality Training, which fills in your weights and tells you when to go up. Strength Foundations and the Health Guidelines programmes are free on its Free plan, and the rest come with a Training plan.</p>
      <div class="btn-row mt-5">
        <a class="btn btn--training" href="/get-training.html">Get Totality Training</a>
        <a class="btn btn--ghost" href="/training.html#pricing">See Training plans</a>
      </div>
    </div>
    <img src="/img/app/tr_programme.webp" alt="A programme in the Totality Training app" width="585" height="1266" loading="lazy">
  </div>
</section>

<section class="section">
  <div class="container container--narrow">
    <div class="section-head">
      <h2>Questions</h2>
    </div>
    <div class="faq">
{faq}
    </div>
    <p class="small muted mt-6">If you have an injury or a health condition, check with your doctor or physio before you start, and stop any exercise that causes sharp pain.</p>
  </div>
</section>
</main>
<!-- chrome:footer -->
<!-- /chrome:footer -->
<script src="/js/nav.js" defer></script>
</body>
</html>
"""


if __name__ == "__main__":
    out = ROOT / "programmes.html"
    out.write_text(page(), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}: {len(ITEMS)} programmes, {VERSIONS} versions")
