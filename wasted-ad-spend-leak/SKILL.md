---
name: wasted-ad-spend-leak
description: Finds Meta ad sets and Google search terms or campaigns that spent money with zero purchases, ranks them by money lost, and separates real waste from ad sets that are simply too new. Use when the user asks where ad money is being wasted, before raising budgets, or in a weekly ad review. Boundary: tracking-gap-leak decides whether purchase numbers can be trusted; this skill judges spend.
---

# Wasted Ad Spend Leak

Thresholds: `../references/thresholds.md` (or `references/thresholds.md` in a
single-skill download). Inputs: `../references/shopify-exports.md`.

## Use this skill when

- "Where am I wasting money on ads?"
- Before increasing a budget or launching new campaigns.
- As part of the weekly readout.

## Required input

- **Meta:** ad set export for the period with Ad set name, Campaign name,
  Amount spent, Purchases, and the ad set start date.
- **Google:** Search terms report (Search campaigns) or Campaigns report
  (Shopping / Performance Max) with Cost and Conversions.
- **Target cost per purchase** in the store currency. If the user has none,
  use `ads.wasted_min_spend` and say so.
- The tracking-gap verdict for the same period if it exists (AGENTS.md rule 1).

## Live data (MarketAtoms MCP)

If connected: call `meta_wasted_spend` with the user's target CPA (it applies
the same rule and lists the ad sets) and `meta_summary` for context. Google
still needs its export.

## Analysis workflow

1. Set the bar: `ads.wasted_cpa_multiple` x target CPA, or
   `ads.wasted_min_spend` when no target is given. State the bar.
2. List every ad set, campaign or search term with spend at or above the bar
   and **zero** purchases.
3. Move ad sets that started less than `ads.learning_days` ago into a separate
   "too new to judge" list.
4. Rank the rest by spend. Add up the total and its share of all spend.
5. For each flagged line, name the most likely reason from the data only:
   audience too narrow, search term off-intent, creative with clicks but no
   purchases (good CTR, no sales: check the landing page), or no clicks at all
   (creative problem).
6. If tracking-gap-leak returned `reconcile` for this platform, add the caveat
   that some "zero-purchase" ad sets may have sales the platform didn't see.

## Decision rules

- Spend >= bar, 0 purchases, older than `ads.learning_days`, tracking
  `trusted`: `waste`. Suggest "pause or fix", never pause by itself.
- Same, but tracking `reconcile` for that platform: `possible_waste`, check
  Shopify orders from that campaign's UTM before acting.
- Younger than `ads.learning_days`: `too_new`.
- Search term spending with 0 conversions and clearly off-intent (job seekers,
  free, DIY, a competitor's brand you don't sell): `waste`, suggest it as a
  negative keyword with match type.
- Nothing meets the bar: say so plainly. No finding is a good finding.

## Output format

Summary line: the bar used, total wasted, share of spend.

| Platform | Campaign | Ad set / term | Spend | Purchases | Started | Verdict | Likely reason |
|---|---|---|---|---|---|---|---|

Then: **Too new to judge**, **Suggested negatives** (Google), **Caveats**,
**Approval needed** (every pause is a human decision).

## Practical example

Target CPA $35, so the bar is $52.50. Last 14 days, Meta.

- "Static offer test B": $570 spent, 0 purchases, 540 clicks, started 20 days
  ago: `waste`. Clicks but no sales: check that the landing page matches the
  offer in the ad.
- "LAL 1% purchasers": $430.75, 0 purchases, started 30 days ago: `waste`.
- "LAL 3% purchasers": $12.40: below the bar, not flagged.
- "Holiday hook test": $95, 0 purchases, started 2 days ago: `too_new`.

Total waste $1,000.75, 21.6% of $4,641 total spend. Tracking gap for Meta was
`trusted` this period, so the verdicts stand.

## Guardrails

- Never pause, change or recommend a bid by yourself. List and explain.
- Never judge an ad set inside its learning window.
- Never call a prospecting ad set "waste" only on last-click purchases if the
  user says its job is to feed retargeting; report it with that note.
- Zero findings is a valid answer; don't stretch to find one.
