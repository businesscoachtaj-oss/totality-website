#!/usr/bin/env python3
"""Regenerate data/plans.js from data/plans.json. Edit plans.json, then run this.

data/plans.json is a mirror of Livewell-1 lib/tiers.ts (plans, add-ons) and
TotalityNutrition-1 app/subscribe.tsx (Nutrition prices). Update both together.
"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "plans.json").read_text())
(ROOT / "data" / "plans.js").write_text(
    "// Mirror of Livewell-1 lib/tiers.ts. Update both together.\n"
    "// Generated from data/plans.json by tools/build_plans_js.py. Do not edit by hand.\n"
    "// Nutrition prices mirror TotalityNutrition-1 app/subscribe.tsx.\n"
    "window.TOTALITY_PLANS = " + json.dumps(data, indent=2, ensure_ascii=False) + ";\n")
print("Wrote data/plans.js")
