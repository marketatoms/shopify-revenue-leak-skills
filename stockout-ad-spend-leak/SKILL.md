---
name: stockout-ad-spend-leak
description: Finds products that are receiving ad spend while they are out of stock or about to run out, and the money those ads are burning. Use before a sale or a budget increase, when a best seller is selling fast, or in a weekly review. Boundary: this skill checks stock behind ads; wasted-ad-spend-leak checks ads with no purchases.
---

# Stock-out Ad Spend Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.

## Use this skill when

- A best seller is selling faster than usual, or a sale is coming.
- Ads are running on specific products (Shopping, catalog ads, product-led
  creatives).
- As part of the weekly readout.

## Required input

- **Inventory export:** SKU and available quantity (sum the locations that
  fulfil online orders).
- **Units sold per product or SKU, last 28 days:** Shopify "Sales by product"
  or the Orders export.
- **Ads by product:** Meta catalog / product set spend, Google Shopping
  product report, or ad sets with their destination URL. If ads can't be tied
  to products, the skill still lists low-stock best sellers and says it could
  not link spend.

## Live data (MarketAtoms MCP)

Not yet available as a live tool. Use the exports.

## Analysis workflow

1. For each product: days of cover = available units / (units sold in last 28
   days / 28).
2. Flag products below `stock.days_of_cover_floor`, and products at 0.
3. Match flagged products to ad spend in the period (by product ID, SKU, or
   landing URL handle).
4. For each match, report spend in the period and the spend per day still
   going to it.
5. Check variants: a product can be "in stock" while its best-selling size or
   colour is sold out. If variant-level data is given, flag variant stock-outs
   on the top sellers.

## Decision rules

- Available = 0 and ad spend in the last 7 days: `burning`. Highest priority.
- Days of cover below `stock.days_of_cover_floor` with active ad spend:
  `running_out`. Reorder or shift spend before it hits zero.
- Best-selling variant sold out while the product is in stock and advertised:
  `variant_gap`.
- Low stock but no ad spend found: `low_stock_no_ads`, list for the
  merchandising team, no ad action.
- Ads can't be linked to products: `needs_data` for the spend part.

## Output format

Summary line: products burning spend, money spent on them, products running out.

| Product | Available | Sold / day | Days of cover | Ad spend (period) | Spend / day now | Verdict |
|---|---|---|---|---|---|---|

Then: **Do now** (pause or redirect, for human approval), **Reorder list**,
**What could not be linked**.

## Practical example

Last 28 days. "Overnight Diaper Pants, Size L": 36 units available, selling
9 a day: 4 days of cover, below the 7-day floor. Meta catalog ads spent $640 on
it in the last 7 days ($91 a day). Verdict `running_out`: either reorder now or
move that $91 a day to a product with stock before it sells out on Friday.

"Swim Diapers, 3-pack" shows 0 available and $118 of Google Shopping spend in
the last 7 days: `burning`.

## Guardrails

- Never pause ads yourself; list the spend to redirect and wait for approval.
- Say which locations were counted as available stock.
- Pre-order and made-to-order products are not stock-outs; ask if unsure.
