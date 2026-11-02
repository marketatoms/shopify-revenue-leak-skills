---
name: refund-and-return-leak
description: Shows how much revenue comes back as refunds, which products drive it, and how much reported revenue or ROAS is overstated because platforms never subtract refunds. Use before calling a campaign or product profitable, at month end, or when returns feel high. Boundary: discount-leak covers money given away at checkout; this skill covers money returned after the sale.
---

# Refund and Return Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.

## Use this skill when

- Before reporting a month's revenue or a campaign's ROAS as final.
- Returns or "not as described" complaints are rising.
- A product sells well in ads but the team suspects it comes back a lot.

## Required input

- **Orders export** for the period, including `Refunded Amount`, `Lineitem name`
  and `Lineitem price`. Use a period that ended at least 2-3 weeks ago, so late
  refunds have arrived.

## Live data (MarketAtoms MCP)

If connected: `store_snapshot` gives the store-wide refunded total for the
period. Per-product refund rates still need the Orders export.

## Analysis workflow

1. Store-wide: refund rate = total `Refunded Amount` / total revenue. Compare
   with `refund.store_rate_flag`.
2. Per product: for orders that contain the product, sum refunded value and
   revenue. When an order has several products and the export doesn't say which
   was refunded, split the refund by line-item value and mark it `estimated`.
3. Flag products with at least `refund.min_product_orders` orders and a refund
   rate above `refund.product_rate_flag`.
4. Show the effect on ad numbers: platform-reported purchase value includes
   orders later refunded, so ROAS is overstated by roughly the refund rate.
5. If the export has notes or tags with return reasons, group them (size, damaged,
   not as described, changed mind).

## Decision rules

- Store refund rate above `refund.store_rate_flag`: `material`. All profit
  figures must use net revenue (AGENTS.md rule 4).
- Product with enough orders and refund rate above `refund.product_rate_flag`:
  `problem_product`. Name the most common reason if known.
- Product below `refund.min_product_orders`: no verdict.
- Period too recent for refunds to have arrived: `provisional`, say how many
  days old it is.

## Output format

Summary line: gross revenue, refunded, net revenue, refund rate.

| Product | Orders | Revenue | Refunded | Refund rate | Main reason | Verdict |
|---|---|---|---|---|---|---|

Then: **Effect on ROAS**, **What could not be split** (multi-product orders),
**Suggested fixes** (size guide, product photos, description: for approval).

## Practical example

September: revenue $86,400, refunded $8,120: a 9.4% refund rate, above the
8% store flag: `material`. Every September profit figure uses $78,280.

"Bamboo Sleep Set" (64 orders): $4,480 revenue, $790 refunded: 17.6%,
`problem_product`. Order notes mention "runs small" 11 times. Suggested fix:
add a size guide and a "runs small" note on the product page.

Meta reported a 3.1 ROAS for September; after refunds the real figure is about
2.8.

## Guardrails

- Never report the adjusted figure as if it were the platform's own number;
  show both, side by side.
- Mark split refunds as `estimated`.
- Never issue, refuse or change a refund; this skill only measures.
