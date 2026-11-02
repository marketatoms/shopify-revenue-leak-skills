---
name: checkout-drop-leak
description: Finds the step between landing and purchase where the store is losing more visitors than before (cart, checkout or payment), and estimates the orders lost. Use when conversion rate fell, when traffic is up but orders aren't, or after a theme, app or checkout change. Boundary: mobile-conversion-gap-leak compares devices; this skill compares the funnel over time.
---

# Checkout Drop Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.

## Use this skill when

- Conversion rate dropped and nobody knows where.
- Traffic is up but orders are flat.
- After installing an app, changing theme, adding a checkout extension or a
  new payment method.

## Required input

- **Shopify Analytics conversion funnel** for the period and the previous
  period of equal length: sessions, sessions with cart additions, sessions
  reaching checkout, sessions converted. Both periods.
- Optional: the same report split by device, and dates of recent changes
  (new app, theme update, shipping price change).

## Live data (MarketAtoms MCP)

Not yet available as a live tool. Use the Shopify Analytics report.

## Analysis workflow

1. Check both periods have at least `funnel.min_sessions` sessions.
2. Compute three step rates per period:
   - add-to-cart rate = sessions with cart additions / sessions
   - checkout rate = sessions reaching checkout / sessions with cart additions
   - completion rate = sessions converted / sessions reaching checkout
3. Relative change per step = (current - previous) / previous. Flag steps that
   fell by `funnel.step_drop_flag` or more.
4. Estimate lost orders for a flagged step: sessions entering the step this
   period x (previous rate - current rate) x the later step rates.
5. Match the timing to known changes. A drop in the completion step that
   started on the day a new shipping rate or payment app went live is the
   first suspect.
6. If a device split is given and the drop is mostly on one device, hand over
   to mobile-conversion-gap-leak and report one finding (AGENTS.md rule 6).

## Decision rules

- A step fell by `funnel.step_drop_flag` or more, enough sessions: `leak`.
  Name the step and the estimated orders lost.
- All steps within the flag: `stable`. Say which step is weakest compared with
  the others, for information only.
- Fewer than `funnel.min_sessions` in either period: `needs_data`.
- Sessions jumped because of a new traffic source (for example a viral post):
  `mix_change`. Lower rates may come from colder traffic, not a broken step.

## Output format

Summary line: overall CVR now vs before, the step that broke, estimated orders lost.

| Step | Previous rate | Current rate | Relative change | Verdict |
|---|---|---|---|---|

Then: **Most likely cause** (with the evidence), **What to check first**
(a 5-minute test checkout on mobile and desktop), **What could not be seen**.

## Practical example

Previous 14 days: 21,000 sessions, 1,680 with cart additions (8.0%), 1,010
reached checkout (60.1%), 606 converted (60.0%).

Last 14 days: 22,400 sessions, 1,790 with cart additions (8.0%), 1,090 reached
checkout (60.9%), 490 converted (45.0%).

Completion rate fell from 60.0% to 45.0%: a 25% relative drop, above the 15%
flag. Verdict `leak` at the payment step. Estimated orders lost: 1,090 x
(0.600 - 0.450) = about 164 orders. The drop started on the day a new
"shipping protection" checkout app was installed: test checkout with and
without it.

## Guardrails

- Never uninstall an app or change a setting yourself; name the suspect and
  the test.
- Relative change, not percentage points: say which you mean.
- Don't blame a step for a traffic-mix change; check sources first.
