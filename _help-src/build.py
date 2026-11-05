#!/usr/bin/env python3
"""Builds the help guides (Nov 2026).

Source:  _help-src/<guide>/guide.json and one .md file per page (Jekyll ignores _ folders).
Output:  help/<guide>/<slug>.html, help/<guide>/search.json, help/index.html.
Images:  put them in help/<guide>/img/ and reference them as img/<file>.png.

Markdown extras (all optional):
  front matter     ---\ntitle: ...\nsummary: ...\n---
  plan badges      [[Free]] [[Paid]] [[Trial]] [[Pro]] [[Plus]] [[Owner]] [[Trainer]] [[Client]] ...
  phone screen     !phone[Caption text](img/file.png)
  two phones       !phones[Caption A](img/a.png)[Caption B](img/b.png)
  wide screen      !wide[Caption](img/file.png)   (desktop or landscape shots)
  callouts         :::tip / :::note / :::warn / :::tali  ...  :::
  steps            a numbered list right after a line "!steps" renders as big numbered steps
  FAQ              ?? Question text   (answer is everything until the next ?? or heading)
Run:  python3 _help-src/build.py            (all guides)
      python3 _help-src/build.py nutrition  (one guide)
"""
import json, re, sys, html, pathlib
import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / '_help-src'
OUT = ROOT / 'help'

ACCENTS = {
    'orange': ('#ED8008', '#C46800', '#FFF4E8', '#1C1420'),
    'blue':   ('#1565A0', '#0F4F80', '#EAF2FA', '#FFFFFF'),
    'purple': ('#6C3483', '#4E2560', '#F3EEF6', '#FFFFFF'),
}

def slugify(s):
    s = re.sub(r'<[^>]+>', '', s).lower()
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or 'section'

def front_matter(text):
    meta = {}
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
            text = text[end + 4:]
    return meta, text

def badge(m):
    label = m.group(1)
    return f'<span class="badge badge--{slugify(label)}">{html.escape(label)}</span>'

def figure(cls, cap, src):
    return (f'<figure class="shot shot--{cls}"><img src="{src}" alt="{html.escape(cap)}" loading="lazy">'
            f'<figcaption>{html.escape(cap)}</figcaption></figure>')

def preprocess(md):
    out, i, lines = [], 0, md.splitlines()
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^!phones((?:\[[^\]]*\]\([^)]+\))+)\s*$', line)
        if m:
            figs = re.findall(r'\[([^\]]*)\]\(([^)]+)\)', m.group(1))
            out.append('<div class="shots">' + ''.join(figure('phone', c, s) for c, s in figs) + '</div>')
            out.append(''); i += 1; continue
        m = re.match(r'^!(phone|wide)\[([^\]]*)\]\(([^)]+)\)\s*$', line)
        if m:
            out.append('<div class="shots">' + figure(m.group(1), m.group(2), m.group(3)) + '</div>')
            out.append(''); i += 1; continue
        m = re.match(r'^:::(tip|note|warn|tali)\s*(.*)$', line)
        if m:
            kind, title = m.group(1), m.group(2).strip()
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != ':::':
                body.append(lines[i]); i += 1
            i += 1
            inner = markdown.markdown(re.sub(r'\[\[([^\]]+)\]\]', badge, '\n'.join(body)), extensions=['tables', 'sane_lists'])
            label = title or {'tip': 'Tip', 'note': 'Good to know', 'warn': 'Heads up', 'tali': 'Tali says'}[kind]
            out.append(f'<aside class="callout callout--{kind}"><p class="callout__title">{html.escape(label)}</p>{inner}</aside>')
            out.append(''); continue
        if line.strip() == '!steps':
            out.append('<div class="steps" markdown="1">'); out.append('')
            i += 1
            while i < len(lines) and (re.match(r'^\s*\d+\.\s', lines[i]) or (lines[i].startswith('   ') and lines[i].strip())):
                out.append(lines[i]); i += 1
            out.append(''); out.append('</div>'); out.append(''); continue
        m = re.match(r'^\?\?\s+(.+)$', line)
        if m:
            q = m.group(1).strip()
            body = []
            i += 1
            while i < len(lines) and not re.match(r'^(\?\?\s|#{1,3}\s)', lines[i]):
                body.append(lines[i]); i += 1
            inner = markdown.markdown(re.sub(r'\[\[([^\]]+)\]\]', badge, '\n'.join(body).strip()), extensions=['tables', 'sane_lists'])
            out.append(f'<details class="faq" id="q-{slugify(q)[:60]}"><summary>{html.escape(q)}</summary><div class="faq__a">{inner}</div></details>')
            out.append(''); continue
        out.append(line); i += 1
    return re.sub(r'\[\[([^\]]+)\]\]', badge, '\n'.join(out))

def add_heading_ids(body):
    heads = []
    def rep(m):
        lvl, inner = m.group(1), m.group(2)
        hid = slugify(inner)[:70]
        n, base = 2, hid
        while any(h[1] == hid for h in heads):
            hid = f'{base}-{n}'; n += 1
        heads.append((int(lvl), hid, re.sub(r'<[^>]+>', '', inner)))
        return f'<h{lvl} id="{hid}">{inner}<a class="anchor" href="#{hid}" aria-label="Link to this section">#</a></h{lvl}>'
    body = re.sub(r'<h([23])>(.*?)</h\1>', rep, body)
    return body, heads

def text_of(h):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()

PAGE = '''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | {guide_title}</title>
<meta name="description" content="{summary}">

<link rel="icon" href="/favicon-96.png" sizes="any">
<link rel="preload" href="/fonts/figtree-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/bricolage-grotesque-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/help/assets/guide.css?v=2">
<style>:root{{--accent:{a};--accent-dark:{ad};--accent-soft:{asoft};--on-accent:{aon}}}</style>
</head>
<body class="guide guide--{key}">
<a class="skip" href="#main">Skip to the guide</a>
<header class="topbar">
  <button class="topbar__menu" type="button" aria-controls="toc" aria-expanded="false">Contents</button>
  <a class="topbar__brand" href="/help/{key}/"><img src="{icon}" alt="" width="28" height="28"><span>{guide_title}</span></a>
  <label class="search"><span class="sr">Search this guide</span><input type="search" placeholder="Search this guide" autocomplete="off" data-guide="{key}"></label>
</header>
<div class="search-results" hidden></div>
<div class="layout">
  <nav class="toc" id="toc" aria-label="Guide contents">
    <p class="toc__audience">{audience}</p>
    {toc}
  </nav>
  <main id="main" class="content">
    <p class="crumb">{guide_title}</p>
    <h1>{title}</h1>
    {summary_html}
    {onpage}
    {body}
    <nav class="pager" aria-label="Previous and next">{pager}</nav>
    <footer class="foot">
      <p>Still stuck? Email <span class="mail">admintotality@gmail.com</span> and a real person will help.</p>
      <p class="foot__small">Totality 360 Pty Ltd, ABN 58 698 902 975. Screens show demo data. Last updated {updated}.</p>
    </footer>
  </main>
</div>
<script src="/help/assets/guide.js" defer></script>
</body>
</html>
'''

def build_guide(key):
    gdir = SRC / key
    cfg = json.loads((gdir / 'guide.json').read_text())
    a, ad, asoft, aon = ACCENTS[cfg.get('accent', 'orange')]
    odir = OUT / key
    odir.mkdir(parents=True, exist_ok=True)
    pages = []
    for slug in cfg['pages']:
        meta, md = front_matter((gdir / f'{slug}.md').read_text())
        body = markdown.markdown(preprocess(md), extensions=['tables', 'sane_lists', 'md_in_html', 'attr_list'])
        body, heads = add_heading_ids(body)
        pages.append({'slug': slug, 'title': meta.get('title', slug), 'summary': meta.get('summary', ''), 'body': body, 'heads': heads})
    index = []
    for n, pg in enumerate(pages):
        href = lambda p: f'/help/{key}/' if p['slug'] == 'index' else f'/help/{key}/{p["slug"]}.html'
        items = []
        groups = cfg.get('groups')
        def li(p):
            cur = ' aria-current="page"' if p is pg else ''
            return f'<li><a href="{href(p)}"{cur}>{html.escape(p["title"])}</a></li>'
        if groups:
            for g in groups:
                ps = [p for p in pages if p['slug'] in g['pages']]
                items.append(f'<p class="toc__group">{html.escape(g["title"])}</p><ol>' + ''.join(li(p) for p in ps) + '</ol>')
            toc = ''.join(items)
        else:
            toc = '<ol>' + ''.join(li(p) for p in pages) + '</ol>'
        h2s = [h for h in pg['heads'] if h[0] == 2]
        onpage = ''
        if len(h2s) >= 3:
            onpage = '<nav class="onpage" aria-label="On this page"><p>On this page</p><ul>' + ''.join(f'<li><a href="#{h[1]}">{html.escape(h[2])}</a></li>' for h in h2s) + '</ul></nav>'
        prev = pages[n - 1] if n > 0 else None
        nxt = pages[n + 1] if n + 1 < len(pages) else None
        pager = (f'<a class="pager__prev" href="{href(prev)}"><span>Previous</span>{html.escape(prev["title"])}</a>' if prev else '<span></span>') + \
                (f'<a class="pager__next" href="{href(nxt)}"><span>Next</span>{html.escape(nxt["title"])}</a>' if nxt else '<span></span>')
        page_html = PAGE.format(
            title=html.escape(pg['title']), guide_title=html.escape(cfg['title']), summary=html.escape(pg['summary']),
            summary_html=f'<p class="lead">{html.escape(pg["summary"])}</p>' if pg['summary'] else '',
            a=a, ad=ad, asoft=asoft, aon=aon, key=key, icon=cfg.get('icon', '/favicon-96.png'),
            audience=html.escape(cfg.get('audience', '')), toc=toc, onpage=onpage, body=pg['body'], pager=pager,
            updated=cfg.get('updated', ''))
        (odir / ('index.html' if pg['slug'] == 'index' else f'{pg["slug"]}.html')).write_text(page_html)
        # search entries: one per h2 section plus the page itself
        parts = re.split(r'(?=<h2 id=")', pg['body'])
        for part in parts:
            m = re.match(r'<h2 id="([^"]+)">(.*?)<a class="anchor"', part)
            sec_id, sec_title = (m.group(1), text_of(m.group(2))) if m else ('', pg['title'])
            index.append({'u': href(pg) + (f'#{sec_id}' if sec_id else ''), 'p': pg['title'], 's': sec_title, 't': text_of(part)[:1200]})
            for q in re.finditer(r'<details class="faq" id="([^"]+)"><summary>(.*?)</summary>', part):
                index.append({'u': href(pg) + f'#{q.group(1)}', 'p': pg['title'], 's': html.unescape(q.group(2)), 't': ''})
    (odir / 'search.json').write_text(json.dumps(index, ensure_ascii=False))
    return cfg, len(pages)

def build_hub(cfgs):
    cards = ''.join(
        f'<a class="hub__card" href="/help/{k}/" style="--accent:{ACCENTS[c.get("accent","orange")][0]}"><img src="{c.get("icon","/favicon-96.png")}" alt="" width="40" height="40"><b>{html.escape(c["title"])}</b><span>{html.escape(c.get("audience",""))}</span><small>{len(c["pages"])} pages</small></a>'
        for k, c in cfgs)
    (OUT / 'index.html').write_text(f'''<!DOCTYPE html><html lang="en-AU"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>How to use Totality, Totality Nutrition and Tali HQ</title><link rel="icon" href="/favicon-96.png" sizes="any"><link rel="stylesheet" href="/help/assets/guide.css?v=2"></head><body class="hub"><main class="hub__main"><p class="hub__back"><a href="/">&larr; totality360.com.au</a></p><h1>How to use our apps</h1><p class="lead">Pick your guide. Every guide has screens from the real app and a search box at the top.</p><div class="hub__grid">{cards}</div><p class="foot__small">Still stuck? Email admintotality@gmail.com.</p></main></body></html>''')

if __name__ == '__main__':
    keys = sys.argv[1:] or sorted(p.name for p in SRC.iterdir() if p.is_dir() and (p / 'guide.json').exists())
    done = []
    for k in keys:
        cfg, n = build_guide(k)
        done.append((k, cfg)); print(f'{k}: {n} pages')
    order = ['totality-owner', 'totality-trainer', 'totality-client', 'nutrition', 'tali-hq']
    allk = sorted([p.name for p in SRC.iterdir() if p.is_dir() and (p / 'guide.json').exists()], key=lambda k: order.index(k) if k in order else 99)
    build_hub([(k, json.loads((SRC / k / 'guide.json').read_text())) for k in allk])
