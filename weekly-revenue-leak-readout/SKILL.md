---
name: weekly-revenue-leak-readout
description: Combines the results of the other revenue-leak skills run this week into one short, plain-language readout - the money at stake, ranked, and at most three actions. Use every Monday, for a founder update or a client report, or after running several leak checks. Boundary: it combines other skills' outputs and never re-analyses raw exports.
---

# Weekly Revenue Leak Readout

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). How the skills fit together: `../AGENTS.md`.

## Use this skill when

- Monday review, founder update or client report.
- After running two or more leak skills, to decide what to do first.

## Required input

- The outputs of whichever leak skills ran this week (pasted, or from earlier
  in the conversation).
- Optional: last week's readout, to show what changed.

## Live data (MarketAtoms MCP)

If connected, `store_snapshot` adds the week's headline numbers (orders,
revenue, AOV against the week before). Findings still come from the skills.

## Analysis workflow

1. List which skills ran and which didn't. For each skill that didn't run, say
   what this readout therefore cannot state.
2. Apply the blocking rules in AGENTS.md first: tracking caveats, learning
   windows, stock before page, refunds before profit, one finding where two
   overlap.
3. Put every finding into one ranked list by money at stake per month. Keep the
   ranges and confidence each skill gave; never upgrade them.
4. Pick at most `readout.max_actions` actions. Prefer: biggest money at stake,
   quickest to fix, least risky. A `burning` stock-out or a `critical` margin
   always goes first.
5. For each action: what to do, who does it, how we'll know it worked (the
   number to check next week).
6. Write for a founder: no jargon without a one-line explanation.

## Decision rules

- Any `critical` or `burning` finding: action 1, whatever its size.
- Findings with `needs_data`: listed under "What we couldn't check", with the
  export that would fix it.
- Never more than `readout.max_actions` actions; the rest go under "Next week".
- If nothing material was found: say "No significant leak this week" and give
  the one number to watch.

## Output format

```
Week of [date] - Revenue Leak Readout

Headline: [orders, revenue, AOV vs last week]
Money at stake this month: [range], across [N] leaks

Do this week:
1. [Action] - [who] - [$ at stake] - check next week: [number]
2. ...
3. ...

Next week: [other findings, one line each]
What we couldn't check: [skills not run / data missing]
Trust note: [any tracking caveats]
```

## Practical example

Week of Nov 2. Ran: tracking gap, wasted ad spend, stock-out, discount,
second-order gap.

1. Pause Meta catalog ads on "Swim Diapers 3-pack" (0 in stock, $17 a day
   burning) - media buyer - check next week: spend on out-of-stock products = $0.
2. Cap the leaked code SARAH15 and issue unique codes - founder - about $430 a
   week at stake - check: SARAH15 uses back near 12 a week.
3. Fix Meta's Conversions API (23% of purchases unseen) - developer - every Meta
   decision depends on it - check: gap under 15%.

Next week: a day-21 reminder for diaper buyers (second-order rate 14%).
Couldn't check: checkout funnel and product pages (no Analytics export given).

## Guardrails

- Never re-analyse raw data here; use the skills' outputs.
- Never upgrade a `needs_data` or low-confidence finding.
- Never more than `readout.max_actions` actions.
