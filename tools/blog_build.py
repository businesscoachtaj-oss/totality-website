#!/usr/bin/env python3
"""Normalise Totality Reports posts and rebuild the blog index cards.

Run after adding or editing a post:   python3 tools/blog_build.py

For every blog/posts/*.html it:
  * reads title (<h1>), category (post-badge class), date (JSON-LD datePublished),
    description (meta description)
  * rewrites the <head> SEO block: title, description, canonical, Open Graph,
    Twitter, Article + BreadcrumbList JSON-LD (author "Totality Reports")
  * rebuilds the post header: breadcrumbs, category link, title, date, reading time
  * names the sources section "Sources and references" (id="references")
  * replaces em and en dashes in visible text (Taj's copy rule), and the old
    "2 months on us" CTA wording
  * adds /js/track.js
Then it regenerates the cards in blog/index.html between
<!-- posts:start --> and <!-- posts:end -->, newest first.

The shared header/footer (<!-- chrome:... --> blocks) and <script>/<style> blocks are
never touched. Idempotent.
"""
import html
import json
import math
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "blog", "posts")
INDEX = os.path.join(ROOT, "blog", "index.html")
SITE = "https://totality360.com.au"
CATS = {"nutrition": "Nutrition", "training": "Training", "mindset": "Mindset", "business": "Business"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]

# ---------------------------------------------------------------- dashes

SPECIFIC = [
    ("Confirms the Strength Gains — and Exposes a Trust Gap", "Confirms the Strength Gains, and Exposes a Trust Gap"),
    ("Why this happens — the plain-English version", "Why this happens: the plain-English version"),
    ("applied automatically at checkout — no code needed.", "applied automatically at checkout. No code needed."),
    ("— referenced for supporting", ". Referenced for supporting"),
]
CTA_TEXT = [
    (re.compile(r'(class="post-cta-btn"[^>]*>)\s*(?:Start Totality free[^<]*|Try Totality free[^<]*)</a>'),
     r'\1Start your 7 day free trial</a>'),
    (re.compile(r'(class="post-cta-btn"[^>]*>)\s*Try Totality Nutrition free[^<]*</a>'),
     r'\1Try Totality Nutrition free</a>'),
]

PROTECT = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>|<!-- chrome:(\w+) -->.*?<!-- /chrome:\2 -->)", re.S)


def clean_text(s):
    for a, b in SPECIFIC:
        s = s.replace(a, b)
    s = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1-\2", s)          # 1–2 reps -> 1-2
    s = re.sub(r"(\s|\()[–—](\d)", r"\1-\2", s)               # –0.23 -> -0.23
    s = re.sub(r"\s*—\s*\n(\s*)", r",\n\1", s)                      # dash at line end
    s = re.sub(r"\s+[—–]\s+", ", ", s)                          # spaced dash
    s = re.sub(r"[—–]", ", ", s)                                # anything left
    s = s.replace("← ", "").replace(" →", "").replace("→", "")  # arrows on links
    return s


def clean_outside_protected(doc):
    out, last = [], 0
    for m in PROTECT.finditer(doc):
        out.append(clean_text(doc[last:m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(clean_text(doc[last:]))
    return "".join(out)

# ---------------------------------------------------------------- helpers


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def nice_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def reading_minutes(doc):
    m = re.search(r'<article class="post-body"[^>]*>(.*?)</article>', doc, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r'<div class="post-cta.*?</div>', "", body, flags=re.S)
    body = re.split(r'<h2[^>]*id="references"', body)[0]
    words = len(strip_tags(body).split())
    return max(1, math.ceil(words / 220))


def attr(s):
    return html.escape(s, quote=True)


def parse_post(doc, slug):
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", doc, re.S)
    title = re.sub(r"\s+", " ", strip_tags(h1.group(1))).strip()
    cat = re.search(r'post-badge badge-(\w+)', doc).group(1)
    iso = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', doc)
    if not iso:
        raise SystemExit(f"{slug}: no datePublished")
    desc = re.search(r'<meta name="description" content="([^"]*)"', doc)
    desc = html.unescape(desc.group(1)).strip() if desc else ""
    return {"slug": slug, "title": title, "cat": cat, "date": iso.group(1), "desc": desc}

# ---------------------------------------------------------------- head block


def head_block(p, minutes):
    url = f"{SITE}/blog/posts/{p['slug']}.html"
    full_title = f"{p['title']} | Totality Reports"
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": p["title"][:110],
        "description": p["desc"],
        "datePublished": p["date"],
        "dateModified": p["date"],
        "articleSection": CATS[p["cat"]],
        "timeRequired": f"PT{minutes}M",
        "inLanguage": "en-AU",
        "mainEntityOfPage": url,
        "url": url,
        "image": f"{SITE}/og-image.png",
        "author": {"@type": "Organization", "name": "Totality Reports", "url": f"{SITE}/blog/"},
        "publisher": {
            "@type": "Organization",
            "name": "Totality 360",
            "url": f"{SITE}/",
            "logo": {"@type": "ImageObject", "url": f"{SITE}/logo.png"},
        },
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Totality Reports", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": CATS[p["cat"]], "item": f"{SITE}/blog/#{p['cat']}"},
            {"@type": "ListItem", "position": 4, "name": p["title"], "item": url},
        ],
    }
    lines = [
        "<!-- seo:start (generated by tools/blog_build.py) -->",
        f"<title>{html.escape(full_title)}</title>",
        f'<meta name="description" content="{attr(p["desc"])}">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="article">',
        '<meta property="og:site_name" content="Totality 360">',
        '<meta property="og:locale" content="en_AU">',
        f'<meta property="og:title" content="{attr(full_title)}">',
        f'<meta property="og:description" content="{attr(p["desc"])}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{SITE}/og-image.png">',
        f'<meta property="article:published_time" content="{p["date"]}">',
        f'<meta property="article:section" content="{CATS[p["cat"]]}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{attr(full_title)}">',
        f'<meta name="twitter:description" content="{attr(p["desc"])}">',
        f'<meta name="twitter:image" content="{SITE}/og-image.png">',
        '<script type="application/ld+json">',
        json.dumps(article, indent=2, ensure_ascii=False),
        "</script>",
        '<script type="application/ld+json">',
        json.dumps(crumbs, indent=2, ensure_ascii=False),
        "</script>",
        "<!-- seo:end -->",
    ]
    return "\n".join(lines)


OLD_HEAD = [
    re.compile(r"<!-- seo:start.*?<!-- seo:end -->\n?", re.S),
    re.compile(r"<title>.*?</title>\n?", re.S),
    re.compile(r'<meta name="description"[^>]*>\n?'),
    re.compile(r'<link rel="canonical"[^>]*>\n?'),
    re.compile(r'<meta (?:property|name)="(?:og|twitter|article):[^"]*"[^>]*>\n?'),
    re.compile(r'<script type="application/ld\+json">.*?</script>\n?', re.S),
]


def header_block(p, minutes):
    cat, label = p["cat"], CATS[p["cat"]]
    return f"""<header class="post-header">
  <nav class="crumbs post-crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog/">Totality Reports</a> / <a href="/blog/#{cat}">{label}</a></nav>
  <div>
    <a class="post-badge badge-{cat}" href="/blog/#{cat}">{label}</a>
  </div>
  <h1>{html.escape(p['title'], quote=False)}</h1>
  <p class="post-byline"><time datetime="{p['date']}">{nice_date(p['date'])}</time> &nbsp;&middot;&nbsp; {minutes} min read &nbsp;&middot;&nbsp; Totality Reports</p>
</header>"""


def footer_nav(p):
    cat, label = p["cat"], CATS[p["cat"]]
    return f"""<div class="post-footer-nav">
  <a href="/blog/">All posts</a>
  <a href="/blog/#{cat}">More {label.lower()} posts</a>
</div>"""


POST_CSS = """
  /* blog_build.py: shared post header bits */
  .post-crumbs { font-size: 0.85rem; margin-bottom: 14px; }
  a.post-badge { text-decoration: none; }
  .post-footer-nav { display: flex; gap: 20px; flex-wrap: wrap; }
"""


def build_post(path):
    slug = os.path.basename(path)[:-5]
    doc = open(path, encoding="utf-8").read()
    doc = clean_outside_protected(doc)
    doc = re.sub(r'<meta name="robots" content="noindex">\n?', "", doc)  # left over from the template
    doc = re.sub(r"<!--\n  TOTALITY REPORTS POST TEMPLATE.*?-->\n", "", doc, flags=re.S)
    for rx, rep in CTA_TEXT:
        doc = rx.sub(rep, doc)
    doc = re.sub(r'(class="post-cta-btn")(?![^>]*data-track-placement)', r'\1 data-track-placement="blog_post_cta"', doc)
    p = parse_post(doc, slug)
    p["desc"] = clean_text(p["desc"])
    # the h1 must be cleaned before the header is rebuilt
    minutes = reading_minutes(doc)

    for rx in OLD_HEAD:
        doc = rx.sub("", doc)
    doc = re.sub(r'(<meta name="viewport"[^>]*>\n?)', lambda m: m.group(1).rstrip("\n") + "\n" + head_block(p, minutes) + "\n", doc, count=1)
    doc = re.sub(r'<header class="post-header">.*?</header>', lambda m: header_block(p, minutes), doc, count=1, flags=re.S)
    doc = re.sub(r'<div class="post-footer-nav">.*?</div>', lambda m: footer_nav(p), doc, count=1, flags=re.S)
    doc = re.sub(r'<h2[^>]*>\s*(?:Evidence|Sources &amp; References|Sources and references|References|Sources)\s*</h2>',
                 '<h2 id="references">Sources and references</h2>', doc, count=1)
    if "blog_build.py: shared post header" not in doc:
        doc = doc.replace("</style>", POST_CSS + "</style>", 1)
    doc = doc.replace('<html lang="en">', '<html lang="en-AU">', 1)
    if "/js/track.js" not in doc:
        doc = doc.replace("</body>", '<script src="/js/track.js" defer></script>\n</body>', 1)
    open(path, "w", encoding="utf-8").write(doc)
    p["minutes"] = minutes
    return p

# ---------------------------------------------------------------- index


def existing_excerpts(index_doc):
    out = {}
    for m in re.finditer(r'<a href="posts/([\w-]+)\.html" class="post-card".*?<p class="post-excerpt">(.*?)</p>', index_doc, re.S):
        out[m.group(1)] = re.sub(r"\s+", " ", m.group(2)).strip()
    return out


def card(p, excerpt):
    cat, label = p["cat"], CATS[p["cat"]]
    return f"""    <a href="posts/{p['slug']}.html" class="post-card" data-category="{cat}">
      <span class="post-badge badge-{cat}">{label}</span>
      <h3>{html.escape(p['title'], quote=False)}</h3>
      <p class="post-excerpt">{excerpt}</p>
      <div class="post-meta">
        <span><time datetime="{p['date']}">{nice_date(p['date'])}</time> &middot; {p['minutes']} min read</span>
        <span class="post-read-more">Read more</span>
      </div>
    </a>"""


def build_index(posts):
    doc = open(INDEX, encoding="utf-8").read()
    ex = existing_excerpts(doc)
    posts = sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)
    cards = "\n\n".join(card(p, clean_text(ex.get(p["slug"]) or html.escape(p["desc"], quote=False))) for p in posts)
    block = f"<!-- posts:start (generated by tools/blog_build.py, do not edit by hand) -->\n{cards}\n    <!-- posts:end -->"
    if "<!-- posts:start" in doc:
        doc = re.sub(r"<!-- posts:start.*?<!-- posts:end -->", lambda m: block, doc, count=1, flags=re.S)
    else:
        # First run: replace everything inside the grid up to the empty state.
        doc = re.sub(r'(<div class="blog-grid" id="blogGrid">\n).*?(\n\s*<div class="empty-state")',
                     lambda m: m.group(1) + "\n    " + block + "\n" + m.group(2), doc, count=1, flags=re.S)
    open(INDEX, "w", encoding="utf-8").write(doc)
    return posts


def main():
    files = sorted(f for f in os.listdir(POSTS) if f.endswith(".html"))
    posts = [build_post(os.path.join(POSTS, f)) for f in files]
    posts = build_index(posts)
    for p in posts:
        print(f"{p['date']}  {p['cat']:<9} {p['minutes']:>2} min  {p['slug']}")
    print(f"{len(posts)} posts")


if __name__ == "__main__":
    main()
