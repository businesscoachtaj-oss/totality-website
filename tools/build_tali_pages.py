#!/usr/bin/env python3
"""Build the Tali HQ search pages and Tali HQ comparison pages.

Content lives in this file (SEARCH_PAGES) and in data/tali-compare.json (comparisons, with sources).
Run, then add the shared header and footer:

    python3 tools/build_tali_pages.py
    python3 tools/apply_chrome.py
    python3 tools/build_sitemap.py

Every Tali HQ fact here matches tali-hq.html. Competitor facts come only from their own pages,
listed as sources on each page with the date checked.
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://totality360.com.au"
APP = "https://talihq.com.au"

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

STYLE = """<style>
.cmp-table th[scope="row"] { width: 22%; }
.cmp-table td { width: 39%; }
.cmp-table thead th:nth-child(3) { color: #6C3483; }
.cmp-src { font-size: var(--fs-xs); color: var(--muted); word-break: break-word; }
.cmp-src a { text-decoration: underline; }
.thq-tag { display: inline-block; font-size: var(--fs-xs); font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: #6C3483; }
.thq-plans td, .thq-plans th { vertical-align: top; }
</style>"""

e = html.escape


def app_link(slug):
    return f"{APP}/?ref=site-{slug}"


def head(title, desc, url, crumbs, faq):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)]
    ld = [{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}]
    if faq:
        ld.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq],
        })
    lds = "\n".join(f'<script type="application/ld+json">\n{json.dumps(x, indent=2, ensure_ascii=False)}\n</script>' for x in ld)
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
{PIXEL}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Totality 360">
<meta property="og:locale" content="en_AU">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{url}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/og-image.png">
<link rel="icon" href="/favicon-96.png" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
<!-- chrome:head -->
<!-- /chrome:head -->
<link rel="stylesheet" href="/css/site.css">
{lds}
{STYLE}
<link rel="stylesheet" href="/css/hybrid.css?v=4">
</head>
<body>
<!-- chrome:header -->
<!-- /chrome:header -->
<main id="main">
"""


FOOT = """</main>
<!-- chrome:footer -->
<!-- /chrome:footer -->
<script src="/js/nav.js" defer></script>
</body>
</html>
"""


def hero(crumbs, h1, lead, note=None):
    trail = " / ".join(f'<a href="{u}">{e(n)}</a>' for n, u in crumbs[:-1]) + f" / {e(crumbs[-1][0])}"
    n = f'\n    <p class="small muted mt-4">{note}</p>' if note else ""
    return f"""<section class="page-hero">
  <div class="container">
    <nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>
    <h1>{e(h1)}</h1>
    <p class="lead">{lead}</p>{n}
  </div>
</section>
"""


def section(inner, tint=False):
    return f"""<section class="section{' section--tint' if tint else ''}">
  <div class="container">
{inner}
  </div>
</section>
"""


def prose(h2, paras=(), bullets=()):
    out = [f'    <div class="prose">', f'      <h2>{e(h2)}</h2>']
    out += [f"      <p>{p}</p>" for p in paras]
    if bullets:
        out.append('      <ul class="ticks">')
        out += [f"        <li>{b}</li>" for b in bullets]
        out.append("      </ul>")
    out.append("    </div>")
    return "\n".join(out)


def cards(left_title, left, right_title, right):
    li = lambda xs, cls: f'<ul class="ticks{cls}">' + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    return f"""<section class="section section--tint">
  <div class="container grid-2">
    <div class="card">
      <h2 class="h3">{e(left_title)}</h2>
      {li(left, '')}
    </div>
    <div class="card card--orange">
      <h2 class="h3">{e(right_title)}</h2>
      {li(right, ' ticks--orange')}
    </div>
  </div>
</section>
"""


PLANS = """    <h2>Plans and prices</h2>
    <p class="mt-4">Prices in Australian dollars. Every new account starts with a 7 day free trial of Tali HQ, and yearly plans are 15% off.</p>
    <div class="table-wrap">
      <table class="table thq-plans">
        <caption class="visually-hidden">Tali HQ plans</caption>
        <thead><tr><th scope="col">Plan</th><th scope="col">Price</th><th scope="col">What you get</th></tr></thead>
        <tbody>
          <tr><th scope="row">Free</th><td>A$0</td><td>Chat with Tali (250 messages a month), log food and training by telling her, a private journal she reads and remembers, and a Friday check-in on your goals.</td></tr>
          <tr><th scope="row">Tali HQ</th><td>A$19.99 a month</td><td>1,000 credits a month. Gmail or Outlook sorted with drafted replies, a morning brief, clients, leads and Stripe invoices, Google Calendar, web search with sources.</td></tr>
          <tr><th scope="row">Tali HQ Pro</th><td>A$39.99 a month</td><td>3,000 credits a month. Everything in Tali HQ, plus your own Tali email address, night school and Rules.</td></tr>
        </tbody>
      </table>
    </div>
    <p class="mt-4"><a class="text-link" href="/tali-hq.html#pricing">See the full plans</a></p>"""


def faq_block(faq):
    rows = "\n".join(f"        <details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    return f"""    <h2>Questions</h2>
      <div class="faq mt-4">
{rows}
      </div>"""


def offer(slug):
    return f"""<section class="section">
  <div class="container">
    <div class="offer">
      <p><strong>Try Tali HQ:</strong> start free with 250 messages a month, and every new account gets a 7 day free trial of Tali HQ.</p>
      <div class="btn-row">
        <a class="btn btn--white" href="{app_link(slug)}" target="_blank" rel="noopener" data-ev="tali_hq_open">Start free</a>
        <a class="btn btn--ghost-light" href="/tali-hq.html">See Tali HQ</a>
      </div>
    </div>
    <p class="mt-5"><a class="text-link" href="/compare/#tali-hq">Compare Tali HQ with other apps</a></p>
  </div>
</section>
"""


COMMON_FAQ = [
    ("Where do I get Tali HQ?", "It's live now as a web app at talihq.com.au and works on iPhone, Android and computer. On your phone, add it to your home screen and it works like any other app. The App Store and Google Play versions are coming soon."),
    ("Do I need Totality or Totality Nutrition?", "No. Tali HQ is its own app with its own sign-up. You don't need any other app to use it."),
    ("Who makes Tali HQ?", "Totality 360, an Australian software company."),
]

# ---------------------------------------------------------------- search pages
SEARCH_PAGES = [
    {
        "slug": "chatgpt-alternative-that-remembers",
        "title": "A ChatGPT alternative that remembers you | Tali HQ",
        "desc": "Tali HQ is an AI manager that remembers you. She keeps what she learns in a brain you can see and edit, and uses it every time you talk. Free plan, made in Australia.",
        "h1": "A ChatGPT alternative that remembers you",
        "lead": "Tali HQ is an AI manager for business and life from Totality 360, an Australian software company. She keeps what she learns about you in a brain you can see, and uses it every time you talk.",
        "body": [
            ("What she remembers", [
                "Tali is built around remembering you. She saves what matters as she goes, then brings it back when it's useful, so you don't have to repeat yourself.",
            ], [
                "Your business, your clients and the people in your life",
                "Your goals, and what you decided and why",
                "How you like things done",
                "What you write in your private journal",
            ]),
            ("You can see everything she keeps", [
                "Tali files what she learns into parts of a brain, a bit like yours does. Open the brain, tap a part and see the memories in it, and delete anything you don't want her to keep.",
                'Want a look first? <a href="/tali-hq.html#brain">Spin the demo brain</a> on the Tali HQ page.',
            ], []),
            ("What she does with it", [
                "Remembering is only useful if it changes what she does for you. On Tali HQ she uses what she knows to:",
            ], [
                "Write your morning brief: what came in, who needs a reply and what's on today",
                "Draft replies to your Gmail or Outlook, ready for you to send",
                "Check in on your goals every Friday",
                "Flag clients who have gone quiet and invoices that are overdue",
            ]),
            ("Nothing happens without your yes", [
                "Tali drafts, you decide. She never sends a message, an invoice or a booking until you approve it, and she never asks for your passwords.",
            ], []),
        ],
        "faq": [
            ("Is Tali HQ free?", "Yes. The Free plan is A$0 with 250 messages a month, a private journal and a Friday goals check-in. Paid plans are A$19.99 and A$39.99 a month, and every new account gets a 7 day free trial of Tali HQ."),
            ("Can I delete what Tali remembers?", "Yes. Open her brain, find the memory and delete it. You can see everything she keeps."),
            ("How is it different from ChatGPT?", "Tali HQ is built around running your week: she remembers you in a brain you can see, sorts your inbox, drafts replies and invoices, and checks in on your goals. ChatGPT is a general assistant. See the full comparison for details."),
        ],
        "related": [("Tali HQ and ChatGPT compared", "/compare/tali-hq-vs-chatgpt.html"), ("An AI assistant for small business in Australia", "/ai-assistant-small-business-australia.html")],
    },
    {
        "slug": "ai-assistant-small-business-australia",
        "title": "AI assistant for small business in Australia | Tali HQ",
        "desc": "Tali HQ is an AI assistant for Australian small businesses: morning brief, inbox sorted with drafted replies, clients and Stripe invoices, calendar. Priced in AUD, free plan.",
        "h1": "An AI assistant for small business in Australia",
        "lead": "Tali HQ runs the busy bits of a small business so you can do the work you're good at. Built in Australia by Totality 360, written in Australian English and priced in Australian dollars.",
        "body": [
            ("What she handles each day", [], [
                "<b>A morning brief</b> at the time you pick: what came in overnight, who needs a reply, what's on today and how the money looks",
                "<b>Your inbox sorted.</b> Connect Gmail or Outlook and she flags what needs you and drafts the reply",
                "<b>Clients, leads and invoices</b> in one place. Connect your own Stripe and she sends the invoice when you tap send, and marks it paid when your client pays",
                "<b>Your calendar.</b> She knows your week from Google Calendar and books into it when you approve",
                "<b>Follow-ups.</b> Health checks twice a day flag overdue invoices, quiet clients, new leads and drafts waiting on you",
                "<b>Web search with sources</b>, and a weekly journal of how the business is going",
            ]),
            ("Made for how Australian businesses work", [
                "Prices are in Australian dollars, with no conversion surprises. Tali writes in Australian English, and the people behind her are a small Australian software company you can actually reach.",
            ], []),
            ("You stay in charge", [
                "Tali drafts, you decide. She never sends a message, an invoice or a booking until you approve it, and she never asks for your passwords. You can see and delete anything she remembers about your business.",
            ], []),
            ("Hand her the front desk on Pro", [
                "Tali HQ Pro gives Tali her own email address. Give it to customers and she handles the enquiries, with one-tap replies. Pro also adds night school, where she studies your industry, and Rules, where she keeps watch for quiet clients and new leads.",
            ], []),
        ],
        "faq": [
            ("How much does Tali HQ cost?", "Free at A$0, Tali HQ at A$19.99 a month or Tali HQ Pro at A$39.99 a month, with 15% off yearly. Every new account starts with a 7 day free trial of Tali HQ."),
            ("Does Tali send emails or invoices on her own?", "No. She drafts them and nothing goes out until you tap yes."),
            ("Which email does it work with?", "Gmail and Outlook on the paid plans."),
        ],
        "related": [("An AI email assistant that drafts your replies", "/ai-email-assistant.html"), ("An AI invoice assistant with Stripe", "/ai-invoice-assistant.html")],
    },
    {
        "slug": "ai-email-assistant",
        "title": "AI email assistant for Gmail and Outlook that drafts replies | Tali HQ",
        "desc": "Connect Gmail or Outlook and Tali HQ sorts your inbox, flags what needs you and drafts the replies. Nothing is sent until you tap send. From A$19.99 a month, Australian made.",
        "h1": "An AI email assistant that sorts your inbox and drafts your replies",
        "lead": "Connect Gmail or Outlook to Tali HQ and she reads what comes in, flags what needs you, and has a reply drafted before you open it. You check it, tap send, and it goes from your own address.",
        "body": [
            ("How it works", [], [
                "<b>Sorted:</b> what needs you, what's just for your information, and what's junk",
                "<b>Drafted:</b> a reply for anything that needs one, written from what she knows about you and your business",
                "<b>Your call:</b> edit the draft or send it as is. It goes out from your Gmail or Outlook, so people see an address they know",
                "<b>Followed up:</b> she drafts follow-ups and check-ins with people who've gone quiet",
                "<b>In your brief:</b> every morning she tells you what came in and who is waiting on you",
            ]),
            ("Nothing goes out without your yes", [
                "Tali never sends an email on her own. Every reply waits for your tap.",
            ], []),
            ("Your own Tali address on Pro", [
                "On Tali HQ Pro, Tali gets her own email address you can give to customers. She drafts the replies to those enquiries too, and when you tap send they go from your connected Gmail or Outlook, or from Tali's address if you haven't connected one.",
            ], []),
        ],
        "faq": [
            ("Which plans include email?", "Gmail and Outlook sorting with drafted replies come with Tali HQ (A$19.99 a month) and Tali HQ Pro (A$39.99 a month). Every new account gets a 7 day free trial of Tali HQ."),
            ("Can Tali send emails without asking?", "No. She drafts, and nothing is sent until you tap send."),
            ("Does she need my email password?", "No. You connect your account with Google or Microsoft's own sign-in. Tali never asks for your passwords."),
        ],
        "related": [("An AI assistant for small business in Australia", "/ai-assistant-small-business-australia.html"), ("A ChatGPT alternative that remembers you", "/chatgpt-alternative-that-remembers.html")],
    },
    {
        "slug": "ai-invoice-assistant",
        "title": "AI invoice assistant with Stripe for small business | Tali HQ",
        "desc": "Tali HQ keeps your clients and invoices in one place, sends Stripe invoices when you tap send and marks them paid when your client pays. Australian made, priced in AUD.",
        "h1": "An AI invoice assistant that works with your Stripe",
        "lead": "Tali HQ keeps your clients, leads and invoices in one place. Connect the Stripe account you already have, and she sends the invoice when you tap send, then marks it paid when your client pays.",
        "body": [
            ("How it works", [], [
                "<b>Tell her what to bill.</b> Tali drafts the invoice for the right client",
                "<b>You tap send.</b> The invoice goes out through your own Stripe, and payment goes to your bank",
                "<b>It marks itself paid</b> when your client pays",
                "<b>She keeps watch.</b> Overdue invoices show up in your morning brief and health checks. On Pro, a Rule can draft the reminder for you to send",
            ]),
            ("Your Stripe, your money", [
                "You connect your existing Stripe account. Tali HQ never holds your money, and nothing is sent until you approve it.",
            ], []),
        ],
        "faq": [
            ("Which plans include invoices?", "Clients, leads and Stripe invoices come with Tali HQ (A$19.99 a month) and Tali HQ Pro (A$39.99 a month). Every new account gets a 7 day free trial of Tali HQ."),
            ("Do I need a Stripe account?", "Yes, to send invoices. You connect the Stripe account you already have."),
            ("Does Tali send invoices on her own?", "No. She drafts them and nothing is sent until you tap send."),
        ],
        "related": [("An AI assistant for small business in Australia", "/ai-assistant-small-business-australia.html"), ("An AI email assistant that drafts your replies", "/ai-email-assistant.html")],
    },
]


def build_search(p):
    slug = p["slug"]
    url = f"/{slug}.html"
    crumbs = [("Home", "/"), ("Tali HQ", "/tali-hq.html"), (p["h1"], url)]
    faq = p["faq"] + COMMON_FAQ
    out = [head(p["title"], p["desc"], url, crumbs, faq), hero(crumbs, p["h1"], p["lead"])]
    body = "\n".join(prose(h2, paras, bullets).replace('<div class="prose">', f'<div class="prose{" mt-6" if i else ""}">', 1)
                     for i, (h2, paras, bullets) in enumerate(p["body"]))
    out.append(section(body))
    out.append(section(PLANS, tint=True))
    rel = " &middot; ".join(f'<a class="text-link" href="{u}">{e(n)}</a>' for n, u in p["related"])
    out.append(section(faq_block(faq) + f'\n    <p class="mt-5"><b>Related:</b> {rel}</p>'))
    out.append(offer(slug))
    out.append(FOOT)
    (ROOT / f"{slug}.html").write_text("".join(out), encoding="utf-8")
    return url


# ---------------------------------------------------------------- comparison pages
ROWS = [
    ("Who it is for", "who"), ("Price", "price"), ("Free plan or trial", "free"), ("Remembers you", "memory"),
    ("Email", "email"), ("Calendar", "calendar"), ("Clients and invoices", "invoices"),
    ("Asks before acting", "approval"), ("Works for you unprompted", "proactive"), ("Apps", "apps"),
    ("Currency and maker", "currency"),
]
TALI = {}


def build_compare(c, checked):
    slug = c["slug"]
    url = f"/compare/{slug}.html"
    name = c["name"]
    crumbs = [("Home", "/"), ("Compare", "/compare/"), (f"Tali HQ and {name}", url)]
    rows = "\n".join(
        f'          <tr><th scope="row">{e(label)}</th><td>{e(c[k])}</td><td>{e(TALI[k])}</td></tr>' for label, k in ROWS
    )
    srcs = " ".join(f'<a href="{e(u)}" rel="nofollow noopener">{e(u)}</a>' for u in c["sources"])
    table = f"""    <div class="table-wrap">
      <table class="table cmp-table">
        <caption class="visually-hidden">{e(name)} and Tali HQ side by side</caption>
        <thead><tr><th scope="col">&nbsp;</th><th scope="col">{e(name)}</th><th scope="col">Tali HQ</th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p class="cmp-src mt-4">{e(name)} sources (checked {e(checked)}): {srcs}</p>"""
    faq = c.get("faq", []) + COMMON_FAQ[:1]
    out = [
        head(c["title"], c["desc"], url, crumbs, faq),
        hero(crumbs, c["h1"], e(c["lead"]), f"Checked {e(checked)}. Prices and features change, so check {e(name)}'s site before you decide."),
        section(table),
        cards(f"{name} may suit you better if you want", [e(x) for x in c["them_better"]],
              "Tali HQ may suit you better if", [e(x) for x in c["us_better"]]),
        section(faq_block(faq)),
        offer(slug),
        FOOT,
    ]
    (ROOT / "compare" / f"{slug}.html").write_text("".join(out), encoding="utf-8")
    return url


def main():
    built = [build_search(p) for p in SEARCH_PAGES]
    data_file = ROOT / "data" / "tali-compare.json"
    if data_file.exists():
        data = json.loads(data_file.read_text())
        TALI.update(data["tali"])
        built += [build_compare(c, data["checked"]) for c in data["pages"]]
    print("\n".join(built))


if __name__ == "__main__":
    main()
