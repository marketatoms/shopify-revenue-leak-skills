# Worked example: the sample store

Everything below was produced by running the scripts on `sample-orders-export.csv`: a **made-up** baby-products store, 1,533 orders from April to October 2026 (17 cancelled). Use it to check your install gives the same numbers.

## 1. Tracking gap (`tracking-gap-leak`)

Platform figures typed in for October 1-28: Meta reported 70 purchases where Shopify attributed 92 orders to Meta; Google 45 vs 42; TikTok 9 vs 12.

```bash
python3 scripts/tracking_gap.py --orders examples/sample-orders-export.csv --from 2026-10-01 --to 2026-10-28 --channel Meta 70 92 --channel Google 45 42 --channel TikTok 9 12
```

Shopify orders in range: 199, revenue 8,973.90
Rule: |gap| > 15.0% -> reconcile; fewer than 30 Shopify orders -> needs_data
| Platform | Platform purchases | Shopify-attributed | Gap | Direction | Orders apart | Verdict |
|---|---|---|---|---|---|---|
| Meta | 70 | 92 | -23.9% | under-tracking | 22 | reconcile |
| Google | 45 | 42 | 7.1% | over-claiming | 3 | trusted |
| TikTok | 9 | 12 | - | too few Shopify orders | - | needs_data |

**Reading it:** Meta misses about 22 orders (under-tracking), so every Meta cost-per-purchase this month is provisional (AGENTS.md rule 1). Google is fine. TikTok has too few orders to judge, and the script says so instead of guessing.

## 2. Discount leak (`discount-leak`)

```bash
python3 scripts/discount_leak.py --orders examples/sample-orders-export.csv --private SARAH15
```

Orders: 1516, with a discount: 578 (38.1%, flag 40.0%) -> ok
Discount given: 3,102.65; depth on discounted orders: 11.2% (flag 20.0%) -> ok
Spike rule: latest 7 days >= 3x the weekly average of the 4 weeks before; codes with < 20 orders not judged
| Code | Orders | Revenue | Discount given | Depth | Latest week vs avg | Verdict |
|---|---|---|---|---|---|---|
| WELCOME10 | 439 | 18,837.95 | 1,875.60 | 9.1% | 10 vs 14.5/wk (0.7x) | normal |
| BFCM20 | 108 | 4,649.35 | 1,047.80 | 18.4% | 6 vs 5.2/wk (1.1x) | normal |
| SARAH15 | 31 | 1,182.35 | 179.25 | 13.2% | 4 vs 1.0/wk (4.0x) | leaked |
LEAKED SARAH15: about 3 extra uses last week, about 17.35 given away above normal

**Reading it:** discount share and depth are under their flags. The private influencer code `SARAH15` jumped to 4x its normal weekly use: flagged `leaked`. Small in money here, but this is the pattern to catch early.

## 3. Basket value (`basket-value-gap-leak`), free shipping from $50

```bash
python3 scripts/basket_value.py --orders examples/sample-orders-export.csv --threshold 50
```

| Measure | Value | Flag | Result |
|---|---|---|---|
| Orders | 1516 | >= 100 |  |
| AOV | 45.19 |  |  |
| Near misses (42.50 to under 50.00) | 46 (3.0%) | > 20.0% | ok |
| Single-unit orders | 62.9% | > 70.0% | ok |
Verdict: healthy
Most often bought alone: Overnight Diaper Pants - Size L (307); Overnight Diaper Pants - Size M (240); Organic Cotton Romper (130); Bamboo Sleep Set (91); Gift Box Set (65)

**Reading it:** few near misses and single-unit orders under 70%: `healthy`. A finding of "no leak" is a valid result.

## 4. Second-order gap (`second-order-gap-leak`)

```bash
python3 scripts/repeat_rate.py --orders examples/sample-orders-export.csv
```

Window: 90 days (as of 2026-10-31). First-time customers judged: 774
Came back: 158 -> second-order rate 20.4% (floor 20.0%) -> healthy
Median days to second order: 49

By first product
| First product | Customers | Came back | Rate | vs store | Verdict |
|---|---|---|---|---|---|
| Overnight Diaper Pants - Size L | 230 | 65 | 28.3% | 1.38x | normal |
| Overnight Diaper Pants - Size M | 178 | 53 | 29.8% | 1.46x | normal |
| Organic Cotton Romper | 106 | 14 | 13.2% | 0.65x | normal |
| Bamboo Sleep Set | 89 | 6 | 6.7% | 0.33x | dead_end_product |
| Gift Box Set | 65 | 5 | 7.7% | 0.38x | dead_end_product |
| Baby Wipes 6-pack | 54 | 10 | 18.5% | 0.91x | normal |
| Swim Diapers 3-pack | 52 | 5 | 9.6% | 0.47x | dead_end_product |

By first-order month
| Month | Customers | Came back | Rate |
|---|---|---|---|
| 2026-04 | 182 | 36 | 19.8% |
| 2026-05 | 199 | 41 | 20.6% |
| 2026-06 | 191 | 41 | 21.5% |
| 2026-07 | 192 | 39 | 20.3% |
| 2026-08 | 10 | 1 | 10.0% |

**Reading it:** the store as a whole is just above the 20% floor, but three first products are dead ends: Bamboo Sleep Set, Gift Box Set and Swim Diapers. Customers who start with diaper pants come back about 30% of the time. Push diaper pants as the entry product in ads; give gift buyers a different follow-up.

The August cohort shows only 10 customers because most August buyers have not yet had their full 90 days; the script leaves them out rather than judging them early.
