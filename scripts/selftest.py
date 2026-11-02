#!/usr/bin/env python3
"""Self-test: recomputes the scripts' key numbers by a second, independent route
(reading the CSV directly, without leakkit) and checks they agree. Also checks
that bad input is refused with a clear message instead of a silent empty result.

Usage: python3 scripts/selftest.py
"""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import basket_value  # noqa: E402
import discount_leak  # noqa: E402
import repeat_rate  # noqa: E402
import tracking_gap  # noqa: E402
from leakkit import load_orders, load_thresholds  # noqa: E402

SAMPLE = ROOT / "examples" / "sample-orders-export.csv"
failures = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global failures
    print(("PASS  " if ok else "FAIL  ") + name + (f"  ({detail})" if detail and not ok else ""))
    failures += 0 if ok else 1


# Independent read: first row per order number, skip cancelled.
raw: dict[str, dict] = {}
units: dict[str, int] = {}
with SAMPLE.open(newline="") as fh:
    for row in csv.DictReader(fh):
        n = row["Name"]
        if n not in raw:
            raw[n] = row
            units[n] = 0
        units[n] += int(row["Lineitem quantity"])
live = {n: r for n, r in raw.items() if not r["Cancelled at"]}

t = load_thresholds()
orders = load_orders(SAMPLE)

check("order count matches an independent read", len(orders) == len(live), f"{len(orders)} vs {len(live)}")
check("revenue matches", abs(sum(o.total for o in orders) - sum(float(r["Total"]) for r in live.values())) < 0.01)
check("units per order counted across line-item rows",
      all(o.units == units[o.name] for o in orders))

# Thresholds are read from the file, not hard-coded.
check("thresholds parsed (15% -> 0.15)", abs(t["tracking.gap_flag"] - 0.15) < 1e-9)
check("thresholds parsed (multiplier)", abs(t["discount.spike_multiple"] - 3) < 1e-9)

# Discount share by a second route.
d = discount_leak.analyse(orders, t, {"SARAH15"})
disc = [r for r in live.values() if float(r["Discount Amount"] or 0) > 0 or r["Discount Code"]]
check("discount share agrees", abs(d["share"] - len(disc) / len(live)) < 1e-9)
check("leaked private code detected", any(code == "SARAH15" for code, *_ in d["leaked"]))
d_public = discount_leak.analyse(orders, t, set())
check("same spike on a public code is not called leaked", not d_public["leaked"])

# Basket near misses by a second route.
b = basket_value.analyse(orders, t, 50.0)
low = 50 * (1 - t["aov.near_threshold_band"])
near = [r for r in live.values() if low <= float(r["Subtotal"]) < 50]
check("near-miss count agrees", len(b["near"]) == len(near), f"{len(b['near'])} vs {len(near)}")
from leakkit import LineItem, Order  # noqa: E402
edge = [Order(f"#E{i}", f"e{i}@x.com", datetime(2026, 10, 1), s, s, "", 0, 0, "web", [LineItem("x", 1, s)])
        for i, s in enumerate([42.49, 42.50, 49.99, 50.00])]
eb = basket_value.analyse(edge, t, 50.0)
check("near-miss band includes 42.50 and 49.99, excludes 42.49 and 50.00",
      sorted(o.subtotal for o in eb["near"]) == [42.50, 49.99])
single = sum(1 for n in live if units[n] == 1) / len(live)
check("single-unit share agrees", abs(b["single_share"] - single) < 1e-9)

# Repeat rate by a second route.
rr = repeat_rate.analyse(orders, t)
by_email: dict[str, list[datetime]] = {}
for r in live.values():
    by_email.setdefault(r["Email"].lower(), []).append(datetime.strptime(r["Created at"][:19], "%Y-%m-%d %H:%M:%S"))
as_of = max(dt for v in by_email.values() for dt in v)
window = timedelta(days=int(t["repeat.window_days"]))
elig = back = 0
for dates in by_email.values():
    dates.sort()
    if dates[0] > as_of - window:
        continue
    elig += 1
    back += any(dates[0] < x <= dates[0] + window for x in dates[1:]) or (len(dates) > 1 and dates[1] == dates[0])
check("repeat eligible customers agree", rr["eligible"] == elig, f"{rr['eligible']} vs {elig}")
check("repeat rate agrees", rr["came_back"] == back, f"{rr['came_back']} vs {back}")

# Tracking gap logic.
v, gap, direction = tracking_gap.gap_verdict(181, 236, t["tracking.gap_flag"], t["tracking.min_orders"])
check("tracking: 181 vs 236 is a 23.3% under-tracking gap -> reconcile",
      v == "reconcile" and direction == "under-tracking" and abs(gap + 0.2330508) < 1e-6)
v2, _, _ = tracking_gap.gap_verdict(104, 98, t["tracking.gap_flag"], t["tracking.min_orders"])
check("tracking: 104 vs 98 -> trusted", v2 == "trusted")
v3, _, _ = tracking_gap.gap_verdict(9, 12, t["tracking.gap_flag"], t["tracking.min_orders"])
check("tracking: too few orders -> needs_data", v3 == "needs_data")

# Refusal paths must fail loudly.
for script, args in [("basket_value.py", ["--orders", "missing.csv", "--threshold", "50"]),
                     ("repeat_rate.py", ["--orders", str(ROOT / "README.md")])]:
    p = subprocess.run([sys.executable, str(HERE / script), *args], capture_output=True, text=True)
    check(f"{script} refuses bad input with a message", p.returncode != 0 and (p.stderr or p.stdout).strip() != "")

print("\nAll checks passed" if not failures else f"\n{failures} check(s) failed")
sys.exit(1 if failures else 0)
