#!/usr/bin/env python3
"""Arithmetic for second-order-gap-leak.

Second-order rate within a window, by first-order month and by first product,
from a Shopify Orders export. Customers are identified by email. Only customers
whose window has fully passed (before the last order date in the export) count.
Reads repeat.* keys from references/thresholds.md.

Usage:
  python3 scripts/repeat_rate.py --orders orders.csv [--window-days 60]
"""

from __future__ import annotations

import argparse
import statistics
from collections import defaultdict
from datetime import timedelta

from leakkit import load_orders, load_thresholds, pct, table, threshold


def analyse(orders, t, window_days: int | None = None):
    window = int(window_days or threshold(t, "repeat.window_days"))
    floor = threshold(t, "repeat.second_order_rate_floor")
    min_cohort = threshold(t, "repeat.min_cohort_customers")
    gap_ratio = threshold(t, "repeat.product_gap_ratio")

    by_email = defaultdict(list)
    for o in orders:
        if o.email:
            by_email[o.email].append(o)
    as_of = orders[-1].created
    cutoff = as_of - timedelta(days=window)

    eligible, came_back, gaps = 0, 0, []
    months = defaultdict(lambda: [0, 0])
    products = defaultdict(lambda: [0, 0])
    for os_ in by_email.values():
        os_.sort(key=lambda o: o.created)
        first = os_[0]
        if first.created > cutoff:
            continue  # window not finished
        eligible += 1
        second = next((o for o in os_[1:] if o.created <= first.created + timedelta(days=window)), None)
        back = second is not None
        came_back += back
        if back:
            gaps.append((second.created - first.created).days)
        m = first.created.strftime("%Y-%m")
        months[m][0] += 1
        months[m][1] += back
        top = max(first.items, key=lambda i: i.price * i.quantity).name if first.items else "(unknown)"
        products[top][0] += 1
        products[top][1] += back

    if eligible == 0:
        return {"window": window, "eligible": 0}
    rate = came_back / eligible
    prod_rows = []
    for name, (n, b) in sorted(products.items(), key=lambda kv: -kv[1][0]):
        r = b / n
        if n < min_cohort:
            v = "too_small"
        elif r < gap_ratio * rate:
            v = "dead_end_product"
        elif r >= 1.5 * rate:
            v = "gateway_product"
        else:
            v = "normal"
        prod_rows.append([name, n, b, pct(r), f"{r / rate:.2f}x" if rate else "-", v])
    month_rows = [[m, n, b, pct(b / n)] for m, (n, b) in sorted(months.items())]
    return {"window": window, "eligible": eligible, "came_back": came_back, "rate": rate,
            "verdict": "retention_leak" if rate < floor else "healthy",
            "median_days": statistics.median(gaps) if gaps else None,
            "products": prod_rows, "months": month_rows, "floor": floor, "as_of": as_of}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--orders", required=True)
    ap.add_argument("--window-days", type=int)
    args = ap.parse_args()
    r = analyse(load_orders(args.orders), load_thresholds(), args.window_days)
    if not r["eligible"]:
        print(f"needs_data: no first-time customers whose {r['window']}-day window has finished.")
        return
    print(f"Window: {r['window']} days (as of {r['as_of']:%Y-%m-%d}). First-time customers judged: {r['eligible']}")
    print(f"Came back: {r['came_back']} -> second-order rate {pct(r['rate'])} (floor {pct(r['floor'])}) -> {r['verdict']}")
    if r["median_days"] is not None:
        print(f"Median days to second order: {r['median_days']:g}")
    print("\nBy first product")
    print(table(["First product", "Customers", "Came back", "Rate", "vs store", "Verdict"], r["products"]))
    print("\nBy first-order month")
    print(table(["Month", "Customers", "Came back", "Rate"], r["months"]))


if __name__ == "__main__":
    main()
