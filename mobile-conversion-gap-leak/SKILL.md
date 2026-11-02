---
name: mobile-conversion-gap-leak
description: Compares mobile and desktop conversion and estimates the orders lost because the store converts much worse on phones, where most paid social traffic lands. Use when most traffic is mobile, after a theme change, or when Meta ads get clicks but few sales. Boundary: checkout-drop-leak compares the funnel over time; this skill compares devices in the same period.
---

# Mobile Conversion Gap Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.

## Use this skill when

- Most traffic is mobile (usually 70-90% for stores running Meta ads).
- Ads get clicks but few sales.
- After a theme or app change.

## Required input

- **Shopify Analytics sessions by device type with conversion** for the period:
  device, sessions, sessions converted (and add-to-cart if available).
- Optional: the same split for the top 5 landing pages from ads.

## Live data (MarketAtoms MCP)

Not yet available as a live tool. Use the Shopify Analytics report.

## Analysis workflow

1. Check each device has at least `device.min_sessions` sessions.
2. CVR per device = sessions converted / sessions.
3. Ratio = mobile CVR / desktop CVR. Compare with
   `device.mobile_cvr_ratio_floor`.
4. If add-to-cart by device is given, find where the gap starts: before the
   cart (product page) or after it (checkout).
5. Estimate the opportunity, conservatively: orders if mobile reached the floor
   ratio = mobile sessions x desktop CVR x `device.mobile_cvr_ratio_floor`,
   minus actual mobile orders. Never use "mobile matches desktop" as the target;
   some gap is normal.
6. List the common mobile causes to check, in order: slow load, the add-to-cart
   button below the first screen, pop-ups covering the page, size or variant
   pickers that are hard to tap, a checkout without express wallets
   (Shop Pay, Apple Pay, Google Pay).

## Decision rules

- Ratio below `device.mobile_cvr_ratio_floor`, enough sessions: `leak`. Report
  the extra orders at the floor ratio.
- Ratio at or above the floor: `healthy`.
- Either device below `device.min_sessions`: `needs_data`.
- Gap mostly after the cart: tag `checkout_side`; mostly before: `page_side`.

## Output format

Summary line: mobile share of sessions, mobile vs desktop CVR, ratio, extra
orders at the floor.

| Device | Sessions | Orders | CVR | Add-to-cart rate |
|---|---|---|---|---|

Then: **Where the gap starts**, **Top 3 things to check on a phone**,
**Estimated monthly upside** (as a range).

## Practical example

Last 30 days: mobile 38,000 sessions, 380 orders (1.0% CVR). Desktop 7,000
sessions, 175 orders (2.5% CVR). Ratio 0.40, below the 0.5 floor: `leak`.

At the floor, mobile would convert at 1.25%: 475 orders, so about 95 more
orders a month at the current traffic. Add-to-cart is similar on both devices,
so the gap is `checkout_side`: check express wallets and a pop-up that covers
the checkout button on small screens.

## Guardrails

- Never promise "mobile = desktop"; use the floor ratio for the estimate.
- Give the upside as a range, never a single exact number.
- Tablet goes with mobile only if the user agrees; say what you did.
