#!/usr/bin/env python3
"""Generate a fixed Garrett proposal table from the v2 market data.

No dynamic generation: this writes a stable set of offers and missions that can
be reviewed and later embedded in the NPC as constants.
"""
from __future__ import annotations

import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from market import build_sample, common  # noqa: E402

OUT_DIR = common.ROOT / "data" / "market" / "samples"
SEED = 20261118
OFFER_COUNT = 200
MISSION_COUNTS = {"common": 20, "uncommon": 20, "rare": 10}
TIER_TARGET = {"common": 800_000, "uncommon": 1_050_000, "rare": 1_300_000}
MIN_QTY = {"common": 20, "uncommon": 10, "rare": 5}
MAX_QTY = {"common": 1000, "uncommon": 500, "rare": 200}
MISSION_MULTIPLIER = 1.10
MISSION_CAP = 1_500_000
MAX_WEIGHT = 5000
GARRETT_MULTIPLIER = 1.15
MIN_OFFER_PRICE = 500

RESTRICTED_TAGS = {
    "instance_only",
    "guild_only",
    "boss_only",
    "high_hp",
    "high_hp_source",
    "no_spawn",
    "untradeable",
    "cash_shop",
}


def garrett_buy(metric: dict[str, Any]) -> int:
    base = metric["price"]["npcBuyPrice"]
    mid = metric["price"]["mid"]
    npc_sell = metric["npcSellToPlayer"]
    cap = min(mid * 0.85, metric["price"]["npcSellPrice"] * 0.95)
    if metric["npcShop"] and npc_sell > 0:
        cap = min(cap, npc_sell * 0.90)
    return max(1, common.round_price(min(base * GARRETT_MULTIPLIER, cap)))


def mission_tier(metric: dict[str, Any]) -> str:
    abundance = metric["abundanceTier"]
    difficulty = metric["difficultyTier"]
    if abundance in {"uncommon", "scarce", "rare"} or difficulty in {"hard", "extreme"}:
        return "rare"
    if abundance == "common" or difficulty == "medium":
        return "uncommon"
    return "common"


def eligible(metric: dict[str, Any]) -> bool:
    tags = set(metric["tags"])
    access = metric["taxonomy"].get("access", {})
    if not metric["marketEligible"]:
        return False
    if not access.get("commonFarmEligible"):
        return False
    if metric["supplyOpen"] <= 0:
        return False
    if tags & RESTRICTED_TAGS:
        return False
    if metric["taxonomy"].get("sources") == ["group"]:
        return False
    if metric["price"]["status"] not in {"market", "synthetic"}:
        return False
    return True


def best_source(metric: dict[str, Any], data: dict[str, Any]) -> dict[str, Any] | None:
    item_id = metric["itemId"]
    item_type = metric["type"]
    rates = data["rates"]
    mobs = data["mobs"]
    spawn_by_mob = common.spawns_by_mob(data["spawns"])
    best = None
    for mob_id, drop in data["drops"].get(item_id, {}).items():
        mob = mobs.get(mob_id)
        if not mob:
            continue
        mob_is_boss = str(mob.get("Class") or "") == "Boss"
        for spawn in spawn_by_mob.get(mob_id, []):
            if spawn.get("boss") or mob_is_boss:
                continue
            if spawn["mapType"] not in {"field", "dungeon"}:
                continue
            eff = common.effective_rate(rates, item_type, drop["rate"], False, drop["mvp"])
            if eff <= 0:
                continue
            delay_s = spawn["delay"] / 1000 if spawn.get("delay") else 10
            flow = spawn["amount"] * eff * common.ACCESS_FACTOR.get(spawn["mapType"], 0.5) * 60 / max(delay_s, 1)
            if best is None or flow > best["flow"]:
                best = {
                    "mobId": mob_id,
                    "mob": str(mob.get("Name") or mob.get("AegisName") or mob_id),
                    "mobHp": common.effective_hp(mob, rates),
                    "mobLevel": common.as_int(mob.get("Level")),
                    "map": spawn["map"],
                    "mapType": spawn["mapType"],
                    "spawnAmount": spawn["amount"],
                    "delaySeconds": delay_s,
                    "dropRate": drop["rate"],
                    "effectiveRate": round(eff, 6),
                    "flow": flow,
                }
    return best


def mission_quantity(metric: dict[str, Any], tier: str, unit: int) -> tuple[int, int, bool]:
    target = TIER_TARGET[tier] * (1 + (metric["demandPercentile"] or 50) / 200)
    target = common.clamp(target, 200_000, 1_500_000)
    qty = round(target / max(1, unit))
    qty = max(MIN_QTY[tier], min(MAX_QTY[tier], qty))
    weight_cap = MAX_WEIGHT // max(1, metric["weight"])
    weight_limited = qty > weight_cap
    qty = max(1, min(qty, weight_cap))
    payout = max(1000, int(round(unit * qty * MISSION_MULTIPLIER / 1000) * 1000))
    payout = min(payout, MISSION_CAP)
    return qty, payout, weight_limited


def pick_buckets(candidates: list[dict[str, Any]], quotas: dict[str, int]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for metric in candidates:
        buckets[metric["abundanceTier"]].append(metric)
    selected: list[dict[str, Any]] = []
    used: set[int] = set()
    for tier, quota in quotas.items():
        pool = buckets.get(tier, [])
        pool.sort(key=lambda m: (m["price"]["npcBuyPrice"], m["itemId"]))
        for metric in pool:
            if len(selected) >= sum(quotas.values()):
                break
            if len([m for m in selected if m["abundanceTier"] == tier]) >= quota:
                break
            if metric["itemId"] in used:
                continue
            selected.append(metric)
            used.add(metric["itemId"])
    if len(selected) < sum(quotas.values()):
        rest = sorted(
            (m for m in candidates if m["itemId"] not in used),
            key=lambda m: (m["price"]["npcBuyPrice"], m["itemId"]),
        )
        selected.extend(rest[: sum(quotas.values()) - len(selected)])
    return selected


def main() -> None:
    data = build_sample.load_inputs()
    metrics = build_sample.build_metrics(data)
    build_sample.build_prices(data, metrics)
    build_sample.apply_craft_costs(metrics)

    candidates = [metric for metric in metrics.values() if eligible(metric)]
    candidates.sort(key=lambda m: (m["abundanceTier"], m["price"]["npcBuyPrice"], m["itemId"]))
    rng = random.Random(SEED)

    missions_by_tier: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for tier in ("common", "uncommon", "rare"):
        pool = [m for m in candidates if mission_tier(m) == tier]
        options = []
        target = TIER_TARGET[tier]
        for metric in pool:
            if metric["weight"] > MAX_WEIGHT // max(1, MIN_QTY[tier]):
                continue
            source = best_source(metric, data)
            if not source:
                continue
            unit = garrett_buy(metric)
            qty, payout, weight_limited = mission_quantity(metric, tier, unit)
            if qty < MIN_QTY[tier]:
                continue
            options.append(
                (
                    abs(payout - target),
                    1 if weight_limited else 0,
                    metric["itemId"],
                    metric,
                    source,
                    unit,
                    qty,
                    payout,
                    weight_limited,
                )
            )
        options.sort(key=lambda row: (row[0], row[1], row[2]))
        for _, _, _, metric, source, unit, qty, payout, weight_limited in options[: MISSION_COUNTS[tier]]:
            missions_by_tier[tier].append(
                {
                    "tier": tier,
                    "itemId": metric["itemId"],
                    "name": metric["name"],
                    "type": metric["type"],
                    "weight": metric["weight"],
                    "quantity": qty,
                    "garrettUnit": unit,
                    "payout": payout,
                    "canonicalBuy": metric["price"]["npcBuyPrice"],
                    "canonicalSell": metric["price"]["npcSellPrice"],
                    "canonicalMid": metric["price"]["mid"],
                    "canonicalBuyValue": metric["price"]["npcBuyPrice"] * qty,
                    "midValue": metric["price"]["mid"] * qty,
                    "abundance": metric["abundanceTier"],
                    "difficulty": metric["difficultyTier"],
                    "demand": metric["demandTier"],
                    "supplyOpen": round(metric["supplyOpen"], 3),
                    "weightLimited": weight_limited,
                    "partialDelivery": True,
                    "forfeitOnFail": True,
                    **source,
                }
            )

    mission_ids = {row["itemId"] for rows in missions_by_tier.values() for row in rows}
    offer_pool = [
        m
        for m in candidates
        if m["itemId"] not in mission_ids and garrett_buy(m) >= MIN_OFFER_PRICE
    ]
    offers = pick_buckets(
        offer_pool,
        {"abundant": 70, "common": 70, "uncommon": 40, "scarce": 20, "rare": 0},
    )[:OFFER_COUNT]
    offer_rows = []
    for metric in offers:
        source = best_source(metric, data)
        if not source:
            continue
        offer_rows.append(
            {
                "itemId": metric["itemId"],
                "name": metric["name"],
                "type": metric["type"],
                "weight": metric["weight"],
                "canonicalBuy": metric["price"]["npcBuyPrice"],
                "garrettBuy": garrett_buy(metric),
                "canonicalMid": metric["price"]["mid"],
                "canonicalSell": metric["price"]["npcSellPrice"],
                "abundance": metric["abundanceTier"],
                "difficulty": metric["difficultyTier"],
                "demand": metric["demandTier"],
                "supplyOpen": round(metric["supplyOpen"], 3),
                **source,
            }
        )

    missions = [row for tier in ("common", "uncommon", "rare") for row in missions_by_tier[tier]]
    summary = {
        "offers": len(offer_rows),
        "missions": len(missions),
        "missionsByTier": {tier: len(missions_by_tier[tier]) for tier in ("common", "uncommon", "rare")},
        "missionPayoutAvg": round(sum(row["payout"] for row in missions) / max(1, len(missions))),
        "missionPayoutMin": min((row["payout"] for row in missions), default=0),
        "missionPayoutMax": max((row["payout"] for row in missions), default=0),
        "missionQtyMin": min((row["quantity"] for row in missions), default=0),
        "missionQtyMax": max((row["quantity"] for row in missions), default=0),
        "missionRatioAvg": round(
            sum(row["payout"] / max(1, row["canonicalBuyValue"]) for row in missions) / max(1, len(missions)), 3
        ),
        "weightLimited": sum(1 for row in missions if row["weightLimited"]),
    }

    out = {
        "schemaVersion": 1,
        "seed": SEED,
        "policy": {
            "garrettMultiplier": GARRETT_MULTIPLIER,
            "minOfferPrice": MIN_OFFER_PRICE,
            "missionMultiplier": MISSION_MULTIPLIER,
            "missionCap": MISSION_CAP,
            "maxWeight": MAX_WEIGHT,
            "tierTarget": TIER_TARGET,
            "minQty": MIN_QTY,
            "maxQty": MAX_QTY,
            "partialDelivery": True,
            "forfeitOnFail": True,
            "dynamic": False,
        },
        "summary": summary,
        "offers": offer_rows,
        "missions": missions,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "garrett_proposal.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Garrett v2 proposal",
        "",
        f"Seed: `{SEED}`. Fixed table, no dynamic generation.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(summary, indent=2),
        "```",
        "",
        "## Missions",
        "",
        "| # | Tier | Item | Qty | Canonical buy | Garrett unit | Payout | Buy value | Mob | HP | Mob lvl | Abundance | Difficulty | Partial | Forfeit |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|---|---|---|",
    ]
    for index, row in enumerate(missions, 1):
        lines.append(
            f"| {index} | {row['tier']} | {row['name']} | {row['quantity']} | "
            f"{row['canonicalBuy']:,} | {row['garrettUnit']:,} | {row['payout']:,} | "
            f"{row['canonicalBuyValue']:,} | {row['mob']} | {row['mobHp']:,} | {row['mobLevel']} | "
            f"{row['abundance']} | {row['difficulty']} | yes | yes |"
        )
    lines += [
        "",
        "## Offers",
        "",
        "| # | Item | Canonical buy | Garrett buy | Mid | Abundance | Demand | Mob | HP | Mob lvl | Map | Spawn | Drop |",
        "|---:|---|---:|---:|---:|---|---|---|---:|---:|---|---:|---:|",
    ]
    for index, row in enumerate(offer_rows, 1):
        lines.append(
            f"| {index} | {row['name']} | {row['canonicalBuy']:,} | {row['garrettBuy']:,} | "
            f"{row['canonicalMid']:,} | {row['abundance']} | {row['demand']} | {row['mob']} | "
            f"{row['mobHp']:,} | {row['mobLevel']} | {row['map']} | {row['spawnAmount']} | {row['dropRate']} |"
        )
    (OUT_DIR / "garrett_proposal.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_DIR / 'garrett_proposal.json'}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
