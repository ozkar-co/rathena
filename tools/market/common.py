"""Shared loaders for the OzRo market master samples.

The taxonomy is an intermediate artifact: it provides item identity, sources
and access tags. This module adds the canonical server state (rates, HP, spawns)
and the historical market snapshot needed to estimate prices.
"""
from __future__ import annotations

import bisect
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ROOT = TOOLS.parent
SITE = ROOT.parent / "ozro-site"
TAXONOMY = SITE / "assets" / "items" / "taxonomy.json"
MASTER_LIST = ROOT.parent / "ragnabots" / "staging" / "market" / "pricing" / "master_list.json"
BATTLE_CONF = ROOT / "conf/import/battle_conf.txt"
CANON = ROOT / "data" / "market" / "canon.yml"
SPAWN_CONF = "npc/re/scripts_main.conf"

ITEM_FILES = [
    ROOT / "db/re/item_db.yml",
    ROOT / "db/re/item_db_equip.yml",
    ROOT / "db/re/item_db_etc.yml",
    ROOT / "db/re/item_db_usable.yml",
    ROOT / "db/import/item_db.yml",
]
MOB_FILES = [ROOT / "db/re/mob_db.yml", ROOT / "db/import/mob_db.yml"]

sys.path.insert(0, str(TOOLS))
import mob_spawns  # noqa: E402


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace")) or {}


def body(path: Path) -> list[dict[str, Any]]:
    return load_yaml(path).get("Body") or []


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_aegis(value: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", value.lower())


def load_taxonomy() -> dict[str, Any]:
    return json.loads(TAXONOMY.read_text(encoding="utf-8"))


def load_canon() -> dict[str, Any]:
    if not CANON.exists():
        return {}
    return yaml.safe_load(CANON.read_text(encoding="utf-8")) or {}


def load_master_list() -> dict[int, dict[str, Any]]:
    if not MASTER_LIST.exists():
        return {}
    rows = json.loads(MASTER_LIST.read_text(encoding="utf-8"))
    return {as_int(row.get("item_id"), -1): row for row in rows if as_int(row.get("item_id"), -1) >= 0}


def load_battle_config() -> dict[str, int]:
    values: dict[str, int] = {}
    if not BATTLE_CONF.exists():
        return values
    for raw in BATTLE_CONF.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("//", 1)[0].strip()
        match = re.match(r"([A-Za-z0-9_.]+):\s*(-?\d+)", line)
        if match:
            values[match.group(1)] = int(match.group(2))
    return values


def load_items() -> dict[int, dict[str, Any]]:
    items: dict[int, dict[str, Any]] = {}
    for path in ITEM_FILES:
        for row in body(path):
            item_id = as_int(row.get("Id"), -1)
            if item_id < 0:
                continue
            raw_buy = row.get("Buy")
            raw_sell = row.get("Sell")
            buy = as_int(raw_buy) if raw_buy is not None else as_int(raw_sell) * 2
            sell = as_int(raw_sell) if raw_sell is not None else buy // 2
            items[item_id] = {
                "id": item_id,
                "aegis": str(row.get("AegisName") or ""),
                "name": str(row.get("Name") or row.get("AegisName") or ""),
                "type": str(row.get("Type") or "Etc"),
                "buy": buy,
                "sell": sell,
                "slots": as_int(row.get("Slots")),
                "refineable": bool(row.get("Refineable")),
                "attack": as_int(row.get("Attack")),
                "defense": as_int(row.get("Defense")),
                "equipLevelMin": as_int(row.get("EquipLevelMin")),
                "custom": path == ROOT / "db/import/item_db.yml",
            }
    return items


def load_mobs() -> dict[int, dict[str, Any]]:
    mobs: dict[int, dict[str, Any]] = {}
    for path in MOB_FILES:
        for row in body(path):
            mob_id = as_int(row.get("Id"), -1)
            if mob_id >= 0:
                mobs[mob_id] = row
    return mobs


def load_drop_sources(
    taxonomy: dict[str, Any],
    items: dict[int, dict[str, Any]],
    mobs: dict[int, dict[str, Any]],
) -> dict[int, dict[int, dict[str, Any]]]:
    aegis_to_id: dict[str, int] = {}
    for item in items.values():
        if item["aegis"]:
            aegis_to_id[normalize_aegis(item["aegis"])] = item["id"]
    for key, meta in taxonomy["items"].items():
        if meta.get("aegis"):
            aegis_to_id.setdefault(normalize_aegis(str(meta["aegis"])), as_int(key, -1))

    sources: dict[int, dict[int, dict[str, Any]]] = defaultdict(dict)
    for mob_id, row in mobs.items():
        for field, kind in (("Drops", "normal"), ("MvpDrops", "mvp")):
            for drop in row.get(field) or []:
                item_id = aegis_to_id.get(normalize_aegis(str(drop.get("Item") or "")))
                if item_id is None:
                    continue
                rate = as_int(drop.get("Rate"))
                entry = sources[item_id].setdefault(
                    mob_id, {"normal": False, "mvp": False, "rate": 0}
                )
                entry[kind] = True
                entry["rate"] = max(entry["rate"], rate)
    return sources


def classify_map(map_name: str, instance_maps: set[str]) -> str:
    if (
        map_name in instance_maps
        or map_name.startswith("@")
        or re.match(r"^\d+@", map_name)
        or map_name.endswith("_i")
    ):
        return "instance"
    if map_name.startswith("gld"):
        return "guild"
    if map_name.startswith(("evt", "event", "quiz")):
        return "event"
    if map_name.startswith(("que_", "job_", "job3_")):
        return "quest"
    if "fild" in map_name or map_name.endswith("_field") or map_name.startswith(("mjolnir_", "moro_vol")):
        return "field"
    if "dun" in map_name or "maze" in map_name or re.search(r"_d\d", map_name):
        return "dungeon"
    if map_name.startswith(
        (
            "abbey",
            "catacomb",
            "thr_",
            "anthell",
            "treasure",
            "gefenia",
            "odin_tem",
            "thor_v",
            "abyss",
            "c_tower",
            "juperos",
            "jupe_",
            "tha_t",
            "gl_",
            "yggdrasil",
            "kh_kiehl",
        )
    ):
        return "dungeon"
    return "other"


def load_spawns() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = str(ROOT)
    files = mob_spawns.resolve_script_files(root, SPAWN_CONF)
    mob_names, _ = mob_spawns.load_mob_names(root, None)
    instance_maps = mob_spawns.load_instance_maps(root)
    spawns, errors, unresolved = mob_spawns.parse_spawns(files, root, mob_names)
    for spawn in spawns:
        spawn["mapType"] = classify_map(spawn["map"], instance_maps)
        spawn["spawnType"] = "boss" if spawn["boss"] else spawn["mapType"]
    report = {
        "files": len(files),
        "spawns": len(spawns),
        "maps": len({spawn["map"] for spawn in spawns}),
        "mobs": len({spawn["mobId"] for spawn in spawns}),
        "parseErrors": errors,
        "unresolvedMobs": dict(unresolved),
        "byType": dict(sorted(_count(spawn["spawnType"] for spawn in spawns).items())),
    }
    return spawns, report


def _count(values) -> dict[str, int]:
    result: dict[str, int] = defaultdict(int)
    for value in values:
        result[str(value)] += 1
    return result


def spawns_by_mob(spawns: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for spawn in spawns:
        grouped[spawn["mobId"]].append(spawn)
    return grouped


RATE_CATEGORY = {
    "Healing": "heal",
    "Usable": "use",
    "DelayConsume": "use",
    "Cash": "use",
    "Weapon": "equip",
    "Armor": "equip",
    "ShadowGear": "equip",
    "Shadowgear": "equip",
    "Ammo": "equip",
    "Card": "card",
}
ACCESS_FACTOR = {
    "field": 1.0,
    "dungeon": 0.85,
    "quest": 0.40,
    "instance": 0.15,
    "guild": 0.10,
    "event": 0.0,
    "other": 0.50,
}


def rate_multiplier(rates: dict[str, int], item_type: str, is_boss: bool, is_mvp: bool) -> int:
    category = RATE_CATEGORY.get(item_type, "common")
    if is_mvp:
        if category == "card":
            return rates.get("item_rate_card_mvp", rates.get("item_rate_mvp", 100))
        return rates.get("item_rate_mvp", 100)
    if is_boss:
        return rates.get(f"item_rate_{category}_boss", rates.get(f"item_rate_{category}", 100))
    return rates.get(f"item_rate_{category}", 100)


def effective_rate(
    rates: dict[str, int], item_type: str, base_rate: int, is_boss: bool, is_mvp: bool
) -> float:
    mult = rate_multiplier(rates, item_type, is_boss, is_mvp)
    return min(10000, base_rate * mult // 100) / 10000


def effective_hp(mob: dict[str, Any], rates: dict[str, int]) -> int:
    raw = as_int(mob.get("Hp"))
    rate = rates.get("mvp_hp_rate", 100) if str(mob.get("Class") or "") == "Boss" else rates.get("monster_hp_rate", 100)
    return raw * rate // 100


def threat(mob: dict[str, Any], rates: dict[str, int], is_boss: bool) -> float:
    hp = effective_hp(mob, rates)
    defense = as_int(mob.get("Defense"))
    magic_defense = as_int(mob.get("MagicDefense"))
    level = as_int(mob.get("Level"))
    return (
        math.log1p(max(0, hp))
        * (1 + defense / 100 + magic_defense / 200)
        * (1 + 0.5 * (1 if is_boss else 0))
        * (1 + 0.2 * max(0, level - 100) / 50)
    )


def percentile_rank(sorted_values: list[float], value: float | None) -> float | None:
    if value is None or not sorted_values:
        return None
    idx = bisect.bisect_left(sorted_values, value)
    return 100.0 * idx / len(sorted_values)


def tier_from_percentile(percentile: float | None, bands: list[tuple[float, str]], default: str = "unknown") -> str:
    if percentile is None:
        return default
    for limit, name in bands:
        if percentile < limit:
            return name
    return bands[-1][1]


def median(values: list[float]) -> float:
    return statistics_median(values)


def statistics_median(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    key = (len(ordered) - 1) * p
    low = int(key)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (key - low)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def round_price(value: float) -> int:
    value = max(1.0, value)
    if value < 1000:
        return int(round(value))
    if value < 100_000:
        return int(round(value / 100) * 100)
    if value < 1_000_000:
        return int(round(value / 1_000) * 1_000)
    return int(round(value / 10_000) * 10_000)
