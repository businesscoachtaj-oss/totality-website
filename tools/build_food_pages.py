#!/usr/bin/env python3
"""Build the food and nutrient pages for Totality Nutrition from Australian food data.

Writes:
  foods/index.html             search box and categories
  foods/<category>.html        every food in a category
  foods/<food>.html            one page per food, cooking methods grouped together
  nutrients/index.html         every nutrient
  nutrients/<nutrient>.html    what it does, how much you need, foods highest in it

Data:
  data/afcd_foods.json      every food in the Totality Nutrition foods table with source 'afcd'
                            (Australian Food Composition Database, Release 3, FSANZ), per 100 g.
                            Re-export from Supabase (Livewell project) when the table changes.
  data/nutrient_info.json   lib/nutrientInfo.ts and lib/nutrients.ts from the Nutrition app
                            (what each nutrient does, why you need it, foods, daily targets).

The AFCD Data User Licence (CC BY-SA 3.0 AU based) needs, on every page that shows the data:
credit to FSANZ and the database title, a link to the licence, the Limitation of Data
Statement in full, a note that it is Australian data, a note of what we changed, the same
licence for the figures we share, and no hint that FSANZ endorses us. CREDIT below does that.

After building, run:  python3 tools/apply_chrome.py   then   python3 tools/build_sitemap.py

Usage: python3 tools/build_food_pages.py
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

FOODS = json.load(open(os.path.join(ROOT, 'data/afcd_foods.json'), encoding='utf-8'))
NI = json.load(open(os.path.join(ROOT, 'data/nutrient_info.json'), encoding='utf-8'))

LICENCE_URL = 'https://www.foodstandards.gov.au/science-data/monitoringnutrients/afcd/datauserlicenceagreement'
NRV_URL = 'https://www.eatforhealth.gov.au/nutrient-reference-values'

CREDIT = f"""<div class="fd-credit">
  <p><strong>Where these numbers come from.</strong> Nutrition figures are from the Australian Food Composition Database (AFCD), Release 3, © Food Standards Australia New Zealand (FSANZ), used under the <a href="{LICENCE_URL}" rel="noopener">AFCD Data User Licence</a>. The figures on this page are shared under the same licence. We rounded the values, converted energy to calories as well as kilojoules, grouped cooking methods for the same food together and worked out amounts for other weights. This site is not endorsed by or connected with FSANZ.</p>
  <p>There are limitations associated with food composition databases. Food composition data used in the database or databases may represent an average of the nutrient content of a particular sample of foods and ingredients, determined at a particular time. The nutrient composition of foods and ingredients can vary substantially between batches and brands because of a number of factors, including changes in season, processing practices and ingredient source, and methods of calculation.</p>
  <p>The AFCD is based on Australian data and may not be appropriate for use in other countries. General information only, not medical or dietary advice.</p>
</div>"""

# ── Nutrients ─────────────────────────────────────────────────────────────────
UNIT = {'ug': 'µg', 'mg': 'mg', 'g': 'g'}
MICRO_DEFS = {d['key']: d for d in NI['vitamins'] + NI['minerals']}
DI = NI['daily']

# slug, label, data key in a food row, unit, target, basis text, info key, kind
NUTRIENTS = []
def add_n(slug, label, key, unit, target, basis, info, kind):
    NUTRIENTS.append(dict(slug=slug, label=label, key=key, unit=unit, target=target, basis=basis, info=info, kind=kind))

add_n('protein', 'Protein', 'p', 'g', DI['protein_g'], 'label', None, 'goal')
add_n('fibre', 'Fibre', 'fibre', 'g', DI['fibre_g'], 'label', 'fibre', 'goal')
add_n('sugar', 'Sugar', 'sugar', 'g', DI['sugar_g'], 'label', 'sugar', 'limit')
add_n('saturated-fat', 'Saturated fat', 'sat', 'g', DI['saturated_fat_g'], 'label', 'saturatedFat', 'limit')
add_n('sodium', 'Sodium', 'na', 'mg', DI['sodium_mg'], 'label', 'sodium', 'limit')
for k in ['vitamin_a_ug', 'thiamin_mg', 'riboflavin_mg', 'niacin_mg', 'vitamin_b6_mg', 'folate_ug', 'vitamin_b12_ug',
          'vitamin_c_mg', 'vitamin_d_ug', 'vitamin_e_mg', 'calcium_mg', 'iron_mg', 'magnesium_mg', 'phosphorus_mg',
          'potassium_mg', 'zinc_mg', 'iodine_ug', 'selenium_ug']:
    d = MICRO_DEFS[k]
    unit = k.rsplit('_', 1)[1]
    slug = re.sub(r'[^a-z0-9]+', '-', d['label'].lower().replace('(', '').replace(')', '')).strip('-')
    basis = 'potassium' if k == 'potassium_mg' else 'rdi'
    add_n(slug, d['label'], k, unit, d['target'], basis, k, 'goal')
add_n('cholesterol', 'Cholesterol', 'cholesterol_mg', 'mg', None, 'none', 'cholesterol_mg', 'info')
N_BY_KEY = {n['key']: n for n in NUTRIENTS}

PROTEIN_INFO = {
    'does': 'Builds and repairs your muscles and every other tissue in your body, and helps you feel full.',
    'why': 'Your body can’t store protein, so you need some every day. People who train, older adults and people trying to lose weight often do better with a little more.',
    'listKind': 'sources',
    'list': ['Meat, chicken and fish', 'Eggs', 'Milk, yoghurt and cheese', 'Tofu, tempeh, lentils and beans', 'Nuts and seeds'],
}
# Extra daily amounts for adults where we show more than one figure (NHMRC Nutrient Reference Values).
NRV_TABLES = {
    'p': [('Men, 19 to 70', '64 g'), ('Women, 19 to 70', '46 g'), ('Men, over 70', '81 g'), ('Women, over 70', '57 g'), ('Pregnancy, 19 to 50', '60 g')],
    'fibre': [('Men, 19 and over', '30 g'), ('Women, 19 and over', '25 g')],
    'iron_mg': [('Men, 19 and over', '8 mg'), ('Women, 19 to 50', '18 mg'), ('Women, 51 and over', '8 mg'), ('Pregnancy', '27 mg'),
                ('Breastfeeding, 19 to 50', '9 mg'), ('Boys, 14 to 18', '11 mg'), ('Girls, 14 to 18', '15 mg')],
}
NRV_NAME = {'p': 'NHMRC recommended dietary intake', 'fibre': 'NHMRC adequate intake', 'iron_mg': 'NHMRC recommended dietary intake'}

def get(row, key):
    if key in ('p', 'fibre', 'sugar', 'sat', 'na', 'kcal', 'c', 'f'):
        return row.get(key)
    return row['m'].get(key)

def fmt(x, unit=''):
    if x is None:
        return 'no data'
    if x >= 100:
        s = f'{x:,.0f}'
    elif x >= 10:
        s = f'{x:.0f}' if abs(x - round(x)) < 0.05 or x >= 20 else f'{x:.1f}'
    elif x >= 1:
        s = f'{x:.1f}'.rstrip('0').rstrip('.')
    elif x == 0:
        s = '0'
    else:
        s = f'{x:.2f}'.rstrip('0').rstrip('.')
    return f'{s} {UNIT.get(unit, unit)}'.strip()

def kj(kcal):
    return round(kcal * 4.184)

# ── Grouping foods ───────────────────────────────────────────────────────────
PREP = re.compile(r"^(raw|uncooked|cooked|boiled|hard-boiled|soft-boiled|poached|steamed|microwaved|grilled|barbecued|bbq'd|grilled or bbq'd|baked|roasted|roast|fried|deep-fried|pan-fried|stir-fried|shallow-fried|sauteed|casseroled|stewed|braised|simmered|scrambled|toasted|dried|drained|canned|frozen)\b", re.I)
PREP_LATE = re.compile(r'^(no added|added|with |without |in |from |as purchased|peeled|unpeeled|undrained)', re.I)
SKIP = re.compile(r'separable fat', re.I)

def split_top(name):
    """Split on commas that are not inside brackets."""
    out, depth, cur = [], 0, ''
    for ch in name:
        depth += ch == '('
        depth -= ch == ')'
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    out.append(cur.strip())
    return out

def key_of(name):
    parts = split_top(name)
    for i, p in enumerate(parts):
        if i >= 1 and (PREP.match(p) or (i >= 2 and PREP_LATE.match(p))):
            return ', '.join(parts[:i])
    return name

JOIN_HEADS = {'Beef', 'Lamb', 'Pork', 'Chicken', 'Veal', 'Turkey', 'Duck', 'Mutton', 'Goat', 'Kangaroo', 'Buffalo', 'Venison', 'Emu', 'Rabbit', 'Coconut', 'Potato', 'Sweet potato'}
REVERSE_HEADS = {'Bread', 'Cheese', 'Jam', 'Nut', 'Seed', 'Wine', 'Juice', 'Oil', 'Flour', 'Yoghurt', 'Bean', 'Lentil', 'Biscuit', 'Sauce', 'Soft drink', 'Cordial', 'Beer', 'Breakfast cereal', 'Cake', 'Noodle', 'Muffin', 'Spirits', 'Tea', 'Pie', 'Soup', 'Lolly', 'Bar', 'Paste', 'Spread', 'Rice', 'Pasta', 'Sausage', 'Salami', 'Milk', 'Cream', 'Sugar', 'Syrup', 'Vinegar', 'Pastry', 'Pizza', 'Cracker'}
NO_MERGE = re.compile(r'^(from|with|in|made|commercial|homemade|farmed|wild|fresh|canned|frozen|dried|raw|cooked|plain|regular|reduced|full|low|lower|higher|lean|untrimmed|various|all|average|unspecified|not further)\b', re.I)
TITLE_OVERRIDES = {
    'Egg, chicken, whole': 'Eggs',
    'Egg, chicken, white (albumen)': 'Egg white',
    'Egg, chicken, yolk': 'Egg yolk',
    'Egg, chicken, whole, omega-3 polyunsaturate enriched': 'Omega-3 eggs',
}

def cap(s):
    return s[:1].upper() + s[1:]

def title_of(key):
    if key in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[key]
    parts = split_top(key)
    head, rest = parts[0], parts[1:]
    if rest:
        head = re.sub(r'\s*\([^)]*\)', '', head).strip()
        rest = [re.sub(r'\s+', ' ', p.replace('(', '').replace(')', '')).strip() for p in rest]
    if not rest:
        return cap(head)
    second = rest[0]
    short = len(second.split()) <= 3 and not NO_MERGE.match(second) and '(' not in second
    if short and head in REVERSE_HEADS:
        base, rest = f'{cap(second)} {head.lower()}', rest[1:]
    elif short and head in JOIN_HEADS:
        base, rest = f'{head} {second.lower() if second[:1].islower() else second}', rest[1:]
    else:
        base = cap(head)
    return base + (f' ({", ".join(rest)})' if rest else '')

def slugify(s):
    s = s.lower().replace('&', ' and ').replace("'", '')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:80].strip('-')

CATS = {
    'meat-poultry-and-game-products-and-dishes': ('Meat, poultry and game', 'meat-poultry-and-game'),
    'vegetable-products-and-dishes': ('Vegetables', 'vegetables'),
    'cereals-and-cereal-products': ('Grains, rice, pasta and cereals', 'grains-and-cereals'),
    'fruit-products-and-dishes': ('Fruit', 'fruit'),
    'fish-and-seafood-products-and-dishes': ('Fish and seafood', 'fish-and-seafood'),
    'cereal-based-products-and-dishes': ('Bread, cakes, biscuits and pastries', 'bread-cakes-and-biscuits'),
    'non-alcoholic-beverages': ('Drinks', 'drinks'),
    'milk-products-and-dishes': ('Milk, cheese and yoghurt', 'dairy'),
    'seed-and-nut-products-and-dishes': ('Nuts and seeds', 'nuts-and-seeds'),
    'savoury-sauces-and-condiments': ('Sauces and condiments', 'sauces-and-condiments'),
    'fats-and-oils': ('Fats and oils', 'fats-and-oils'),
    'confectionery-and-cereal-nut-fruit-seed-bars': ('Chocolate, lollies and bars', 'chocolate-lollies-and-bars'),
    'dairy-meat-substitutes': ('Plant-based milks and meat alternatives', 'plant-based-alternatives'),
    'miscellaneous': ('Herbs, spices and other foods', 'herbs-spices-and-other'),
    'alcoholic-beverages': ('Alcohol', 'alcohol'),
    'legume-and-pulse-products-and-dishes': ('Beans, lentils and legumes', 'beans-and-lentils'),
    'sugar-products-and-dishes': ('Sugar, honey and spreads', 'sugar-and-honey'),
    'snack-foods': ('Snack foods', 'snack-foods'),
    'egg-products-and-dishes': ('Eggs', 'eggs-and-egg-dishes'),
    'soup': ('Soup', 'soup'),
    'reptiles-amphibia-and-insects': ('Insects and reptiles', 'insects-and-reptiles'),
    'special-dietary-foods': ('Special dietary foods', 'special-dietary-foods'),
    'infant-formulae-and-foods': ('Baby food', 'baby-food'),
}
COOKED_FIRST = {'meat-poultry-and-game-products-and-dishes', 'fish-and-seafood-products-and-dishes', 'egg-products-and-dishes',
                'legume-and-pulse-products-and-dishes', 'cereals-and-cereal-products'}
COOK_ORDER = ['hard-boiled', 'boiled', 'grilled', 'baked', 'roasted', 'cooked', 'poached', 'steamed', 'pan-fried', 'fried', 'stir-fried', 'microwaved']

def variant_label(row, key):
    rest = row['name'][len(key):].lstrip(', ').strip()
    return cap(rest) if rest else 'As sold'

def pick_default(rows, cat):
    def score(r):
        n = r['name'].lower()
        tail = n[len(r['_key']):]
        if cat in COOKED_FIRST:
            for i, w in enumerate(COOK_ORDER):
                if w in tail:
                    return (0, i, len(n))
            return (1 if 'raw' in tail or 'uncooked' in tail else 2, 0, len(n))
        if tail.strip(', ') in ('', 'raw', 'fresh, raw'):
            return (0, 0, len(n))
        if 'unpeeled' in tail and 'raw' in tail:
            return (0, 1, len(n))
        return (1 if 'raw' in tail else 2, 0, len(n))
    return sorted(rows, key=score)[0]

groups = defaultdict(list)
for r in FOODS:
    if SKIP.search(r['name']) or r['kcal'] is None:
        continue
    r['_key'] = key_of(r['name'])
    groups[r['_key']].append(r)

PAGES = []          # one per food page
used = {'index'} | {v[1] for v in CATS.values()}
for key in sorted(groups):
    rows = sorted(groups[key], key=lambda r: r['name'])
    cat = rows[0]['cat']
    title = title_of(key)
    slug = slugify(title)
    n = 2
    while slug in used:
        slug = f'{slugify(title)}-{n}'; n += 1
    used.add(slug)
    PAGES.append(dict(key=key, title=title, slug=slug, cat=cat, rows=rows, default=pick_default(rows, cat)))
PAGE_BY_NAME = {r['name']: p for p in PAGES for r in p['rows']}
BY_CAT = defaultdict(list)
for p in PAGES:
    BY_CAT[p['cat']].append(p)
for c in BY_CAT:
    BY_CAT[c].sort(key=lambda p: p['title'].lower())

# ── Page shell ───────────────────────────────────────────────────────────────
STYLE = """
  .fd-hero { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: var(--s-7); align-items: start; }
  .fd-hero h1 { max-width: 22ch; }
  .fd-hero > *, .fd-cta > * { min-width: 0; }
  .fd-label { background: #fff; border: 2px solid var(--ink); border-radius: var(--radius); padding: var(--s-4) var(--s-5); }
  .fd-label h2 { font-size: var(--fs-xl); margin: 0 0 2px; }
  .fd-label .sub { margin: 0 0 var(--s-3); color: var(--muted); font-size: var(--fs-sm); }
  .fd-amt { display: flex; align-items: center; gap: var(--s-2); margin: 0 0 var(--s-3); font-size: var(--fs-sm); color: var(--ink-2); flex-wrap: wrap; }
  .fd-amt input, .fd-amt select { font: inherit; padding: 6px 10px; border: 1px solid var(--line-strong); border-radius: var(--radius-sm); background: #fff; color: var(--ink); max-width: 100%; }
  .fd-amt input { width: 84px; }
  .fd-amt select { min-width: 0; width: 100%; flex: 1 1 100%; text-overflow: ellipsis; }
  .fd-row { display: flex; justify-content: space-between; gap: var(--s-3); padding: 7px 0; border-top: 1px solid var(--line); font-size: var(--fs-sm); }
  .fd-row b { font-weight: 800; white-space: nowrap; }
  .fd-row.in { padding-left: var(--s-4); color: var(--ink-2); }
  .fd-row.big { border-top: 6px solid var(--ink); font-size: var(--fs-md); }
  .fd-stats { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--s-4); margin: var(--s-5) 0; }
  .fd-stat { background: #fff; border: 1px solid var(--line); border-radius: var(--radius); padding: var(--s-4); }
  .fd-stat .stat-num { color: var(--blue); }
  .fd-bars { display: grid; gap: var(--s-3); }
  .fd-bar { display: grid; grid-template-columns: 150px minmax(0, 1fr) 130px; gap: var(--s-3); align-items: center; font-size: var(--fs-sm); }
  .fd-bar a { color: inherit; }
  .fd-track { display: block; height: 12px; border-radius: 6px; background: var(--blue-50); overflow: hidden; }
  .fd-fill { display: block; height: 100%; background: var(--blue); border-radius: 6px; }
  .fd-bar .v { text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
  .fd-credit { font-size: var(--fs-xs); color: var(--muted); max-width: 80ch; display: grid; gap: var(--s-2); }
  .fd-credit p { margin: 0; }
  .fd-credit a { color: inherit; }
  .fd-note { font-size: var(--fs-xs); color: var(--muted); max-width: 72ch; }
  .fd-cta { display: grid; grid-template-columns: minmax(0, 1fr) 240px; gap: var(--s-6); align-items: center; }
  .fd-cta img { width: 100%; height: 480px; object-fit: cover; object-position: top; border-radius: var(--radius); border: 1px solid var(--line-strong); }
  .fd-tag { display: inline-block; font-size: var(--fs-xs); font-weight: 700; padding: 2px 8px; border-radius: 999px; background: var(--blue-50); color: var(--blue); }
  .table td.n, .table th.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .table tr.is-on td { background: var(--blue-50); }
  .fd-links { display: flex; flex-wrap: wrap; gap: var(--s-2); }
  .fd-links a { text-decoration: none; }
  .fd-search { width: 100%; font: inherit; font-size: var(--fs-md); padding: 14px 18px; border: 2px solid var(--line-strong); border-radius: var(--radius-pill); background: #fff; color: var(--ink); }
  .fd-search:focus { outline: none; border-color: var(--blue); }
  .fd-results { list-style: none; margin: var(--s-4) 0 0; padding: 0; display: grid; gap: 2px; }
  .fd-results a { display: flex; justify-content: space-between; gap: var(--s-3); padding: 10px 14px; border-radius: var(--radius-sm); text-decoration: none; color: var(--ink); background: #fff; border: 1px solid var(--line); }
  .fd-results a:hover { border-color: var(--blue); }
  .fd-results small { color: var(--muted); white-space: nowrap; }
  .fd-cats { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: var(--s-3); }
  .fd-cats a { display: block; padding: var(--s-4); background: #fff; border: 1px solid var(--line); border-radius: var(--radius); text-decoration: none; color: var(--ink); font-weight: 700; }
  .fd-cats a:hover { border-color: var(--blue); }
  .fd-cats small { display: block; color: var(--muted); font-weight: 500; }
  @media (max-width: 860px) { .fd-hero, .fd-cta { grid-template-columns: minmax(0, 1fr); } .fd-stats { grid-template-columns: repeat(2, minmax(0, 1fr)); } .fd-cta img { max-width: 240px; height: 420px; } }
  @media (max-width: 560px) { .fd-bar { grid-template-columns: 104px minmax(0, 1fr) 96px; } }
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

def page(title, desc, path, crumbs, body, schema=(), script=''):
    sch = '\n'.join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schema)
    crumb_html = ' / '.join(f'<a href="{u}">{e(n)}</a>' if u else e(n) for n, u in crumbs)
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
<meta property="og:image" content="{BASE}/og-image-nutrition.png">
<meta name="twitter:card" content="summary_large_image">
<!-- chrome:head -->
<!-- /chrome:head -->
<link rel="stylesheet" href="/css/site.css">
<style>{STYLE}</style>
{sch}
</head>
<body data-brand="nutrition">
<!-- chrome:header -->
<!-- /chrome:header -->
<main id="main" class="theme-nutrition">
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
    strip = lambda s: re.sub('<[^>]+>', '', s)
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": html.unescape(strip(a))}} for q, a in items]}

def cta(heading, text, img, alt):
    return f"""<section class="section section--tint">
  <div class="container fd-cta">
    <div>
      <h2>{heading}</h2>
      <p class="lead">{text}</p>
      <div class="btn-row"><a class="btn btn--nutrition btn--lg" href="/get-nutrition.html">Start free</a><a class="btn btn--ghost" href="/nutrition.html">See Totality Nutrition</a></div>
      <p class="small muted mt-4">Free on Android and at totalitynutrition.com.au on any phone or computer.</p>
    </div>
    <img src="/img/app/{img}" alt="{e(alt)}" width="780" height="1688" loading="lazy">
  </div>
</section>"""

def tail(links_title, links_html, extra=''):
    return f"""<section class="section section--tight">
  <div class="container container--narrow">
    {f'<h2 style="font-size:var(--fs-md)">{links_title}</h2><div class="fd-links">{links_html}</div>' if links_html else ''}
    {extra}
    <div class="mt-5">{CREDIT}</div>
  </div>
</section>"""

# ── Food pages ───────────────────────────────────────────────────────────────
ON = ' class="is-on"'
MICRO_KEYS = [n['key'] for n in NUTRIENTS if n['key'] in MICRO_DEFS]

def food_page(pg):
    d = pg['default']
    title = pg['title']
    t_low = title[:1].lower() + title[1:] if not title[:2].isupper() else title
    cat_name, cat_slug = CATS[pg['cat']]
    crumbs = [('Totality Nutrition', '/nutrition.html'), ('Food facts', '/foods/'), (cat_name, f'/foods/{cat_slug}.html'), (title, None)]
    multi = len(pg['rows']) > 1
    dlabel = variant_label(d, pg['key'])
    what = t_low if dlabel == 'As sold' else f'{t_low}, {dlabel[:1].lower() + dlabel[1:]},'

    def row(label, key, val, unit, cls=''):
        return f'<div class="fd-row {cls}"><span>{label}</span><b data-k="{key}" data-u="{unit}">{fmt(val, unit)}</b></div>'
    energy = f'<div class="fd-row big"><span>Energy</span><b data-k="energy">{kj(d["kcal"])} kJ ({round(d["kcal"])} cal)</b></div>'
    select = ''
    if multi:
        opts = ''.join(f'<option value="{i}"{" selected" if r is d else ""}>{e(variant_label(r, pg["key"]))}</option>' for i, r in enumerate(pg['rows']))
        select = f'<label class="fd-amt"><span>Type</span><select id="fdVar">{opts}</select></label>'
    label = f"""<aside class="fd-label" aria-label="Nutrition in {e(t_low)}">
      <h2>Nutrition</h2>
      <p class="sub" id="fdSub">{e(dlabel)}</p>
      {select}
      <label class="fd-amt"><span>Amount</span><input id="fdG" type="number" min="1" max="2000" step="1" value="100" inputmode="numeric"> <span>g</span></label>
      {energy}
      {row('Protein', 'p', d['p'], 'g')}
      {row('Fat, total', 'f', d['f'], 'g')}
      {row('Saturated', 'sat', d['sat'], 'g', 'in')}
      {row('Carbohydrate', 'c', d['c'], 'g')}
      {row('Sugars', 'sugar', d['sugar'], 'g', 'in')}
      {row('Fibre', 'fibre', d['fibre'], 'g')}
      {row('Sodium', 'na', d['na'], 'mg')}
      {row('Cholesterol', 'cholesterol_mg', d['m'].get('cholesterol_mg'), 'mg') if d['m'].get('cholesterol_mg') is not None else ''}
    </aside>"""
    pe = (d['p'] or 0) * 4 / d['kcal'] * 100 if d['kcal'] else 0
    stats = ''.join(f'<div class="fd-stat stat"><span class="stat-num">{v}</span><span class="stat-label">{l}</span></div>' for v, l in [
        (f'{round(d["kcal"])} cal', f'{kj(d["kcal"])} kJ per 100 g'), (fmt(d['p'], 'g'), 'protein per 100 g'),
        (fmt(d['c'], 'g'), 'carbs per 100 g'), (fmt(d['f'], 'g'), 'fat per 100 g')])

    # vitamins and minerals per 100 g as % of the app's adult targets
    vits = []
    for k in MICRO_KEYS:
        v = d['m'].get(k)
        n = N_BY_KEY[k]
        if v is None or not n['target']:
            continue
        vits.append((v / n['target'] * 100, k, n, v))
    vits.sort(key=lambda x: -x[0])
    bars = ''
    for pct, k, n, v in vits[:12]:
        bars += (f'<div class="fd-bar"><span><a href="/nutrients/{n["slug"]}.html">{n["label"]}</a></span>'
                 f'<span class="fd-track"><span class="fd-fill" style="width:{min(pct, 100):.0f}%"></span></span>'
                 f'<span class="v">{fmt(v, n["unit"])} · {round(pct)}%</span></div>')
    top = [x for x in vits if x[0] >= 15][:3]

    lead = (f'100 g of {e(what)} has <strong>{round(d["kcal"])} calories ({kj(d["kcal"])} kJ)</strong>, '
            f'<strong>{fmt(d["p"], "g")} of protein</strong>, {fmt(d["c"], "g")} of carbohydrate and {fmt(d["f"], "g")} of fat.')
    if top:
        names = [x[2]['label'].split(' (')[0].lower().replace('vitamin b', 'vitamin B').replace('vitamin a', 'vitamin A').replace('vitamin c', 'vitamin C').replace('vitamin d', 'vitamin D').replace('vitamin e', 'vitamin E') for x in top]
        joined = names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]
        lead += f' Of the vitamins and minerals, it has the most {e(joined)} for its weight.'
    lead += ' These are Australian figures from the national food database.'

    variants = ''
    if multi:
        trs = ''.join(
            f'<tr{ON if r is d else ""}><td>{e(variant_label(r, pg["key"]))}</td><td class="n">{round(r["kcal"])}</td>'
            f'<td class="n">{fmt(r["p"], "g")}</td><td class="n">{fmt(r["c"], "g")}</td><td class="n">{fmt(r["f"], "g")}</td></tr>'
            for r in pg['rows'])
        variants = f"""<section class="section section--tint">
  <div class="container container--narrow">
    <div class="section-head"><h2>Every type of {e(t_low)}</h2>
      <p class="section-sub">Per 100 g. Pick a type in the nutrition panel to see its full breakdown.</p></div>
    <div class="table-wrap"><table class="table">
      <thead><tr><th>Type</th><th class="n">Calories</th><th class="n">Protein</th><th class="n">Carbs</th><th class="n">Fat</th></tr></thead>
      <tbody>{trs}</tbody></table></div>
    <p class="fd-note mt-4">Cooking changes how much water a food holds, so the same weight cooked and raw won’t match.</p>
  </div>
</section>"""

    faqs = [
        (f'How many calories are in {t_low}?', f'100 g of {e(what)} has {round(d["kcal"])} calories, which is {kj(d["kcal"])} kJ.'),
        (f'How much protein is in {t_low}?', f'{fmt(d["p"], "g")} per 100 g, which is {round(pe)}% of its energy.'),
        (f'How many carbs are in {t_low}?', f'{fmt(d["c"], "g")} of carbohydrate per 100 g, with {fmt(d["sugar"], "g")} of sugars and {fmt(d["fibre"], "g")} of fibre.'),
        ('Where do these numbers come from?', 'The Australian Food Composition Database from Food Standards Australia New Zealand. They’re averages, so a particular brand or batch will be a little different.'),
    ]
    sib = [p for p in BY_CAT[pg['cat']] if p is not pg]
    i = BY_CAT[pg['cat']].index(pg)
    near = (BY_CAT[pg['cat']][max(0, i - 5):i] + BY_CAT[pg['cat']][i + 1:i + 6])[:10] or sib[:10]
    links = ''.join(f'<a class="pill pill--blue" href="/foods/{p["slug"]}.html">{e(p["title"])}</a>' for p in near)
    links += f'<a class="pill pill--ink" href="/foods/{cat_slug}.html">All {e(cat_name.lower())}</a>'

    body = f"""    <div class="fd-hero">
      <div>
        <p class="kicker">Food facts</p>
        <h1>{e(title)}: calories, protein and nutrition</h1>
        <p class="lead">{lead}</p>
        <div class="fd-stats">{stats}</div>
        <div class="btn-row"><a class="btn btn--nutrition" href="/get-nutrition.html">Track it free in Totality Nutrition</a></div>
      </div>
      {label}
    </div>
  </div>
</section>
{f'''<section class="section">
  <div class="container container--narrow">
    <div class="section-head"><h2>Vitamins and minerals</h2>
      <p class="section-sub">In 100 g of {e(what.rstrip(','))}, and how much of an adult’s daily amount that is.</p></div>
    <div class="fd-bars">{bars}</div>
    <p class="fd-note mt-4">Daily amounts are the reference values on Australian food labels, the same ones Totality Nutrition uses. Potassium uses the NHMRC adequate intake for women. Your own needs depend on your age, sex and stage of life.</p>
  </div>
</section>''' if bars else ''}
{variants}
<section class="section">
  <div class="container container--narrow">
    <div class="section-head"><h2>Questions people ask</h2></div>
    {faq_html(faqs)}
  </div>
</section>

{cta('Track everything you eat', 'Search the same Australian food data in Totality Nutrition, scan barcodes, and watch your protein, vitamins and minerals add up through the day.', 'n_foodlog.webp', 'The food log in Totality Nutrition')}
{tail('More ' + cat_name.lower(), links)}"""

    data = [{'l': variant_label(r, pg['key']), 'kcal': r['kcal'], 'p': r['p'], 'f': r['f'], 'sat': r['sat'], 'c': r['c'],
             'sugar': r['sugar'], 'fibre': r['fibre'], 'na': r['na'], 'cholesterol_mg': r['m'].get('cholesterol_mg')} for r in pg['rows']]
    script = f"""<script>
(function () {{
  var D = {json.dumps(data, separators=(',', ':'))};
  var cur = {pg['rows'].index(d)};
  var g = document.getElementById('fdG'), sel = document.getElementById('fdVar'), sub = document.getElementById('fdSub');
  var U = {{ ug: '\\u00b5g' }};
  function fmt(x, u) {{
    if (x === null || x === undefined) return 'no data';
    var s = x >= 100 ? Math.round(x).toLocaleString('en-AU') : x >= 10 ? (x >= 20 ? Math.round(x) : x.toFixed(1)) : x >= 1 ? (+x.toFixed(1)).toString() : x === 0 ? '0' : (+x.toFixed(2)).toString();
    return s + ' ' + (U[u] || u);
  }}
  function draw() {{
    var w = Math.max(0, parseFloat(g.value) || 0) / 100, r = D[cur];
    document.querySelectorAll('[data-k]').forEach(function (el) {{
      var k = el.getAttribute('data-k');
      if (k === 'energy') {{ el.textContent = Math.round(r.kcal * w * 4.184) + ' kJ (' + Math.round(r.kcal * w) + ' cal)'; return; }}
      el.textContent = fmt(r[k] === null || r[k] === undefined ? null : r[k] * w, el.getAttribute('data-u'));
    }});
    if (sub) sub.textContent = r.l + (w !== 1 ? ', ' + (+g.value) + ' g' : '');
  }}
  g.addEventListener('input', draw);
  if (sel) sel.addEventListener('change', function () {{ cur = +sel.value; draw(); }});
}})();
</script>"""
    meta_title = f'{title} calories, protein and nutrition (Australia) | Totality Nutrition'
    desc = (f'100 g of {t_low} has {round(d["kcal"])} calories ({kj(d["kcal"])} kJ), {fmt(d["p"], "g")} protein, '
            f'{fmt(d["c"], "g")} carbs and {fmt(d["f"], "g")} fat. Full vitamins and minerals from Australian food data.')
    return page(meta_title, desc, f'/foods/{pg["slug"]}.html', crumbs, body, [faq_schema(faqs), crumbs_schema(crumbs)], script)

# ── Category and index pages ─────────────────────────────────────────────────
def cat_page(cat):
    name, slug = CATS[cat]
    pages = BY_CAT[cat]
    crumbs = [('Totality Nutrition', '/nutrition.html'), ('Food facts', '/foods/'), (name, None)]
    trs = ''.join(f'<tr><td><a href="/foods/{p["slug"]}.html">{e(p["title"])}</a></td><td class="n">{round(p["default"]["kcal"])}</td>'
                  f'<td class="n">{fmt(p["default"]["p"], "g")}</td><td class="n">{fmt(p["default"]["c"], "g")}</td><td class="n">{fmt(p["default"]["f"], "g")}</td></tr>'
                  for p in pages)
    others = ''.join(f'<a class="pill pill--blue" href="/foods/{s}.html">{e(n)}</a>' for c, (n, s) in CATS.items() if c != cat and BY_CAT.get(c))
    body = f"""    <p class="kicker">Food facts</p>
    <h1>{e(name)}: calories and nutrition</h1>
    <p class="lead">Calories, protein, carbs and fat per 100 g for {len(pages)} {e(name.lower())} from Australian food data. Tap a food for its full vitamins and minerals.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="table-wrap"><table class="table">
      <thead><tr><th>Food</th><th class="n">Calories</th><th class="n">Protein</th><th class="n">Carbs</th><th class="n">Fat</th></tr></thead>
      <tbody>{trs}</tbody></table></div>
  </div>
</section>
{cta('Track everything you eat', 'Search the same Australian food data in Totality Nutrition, scan barcodes, and watch your protein, vitamins and minerals add up through the day.', 'n_foodlog.webp', 'The food log in Totality Nutrition')}
{tail('Other food groups', others)}"""
    desc = f'Calories, protein, carbs and fat per 100 g for {len(pages)} {name.lower()}, from the Australian Food Composition Database.'
    return page(f'{name}: calories and nutrition per 100 g (Australia) | Totality Nutrition', desc, f'/foods/{slug}.html', crumbs, body, [crumbs_schema(crumbs)])

def foods_index():
    crumbs = [('Totality Nutrition', '/nutrition.html'), ('Food facts', None)]
    cats = ''.join(f'<a href="/foods/{s}.html">{e(n)}<small>{len(BY_CAT[c])} foods</small></a>' for c, (n, s) in sorted(CATS.items(), key=lambda x: -len(BY_CAT.get(x[0], []))) if BY_CAT.get(c))
    idx = [[p['title'], p['slug'], round(p['default']['kcal'])] for p in sorted(PAGES, key=lambda p: p['title'].lower())]
    body = f"""    <p class="kicker">Food facts</p>
    <h1>Calories and nutrition for {len(PAGES):,} Australian foods</h1>
    <p class="lead">Calories, protein, carbs, fat, vitamins and minerals for everyday foods, from the Australian Food Composition Database. Search for a food or browse by group.</p>
    <input class="fd-search mt-5" id="fdQ" type="search" placeholder="Search foods, like egg, rice or banana" aria-label="Search foods" autocomplete="off">
    <ul class="fd-results" id="fdR"></ul>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head"><h2>Browse by food group</h2></div>
    <div class="fd-cats">{cats}</div>
  </div>
</section>
<section class="section section--tint">
  <div class="container">
    <div class="section-head"><h2>Nutrients</h2><p class="section-sub">What each one does, how much you need and which foods have the most.</p></div>
    <div class="fd-links">{''.join(f'<a class="pill pill--blue" href="/nutrients/{n["slug"]}.html">{e(n["label"])}</a>' for n in NUTRIENTS)}</div>
  </div>
</section>
{tail('', '')}"""
    script = f"""<script>
(function () {{
  var I = {json.dumps(idx, separators=(',', ':'), ensure_ascii=False)};
  var q = document.getElementById('fdQ'), out = document.getElementById('fdR');
  function esc(s) {{ return s.replace(/[&<>"]/g, function (c) {{ return {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }}[c]; }}); }}
  q.addEventListener('input', function () {{
    var t = q.value.trim().toLowerCase().split(/\\s+/).filter(Boolean);
    if (!t.length) {{ out.innerHTML = ''; return; }}
    var hits = I.filter(function (r) {{ var n = r[0].toLowerCase(); return t.every(function (w) {{ return n.indexOf(w) >= 0; }}); }});
    hits.sort(function (a, b) {{ return a[0].toLowerCase().indexOf(t[0]) - b[0].toLowerCase().indexOf(t[0]) || a[0].length - b[0].length; }});
    out.innerHTML = hits.slice(0, 30).map(function (r) {{ return '<li><a href="/foods/' + r[1] + '.html"><span>' + esc(r[0]) + '</span><small>' + r[2] + ' cal per 100 g</small></a></li>'; }}).join('') || '<li class="muted">No foods match that. Try a shorter word.</li>';
  }});
  var pre = new URLSearchParams(location.search).get('q');
  if (pre) {{ q.value = pre; q.dispatchEvent(new Event('input')); }}
}})();
</script>"""
    desc = f'Calories, protein, carbs, fat, vitamins and minerals for {len(PAGES):,} Australian foods, from the Australian Food Composition Database.'
    return page('Food calories and nutrition facts (Australia) | Totality Nutrition', desc, '/foods/', crumbs, body, [crumbs_schema(crumbs)], script)

# ── Nutrient pages ───────────────────────────────────────────────────────────
TOP_EXCLUDE_CATS = {'miscellaneous', 'special-dietary-foods', 'infant-formulae-and-foods'}
TOP_EXCLUDE = re.compile(r'powder|beverage base|dried, ground|, dry$|dry mix|supplement|essence|cordial base|, uncooked|, dried$|yeast|stock cube', re.I)

def basis_text(n):
    if n['basis'] == 'label':
        kind = 'a daily limit' if n['kind'] == 'limit' else 'a daily amount'
        return f'{fmt(n["target"], n["unit"])} is the reference used on Australian food labels as {kind} for an average adult diet of 8,700 kJ. Totality Nutrition uses the same figure unless you set your own.'
    if n['basis'] == 'potassium':
        return f'There’s no food label reference for potassium. Totality Nutrition uses {fmt(n["target"], n["unit"])}, the NHMRC adequate intake for adult women. The figure for men is higher.'
    if n['basis'] == 'rdi':
        return f'{fmt(n["target"], n["unit"])} is the recommended daily intake used on Australian food labels, and the target Totality Nutrition uses for adults.'
    return 'There’s no Australian daily reference for cholesterol in food, so Totality Nutrition shows it without a target.'

def nutrient_page(n):
    info = PROTEIN_INFO if n['info'] is None else NI['info'][n['info']]
    crumbs = [('Totality Nutrition', '/nutrition.html'), ('Nutrients', '/nutrients/'), (n['label'], None)]
    label = n['label']
    lname = label if label.startswith('Vitamin') else label.split(' (')[0].lower()
    # foods highest in this nutrient per 100 g, one per food page
    best = {}
    for r in FOODS:
        if r['cat'] in TOP_EXCLUDE_CATS or TOP_EXCLUDE.search(r['name']) or SKIP.search(r['name']):
            continue
        v = get(r, n['key'])
        if v is None:
            continue
        pg = PAGE_BY_NAME.get(r['name'])
        if not pg:
            continue
        if pg['slug'] not in best or v > best[pg['slug']][0]:
            best[pg['slug']] = (v, r, pg)
    top = sorted(best.values(), key=lambda x: -x[0])[:20]
    trs = ''
    for v, r, pg in top:
        pct = f'{round(v / n["target"] * 100)}%' if n['target'] else ''
        trs += (f'<tr><td><a href="/foods/{pg["slug"]}.html">{e(pg["title"])}</a><br><span class="small muted">{e(variant_label(r, pg["key"]))}</span></td>'
                f'<td class="n"><b>{fmt(v, n["unit"])}</b></td>{f"<td class=n>{pct}</td>" if n["target"] else ""}<td class="n">{round(r["kcal"])}</td></tr>')
    is_limit = n['kind'] == 'limit'
    head_top = f'Foods highest in {lname}' if not is_limit else f'Foods with the most {lname}'
    if n['key'] in NRV_TABLES:
        rows = ''.join(f'<div class="fd-row{" big" if i == 0 else ""}"><span>{a}</span><b>{b}</b></div>' for i, (a, b) in enumerate(NRV_TABLES[n['key']]))
        box = f'<aside class="fd-label"><h2>{e(label)} you need a day</h2><p class="sub">{NRV_NAME[n["key"]]}</p>{rows}</aside>'
    elif n['target']:
        box = (f'<aside class="fd-label"><h2>{"Daily limit" if is_limit else "Daily amount"}</h2><p class="sub">For an adult</p>'
               f'<div class="fd-row big"><span>{e(label)}</span><b>{fmt(n["target"], n["unit"])}</b></div>'
               f'<p class="small muted mt-4" style="margin-bottom:0">{basis_text(n)}</p></aside>')
    else:
        box = f'<aside class="fd-label"><h2>No daily target</h2><p class="small muted" style="margin:0">{basis_text(n)}</p></aside>'
    amount_line = ''
    if n['key'] in NRV_TABLES:
        t = NRV_TABLES[n['key']]
        amount_line = f' Adult men need about <strong>{t[0][1]}</strong> a day and women <strong>{t[1][1]}</strong>{" aged 19 to 50" if n["key"] == "iron_mg" else ""}.'
    elif n['target']:
        amount_line = f' The {"daily limit" if is_limit else "daily amount"} on Australian food labels is <strong>{fmt(n["target"], n["unit"])}</strong>.'
    kind_word = {'sources': 'Everyday foods that have it', 'swaps': 'Easy ways to have less', 'found': 'Where it’s found'}[info['listKind']]
    ticks = ''.join(f'<li>{e(x)}</li>' for x in info['list'])
    faqs = []
    if n['target'] or n['key'] in NRV_TABLES:
        faqs.append((f'How much {lname} do I need a day?' if not is_limit else f'How much {lname} is too much?',
                     re.sub('<[^>]+>', '', amount_line).strip() + (' ' + basis_text(n) if n['key'] not in NRV_TABLES else ' These are the NHMRC Nutrient Reference Values for Australia and New Zealand.')))
    if top:
        faqs.append((f'Which foods are highest in {lname}?', 'Per 100 g, the foods with the most are ' + ', '.join(pg['title'].lower() if not pg['title'][:2].isupper() else pg['title'] for _, _, pg in top[:5]) + '. The table on this page lists the top 20.'))
    faqs.append((f'What does {lname} do?', e(info['does'])))
    faqs.append(('Where do these numbers come from?', 'Food figures are from the Australian Food Composition Database from Food Standards Australia New Zealand. Daily amounts are from the Australian food labelling rules and the NHMRC Nutrient Reference Values.'))
    pct_head = '<th class="n">Of daily amount</th>' if n['target'] else ''
    others = ''.join(f'<a class="pill pill--blue" href="/nutrients/{m["slug"]}.html">{e(m["label"])}</a>' for m in NUTRIENTS if m is not n)
    body = f"""    <div class="fd-hero">
      <div>
        <p class="kicker">Nutrients</p>
        <h1>{e(label)}: {"how much is too much" if is_limit else "how much you need"} and the foods that have it</h1>
        <p class="lead">{e(info['does'])}{amount_line}</p>
        <p style="margin-top:var(--s-3)">{e(info['why'])}</p>
        <div class="btn-row"><a class="btn btn--nutrition" href="/get-nutrition.html">Track your {e(lname)} free in Totality Nutrition</a></div>
      </div>
      {box}
    </div>
  </div>
</section>

<section class="section">
  <div class="container container--narrow">
    <div class="section-head"><h2>{head_top}</h2>
      <p class="section-sub">Per 100 g, from Australian food data. Spices, powders and supplements are left out because nobody eats 100 g of them.</p></div>
    <div class="table-wrap"><table class="table">
      <thead><tr><th>Food</th><th class="n">{e(label.split(" (")[0])}</th>{pct_head}<th class="n">Calories</th></tr></thead>
      <tbody>{trs}</tbody></table></div>
  </div>
</section>

<section class="section section--tint">
  <div class="container container--narrow">
    <div class="section-head"><h2>{kind_word}</h2></div>
    <ul class="ticks ticks--blue">{ticks}</ul>
  </div>
</section>

<section class="section">
  <div class="container container--narrow">
    <div class="section-head"><h2>Questions people ask</h2></div>
    {faq_html(faqs)}
  </div>
</section>

{cta(f'See how much {e(lname)} you’re getting', 'Totality Nutrition adds up your protein, fibre, vitamins and minerals from everything you log, so you can see what you’re short on.', 'n_breakdown.webp', 'The vitamins and minerals breakdown in Totality Nutrition')}
{tail('Other nutrients', others, f'<p class="fd-note mt-4">Daily amounts: Australia New Zealand Food Standards Code and the <a href="{NRV_URL}" rel="noopener">NHMRC Nutrient Reference Values</a>. General information only. Talk to your GP or a dietitian about your own needs.</p>')}"""
    title = f'{label}: {"daily limit" if is_limit else "how much you need a day"} and foods high in {lname} (Australia) | Totality Nutrition'
    desc = re.sub('<[^>]+>', '', f'{info["does"]}{amount_line} See the Australian foods with the most {lname} per 100 g.')
    return page(title, desc, f'/nutrients/{n["slug"]}.html', crumbs, body, [faq_schema(faqs), crumbs_schema(crumbs)])

def nutrients_index():
    crumbs = [('Totality Nutrition', '/nutrition.html'), ('Nutrients', None)]
    cards = ''.join(f'<a href="/nutrients/{n["slug"]}.html">{e(n["label"])}<small>{e((PROTEIN_INFO if n["info"] is None else NI["info"][n["info"]])["does"])}</small></a>' for n in NUTRIENTS)
    body = f"""    <p class="kicker">Nutrients</p>
    <h1>Vitamins, minerals and nutrients</h1>
    <p class="lead">What each nutrient does, how much an adult needs, and the Australian foods that have the most.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="fd-cats">{cards}</div>
    <p class="mt-5"><a class="text-link" href="/foods/">Look up a food instead</a></p>
  </div>
</section>
{cta('See how much you’re getting', 'Totality Nutrition adds up your protein, fibre, vitamins and minerals from everything you log, so you can see what you’re short on.', 'n_breakdown.webp', 'The vitamins and minerals breakdown in Totality Nutrition')}
{tail('', '')}"""
    return page('Vitamins, minerals and nutrients: how much you need (Australia) | Totality Nutrition',
                'What each vitamin and mineral does, how much an adult needs a day, and the Australian foods highest in each one.',
                '/nutrients/', crumbs, body, [crumbs_schema(crumbs)])

def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def main():
    for d in ('foods', 'nutrients'):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    for pg in PAGES:
        write(f'foods/{pg["slug"]}.html', food_page(pg))
    for c in BY_CAT:
        write(f'foods/{CATS[c][1]}.html', cat_page(c))
    write('foods/index.html', foods_index())
    for n in NUTRIENTS:
        write(f'nutrients/{n["slug"]}.html', nutrient_page(n))
    write('nutrients/index.html', nutrients_index())
    clash = {p['slug'] for p in PAGES} & {s for _, s in CATS.values()}
    print(f'{len(PAGES)} food pages, {len(BY_CAT)} food groups, {len(NUTRIENTS)} nutrient pages' + (f'. SLUG CLASH: {clash}' if clash else ''))

if __name__ == '__main__':
    main()
