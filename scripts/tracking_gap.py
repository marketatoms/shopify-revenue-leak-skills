#!/usr/bin/env python3
"""Arithmetic for tracking-gap-leak.

Compares, per platform, the purchases the ad platform reports with the orders
Shopify attributes to that channel, for the same dates. Reads
`tracking.gap_flag` and `tracking.min_orders` from references/thresholds.md.

Usage:
  python3 scripts/tracking_gap.py --channel Meta 181 236 --channel Google 104 98
  python3 scripts/tracking_gap.py --orders orders.csv --from 2026-10-01 --to 2026-10-28 \
      --channel Meta 181 236

  --channel NAME REPORTED SHOPIFY_ATTRIBUTED   (repeat per platform)
  --orders adds the Shopify total order count for the dates (context only).
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from leakkit import load_orders, load_thresholds, pct, table, threshold


def gap_verdict(reported: float, shopify: float, flag: float, min_orders: float) -> tuple[str, float | None, str]:
    if shopify < min_orders:
        return "needs_data", None, "too few Shopify orders"
    gap = (reported - shopify) / shopify
    direction = "under-tracking" if gap < 0 else "over-claiming" if gap > 0 else "match"
    verdict = "reconcile" if abs(gap) > flag else "trusted"
    return verdict, gap, direction


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--channel", nargs=3, action="append", metavar=("NAME", "REPORTED", "SHOPIFY"), required=True)
    ap.add_argument("--orders", help="Shopify Orders export (optional, for the store total)")
    ap.add_argument("--from", dest="date_from", help="YYYY-MM-DD, inclusive")
    ap.add_argument("--to", dest="date_to", help="YYYY-MM-DD, inclusive")
    args = ap.parse_args()

    t = load_thresholds()
    flag, min_orders = threshold(t, "tracking.gap_flag"), threshold(t, "tracking.min_orders")

    if args.orders:
        orders = load_orders(args.orders)
        if args.date_from:
            start = datetime.fromisoformat(args.date_from)
            orders = [o for o in orders if o.created >= start]
        if args.date_to:
            end = datetime.fromisoformat(args.date_to) + timedelta(days=1)
            orders = [o for o in orders if o.created < end]
        print(f"Shopify orders in range: {len(orders)}, revenue {sum(o.total for o in orders):,.2f}")

    rows = []
    for name, reported, shopify in args.channel:
        r, s = float(reported), float(shopify)
        verdict, gap, direction = gap_verdict(r, s, flag, min_orders)
        rows.append([name, f"{r:g}", f"{s:g}", pct(gap) if gap is not None else "-", direction,
                     f"{abs(r - s):g}" if gap is not None else "-", verdict])
    print(f"Rule: |gap| > {pct(flag)} -> reconcile; fewer than {min_orders:g} Shopify orders -> needs_data")
    print(table(["Platform", "Platform purchases", "Shopify-attributed", "Gap", "Direction", "Orders apart", "Verdict"], rows))


if __name__ == "__main__":
    main()
