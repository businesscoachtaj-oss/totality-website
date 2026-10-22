#!/usr/bin/env python3
"""Regenerate sitemap.xml from the pages that actually exist.

Usage: python3 tools/build_sitemap.py           (writes sitemap.xml)
       python3 tools/build_sitemap.py --check   (exit 1 if sitemap.xml is stale or lists a missing page)

Rules
- Every .html page in the repo is included unless it matches EXCLUDE.
- PDFs, download/thank-you pages, brand kits, templates and partials are never listed.
- lastmod is the date of the page's last git commit (falls back to file mtime).
- A page only gets listed if the file exists, so planned pages appear once they are built.
"""
import datetime, fnmatch, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://totality360.com.au/"

EXCLUDE = [
    "*-download.html",          # paid-product thank-you pages (noindex)
    "brand-kit-*.html",         # internal brand kits (noindex)
    "blog/post-template.html",
    "partials/*", "tools/*", "data/*", "node_modules/*",
    "delete-account.html",      # account utility page for app store review
    "404.html",
]

# Priority and change frequency by path pattern (first match wins).
RULES = [
    ("index.html",            "1.0", "weekly"),
    ("totality.html",         "0.9", "weekly"),
    ("nutrition.html",        "0.9", "weekly"),
    ("pricing.html",          "0.9", "weekly"),
    ("features.html",         "0.8", "monthly"),
    ("nutrition-features.html","0.8", "monthly"),
    ("tali-ai.html",          "0.8", "monthly"),
    ("for-pts.html",          "0.8", "monthly"),
    ("for-gyms.html",         "0.8", "monthly"),
    ("compare/*.html",        "0.7", "monthly"),
    ("get-*.html",            "0.7", "monthly"),
    ("blog/index.html",       "0.7", "weekly"),
    ("blog/posts/*.html",     "0.6", "monthly"),
    ("whats-new.html",        "0.6", "weekly"),
    ("faq.html",              "0.6", "monthly"),
    ("help/*.html",           "0.5", "monthly"),
    ("privacy.html",          "0.3", "yearly"),
    ("terms.html",            "0.3", "yearly"),
    ("refund.html",           "0.3", "yearly"),
    ("*",                     "0.6", "monthly"),
]


def excluded(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in EXCLUDE) or rel.startswith(".")


def rule(rel: str):
    for pat, pr, cf in RULES:
        if fnmatch.fnmatch(rel, pat):
            return pr, cf
    return "0.5", "monthly"


def lastmod(path: pathlib.Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%cs", "--", str(path)],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        if out:
            # A modified working copy is newer than its last commit.
            dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", str(path)],
                                   capture_output=True, text=True, timeout=10).stdout.strip()
            if not dirty:
                return out
    except Exception:
        pass
    return datetime.date.fromtimestamp(path.stat().st_mtime).isoformat()


def url_for(rel: str) -> str:
    if rel == "index.html":
        return BASE
    if rel.endswith("/index.html"):
        return BASE + rel[: -len("index.html")]
    return BASE + rel


def pages():
    found = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT).as_posix()
        if rel.split("/")[0].startswith(".") or excluded(rel):
            continue
        found.append(rel)
    def key(rel):
        pr, _ = rule(rel)
        return (-float(pr), rel)
    return sorted(found, key=key)


def build() -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for rel in pages():
        pr, cf = rule(rel)
        lines += ["  <url>",
                  f"    <loc>{url_for(rel)}</loc>",
                  f"    <lastmod>{lastmod(ROOT / rel)}</lastmod>",
                  f"    <changefreq>{cf}</changefreq>",
                  f"    <priority>{pr}</priority>",
                  "  </url>"]
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def check() -> int:
    import re
    xml = (ROOT / "sitemap.xml").read_text()
    bad = 0
    for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
        rel = loc[len(BASE):] or "index.html"
        if rel.endswith("/"):
            rel += "index.html"
        if not (ROOT / rel).exists():
            print("listed but missing:", loc); bad += 1
    listed = set(re.findall(r"<loc>([^<]+)</loc>", xml))
    for rel in pages():
        if url_for(rel) not in listed:
            print("page not in sitemap:", rel); bad += 1
    print("sitemap OK" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(check())
    (ROOT / "sitemap.xml").write_text(build())
    print(f"Wrote sitemap.xml with {len(pages())} pages")
