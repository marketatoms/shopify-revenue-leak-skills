---
name: second-order-gap-leak
description: Measures how many first-time customers come back for a second order, which first products lead to repeat buyers and which lead nowhere, and the revenue a better second-order rate would add. Use when growth depends on ads, when CAC is rising, or when planning post-purchase emails or WhatsApp flows. Boundary: this is the retention check; all other skills look at the first sale.
---

# Second Order Gap Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.
Arithmetic: `../scripts/repeat_rate.py`.

## Use this skill when

- Growth depends almost entirely on new customers from ads.
- Cost per new customer is rising.
- Planning post-purchase email, SMS or WhatsApp flows.

## Required input

- **Orders export covering at least 6 months**, so each first-order cohort has
  had `repeat.window_days` to come back. A longer history gives better cohorts.
- The category, so the window can be adjusted (say if you change it).

## Live data (MarketAtoms MCP)

Not yet available as a live tool. Use the Orders export.

## Analysis workflow

1. Run `../scripts/repeat_rate.py` on the Orders export. Customers are
   identified by email. For each customer, the first order and whether a second
   order came within `repeat.window_days`.
2. Only cohorts whose window has fully passed count (a customer who bought 20
   days ago can't be judged on a 90-day window yet).
3. Read the store-wide second-order rate against
   `repeat.second_order_rate_floor`.
4. Read it by first-order month (is it getting better or worse?) and by first
   product. A first product with a rate below `repeat.product_gap_ratio` x the
   store rate is a dead end; one well above it is a "gateway" product worth
   pushing in ads.
5. Median days to second order: the right moment for the reminder message.
6. Upside: first-time customers per month x (floor rate - current rate) x the
   average second-order value. Only when the store is below the floor.

## Decision rules

- Store rate below `repeat.second_order_rate_floor`: `retention_leak`.
- First product below `repeat.product_gap_ratio` x store rate, at least
  `repeat.min_cohort_customers` customers: `dead_end_product`.
- First product well above the store rate (1.5x or more), enough customers:
  `gateway_product`. Report it as an opportunity, not a leak.
- Cohort smaller than `repeat.min_cohort_customers`: no verdict.
- History shorter than `repeat.window_days` plus one month: `needs_data`.

## Output format

Summary line: second-order rate, median days to second order, monthly upside.

| First product | First-time customers | Came back | Rate | vs store | Verdict |
|---|---|---|---|---|---|

Then: **Cohorts by month** (trend), **When to send the reminder** (median
days), **Flows to test** (for approval).

## Practical example

January-June first-time customers: 3,120. Within 90 days, 437 ordered again:
14.0%, below the 20% floor: `retention_leak`. Median time to second order:
26 days.

Customers whose first product was "Overnight Diaper Pants": 31% came back
(`gateway_product`). "Gift Box Set": 4% (below 0.5 x 14% = 7%):
`dead_end_product`. These are gift buyers, not users.

Upside: 520 first-time customers a month x (20% - 14%) x $38 average second
order = about $1,190 a month. Test: a day-21 reminder for diaper buyers, by
WhatsApp or email.

## Guardrails

- Never judge a cohort whose window hasn't finished.
- Email is the customer key; guest checkouts with different emails count as
  different people. Say so.
- Never send messages yourself; suggest flows for approval.
