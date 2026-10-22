#!/usr/bin/env python3
"""Inject the shared header, footer and font links into every page.

Source of truth: partials/header.html, partials/footer.html, partials/head.html.

For each HTML page it:
  * fills <!-- chrome:head -->...<!-- /chrome:head -->      (or inserts it before the site.css link)
  * fills <!-- chrome:header -->...<!-- /chrome:header -->  (or replaces the old <nav> with class nav-logo)
  * fills <!-- chrome:footer -->...<!-- /chrome:footer -->  (or replaces the old <footer> with footer-brand)
  * moves a Meta Pixel block that sits above <!DOCTYPE> into <head> (above DOCTYPE forces quirks mode)
  * marks the current page's nav link with aria-current="page"
  * adds /js/nav.js if the page has no nav.js
  * regenerates js/site-chrome.js (JS fallback that injects the same markup)

Pages that have neither markers nor the old nav/footer are left alone and listed.
It is idempotent: run it as often as you like.

Usage:  python3 tools/apply_chrome.py [--dry-run] [files...]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE = {
    "brand-kit-totality.html",   # internal brand reference sheets
    "brand-kit-nutrition.html",
    "links.html",                # standalone link-in-bio page
}
EXCLUDE_DIRS = {"partials", "node_modules", ".git", "tools"}
NUTRITION_PAGES = {
    "nutrition.html", "get-nutrition.html", "nutrition-features.html",
    "calculator.html", "high-protein-meals.html", "high-protein-meals-download.html",
}

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

HEAD = read(os.path.join(ROOT, "partials/head.html")).strip()
HEADER = read(os.path.join(ROOT, "partials/header.html")).strip()
FOOTER = read(os.path.join(ROOT, "partials/footer.html")).strip()

def block(name, inner):
    return f"<!-- chrome:{name} -->\n{inner}\n<!-- /chrome:{name} -->"

MARK = lambda n: re.compile(r"<!-- chrome:%s -->.*?<!-- /chrome:%s -->" % (n, n), re.S)
OLD_NAV = re.compile(r"<nav\b[^>]*>(?:(?!</nav>).)*?nav-logo.*?</nav>", re.S)
OLD_FOOTER = re.compile(r"<footer\b(?![^>]*site-footer)[^>]*>(?:(?!</footer>).)*?footer-brand.*?</footer>", re.S)
CSS_LINK = re.compile(r'<link[^>]+href="[^"]*css/site\.css"[^>]*>')
PIXEL = re.compile(r"\A\s*(<!-- Meta Pixel Code -->.*?<!-- End Meta Pixel Code -->)\s*(?=<!DOCTYPE)", re.S | re.I)

def brand_of(rel, html):
    m = re.search(r'<body[^>]*data-brand="(\w+)"', html)
    if m:
        return m.group(1)
    return "nutrition" if os.path.basename(rel) in NUTRITION_PAGES else "totality"

def header_for(rel, html):
    if brand_of(rel, html) == "nutrition":
        h = HEADER.replace("{{CTA_CLASS}}", "btn--nutrition").replace("{{CTA_HREF}}", "/get-nutrition.html")
    else:
        h = HEADER.replace("{{CTA_CLASS}}", "btn--primary").replace("{{CTA_HREF}}", "/get-totality.html")
    return h

def url_path(rel):
    p = "/" + rel.replace(os.sep, "/")
    if p.endswith("index.html"):
        p = p[: -len("index.html")]
    return p

def mark_current(markup, rel):
    here = url_path(rel)
    def sub(m):
        tag = m.group(0)
        href = m.group(1)
        norm = href[: -len("index.html")] if href.endswith("index.html") else href
        if norm == here and "aria-current" not in tag:
            return tag[:-1] + ' aria-current="page">'
        return tag
    return re.sub(r'<a [^>]*href="(/[^"#]*)"[^>]*>', sub, markup)

def process(rel, html):
    notes = []
    out = html

    # Pixel above DOCTYPE -> into <head>
    m = PIXEL.match(out)
    if m:
        pixel = m.group(1)
        out = out[m.end():]
        out = re.sub(r"(<head[^>]*>)", lambda h: h.group(1) + "\n" + pixel, out, count=1)
        notes.append("pixel moved into head")

    has_markers = MARK("header").search(out) or MARK("footer").search(out)
    has_old = OLD_NAV.search(out) or OLD_FOOTER.search(out)
    if not has_markers and not has_old:
        return out, notes + ["SKIPPED (no markers, no old nav/footer)"]

    # Head (fonts)
    if MARK("head").search(out):
        out = MARK("head").sub(lambda _: block("head", HEAD), out)
    elif CSS_LINK.search(out):
        out = CSS_LINK.sub(lambda l: block("head", HEAD) + "\n" + l.group(0), out, count=1)
    else:
        out = out.replace("</head>", block("head", HEAD) + '\n<link rel="stylesheet" href="/css/site.css">\n</head>', 1)
        notes.append("site.css added")

    header = mark_current(header_for(rel, out), rel)
    footer = mark_current(FOOTER, rel)

    if MARK("header").search(out):
        out = MARK("header").sub(lambda _: block("header", header), out)
    elif OLD_NAV.search(out):
        out = OLD_NAV.sub(lambda _: block("header", header), out, count=1)
        notes.append("old nav replaced")
    else:
        # Page never had the site nav (ad landing pages such as guide.html): keep it nav-free.
        notes.append("no header (page had no site nav; add <!-- chrome:header --> markers to opt in)")

    if MARK("footer").search(out):
        out = MARK("footer").sub(lambda _: block("footer", footer), out)
    elif OLD_FOOTER.search(out):
        out = OLD_FOOTER.sub(lambda _: block("footer", footer), out, count=1)
        notes.append("old footer replaced")
    else:
        out = out.replace("</body>", block("footer", footer) + "\n</body>", 1)
        notes.append("footer inserted before </body>")

    # Skip-link target
    if 'id="main"' not in out and "<!-- /chrome:header -->" in out:
        out = out.replace("<!-- /chrome:header -->", '<!-- /chrome:header -->\n<span id="main" tabindex="-1"></span>', 1)

    if "nav.js" not in out:
        out = out.replace("</body>", '<script src="/js/nav.js" defer></script>\n</body>', 1)
        notes.append("nav.js added")
    return out, notes

def write_site_chrome_js():
    js = """/* GENERATED by tools/apply_chrome.py from partials/. Do not edit by hand.
   Fallback only: pages normally get the header/footer written in statically.
   If a page has <div data-chrome="header"></div> / <div data-chrome="footer"></div>
   (or no .site-header at all), this injects the same markup at runtime. */
(function () {
  var HEADER = %s;
  var FOOTER = %s;
  function brand() { return (document.body.getAttribute('data-brand') || 'totality'); }
  function headerHtml() {
    var n = brand() === 'nutrition';
    return HEADER.replace('{{CTA_CLASS}}', n ? 'btn--nutrition' : 'btn--primary')
                 .replace('{{CTA_HREF}}', n ? '/get-nutrition.html' : '/get-totality.html');
  }
  function place(sel, html, atStart) {
    var slot = document.querySelector(sel);
    var wrap = document.createElement('div');
    wrap.innerHTML = html;
    var frag = document.createDocumentFragment();
    while (wrap.firstChild) frag.appendChild(wrap.firstChild);
    if (slot) { slot.replaceWith(frag); }
    else if (atStart) { document.body.insertBefore(frag, document.body.firstChild); }
    else { document.body.appendChild(frag); }
  }
  function run() {
    document.documentElement.classList.add('js');
    if (!document.querySelector('.site-header')) place('[data-chrome="header"]', headerHtml(), true);
    if (!document.querySelector('.site-footer')) place('[data-chrome="footer"]', FOOTER, false);
    document.dispatchEvent(new CustomEvent('chrome:ready'));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
})();
""" % (json.dumps(HEADER.split("\n", 1)[1]), json.dumps(FOOTER))
    with open(os.path.join(ROOT, "js/site-chrome.js"), "w", encoding="utf-8") as f:
        f.write(js)

def all_pages():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in EXCLUDE_DIRS and not x.startswith(".")]
        for fn in files:
            if fn.endswith(".html"):
                yield os.path.relpath(os.path.join(d, fn), ROOT)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    pages = args or sorted(all_pages())
    write_site_chrome_js()
    changed = skipped = 0
    for rel in pages:
        rel = os.path.relpath(os.path.abspath(rel), ROOT) if os.path.isabs(rel) or os.path.exists(rel) else rel
        if rel.replace(os.sep, "/") in EXCLUDE:
            print(f"  excluded  {rel}")
            continue
        path = os.path.join(ROOT, rel)
        html = read(path)            # re-read right before writing (other people edit pages)
        out, notes = process(rel, html)
        if any(n.startswith("SKIPPED") for n in notes):
            skipped += 1
        if out != html:
            changed += 1
            if not dry:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(out)
        print(f"{'*' if out != html else ' '} {rel}  {'; '.join(notes)}")
    print(f"\n{changed} page(s) updated, {skipped} skipped{' (dry run)' if dry else ''}.")

if __name__ == "__main__":
    main()
