"""Canonical composed-item valuation.

The master stores base items and component tables. This module turns a base
item plus refine/cards/slots/enchant tier into a price breakdown. It does not
enumerate combinations.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = ROOT / "data" / "market" / "components.yml"


def load_components() -> dict[str, Any]:
    return yaml.safe_load(COMPONENTS.read_text(encoding="utf-8")) or {}


def compose_value(
    base_mid: float,
    refine: int = 0,
    card_mids: list[float] | None = None,
    slots: int = 0,
    enchant_value: float = 0.0,
    components: dict[str, Any] | None = None,
) -> dict[str, Any]:
    table = components or load_components()
    refine_factors = table["refine"]["factors"]
    index = max(0, min(int(refine), len(refine_factors) - 1))
    refine_factor = float(refine_factors[index])
    card_discount = float(table["cards"]["liquidityDiscount"])
    card_sum = sum(float(value) for value in (card_mids or []))
    card_value = card_sum * card_discount
    base_value = float(base_mid) * refine_factor
    raw = base_value + card_value + float(enchant_value)
    cap = (
        float(base_mid) * float(table["caps"]["baseMultiplier"])
        + card_value * float(table["caps"]["cardMultiplier"])
    )
    value = min(raw, cap) if cap > 0 else raw
    return {
        "baseMid": round(base_mid),
        "refine": int(refine),
        "refineFactor": refine_factor,
        "slots": int(slots),
        "cardMids": [round(value) for value in (card_mids or [])],
        "cardValue": round(card_value),
        "enchantValue": round(float(enchant_value)),
        "raw": round(raw),
        "cap": round(cap),
        "value": round(value),
    }
