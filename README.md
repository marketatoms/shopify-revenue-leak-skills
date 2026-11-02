# Shopify Revenue Leak Skills for Claude

**12 free Claude Skills that find where a Shopify store is losing money** - in
the ads, at checkout, in the basket, in discounts and refunds, and after the
first order - and say how much is at stake.

Built by [MarketAtoms](https://www.marketatoms.com), from the checks we run on
client stores. *Find the leak. Fix the system. Scale what works.*

- **Read-only.** No skill logs into your store or ad accounts, and none of them
  edits a product, price, discount or campaign. Every finding is a decision for
  you.
- **Honest.** When the data can't support an answer, a skill says `needs_data`
  instead of guessing. Every number it uses is written down in one file.
- **Whole store, not just ads.** Most AI packs stop at ROAS. These follow the
  money from the ad click to the second order.

## The 12 skills

### 1. Can the numbers be trusted?

| # | Skill | The question it answers |
|---|---|---|
| 1 | [`tracking-gap-leak`](tracking-gap-leak/SKILL.md) | Do Meta and Google report the same sales Shopify recorded, or is one blind (or bragging)? |

### 2. Money leaving the store

| # | Skill | The question it answers |
|---|---|---|
| 2 | [`wasted-ad-spend-leak`](wasted-ad-spend-leak/SKILL.md) | Which ad sets and search terms spent money and sold nothing? |
| 3 | [`stockout-ad-spend-leak`](stockout-ad-spend-leak/SKILL.md) | Which ads are sending people to products that are sold out, or about to be? |
| 4 | [`discount-leak`](discount-leak/SKILL.md) | How much do codes give away, and has a private code leaked to coupon sites? |
| 5 | [`refund-and-return-leak`](refund-and-return-leak/SKILL.md) | How much revenue comes back, from which products, and how much does it inflate ROAS? |

### 3. Money not won

| # | Skill | The question it answers |
|---|---|---|
| 6 | [`checkout-drop-leak`](checkout-drop-leak/SKILL.md) | Which step between cart and payment started losing people? |
| 7 | [`mobile-conversion-gap-leak`](mobile-conversion-gap-leak/SKILL.md) | How many orders are lost because the store converts badly on phones? |
| 8 | [`product-page-conversion-leak`](product-page-conversion-leak/SKILL.md) | Which product pages get views but no add-to-carts? |
| 9 | [`basket-value-gap-leak`](basket-value-gap-leak/SKILL.md) | How many orders stop just short of free shipping, and how many are single items? |
| 10 | [`second-order-gap-leak`](second-order-gap-leak/SKILL.md) | How many first-time buyers come back, and which first products lead nowhere? |

### 4. Profit and the weekly decision

| # | Skill | The question it answers |
|---|---|---|
| 11 | [`contribution-margin-leak`](contribution-margin-leak/SKILL.md) | After product cost, shipping, fees, refunds and ads, what is actually left? |
| 12 | [`weekly-revenue-leak-readout`](weekly-revenue-leak-readout/SKILL.md) | Of everything found this week, what are the 3 things to do first? |

## Where to start

1. Run **`tracking-gap-leak`** first. If the ad platforms' numbers are wrong,
   every ad decision built on them is wrong too.
2. Then the checks for your biggest worry: wasted spend, checkout, discounts,
   retention.
3. Every Monday, finish with **`weekly-revenue-leak-readout`**.

How the skills depend on each other is written in [`AGENTS.md`](AGENTS.md).

## How to use them (pick one)

### A. Copy and paste - no setup, works anywhere

Open any skill's `SKILL.md`, copy all of it into a new Claude chat (ChatGPT
works too), then attach the export it asks for. That's it. Claude will tell
you if something is missing.

The skills point to `references/thresholds.md` for their numbers. If you only
paste one skill, paste [`references/thresholds.md`](references/thresholds.md)
in as well.

### B. Add a skill to the Claude app

1. Download the skill's ZIP from the **Releases** page of this repository (or
   build them yourself: `python3 scripts/build_zips.py` creates `dist/`).
   Each ZIP already contains the thresholds file and any script it needs.
2. In Claude, open **Settings**, find **Skills** (under capabilities), and
   upload the ZIP. Skills availability depends on your Claude plan and on
   whether your workspace admin has enabled them.
3. Start a new chat and ask, for example: *"Check my discount codes for
   leaks"* and attach your Orders export.

### C. Claude Code - the full pack

```bash
git clone https://github.com/marketatoms/shopify-revenue-leak-skills.git
mkdir -p ~/.claude/skills
cp -r shopify-revenue-leak-skills/*-leak \
      shopify-revenue-leak-skills/weekly-revenue-leak-readout \
      shopify-revenue-leak-skills/references \
      shopify-revenue-leak-skills/scripts \
      shopify-revenue-leak-skills/AGENTS.md \
      ~/.claude/skills/
```

Each skill folder must sit directly inside `~/.claude/skills/`, with
`references/` and `scripts/` next to them: the skills find their numbers and
arithmetic there. If `~/.claude/skills/` already has a `references/` or
`scripts/` folder from another pack, install into a project instead
(`.claude/skills/` inside that project). Start a new Claude Code session;
skills switch on when your question matches their description.

## Live data with the MarketAtoms MCP

Every skill works from exports. If you connect the **MarketAtoms MCP** to
Claude, skills that have a live tool (store totals, Meta campaigns, Meta wasted
spend) read your Shopify and Meta data directly instead, so the same checks can
run every morning without downloading anything.

The connector is in a private pilot with a small number of stores. To join,
email **support@marketatoms.com** with the subject "Engine pilot", or book a
free Revenue Leak Audit at [marketatoms.com](https://www.marketatoms.com).

## How the numbers work

Every threshold lives once in [`references/thresholds.md`](references/thresholds.md).
Skills cite it by key (for example `discount.order_share_flag`), so a number
can't drift between skills. Each one is tagged:

- `[platform]` - stated by Shopify, Google or Meta.
- `[heuristic]` - a starting point from our client work. Recalibrate it to your
  store, and say which one you moved and why.

Almost all of them are heuristics, and they say so.

Counting is done by small Python scripts (standard library only, no installs),
not by the AI reading a spreadsheet by eye:

| Script | Used by |
|---|---|
| `scripts/tracking_gap.py` | tracking-gap-leak |
| `scripts/discount_leak.py` | discount-leak |
| `scripts/basket_value.py` | basket-value-gap-leak |
| `scripts/repeat_rate.py` | second-order-gap-leak |

See them run on a made-up sample store in
[`examples/worked-example.md`](examples/worked-example.md).

## Checking the pack yourself

```bash
python3 scripts/validate_skills.py   # every skill has its sections; every key and path exists
python3 scripts/selftest.py          # the scripts' maths agrees with an independent recount
```

`selftest.py` recounts orders, discounts, near-misses and repeat customers
straight from the CSV without the shared helper, checks edge cases (an order of
exactly $50.00 is not a "near miss" under a $50 threshold), and checks that bad
input is refused with a message. Both were tested by deliberately breaking a
copy of the code and confirming they fail.

What they can't check: whether the advice in a skill is right for your store.
That's your call, and why every threshold is written down.

## What these skills won't do

- Log into Shopify, Meta, Google or anything else.
- Change a product, price, discount, theme, campaign or budget.
- Invent a number to make a report look complete.
- Call something a leak on too little data.

## Licence

MIT. Use them, change them, build them into your own process. A link back is
appreciated.
