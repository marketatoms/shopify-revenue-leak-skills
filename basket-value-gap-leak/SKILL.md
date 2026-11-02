---
name: basket-value-gap-leak
description: Finds basket value left on the table - orders just under the free-shipping threshold and a high share of single-item orders - and estimates the revenue a better threshold, bundle or cart upsell could add. Use when average order value is flat, before changing shipping rules, or when planning bundles. Boundary: discount-leak covers money given away with codes; this skill covers money not added to the cart.
---

# Basket Value Gap Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.
Arithmetic: `../scripts/basket_value.py`.

## Use this skill when

- Average order value (AOV) has been flat for months.
- Before changing the free-shipping threshold or shipping prices.
- Planning bundles, "frequently bought together" or a cart upsell.

## Required input

- **Orders export** for the period (at least `aov.min_orders` orders).
- **Free-shipping threshold** in the store currency (or "none").

## Live data (MarketAtoms MCP)

If connected: `store_snapshot` gives orders, revenue and AOV for the period.
The near-miss and single-item checks still need the Orders export.

## Analysis workflow

1. Run `../scripts/basket_value.py` with the Orders export and the threshold.
   It returns AOV, the share of orders whose subtotal sits within
   `aov.near_threshold_band` below the threshold ("near misses"), and the share
   of single-unit orders.
2. Compare near misses with `aov.near_threshold_share_flag` and single-unit
   orders with `aov.single_item_share_flag`.
3. For near misses, estimate the upside: if a quarter of near-miss customers
   added one low-priced item to reach free shipping, revenue added = near-miss
   orders x 25% x the store's cheapest common add-on price. Say the 25% is an
   assumption.
4. For single-item orders, list the top 5 products bought alone. They are the
   best candidates for a bundle or a "pairs well with" block.
5. If no threshold exists, report AOV distribution only and suggest testing one
   at about the 60th percentile of order subtotals.

## Decision rules

- Near misses above `aov.near_threshold_share_flag`: `threshold_gap`. A cart
  message ("You're $6 away from free shipping") or a small add-on is the fix to
  test.
- Single-unit orders above `aov.single_item_share_flag`: `bundle_gap`.
- Both below their flags: `healthy`.
- Fewer than `aov.min_orders` orders: `needs_data`.

## Output format

Summary line: AOV, near-miss share, single-item share, estimated monthly upside
(range).

| Measure | Value | Flag | Verdict |
|---|---|---|---|

Then: **Products most often bought alone**, **Tests to run** (for approval),
**Assumptions used**.

## Practical example

October, 1,240 orders, AOV $41.20, free shipping from $50. Near misses
($42.50-$49.99): 298 orders, 24% of all orders, above the 20% flag:
`threshold_gap`. Single-unit orders: 74%, above the 70% flag: `bundle_gap`.

If a quarter of near-miss customers added the $9 wipes pack: about 75 orders x
$9 = $670 more a month, plus shipping cost saved on their side. Top product
bought alone: "Overnight Diaper Pants": bundle it with wipes.

## Guardrails

- Never change shipping rules or prices yourself; suggest tests.
- Label every assumption (like "25% would add an item").
- Use subtotal (before shipping) for the threshold check, not Total.
