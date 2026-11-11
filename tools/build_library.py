#!/usr/bin/env python3
"""Build Tali's library: /library/ (her bookcase) and one page per book.

The books, her notes and the free first page come from Tali HQ (public functions library_shelf,
library_book and library_preview). A copy is kept in data/tali-library.json so the pages can be
rebuilt offline.

    python3 tools/build_library.py --fetch     (refresh data/tali-library.json from Tali HQ, then build)
    python3 tools/build_library.py             (build from the saved copy)
    python3 tools/apply_chrome.py
    python3 tools/build_sitemap.py

Rules the pages keep:
  * Every book stays on the shelf for good. Finished books move to the top shelf and open to read.
  * Only finished books can be read, and only after an email (the server checks both).
  * One page of each finished book is on the page itself, so the book's own words are there to find.
  * The book text is shown as written. Our own words follow the house style (no dashes).
"""
import hashlib
import html
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://totality360.com.au"
APP = "https://talihq.com.au"
SUPA = "https://jbyzblwrywgxilhmfyjt.supabase.co"
KEY = "sb_publishable_6boNZk1eRN8-7Z4PIbxB3w_n4VDXf51"   # the app's public key, the same one the web app ships with
DATA = ROOT / "data" / "tali-library.json"
OUT = ROOT / "library"
BAKED_NOTES = 60      # notes written into the page; the rest load when the reader asks
SHOWN_NOTES = 6
PALETTE = ["#C6F08A", "#FFC978", "#6FC3F7", "#B9A6FF", "#A893F5", "#7FE0B0", "#F7A6C8"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

e = html.escape


# ---------- data ----------

def rpc(name, body=None):
    req = urllib.request.Request(
        f"{SUPA}/rest/v1/rpc/{name}", data=json.dumps(body or {}).encode(),
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def fetch():
    shelf = rpc("library_shelf")
    if not isinstance(shelf, list) or not shelf:
        raise SystemExit("library_shelf returned nothing, leaving the saved copy alone")
    books = []
    for s in shelf:
        detail = rpc("library_book", {"p_book": s["id"]}) or {}
        notes = [{"n": n.get("n"), "text": n.get("text", "")} for n in (detail.get("notes") or [])][:BAKED_NOTES]
        preview = []
        if s.get("state") == "finished":
            preview = [{"n": p.get("n"), "text": p.get("text", "")} for p in (rpc("library_preview", {"p_book": s["id"]}) or [])]
        books.append({
            "id": s["id"], "state": s.get("state"), "title": s.get("title"), "author": s.get("author"),
            "subject": s.get("subject"), "lessons": s.get("lessons") or 0, "studied": s.get("studied") or 0,
            "passages": s.get("passages") or 0, "source_url": s.get("source_url"),
            "last_read_at": sydney_day(s.get("last_read_at") or ""), "licence_note": s.get("licence_note"),
            "notes": notes, "preview": preview,
        })
    old = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {}
    if old.get("books") == books:
        return
    import datetime
    DATA.write_text(json.dumps({"fetched_at": datetime.date.today().isoformat(), "books": books},
                               indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------- helpers ----------

def sydney_day(stamp):
    """The day in Sydney, so a book finished on the morning of the 11th is not stamped the 10th."""
    try:
        import datetime, zoneinfo
        t = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return t.astimezone(zoneinfo.ZoneInfo("Australia/Sydney")).date().isoformat()
    except Exception:
        return stamp[:10]


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def h(book, salt, lo, hi):
    v = int(hashlib.md5((book["id"] + salt).encode()).hexdigest()[:6], 16)
    return lo + v % (hi - lo + 1)


def colour(book):
    return PALETTE[h(book, "c", 0, len(PALETTE) - 1)]


def finished(book):
    return book.get("state") == "finished"


def pct(book):
    if finished(book):
        return 100
    total = book.get("passages") or 0
    return max(1, min(99, round(100 * (book.get("studied") or 0) / total))) if total else 0


def nice_date(iso):
    try:
        y, m, d = [int(x) for x in iso[:10].split("-")]
        return f"{d} {MONTHS[m - 1]} {y}"
    except Exception:
        return ""


def paragraphs(text):
    """Book text arrives hard wrapped. Join the lines of each paragraph, keep the words as written."""
    out = []
    for block in re.split(r"\n\s*\n", text.replace("\r", "")):
        line = re.sub(r"\s+", " ", block).strip()
        if not line or line.lower().startswith("produced by"):
            continue
        out.append(re.sub(r"_([^_]+)_", r"<em>\1</em>", e(line, quote=False)))
    return out


# ---------- shared page parts ----------

STYLE = """<style>
    /* Tali's library (11 Nov 2026) */
    .lib-hero { background: var(--thq-deep); color: #fff; }
    .lib-hero__in { max-width: 1080px; margin: 0 auto; padding: var(--s-8) var(--gutter); display: grid; grid-template-columns: 1fr auto; gap: var(--s-6); align-items: center; }
    .lib-hero h1 { font-family: var(--font-display); font-weight: 800; letter-spacing: -0.03em; line-height: 1.05; font-size: clamp(2.2rem, 5vw, 3.2rem); margin: 0 0 var(--s-3); text-wrap: balance; }
    .lib-hero p { color: rgba(255,255,255,.86); font-size: 1.125rem; max-width: 36em; margin: 0; }
    .lib-hero img { width: 170px; height: auto; }
    .lib-hero .lib-back { display: inline-block; margin-bottom: var(--s-3); color: rgba(255,255,255,.8); font-weight: 700; font-size: .9rem; }
    .lib-stats { display: flex; gap: var(--s-5); flex-wrap: wrap; margin-top: var(--s-5); }
    .lib-stats b { display: block; font-family: var(--font-display); font-size: 1.9rem; line-height: 1; }
    .lib-stats span { font-size: .85rem; color: rgba(255,255,255,.75); }
    .lib-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s-4); }
    .lib-book { display: flex; gap: var(--s-4); background: #fff; border-radius: var(--radius-lg); padding: var(--s-4); box-shadow: 0 1px 2px rgba(20,16,51,.06), 0 10px 26px rgba(20,16,51,.10); border: 1px solid rgba(20,16,51,.06); text-decoration: none; color: var(--ink); }
    .lib-spine { flex: none; width: 54px; height: 82px; border-radius: 6px; box-shadow: inset -6px 0 0 rgba(0,0,0,.12), 0 6px 14px rgba(20,16,51,.22); }
    .lib-book h3 { margin: 0 0 2px; font-family: var(--font-display); font-size: 1.12rem; line-height: 1.2; }
    .lib-book small { color: var(--ink-2); display: block; }
    .lib-tag { display: inline-block; margin-top: 8px; font-size: .78rem; font-weight: 800; padding: 3px 10px; border-radius: 999px; }
    .lib-tag--open { background: #E4F7EC; color: #14713F; }
    .lib-tag--reading { background: #EFEAFB; color: #5B3FA8; }
    .lib-bar { height: 6px; border-radius: 3px; background: #ECE8F6; margin-top: 10px; overflow: hidden; }
    .lib-bar i { display: block; height: 6px; border-radius: 3px; }
    .lib-two { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: var(--s-6); align-items: start; }
    .lib-two > * { min-width: 0; }
    .lib-paper { background: #F3ECDD; color: #2A2340; border-radius: var(--radius-lg); padding: clamp(20px, 4vw, 44px); box-shadow: 0 14px 40px rgba(20,16,51,.16); font-family: Georgia, 'Times New Roman', serif; font-size: 1.16rem; line-height: 1.75; position: relative; overflow: hidden; overflow-wrap: break-word; }
    .lib-paper p { margin: 0 0 1em; }
    .lib-paper h2 { font-family: Georgia, serif; font-weight: 400; font-size: 1.6rem; margin: 0 0 var(--s-3); }
    .lib-paper .lib-eyebrow { font-family: var(--font-body, system-ui); font-size: .72rem; font-weight: 800; letter-spacing: .12em; color: #7A6F8F; margin: 0 0 10px; }
    .lib-paper .lib-eyebrow + p { margin-top: 0; }
    .lib-paper hr { border: 0; border-top: 1px solid #CDBFA6; margin: var(--s-5) 0; }
    .lib-kept { font-family: var(--font-body, system-ui); font-size: .95rem; line-height: 1.5; background: #fff; border-left: 4px solid #B9A6FF; border-radius: 10px; padding: 12px 14px; margin: 14px 0; }
    .lib-kept b { display: block; font-size: .68rem; letter-spacing: .12em; color: #5B3FA8; margin-bottom: 4px; }
    .lib-fade { position: absolute; left: 0; right: 0; bottom: 0; height: 190px; background: linear-gradient(rgba(243,236,221,0), #F3ECDD 70%); }
    .lib-gate { background: var(--thq-deep); color: #fff; border-radius: var(--radius-lg); padding: var(--s-6); margin-top: calc(-1 * var(--s-6)); position: relative; box-shadow: 0 18px 44px rgba(20,16,51,.3); display: grid; grid-template-columns: auto 1fr; gap: var(--s-5); align-items: center; }
    .lib-gate img { width: 96px; height: auto; }
    .lib-gate h2 { margin: 0 0 6px; font-family: var(--font-display); font-size: 1.5rem; }
    .lib-gate p { margin: 0 0 var(--s-4); color: rgba(255,255,255,.85); }
    .lib-gate form { display: flex; gap: 10px; flex-wrap: wrap; }
    .lib-gate input { flex: 1 1 220px; min-width: 0; padding: 14px 16px; border-radius: 999px; border: 0; font-size: 1rem; }
    .lib-btn { padding: 14px 22px; border-radius: 999px; border: 0; background: #F28A1B; color: #fff; font-weight: 800; font-size: 1rem; box-shadow: 0 6px 16px rgba(242,138,27,.4); cursor: pointer; font-family: inherit; }
    .lib-btn[disabled] { opacity: .6; cursor: default; }
    .lib-gate small { display: block; margin-top: 10px; color: rgba(255,255,255,.7); }
    .lib-gate .lib-err { color: #FFD3C9; font-weight: 700; }
    .lib-more { display: flex; gap: 12px; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-top: var(--s-4); font-family: var(--font-body, system-ui); font-size: .95rem; }
    .lib-gate[hidden], .lib-more[hidden] { display: none; }
    .lib-note { background: #fff; border-left: 4px solid #B9A6FF; border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(20,16,51,.06), 0 8px 20px rgba(20,16,51,.08); font-size: .98rem; line-height: 1.5; }
    .js .lib-notes:not(.is-open) .lib-note--more { display: none; }
    .lib-link { background: none; border: 0; padding: 0; color: #6C3483; font-weight: 800; font-size: 1rem; text-decoration: underline; cursor: pointer; font-family: inherit; }
    .lib-side h2 { font-family: var(--font-display); font-size: 1.35rem; margin: 0 0 4px; }
    .lib-side > p { color: var(--ink-2); margin: 0 0 var(--s-4); }
    .lib-credit { color: var(--ink-2); font-size: .9rem; margin-top: var(--s-5); }
    .lib-credit a { text-decoration: underline; }
    .lib-case { background: #24150E; border: 10px solid #5B3620; border-radius: 16px; padding: 26px 0 8px; box-shadow: 0 22px 50px rgba(20,16,51,.28); }
    .lib-plaque { display: table; margin: 0 auto 14px; background: #D4AE5C; color: #3B2A0A; font-size: .7rem; font-weight: 900; letter-spacing: .14em; padding: 5px 14px; border-radius: 4px; border: 1px solid #F1D58F; box-shadow: 0 3px 6px rgba(0,0,0,.4); }
    .lib-row { display: flex; align-items: flex-end; gap: 8px; padding: 0 26px; min-height: 250px; }
    .lib-plank { height: 20px; background: linear-gradient(#A06A40 0 6px, #7A4A2A 6px); box-shadow: 0 10px 14px rgba(0,0,0,.55); margin-bottom: 8px; }
    .lib-labels { display: flex; gap: 8px; padding: 0 26px; margin-bottom: 26px; }
    .lib-labels span { min-width: 0; text-align: center; font-size: .72rem; font-weight: 800; color: #C9B8A6; }
    .lib-labels span.open { color: #F1D58F; }
    .lib-sp { position: relative; min-width: 0; border-radius: 6px 6px 3px 3px; display: flex; align-items: center; justify-content: center; text-decoration: none; box-shadow: 3px 0 8px rgba(0,0,0,.5), inset 7px 0 0 rgba(255,255,255,.28), inset -8px 0 0 rgba(0,0,0,.16); transition: transform .15s; }
    a.lib-sp:hover, a.lib-sp:focus-visible { transform: translateY(-10px); }
    .lib-sp::before, .lib-sp::after { content: ""; position: absolute; left: 0; right: 0; height: 4px; background: rgba(40,24,60,.45); }
    .lib-sp::before { top: 18px; } .lib-sp::after { bottom: 18px; }
    .lib-sp b { writing-mode: vertical-rl; transform: rotate(180deg); font-family: Georgia, serif; font-weight: 400; color: #1C1433; font-size: 1rem; line-height: 1.15; max-height: 76%; overflow: hidden; text-align: center; padding: 0 6px; }
    .lib-sp i { position: absolute; top: 0; right: 14px; width: 11px; background: #C8372D; border-radius: 0 0 5px 5px; }
    .lib-room { flex: 1; color: #C9B8A6; text-align: right; font-size: .95rem; padding: 0 6px 18px 20px; }
    .lib-cardstock { background: #F3ECDD; color: #2A2340; border-radius: 10px; padding: 20px 22px; width: 320px; box-shadow: 0 16px 36px rgba(0,0,0,.4); transform: rotate(2deg); font-family: Georgia, serif; }
    .lib-cardstock small { font-family: var(--font-body, system-ui); font-size: .66rem; font-weight: 900; letter-spacing: .16em; color: #8A7B66; }
    .lib-cardstock h3 { font-weight: 400; font-size: 1.5rem; line-height: 1.15; margin: 8px 0 10px; }
    .lib-cardstock p { margin: 0; padding: 7px 0; border-bottom: 1px solid #CDBFA6; font-size: .95rem; color: #2A2340; display: flex; justify-content: space-between; gap: 10px; max-width: none; }
    .lib-cardstock::after { content: ""; display: block; clear: both; }
    .lib-stamp { display: inline-block; margin: 14px 0 0 auto; float: right; border: 2px solid #B23A30; color: #B23A30; font-family: var(--font-body, system-ui); font-weight: 900; font-size: .78rem; letter-spacing: .1em; padding: 4px 10px; border-radius: 6px; transform: rotate(-6deg); }
    .lib-stamp--reading { border-color: #5B3FA8; color: #5B3FA8; }
    @media (max-width: 800px) {
      .lib-hero__in, .lib-two, .lib-gate { grid-template-columns: 1fr; }
      .lib-hero img { width: 110px; } .lib-gate img { display: none; }
      .lib-cardstock { width: auto; transform: rotate(1deg); }
      .lib-row { gap: 5px; padding: 0 12px; min-height: 190px; } .lib-labels { gap: 5px; padding: 0 12px; }
      .lib-sp b { font-size: .78rem; padding: 0 3px; } .lib-sp i { right: 8px; width: 8px; }
      .lib-room { font-size: .8rem; padding-left: 8px; }
    }
    </style>"""


def head(title, desc, path, ld):
    """The Tali HQ page's head (pixel, fonts, its styles), with this page's own title and tags."""
    src = (ROOT / "tali-hq.html").read_text(encoding="utf-8")
    hd = src[: src.index("</head>")]
    url = SITE + path
    hd = re.sub(r"<title>.*?</title>", lambda m: f"<title>{e(title)}</title>", hd, flags=re.S)
    hd = re.sub(r'<meta name="description" content="[^"]*">', lambda m: f'<meta name="description" content="{e(desc)}">', hd)
    hd = re.sub(r'<link rel="canonical" href="[^"]*">', lambda m: f'<link rel="canonical" href="{url}">', hd)
    hd = re.sub(r'<meta property="og:title" content="[^"]*">', lambda m: f'<meta property="og:title" content="{e(title)}">', hd)
    hd = re.sub(r'<meta property="og:description" content="[^"]*">', lambda m: f'<meta property="og:description" content="{e(desc)}">', hd)
    hd = re.sub(r'<meta property="og:url" content="[^"]*">', lambda m: f'<meta property="og:url" content="{url}">', hd)
    hd = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", hd, flags=re.S)
    hd = hd.replace('href="css/', 'href="/css/')
    scripts = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return hd + STYLE + "\n" + scripts + "\n</head>\n"


def crumbs(*items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def page(headhtml, main, script=""):
    return (headhtml + '<body class="thq">\n  <!-- chrome:header -->\n<!-- /chrome:header -->\n\n'
            + '  <main id="main">\n' + main + '\n  </main>\n\n  <!-- chrome:footer -->\n<!-- /chrome:footer -->\n'
            + script + '<script src="/js/nav.js" defer></script>\n</body>\n</html>\n')


# ---------- the bookcase ----------

def spine(book, link=True):
    w, ht, p = h(book, "w", 66, 86), h(book, "h", 222, 246), pct(book)
    ribbon = "" if finished(book) else f'<i style="height:{30 + round(p * 0.4)}px"></i>'
    label = f'{book["title"]} by {book["author"]}. ' + ("Finished, open to read." if finished(book) else f"{p}% read.")
    return (f'<a href="/library/{slug(book["title"])}.html" class="lib-sp" aria-label="{e(label)}" '
            f'style="flex:0 1 {w}px;height:{ht}px;background:{colour(book)}"><b>{e(book["title"])}</b>{ribbon}</a>')


def label(book):
    w = h(book, "w", 66, 86)
    return (f'<span class="open" style="flex:0 1 {w}px">OPEN</span>' if finished(book)
            else f'<span style="flex:0 1 {w}px">{pct(book)}%</span>')


def shelf_row(books, room=""):
    return ('<div class="lib-row">' + "".join(spine(b) for b in books) + room + '</div>\n        <div class="lib-plank"></div>'
            '<div class="lib-labels" aria-hidden="true">' + "".join(label(b) for b in books) + '</div>')


def card(book):
    p, c = pct(book), colour(book)
    tag = ('<span class="lib-tag lib-tag--open">Finished. Open to read</span>' if finished(book) else
           f'<span class="lib-tag lib-tag--reading">{p}% read</span><div class="lib-bar"><i style="width:{p}%;background:{c}"></i></div>')
    return (f'<a class="lib-book" href="/library/{slug(book["title"])}.html"><span class="lib-spine" style="background:{c}"></span>'
            f'<span style="flex:1;min-width:0"><h3>{e(book["title"])}</h3><small>{e(book["author"])} · {e(book["subject"] or "")}</small>'
            f'<small>{book["lessons"]} things kept{"" if finished(book) else " so far"}</small>{tag}</span></a>')


def build_index(books):
    done = [b for b in books if finished(b)]
    reading = sorted([b for b in books if not finished(b)], key=lambda b: -pct(b))
    kept = sum(b["lessons"] for b in books)
    rows = [reading[i:i + 5] for i in range(0, len(reading), 5)]
    case = ['<span class="lib-plaque">FINISHED · OPEN TO READ</span>',
            shelf_row(done, '<div class="lib-room">Room on this shelf for the next one she finishes.</div>')]
    for i, r in enumerate(rows):
        case.append('<span class="lib-plaque">STILL READING</span>' if i == 0 else "")
        case.append(shelf_row(r))
    title = "Tali's library: the books Tali has read and what she kept"
    desc = (f"The {len(books)} books Tali, the AI in Tali HQ, is reading, with her notes on each one. "
            f"The {len(done)} she has finished are free to read.")
    ld = [crumbs(("Home", "/"), ("Tali HQ", "/tali-hq.html"), ("Tali's library", "/library/")),
          {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Tali's library", "url": SITE + "/library/",
           "hasPart": [{"@type": "Book", "name": b["title"], "author": {"@type": "Person", "name": b["author"]},
                        "url": f'{SITE}/library/{slug(b["title"])}.html'} for b in books]}]
    main = f"""    <section class="lib-hero"><div class="lib-hero__in"><div>
      <span class="thq-eyebrow">Tali's library</span>
      <h1>The books Tali has read, and what she kept from each one.</h1>
      <p>Tali reads a few pages every night and files what is still worth knowing into her brain. When she finishes a book, the whole thing opens here for you to read, with her notes beside it.</p>
      <div class="lib-stats"><div><b>{len(books)}</b><span>books on her shelf</span></div><div><b>{len(done)}</b><span>finished and open</span></div><div><b>{kept}</b><span>things kept so far</span></div></div>
    </div><img src="/img/tali/tali_think.webp" alt="Tali thinking" width="340" height="460"></div></section>
    <section class="thq-sec"><h2>Her shelf</h2><p>Pick a book off the shelf. The finished ones open to read. The red ribbon is her bookmark in the ones she is still reading, and you can see her notes so far.</p>
      <div class="lib-case">
        {chr(10).join(x for x in case if x)}
      </div></section>
    <section class="thq-sec"><h2>The catalogue</h2><p>The same books as a list. Free to read: enter your email once and every finished book opens.</p>
      <div class="lib-grid">{"".join(card(b) for b in done)}</div></section>
    <section class="thq-sec" style="padding-top: var(--s-5);"><h2 style="font-size:1.3rem">Still reading</h2>
      <div class="lib-grid">{"".join(card(b) for b in reading)}</div></section>
    <section class="thq-end" style="margin-top: var(--s-8);"><div class="thq-end__in"><h2>Want a Tali who reads for you too?</h2><a href="{APP}/?ref=site-library" target="_blank" rel="noopener">Open Tali HQ</a></div></section>"""
    (OUT / "index.html").write_text(page(head(title + " | Totality 360", desc, "/library/", ld), main), encoding="utf-8")


# ---------- one book ----------

def build_book(book):
    s, p, fin = slug(book["title"]), pct(book), finished(book)
    path = f"/library/{s}.html"
    when = nice_date(book.get("last_read_at") or "")
    subject = book.get("subject") or ""
    notes = book.get("notes") or []
    kept = book["lessons"]
    if fin:
        title = f'{book["title"]} by {book["author"]}: read it free with Tali\'s notes'
        desc = (f'Read {book["title"]} by {book["author"]} free online, with the {kept} things Tali, the AI in Tali HQ, kept from it.')
        lede = (f'By {e(book["author"])}. Tali finished it{" on " + when if when else ""} and kept {kept} things from it. '
                'Read the book free, with her notes beside it.')
        stamp = f'<span class="lib-stamp">READ{" · " + when.upper() if when else ""}</span>'
        stats = (f'<div><b>{book["passages"]}</b><span>passages</span></div><div><b>{kept}</b><span>things Tali kept</span></div>'
                 '<div><b>Free</b><span>out of copyright</span></div>')
    else:
        title = f'{book["title"]} by {book["author"]}: Tali\'s notes so far'
        desc = (f'Tali, the AI in Tali HQ, is {p}% of the way through {book["title"]} by {book["author"]}. '
                f'Here are the {kept} things she has kept so far.')
        lede = (f'By {e(book["author"])}. Tali is {p}% of the way through and has kept {kept} things so far. '
                'The whole book opens here to read when she finishes it.')
        stamp = f'<span class="lib-stamp lib-stamp--reading">READING · {p}%</span>'
        stats = (f'<div><b>{p}%</b><span>read so far</span></div><div><b>{kept}</b><span>things Tali kept</span></div>'
                 f'<div><b>{book["passages"]}</b><span>passages in the book</span></div>')

    cardstock = (f'<div class="lib-cardstock"><small>TALI\'S LIBRARY · {e(subject.upper())}</small><h3>{e(book["title"])}</h3>'
                 f'<p><span>{e(book["author"])}</span></p><p><span>{book["passages"]} passages</span><span>{kept} things kept</span></p>{stamp}</div>')

    if fin:
        pv = (book.get("preview") or [{}])[0]
        paras = "\n          ".join(f"<p>{x}</p>" for x in paragraphs(pv.get("text") or ""))
        left = f"""        <div class="lib-paper" id="lib-paper">
          <div class="lib-eyebrow">PASSAGE {pv.get("n") or 1} OF {book["passages"]}</div>
          {paras}
          <div class="lib-fade" id="lib-fade"></div>
        </div>
        <div class="lib-gate" id="lib-gate">
          <img src="/img/tali/tali_point.webp" alt="" width="200" height="270">
          <div><h2>Keep reading, free</h2><p>Enter your email and the whole book opens, along with every other book Tali has finished.</p>
          <form id="lib-form"><input type="email" name="email" required autocomplete="email" placeholder="you@example.com" aria-label="Your email"><button type="submit" class="lib-btn">Open the book</button></form>
          <small id="lib-msg" role="status">By entering your email you are OK with us emailing you about Tali's library and Tali HQ. You can unsubscribe any time.</small></div>
        </div>
        <div class="lib-more" id="lib-more" hidden><span id="lib-pos"></span><button type="button" class="lib-btn" id="lib-next">Next pages</button></div>
        <noscript><p class="lib-credit">Turn on JavaScript to open the rest of the book.</p></noscript>"""
    else:
        left = f"""        <div class="lib-paper">
          <div class="lib-eyebrow">STILL ON HER DESK</div>
          <h2>Tali is {p}% of the way through.</h2>
          <p>She reads a few pages every night. So far she has read {book["studied"]} of {book["passages"]} passages and kept {kept} things from them.</p>
          <p>When she finishes, the whole book opens here to read, free, with her notes beside each page.</p>
          <div class="lib-bar" style="background:#E2D8C2"><i style="width:{p}%;background:#C8372D"></i></div>
        </div>
        <p style="margin-top: var(--s-5);"><a class="lib-link" href="/library/">See the books she has finished</a></p>"""

    note_html = "".join(
        f'<div class="lib-note{" lib-note--more" if i >= SHOWN_NOTES else ""}">{e(n["text"], quote=False)}</div>' for i, n in enumerate(notes))
    more = ""
    if kept > SHOWN_NOTES or len(notes) > SHOWN_NOTES:
        more = f'<p><button type="button" class="lib-link" id="lib-all">See all {kept}</button></p>'
    shown = min(SHOWN_NOTES, len(notes))
    side = (f'<aside class="lib-side"><h2>What Tali kept</h2><p>{kept} things from this book went into her brain{"" if fin else " so far"}. '
            f'Here are the first {shown}.</p><div class="lib-notes" id="lib-notes">{note_html}</div>{more}</aside>')

    credit = (f'<p class="lib-credit">The text is from <a href="{e(book["source_url"] or "")}" target="_blank" rel="noopener">Project Gutenberg</a>. '
              f'{e(book.get("licence_note") or "")} The notes are Tali\'s own summaries.</p>')

    ld = [crumbs(("Home", "/"), ("Tali HQ", "/tali-hq.html"), ("Tali's library", "/library/"), (book["title"], path)),
          {"@context": "https://schema.org", "@type": "Book", "name": book["title"],
           "author": {"@type": "Person", "name": book["author"]}, "url": SITE + path,
           "isAccessibleForFree": True, "inLanguage": "en", "genre": subject}]
    main = f"""    <section class="lib-hero"><div class="lib-hero__in"><div>
      <a class="lib-back" href="/library/">&larr; Tali's library</a><br>
      <span class="thq-eyebrow">Tali's library · {e(subject)}</span>
      <h1>{e(book["title"])}</h1>
      <p>{lede}</p>
      <div class="lib-stats">{stats}</div>
    </div>{cardstock}</div></section>
    <section class="thq-sec"><div class="lib-two">
      <div>
{left}
      </div>
      {side}
    </div>{credit}</section>
    <section class="thq-end" style="margin-top: var(--s-8);"><div class="thq-end__in"><h2>Tali can read for you too.</h2><a href="{APP}/?ref=site-library" target="_blank" rel="noopener">Open Tali HQ</a></div></section>"""
    cfg = {"id": book["id"], "finished": fin, "passages": book["passages"], "kept": kept, "baked": len(notes)}
    script = f'<script>window.TALI_LIBRARY = {json.dumps(cfg)};</script>\n<script src="/js/library.js?v=1" defer></script>\n'
    (OUT / f"{s}.html").write_text(page(head(title + " | Tali's library", desc, path, ld), main, script), encoding="utf-8")
    return f"{s}.html"


def main():
    if "--fetch" in sys.argv:
        fetch()
    books = json.loads(DATA.read_text(encoding="utf-8"))["books"]
    OUT.mkdir(exist_ok=True)
    made = {"index.html"}
    build_index(books)
    for b in books:
        made.add(build_book(b))
    for old in OUT.glob("*.html"):
        if old.name not in made:
            old.unlink()
    print(f"library: {len(books)} books, {sum(1 for b in books if finished(b))} finished")


if __name__ == "__main__":
    main()
