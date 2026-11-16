#!/usr/bin/env python3
"""Precompute Garrett's daily offers and mission contracts.

This is a design artifact, not the final NPC script. It reads the current item
taxonomy, item weights and drop supply, then writes a table the NPC can use
without recalculating anything at runtime.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

import generate_item_taxonomy as taxonomy

ROOT = taxonomy.ROOT
DEFAULT_OUTPUT = ROOT.parent / "ozro-site" / "assets" / "items" / "garrett-missions.json"
TAXONOMY = ROOT.parent / "ozro-site" / "assets" / "items" / "taxonomy.json"

TIER_BANDS = {
    "abundant": (500, 1500),
    "common": (1500, 4000),
    "uncommon": (4000, 10000),
    "rare": (10000, 30000),
}
MISSION_QTY = {
    "common": (80, 150),
    "uncommon": (30, 70),
    "rare": (10, 25),
}
MISSION_TIERS = ("common", "uncommon", "rare")
MAX_MISSION_WEIGHT = 5000
MISSION_MULTIPLIER = 1.5
MISSION_PAYOUT_CAP = 1_500_000
MIN_MISSION_PAYOUT = 500_000
DAILY_CAP = 500_000
DAILY_OFFER_COUNT = 5


def load_weights() -> dict[int, int]:
    weights: dict[int, int] = {}
    for path in taxonomy.ITEM_FILES:
        for row in taxonomy.body(path):
            item_id = taxonomy.as_int(row.get("Id"), -1)
            if item_id >= 0:
                weights[item_id] = taxonomy.as_int(row.get("Weight"), 0)
    return weights


def load_mob_amounts() -> tuple[dict[int, int], dict[int, set[str]], dict[str, str]]:
    amounts: dict[int, int] = defaultdict(int)
    maps: dict[int, set[str]] = defaultdict(set)
    map_kind: dict[str, str] = {}
    instance_maps = taxonomy.load_instance_maps()

    if not taxonomy.SPAWNS.exists():
        return amounts, maps, map_kind

    for spawn in json.loads(taxonomy.SPAWNS.read_text(encoding="utf-8")).get("spawns", []):
        mob_id = taxonomy.as_int(spawn.get("mobId"), -1)
        map_name = str(spawn.get("map") or "")
        if mob_id < 0 or not map_name:
            continue
        amounts[mob_id] += taxonomy.as_int(spawn.get("amount"), 1)
        maps[mob_id].add(map_name)
        if map_name.startswith("gld"):
            map_kind[map_name] = "guild"
        elif map_name in instance_maps:
            map_kind[map_name] = "instance"
        else:
            map_kind[map_name] = "normal"
    return amounts, maps, map_kind


def load_rates(aegis_map: dict[str, int]) -> dict[int, dict[int, int]]:
    rates: dict[int, dict[int, int]] = defaultdict(dict)
    for path in taxonomy.MOB_FILES:
        for row in taxonomy.body(path):
            mob_id = taxonomy.as_int(row.get("Id"), -1)
            for field in ("Drops", "MvpDrops"):
                for drop in row.get(field) or []:
                    item_id = aegis_map.get(
                        taxonomy.normalize_aegis(str(drop.get("Item") or ""))
                    )
                    if item_id is not None:
                        rates[item_id][mob_id] = max(
                            rates[item_id].get(mob_id, 0),
                            taxonomy.as_int(drop.get("Rate")),
                        )
    return rates


def supply_for(
    item_id: int,
    rates: dict[int, dict[int, int]],
    amounts: dict[int, int],
    maps: dict[int, set[str]],
    map_kind: dict[str, str],
) -> tuple[float, int, int]:
    supply = 0.0
    map_names: set[str] = set()
    mobs = 0
    for mob_id, rate in rates.get(item_id, {}).items():
        map_names |= maps.get(mob_id, set())
        if not maps.get(mob_id):
            access = 0.05
        else:
            kinds = {map_kind.get(name, "normal") for name in maps[mob_id]}
            access = 1.0 if "normal" in kinds else (0.3 if "guild" in kinds else 0.1)
        effective = min(10000, rate * 5) / 10000
        supply += effective * amounts.get(mob_id, 0) * access
        mobs += 1
    return supply, mobs, len(map_names)


def price_for(tier: str, position: float) -> int:
    low, high = TIER_BANDS[tier]
    value = high - (high - low) * position
    return max(100, int(round(value / 100) * 100))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Garrett mission/offer tables")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not TAXONOMY.exists():
        raise SystemExit(f"missing taxonomy: {TAXONOMY}")

    taxonomy_data = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    candidates = taxonomy_data["categories"]["garrett_candidates"]
    weights = load_weights()
    aegis_map, _ = taxonomy.load_name_maps(taxonomy.load_items())
    rates = load_rates(aegis_map)
    amounts, mob_maps, map_kind = load_mob_amounts()

    known: list[dict] = []
    for item_id in candidates:
        supply, mobs, map_count = supply_for(item_id, rates, amounts, mob_maps, map_kind)
        if supply <= 0 or map_count == 0:
            continue
        known.append(
            {
                "id": item_id,
                "name": taxonomy_data["items"][str(item_id)]["name"],
                "weight": weights.get(item_id, 0),
                "supply": round(supply, 2),
                "mobs": mobs,
                "maps": map_count,
            }
        )

    known.sort(key=lambda row: (row["supply"], row["id"]))
    total = len(known)
    for index, row in enumerate(known):
        position = index / (total - 1) if total > 1 else 0
        if position >= 0.75:
            row["tier"] = "abundant"
        elif position >= 0.50:
            row["tier"] = "common"
        elif position >= 0.25:
            row["tier"] = "uncommon"
        elif position >= 0.10:
            row["tier"] = "rare"
        else:
            row["tier"] = "very_rare"

    tiers: dict[str, list[dict]] = {tier: [] for tier in TIER_BANDS}
    for tier in TIER_BANDS:
        rows = [row for row in known if row["tier"] == tier]
        for index, row in enumerate(rows):
            row["position"] = index / (len(rows) - 1) if len(rows) > 1 else 0
            row["unitPrice"] = price_for(tier, row["position"])
            tiers[tier].append(row)

    missions: list[dict] = []
    for tier in MISSION_TIERS:
        qty_min, qty_max = MISSION_QTY[tier]
        for row in tiers[tier]:
            weight = max(1, row["weight"])
            weight_cap = math.floor(MAX_MISSION_WEIGHT / weight)
            payout_cap_qty = math.floor(
                MISSION_PAYOUT_CAP / max(1, row["unitPrice"] * MISSION_MULTIPLIER)
            )
            target_quantity = round(qty_max - (qty_max - qty_min) * row["position"])
            quantity = max(1, min(target_quantity, weight_cap, payout_cap_qty))
            payout = int(round(row["unitPrice"] * quantity * MISSION_MULTIPLIER / 100) * 100)
            if payout < MIN_MISSION_PAYOUT:
                continue
            missions.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "tier": tier,
                    "supply": row["supply"],
                    "weight": row["weight"],
                    "quantity": quantity,
                    "quantityMin": qty_min,
                    "quantityMax": qty_max,
                    "unitPrice": row["unitPrice"],
                    "payout": payout,
                    "totalWeight": quantity * weight,
                }
            )

    missions.sort(key=lambda row: (MISSION_TIERS.index(row["tier"]), row["payout"], row["id"]))
    daily_offers = []
    for tier in ("abundant", "common", "uncommon", "rare"):
        for row in tiers[tier]:
            daily_offers.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "tier": tier,
                    "supply": row["supply"],
                    "weight": row["weight"],
                    "unitPrice": row["unitPrice"],
                }
            )

    output = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "config": {
            "dailyCap": DAILY_CAP,
            "dailyOfferCount": DAILY_OFFER_COUNT,
            "missionMultiplier": MISSION_MULTIPLIER,
            "missionPayoutCap": MISSION_PAYOUT_CAP,
            "minMissionPayout": MIN_MISSION_PAYOUT,
            "maxMissionWeight": MAX_MISSION_WEIGHT,
            "missionQuantity": {tier: list(MISSION_QTY[tier]) for tier in MISSION_TIERS},
            "unitPriceBands": {tier: list(band) for tier, band in TIER_BANDS.items()},
            "excludedTiers": ["very_rare"],
        },
        "counts": {
            "knownSupply": total,
            "missions": len(missions),
            "dailyOffers": len(daily_offers),
            **{tier: len(tiers[tier]) for tier in TIER_BANDS},
        },
        "missions": missions,
        "dailyOffers": daily_offers,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(missions)} missions and {len(daily_offers)} daily offers -> {args.output}")
    for tier in MISSION_TIERS:
        rows = [row for row in missions if row["tier"] == tier]
        if rows:
            payouts = [row["payout"] for row in rows]
            print(
                f"{tier}: {len(rows)} missions, payout {min(payouts):,}–{max(payouts):,}, "
                f"qty {min(row['quantity'] for row in rows)}–{max(row['quantity'] for row in rows)}"
            )


if __name__ == "__main__":
    main()
