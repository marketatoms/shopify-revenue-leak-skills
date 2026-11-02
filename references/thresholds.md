# Thresholds

Every number this pack uses lives in this file, once. Skills cite a number by
its **key** (for example `discount.order_share_flag`) and never restate the
value. Change a number here and every skill and script follows.

Each entry has one tag:

- `[platform]` - stated by Shopify, Google or Meta in their own documentation
  or interface.
- `[heuristic]` - a practitioner starting point from MarketAtoms client work.
  Recalibrate it against the store's own history.

Almost everything here is `[heuristic]`, and that is the honest label.
Shopify, Google and Meta publish requirements, not benchmarks for a "healthy"
repeat rate or discount share.

## Rules for using a threshold

1. **One number, not a range.** Two people applying the same rule to the same
   store should land in the same place.
2. **Use the default unless you have a reason.** When you move a value for a
   store, say in the output which key you moved, to what, and why. An
   unexplained change reads as a fact.
3. **Respect the minimum sample.** Every check has a minimum volume key. Below
   it, the verdict is `needs_data`, never a guess.

## Words used in this file

| Term | Means | Does not mean |
| --- | --- | --- |
| **order** | One completed Shopify order, counted once however many line items it has. Test and cancelled orders excluded. | A checkout, a cart or a session |
| **customer** | One unique email address in the Orders export | A Shopify customer record with no orders |
| **period** | The date range under review, in the store's own time zone | A rolling window in another time zone |
| **previous period** | The same number of days immediately before the period | The same dates last year (unless the skill says so) |
| **revenue** | Order `Total` after discounts, before refunds, in the store currency | Gross sales before discounts |
| **net revenue** | Revenue minus `Refunded Amount` | |
| **CVR** | Orders divided by sessions for the same period and segment | Add-to-cart rate |

## Checkout and conversion

| Key | Value | Tag | Notes |
| --- | --- | --- | --- |
| `funnel.min_sessions` | **1000 sessions** | [heuristic] | Minimum sessions in each period before a funnel step change is judged. Below this, normal day-to-day noise is bigger than most real changes. |
| `funnel.step_drop_flag` | **15% relative drop** | [heuristic] | A funnel step rate (for example "reached checkout -> completed") that fell by this share or more against the previous period. 15% relative, not 15 percentage points. |
| `device.min_sessions` | **500 sessions** | [heuristic] | Minimum sessions per device type before mobile and desktop are compared. |
| `device.mobile_cvr_ratio_floor` | **0.5** | [heuristic] | Mobile CVR divided by desktop CVR. Below this, mobile converts at less than half of desktop: a leak worth fixing, because most paid social traffic is mobile. |
| `pdp.min_views` | **300 product views** | [heuristic] | Minimum views in the period before a product page's add-to-cart rate is judged. |
| `pdp.atc_ratio_floor` | **0.5** | [heuristic] | A product's add-to-cart rate divided by the store's median product add-to-cart rate. Below this, the page under-converts its own traffic. |

## Basket value

| Key | Value | Tag | Notes |
| --- | --- | --- | --- |
| `aov.near_threshold_band` | **15%** | [heuristic] | Orders whose subtotal sits within this share **below** the free-shipping threshold count as "near misses" (for a $50 threshold: $42.50 to $49.99). |
| `aov.near_threshold_share_flag` | **20% of orders** | [heuristic] | If this share of orders are near misses, the threshold or the cart upsell is costing basket value. |
| `aov.single_item_share_flag` | **70% of orders** | [heuristic] | Share of orders with exactly one unit. Above this, there is room for bundles or cross-sells. |
| `aov.min_orders` | **100 orders** | [heuristic] | Minimum orders in the period before basket checks are judged. |

## Retention

| Key | Value | Tag | Notes |
| --- | --- | --- | --- |
| `repeat.window_days` | **90 days** | [heuristic] | How long after a first order the pack looks for a second order. Use 60 for consumables bought monthly; 180 for slow categories such as furniture. Say which you used. |
| `repeat.second_order_rate_floor` | **20%** | [heuristic] | Share of first-time customers who place a second order within `repeat.window_days`. Below this, retention is a leak. Strongly category-dependent: recalibrate against the store's own best cohort. |
| `repeat.min_cohort_customers` | **50 customers** | [heuristic] | Minimum first-time customers in a cohort (month or first product) before its repeat rate is judged. |
| `repeat.product_gap_ratio` | **0.5** | [heuristic] | A first product whose second-order rate is below this share of the store average: customers who start there rarely come back. |

## Discounts and refunds

| Key | Value | Tag | Notes |
| --- | --- | --- | --- |
| `discount.order_share_flag` | **40% of orders** | [heuristic] | Share of orders using any discount code. Above this, full price has stopped being the normal price. |
| `discount.depth_flag` | **20%** | [heuristic] | Average discount amount divided by (revenue + discount amount) on discounted orders. |
| `discount.spike_multiple` | **3x** | [heuristic] | A code's weekly uses against its own average over the previous 4 weeks. A sudden spike on a code meant for a small group often means it leaked to a coupon site. |
| `discount.min_code_orders` | **20 orders** | [heuristic] | Minimum uses of a code in the period before it is judged on its own. |
| `refund.product_rate_flag` | **10% of a product's revenue** | [heuristic] | Refunded value divided by revenue, per product, for the period. |
| `refund.min_product_orders` | **20 orders** | [heuristic] | Minimum orders containing a product before its refund rate is judged. |
| `refund.store_rate_flag` | **8% of revenue** | [heuristic] | Store-wide refunded value divided by revenue. Above this, profit reported on gross revenue is overstated enough to change decisions. |

## Tracking and ads

| Key | Value | Tag | Notes |
| --- | --- | --- | --- |
| `tracking.gap_flag` | **15%** | [heuristic] | Gap between orders Shopify attributes to a channel and purchases that channel's ad platform reports, for the same dates, time zone and attribution basis. Above this, reconcile before trusting either number for budget decisions. |
| `tracking.min_orders` | **30 orders** | [heuristic] | Minimum Shopify orders attributed to a channel in the period before its gap is judged. |
| `ads.wasted_cpa_multiple` | **1.5x target CPA** | [heuristic] | An ad set, campaign or search term that has spent this multiple of the store's target cost per purchase with zero purchases. |
| `ads.wasted_min_spend` | **20 in store currency** | [heuristic] | Used only when no target CPA is given: minimum spend with zero purchases to flag. |
| `ads.learning_days` | **4 days** | [heuristic] | Ad sets launched more recently than this are excluded from wasted-spend verdicts; they have not had time to learn. |
| `stock.days_of_cover_floor` | **7 days** | [heuristic] | Units in stock divided by average daily units sold (last 28 days). Below this, a product receiving ad traffic is about to run out. |

## Profit

| Key | Value | Tag | Notes |
| --- | --- | --- | --- |
| `margin.contribution_floor` | **10% of net revenue** | [heuristic] | Contribution margin = net revenue - cost of goods - shipping cost - payment fees - discounts already in revenue - ad spend. Below this, growth is buying revenue, not profit. Negative = `critical`. |
| `margin.payment_fee_default` | **3% of revenue** | [heuristic] | Used only when the store does not supply its own payment fee rate. Say when the default was used. |

## Readout

| Key | Value | Tag | Notes |
| --- | --- | --- | --- |
| `readout.max_actions` | **3** | [heuristic] | The weekly readout names at most this many actions. More than three and none get done. |
