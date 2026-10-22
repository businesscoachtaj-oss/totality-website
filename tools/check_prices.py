#!/usr/bin/env python3
"""Flag any A$ price on a site page that is not in data/plans.json.

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
ALLOW = set(json.loads((ROOT / "tools" / "price_allowlist.json").read_text())) if (ROOT / "tools" / "price_allowlist.json").exists() else set()

pat = re.compile(r"A\$\s?([\d,]+(?:\.\d{1,2})?)")
bad = 0
for page in sorted(ROOT.rglob("*.html")):
    if any(p.startswith(".") for p in page.relative_to(ROOT).parts):
        continue
    for i, line in enumerate(page.read_text(errors="ignore").splitlines(), 1):
        for m in pat.finditer(line):
            v = m.group(1).replace(",", "").rstrip(".")
            if v not in known and v not in ALLOW:
                bad += 1
                print(f"{page.relative_to(ROOT)}:{i}: A${m.group(1)} not in plans.json")
print(f"\n{bad} unknown A$ price(s). Known prices: {', '.join(sorted(known, key=float))}")
sys.exit(1 if bad else 0)
