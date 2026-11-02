# Changelog

## 1.0.0 - 2026-11-03

First public release: 12 Claude Skills that find revenue leaks in a Shopify
store.

### Added

- Measurement: `tracking-gap-leak`
- Money leaving: `wasted-ad-spend-leak`, `stockout-ad-spend-leak`,
  `discount-leak`, `refund-and-return-leak`
- Money not won: `checkout-drop-leak`, `mobile-conversion-gap-leak`,
  `product-page-conversion-leak`, `basket-value-gap-leak`,
  `second-order-gap-leak`
- Profit and decision: `contribution-margin-leak`, `weekly-revenue-leak-readout`
- `references/thresholds.md`: the single home for every number (30 keys)
- `references/shopify-exports.md`: where each input comes from
- `AGENTS.md`: the order of the checks and 8 blocking rules
- Scripts (standard library only): `tracking_gap.py`, `discount_leak.py`,
  `basket_value.py`, `repeat_rate.py`, shared `leakkit.py`
- Checks: `validate_skills.py`, `selftest.py`; `build_zips.py` for single-skill
  downloads
- `examples/`: a made-up sample store (1,533 orders) and a worked example

### Notes

Every threshold is at its first default and tagged `[heuristic]` unless a
platform states it. Expect recalibration in 1.1 as results from real stores
come in.
