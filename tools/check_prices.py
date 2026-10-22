#!/usr/bin/env python3
"""Flag any $ price on a site page that is not in data/plans.json (plans, add-ons,
Nutrition, one-off products) or tools/price_allowlist.json. Also flags bare "$"
prices that should be written "A$".

Usage: python3 tools/check_prices.py   (from the repo root or anywhere)
Exit code 1 if anything unknown is found.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "plans.json").read_text())

known = set()
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, str):
        for m in re.findall(r"A\$\s?([\d,]+(?:\.\d{1,2})?)", o):
            known.add(m.replace(",", ""))
walk(data)

# Prices that are not plan prices but legitimately appear (guides, calculators examples).
# Add here deliberately, with a reason.
_allow_file = ROOT / "tools" / "price_allowlist.json"
ALLOW = set(json.loads(_allow_file.read_text()).get("allow", {})) if _allow_file.exists() else set()

# Matches "A$29.99" and bare "$29.99" (bare prices should usually say A$ on this site).
pat = re.compile(r"(?<![\w{])(A)?\$\s?(\d[\d,]*(?:\.\d{1,2})?)")
bad = 0
bare = 0
for page in sorted(ROOT.rglob("*.html")):
    if any(p.startswith(".") for p in page.relative_to(ROOT).parts):
        continue
    for i, line in enumerate(page.read_text(errors="ignore").splitlines(), 1):
        for m in pat.finditer(line):
            v = m.group(2).replace(",", "").rstrip(".")
            if v not in known and v not in ALLOW:
                bad += 1
                print(f"{page.relative_to(ROOT)}:{i}: {m.group(0)} not in plans.json")
            elif not m.group(1) and v not in ALLOW and not re.match(r"\s*(<small>)?\s*AUD", line[m.end():]):
                bare += 1
                print(f"{page.relative_to(ROOT)}:{i}: {m.group(0)} is a known price but should be written A${m.group(2)}")
print(f"\n{bad} unknown price(s), {bare} bare $ price(s). Known prices: {', '.join(sorted(known, key=float))}")
sys.exit(1 if bad else 0)
