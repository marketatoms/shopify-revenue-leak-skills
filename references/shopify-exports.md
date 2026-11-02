# Where each input comes from

Every skill in this pack works from something you can download or copy in a
few minutes. Nothing here logs into your store or your ad accounts. Shopify
renames reports from time to time; if a name below doesn't match your admin,
look for the report with the same columns.

If the **MarketAtoms MCP** is connected to Claude, several of these inputs are
read live instead (see each skill's "Live data" section). You never need both.

## Orders export

**Where:** Shopify admin > **Orders** > **Export** > choose the date range >
"Export orders" as CSV (plain CSV or CSV for Excel).

**Used by:** second-order gap, discount leak, refund and return leak, tracking
gap, basket value gap, contribution margin, weekly readout.

**Columns this pack reads:** `Name` (order number), `Email`, `Financial Status`,
`Currency`, `Subtotal`, `Shipping`, `Total`, `Discount Code`, `Discount Amount`,
`Created at`, `Lineitem quantity`, `Lineitem name`, `Lineitem price`,
`Lineitem sku`, `Cancelled at`, `Refunded Amount`, `Source`.

**Read this before using it:**

- The export has **one row per line item**. An order with 3 products has 3
  rows; the order-level columns (`Total`, `Discount Code`, `Refunded Amount`,
  ...) are filled only on the first row. The scripts handle this; if you read
  the CSV by eye, count orders by unique `Name`, not by rows.
- `Created at` is in the store's time zone. Ad platforms may report in another
  time zone; line the dates up before comparing.
- `Source` is the **sales channel** (web, pos, shopify_draft_order, an app),
  not the ad that drove the order. Use Shopify Analytics' "Sales attributed to
  marketing" for channel attribution.
- Exclude test orders and cancelled orders (`Cancelled at` not empty).

## Products and inventory exports

**Products:** Shopify admin > **Products** > **Export** > CSV. Reads `Handle`,
`Title`, `Variant SKU`, `Variant Price`, `Status`.

**Inventory:** Shopify admin > **Products** > **Inventory** > **Export** > CSV.
Reads `SKU` and the `Available` quantity per location (sum the locations that
fulfil online orders).

**Used by:** stock-out ad spend.

## Shopify Analytics reports

**Where:** Shopify admin > **Analytics** > **Reports**. Set the date range,
then export as CSV or copy the table.

| Report (search for it by name) | Columns needed | Used by |
| --- | --- | --- |
| Conversion rate breakdown / online store conversion over time | sessions, sessions with cart additions, sessions reaching checkout, sessions converted | checkout drop |
| Sessions by device type (with conversion) | device type, sessions, sessions converted | mobile conversion gap |
| Product analytics / product views and add-to-carts | product title, product views (or sessions with product views), add-to-carts | product page conversion |
| Sales attributed to marketing / sales by referrer | channel or referrer, orders, sales | tracking gap |
| Sales by product | product title, net quantity, net sales | stock-out ad spend, contribution margin |

## Ad platform reports

**Meta Ads Manager:** Ads Manager > choose **Ad sets** (or Campaigns) > set the
date range > **Reports** > **Export table data** (CSV). Include the columns
Ad set name, Amount spent, Purchases, Purchases conversion value, Starts (or
the ad set's start date) and Website URL of the ads if you have it.
Note the **attribution setting** shown in the column header (for example
"7-day click or 1-day view").

**Google Ads:** Campaigns report or Search terms report > **Download** > CSV.
Columns: Campaign / Search term, Cost, Conversions, Conv. value. Note which
conversion action is counted.

**Used by:** tracking gap, wasted ad spend, stock-out ad spend, contribution
margin, weekly readout.

## Store settings you type in

Some checks need a number only you know. The skill asks for it:

- **Free-shipping threshold** (basket value gap)
- **Target cost per purchase** (wasted ad spend)
- **Cost of goods** per product or as an average % of price, **shipping cost**
  per order, **payment fee** rate (contribution margin)
