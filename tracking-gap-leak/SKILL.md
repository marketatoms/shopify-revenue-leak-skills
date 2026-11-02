---
name: tracking-gap-leak
description: Compares the orders Shopify attributes to each paid channel with the purchases Meta and Google report for the same dates, and says which numbers can be trusted for budget decisions. Use when ROAS looks too good or too bad, when platforms claim more sales than the store recorded, or before any other ad check. Boundary: this skill only checks whether the numbers agree; wasted-ad-spend-leak judges spend.
---

# Tracking Gap Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.
Arithmetic: `../scripts/tracking_gap.py`.

## Use this skill when

- Meta or Google reports a ROAS the bank account doesn't seem to agree with.
- Meta + Google together claim more purchases than Shopify recorded in total.
- Before running any other ad-related skill in this pack (see AGENTS.md rule 1).

## Required input

- **Shopify orders for the period:** the Orders export, or Shopify Analytics
  "Sales attributed to marketing" with orders per channel.
- **Each platform's reported purchases** for the identical dates, with the
  attribution setting written down (for example Meta "7-day click, 1-day view").
- The store's time zone and each ad account's time zone.

Without a Shopify order count for the same dates there is nothing to compare
against: return `needs_data`.

## Live data (MarketAtoms MCP)

If connected: `store_snapshot` gives Shopify orders and revenue for the period
and `meta_summary` gives Meta purchases and value for a matching date preset.
Use the same window for both. Google still needs its export.

## Analysis workflow

1. Line up the dates and time zones. If they differ, say so; a one-day offset
   alone can create a 5-10% gap on a small store.
2. Run `../scripts/tracking_gap.py` with the Shopify Orders export and each
   platform's reported purchases. It returns Shopify total orders, orders per
   channel (if the attribution report was given) and the gap per platform.
3. Judge each platform separately against `tracking.gap_flag`. Platforms
   adding up to more than Shopify's total is normal (they both claim shared
   customers) and is **not** a finding by itself.
4. Name the direction:
   - **Platform reports fewer** purchases than Shopify attributes to it:
     under-tracking (pixel or Conversions API missing events). The platform
     looks worse than it is, and its algorithm is learning from too little.
   - **Platform reports more:** over-claiming (wide attribution windows,
     view-through, duplicate events). The platform looks better than it is.
5. Check the purchase **value** the same way when it is supplied. Counts can
   match while value differs (tax, shipping or currency settings).
6. State which number to use for the period's headline revenue: Shopify's.

## Decision rules

- Platform gap above `tracking.gap_flag` and channel has at least
  `tracking.min_orders` orders: `reconcile`. Name the platform, the direction,
  and the gap in orders.
- Gap within `tracking.gap_flag`: `trusted`. Usable for that platform's ROAS,
  alongside the Shopify total.
- Channel has fewer than `tracking.min_orders` orders: `needs_data`.
- No Shopify count for the same dates, or attribution setting unknown:
  `needs_data`, say exactly what is missing.

## Output format

One summary line: Shopify orders and revenue for the period, platforms that
need reconciling.

| Platform | Platform purchases | Shopify-attributed orders | Gap | Direction | Verdict |
|---|---|---|---|---|---|

Then: **Likely causes** (max 3, ranked), **What this could not see**,
**Next step** (one sentence).

## Practical example

Store, October 1-28. Shopify: 410 orders. Shopify attribution credits Meta
with 236 orders and Google with 98.

Meta reports 181 purchases: a 23.3% gap below Shopify's 236, above
`tracking.gap_flag`. Verdict `reconcile`, direction under-tracking: about 55
orders Meta never saw. Likely causes: Conversions API not connected through
the Facebook & Instagram app; a checkout extension firing the purchase event
late.

Google reports 104 conversions against 98: a 6.1% gap, within the flag.
Verdict `trusted`.

Headline revenue for the period: Shopify's figure.

## Guardrails

- Never call "platforms add up to more than Shopify" a finding on its own.
- Never recommend a budget change; this skill decides which numbers to trust.
- Never compare figures pulled on different attribution windows without
  saying so first.
- If `Source` is all you have, say it shows the sales channel, not the ad.
