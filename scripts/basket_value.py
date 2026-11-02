#!/usr/bin/env python3
"""Arithmetic for basket-value-gap-leak.

AOV, near-miss orders just under the free-shipping threshold, and the share of
single-unit orders, from a Shopify Orders export. Reads aov.* keys from
references/thresholds.md.

Usage:
  python3 scripts/basket_value.py --orders orders.csv --threshold 50
  python3 scripts/basket_value.py --orders orders.csv --threshold none
"""

from __future__ import annotations

import argparse
from collections import Counter

from leakkit import load_orders, load_thresholds, pct, table, threshold


def analyse(orders, t, free_ship: float | None):
    band = threshold(t, "aov.near_threshold_band")
    near_flag = threshold(t, "aov.near_threshold_share_flag")
    single_flag = threshold(t, "aov.single_item_share_flag")
    min_orders = threshold(t, "aov.min_orders")

    n = len(orders)
    aov = sum(o.total for o in orders) / n
    single = [o for o in orders if o.units == 1]
    single_share = len(single) / n
    alone = Counter(o.items[0].name for o in single if o.items)

    near = None
    if free_ship:
        low = free_ship * (1 - band)
        near = [o for o in orders if low <= o.subtotal < free_ship]
    near_share = len(near) / n if near is not None else None

    if n < min_orders:
        verdicts = ["needs_data"]
    else:
        verdicts = []
        if near_share is not None and near_share > near_flag:
            verdicts.append("threshold_gap")
        if single_share > single_flag:
            verdicts.append("bundle_gap")
        verdicts = verdicts or ["healthy"]
    return {"n": n, "aov": aov, "near": near, "near_share": near_share, "single_share": single_share,
            "alone": alone.most_common(5), "verdicts": verdicts, "band": band,
            "flags": (near_flag, single_flag, min_orders)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--orders", required=True)
    ap.add_argument("--threshold", required=True, help="Free-shipping threshold, or 'none'")
    args = ap.parse_args()
    free_ship = None if args.threshold.lower() == "none" else float(args.threshold)
    r = analyse(load_orders(args.orders), load_thresholds(), free_ship)
    near_flag, single_flag, min_orders = r["flags"]
    rows = [["Orders", r["n"], f">= {min_orders:g}", ""], ["AOV", f"{r['aov']:,.2f}", "", ""]]
    if r["near"] is not None:
        lo = free_ship * (1 - r["band"])
        rows.append([f"Near misses ({lo:,.2f} to under {free_ship:,.2f})", f"{len(r['near'])} ({pct(r['near_share'])})",
                     f"> {pct(near_flag)}", "threshold_gap" if r["near_share"] > near_flag else "ok"])
    rows.append(["Single-unit orders", pct(r["single_share"]), f"> {pct(single_flag)}",
                 "bundle_gap" if r["single_share"] > single_flag else "ok"])
    print(table(["Measure", "Value", "Flag", "Result"], rows))
    print("Verdict: " + ", ".join(r["verdicts"]))
    print("Most often bought alone: " + "; ".join(f"{name} ({count})" for name, count in r["alone"]))


if __name__ == "__main__":
    main()
