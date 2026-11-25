"""Free guides for coaches (the Coach's Starter Series), rebuilt 25 Nov 2026 in the setup guide look.
Source: <slug>.md (front matter: title, kicker, lede, number, file). Build: python3 build.py [slug]
Writes /guides/<file>.pdf. Markdown extras:
  # Chapter title        a new chapter (numbered), starts on a new page
  :::box Title ... :::   an orange note box
  - [ ] item             checklist item
  ?? Mistake :: why      a common mistake row
Rules (Taj): Australian English, no dashes, plain and direct, detailed but simple, no upselling."""
import re, sys, os, html, subprocess, pathlib, markdown
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / 'guides'
SERIES = [('how-to-start', 'How to start a personal training business'), ('marketing', 'Marketing and finding clients'),
          ('how-to-program', 'How to write a training programme'), ('nutrition', 'Nutrition coaching fundamentals')]

def fm(t):
    meta = {}
    if t.startswith('---'):
        end = t.find('\n---', 3)
        for line in t[3:end].strip().splitlines():
            k, v = line.split(':', 1); meta[k.strip()] = v.strip()
        t = t[end + 4:]
    return meta, t

def body(md):
    out, lines, i, ch = [], md.splitlines(), 0, 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('# '):
            ch += 1
            out.append(f'<div class="chap"><span class="cn">{ch:02d}</span><div><span class="ck">Chapter {ch}</span><h1>{html.escape(l[2:].strip())}</h1></div></div>')
            i += 1; continue
        m = re.match(r'^:::box\s*(.*)$', l)
        if m:
            b = []; i += 1
            while lines[i].strip() != ':::': b.append(lines[i]); i += 1
            i += 1
            out.append(f'<div class="box"><b>{html.escape(m.group(1))}</b>{markdown.markdown(chr(10).join(b))}</div>'); continue
        if l.startswith('- [ ] '):
            items = []
            while i < len(lines) and lines[i].startswith('- [ ] '): items.append(lines[i][6:]); i += 1
            out.append('<ul class="check">' + ''.join(f'<li>{markdown.markdown(x)[3:-4]}</li>' for x in items) + '</ul>'); continue
        if l.startswith('?? '):
            rows = []
            while i < len(lines) and lines[i].startswith('?? '):
                a, b2 = lines[i][3:].split('::', 1); rows.append((a.strip(), b2.strip())); i += 1
            out.append('<div class="mist">' + ''.join(f'<div><b>{html.escape(a)}</b><span>{markdown.markdown(b2)[3:-4]}</span></div>' for a, b2 in rows) + '</div>'); continue
        out.append(l); i += 1
    h = markdown.markdown('\n'.join(out), extensions=['tables', 'md_in_html'])
    # keep each chapter heading with the first thing under it
    return re.sub(r'(<div class="chap">.*?</h1></div></div>)\s*(<(p|ul|ol|table)>.*?</\3>)', r'<div class="keep">\1\2</div>', h, flags=re.S)

def build(slug):
    meta, md = fm((HERE / f'{slug}.md').read_text())
    n = int(meta['number'])
    chapters = re.findall(r'^# (.+)$', md, re.M)
    toc = ''.join(f'<li><span>{k+1:02d}</span>{html.escape(c)}</li>' for k, c in enumerate(chapters))
    others = ''.join(f'<li>{html.escape(t)}</li>' for s, t in SERIES if s != slug)
    css = (HERE / 'free.css').read_text()
    doc = f'''<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>{html.escape(meta['title'])}</title><style>{css}</style></head><body>
<section class="cover"><div class="brand"><img src="icon-totality.png" alt=""><span>Totality <i>360</i></span></div>
<div class="ctext"><p class="kick">Free guide {n} of 4 · {html.escape(meta['kicker'])}</p><h1 class="ct">{html.escape(meta['title'])}</h1><p class="lede">{html.escape(meta['lede'])}</p></div>
<div class="inside"><p class="kick">In this guide</p><ol>{toc}</ol></div>
<p class="cfoot">The Coach's Starter Series · free from totality360.com.au · Australia, November 2026</p></section>
<main>{body(md)}
<section class="end"><h2>About this guide</h2>
<p>This guide is free from Totality 360, an Australian software company. We make Totality, the app personal trainers, studios and gyms use to run their business: programmes, sessions, check-ins, bookings and payments, with a free app for their clients. We also make Totality Nutrition, a food and macro tracker.</p>
<p><b>More in the series:</b></p><ul>{others}</ul><p>All free at <b>totality360.com.au/resources</b>. Step by step guides for the apps are at <b>totality360.com.au/help</b>.</p>
<p class="small">General information only, not legal, financial, medical or dietary advice. Rules and research change, so check current requirements with the body named in each section before you act on them. © 2026 Totality 360 Pty Ltd, ABN 58 698 902 975.</p></section></main></body></html>'''
    src = HERE / f'_{slug}.html'; src.write_text(doc)
    out = OUT / meta['file']
    subprocess.run(['node', str(HERE / 'pdf.js'), str(src), str(out), meta['title']], check=True)
    print(out)

if __name__ == '__main__':
    for s in (sys.argv[1:] or [s for s, _ in SERIES]): build(s)
