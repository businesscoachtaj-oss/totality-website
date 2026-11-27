#!/usr/bin/env python3
"""Builds site-map.html, the "Everything on this site" page for people (21 Nov 2026).

sitemap.xml is for search engines. This page is the same idea for a person: every part of
the site in one list, grouped the way the menu is. The long collections (exercises, foods,
books) are linked by their index page with a count, and everything else is listed page by page.

Lists that grow (blog posts, comparisons, how-to guides, nutrients) are read from the files,
so run this again after adding pages, then run tools/apply_chrome.py to fill the header and footer.

Usage: python3 tools/build_site_map_page.py
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent


def title_of(path: pathlib.Path) -> str:
    s = path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S) or re.search(r"<title>(.*?)</title>", s, re.S)
    t = re.sub(r"<[^>]+>", " ", m.group(1)) if m else path.stem
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def indexable(path: pathlib.Path) -> bool:
    head = path.read_text(encoding="utf-8", errors="ignore")[:8000]
    return not re.search(r'<meta name="robots" content="[^"]*noindex', head)


def count(folder: str) -> int:
    return len([p for p in (ROOT / folder).glob("*.html") if p.name != "index.html"])


# HIDDEN (25 Nov 2026, Taj): Tali HQ pages are off the site's listings for now. They stay live.
HIDDEN = {"tali-hq-vs-chatgpt.html", "tali-hq-vs-claude.html", "tali-hq-vs-copilot.html", "tali-hq-vs-gemini.html",
          "tali-hq-vs-lindy.html", "tali-hq-vs-notion-ai.html", "tali-hq-vs-reclaim.html",
          "why-tali-asks-before-sending.html", "tali-night-school.html", "tali-morning-brief.html", "how-talis-brain-works.html"}


def listing(folder: str, skip=("index.html",)):
    out = []
    for p in sorted((ROOT / folder).glob("*.html")):
        if p.name in skip or p.name in HIDDEN or not indexable(p):
            continue
        out.append((f"/{folder}/{p.name}", title_of(p)))
    return sorted(out, key=lambda x: x[1].lower())


def guides():
    # HIDDEN (25 Nov 2026, Taj): Tali HQ is off the site's navigation and listings for now.
    order = ["totality-owner", "totality-trainer", "totality-client", "nutrition", "training"]
    out = []
    for k in order:
        cfg = ROOT / "_help-src" / k / "guide.json"
        if cfg.exists():
            c = json.loads(cfg.read_text())
            out.append((f"/help/{k}/", f'{c["title"]} ({len(c["pages"])} pages)'))
    return out


def group(title, links, note=None, cls=""):
    lis = "".join(f'<li><a href="{h}">{html.escape(t)}</a></li>' for h, t in links)
    n = f'<p class="sm-note">{html.escape(note)}</p>' if note else ""
    return f'<section class="sm-group {cls}"><h3>{html.escape(title)}</h3>{n}<ul>{lis}</ul></section>'


def build() -> str:
    apps = [
        group("Totality", [
            ("/totality.html", "Totality overview"), ("/features.html", "Every Totality feature"),
            ("/for-pts.html", "For personal trainers"), ("/for-gyms.html", "For studios and gyms"),
            ("/for-allied-health.html", "For allied health and clinics"), ("/get-totality.html", "Get Totality: App Store, Google Play and web"),
        ]),
        group("Totality Nutrition", [
            ("/nutrition.html", "Totality Nutrition overview"), ("/nutrition-features.html", "Every Nutrition feature"),
            ("/nutrition-teams.html", "Nutrition for teams and workplaces"), ("/get-nutrition.html", "Get Totality Nutrition"),
        ]),
        group("Totality Training", [
            ("/training.html", "Totality Training overview"), ("/training.html#features", "What it does"),
            ("/training.html#pricing", "Plans and the Nutrition bundle"), ("/training-teams.html", "Training for teams and workplaces"), ("/get-training.html", "Get Totality Training"),
        ]),
        group("Tali AI and prices", [
            ("/tali-ai.html", "Tali AI in the apps"), ("/pricing.html", "Pricing for every app"),
            ("/pricing.html#training", "Totality Training plans"), ("/whats-new.html", "What's new"),
        ]),
    ]
    tools = [
        group("Calculators and guides", [
            ("/calculator.html", "Calorie and macro calculator"), ("/commission-calculator.html", "Commission savings calculator"),
            ("/resources.html", "Free guides for personal trainers"),
        ]),
        group("Libraries", [
            ("/exercises/", "Exercise library (750+ exercises)"),
            ("/foods/", "Food facts for Australian foods"),
            ("/nutrients/", f"Nutrients ({count('nutrients')} guides)"),
        ]),
        group("Nutrients", [(h, t.split(":")[0]) for h, t in listing("nutrients")], cls="sm-wide"),
    ]
    blog = [group("Totality Reports", [("/blog/", "All reports")] + listing("blog/posts"), cls="sm-wide")]
    compare = [group("Compare", [("/compare/", "All comparisons")] + listing("compare"), cls="sm-wide")]
    dev = [
        group("Developers", [
            ("/api", "Exercise API"), ("/api#websites", "Exercise widget for websites"), ("/api-terms.html", "API and widget terms"),
            ("/sign-in-with-totality.html", "Sign in with Totality"), ("/claude.html", "Tali in Claude"), ("https://talihq.com.au/brain", "Tali Brain licence for software companies"),
        ]),
        group("Partners", [
            ("/affiliates.html", "Become an affiliate"), ("/online-training.html", "Online training with Taj"),
            ("/skool-tools/", "Tools for Skool owners"), ("/links.html", "Our links page"),
        ]),
    ]
    helps = [
        group("How to use", [("/help/", "All how-to guides")] + guides()),
        group("Answers and support", [
            ("/help.html", "Quick answers"), ("/faq.html", "FAQ"), ("/support.html", "Support"), ("/security.html", "Security and your data"),
        ]),
        group("Policies", [
            ("/privacy.html", "Privacy policy"), ("/terms.html", "Terms"), ("/refund.html", "Refund policy"),
            ("/delete-account.html", "Delete your account"),
        ]),
    ]
    logins = [group("Open an app", [
        ("https://totalityapp.com.au", "Totality web app"), ("https://totalitynutrition.com.au", "Totality Nutrition web app"),
        ("https://totality-training.vercel.app", "Totality Training web app"),
    ])]

    def block(anchor, heading, groups):
        return f'<section class="section section--tight" id="{anchor}"><div class="container"><h2>{heading}</h2><div class="sm-grid">{"".join(groups)}</div></div></section>'

    body = "".join([
        block("apps", "The apps", apps + logins),
        block("free", "Free tools and libraries", tools),
        block("reports", "The blog", blog),
        block("compare", "Comparisons", compare),
        block("developers", "Developers and partners", dev),
        block("help", "Help and policies", helps),
    ])
    old = (ROOT / "site-map.html").read_text(encoding="utf-8") if (ROOT / "site-map.html").exists() else ""

    def keep(name):
        m = re.search(rf"<!-- chrome:{name} -->.*?<!-- /chrome:{name} -->", old, re.S)
        return m.group(0) if m else f"<!-- chrome:{name} -->\n<!-- /chrome:{name} -->"

    return f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Everything on this site | Totality 360</title>
<meta name="description" content="Every page on totality360.com.au in one list: the three apps, pricing, free tools, the exercise and food libraries, the blog, comparisons, developer pages, how-to guides and support.">
<link rel="canonical" href="https://totality360.com.au/site-map.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Totality 360">
<meta property="og:locale" content="en_AU">
<meta property="og:title" content="Everything on this site | Totality 360">
<meta property="og:description" content="Every page on totality360.com.au in one list.">
<meta property="og:url" content="https://totality360.com.au/site-map.html">
<meta property="og:image" content="https://totality360.com.au/og-image.png">
<link rel="icon" href="/favicon-96.png" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
{keep("head")}
<link rel="stylesheet" href="/css/site.css">
<style>
  .sm-jump {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: var(--s-4); }}
  .sm-jump a {{ padding: 8px 14px; border-radius: 999px; border: 1.5px solid var(--line, #E6E4E1); background: #fff; font-weight: 700; font-size: var(--fs-sm); text-decoration: none; color: var(--ink); }}
  .sm-jump a:hover {{ border-color: var(--orange); }}
  .sm-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--s-5) var(--s-6); margin-top: var(--s-4); }}
  .sm-group h3 {{ font-size: var(--fs-md, 1.05rem); margin-bottom: var(--s-2); }}
  .sm-group ul {{ list-style: none; display: grid; gap: 7px; padding: 0; margin: 0; }}
  .sm-group a {{ color: var(--ink); text-decoration: none; border-bottom: 1px solid var(--line, #E6E4E1); }}
  .sm-group a:hover {{ color: var(--orange-700, #C46800); border-color: var(--orange); }}
  .sm-wide {{ grid-column: 1 / -1; }}
  .sm-wide ul {{ grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 7px var(--s-6); }}
  .sm-note {{ color: var(--muted, #62605D); font-size: var(--fs-sm); margin-bottom: var(--s-2); }}
</style>
</head>
<body class="reading">
{keep("header")}
<main id="main">
  <section class="page-hero">
    <div class="container">
      <p class="crumbs"><a href="/">Home</a> / Everything on this site</p>
      <h1>Everything on this site</h1>
      <p class="lead">Every part of totality360.com.au in one list. The big libraries are linked by their front page, and everything else is listed page by page.</p>
      <nav class="sm-jump" aria-label="Jump to a section">
        <a href="#apps">The apps</a><a href="#free">Free tools</a><a href="#reports">The blog</a><a href="#compare">Comparisons</a><a href="#developers">Developers and partners</a><a href="#help">Help and policies</a>
      </nav>
    </div>
  </section>
  {body}
</main>
{keep("footer")}
<script src="/js/nav.js" defer></script>
<script src="/js/track.js" defer></script>
</body>
</html>
'''


if __name__ == "__main__":
    out = build()
    (ROOT / "site-map.html").write_text(out, encoding="utf-8")
    print(f"site-map.html written, {out.count('<li>')} links")
