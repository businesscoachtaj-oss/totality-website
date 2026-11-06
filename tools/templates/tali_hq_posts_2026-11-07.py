import pathlib, re, sys

ROOT = pathlib.Path("/home/claude/totality-website")
TPL = (ROOT / "blog/posts/contractor-pt-first-8-weeks.html").read_text()
OLD_SLUG = "contractor-pt-first-8-weeks"
OLD_H1 = "Your First 8 Weeks as a Contractor PT: A Checklist"
OLD_DESC = "Many clubs start new contractor PTs with a few rent-free weeks. A week by week checklist for the paperwork, the rent maths, money habits and your first clients."
DATE = "2026-11-07"

CTA_CSS = """
  .post-cta.cta-talihq { background: rgba(108,52,131,0.08); }
  .post-cta.cta-talihq h2 { color: #6C3483; }
  .post-cta.cta-talihq .post-cta-btn { background: #6C3483; }
  .post-cta.cta-talihq .post-cta-btn:hover { background: #5B2A70; }
"""

def cta(slug):
    return f"""  <hr>

  <div class="post-cta cta-talihq">
    <h2>Try Tali HQ Free</h2>
    <p>
      Tali HQ is an AI manager for business and life from Totality 360. She writes your morning brief,
      sorts your inbox, drafts replies and invoices, and keeps what she learns in a brain you can see.
    </p>
    <a href="https://talihq.com.au/?ref=blog-{slug}" class="post-cta-btn" target="_blank" rel="noopener" data-track-placement="blog_post_cta">Start free</a>
    <p class="post-cta-fine">Free plan with 250 messages a month. Every new account gets a 7 day free trial of Tali HQ. Prices in AUD.</p>
  </div>
"""

POSTS = [
 dict(slug="how-talis-brain-works",
  h1="How Tali's Brain Works",
  desc="Tali HQ files what she learns into parts of a brain, a bit like yours. What goes where, how she settles contradictions, and how you can see and delete any of it.",
  body="""  <p>When you tell Tali something worth keeping, she doesn't drop it into one long list. She files it into a part of a brain, a bit like yours does. Facts go one place, people go another, lessons somewhere else again. It sounds like a gimmick until you need to find something, and then it's just tidy.</p>

  <p>This is a plain walk through what goes where, and what you can do about it.</p>

  <h2>The parts she fills as you talk</h2>
  <ul>
    <li><strong>Hippocampus:</strong> facts and events. Your business hours, the day you signed a new client, the price you settled on.</li>
    <li><strong>Temporal lobe:</strong> the people in your world, and what she knows about each of them.</li>
    <li><strong>Cerebellum:</strong> lessons and mistakes. A lesson that keeps holding up becomes proven.</li>
    <li><strong>Frontal lobe:</strong> rules and preferences she sticks to, including the big one: nothing goes out without your yes.</li>
    <li><strong>Prefrontal cortex:</strong> plans, ideas, your live goals and the decisions you haven't made yet.</li>
    <li><strong>Amygdala:</strong> anything urgent, and contradictions for you to settle.</li>
    <li><strong>Occipital lobe:</strong> what she saw in photos and screenshots you sent, and the images she made for you.</li>
  </ul>

  <h2>The parts that keep her running</h2>
  <p>Some parts aren't memories so much as machinery. The parietal lobe is what she can feel, meaning your connected Gmail and Calendar. The hypothalamus is her schedule: the morning brief, health checks, the end of day shutdown and night school. The thalamus files every new memory into the right part, and the brainstem keeps every memory searchable.</p>

  <h2>When two memories disagree</h2>
  <p>People change their minds. If you told Tali in March that you'd never work Saturdays and in June that Saturdays are now your busiest day, she shouldn't quietly pick one. A new memory that contradicts an old one lands in the amygdala, and you settle it on the Brain screen: keep the new one, keep the old one, or say both are true.</p>

  <h2>You can see all of it</h2>
  <p>Open the Brain screen, tap a part and read what she keeps there. Anything you don't want her to remember, you delete. That matters more than any clever filing. An assistant that remembers you is only comfortable if you can check what it remembers.</p>

  <h2>What gets shared, and what never does</h2>
  <p>Tali also keeps a shared brain of general business lessons that every user's Tali learns from. Lessons from night school, and lessons, mistakes and rules that have proven themselves in your chats, may be added to it. Before anything is shared it's rewritten as a general lesson with no names, clients, places, prices or contact details, and it's left out if it can't be made general.</p>
  <p>Your facts, people, events, photos, journal and chats are never shared. Sharing is on by default, and you can switch it off in Tali HQ under Me, Settings, Help every Tali learn. The <a href="/privacy.html">privacy policy</a> has the detail.</p>

  <p>If you'd like to see the brain before you sign up, there's a demo with made up memories on the <a href="/tali-hq.html#brain">Tali HQ page</a>. Spin it, tap a part, and have a look around.</p>
"""),
 dict(slug="tali-night-school",
  h1="What Tali Does at Night School",
  desc="On Tali HQ Pro, Tali studies while you sleep: topics you pick, three nights a week or every night, from sources she shows you. How it works and what you get.",
  body="""  <p>Most software is the same on day three hundred as it was on day one. Tali is meant to be a bit different. On Tali HQ Pro she goes to night school, and she turns up the next morning knowing a little more about the work you do.</p>

  <h2>How a night works</h2>
  <p>You pick what she studies. It might be your industry, a part of the business you'd like to get better at, or a question you keep meaning to look into. You also pick how often: three nights a week, or every night.</p>
  <p>While you sleep, she searches the web, reads, and writes up what she learned. She shows her sources, so you can see where an idea came from and check it yourself.</p>

  <h2>Where it goes</h2>
  <p>What she learns is filed into her brain like any other memory, mostly as lessons. You can open the Brain screen, read what she kept and delete anything you don't think is right.</p>

  <h2>Why bother</h2>
  <p>A morning brief or a drafted reply is only as good as what sits behind it. If Tali has spent a few nights on how your industry handles quiet clients, or how people price the kind of work you do, her drafts and suggestions get a little sharper. It's slow, and that's the point. The value builds the same way it does for a person who keeps reading about their trade.</p>

  <h2>What it costs</h2>
  <p>Night school is part of Tali HQ Pro, at A$39.99 a month. Every new account starts with a 7 day free trial of Tali HQ, and there's a free plan if you'd rather just talk to her first. See the <a href="/tali-hq.html#pricing">plans</a>.</p>
"""),
 dict(slug="why-tali-asks-before-sending",
  h1="Why Tali Asks Before She Sends Anything",
  desc="Tali HQ drafts emails, invoices and bookings, but nothing goes out until you tap yes. Why we built it that way, and what it means day to day.",
  body="""  <p>Tali can write an email, put together an invoice and find a gap in your calendar. She can't send any of them on her own. Every one waits for you to tap yes. That's not a missing feature. We built it that way on purpose.</p>

  <h2>What she does, and what you do</h2>
  <ul>
    <li><strong>Email:</strong> she sorts your Gmail or Outlook and drafts the replies. You read the draft, change it if you like, and tap send. It goes from your own address.</li>
    <li><strong>Invoices:</strong> she drafts the invoice for the right client. You tap send, it goes out through your own Stripe, and it marks itself paid when your client pays.</li>
    <li><strong>Bookings:</strong> she knows your week from Google Calendar and suggests where things fit. She only books when you approve.</li>
    <li><strong>Follow-ups:</strong> she spots clients who've gone quiet and drafts a check-in. You decide whether it goes.</li>
  </ul>

  <h2>Why it works this way</h2>
  <p>The things a small business sends are personal. A reply to a client, a price, a reminder about money owed. Each one carries your name, and a wrong one is hard to take back. A draft you can glance over in ten seconds keeps most of the time saving and almost none of the risk.</p>
  <p>It also makes Tali easier to trust while you get to know her. You see what she would have said, every time, and you notice quickly where she's spot on and where she needs a nudge.</p>

  <h2>What she never asks for</h2>
  <p>Tali never asks for your passwords. Gmail, Outlook, Google Calendar and Stripe are connected through each company's own sign-in, and you can disconnect them in the app.</p>

  <p>You'll find the yes button on Today, where drafts that need you sit together, so a morning's worth of approvals takes a minute or two. More on <a href="/tali-hq.html">Tali HQ</a>.</p>
"""),
 dict(slug="tali-morning-brief",
  h1="What's in Tali's Morning Brief",
  desc="Every morning Tali HQ tells you what came in, who needs a reply, what's on today and one nudge on your health or goals. What's in it and how to set the time.",
  body="""  <p>The first ten minutes of a work day often go on finding out what the day holds. Opening the inbox, checking the calendar, remembering who you promised to get back to. Tali's morning brief does that part for you, at the time you pick.</p>

  <h2>What's in it</h2>
  <ul>
    <li><strong>What came in overnight</strong>, from your connected Gmail or Outlook, sorted into what needs you and what doesn't.</li>
    <li><strong>Who needs a reply</strong>, with drafts already waiting.</li>
    <li><strong>What's on today</strong>, from Google Calendar.</li>
    <li><strong>Your money</strong>, so you know where things stand.</li>
    <li><strong>Who has gone quiet</strong>, so a client doesn't slip away without anyone noticing.</li>
    <li><strong>One nudge</strong> on your health or goals.</li>
  </ul>

  <h2>During the day</h2>
  <p>On Tali HQ she also runs health checks twice a day. They look for overdue invoices, follow-ups, quiet clients, new leads, drafts waiting on you and reminders. Anything that needs you shows up on Today.</p>

  <h2>At the end of the week</h2>
  <p>Every Friday she checks in on your goals with you. That one is on the free plan too.</p>

  <h2>Getting it</h2>
  <p>The morning brief comes with Tali HQ at A$19.99 a month and Tali HQ Pro at A$39.99. Every new account gets a 7 day free trial of Tali HQ, so you can try a week of mornings before you decide. See the <a href="/tali-hq.html#pricing">plans</a>.</p>
"""),
]

for p in POSTS:
    s = TPL.replace(OLD_SLUG, p["slug"]).replace(OLD_H1, p["h1"]).replace(OLD_DESC, p["desc"])
    s = s.replace("2026-10-25", DATE).replace("25 October 2026", "7 November 2026")
    s = re.sub(r'(<article class="post-body">\n).*?(</article>)', lambda m: m.group(1) + p["body"] + "\n" + cta(p["slug"]) + m.group(2), s, flags=re.S)
    s = s.replace("  .badge-business {", CTA_CSS + "  .badge-business {", 1)
    for bad in ["contractor", "Contractor", "—", "–"]:
        assert bad not in s.split('<article class="post-body">')[1].split("</article>")[0], (p["slug"], bad)
    (ROOT / "blog/posts" / f"{p['slug']}.html").write_text(s)
    print(p["slug"])
