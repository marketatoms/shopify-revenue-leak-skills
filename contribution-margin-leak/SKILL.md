---
name: contribution-margin-leak
description: Works out what is really left after product cost, shipping, payment fees, refunds and ad spend, for the whole store and per channel or product, and flags where growth is buying revenue but losing profit. Use when ROAS looks fine but the bank account doesn't, before scaling a channel, or at month end. Boundary: other skills find individual leaks; this one adds up whether the store makes money.
---

# Contribution Margin Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.

## Use this skill when

- "ROAS is 3x but we have no cash."
- Before scaling a channel or a product with ads.
- Month-end profit check.

## Required input

- **Orders export** for the period (revenue, refunds, line items).
- **Cost of goods:** per product, or one average % of price.
- **Shipping cost** per order (what the store pays the carrier) or a monthly
  total.
- **Payment fee rate**; if missing, use `margin.payment_fee_default` and say so.
- **Ad spend** per platform for the same dates.
- Refund findings and tracking findings for the period, if run.

## Live data (MarketAtoms MCP)

If connected: `store_snapshot` gives revenue, discounts and refunds;
`meta_summary` gives Meta spend. Costs are always supplied by the user.

## Analysis workflow

1. Start from **net revenue** = revenue - refunds (AGENTS.md rule 4).
   Discounts are already inside revenue; don't subtract them again (rule 5).
2. Subtract cost of goods (on units not refunded), shipping cost, payment fees
   and ad spend.
3. Contribution margin % = contribution / net revenue. Compare with
   `margin.contribution_floor`.
4. Where per-channel data exists, repeat per channel using Shopify-attributed
   orders, not platform-reported ones. If a channel's tracking was
   `reconcile`, say the split is approximate.
5. Per product (if cost of goods per product is given): which products lose
   money once their ad spend is counted.
6. Show the break-even ROAS: the platform ROAS needed for contribution to be
   zero = 1 / (gross margin % after shipping, fees and refunds).

## Decision rules

- Contribution below 0: `critical`. Growth is losing money on every order.
- Below `margin.contribution_floor`: `thin`.
- At or above: `healthy`.
- Cost of goods missing: `needs_data`; no estimate from industry averages.
- Default payment fee used: still give a verdict, with the assumption stated.

## Output format

Summary line: net revenue, contribution, contribution %, verdict, break-even ROAS.

| Line | Amount | % of net revenue |
|---|---|---|
| Revenue (after discounts) | | |
| Refunds | | |
| Net revenue | | 100% |
| Cost of goods | | |
| Shipping | | |
| Payment fees | | |
| Ad spend | | |
| **Contribution** | | |

Then: **By channel / product** (where possible), **Break-even ROAS**,
**Assumptions used**.

## Practical example

October: revenue $51,080, refunds $3,050, net revenue $48,030. Cost of goods
$17,290 (36%), shipping $6,200, payment fees at the 3% default $1,532, ad spend
$19,400. Contribution: $3,608, 7.5% of net revenue, below the 10% floor:
`thin`.

Margin before ads = (48,030 - 17,290 - 6,200 - 1,532) / 48,030 = 47.9% of net
revenue, so the break-even blended ROAS is 1 / 0.479 = about 2.09 on net
revenue. Current blended ROAS on net revenue is 48,030 / 19,400 = 2.48. Meta reports 2.6 but tracking is under-counted by 23%, so
treat that channel's split as approximate. The store is profitable, but barely.

## Guardrails

- Never estimate cost of goods from "industry averages"; ask.
- Never report margin on gross revenue.
- State every default and assumption in the output.
