---
name: product-page-conversion-leak
description: Finds product pages that get plenty of views but turn far fewer of them into add-to-carts than the store's typical product, and ranks them by revenue at stake. Use before sending more ad traffic to a product, when a hero product underperforms, or in a CRO review. Boundary: stockout-ad-spend-leak checks stock; checkout-drop-leak checks the steps after the cart.
---

# Product Page Conversion Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.

## Use this skill when

- Before scaling ads to a product page.
- A product gets traffic but not sales.
- Choosing which product pages to improve first.

## Required input

- **Shopify Analytics product report** for the period: product title, product
  views (or sessions with product views), add-to-carts. Purchases if available.
- Average price per product (Products export or Sales by product).
- The stock-out findings for the same period, if run (AGENTS.md rule 3).

## Live data (MarketAtoms MCP)

Not yet available as a live tool. Use the Shopify Analytics report.

## Analysis workflow

1. Keep products with at least `pdp.min_views` views.
2. Add-to-cart rate per product = add-to-carts / views. Find the store median
   across these products.
3. Ratio = product rate / median. Flag products below `pdp.atc_ratio_floor`.
4. Remove or caveat products flagged by stockout-ad-spend-leak in the same
   period (missing variants lower add-to-cart without any page problem).
5. Revenue at stake per flagged product = views x (median rate x floor ratio -
   product rate) x the store's cart-to-purchase rate x average price. Use the
   floor, not the median, as the target, to stay conservative.
6. For the top 3 by revenue at stake, list what to check on the page: price and
   offer clear above the fold, real photos, reviews visible, shipping and
   returns info, the ad's promise visible on the page.

## Decision rules

- Ratio below `pdp.atc_ratio_floor`, enough views, no stock-out: `leak`.
- Same, but stock-out or missing variants: `stock_first`.
- Fewer than `pdp.min_views`: no verdict.
- Price far above the store's other products: report with the note
  "expensive items normally convert lower; compare with similar-priced products".

## Output format

Summary line: products checked, products leaking, revenue at stake per month
(range).

| Product | Views | Add-to-carts | ATC rate | vs median | Revenue at stake | Verdict |
|---|---|---|---|---|---|---|

Then: **Top 3 pages to fix** with the checks above, **What could not be seen**.

## Practical example

Last 30 days, 18 products with 300+ views. Median add-to-cart rate: 9.0%.

"Organic Cotton Romper": 4,200 views, 126 add-to-carts: 3.0%, a ratio of 0.33,
below the 0.5 floor. Not out of stock. Verdict `leak`. At the floor (4.5%) it
would get 189 add-to-carts, 63 more. With 55% of carts becoming orders and a
$28 average price: about $970 a month at stake. Page check: the size chart is
hidden below reviews and shipping time isn't shown.

## Guardrails

- Never edit a product page yourself; list what to test.
- Use the floor as the target, not the best product.
- Expensive items and new launches convert differently; say so.
