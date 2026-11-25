"""Totality guide templates (25 Nov 2026, Taj: "a template version of this, and a few others for other
questions that come up, that when people want a call, we quickly personalise to them").

Usage:  python3 build.py <guide> [people/<person>.json] [out.pdf]
  guide: getting-paid | clients-across | studio-setup | coaching
  No person file = the general version anyone can be sent.

Template rules: {{key}} is replaced from the person file (falling back to DEFAULTS[guide]).
<!--if:key-->...<!--endif:key--> shows only when key has a value, <!--ifnot:key-->...<!--endifnot:key--> only when it doesn't.
{{HEADER:subtitle}}, {{FOOTER:middle text}} and {{CONTACT}} are the shared page parts.
Keep the words simple, accurate to the app, no upselling (Taj, 25 Nov)."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AS_AT = "25 November 2026"

def money(x): return f"{x:,.2f}"

DEFAULTS = {
  'getting-paid': dict(
    title="Getting paid with Totality",
    lede="This guide shows how to move your clients onto automatic payments: your options, what each one costs, and the exact steps in the app. The last page has a switch plan and a checklist.",
    pay_now_short="Cash or bank transfer", keep_use_for="clients who'd rather pay you directly.",
    amount=120, amount_label="weekly payment",
    switch_title="Your switch, step by step", switch_in="",
    t1_when="Now", t2_when="This week", t3_when="Before you switch", t4_when="Switch day",
    start_item="Start each client's plan on your switch day",
    abn_text="Free from the Australian Business Register (abr.gov.au). As a sole trader you have one ABN for all your business activities.",
    gst_text="You must register once your GST turnover reaches A$75,000 a year, within 21 days. Under that, it's optional.",
  ),
  'clients-across': dict(title="Bringing your clients into Totality",
    lede="How to add your clients, what they do the first time they log in, and how to bring across the sessions they've already paid for and their programmes.",
    from_system="a spreadsheet or another app"),
  'studio-setup': dict(from_system="your old system or a spreadsheet", title="Setting up your studio in Totality",
    lede="Everything to get your studio running: your account, your members, your team, your timetable, your memberships and getting paid. Do it in this order and each step builds on the last."),
  'coaching': dict(has_tali="1", title="Coaching your clients in Totality",
    lede="Build a programme once and give it to any client, run their sessions, and keep in touch every week with check-ins."),
}

def header(v, sub):
    who = f"Setup guide for {v['for_name']}" if v.get('for_name') else "Setup guide"
    return (f'<div class="top"><img src="icon-totality.png" alt="" style="width:30px;height:30px;border-radius:7px">'
            f'<div class="brand">Totality <span>360</span></div><div class="right">{who}<br>{sub}</div></div>')

def contact(v):
    return ('<div class="contact"><div><b>Questions?</b> Email Taj any time at <b>taj@totality360.com.au</b>. '
            'He set up these tools and is happy to walk you through them.</div></div>')

def render(guide, person):
    v = dict(DEFAULTS.get(guide, {})); v.update(person); v.setdefault('as_at', AS_AT)
    if guide == 'getting-paid':
        a = float(v['amount']); tot = round(a * 0.0125, 2)
        card = round(a * 0.0165 + 0.30, 2); bank = round(min(a * 0.01 + 0.30, 3.50), 2)
        v.update(tot_fee=money(tot), card_fee=money(card), bank_fee=money(bank),
                 card_keep=money(a - tot - card), bank_keep=money(a - tot - bank), amount=f"{a:,.0f}")
    src = open(os.path.join(HERE, f'{guide}.html')).read()
    for k in set(re.findall(r'<!--if:(\w+)-->', src)):
        src = re.sub(rf'<!--if:{k}-->(.*?)<!--endif:{k}-->', (lambda m: m.group(1)) if v.get(k) else '', src, flags=re.S)
    for k in set(re.findall(r'<!--ifnot:(\w+)-->', src)):
        src = re.sub(rf'<!--ifnot:{k}-->(.*?)<!--endifnot:{k}-->', '' if v.get(k) else (lambda m: m.group(1)), src, flags=re.S)
    pages = src.count('<section class="page">')
    n = iter(range(1, pages + 1))
    src = src.replace('{{as_at}}', v['as_at'])
    src = re.sub(r'\{\{FOOTER:(.*?)\}\}', lambda m: f'<div class="foot"><span>Totality 360 Pty Ltd, ABN 58 698 902 975</span><span>{m.group(1)}</span><span>{next(n)} of {pages}</span></div>', src)
    src = re.sub(r'\{\{HEADER:(.*?)\}\}', lambda m: header(v, m.group(1)), src)
    src = src.replace('{{CONTACT}}', contact(v))
    src = re.sub(r'\{\{(\w+)\}\}', lambda m: str(v.get(m.group(1), '')), src)
    css = open(os.path.join(HERE, 'base.css')).read()
    title = v.get('title', 'Totality guide')
    return f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head><body>{src}</body></html>'

if __name__ == '__main__':
    guide = sys.argv[1]
    person = json.load(open(sys.argv[2])) if len(sys.argv) > 2 and sys.argv[2].endswith('.json') else {}
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, '..', f"Totality_{guide.replace('-', '_').title()}_Guide{('_for_' + person['file_name']) if person.get('file_name') else ''}.pdf")
    html_path = os.path.join(HERE, f'_{guide}.render.html')
    open(html_path, 'w').write(render(guide, person))
    left = re.findall(r'\{\{\w+\}\}', open(html_path).read())
    if left: print('WARNING unfilled:', set(left))
    subprocess.run(['node', os.path.join(HERE, 'pdf.js'), html_path, os.path.abspath(out)], check=True)
    print(os.path.abspath(out))
