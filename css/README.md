# Totality site design system

One stylesheet: `css/site.css`. Every page links it plus the fonts. Page-specific
layout can still live in a page `<style>` block, but it should read the tokens
below and reuse these components rather than redefine buttons, cards or colours.

## Page skeleton

```html
<!DOCTYPE html>
<html lang="en-AU">
<head>
  <!-- Meta Pixel snippet goes INSIDE <head>, never above <!DOCTYPE> (that forces quirks mode) -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>...</title>
  <!-- chrome:head --><!-- /chrome:head -->   (apply_chrome.py fills in the font preloads)
  <link rel="stylesheet" href="/css/site.css">
</head>
<body>                       <!-- add data-brand="nutrition" on Nutrition pages -->
<!-- chrome:header --><!-- /chrome:header -->
<main id="main"> ... </main>
<!-- chrome:footer --><!-- /chrome:footer -->
<script src="/js/nav.js" defer></script>
</body>
</html>
```

- Put the three marker pairs in your page and leave them empty. `python3 tools/apply_chrome.py`
  fills them with the shared header, footer and font links (stream B runs it at the end).
- Pages with the old `<nav>...</nav>` / `<footer>...</footer>` markup are converted automatically
  by the script, so you do not have to remove them by hand, but new pages should use markers.
- Use absolute links (`/pricing.html`, `/blog/`) so the same markup works in `/blog/posts/`.
- `<body data-brand="nutrition">` switches the accent to blue and makes the header CTA
  "Start free" point at Totality Nutrition. Default is Totality orange.
- Wrap page content in `<main id="main">` (the header has a skip link to `#main`).
- One `<h1>` per page.

## Tokens (CSS custom properties)

| Token | Value | Use |
|---|---|---|
| `--orange` | #ED8008 | App orange. Fills, rules, big shapes, text on dark only. NOT small text on white, NOT under white text (2.7:1). |
| `--orange-600` | #B85C00 | Orange buttons with white text (4.6:1). |
| `--orange-700` | #A65000 | Orange text on white (5.6:1), hover. |
| `--orange-50` / `--orange-100` | #FFF4E8 / #FFE6CC | Tints. |
| `--blue` | #1565A0 | Nutrition blue. Buttons with white text and blue text on white (6.2:1). |
| `--blue-700` | #0F4F80 | Hover. |
| `--blue-50` / `--blue-100` | #EAF2FA / #D3E5F5 | Tints. |
| `--ink` | #272626 | Body text, dark sections. |
| `--ink-2` | #45423F | Secondary strong text. |
| `--muted` | #62605D | Secondary text (6.3:1). Replaces the old failing #A0A0A0. |
| `--line` / `--line-strong` | #E6E4E1 / #D2CFCB | Borders. |
| `--surface` | #F5F5F4 | Tinted sections and flat cards. |
| `--on-dark-muted` | #C9C5C0 | Secondary text on `--ink`. |
| `--accent`, `--accent-strong`, `--accent-ink`, `--accent-tint` | orange by default, blue under `.theme-nutrition` / `data-brand="nutrition"` | Components use these, so one class re-themes a section. |

Purple (`--purple*`) is the app's Super Admin colour only. Do not use it on the site.

Type: `--font-display` Bricolage Grotesque (headings, prices, stats), `--font-body` Figtree. Both are Google Fonts, self-hosted from `/fonts/` (variable woff2, latin subset) so there is no third-party request; `@font-face` lives in site.css.
Scale: `--fs-xs` 13, `--fs-sm` 15, `--fs-md` 17 (body), `--fs-lg` 20, `--fs-xl` 24,
`--fs-2xl` 24 to 32, `--fs-3xl` 30 to 44, `--fs-4xl` 38 to 64 (fluid).
Space: `--s-1`..`--s-9` = 4, 8, 12, 16, 24, 32, 48, 64, 96px. Radius: `--radius-sm` 8,
`--radius` 14, `--radius-lg` 24, `--radius-pill`. Container 1160px, gutter 20px (32px from 720px).

## Components

**Layout**: `.container` (max width + gutter), `.container--narrow` (780px), `.section`
(vertical padding 64/96px), `.section--tight`, `.section--tint` (grey), `.section--accent`
(brand tint), `.section--dark` (ink, white text), `.section--orange`, `.section--blue`,
`.section-head` (+ `.center`), `.grid-2` `.grid-3` `.grid-4` (collapse at 960 / 720px),
`.split` (two columns, stacks at 720px), `.stack`, `.stack-lg`, `.cluster`, `.btn-row`,
`.page-hero` (inner page top: h1 + `.lead` + `.btn-row`), `.page-hero--tint`, `.crumbs`.

**Type**: `h1`..`h4` (or `.h1`..`.h4`), `.lead`, `.muted`, `.small`, `.tiny`, `.kicker`
(short sentence-case label above a heading; use sparingly, not on every section),
`.prose` (long-form text: blog, legal, help), `.text-link`, `.visually-hidden`.

**Buttons**: `.btn` + one of `.btn--primary` (Totality orange), `.btn--nutrition` (blue),
`.btn--ink`, `.btn--white`, `.btn--ghost`, `.btn--ghost-light` (on dark). Sizes `.btn--lg`,
`.btn--sm`, `.btn--block`. Plain `.btn` uses the current accent. All buttons are 48px+ tall.
Button text says what happens ("Start your 7 day free trial", "Open the web app"). No arrows
glued onto text.

**Cards**: `.card` (white, border), `.card--flat` (grey, no border), `.card--raised`
(shadow), `.card--accent` / `.card--orange` / `.card--blue` (4px top rule), `.card--dark`.
`a.card` is a whole-card link. Inside: `h3`, `p`, `.card-meta`, `.card-foot` (pushes to bottom).
`.icon-tile` holds an inline SVG icon (no emoji icons).

**Pills**: `.pill` (accent), `.pill--orange`, `.pill--blue`, `.pill--ink`, `.pill--new`
(green, for shipped items), `.pill--soon` (grey, for not live yet).

**Lists**: `.ticks` (check-mark list), `.ticks--orange`, `.ticks--blue`.

**Pricing**: `.price` (big number, put `/mo` in `<small>`), `.price-card` on a `.card`,
`.price-card.is-featured`. `.offer` (dark band for the trial + 50% off line), `.notice`
(left-ruled callout).

**Stats**: `.stat` > `.stat-num` + `.stat-label`.

**Forms**: `.label`, `.input`, `.select`, `.textarea`.

**Tables**: `.table-wrap` > `table.table` (scrolls sideways on phones inside its wrapper,
never the page). Cells: `.yes`, `.no`.

**FAQ**: `.faq` > `<details><summary>Question</summary><p>Answer</p></details>`. Works without JS.

**Phone mock**: `.phone` > `<img>` (a 9:18.5 screenshot) or `.phone-screen` (HTML screen).
**Tali**: images in `/img/tali/` (`tali_point`, `tali_wave`, `tali_thumbs`, `tali_cook`,
`tali_idle`, `tali_think`, `tali_celebrate`, each `.webp` + `.png`). Use `<picture>` with
the webp, add `class="tali"`, `width`/`height` attributes (300x430) and `alt`. Never edit,
recolour or crop the sprites. `.tali-bubble` is a speech bubble.

## Migration list (old class to new)

| Old | New | Status |
|---|---|---|
| `<nav>` with `.nav-logo .nav-links .nav-cta .nav-cta-nutrition .nav-toggle` | shared header (`.site-header`) via markers | Replaced automatically by `apply_chrome.py` |
| `<footer>` with `.footer-brand .footer-links .footer-copy` | shared footer (`.site-footer`) | Replaced automatically |
| `.btn-primary` | `.btn .btn--primary` | Alias kept |
| `.btn-secondary` | `.btn .btn--ghost` | Alias kept |
| `.btn-nutrition` | `.btn .btn--nutrition` | Alias kept |
| `.section`, `.section-inner`, `.section-eyebrow`, `.section-title`, `.section-sub` | same names | Kept, restyled |
| `.promo-banner` | same | Kept |
| `--off-white`, `--border`, `--white`, `--dark`, `--orange-dark`, `--orange-light`, `--nutrition*` | `--surface`, `--line`, `#fff`, `--ink`, `--orange-600`, `--orange-300`, `--blue*` | Aliases kept |
| `--muted` | same name, now #62605D | Darkened for contrast |
| `--purple*` | none | Do not use |

## Copy rules (apply to every page)

No em or en dashes. No "not X, it's Y" lines, no "here's the truth". Never claim a feature
that does not exist. Offer wording: "7 day free trial, then 50% off your first 2 months,
applied automatically". Never "2 months free". Plain Australian English.

## Shared header and footer (how chrome works)

- Source: `partials/header.html`, `partials/footer.html`, `partials/head.html` (font preloads).
  Edit those, never the copies inside pages.
- `python3 tools/apply_chrome.py` (or `... file1.html file2.html`, `--dry-run` to preview) writes the
  partials into every page between the marker comments. It re-reads each file right before writing
  and is safe to re-run any time. It also moves a Meta Pixel block sitting above `<!DOCTYPE>` into
  `<head>`, sets `aria-current="page"` on the matching nav link, and adds `/js/nav.js` if missing.
- Old `<nav>` (with `.nav-logo`) and old `<footer>` (with `.footer-brand`) are converted to markers.
- Pages that never had the site nav (ad landing pages like `guide.html`) keep no header; add
  `<!-- chrome:header --><!-- /chrome:header -->` to opt in. Excluded: `links.html`, `brand-kit-*.html`.
- `js/site-chrome.js` is generated by the same script: a JS fallback for a page that cannot be
  processed (put `<div data-chrome="header"></div>` / `<div data-chrome="footer"></div>` and load it).
  Static injection is preferred for SEO.
- `js/nav.js` handles the mobile drawer (below 1020px), dropdowns (`<details>`, work without JS),
  Escape and outside-click closing.
- Do not style bare `header`, `nav` or `footer` elements in page CSS; scope to your own class.
