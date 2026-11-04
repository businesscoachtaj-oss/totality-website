# How-to guides: brief for every writer

Taj wants complete "how to use" guides for Totality (gym owner and admin, trainer, client), Totality Nutrition and Tali HQ. They replace him personally walking every user through the app, so a brand new user who has never seen the app must be able to set up and use **everything** from the guide alone. Cover every screen, every button, every setting, every plan difference, every common question and every "what happens if". Long is good. Accuracy matters more than anything.

## Where things go

- Source: `/home/claude/totality-website/_help-src/<guide>/` (Jekyll ignores folders starting with `_`, so the source is not published).
  - `guide.json`: `{"title", "audience", "accent": "orange"|"blue"|"purple", "icon", "updated": "5 November 2026", "groups": [{"title","pages":[slugs]}], "pages": [slugs in order]}`. The first page slug must be `index`.
  - One `<slug>.md` per page with front matter `title` and `summary` (one sentence).
- Images: `/home/claude/totality-website/help/<guide>/img/` and referenced as `img/<file>.png`.
- Build: `python3 /home/claude/totality-website/_help-src/build.py <guide>` writes `help/<guide>/*.html`, `search.json` and the hub `help/index.html`. Read the top of `build.py` for the markdown extras: `[[Free]]` style badges, `!phone[caption](img/x.png)`, `!phones[a](img/a.png)[b](img/b.png)`, `!wide[...]`, `:::tip / :::note / :::warn / :::tali` callouts, `!steps` before a numbered list, `?? Question` FAQ entries.
- Check your pages look right: `python3 /tmp/claude-0/-home-claude/126757c1-2585-5cb2-b58f-5ab5f29b06c9/scratchpad/helpshot.py /help/<guide>/<page>.html /tmp/claude-0/-home-claude/126757c1-2585-5cb2-b58f-5ab5f29b06c9/scratchpad/check_<guide>` then Read the `_desk.png` / `_mob.png`. Spot check at least the index and three other pages.
- Do NOT commit, push, switch branches, or edit anything outside your own `_help-src/<guide>/` and `help/<guide>/` folders (other writers are working in parallel). Do not edit build.py, guide.css or guide.js; if you need a feature, describe it in your report.

## Truth rules

- Read the app code before you write about a feature. Document what the code actually does: button labels exactly as they appear on screen, real limits, real prices from the code or the website (`/home/claude/totality-website/pricing.html`, `get-nutrition.html`, `tali-hq.html`), real plan rules. If something is behind a flag, unfinished, "coming soon" or not in the code, leave it out. Never invent a feature.
- When the code and the website disagree, follow the code and mention the conflict in your report.
- Support contact: `admintotality@gmail.com` (the footer already shows it).
- Platforms: each app runs on iPhone, Android and the web (PWA). Totality web is `totalityapp.com.au`, Nutrition web is `totalitynutrition.com.au`, Tali HQ web is `tali-hq.vercel.app`. Taj has no iPhone; still describe iPhone steps from the code (for example Apple Health on iPhone, Health Connect on Android).
- App updates arrive over the air: open the app, close it fully, open it again. A fresh install still needs that one close and reopen.

## Writing rules (Taj's)

- Australian English ("programme", "colour", "organise"). No em dashes or en dashes anywhere. Use commas, full stops or "to".
- Plain, warm, direct. Second person ("you"). Short sentences. No hype, no "seamless", no "unlock", no rhetorical contrast lines like "It's not X, it's Y". No "here's the thing".
- Lead each page with what the reader can do, then the steps. Use `!steps` for anything with more than two steps.
- Use `:::tali` sparingly (a couple of times per guide) for friendly tips in Tali's voice: Aussie, cheeky, short, "programme" not "program".
- Every page ends with a short `## Questions` section of real questions a user would ask, as `??` entries.
- Mark plan-gated features with badges inline, e.g. "Barcode scanning [[Free]] 7 a week, unlimited on [[Paid]]".

## Screens (required, from the real app, never drawn)

- Capture from the real web builds already exported in `/home/claude/depth_mock/` with Supabase mocked by Playwright route interception. Copy the patterns in the existing scripts there (named per guide below). Do NOT run `expo export` again and do NOT touch the app repos; the builds are already there.
- Fake demo data only (the Iron Works gym, trainer Sam, made up clients like Priya Nair, Lou Harvey, Matthew Pex, Zack Donaldson, Ava Chen). Never real customer names or emails.
- 390 x 844 viewport, deviceScaleFactor 2, PNG. Then shrink each to 600 px wide with PIL to keep pages light. Name files `<page-slug>-<what>.png`.
- Every page that describes a screen shows that screen. Aim for at least one screen per page and more on setup pages. If a screen will not render after three honest attempts at mocking its queries, write the page without it and list it in your report.
- Look at every screen you use (Read the PNG) before putting it in a page. Blank, clipped, error or spinner screens do not go in.

## Report back (under 300 words)

Pages written (count), screens captured (count), anything you could not capture, any conflicts between code and website, anything unfinished.
