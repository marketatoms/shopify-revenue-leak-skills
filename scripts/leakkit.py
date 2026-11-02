"""Shared helpers for the revenue-leak scripts. Python 3.9+, standard library only.

- load_thresholds(): reads every number from references/thresholds.md, so the
  scripts never carry their own copies.
- load_orders(): reads a Shopify Orders export (one row per line item) and
  returns one record per order, with test and cancelled orders removed.
"""

from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _thresholds_path() -> Path:
    # Works for the full pack (scripts/ next to references/) and for a
    # single-skill download (scripts/ and references/ inside the skill folder).
    for candidate in (ROOT / "references" / "thresholds.md",
                      Path(__file__).resolve().parent.parent / "references" / "thresholds.md"):
        if candidate.exists():
            return candidate
    sys.exit("thresholds.md not found: keep the references/ folder next to scripts/.")


def load_thresholds() -> dict[str, float]:
    """Return {key: value}. Percentages become fractions (15% -> 0.15)."""
    values: dict[str, float] = {}
    row = re.compile(r"^\|\s*`([a-z_]+\.[a-z_]+)`\s*\|\s*\*\*([^*]+)\*\*")
    for line in _thresholds_path().read_text(encoding="utf-8").splitlines():
        m = row.match(line)
        if not m:
            continue
        key, raw = m.group(1), m.group(2)
        num = re.search(r"-?\d+(?:\.\d+)?", raw.replace(",", ""))
        if not num:
            continue
        value = float(num.group())
        if "%" in raw:
            value /= 100
        values[key] = value
    return values


def threshold(values: dict[str, float], key: str) -> float:
    if key not in values:
        sys.exit(f"Threshold `{key}` is missing from references/thresholds.md.")
    return values[key]


def money(text: str | None) -> float:
    if not text:
        return 0.0
    cleaned = re.sub(r"[^\d.\-]", "", text)
    try:
        return float(cleaned) if cleaned not in ("", "-", ".") else 0.0
    except ValueError:
        return 0.0


def parse_date(text: str) -> datetime:
    text = (text or "").strip()
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt)
            return dt.replace(tzinfo=None)  # keep the store's local clock time
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date: {text!r}")


@dataclass
class LineItem:
    name: str
    quantity: int
    price: float


@dataclass
class Order:
    name: str
    email: str
    created: datetime
    subtotal: float
    total: float
    discount_code: str
    discount_amount: float
    refunded: float
    source: str
    items: list[LineItem] = field(default_factory=list)

    @property
    def units(self) -> int:
        return sum(i.quantity for i in self.items)


REQUIRED = ["Name", "Created at", "Total", "Lineitem quantity", "Lineitem name"]


def load_orders(path: str | Path) -> list[Order]:
    path = Path(path)
    if not path.exists():
        sys.exit(f"Orders export not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"Not a Shopify Orders export: missing column(s) {', '.join(missing)}.")
        orders: dict[str, Order] = {}
        skipped: set[str] = set()
        for row in reader:
            name = (row.get("Name") or "").strip()
            if not name or name in skipped:
                continue
            if name not in orders:
                # Order-level fields are only filled on the first line-item row.
                status = (row.get("Financial Status") or "").lower()
                if (row.get("Cancelled at") or "").strip() or status in ("voided",) or (row.get("Test") or "").lower() == "true":
                    skipped.add(name)
                    continue
                orders[name] = Order(
                    name=name,
                    email=(row.get("Email") or "").strip().lower(),
                    created=parse_date(row.get("Created at", "")),
                    subtotal=money(row.get("Subtotal")),
                    total=money(row.get("Total")),
                    discount_code=(row.get("Discount Code") or "").strip().upper(),
                    discount_amount=money(row.get("Discount Amount")),
                    refunded=money(row.get("Refunded Amount")),
                    source=(row.get("Source") or "").strip(),
                )
            qty = int(money(row.get("Lineitem quantity")) or 0)
            orders[name].items.append(LineItem(row.get("Lineitem name", "").strip(), qty, money(row.get("Lineitem price"))))
    if not orders:
        sys.exit("No usable orders in the export (all empty, test or cancelled).")
    return sorted(orders.values(), key=lambda o: o.created)


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def table(headers: list[str], rows: list[list[object]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)
