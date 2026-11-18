#!/usr/bin/env python3
"""Build a sample of the future OzRo market master.

This is deliberately a sample, not the final master. It joins the current
taxonomy, canonical server spawns, custom rates/HP and the historical market
snapshot, then writes:

  data/market/samples/general.jsonl
  data/market/samples/edge.jsonl
  data/market/samples/summary.json
  data/market/samples/REPORT.md

The report is generated; interpretation lives in the design docs.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from market import common, valuation  # noqa: E402

OUT_DIR = common.ROOT / "data" / "market" / "samples"
GENERAL_SIZE = 150
EDGE_PER_CATEGORY = 8
SEED = 20261118

ABUNDANCE_BANDS = [(10, "rare"), (25, "scarce"), (50, "uncommon"), (75, "common"), (101, "abundant")]
DIFFICULTY_BANDS = [(50, "easy"), (75, "medium"), (90, "hard"), (101, "extreme")]
DEMAND_BANDS = [(10, "none"), (40, "low"), (75, "medium"), (101, "high")]
CONFIDENCE_UNCERTAINTY = {"high": 0.15, "medium": 0.30, "low": 0.50, "server": 0.20, None: 0.50}


def weighted_average(pairs: list[tuple[float, float]]) -> float | None:
    total = sum(weight for weight, _ in pairs if weight > 0)
    if total <= 0:
        return None
    return sum(weight * value for weight, value in pairs if weight > 0) / total


def tier(percentile: float | None, bands: list[tuple[float, str]], default: str = "unknown") -> str:
    return common.tier_from_percentile(percentile, bands, default)


def load_inputs() -> dict[str, Any]:
    taxonomy = common.load_taxonomy()
    items = common.load_items()
    mobs = common.load_mobs()
    rates = common.load_battle_config()
    drops = common.load_drop_sources(taxonomy, items, mobs)
    spawns, spawn_report = common.load_spawns()
    master = common.load_master_list()
    groups = common.load_item_groups(taxonomy, items)
    craft = common.load_craft_recipes()
    cash = common.load_cash_prices(taxonomy, items)
    return {
        "taxonomy": taxonomy,
        "items": items,
        "mobs": mobs,
        "rates": rates,
        "drops": drops,
        "spawns": spawns,
        "spawn_report": spawn_report,
        "master": master,
        "groups": groups,
        "craft": craft,
        "cash": cash,
        "canon": common.load_canon(),
    }


def build_metrics(data: dict[str, Any]) -> dict[int, dict[str, Any]]:
    taxonomy = data["taxonomy"]
    items = data["items"]
    mobs = data["mobs"]
    rates = data["rates"]
    drops = data["drops"]
    spawn_by_mob = common.spawns_by_mob(data["spawns"])
    master = data["master"]

    metrics: dict[int, dict[str, Any]] = {}
    for item_id_raw, tax in taxonomy["items"].items():
        item_id = int(item_id_raw)
        item = items.get(item_id, {})
        item_type = item.get("type") or tax.get("type") or "Etc"
        flows: dict[str, float] = defaultdict(float)
        threats: list[tuple[float, float]] = []

        for mob_id, drop in drops.get(item_id, {}).items():
            mob = mobs.get(mob_id)
            if not mob:
                continue
            mob_is_boss = str(mob.get("Class") or "") == "Boss"
            for spawn in spawn_by_mob.get(mob_id, []):
                is_boss = bool(spawn.get("boss")) or mob_is_boss
                eff = common.effective_rate(rates, item_type, drop["rate"], is_boss, drop["mvp"])
                if eff <= 0:
                    continue
                delay_s = spawn["delay"] / 1000 if spawn.get("delay") else 10
                flow = (
                    spawn["amount"]
                    * eff
                    * common.ACCESS_FACTOR.get(spawn["mapType"], 0.5)
                    * 60
                    / max(delay_s, 1)
                )
                if is_boss:
                    flows["boss"] += flow
                    threats.append((flow, common.threat(mob, rates, True)))
                else:
                    flows[spawn["mapType"]] += flow
                    threats.append((flow, common.threat(mob, rates, False)))

        supply_open = flows["field"] + flows["dungeon"]
        supply_total = sum(flows.values())
        metrics[item_id] = {
            "itemId": item_id,
            "name": item.get("name") or tax.get("name") or str(item_id),
            "aegis": item.get("aegis") or tax.get("aegis") or "",
            "type": item_type,
            "weight": item.get("weight", 0),
            "slots": item.get("slots", 0),
            "refineable": bool(item.get("refineable")),
            "attack": item.get("attack", 0),
            "defense": item.get("defense", 0),
            "equipLevelMin": item.get("equipLevelMin", 0),
            "custom": bool(item.get("custom")),
            "groupInfo": data["groups"].get(item_id, {}),
            "craftRecipe": data["craft"].get(item_id),
            "cashInfo": data["cash"].get(item_id),
            "npcSellToPlayer": item.get("buy", 0),
            "npcBuyFromPlayer": item.get("sell", 0),
            "taxonomy": tax,
            "flows": dict(flows),
            "supplyOpen": supply_open,
            "supplyTotal": supply_total,
            "difficultyRaw": weighted_average(threats),
            "salesLatam": ((master.get(item_id) or {}).get("latam") or {}).get("total_sold"),
            "salesAtlantis": ((master.get(item_id) or {}).get("atlantis") or {}).get("total_sold"),
            "soldForRank": ((master.get(item_id) or {}).get("stats") or {}).get("sold_for_rank"),
            "history": master.get(item_id),
        }

    open_values = sorted(m["supplyOpen"] for m in metrics.values() if m["supplyOpen"] > 0)
    threat_values = sorted(m["difficultyRaw"] for m in metrics.values() if m["difficultyRaw"] is not None)

    for metric in metrics.values():
        metric["supplyPercentile"] = common.percentile_rank(open_values, metric["supplyOpen"]) if metric["supplyOpen"] > 0 else None
        metric["abundanceTier"] = tier(metric["supplyPercentile"], ABUNDANCE_BANDS, "none") if metric["supplyOpen"] > 0 else "none"
        metric["difficultyPercentile"] = common.percentile_rank(threat_values, metric["difficultyRaw"])
        metric["difficultyTier"] = tier(metric["difficultyPercentile"], DIFFICULTY_BANDS) if metric["difficultyRaw"] is not None else "unknown"

    def residual_map(field: str) -> dict[int, float]:
        expected: dict[tuple[str, str], list[float]] = defaultdict(list)
        fallback: dict[str, list[float]] = defaultdict(list)
        for metric in metrics.values():
            sold = metric[field]
            if sold:
                expected[(metric["type"], metric["abundanceTier"])].append(math.log1p(sold))
                fallback[metric["type"]].append(math.log1p(sold))
        expected_median = {key: common.median(values) for key, values in expected.items()}
        fallback_median = {key: common.median(values) for key, values in fallback.items()}
        result: dict[int, float] = {}
        for metric in metrics.values():
            sold = metric[field]
            if not sold:
                continue
            key = (metric["type"], metric["abundanceTier"])
            expected_log = expected_median.get(key, fallback_median.get(metric["type"], 0.0))
            result[metric["itemId"]] = math.log1p(sold) - expected_log
        return result

    latam_residuals = residual_map("salesLatam")
    atlantis_residuals = residual_map("salesAtlantis")
    for metric in metrics.values():
        item_id = metric["itemId"]
        metric["demandLatamResidual"] = latam_residuals.get(item_id)
        metric["demandAtlantisResidual"] = atlantis_residuals.get(item_id)
        sources = []
        if item_id in latam_residuals:
            sources.append((latam_residuals[item_id], min(15.0, math.log1p(metric["salesLatam"] or 0))))
        if item_id in atlantis_residuals:
            sources.append((atlantis_residuals[item_id], min(15.0, math.log1p(metric["salesAtlantis"] or 0))))
        if sources:
            weight = sum(weight for _, weight in sources)
            metric["demandResidual"] = sum(value * weight for value, weight in sources) / weight if weight else None
            metric["demandSources"] = len(sources)
        else:
            metric["demandResidual"] = None
            metric["demandSources"] = 0

    residuals = sorted(m["demandResidual"] for m in metrics.values() if m["demandResidual"] is not None)
    for metric in metrics.values():
        residual = metric["demandResidual"]
        metric["demandPercentile"] = common.percentile_rank(residuals, residual)
        metric["demandTier"] = (
            tier(metric["demandPercentile"], DEMAND_BANDS, "unknown")
            if residual is not None
            else "unknown"
        )

    return metrics


def build_tags(taxonomy: dict[str, Any], metric: dict[str, Any]) -> list[str]:
    item_id = metric["itemId"]
    tags = {
        name
        for name, members in taxonomy["categories"].items()
        if item_id in members
    }
    tags |= set(metric["taxonomy"].get("access", {}).get("restrictions", []))
    return sorted(tags)


def build_prices(data: dict[str, Any], metrics: dict[int, dict[str, Any]]) -> None:
    master = data["master"]
    canon = data.get("canon") or {}
    manual_prices = {
        int(key): int(value)
        for key, value in ((canon.get("pricing") or {}).get("manual_prices") or {}).items()
    }
    priced = [m for m in metrics.values() if (m.get("history") or {}).get("price", {}).get("reference")]
    type_bases: dict[str, float] = {}
    type_medians: dict[str, float] = {}
    type_lows: dict[str, float] = {}
    type_highs: dict[str, float] = {}
    for item_type in {m["type"] for m in priced}:
        values = [
            math.log(m["history"]["price"]["reference"])
            for m in priced
            if m["type"] == item_type and m["history"]["price"]["reference"] > 0
        ]
        if values:
            type_bases[item_type] = math.exp(common.percentile(values, 0.40))
            type_medians[item_type] = math.exp(common.median(values))
            type_lows[item_type] = math.exp(common.percentile(values, 0.10))
            type_highs[item_type] = math.exp(common.percentile(values, 0.90))
    open_supplies = [m["supplyOpen"] for m in metrics.values() if m["supplyOpen"] > 0]
    median_open_supply = common.median(open_supplies) if open_supplies else 1.0
    equipment_types = {"Weapon", "Armor", "ShadowGear", "Shadowgear"}

    for metric in metrics.values():
        hist = metric.get("history") or {}
        price = hist.get("price") or {}
        stats = hist.get("stats") or {}
        reference = price.get("reference")
        confidence = stats.get("confidence_label")
        cv = stats.get("atlantis_cv")
        outlier_flags = hist.get("outlier_flags") or []
        manipulation = bool((cv is not None and cv > 3) or "atlantis_extreme_max" in outlier_flags)
        metric["manipulationSuspected"] = manipulation
        tags = set(build_tags(data["taxonomy"], metric))

        is_untradeable = "untradeable" in tags
        is_unobtainable = "unobtainable" in tags
        has_source = bool(metric["taxonomy"].get("sources")) or metric["taxonomy"].get("access", {}).get("best") not in (None, "none")
        market_eligible = not is_untradeable and (not is_unobtainable or bool(reference)) and (has_source or bool(reference))
        metric["marketEligible"] = market_eligible

        access_best = str(metric["taxonomy"].get("access", {}).get("best") or "none")
        manual_mid = manual_prices.get(metric["itemId"])
        source_factor = 1.0
        gear_factor = 1.0
        supply_mult = 1.0
        demand_mult = 1.0
        difficulty_mult = 1.0
        floor = metric["npcBuyFromPlayer"] * 1.05 if metric["npcBuyFromPlayer"] > 0 else 1.0
        npc_shop = "npc_shop" in tags or "npc_shop" in metric["taxonomy"].get("sources", [])
        ceiling = float("inf")
        if npc_shop and metric["npcSellToPlayer"] > 0:
            ceiling = metric["npcSellToPlayer"] * 0.95

        if manual_mid:
            status = "manual"
            base = float(manual_mid)
            base_method = "manual"
            mid = float(manual_mid)
            low = high = mid
            uncertainty = 0.0
            buy_ceiling = mid
            npc_sell = mid
            sell_margin = 0.0
        else:
            if reference:
                status = "market"
                base = float(reference)
                base_method = "historical"
            else:
                status = "synthetic"
                source_factor = {
                    "group": 0.70,
                    "craft": 0.90,
                    "quest": 0.80,
                    "instance": 0.80,
                    "guild": 0.70,
                    "unknown": 0.50,
                    "none": 0.50,
                }.get(access_best, 1.0)
                group_share = float((metric.get("groupInfo") or {}).get("bestShare") or 0.0)
                if access_best == "group" and group_share > 0:
                    source_factor = 0.60 + 0.10 * (1.0 - group_share)
                if metric["type"] in equipment_types:
                    combat = metric["attack"] + metric["defense"]
                    gear_factor = common.clamp(
                        1
                        + 0.08 * metric["slots"]
                        + 0.05 * math.log1p(max(0, combat))
                        + 0.10 * max(0, metric["equipLevelMin"] - 50) / 50,
                        0.70,
                        2.00,
                    )
                if not has_source:
                    base = min(type_lows.get(metric["type"], 1000.0), 1_000_000.0) * 0.50
                    source_factor = 0.50
                    base_method = "no_source_cap"
                else:
                    base = type_bases.get(metric["type"], type_medians.get(metric["type"], 1000.0)) * source_factor * gear_factor
                    base_method = "type_p40"

            if metric["supplyOpen"] > 0 and median_open_supply > 0:
                supply_mult = common.clamp((median_open_supply / metric["supplyOpen"]) ** 0.25, 0.5, 2.0)
            demand_z = ((metric["demandPercentile"] or 50) - 50) / 50
            difficulty_z = ((metric["difficultyPercentile"] or 50) - 50) / 50
            demand_mult = common.clamp(1 + 0.25 * demand_z, 0.7, 1.5)
            difficulty_mult = common.clamp(1 + 0.15 * difficulty_z, 0.8, 1.5)
            raw = base * supply_mult * demand_mult * difficulty_mult

            mid = common.clamp(raw, floor, ceiling)
            if status == "synthetic" and has_source:
                mid = min(mid, type_highs.get(metric["type"], mid))
            uncertainty = CONFIDENCE_UNCERTAINTY.get(confidence, 0.50)
            if not reference:
                uncertainty = max(uncertainty, 0.50)
            low = max(floor, mid * (1 - uncertainty))
            high = min(ceiling, mid * (1 + uncertainty))
            if high <= low:
                high = low * 1.05

            type_median = type_medians.get(metric["type"], base)
            type_cap = type_median * 0.50
            if manipulation:
                buy_ceiling = min(mid * 0.35, low * 0.70, type_cap)
            elif status == "synthetic":
                buy_ceiling = min(mid * 0.45, type_cap)
            elif confidence == "high":
                buy_ceiling = mid * 0.75
            elif confidence == "server":
                buy_ceiling = min(mid * 0.60, metric["npcBuyFromPlayer"] if metric["npcBuyFromPlayer"] > 0 else mid)
            elif confidence == "medium":
                buy_ceiling = min(mid * 0.60, type_median)
            else:
                buy_ceiling = min(mid * 0.45, low * 0.75, type_cap)
            buy_ceiling = min(buy_ceiling, ceiling * 0.95, high * 0.80)
            buy_ceiling = max(floor, buy_ceiling)

            if manipulation:
                sell_margin = 0.50
            elif status == "synthetic":
                sell_margin = 0.35
            elif confidence == "high":
                sell_margin = 0.10
            elif confidence in {"medium", "server"}:
                sell_margin = 0.20
            else:
                sell_margin = 0.30
            candidate_sell = mid * (1 + sell_margin)
            npc_sell = max(buy_ceiling * 1.10, min(candidate_sell, buy_ceiling * 1.50))
            if not math.isinf(ceiling):
                npc_sell = min(npc_sell, ceiling)
            npc_sell = max(npc_sell, buy_ceiling * 1.05)

        demand_pct = metric["demandPercentile"]
        supply_pct = metric["supplyPercentile"]
        if demand_pct is None and supply_pct is None:
            market_pressure = None
            stock_hint = "unknown"
            restock_weight = None
        else:
            market_pressure = (demand_pct if demand_pct is not None else 50) - (supply_pct if supply_pct is not None else 50)
            stock_hint = "low" if market_pressure > 25 else "high" if market_pressure < -25 else "normal"
            restock_weight = common.clamp(0.5 + market_pressure / 200, 0.1, 0.9)

        metric["marketPressure"] = round(market_pressure, 2) if market_pressure is not None else None
        metric["stockHint"] = stock_hint
        metric["restockWeight"] = round(restock_weight, 4) if restock_weight is not None else None
        metric["tags"] = sorted(tags)
        metric["npcShop"] = npc_shop
        metric["price"] = {
            "status": status,
            "baseMethod": base_method,
            "historicalReference": reference,
            "historicalSource": price.get("reference_source"),
            "historicalConfidence": confidence,
            "historicalCv": cv,
            "manipulationSuspected": manipulation,
            "base": common.round_price(base),
            "sourceFactor": source_factor,
            "gearFactor": round(gear_factor, 4),
            "rawMid": common.round_price(raw if not manual_mid else mid),
            "clamped": (not manual_mid and (raw > ceiling or raw < floor)),
            "supplyMultiplier": round(supply_mult, 4),
            "demandMultiplier": round(demand_mult, 4),
            "difficultyMultiplier": round(difficulty_mult, 4),
            "low": common.round_price(low),
            "mid": common.round_price(mid),
            "high": common.round_price(high),
            "npcBuyPrice": common.round_price(buy_ceiling),
            "npcSellPrice": common.round_price(npc_sell),
            "buyCeiling": common.round_price(buy_ceiling),
            "sellFloor": common.round_price(mid if status == "manual" else buy_ceiling),
            "sellMargin": sell_margin,
            "floor": common.round_price(floor),
            "ceiling": None if math.isinf(ceiling) else common.round_price(ceiling),
            "uncertainty": uncertainty,
        }

        review: list[str] = []
        if manipulation:
            review.append("manipulation_suspected")
        if status == "manual":
            review.append("manual_price")
        if status == "synthetic":
            review.append("synthetic_price")
        if not has_source:
            review.append("no_source")
        if metric["supplyOpen"] <= 0:
            review.append("no_open_supply")
        if tags & {"instance_only", "guild_only"}:
            review.append("restricted_access")
        if tags & {"high_hp", "boss_only"}:
            review.append("hard_source")
        if metric["taxonomy"].get("access", {}).get("best") in {"group", "quest", "none"}:
            review.append("no_direct_farm")
        if metric["custom"]:
            review.append("custom_item")
        if not market_eligible:
            review.append("not_market_eligible")
        metric["reviewReasons"] = sorted(set(review))


def apply_craft_costs(metrics: dict[int, dict[str, Any]]) -> None:
    for metric in metrics.values():
        recipe = metric.get("craftRecipe")
        if not recipe:
            continue
        cost = 0.0
        complete = True
        for material in recipe.get("materials") or []:
            material_metric = metrics.get(material["itemId"])
            if not material_metric:
                complete = False
                break
            cost += material_metric["price"]["mid"] * material["amount"]
        if not complete or cost <= 0:
            continue
        craft_cost = cost * 1.15
        metric["craftCost"] = common.round_price(craft_cost)
        if (
            metric["price"]["status"] == "synthetic"
            and metric["taxonomy"].get("access", {}).get("best") == "craft"
            and craft_cost > metric["price"]["mid"]
        ):
            old_mid = max(1, metric["price"]["mid"])
            ratio = craft_cost / old_mid
            metric["price"]["mid"] = common.round_price(craft_cost)
            metric["price"]["low"] = common.round_price(metric["price"]["low"] * ratio)
            metric["price"]["high"] = common.round_price(metric["price"]["high"] * ratio)
            metric["price"]["npcBuyPrice"] = common.round_price(
                min(craft_cost * 0.45, metric["price"]["npcBuyPrice"] * 1.50)
            )
            metric["price"]["buyCeiling"] = metric["price"]["npcBuyPrice"]
            metric["price"]["sellFloor"] = metric["price"]["npcBuyPrice"]
            metric["price"]["npcSellPrice"] = common.round_price(
                max(metric["price"]["npcBuyPrice"] * 1.10, min(craft_cost * 1.35, metric["price"]["npcBuyPrice"] * 1.50))
            )
            metric["price"]["baseMethod"] = "craft_cost"
            metric["price"]["craftCost"] = metric["craftCost"]


def serialize(metric: dict[str, Any]) -> dict[str, Any]:
    tax = metric["taxonomy"]
    return {
        "schemaVersion": 1,
        "itemId": metric["itemId"],
        "name": metric["name"],
        "aegis": metric["aegis"],
        "type": metric["type"],
        "weight": metric["weight"],
        "slots": metric["slots"],
        "refineable": metric["refineable"],
        "custom": metric["custom"],
        "npcEligible": True,
        "marketEligible": metric["marketEligible"],
        "tags": metric["tags"],
        "sources": tax.get("sources", []),
        "groupInfo": metric.get("groupInfo") or {},
        "craftRecipe": metric.get("craftRecipe"),
        "craftCost": metric.get("craftCost"),
        "cash": metric.get("cashInfo"),
        "access": tax.get("access", {}),
        "spawnSupply": {
            "field": round(metric["flows"].get("field", 0), 6),
            "dungeon": round(metric["flows"].get("dungeon", 0), 6),
            "other": round(metric["flows"].get("other", 0), 6),
            "boss": round(metric["flows"].get("boss", 0), 6),
            "instance": round(metric["flows"].get("instance", 0), 6),
            "guild": round(metric["flows"].get("guild", 0), 6),
            "quest": round(metric["flows"].get("quest", 0), 6),
            "event": round(metric["flows"].get("event", 0), 6),
        },
        "supply": {
            "open": round(metric["supplyOpen"], 6),
            "total": round(metric["supplyTotal"], 6),
            "percentile": round(metric["supplyPercentile"], 2) if metric["supplyPercentile"] is not None else None,
            "abundanceTier": metric["abundanceTier"],
            "difficulty": round(metric["difficultyRaw"], 6) if metric["difficultyRaw"] is not None else None,
            "difficultyPercentile": round(metric["difficultyPercentile"], 2) if metric["difficultyPercentile"] is not None else None,
            "difficultyTier": metric["difficultyTier"],
        },
        "demand": {
            "salesLatam": metric["salesLatam"],
            "salesAtlantis": metric["salesAtlantis"],
            "soldForRank": metric["soldForRank"],
            "residual": round(metric["demandResidual"], 4) if metric["demandResidual"] is not None else None,
            "latamResidual": round(metric["demandLatamResidual"], 4) if metric.get("demandLatamResidual") is not None else None,
            "atlantisResidual": round(metric["demandAtlantisResidual"], 4) if metric.get("demandAtlantisResidual") is not None else None,
            "sources": metric.get("demandSources", 0),
            "percentile": round(metric["demandPercentile"], 2) if metric["demandPercentile"] is not None else None,
            "tier": metric["demandTier"],
            "marketPressure": metric["marketPressure"],
            "stockHint": metric["stockHint"],
            "restockWeight": metric["restockWeight"],
        },
        "npc": {
            "sellToPlayer": metric["npcSellToPlayer"],
            "buyFromPlayer": metric["npcBuyFromPlayer"],
            "shop": metric["npcShop"],
        },
        "price": metric["price"],
        "reviewReasons": metric["reviewReasons"],
    }


def edge_candidates(metrics: dict[int, dict[str, Any]]) -> dict[str, list[int]]:
    categories: dict[str, list[int]] = defaultdict(list)
    for item_id, m in metrics.items():
        hist = m.get("history") or {}
        price = hist.get("price") or {}
        stats = hist.get("stats") or {}
        ref = price.get("reference")
        confidence = stats.get("confidence_label")
        tags = set(m["tags"])
        access = m["taxonomy"].get("access", {})
        if ref and confidence == "high":
            categories["priced_high_confidence"].append(item_id)
        if ref and confidence == "low":
            categories["priced_low_confidence"].append(item_id)
        if m["manipulationSuspected"]:
            categories["manipulation_suspected"].append(item_id)
        if not ref and m["supplyOpen"] > 0:
            categories["no_price_with_open_supply"].append(item_id)
        if m["taxonomy"].get("sources") == ["group"]:
            categories["group_only"].append(item_id)
        if access.get("best") == "craft":
            categories["craft_best"].append(item_id)
        if "instance_only" in tags:
            categories["instance_only"].append(item_id)
        if "guild_only" in tags:
            categories["guild_only"].append(item_id)
        if "boss_only" in tags:
            categories["boss_only"].append(item_id)
        if "high_hp" in tags:
            categories["high_hp"].append(item_id)
        if "npc_shop" in tags:
            categories["npc_shop"].append(item_id)
        if m["custom"]:
            categories["custom"].append(item_id)
        if ref and m["price"]["status"] == "market":
            categories["market_price"].append(item_id)
        if ref and m["price"]["status"] == "synthetic":
            categories["synthetic_price"].append(item_id)
        if m["marketEligible"]:
            categories["market_eligible"].append(item_id)
        if "untradeable" in tags:
            categories["untradeable"].append(item_id)
        if "unobtainable" in tags:
            categories["unobtainable"].append(item_id)
        if not m["taxonomy"].get("sources"):
            categories["no_source"].append(item_id)
        if m["price"]["status"] == "manual":
            categories["manual_price"].append(item_id)
        if not m["marketEligible"]:
            categories["not_market_eligible"].append(item_id)
    if categories.get("market_price"):
        values = [(metrics[i]["price"]["historicalReference"], i) for i in categories["market_price"]]
        values.sort()
        categories["price_bottom_1pct"] = [i for _, i in values[: max(5, len(values) // 100)]]
        categories["price_top_1pct"] = [i for _, i in values[-max(5, len(values) // 100):]]
    supplies = sorted((metrics[i]["supplyOpen"], i) for i in metrics if metrics[i]["supplyOpen"] > 0)
    if supplies:
        categories["max_open_supply"] = [i for _, i in supplies[-EDGE_PER_CATEGORY:]]
        categories["min_open_supply"] = [i for _, i in supplies[:EDGE_PER_CATEGORY]]
    return categories


def choose_edge(metrics: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    categories = edge_candidates(metrics)
    selected: dict[int, set[str]] = defaultdict(set)
    for category, ids in categories.items():
        ordered = sorted(set(ids))
        if category in {"max_open_supply", "min_open_supply"}:
            ordered = list(ids)
        for item_id in ordered[:EDGE_PER_CATEGORY]:
            selected[item_id].add(category)
    rows = []
    for item_id in sorted(selected):
        row = serialize(metrics[item_id])
        row["sampleKind"] = "edge"
        row["edgeTags"] = sorted(selected[item_id])
        rows.append(row)
    return rows



def build_composed(metrics: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    bases = [
        m
        for m in metrics.values()
        if m["type"] in {"Weapon", "Armor"} and m["slots"] > 0 and m["price"]["status"] in {"market", "synthetic"}
    ]
    bases.sort(key=lambda m: (m["price"]["mid"], m["itemId"]))
    if len(bases) > 12:
        indices = sorted({round(i * (len(bases) - 1) / 11) for i in range(12)})
        bases = [bases[index] for index in indices]
    cards = [
        m
        for m in metrics.values()
        if m["type"] == "Card" and m["price"]["status"] == "market"
    ]
    cards.sort(key=lambda m: (m["price"]["mid"], m["itemId"]))
    if not bases or not cards:
        return []
    card_pool = [
        cards[index]
        for index in sorted({0, len(cards) // 4, len(cards) // 2, (3 * len(cards)) // 4, len(cards) - 1})
    ]
    rows = []
    for base_index, base in enumerate(bases[:12]):
        count = min(base["slots"], len(card_pool), 3)
        chosen = [card_pool[(base_index + offset) % len(card_pool)] for offset in range(count)]
        for refine in (0, 4, 7, 10):
            breakdown = valuation.compose_value(
                base["price"]["mid"],
                refine=refine,
                card_mids=[card["price"]["mid"] for card in chosen],
                slots=base["slots"],
            )
            rows.append(
                {
                    "schemaVersion": 1,
                    "sampleKind": "composed",
                    "itemId": base["itemId"],
                    "name": base["name"],
                    "baseMid": base["price"]["mid"],
                    "slots": base["slots"],
                    "refine": refine,
                    "cards": [
                        {"itemId": card["itemId"], "name": card["name"], "mid": card["price"]["mid"]}
                        for card in chosen
                    ],
                    "breakdown": breakdown,
                }
            )
    return rows


def summary(data: dict[str, Any], metrics: dict[int, dict[str, Any]], general: list[dict], edge: list[dict], composed: list[dict]) -> dict[str, Any]:
    def counts(rows: list[dict], key: str) -> dict[str, int]:
        result: dict[str, int] = defaultdict(int)
        for row in rows:
            value = row
            for part in key.split("."):
                value = (value or {}).get(part)
            result[str(value)] += 1
        return dict(sorted(result.items(), key=lambda item: (-item[1], item[0])))

    return {
        "schemaVersion": 1,
        "seed": SEED,
        "sources": {
            "taxonomy": str(common.TAXONOMY),
            "masterList": str(common.MASTER_LIST),
            "battleConf": str(common.BATTLE_CONF),
        },
        "rates": {
            key: value
            for key, value in data["rates"].items()
            if key.startswith(("item_rate_", "monster_hp_rate", "mvp_hp_rate"))
        },
        "spawns": data["spawn_report"],
        "universe": {
            "items": len(metrics),
            "withOpenSupply": sum(1 for m in metrics.values() if m["supplyOpen"] > 0),
            "withHistory": sum(1 for m in metrics.values() if m.get("history")),
            "marketPrice": sum(1 for m in metrics.values() if m["price"]["status"] == "market"),
            "syntheticPrice": sum(1 for m in metrics.values() if m["price"]["status"] == "synthetic"),
            "manualPrice": sum(1 for m in metrics.values() if m["price"]["status"] == "manual"),
            "notApplicable": sum(1 for m in metrics.values() if m["price"]["status"] == "not_applicable"),
            "marketEligible": sum(1 for m in metrics.values() if m["marketEligible"]),
            "marketEligibleMarket": sum(1 for m in metrics.values() if m["marketEligible"] and m["price"]["status"] == "market"),
            "marketEligibleSynthetic": sum(1 for m in metrics.values() if m["marketEligible"] and m["price"]["status"] == "synthetic"),
            "marketEligibleWithOpenSupply": sum(1 for m in metrics.values() if m["marketEligible"] and m["supplyOpen"] > 0),
            "marketEligibleNoOpenSupply": sum(1 for m in metrics.values() if m["marketEligible"] and m["supplyOpen"] <= 0),
            "clampedByAnchor": sum(1 for m in metrics.values() if m["price"].get("clamped")),
            "manipulationSuspected": sum(1 for m in metrics.values() if m["manipulationSuspected"]),
        },
        "samples": {
            "general": len(general),
            "edge": len(edge),
            "composed": len(composed),
            "generalTypes": counts(general, "type"),
            "generalStatus": counts(general, "price.status"),
            "generalAccess": counts(general, "access.best"),
            "generalAbundance": counts(general, "supply.abundanceTier"),
            "generalDifficulty": counts(general, "supply.difficultyTier"),
            "generalReview": counts(general, "reviewReasons"),
            "edgeTags": counts(edge, "edgeTags"),
        },
    }


def report(data: dict[str, Any], metrics: dict[int, dict[str, Any]], general: list[dict], edge: list[dict], summary_data: dict[str, Any]) -> str:
    def rows(rows: list[dict], key: str, limit: int = 10) -> str:
        result: dict[str, int] = defaultdict(int)
        for row in rows:
            value = row
            for part in key.split("."):
                value = (value or {}).get(part)
            result[str(value)] += 1
        lines = ["| Valor | n |", "|---|---:|"]
        for value, count in sorted(result.items(), key=lambda item: (-item[1], item[0]))[:limit]:
            lines.append(f"| `{value}` | {count} |")
        return "\n".join(lines)

    synthetic_high = sorted(
        (m for m in metrics.values() if m["price"]["status"] == "synthetic"),
        key=lambda m: m["price"]["mid"],
        reverse=True,
    )[:8]
    market_conflicts = [
        m for m in metrics.values()
        if m["price"]["status"] == "market" and m["price"]["ceiling"] is not None and m["price"]["mid"] > m["price"]["ceiling"]
    ][:8]
    no_supply_high = [
        m for m in metrics.values()
        if m["price"]["status"] in ("market", "synthetic")
        and m["supplyOpen"] <= 0
        and m["price"]["mid"] >= 1_000_000
    ][:8]

    lines = [
        "# Muestra de la master de mercado",
        "",
        f"Semilla: `{summary_data['seed']}`. Los datos completos están en `general.jsonl` y `edge.jsonl`.",
        "",
        "## Fuentes y rates",
        "",
        f"- Items en la taxonomía: {summary_data['universe']['items']}",
        f"- Items con supply abierto: {summary_data['universe']['withOpenSupply']}",
        f"- Items con histórico: {summary_data['universe']['withHistory']}",
        f"- Precio `market`: {summary_data['universe']['marketPrice']}",
        f"- Precio `synthetic`: {summary_data['universe']['syntheticPrice']}",
        f"- Precio `manual`: {summary_data['universe']['manualPrice']}",
        f"- `not_applicable`: {summary_data['universe']['notApplicable']}",
        f"- `marketEligible`: {summary_data['universe']['marketEligible']}",
        f"- Clampeados por ancla: {summary_data['universe']['clampedByAnchor']}",
        f"- Manipulación sospechada: {summary_data['universe']['manipulationSuspected']}",
        "",
        "```json",
        json.dumps(summary_data["rates"], indent=2),
        "```",
        "",
        "## Spawns",
        "",
        f"Total: {summary_data['spawns']['spawns']} spawns, "
        f"{summary_data['spawns']['maps']} mapas, {summary_data['spawns']['mobs']} mobs.",
        "",
        "| Tipo de spawn | Líneas |",
        "|---|---:|",
    ]
    for key, value in summary_data["spawns"]["byType"].items():
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        "## Muestra general",
        "",
        "### Tipos",
        "",
        rows(general, "type"),
        "",
        "### Estado de precio",
        "",
        rows(general, "price.status"),
        "",
        "### Acceso",
        "",
        rows(general, "access.best"),
        "",
        "### Abundancia",
        "",
        rows(general, "supply.abundanceTier"),
        "",
        "### Dificultad",
        "",
        rows(general, "supply.difficultyTier"),
        "",
        "## Casos borde",
        "",
        "| Categoría | Items |",
        "|---|---:|",
    ]
    for key, value in summary_data["samples"]["edgeTags"].items():
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        f"Ejemplos compuestos: {summary_data['samples']['composed']} filas en `composed.jsonl`.",
        "",
        "## Señales detectadas",
        "",
    ]
    lines.append("### Sintéticos más caros")
    lines.append("")
    lines.append("| Item | Tipo | mid | supply abierto | review |")
    lines.append("|---|---|---:|---:|---|")
    for m in synthetic_high:
        lines.append(
            f"| {m['name']} | {m['type']} | {m['price']['mid']:,} | {m['supplyOpen']:.4f} | {', '.join(m['reviewReasons'])} |"
        )

    lines += ["", "### Precio de mercado por encima del techo NPC", ""]
    lines.append("| Item | mid | ceiling | fuente |")
    lines.append("|---|---:|---:|---|")
    for m in market_conflicts:
        lines.append(
            f"| {m['name']} | {m['price']['mid']:,} | {m['price']['ceiling']:,} | {m['price']['historicalSource']} |"
        )
    if not market_conflicts:
        lines.append("| (ninguno en la muestra completa) | | | |")

    lines += ["", "### Sin supply abierto y precio alto", ""]
    lines.append("| Item | mid | access | sources |")
    lines.append("|---|---:|---|---|")
    for m in no_supply_high:
        lines.append(
            f"| {m['name']} | {m['price']['mid']:,} | {m['taxonomy'].get('access', {}).get('best')} | {', '.join(m['taxonomy'].get('sources', []))} |"
        )

    lines += [
        "",
        "## Decisiones aplicadas en esta muestra",
        "",
        "- `supplyOpen` excluye boss, instancia, guild, quest y event; usa field + dungeon.",
        "- El HP efectivo aplica `monster_hp_rate`/`mvp_hp_rate` (2x).",
        "- El precio sintético usa type_p40 + supply/demanda/dificultad + factor de fuente (group 0.60-0.70, craft 0.90, quest/instancia 0.80, sin fuente 0.50) + factor de grupo + factor de equipo.",
        "- Items sin fuente usan min(type_p10, 1M) * 0.50; los sintéticos con fuente se capan a type_p90.",
        "- La demanda combina LATAM y Atlantis ponderando por log1p(total_sold).",
        "- Los objetos compuestos se calculan con components.yml y valuation.py.",
        "- `npcBuyPrice`: sintético 45% del mid con cap de 50% de la mediana del tipo; market high 75%; medium 60% con cap de 1 mediana; low 45% / low 75%; manipulación 35% / low 70%.",
        "- `npcSellPrice` usa margen y se limita a 1.10–1.50x del `npcBuyPrice`.",
        "- La manipulación se marca con CV > 3 o `atlantis_extreme_max`, sin listas de excepciones.",
        "- Los tags vienen de categorías de taxonomía + restricciones de acceso.",
        "",
    ]
    return "\n".join(lines)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> None:
    global EDGE_PER_CATEGORY
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    parser.add_argument("--general-size", type=int, default=GENERAL_SIZE)
    parser.add_argument("--edge-per-category", type=int, default=EDGE_PER_CATEGORY)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    EDGE_PER_CATEGORY = args.edge_per_category

    data = load_inputs()
    metrics = build_metrics(data)
    build_prices(data, metrics)
    apply_craft_costs(metrics)

    general_population = sorted(item_id for item_id, metric in metrics.items() if metric["marketEligible"])
    rng = random.Random(args.seed)
    general_ids = rng.sample(general_population, min(args.general_size, len(general_population)))
    general = []
    for item_id in general_ids:
        row = serialize(metrics[item_id])
        row["sampleKind"] = "general"
        general.append(row)
    edge = choose_edge(metrics)
    composed = build_composed(metrics)

    summary_data = summary(data, metrics, general, edge, composed)
    args.out.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.out / "general.jsonl", general)
    write_jsonl(args.out / "edge.jsonl", edge)
    write_jsonl(args.out / "composed.jsonl", composed)
    (args.out / "summary.json").write_text(
        json.dumps(summary_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.out / "REPORT.md").write_text(report(data, metrics, general, edge, summary_data), encoding="utf-8")

    print(f"wrote {len(general)} general, {len(edge)} edge and {len(composed)} composed samples -> {args.out}")
    print(f"items: {len(metrics)}, open supply: {summary_data['universe']['withOpenSupply']}, "
          f"market: {summary_data['universe']['marketPrice']}, synthetic: {summary_data['universe']['syntheticPrice']}")


if __name__ == "__main__":
    main()
