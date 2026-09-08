# Totality 360 — SEO head-tag snippets

Paste each block into the `<head>` of the matching file, right after the existing
`<meta name="description">` line. Two new image files (`og-image.png`,
`og-image-nutrition.png`) need to be uploaded to the repo root first — they're
attached alongside this file.

---

## index.html (homepage)

```html
<link rel="canonical" href="https://totality360.com.au/">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Totality 360">
<meta property="og:title" content="Totality — Coaching platform & nutrition tracking for gyms, trainers and individuals">
<meta property="og:description" content="Totality builds software for fitness professionals and individuals. Totality — the all-in-one coaching platform for gyms and trainers. Totality Nutrition — standalone macro tracking for Australians.">
<meta property="og:url" content="https://totality360.com.au/">
<meta property="og:image" content="https://totality360.com.au/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Totality — Coaching platform & nutrition tracking">
<meta name="twitter:description" content="All-in-one coaching platform for gyms and trainers, plus standalone macro tracking for Australians.">
<meta name="twitter:image" content="https://totality360.com.au/og-image.png">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Totality 360",
  "url": "https://totality360.com.au",
  "logo": "https://totality360.com.au/logo.png",
  "sameAs": [
    "https://www.instagram.com/totalityapp",
    "https://www.youtube.com/@TotalityApp",
    "https://www.youtube.com/@TotalityEvidenceBased"
  ]
}
</script>
```

---

## totality.html

```html
<link rel="canonical" href="https://totality360.com.au/totality.html">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Totality 360">
<meta property="og:title" content="Totality — All-in-one coaching platform for gym owners & personal trainers">
<meta property="og:description" content="The all-in-one coaching platform for gyms, trainers and their clients. Programme builder, nutrition tracking, auto-regulation, client management and more.">
<meta property="og:url" content="https://totality360.com.au/totality.html">
<meta property="og:image" content="https://totality360.com.au/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Totality — All-in-one coaching platform">
<meta name="twitter:description" content="Programme builder, nutrition tracking, auto-regulation and client management, in one platform.">
<meta name="twitter:image" content="https://totality360.com.au/og-image.png">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Totality",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "iOS, Android, Web",
  "description": "The all-in-one coaching platform for gyms, trainers and their clients. Programme builder, nutrition tracking, auto-regulation and client management.",
  "brand": {
    "@type": "Organization",
    "name": "Totality 360"
  }
}
</script>
```

*(No `offers`/price block included — fill one in only once your tiers and prices are final. Wrong or stale pricing in structured data is a common cause of Search Console warnings.)*

---

## nutrition.html

```html
<link rel="canonical" href="https://totality360.com.au/nutrition.html">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Totality 360">
<meta property="og:title" content="Totality Nutrition — Australian food tracking app for macro counting">
<meta property="og:description" content="Totality Nutrition — Australian-first food tracking app. Barcode scanner that works at Woolies, macro targets, meal planning, grocery lists, weight tracking and more. From $8.99/mo.">
<meta property="og:url" content="https://totality360.com.au/nutrition.html">
<meta property="og:image" content="https://totality360.com.au/og-image-nutrition.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Totality Nutrition — Australian macro tracking">
<meta name="twitter:description" content="Barcode scanning that works at Woolies, macro targets, meal planning and grocery lists. From $8.99/mo.">
<meta name="twitter:image" content="https://totality360.com.au/og-image-nutrition.png">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Totality Nutrition",
  "applicationCategory": "HealthApplication",
  "operatingSystem": "iOS, Android, Web",
  "description": "Australian-first food tracking app with barcode scanning, macro targets, meal planning and grocery lists.",
  "offers": {
    "@type": "Offer",
    "price": "8.99",
    "priceCurrency": "AUD"
  },
  "brand": {
    "@type": "Organization",
    "name": "Totality 360"
  }
}
</script>
```

---

## blog/index.html

```html
<link rel="canonical" href="https://totality360.com.au/blog/">

<meta property="og:type" content="website">
<meta property="og:site_name" content="Totality 360">
<meta property="og:title" content="Totality Reports — Totality">
<meta property="og:description" content="Training, nutrition and mindset articles from Totality — the all-in-one coaching platform for gyms, trainers and individuals.">
<meta property="og:url" content="https://totality360.com.au/blog/">
<meta property="og:image" content="https://totality360.com.au/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Totality Reports">
<meta name="twitter:description" content="Training, nutrition and mindset articles, backed by primary research.">
<meta name="twitter:image" content="https://totality360.com.au/og-image.png">
```

---

## Each blog post (add to `post-template.html` so every future post inherits it)

Fill in the four `{{...}}` placeholders per post — title, one-line excerpt, slug,
and publish date (`YYYY-MM-DD`).

```html
<link rel="canonical" href="https://totality360.com.au/blog/posts/{{slug}}.html">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Totality 360">
<meta property="og:title" content="{{title}} — Totality Reports">
<meta property="og:description" content="{{excerpt}}">
<meta property="og:url" content="https://totality360.com.au/blog/posts/{{slug}}.html">
<meta property="og:image" content="https://totality360.com.au/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{title}}">
<meta name="twitter:description" content="{{excerpt}}">
<meta name="twitter:image" content="https://totality360.com.au/og-image.png">

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{title}}",
  "description": "{{excerpt}}",
  "datePublished": "{{YYYY-MM-DD}}",
  "author": { "@type": "Organization", "name": "Totality 360" },
  "publisher": {
    "@type": "Organization",
    "name": "Totality 360",
    "logo": { "@type": "ImageObject", "url": "https://totality360.com.au/logo.png" }
  }
}
</script>
```

Retrofit this onto the 6 posts already live once the template is updated:
`real-anti-burnout-formula`, `plant-based-protein-recovery-soreness`,
`cold-plunge-recovery-paradox`, `protein-per-meal-not-just-per-day`,
`rest-3-minutes-between-sets`, `reframe-nerves-as-excitement`.

---

## Files to drop at the repo root

- `robots.txt` (attached) — currently 404s on the live site
- `sitemap.xml` (attached) — currently 404s on the live site; lists every real
  page found in the repo as of Sept 8 2026. **This needs a manual line added
  each time a new Totality Reports post goes up** — there's no build step
  generating it automatically since the site is static HTML, not a framework.
- `og-image.png`, `og-image-nutrition.png` (attached) — branded 1200×630 share
  images referenced by the OG tags above. Quick first pass in your brand
  colours; swap for real product screenshots whenever you get the chance.

## Not touched

- No visible page copy or the homepage H1 was changed — that's a conversion/
  design call, not a technical fix, and outside what was asked for here.
- Nothing was pushed to GitHub — I don't have write access to
  `businesscoachtaj-oss/totality-website` from here, only read access via the
  project's synced knowledge. These five files just need to land in the repo
  root (`robots.txt`, `sitemap.xml`, `og-image.png`, `og-image-nutrition.png`)
  and the per-page snippets need pasting into each file's `<head>`.
