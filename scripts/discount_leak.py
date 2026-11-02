#!/usr/bin/env python3
"""Arithmetic for discount-leak.

From a Shopify Orders export: share of orders with a code, discount depth, and
per code the latest week's uses against its average over the 4 weeks before.
Reads discount.* keys from references/thresholds.md.

Usage:
  python3 scripts/discount_leak.py --orders orders.csv [--private SARAH15,VIP20]

"Latest week" = the 7 days ending on the last order date in the export.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import timedelta

from leakkit import load_orders, load_thresholds, pct, table, threshold


def analyse(orders, t, private: set[str]):
    share_flag = threshold(t, "discount.order_share_flag")
    depth_flag = threshold(t, "discount.depth_flag")
    spike = threshold(t, "discount.spike_multiple")
    min_code = threshold(t, "discount.min_code_orders")

    discounted = [o for o in orders if o.discount_amount > 0 or o.discount_code]
    share = len(discounted) / len(orders)
    disc_total = sum(o.discount_amount for o in discounted)
    rev_disc = sum(o.total for o in discounted)
    depth = disc_total / (rev_disc + disc_total) if (rev_disc + disc_total) else 0.0

    end = orders[-1].created
    week_start = end - timedelta(days=7)
    hist_start = week_start - timedelta(days=28)
    has_history = orders[0].created <= hist_start

    by_code = defaultdict(list)
    for o in discounted:
        if o.discount_code:
            by_code[o.discount_code].append(o)

    rows, leaked, small = [], [], []
    for code, os_ in sorted(by_code.items(), key=lambda kv: -sum(o.discount_amount for o in kv[1])):
        n = len(os_)
        given = sum(o.discount_amount for o in os_)
        rev = sum(o.total for o in os_)
        d = given / (rev + given) if (rev + given) else 0.0
        last = sum(1 for o in os_ if o.created > week_start)
        prior = sum(1 for o in os_ if hist_start < o.created <= week_start) / 4
        ratio = (last / prior) if prior else None
        if n < min_code:
            small.append(code)
            continue
        if not has_history:
            verdict = "needs_data (spike)"
        elif ratio is not None and ratio >= spike:
            verdict = "leaked" if code in private else "promo_effect"
        else:
            verdict = "normal"
        if verdict == "leaked":
            extra = last - prior
            avg_disc = given / n
            leaked.append((code, extra, extra * avg_disc))
        rows.append([code, n, f"{rev:,.2f}", f"{given:,.2f}", pct(d), f"{last} vs {prior:.1f}/wk" + (f" ({ratio:.1f}x)" if ratio else ""), verdict])

    return {
        "orders": len(orders), "discounted": len(discounted), "share": share, "depth": depth,
        "given": disc_total, "share_verdict": "discount_habit" if share > share_flag else "ok",
        "depth_verdict": "too_deep" if depth > depth_flag else "ok",
        "rows": rows, "leaked": leaked, "small": small, "has_history": has_history,
        "flags": (share_flag, depth_flag, spike, min_code),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--orders", required=True)
    ap.add_argument("--private", default="", help="Comma-separated codes meant to be private")
    args = ap.parse_args()
    t = load_thresholds()
    r = analyse(load_orders(args.orders), t, {c.strip().upper() for c in args.private.split(",") if c.strip()})
    share_flag, depth_flag, spike, min_code = r["flags"]
    print(f"Orders: {r['orders']}, with a discount: {r['discounted']} ({pct(r['share'])}, flag {pct(share_flag)}) -> {r['share_verdict']}")
    print(f"Discount given: {r['given']:,.2f}; depth on discounted orders: {pct(r['depth'])} (flag {pct(depth_flag)}) -> {r['depth_verdict']}")
    if not r["has_history"]:
        print("Spike check: needs_data (export covers less than 5 weeks)")
    print(f"Spike rule: latest 7 days >= {spike:g}x the weekly average of the 4 weeks before; codes with < {min_code:g} orders not judged")
    print(table(["Code", "Orders", "Revenue", "Discount given", "Depth", "Latest week vs avg", "Verdict"], r["rows"]))
    for code, extra, cost in r["leaked"]:
        print(f"LEAKED {code}: about {extra:.0f} extra uses last week, about {cost:,.2f} given away above normal")
    if r["small"]:
        print(f"Small codes (no verdict): {', '.join(r['small'])}")


if __name__ == "__main__":
    main()
