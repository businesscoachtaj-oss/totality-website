#!/usr/bin/env python3
"""Build the exercise pages from the Totality exercise library.

Writes:
  exercises/index.html                 search box, muscles and equipment
  exercises/<exercise>.html            one page per exercise in the global library
  exercises/muscle/<muscle>.html       every exercise for a muscle group
  exercises/equipment/<kit>.html       every exercise for a piece of equipment

Data: data/exercises.json, the global exercises (is_global = true) from the Totality
exercises table (Livewell Supabase project). Re-export when the library changes.
Images are the branded thumbnails in the public exercise-thumbnails bucket.

After building, run:  python3 tools/apply_chrome.py   then   python3 tools/build_sitemap.py

Usage: python3 tools/build_exercise_pages.py
"""
import html
import json
import os
import re
import shutil
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://totality360.com.au'
e = html.escape

RAW = json.load(open(os.path.join(ROOT, 'data/exercises.json'), encoding='utf-8'))

# ── Cleaning ─────────────────────────────────────────────────────────────────
def clean(s):
    """House style: no em or en dashes, tidy spaces."""
    if not s:
        return ''
    s = re.sub(r'(\d)\s*[–—]\s*(\d)', r'\1 to \2', s)
    s = re.sub(r'\s*[–—]\s*', ': ', s, count=1)
    s = re.sub(r'\s*[–—]\s*', ', ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:1].upper() + s[1:]

def clean_cues(cues):
    out = []
    for c in cues or []:
        c = (c or '').strip()
        if not c:
            continue
        if out and c[:1].islower():
            out[-1] = out[-1].rstrip('.') + ', ' + c
        else:
            out.append(c)
    return [clean(c).rstrip('.') for c in out]

MUSCLE_ALIAS = {'Quads': 'Quadriceps', 'Abs': 'Core', 'Lower Abs': 'Core', 'Upper Abs': 'Core', 'Lat': 'Lats',
                'Delts': 'Shoulders', 'Hip flexors': 'Hip Flexors', 'Calf': 'Calves', 'Glute': 'Glutes', 'Hamstring': 'Hamstrings'}
EQUIP_ALIAS = {'Dumbbells': 'Dumbbell', 'Band': 'Resistance Band', 'Bands': 'Resistance Band', 'Kettlebells': 'Kettlebell',
               'Cables': 'Cable', 'Cable Machine': 'Cable', 'Barbells': 'Barbell', 'None': 'Bodyweight', 'No Equipment': 'Bodyweight'}
LOAD = {'external_weight': 'Weights', 'bodyweight': 'Bodyweight', 'banded': 'Resistance band', 'banded_external': 'Band and weights'}
GOAL = {'hypertrophy': 'Muscle growth', 'strength': 'Strength', 'endurance': 'Endurance', 'power': 'Power', 'mobility': 'Mobility',
        'rehab': 'Rehab', 'fat_loss': 'Fat loss', 'stability': 'Stability', 'conditioning': 'Conditioning', 'flexibility': 'Flexibility',
        'recovery': 'Recovery', 'athletic': 'Athletic performance', 'general': 'General fitness'}

def slugify(s):
    s = s.lower().replace('&', ' and ').replace("'", '').replace('+', ' plus ')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:80].strip('-')

def uniq(xs):
    seen, out = set(), []
    for x in xs:
        if x and x not in seen:
            seen.add(x); out.append(x)
    return out

def parse_reps(s):
    """'Strength: 4-6 reps | Hypertrophy: 8-15 reps | 3-4 sets' -> rows and a sets line."""
    rows, extra = [], []
    for part in (s or '').split('|'):
        part = clean(part)
        if not part:
            continue
        m = re.match(r'^([A-Za-z /]+):\s*(.+)$', part)
        if m:
            g = m.group(1).strip()
            rows.append(({'Hypertrophy': 'Muscle growth'}.get(g, g), m.group(2).strip()))
        else:
            extra.append(part)
    return rows, extra

EX = []
used = {'index'}
for r in RAW:
    name = clean(r['name'])
    slug = slugify(name)
    richness = sum(len(r.get(k) or '') for k in ('description', 'why', 'form_cues')) + len(r.get('cues') or [])
    if slug in used:
        # Same exercise saved twice with different spelling (Push Up / Push-Up): keep the fuller one.
        prev = next(x for x in EX if x['slug'] == slug)
        if prev['_rich'] >= richness:
            continue
        EX.remove(prev)
    used.add(slug)
    muscles = uniq([MUSCLE_ALIAS.get(m.strip(), m.strip()) for m in (r['muscles'] or [])])
    equipment = uniq([EQUIP_ALIAS.get(x.strip(), x.strip()) for x in (r['equipment'] or [])])
    steps = [clean(x).rstrip('.') for x in re.split(r',\s*(?![^()]*\))', r['form_cues'] or '') if x.strip()] if r.get('form_cues') else []
    video = r.get('video') or ''
    EX.append(dict(
        _rich=richness, id=r['id'], name=name, slug=slug, desc=clean(r['description']), why=clean(r['why']),
        muscles=muscles, equipment=equipment or ['Bodyweight'] if r.get('load') == 'bodyweight' else equipment,
        thumb=r.get('thumb') or '', own_video=video if 'supabase.co' in video else '', yt=video if 'youtu' in video else '',
        steps=steps, cues=clean_cues(r['cues']), reps=parse_reps(r['reps']),
        difficulty=(r.get('difficulty') or '').capitalize(), load=LOAD.get(r.get('load') or '', ''),
        goals=uniq([GOAL.get(g, g.replace('_', ' ').capitalize()) for g in (r.get('goal') or [])]),
    ))
EX.sort(key=lambda x: x['name'].lower())

BY_MUSCLE, BY_EQUIP = defaultdict(list), defaultdict(list)
for x in EX:
    for m in x['muscles']:
        BY_MUSCLE[m].append(x)
    for q in x['equipment']:
        BY_EQUIP[q].append(x)
MUSCLE_HUBS = {m: slugify(m) for m, xs in BY_MUSCLE.items() if len(xs) >= 8}
EQUIP_HUBS = {q: slugify(q) for q, xs in BY_EQUIP.items() if len(xs) >= 6 and q not in ('Anchor Point', 'Wall')}
NOT_MUSCLES = {'Balance', 'Power', 'Stability', 'Cardiovascular', 'Full Body'}
EQUIP_WHAT = {'Bodyweight': 'with just your bodyweight', 'Machine': 'on gym machines', 'Cable': 'on a cable machine', 'Smith Machine': 'on a Smith machine', 'Bench': 'using a bench', 'Incline Bench': 'on an incline bench', 'Decline Bench': 'on a decline bench', 'Rack': 'in a rack', 'Box': 'with a box', 'Pull-up Bar': 'on a pull-up bar'}

# ── Page shell ───────────────────────────────────────────────────────────────
STYLE = """
  .ex-hero { display: grid; grid-template-columns: minmax(0, 1fr) 380px; gap: var(--s-7); align-items: start; }
  .ex-hero > *, .ex-cta > * { min-width: 0; }
  .ex-hero h1 { max-width: 20ch; }
  .ex-media { margin: 0; background: #fff; border: 1px solid var(--line); border-radius: var(--radius-lg); overflow: hidden; }
  .ex-media img, .ex-media video { display: block; width: 100%; height: auto; aspect-ratio: 1 / 1; object-fit: cover; background: #fff; }
  .ex-media figcaption { padding: 10px 14px; font-size: var(--fs-sm); color: var(--muted); border-top: 1px solid var(--line); }
  .ex-facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s-3); margin: var(--s-5) 0; }
  .ex-fact { background: #fff; border: 1px solid var(--line); border-radius: var(--radius); padding: var(--s-3) var(--s-4); }
  .ex-fact span { display: block; font-size: var(--fs-xs); font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); }
  .ex-fact b { display: block; margin-top: 2px; }
  .ex-fact a { color: inherit; }
  .ex-steps { counter-reset: ex; list-style: none; padding: 0; margin: 0; display: grid; gap: var(--s-3); }
  .ex-steps li { counter-increment: ex; display: grid; grid-template-columns: 36px 1fr; gap: var(--s-3); align-items: start; }
  .ex-steps li::before { content: counter(ex); width: 36px; height: 36px; border-radius: 50%; background: var(--orange); color: #fff; font-family: var(--font-display); font-weight: 800; display: grid; place-items: center; }
  .ex-steps li span { padding-top: 6px; }
  .ex-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: var(--s-4); }
  .ex-card { display: block; background: #fff; border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; text-decoration: none; color: var(--ink); }
  .ex-card:hover { border-color: var(--orange); }
  .ex-card img { display: block; width: 100%; height: auto; aspect-ratio: 1 / 1; object-fit: cover; background: var(--orange-50); }
  .ex-card b { display: block; padding: 10px 12px 2px; font-size: var(--fs-sm); }
  .ex-card small { display: block; padding: 0 12px 12px; color: var(--muted); font-size: var(--fs-xs); }
  .ex-links { display: flex; flex-wrap: wrap; gap: var(--s-2); }
  .ex-links a { text-decoration: none; }
  .ex-search { width: 100%; font: inherit; font-size: var(--fs-md); padding: 14px 18px; border: 2px solid var(--line-strong); border-radius: var(--radius-pill); background: #fff; color: var(--ink); }
  .ex-search:focus { outline: none; border-color: var(--orange); }
  .ex-results { list-style: none; margin: var(--s-4) 0 0; padding: 0; display: grid; gap: 2px; }
  .ex-results a { display: flex; justify-content: space-between; gap: var(--s-3); padding: 10px 14px; border-radius: var(--radius-sm); text-decoration: none; color: var(--ink); background: #fff; border: 1px solid var(--line); }
  .ex-results a:hover { border-color: var(--orange); }
  .ex-results small { color: var(--muted); text-align: right; }
  .ex-cta { display: grid; grid-template-columns: minmax(0, 1fr) 240px; gap: var(--s-6); align-items: center; }
  .ex-cta img { width: 100%; height: 480px; object-fit: cover; object-position: top; border-radius: var(--radius); border: 1px solid var(--line-strong); }
  .ex-note { font-size: var(--fs-xs); color: var(--muted); max-width: 72ch; }
  .table td.n, .table th.n { white-space: nowrap; }
  @media (max-width: 900px) { .ex-hero, .ex-cta { grid-template-columns: minmax(0, 1fr); } .ex-hero .ex-media { max-width: 420px; } .ex-cta img { max-width: 240px; height: 420px; } }
  @media (max-width: 480px) { .ex-facts { grid-template-columns: minmax(0, 1fr); } .ex-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
"""

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

def page(title, desc, path, crumbs, body, schema=(), script='', image=None):
    sch = '\n'.join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    crumb_html = ' / '.join(f'<a href="{u}">{e(n)}</a>' if u else e(n) for n, u in crumbs)
    og = image or f'{BASE}/og-image.png'
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
{PIXEL}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<link rel="icon" href="/favicon-96.png" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon-180.png">
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Totality 360">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:image" content="{e(og)}">
<meta name="twitter:card" content="summary_large_image">
<!-- chrome:head -->
<!-- /chrome:head -->
<link rel="stylesheet" href="/css/site.css">
<style>{STYLE}</style>
{sch}
</head>
<body data-brand="totality">
<!-- chrome:header -->
<!-- /chrome:header -->
<main id="main" class="theme-totality">
<section class="page-hero page-hero--tint">
  <div class="container">
    <p class="crumbs">{crumb_html}</p>
{body}
</main>
<!-- chrome:footer -->
<!-- /chrome:footer -->
{script}
<script src="/js/nav.js" defer></script>
</body>
</html>
"""

def crumbs_schema(c):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, **({"item": BASE + u} if u else {})} for i, (n, u) in enumerate(c)]}

def faq_html(items):
    inner = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(items))
    return f'<div class="faq">{inner}</div>'

def faq_schema(items):
    strip = lambda s: html.unescape(re.sub('<[^>]+>', '', s))
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]}

def join_words(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' and ' + xs[-1]

CTA = """<section class="section section--tint">
  <div class="container ex-cta">
    <div>
      <h2>Programme it for your clients in Totality</h2>
      <p class="lead">Totality is the app for personal trainers, gyms and allied health. Every exercise in this library is built in, so you can drop it into a client’s programme, and Tali can draft a whole programme for you to check before it goes out.</p>
      <div class="btn-row"><a class="btn btn--primary btn--lg" href="/get-totality.html">Start your free trial</a><a class="btn btn--ghost" href="/for-pts.html">Totality for trainers</a></div>
    </div>
    <img src="/img/app/t_client.webp" alt="A client’s profile and programme in Totality" width="780" height="1688" loading="lazy">
  </div>
</section>"""

def card(x):
    sub = join_words(x['muscles'][:2]) if x['muscles'] else (x['equipment'][0] if x['equipment'] else '')
    img = f'<img src="{e(x["thumb"])}" alt="" loading="lazy" width="400" height="400">' if x['thumb'] else '<img alt="" width="400" height="400">'
    return f'<a class="ex-card" href="/exercises/{x["slug"]}.html">{img}<b>{e(x["name"])}</b><small>{e(sub)}</small></a>'

def tail(title, links):
    return f"""<section class="section section--tight">
  <div class="container">
    {f'<h2 style="font-size:var(--fs-md)">{title}</h2><div class="ex-links">{links}</div>' if links else ''}
    <p class="ex-note mt-5">General information only. Check with a doctor or physio before starting a new exercise if you have an injury or a health condition.</p>
  </div>
</section>"""

def muscle_link(m):
    return f'<a href="/exercises/muscle/{MUSCLE_HUBS[m]}.html">{e(m)}</a>' if m in MUSCLE_HUBS else e(m)

def equip_link(q):
    return f'<a href="/exercises/equipment/{EQUIP_HUBS[q]}.html">{e(q)}</a>' if q in EQUIP_HUBS else e(q)

# ── Exercise pages ───────────────────────────────────────────────────────────
def exercise_page(x):
    crumbs = [('Totality', '/totality.html'), ('Exercises', '/exercises/')]
    if x['muscles'] and x['muscles'][0] in MUSCLE_HUBS:
        crumbs.append((x['muscles'][0], f'/exercises/muscle/{MUSCLE_HUBS[x["muscles"][0]]}.html'))
    crumbs.append((x['name'], None))
    if x['own_video']:
        media = (f'<figure class="ex-media"><video controls playsinline preload="none" poster="{e(x["thumb"])}" src="{e(x["own_video"])}"></video>'
                 f'<figcaption>{e(x["name"])}, from the Totality exercise library</figcaption></figure>')
    elif x['thumb']:
        media = f'<figure class="ex-media"><img src="{e(x["thumb"])}" alt="{e(x["name"])}" width="800" height="800"><figcaption>{e(x["name"])}, from the Totality exercise library</figcaption></figure>'
    else:
        media = ''
    facts = []
    if x['muscles']:
        facts.append(('Works', ', '.join(muscle_link(m) for m in x['muscles'])))
    if x['equipment']:
        facts.append(('Equipment', ', '.join(equip_link(q) for q in x['equipment'])))
    if x['difficulty']:
        facts.append(('Level', e(x['difficulty'])))
    if x['goals']:
        facts.append(('Good for', e(', '.join(x['goals']))))
    facts_html = ''.join(f'<div class="ex-fact"><span>{k}</span><b>{v}</b></div>' for k, v in facts)
    lead = e(x['desc']) if x['desc'] else f'{e(x["name"])} is an exercise from the Totality library.'
    if x['muscles'] and x['desc'] and not any(m.lower() in x['desc'].lower() for m in x['muscles']):
        lead += f' It works the {e(join_words([m.lower() for m in x["muscles"][:3]]))}.'
    secs = []
    if x['why']:
        secs.append(f"""<div class="section-head"><h2>Why it works</h2></div><p class="lead" style="margin:0">{e(x['why'])}</p>""")
    if x['steps']:
        steps = ''.join(f'<li><span>{e(s)}</span></li>' for s in x['steps'])
        secs.append(f'<div class="section-head"><h2>How to do it</h2></div><ol class="ex-steps">{steps}</ol>')
    if x['cues']:
        cues = ''.join(f'<li>{e(c)}</li>' for c in x['cues'])
        secs.append(f'<div class="section-head"><h2>Coaching cues</h2></div><ul class="ticks ticks--orange">{cues}</ul>')
    rows, extra = x['reps']
    if rows or extra:
        trs = ''.join(f'<tr><td>{e(a)}</td><td class="n"><b>{e(b)}</b></td></tr>' for a, b in rows)
        extra = [('Aim for ' + t) if not rows and re.match(r'^\d', t) else t for t in extra]
        secs.append(f"""<div class="section-head"><h2>Sets and reps</h2><p class="section-sub">A starting point. Adjust to the person in front of you.</p></div>
    {f'<div class="table-wrap"><table class="table" style="min-width:0"><thead><tr><th>Goal</th><th class="n">Reps</th></tr></thead><tbody>{trs}</tbody></table></div>' if trs else ''}
    {''.join(f'<p class="mt-4" style="margin-bottom:0">{e(t)}.</p>' for t in extra)}""")
    if x['yt']:
        secs.append(f"""<p style="margin:0"><a class="text-link" href="{e(x['yt'])}" rel="noopener nofollow" target="_blank">Watch a video demo of the {e(x['name'].lower() if not x['name'][:2].isupper() else x['name'])} on YouTube</a></p>""")

    sections = ''.join(f'<section class="section{" section--tint" if i % 2 else ""}"><div class="container container--narrow">{c}</div></section>' for i, c in enumerate(secs))
    pool = {}
    for m in x['muscles'][:3]:
        for y in BY_MUSCLE[m]:
            if y is not x:
                pool[y['slug']] = y
    def overlap(y):
        return (-len(set(y['muscles'][:3]) & set(x['muscles'][:3])) * 2 - (y['muscles'][:1] == x['muscles'][:1]) * 3
                - len(set(y['equipment']) & set(x['equipment'])), y['name'].lower())
    rel = sorted(pool.values(), key=overlap)[:8]
    related = ''
    if rel:
        related = f"""<section class="section"><div class="container">
    <div class="section-head"><h2>More exercises for the {e(join_words([m.lower() for m in x['muscles'][:2]]))}</h2></div>
    <div class="ex-grid">{''.join(card(y) for y in rel)}</div></div></section>"""

    faqs = []
    if x['muscles']:
        faqs.append((f'What muscles does the {x["name"].lower() if not x["name"][:2].isupper() else x["name"]} work?',
                     f'Mainly the {e(join_words([m.lower() for m in x["muscles"]]))}.'))
    if rows:
        faqs.append(('How many sets and reps should I do?', e('; '.join(f'{a}: {b}' for a, b in rows)) + (f'. {e(" ".join(extra))}' if extra else '.')))
    if x['equipment']:
        faqs.append(('What equipment do I need?', e(join_words([q.lower() if q != 'EZ-Bar' else q for q in x['equipment']])).capitalize() + '.'))
    if x['difficulty']:
        faqs.append(('Is it good for beginners?', {'Beginner': 'Yes. It’s rated as a beginner exercise.',
                                                   'Intermediate': 'It’s rated intermediate. Learn the basic version of the movement first, and start light.',
                                                   'Advanced': 'It’s rated advanced. Build up to it with easier versions, and get coaching on your form first.'}.get(x['difficulty'], f'It’s rated {e(x["difficulty"].lower())}.')))
    faq_sec = f"""<section class="section section--tint"><div class="container container--narrow">
    <div class="section-head"><h2>Questions people ask</h2></div>{faq_html(faqs)}</div></section>""" if faqs else ''

    hubs = ''.join(f'<a class="pill pill--orange" href="/exercises/muscle/{MUSCLE_HUBS[m]}.html">{e(m)} exercises</a>' for m in x['muscles'] if m in MUSCLE_HUBS)
    hubs += ''.join(f'<a class="pill pill--orange" href="/exercises/equipment/{EQUIP_HUBS[q]}.html">{e(q)} exercises</a>' for q in x['equipment'] if q in EQUIP_HUBS)
    hubs += '<a class="pill pill--ink" href="/exercises/">All exercises</a>'
    body = f"""    <div class="ex-hero">
      <div>
        <p class="kicker">Exercise library</p>
        <h1>{e(x['name'])}: how to do it and muscles worked</h1>
        <p class="lead">{lead}</p>
        <div class="ex-facts">{facts_html}</div>
      </div>
      {media}
    </div>
  </div>
</section>
{sections}
{related}
{faq_sec}
{CTA}
{tail('Browse more', hubs)}"""
    mw = join_words([m.lower() for m in x['muscles'][:3]]) if x['muscles'] else ''
    desc = f'How to do the {x["name"].lower() if not x["name"][:2].isupper() else x["name"]}' + (f', the muscles it works ({mw})' if mw else '') + ', coaching cues and sets and reps. From the Totality exercise library.'
    title = f'{x["name"]}: how to do it, muscles worked and coaching cues | Totality'
    return page(title, desc, f'/exercises/{x["slug"]}.html', crumbs, body, [faq_schema(faqs), crumbs_schema(crumbs)] if faqs else [crumbs_schema(crumbs)], image=x['thumb'] or None)

# ── Hubs and index ───────────────────────────────────────────────────────────
def hub_page(kind, label, slug, xs):
    path = f'/exercises/{kind}/{slug}.html'
    crumbs = [('Totality', '/totality.html'), ('Exercises', '/exercises/'), (f'{label} exercises', None)]
    levels = defaultdict(list)
    for x in xs:
        levels[x['difficulty'] or 'Other'].append(x)
    secs = ''
    for lv in ['Beginner', 'Intermediate', 'Advanced', 'Other']:
        if levels.get(lv):
            secs += f'<div class="section-head mt-5"><h2>{lv}</h2></div><div class="ex-grid">{"".join(card(x) for x in levels[lv])}</div>'
    others = MUSCLE_HUBS if kind == 'muscle' else EQUIP_HUBS
    links = ''.join(f'<a class="pill pill--orange" href="/exercises/{kind}/{s}.html">{e(m)}</a>' for m, s in sorted(others.items()) if s != slug)
    if kind == 'muscle':
        what = f'for {label.lower()}' if label in NOT_MUSCLES else f'for the {label.lower()}'
    else:
        what = EQUIP_WHAT.get(label, f'with a {label.lower()}')
    body = f"""    <p class="kicker">Exercise library</p>
    <h1>{e(label)} exercises</h1>
    <p class="lead">{len(xs)} exercises {e(what)}, from beginner to advanced, with how to do each one, coaching cues and sets and reps.</p>
  </div>
</section>
<section class="section"><div class="container">{secs}</div></section>
{CTA}
{tail('Other ' + ('muscle groups' if kind == 'muscle' else 'equipment'), links)}"""
    desc = f'{len(xs)} {label.lower()} exercises {what}, with how to do each one, the muscles worked, coaching cues and sets and reps.'
    return page(f'{label} exercises: {len(xs)} exercises with how-to and coaching cues | Totality', desc, path, crumbs, body, [crumbs_schema(crumbs)])

def index_page():
    crumbs = [('Totality', '/totality.html'), ('Exercises', None)]
    mus = ''.join(f'<a class="pill pill--orange" href="/exercises/muscle/{s}.html">{e(m)} <small>({len(BY_MUSCLE[m])})</small></a>' for m, s in sorted(MUSCLE_HUBS.items(), key=lambda kv: -len(BY_MUSCLE[kv[0]])))
    eqp = ''.join(f'<a class="pill pill--orange" href="/exercises/equipment/{s}.html">{e(q)} <small>({len(BY_EQUIP[q])})</small></a>' for q, s in sorted(EQUIP_HUBS.items(), key=lambda kv: -len(BY_EQUIP[kv[0]])))
    idx = [[x['name'], x['slug'], ', '.join(x['muscles'][:2])] for x in EX]
    body = f"""    <p class="kicker">Exercise library</p>
    <h1>{len(EX)} exercises with how-to, muscles and coaching cues</h1>
    <p class="lead">The full Totality exercise library, free to browse. Search for an exercise, or pick a muscle group or a piece of equipment.</p>
    <input class="ex-search mt-5" id="exQ" type="search" placeholder="Search exercises, like squat, curl or plank" aria-label="Search exercises" autocomplete="off">
    <ul class="ex-results" id="exR"></ul>
  </div>
</section>
<section class="section"><div class="container">
  <div class="section-head"><h2>By muscle group</h2></div><div class="ex-links">{mus}</div>
  <div class="section-head mt-5"><h2>By equipment</h2></div><div class="ex-links">{eqp}</div>
</div></section>
{CTA}
{tail('', '')}"""
    script = f"""<script>
(function () {{
  var I = {json.dumps(idx, separators=(',', ':'), ensure_ascii=False)};
  var q = document.getElementById('exQ'), out = document.getElementById('exR');
  function esc(s) {{ return s.replace(/[&<>"]/g, function (c) {{ return {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }}[c]; }}); }}
  q.addEventListener('input', function () {{
    var t = q.value.trim().toLowerCase().split(/\\s+/).filter(Boolean);
    if (!t.length) {{ out.innerHTML = ''; return; }}
    var hits = I.filter(function (r) {{ var n = (r[0] + ' ' + r[2]).toLowerCase(); return t.every(function (w) {{ return n.indexOf(w) >= 0; }}); }});
    hits.sort(function (a, b) {{ return a[0].toLowerCase().indexOf(t[0]) - b[0].toLowerCase().indexOf(t[0]) || a[0].length - b[0].length; }});
    out.innerHTML = hits.slice(0, 30).map(function (r) {{ return '<li><a href="/exercises/' + r[1] + '.html"><span>' + esc(r[0]) + '</span><small>' + esc(r[2]) + '</small></a></li>'; }}).join('') || '<li class="muted">No exercises match that. Try a shorter word.</li>';
  }});
}})();
</script>"""
    return page('Exercise library: how to do 750+ exercises, muscles worked and coaching cues | Totality',
                f'Free exercise library with {len(EX)} exercises. How to do each one, the muscles it works, coaching cues and sets and reps, by muscle group and equipment.',
                '/exercises/', crumbs, body, [crumbs_schema(crumbs)], script)

def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def main():
    shutil.rmtree(os.path.join(ROOT, 'exercises'), ignore_errors=True)
    for x in EX:
        write(f'exercises/{x["slug"]}.html', exercise_page(x))
    for m, s in MUSCLE_HUBS.items():
        write(f'exercises/muscle/{s}.html', hub_page('muscle', m, s, BY_MUSCLE[m]))
    for q, s in EQUIP_HUBS.items():
        write(f'exercises/equipment/{s}.html', hub_page('equipment', q, s, BY_EQUIP[q]))
    write('exercises/index.html', index_page())
    print(f'{len(EX)} exercise pages, {len(MUSCLE_HUBS)} muscle pages, {len(EQUIP_HUBS)} equipment pages')

if __name__ == '__main__':
    main()
