# How this pack works as a system

Guidance for any AI agent (or person) running these skills. Twelve prompts
become a system only when the order and the blocking rules below are followed.

## The order: trust the numbers, then find the leak, then size it

```
1. Measurement      tracking-gap-leak
        |
        v
2. Money leaving    wasted-ad-spend-leak, stockout-ad-spend-leak,
                    discount-leak, refund-and-return-leak
        |
        v
3. Money not won    checkout-drop-leak, mobile-conversion-gap-leak,
                    product-page-conversion-leak, basket-value-gap-leak,
                    second-order-gap-leak
        |
        v
4. Profit           contribution-margin-leak
        |
        v
5. Decision         weekly-revenue-leak-readout  (combines 1-4, names max 3 actions)
```

**First audit of a store:** run top to bottom. Measurement first, because every
later number stands on it.

**Something already looks wrong:** start at the section that matches the
symptom, then work upwards to check the measurement under it.

## Blocking rules

Apply these without being asked.

1. **A tracking gap makes every ad-platform number provisional.** If
   `tracking-gap-leak` returns `reconcile` for a platform, any cost per
   purchase, ROAS or "wasted" verdict from that platform for the same period is
   reported with the caveat "platform purchases under-counted by about X%".
   Wasted-spend findings may still be listed, but never as "pause this".
2. **A zero-purchase ad set inside its learning window is not waste.** Ad sets
   younger than `ads.learning_days` are listed separately as "too new to judge".
3. **A stock-out outranks a conversion problem on the same product.** If
   `stockout-ad-spend-leak` flags a product, `product-page-conversion-leak`
   does not report that product's low add-to-cart rate as a page problem; the
   product may simply be unavailable in some variants.
4. **Refunds come off before anyone says "profitable".**
   `contribution-margin-leak` always starts from net revenue (after refunds).
   No skill reports a margin on gross revenue.
5. **Discounts are counted once.** Shopify's `Total` is already after
   discounts. `discount-leak` reports the discount given away; it is never
   subtracted a second time in `contribution-margin-leak`.
6. **A device gap and a checkout drop can be the same finding.** If
   `mobile-conversion-gap-leak` and `checkout-drop-leak` both flag, and the
   checkout drop is concentrated on mobile, report one finding (mobile
   checkout), not two.
7. **Small samples get `needs_data`, never a verdict.** Every check has a
   minimum volume key in `references/thresholds.md`. Below it, say what volume
   is missing.
8. **The readout combines; it does not re-analyse.** `weekly-revenue-leak-readout`
   uses the other skills' outputs. If a skill was not run, it says which one
   and what it therefore cannot state. It never upgrades a low-confidence
   finding to a fact.

## Where the arithmetic lives

Counting is done by small Python scripts (standard library only), not by the
AI reading a CSV by eye:

| Script | Used by | Does |
| --- | --- | --- |
| `scripts/repeat_rate.py` | second-order-gap-leak | First-order cohorts by month and by first product; second orders inside the window |
| `scripts/discount_leak.py` | discount-leak | Discount share, depth, per-code usage and weekly spikes |
| `scripts/tracking_gap.py` | tracking-gap-leak | Shopify orders vs each platform's reported purchases |
| `scripts/basket_value.py` | basket-value-gap-leak | Near-miss orders under the free-shipping threshold, single-item share |

Each script reads its thresholds from `references/thresholds.md` at run time,
so changing a number there changes the script. `scripts/selftest.py` checks the
scripts against the sample data in `examples/`.

If the AI client cannot run Python (for example a plain chat), the skill
explains the same calculation step by step and says the result was computed by
hand.

## Live data through the MarketAtoms MCP

If the MarketAtoms MCP is connected, prefer its tools to asking for exports:

| Tool | Replaces |
| --- | --- |
| `store_snapshot` | Orders export totals for a period (orders, revenue, AOV, discounts, refunds) |
| `meta_summary` | Meta Ads campaign export |
| `meta_wasted_spend` | Meta ad set export for the wasted-spend check |

Tools not yet available in the connector still need the export. Never mix a
live number and an exported number for different dates in one comparison.

## Hard limits, in one place

Nothing in this pack logs into Shopify or an ad account by itself, edits a
product, price, discount, theme or campaign, or moves budget. Every finding is
a decision put in front of a person.
