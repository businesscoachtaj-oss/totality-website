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
    'red':    ('#D92B2B', '#B32020', '#FCEBEA', '#FFFFFF'),
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
<link rel="canonical" href="https://totality360.com.au{canonical}">
<link rel="icon" href="/favicon-96.png" sizes="any">
<link rel="preload" href="/fonts/figtree-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/bricolage-grotesque-latin-wght.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/help/assets/guide.css?v=4">
<style>:root{{--accent:{a};--accent-dark:{ad};--accent-soft:{asoft};--on-accent:{aon}}}</style>
</head>
<body class="guide guide--{key}">
<a class="skip" href="#main">Skip to the guide</a>
<header class="topbar">
  <button class="topbar__menu" type="button" aria-controls="toc" aria-expanded="false">Contents</button>
  <a class="topbar__brand" href="/help/{key}/"><img src="{icon}" alt="" width="28" height="28"><span>{guide_title}</span></a>
  <a class="topbar__all" href="/help/">All guides</a>
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
    <p class="meta">{minutes} min read<span aria-hidden="true"> · </span>Updated {updated}</p>
    {onpage}
    {body}
    <nav class="pager" aria-label="Previous and next">{pager}</nav>
    <footer class="foot">
      <p>Still stuck? Email <span class="mail">admintotality@gmail.com</span> and a real person will help.</p>
      <p class="foot__links"><a href="/help/">All guides</a><a href="/help.html">Quick answers</a><a href="/faq.html">FAQ</a><a href="/pricing.html">Pricing</a><a href="/support.html">Support</a><a href="/">totality360.com.au</a></p>
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
            onpage = '<nav class="onpage" aria-label="On this page"><p>On this page</p><ol>' + ''.join(f'<li><a href="#{h[1]}">{html.escape(h[2])}</a></li>' for h in h2s if h[2].strip().lower() != 'questions') + '</ol></nav>'
        prev = pages[n - 1] if n > 0 else None
        nxt = pages[n + 1] if n + 1 < len(pages) else None
        pager = (f'<a class="pager__prev" href="{href(prev)}"><span>Previous</span>{html.escape(prev["title"])}</a>' if prev else '<span></span>') + \
                (f'<a class="pager__next" href="{href(nxt)}"><span>Next</span>{html.escape(nxt["title"])}</a>' if nxt else '<span></span>')
        page_html = PAGE.format(
            title=html.escape(pg['title']), guide_title=html.escape(cfg['title']), summary=html.escape(pg['summary']),
            summary_html=f'<p class="lead">{html.escape(pg["summary"])}</p>' if pg['summary'] else '',
            a=a, ad=ad, asoft=asoft, aon=aon, key=key, icon=cfg.get('icon', '/favicon-96.png'),
            audience=html.escape(cfg.get('audience', '')), toc=toc, onpage=onpage, body=pg['body'], pager=pager,
            updated=cfg.get('updated', ''), canonical=href(pg), minutes=max(1, round(len(text_of(pg['body']).split()) / 200)))
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
    def card(k, c):
        a, ad = ACCENTS[c.get('accent', 'orange')][:2]
        return (f'<a class="hub-card" href="/help/{k}/" style="--accent:{a};--accent-dark:{ad}"><img src="{c.get("icon","/favicon-96.png")}" alt="" width="40" height="40">'
                f'<b>{html.escape(c["title"])}</b><span>{html.escape(c.get("audience",""))}</span><small>{len(c["pages"])} pages</small></a>')
    totality = ''.join(card(k, c) for k, c in cfgs if k.startswith('totality-'))
    others = ''.join(card(k, c) for k, c in cfgs if not k.startswith('totality-'))
    keys = json.dumps([k for k, _ in cfgs])
    titles = json.dumps({k: c['title'] for k, c in cfgs})
    jobs = [
        ('Set up your gym or studio', 'Gym owners', '/help/totality-owner/sign-up.html'),
        ('Bring your members across', 'Gym owners', '/help/totality-owner/import.html'),
        ('Take payments in the app', 'Gym owners', '/help/totality-owner/stripe-connect.html'),
        ('Add and invite clients', 'Trainers', '/help/totality-trainer/adding-clients.html'),
        ('Get paid as a trainer', 'Trainers', '/help/totality-trainer/getting-paid.html'),
        ('Build a programme', 'Trainers', '/help/totality-trainer/programme-builder.html'),
        ('Your invite and first login', 'Clients', '/help/totality-client/your-invite.html'),
        ('Log your food', 'Totality Nutrition', '/help/nutrition/food-log.html'),
    ]
    jobs_html = ''.join(f'<a class="job" href="{u}"><b>{html.escape(t)}</b><span>{html.escape(w)}</span></a>' for t, w, u in jobs)
    pdfs = [
        ('Getting paid with Totality', 'Your payment options, what each costs you, and the steps to move clients onto automatic payments.', 'Totality-Setup-Guide-Getting-Paid.pdf', 4),
        ('Bringing your clients across', 'Adding your clients, what they do the first time, and carrying over sessions and programmes.', 'Totality-Setup-Guide-Clients-Across.pdf', 3),
        ('Setting up your studio', 'Account, team, members, payments, memberships and timetable, in the order to do them.', 'Totality-Setup-Guide-Studio.pdf', 4),
        ('Coaching your clients', 'Programmes, running sessions and weekly check-ins.', 'Totality-Setup-Guide-Coaching.pdf', 3),
    ]
    free = [
        ('How to start a personal training business', 'Qualifications, insurance, ABN and GST, pricing and your first clients.', 7),
        ('Marketing and finding clients', 'Your offer, Google listing, posts, referrals, ads and enquiries.', 6),
        ('How to write a training programme', 'Overload, volume, frequency, periodisation and fitting it to the person.', 7),
        ('Nutrition coaching fundamentals', 'Energy balance, protein, supplements and where your scope ends.', 7),
    ]
    free_html = ''.join(f'<a class="pdf" href="/resources.html"><span class="pdf__tag">Free PDF · {n} pages</span><b>{html.escape(t)}</b><span>{html.escape(d)}</span></a>' for t, d, n in free)
    pdf_html = ''.join(f'<a class="pdf" href="/guides/setup/{f}" target="_blank" rel="noopener"><span class="pdf__tag">PDF · {n} pages</span><b>{html.escape(t)}</b><span>{html.escape(d)}</span></a>' for t, d, f, n in pdfs)
    old = (OUT / 'index.html').read_text() if (OUT / 'index.html').exists() else ''
    def keep(name):
        m = re.search(rf'<!-- chrome:{name} -->.*?<!-- /chrome:{name} -->', old, re.S)
        return m.group(0) if m else f'<!-- chrome:{name} -->\n<!-- /chrome:{name} -->'
    (OUT / 'index.html').write_text(f'''<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>How to use Totality, Totality Nutrition and Totality Training</title>
<meta name="description" content="Step by step guides for Totality, Totality Nutrition and Totality Training, with screens from the real apps, plus setup guides to download.">
<link rel="canonical" href="https://totality360.com.au/help/">
<link rel="icon" href="/favicon-96.png" sizes="any">
{keep('head')}
<link rel="stylesheet" href="/css/site.css">
<style>
  .hub-search {{ position: relative; max-width: 640px; margin-top: var(--s-5, 24px); }}
  .hub-search input {{ width: 100%; font: inherit; font-size: 1.05rem; padding: 15px 18px 15px 46px; border-radius: 999px; border: 1.5px solid var(--line, #E6E4E1); background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' fill='none' stroke='%2362605D' stroke-width='2' stroke-linecap='round' viewBox='0 0 24 24'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cpath d='m20 20-3.5-3.5'/%3E%3C/svg%3E") no-repeat 17px center; color: var(--ink); }}
  .hub-search input:focus {{ outline: none; border-color: #ED8008; box-shadow: 0 0 0 4px rgba(237,128,8,.15); }}
  .hub-results {{ position: absolute; left: 0; right: 0; top: calc(100% + 8px); background: #fff; border: 1px solid var(--line, #E6E4E1); border-radius: 18px; box-shadow: 0 18px 40px rgba(39,38,38,.14); max-height: 60vh; overflow: auto; z-index: 20; padding: 6px; }}
  .hub-results a {{ display: block; padding: 10px 14px; border-radius: 12px; text-decoration: none; color: var(--ink); }}
  .hub-results a:hover, .hub-results a:focus {{ background: #FFF4E8; }}
  .hub-results b {{ display: block; font-size: .98rem; }}
  .hub-results small {{ color: var(--muted, #62605D); font-size: .82rem; }}
  .hub-results .none {{ padding: 12px 14px; margin: 0; color: var(--muted, #62605D); }}
  .hub-h {{ font-family: var(--display); font-size: 1.35rem; margin: 0 0 var(--s-4, 16px); }}
  .hub-sub {{ margin-top: var(--s-7, 40px); }}
  .jobs {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px; }}
  .job {{ display: flex; flex-direction: column; gap: 2px; padding: 14px 16px; border-radius: 14px; background: #fff; border: 1px solid var(--line, #E6E4E1); text-decoration: none; color: var(--ink); }}
  .job:hover {{ border-color: #ED8008; }}
  .job b {{ font-size: 1rem; }}
  .job b::after {{ content: " →"; color: #ED8008; }}
  .job span {{ color: var(--muted, #62605D); font-size: .85rem; }}
  .hub-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: var(--s-4, 16px); }}
  .hub-card {{ display: flex; flex-direction: column; gap: 6px; padding: 20px; border-radius: 18px; background: #fff; border: 1px solid var(--line, #E6E4E1); border-top: 5px solid var(--accent); text-decoration: none; color: var(--ink); transition: box-shadow .2s, transform .2s; }}
  .hub-card:hover {{ box-shadow: 0 12px 28px rgba(39,38,38,.1); transform: translateY(-2px); }}
  .hub-card img {{ border-radius: 10px; width: 40px; height: 40px; }}
  .hub-card b {{ font-family: var(--display); font-size: 1.15rem; line-height: 1.25; }}
  .hub-card span {{ color: var(--muted, #62605D); font-size: .92rem; }}
  .hub-card small {{ color: var(--accent-dark); font-weight: 700; font-size: .82rem; margin-top: 4px; }}
  .pdfs {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--s-4, 16px); }}
  .pdf {{ display: flex; flex-direction: column; gap: 6px; padding: 18px; border-radius: 18px; background: #fff; border: 1px solid var(--line, #E6E4E1); text-decoration: none; color: var(--ink); }}
  .pdf:hover {{ border-color: #ED8008; }}
  .pdf b {{ font-family: var(--display); font-size: 1.08rem; }}
  .pdf span {{ color: var(--muted, #62605D); font-size: .9rem; }}
  .pdf .pdf__tag {{ align-self: flex-start; font-size: .72rem; font-weight: 800; letter-spacing: .06em; text-transform: uppercase; color: #C46800; background: #FFF4E8; border-radius: 999px; padding: 3px 10px; }}
  .hub-more {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--s-4, 16px); }}
</style>
</head>
<body>
{keep('header')}
<main id="main">
  <section class="page-hero">
    <div class="container">
      <p class="crumbs"><a href="/">Home</a> / How to use</p>
      <h1>How to use our apps</h1>
      <p class="lead">Step by step guides with screens from the real apps. Search every guide at once, or pick yours below.</p>
      <div class="hub-search">
        <label for="hub-q" class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Search every guide</label>
        <input id="hub-q" type="search" placeholder="Search every guide, for example debit day" autocomplete="off">
        <div class="hub-results" hidden></div>
      </div>
    </div>
  </section>
  <section class="section section--tight">
    <div class="container">
      <h2 class="hub-h">Most asked for</h2>
      <div class="jobs">{jobs_html}</div>
      <div class="hub-sub">
        <h2 class="hub-h">Totality</h2>
        <div class="hub-grid">{totality}</div>
      </div>
      <div class="hub-sub">
        <h2 class="hub-h">Our other apps</h2>
        <div class="hub-grid">{others}</div>
      </div>
      <div class="hub-sub">
        <h2 class="hub-h">Setup guides to download</h2>
        <p style="margin:-6px 0 16px;color:var(--muted,#62605D)">Short PDFs you can print or keep beside you while you set up.</p>
        <div class="pdfs">{pdf_html}</div>
      </div>
      <div class="hub-sub">
        <h2 class="hub-h">Free guides for personal trainers</h2>
        <p style="margin:-6px 0 16px;color:var(--muted,#62605D)">Starting your business, finding clients, writing programmes and coaching nutrition.</p>
        <div class="pdfs">{free_html}</div>
      </div>
    </div>
  </section>
  <section class="section section--tint">
    <div class="container">
      <div class="section-head"><h2>Looking for something else?</h2></div>
      <div class="hub-more">
        <a class="card" href="/help.html"><h3 class="h4">Quick answers</h3><p>Short answers to the most common questions, on one page.</p></a>
        <a class="card" href="/faq.html"><h3 class="h4">FAQ</h3><p>Plans, payments and how the apps fit together.</p></a>
        <a class="card" href="/pricing.html"><h3 class="h4">Pricing</h3><p>Every plan and add-on, in Australian dollars.</p></a>
        <a class="card" href="/support.html"><h3 class="h4">Support</h3><p>Email admintotality@gmail.com and a real person replies.</p></a>
      </div>
    </div>
  </section>
</main>
{keep('footer')}
<script>
(function () {{
  var keys = {keys}, titles = {titles}, data = null;
  var input = document.getElementById('hub-q'), box = document.querySelector('.hub-results');
  function load() {{
    if (data) return Promise.resolve(data);
    return Promise.all(keys.map(function (k) {{
      return fetch('/help/' + k + '/search.json').then(function (r) {{ return r.json(); }}).then(function (d) {{ d.forEach(function (e) {{ e.g = titles[k]; }}); return d; }}).catch(function () {{ return []; }});
    }})).then(function (all) {{ data = [].concat.apply([], all); return data; }});
  }}
  function esc(s) {{ return String(s).replace(/[&<>"]/g, function (c) {{ return {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }}[c]; }}); }}
  function run() {{
    var q = input.value.trim().toLowerCase();
    if (q.length < 2) {{ box.hidden = true; return; }}
    load().then(function (d) {{
      var words = q.split(/\\s+/);
      var hits = d.map(function (e) {{
        var s = (e.s + ' ' + e.p).toLowerCase(), t = (e.t || '').toLowerCase(), score = 0;
        words.forEach(function (w) {{ if (s.indexOf(w) > -1) score += 5; if (t.indexOf(w) > -1) score += 1; }});
        if (words.some(function (w) {{ return s.indexOf(w) < 0 && t.indexOf(w) < 0; }})) score = 0;
        return {{ e: e, score: score }};
      }}).filter(function (h) {{ return h.score > 0; }}).sort(function (a, b) {{ return b.score - a.score; }}).slice(0, 14);
      box.innerHTML = hits.length ? hits.map(function (h) {{
        return '<a href="' + esc(h.e.u) + '"><b>' + esc(h.e.s) + '</b><small>' + esc(h.e.g) + ', ' + esc(h.e.p) + '</small></a>';
      }}).join('') : '<p class="none">Nothing found. Try another word, or email admintotality@gmail.com.</p>';
      box.hidden = false;
    }});
  }}
  input.addEventListener('input', run);
  input.addEventListener('focus', function () {{ load(); if (input.value.trim().length > 1) run(); }});
  document.addEventListener('click', function (e) {{ if (!box.contains(e.target) && e.target !== input) box.hidden = true; }});
  input.addEventListener('keydown', function (e) {{ if (e.key === 'Escape') box.hidden = true; if (e.key === 'Enter') {{ var f = box.querySelector('a'); if (f) location.href = f.href; }} }});
}})();
</script>
<script src="/js/nav.js" defer></script>
<script src="/js/track.js" defer></script>
</body>
</html>
''')

if __name__ == '__main__':
    keys = sys.argv[1:] or sorted(p.name for p in SRC.iterdir() if p.is_dir() and (p / 'guide.json').exists())
    done = []
    for k in keys:
        cfg, n = build_guide(k)
        done.append((k, cfg)); print(f'{k}: {n} pages')
    order = ['totality-owner', 'totality-trainer', 'totality-client', 'nutrition', 'training', 'tali-hq']
    allk = sorted([p.name for p in SRC.iterdir() if p.is_dir() and (p / 'guide.json').exists()], key=lambda k: order.index(k) if k in order else 99)
    # HIDDEN (25 Nov 2026, Taj): the Tali HQ guide is still built but not listed on the hub for now.
    hub_hidden = {'tali-hq'}
    build_hub([(k, json.loads((SRC / k / 'guide.json').read_text())) for k in allk if k not in hub_hidden])
