---
name: discount-leak
description: Measures how much revenue discount codes give away, which codes drive it, and which codes look leaked to coupon sites after a sudden spike. Use when margin feels thin despite good sales, after a promotion, or when a private code starts showing up everywhere. Boundary: refund-and-return-leak covers money returned after the sale; this skill covers money given away at checkout.
---

# Discount Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.
Arithmetic: `../scripts/discount_leak.py`.

## Use this skill when

- Sales are fine but margin is thin.
- After a promotion, to see what it really cost.
- An influencer or welcome code suddenly gets used a lot more.

## Required input

- **Orders export** for at least 5 weeks (the spike check needs 4 weeks of
  history plus the current week).
- Optional: which codes are meant to be private (influencer, staff, VIP).

## Live data (MarketAtoms MCP)

If connected: `store_snapshot` gives total discounts and the share of orders
with a discount for the period. Per-code detail still needs the Orders export.

## Analysis workflow

1. Run `../scripts/discount_leak.py` on the Orders export. It returns: share
   of orders with a code, discount depth on discounted orders, and per code:
   orders, revenue, discount given, and the latest week's uses against its
   previous 4-week weekly average.
2. Compare the store-wide share against `discount.order_share_flag` and depth
   against `discount.depth_flag`.
3. For each code with at least `discount.min_code_orders` orders, flag a
   latest-week spike at or above `discount.spike_multiple`.
4. For each spiking code, check whether it is meant to be private. A private
   code spiking is the clearest sign of a leak to coupon sites.
5. Size the leak: discount given on orders above the code's normal weekly
   level.

## Decision rules

- Store-wide discounted share above `discount.order_share_flag`:
  `discount_habit`. Customers have learned to wait for a code.
- Depth above `discount.depth_flag`: `too_deep`.
- Private code with a spike at or above `discount.spike_multiple`: `leaked`.
  Suggest a usage limit or replacing it with a unique-code version.
- Public code with a spike: `promo_effect`, normal after a campaign; report
  the cost.
- Code below `discount.min_code_orders`: grouped as "small codes", no verdict.
- Fewer than 5 weeks of orders: spike check `needs_data`; share and depth can
  still run.

## Output format

Summary line: discount given away in the period, share of orders discounted,
average depth.

| Code | Orders | Revenue | Discount given | Depth | Latest week vs 4-week avg | Verdict |
|---|---|---|---|---|---|---|

Then: **Leaked codes**, **What it cost**, **Suggested fixes** (for approval).

## Practical example

October, 1,240 orders. 47% used a code (above the 40% flag):
`discount_habit`. Depth on discounted orders: 16% (below the 20% flag).

Code `SARAH15` (influencer, meant to be private): 4-week average 12 uses a
week, last week 61 uses: 5.1x, above the 3x spike rule. Verdict `leaked`.
The 49 extra uses gave away about $430. Suggested fix: cap `SARAH15` and give
the influencer unique codes.

## Guardrails

- Never disable or edit a code yourself; suggest it for approval.
- Discounts are already inside Shopify's `Total`; report them, never subtract
  them twice (AGENTS.md rule 5).
- Automatic discounts don't appear in `Discount Code`; say so if the store uses
  them.
