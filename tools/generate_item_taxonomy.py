#!/usr/bin/env python3
"""Build an item taxonomy for OzRo from the active rAthena database and scripts.

The output is consumed by the website as a source of truth for future custom
NPCs, quests and item filters. It is intentionally conservative: an item is
marked as unobtainable only when no direct source (drop, shop, cash shop,
quest/instance/NPC reward, crafting or item group/package) is known.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT.parent / "ozro-site" / "assets" / "items" / "taxonomy.json"
MASTER_LIST = ROOT.parent / "ragnabots" / "staging" / "market" / "pricing" / "master_list.json"
SPAWNS = ROOT.parent / "ozro-site" / "assets" / "spawns" / "spawns.json"
ITEMINFO = ROOT.parent / "ozro-site" / "data" / "itemInfo_EN.lua"
IMAGE_INDEX = ROOT.parent / "ozro-site" / "assets" / "items" / "item-images.json"

ITEM_FILES = [
    ROOT / "db/re/item_db.yml",
    ROOT / "db/re/item_db_equip.yml",
    ROOT / "db/re/item_db_etc.yml",
    ROOT / "db/re/item_db_usable.yml",
    ROOT / "db/import/item_db.yml",
]
MOB_FILES = [ROOT / "db/re/mob_db.yml", ROOT / "db/import/mob_db.yml"]
MAP_DROP_FILES = [ROOT / "db/re/map_drops.yml", ROOT / "db/import/map_drops.yml"]
SKILL_FILES = [ROOT / "db/re/skill_db.yml", ROOT / "db/import/skill_db.yml"]
INSTANCE_FILES = [ROOT / "db/re/instance_db.yml", ROOT / "db/import/instance_db.yml"]
CASH_FILES = [ROOT / "db/re/item_cash.yml", ROOT / "db/import/item_cash.yml"]
GROUP_FILES = [ROOT / "db/re/item_group_db.yml", ROOT / "db/import/item_group_db.yml"]
PACKAGE_FILES = [ROOT / "db/re/item_packages.yml", ROOT / "db/import/item_packages.yml"]
COMBO_FILES = [ROOT / "db/re/item_combos.yml", ROOT / "db/import/item_combos.yml"]
LAPHINE_FILES = [ROOT / "db/re/laphine_synthesis.yml", ROOT / "db/import/laphine_synthesis.yml"]
PRODUCE_FILES = [ROOT / "db/re/produce_db.txt", ROOT / "db/import/produce_db.txt"]

EQUIP_TYPES = {"Weapon", "Armor", "ShadowGear", "Shadowgear"}
CONSUMABLE_TYPES = {"Usable", "Healing", "DelayConsume", "Cash"}
ITEM_ARG_COMMANDS = (
    "getitem",
    "getitem2",
    "getitem3",
    "getitem4",
    "getitem5",
    "getitembound",
    "getitembound2",
    "getitembound3",
    "getitempackage",
    "getgroupitem",
    "delitem",
    "countitem",
    "checkitem",
    "consumeitem",
)
ITEM_ARG_RE = re.compile(
    r"\b(" + "|".join(ITEM_ARG_COMMANDS) + r")\s*\(?\s*([^,;\n)]+)",
    re.IGNORECASE,
)
SHOP_RE = re.compile(r"\b(shop|itemshop|pointshop|marketshop|cashshop)\b", re.IGNORECASE)
SHOP_ITEM_RE = re.compile(r"(\d+)\s*:\s*-?\d+")
# A drop source above this effective HP is flagged as a hard source. This is a
# rule, not an item allow/deny list: the flag is exposed in the item metadata so
# consumers (NPCs, quests, market tools) can decide what to do with it.
HIGH_HP_THRESHOLD = 10_000_000
BATTLE_CONF = ROOT / "conf/import/battle_conf.txt"


def load_hp_rates() -> dict[str, int]:
    rates = {"monster_hp_rate": 100, "mvp_hp_rate": 100}
    if not BATTLE_CONF.exists():
        return rates
    for raw in BATTLE_CONF.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("//", 1)[0].strip()
        match = re.match(r"(monster_hp_rate|mvp_hp_rate):\s*(\d+)", line)
        if match:
            rates[match.group(1)] = int(match.group(2))
    return rates


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace")) or {}


def body(path: Path) -> list[dict[str, Any]]:
    data = load_yaml(path)
    return data.get("Body") or []


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def normalize_aegis(value: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", value.lower())


def lookup_item(name: str, aegis_map: dict[str, int], display_map: dict[str, int]) -> int | None:
    return aegis_map.get(normalize_aegis(name)) or display_map.get(normalize(name))


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def resolve_config(path: Path, seen: set[Path], files: list[Path]) -> None:
    path = path.resolve()
    if path in seen or not path.exists():
        return
    seen.add(path)
    if path.suffix != ".conf":
        files.append(path)
        return

    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        match = re.match(r"(npc|import):\s*(\S+)", line)
        if match:
            resolve_config(ROOT / match.group(2), seen, files)


def active_script_files() -> list[Path]:
    files: list[Path] = []
    resolve_config(ROOT / "npc/re/scripts_main.conf", set(), files)
    return files


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
            trade = row.get("Trade") or {}
            items[item_id] = {
                "id": item_id,
                "aegis": str(row.get("AegisName") or ""),
                "name": str(row.get("Name") or row.get("AegisName") or ""),
                "type": str(row.get("Type") or "Etc"),
                "buy": buy,
                "sell": sell,
                "script": bool(row.get("Script")),
                "custom": path == ROOT / "db/import/item_db.yml",
                "untradeable": bool(trade.get("NoSell") or trade.get("NoTrade") or trade.get("NoDrop")),
            }
    return items


def load_name_maps(items: dict[int, dict[str, Any]]) -> tuple[dict[str, int], dict[str, int]]:
    aegis_map: dict[str, int] = {}
    display_map: dict[str, int] = {}
    for item in items.values():
        if item["aegis"]:
            aegis_map.setdefault(normalize_aegis(item["aegis"]), item["id"])
        if item["name"]:
            display_map.setdefault(normalize(item["name"]), item["id"])
    return aegis_map, display_map


def parse_drops(rows: Iterable[dict[str, Any]], aegis_map: dict[str, int]) -> dict[int, dict[str, Any]]:
    drops: dict[int, dict[str, Any]] = {}
    for row in rows:
        for field, kind in (("Drops", "normal"), ("MvpDrops", "mvp")):
            for drop in row.get(field) or []:
                name = str(drop.get("Item") or "")
                item_id = aegis_map.get(normalize_aegis(name))
                if item_id is None:
                    continue
                entry = drops.setdefault(
                    item_id,
                    {
                        "mobs": set(),
                        "normal_mobs": set(),
                        "mvp_mobs": set(),
                        "mvp": False,
                        "maps": set(),
                    },
                )
                entry["mobs"].add(as_int(row.get("Id"), -1))
                entry["mvp"] = entry["mvp"] or kind == "mvp"
                if kind == "mvp":
                    entry["mvp_mobs"].add(as_int(row.get("Id"), -1))
                else:
                    entry["normal_mobs"].add(as_int(row.get("Id"), -1))
    return drops


def is_instance_like(map_name: str, instance_maps: set[str]) -> bool:
    if map_name in instance_maps:
        return True
    # Instance copies of fields/dungeons end in "_i"; instance dungeons use "N@".
    return map_name.endswith("_i") or (map_name[:1].isdigit() and "@" in map_name)


def load_spawns(instance_maps: set[str]) -> tuple[dict[int, set[str]], dict[str, str]]:
    mob_maps: dict[int, set[str]] = defaultdict(set)
    map_kind: dict[str, str] = {}
    if not SPAWNS.exists():
        return mob_maps, map_kind

    data = json.loads(SPAWNS.read_text(encoding="utf-8"))
    for spawn in data.get("spawns", []):
        map_name = str(spawn.get("map") or "")
        mob_id = as_int(spawn.get("mobId"), -1)
        if mob_id < 0 or not map_name:
            continue
        mob_maps[mob_id].add(map_name)
        if map_name.startswith("gld"):
            map_kind[map_name] = "guild"
        elif is_instance_like(map_name, instance_maps):
            map_kind[map_name] = "instance"
        else:
            map_kind[map_name] = "normal"
    return mob_maps, map_kind


def load_instance_maps() -> set[str]:
    maps: set[str] = set()
    for path in INSTANCE_FILES:
        for row in body(path):
            enter = row.get("Enter") or {}
            if enter.get("Map"):
                maps.add(str(enter["Map"]))
            for map_name in (row.get("AdditionalMaps") or {}):
                maps.add(str(map_name))
    return maps


def load_map_drops(aegis_map: dict[str, int]) -> dict[int, set[str]]:
    drops: dict[int, set[str]] = defaultdict(set)
    for path in MAP_DROP_FILES:
        for row in body(path):
            map_name = str(row.get("Map") or "")
            for field in ("GlobalDrops", "SpecificDrops"):
                value = row.get(field)
                if field == "GlobalDrops":
                    for drop in value or []:
                        item_id = aegis_map.get(normalize_aegis(str(drop.get("Item") or "")))
                        if item_id is not None:
                            drops[item_id].add(map_name)
                else:
                    for specific in value or []:
                        for drop in specific.get("Drops") or []:
                            item_id = aegis_map.get(normalize_aegis(str(drop.get("Item") or "")))
                            if item_id is not None:
                                drops[item_id].add(map_name)
    return drops


def load_skill_costs(aegis_map: dict[str, int]) -> dict[int, set[str]]:
    costs: dict[int, set[str]] = defaultdict(set)
    for path in SKILL_FILES:
        for row in body(path):
            skill_name = str(row.get("Name") or row.get("AegisName") or "")
            for cost in (row.get("Requires") or {}).get("ItemCost") or []:
                item_id = aegis_map.get(normalize_aegis(str(cost.get("Item") or "")))
                if item_id is not None:
                    costs[item_id].add(skill_name)
    return costs


def load_cash(aegis_map: dict[str, int]) -> set[int]:
    items: set[int] = set()
    for path in CASH_FILES:
        for tab in body(path):
            for entry in tab.get("Items") or []:
                item_id = aegis_map.get(normalize_aegis(str(entry.get("Item") or "")))
                if item_id is not None:
                    items.add(item_id)
    return items


def load_groups(aegis_map: dict[str, int]) -> tuple[set[int], dict[str, set[int]]]:
    members: set[int] = set()
    by_name: dict[str, set[int]] = defaultdict(set)
    for path in GROUP_FILES:
        for group in body(path):
            group_name = str(group.get("Group") or "")
            for subgroup in group.get("SubGroups") or []:
                for entry in subgroup.get("List") or []:
                    item_id = aegis_map.get(normalize_aegis(str(entry.get("Item") or "")))
                    if item_id is not None:
                        members.add(item_id)
                        by_name[group_name].add(item_id)
    return members, by_name


def load_packages(aegis_map: dict[str, int]) -> set[int]:
    members: set[int] = set()
    for path in PACKAGE_FILES:
        for package in body(path):
            for group in package.get("Groups") or []:
                for entry in group.get("Items") or []:
                    item_id = aegis_map.get(normalize_aegis(str(entry.get("Item") or "")))
                    if item_id is not None:
                        members.add(item_id)
    return members


def load_combos(aegis_map: dict[str, int]) -> set[int]:
    items: set[int] = set()
    for path in COMBO_FILES:
        for row in body(path):
            for combo in row.get("Combos") or []:
                for name in combo.get("Combo") or []:
                    item_id = aegis_map.get(normalize_aegis(str(name)))
                    if item_id is not None:
                        items.add(item_id)
    return items


def load_laphine(aegis_map: dict[str, int], groups: dict[str, set[int]]) -> tuple[set[int], set[int]]:
    materials: set[int] = set()
    rewards: set[int] = set()
    for path in LAPHINE_FILES:
        for row in body(path):
            trigger = aegis_map.get(normalize_aegis(str(row.get("Item") or "")))
            if trigger is not None:
                materials.add(trigger)
            for req in row.get("Requirements") or []:
                item_id = aegis_map.get(normalize_aegis(str(req.get("Item") or "")))
                if item_id is not None:
                    materials.add(item_id)
            rewards |= groups.get(str(row.get("RewardGroup") or ""), set())
    return materials, rewards


def load_produce() -> tuple[set[int], set[int]]:
    outputs: set[int] = set()
    materials: set[int] = set()
    for path in PRODUCE_FILES:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.split("//", 1)[0].strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split(",")]
            if len(parts) < 6:
                continue
            output = as_int(parts[1])
            if output > 0:
                outputs.add(output)
            for index in range(5, len(parts) - 1, 2):
                item_id = as_int(parts[index])
                if item_id > 0:
                    materials.add(item_id)
    return outputs, materials


def script_references(
    files: list[Path],
    aegis_map: dict[str, int],
    display_map: dict[str, int],
    item_ids: set[int],
) -> dict[str, set[int]]:
    refs: dict[str, set[int]] = defaultdict(set)
    for path in files:
        rel = str(path.relative_to(ROOT)).lower()
        if "/instances/" in rel:
            kind = "instance"
        elif "/quests/" in rel or "/custom/ozro/" in rel:
            kind = "quest"
        else:
            kind = "npc"

        text = path.read_text(encoding="latin-1", errors="replace")
        for raw_line in text.splitlines():
            line = raw_line.split("//", 1)[0]
            if not line.strip():
                continue
            for match in ITEM_ARG_RE.finditer(line):
                command = match.group(1).lower()
                arg = match.group(2).strip().strip("\"'")
                if not arg or arg[0] in ".@$#":
                    continue
                item_id: int | None = None
                if arg.isdigit():
                    item_id = int(arg)
                else:
                    item_id = lookup_item(arg, aegis_map, display_map)
                if item_id is None:
                    continue
                refs[f"{kind}_refs"].add(item_id)
                if command.startswith("getitem"):
                    refs[f"{kind}_rewards"].add(item_id)
                if command in {"delitem", "countitem", "checkitem", "consumeitem"}:
                    refs[f"{kind}_requirements"].add(item_id)

            if SHOP_RE.search(line):
                for shop_match in SHOP_ITEM_RE.finditer(line):
                    refs["shop_refs"].add(int(shop_match.group(1)))

        for match in re.finditer(r"\bcallsub\s+S_Make\b(.*?);", text, re.IGNORECASE | re.DOTALL):
            for token in re.findall(r"\b(\d+)\b", match.group(1)):
                item_id = int(token)
                if item_id in item_ids:
                    refs["npc_refs"].add(item_id)
                    refs["craft_material_refs"].add(item_id)
    return refs


def classify_map(map_name: str, map_kind: dict[str, str], instance_maps: set[str]) -> str:
    if is_instance_like(map_name, instance_maps) or map_kind.get(map_name) == "instance":
        return "instance"
    if map_name.startswith("gld"):
        return "guild"
    return "normal"


def load_image_index() -> dict[int, dict[str, bool]]:
    if not IMAGE_INDEX.exists():
        return {}
    raw = json.loads(IMAGE_INDEX.read_text(encoding="utf-8"))
    result: dict[int, dict[str, bool]] = {}
    for key, value in raw.items():
        try:
            result[int(key)] = value
        except (TypeError, ValueError):
            continue
    return result


def load_unidentified_items() -> set[int]:
    if not ITEMINFO.exists():
        return set()
    data = ITEMINFO.read_bytes()
    result: set[int] = set()
    for match in re.finditer(rb"\[(\d+)\]\s*=\s*\{(.*?)\n\t\}", data, re.S):
        name = re.search(rb'identifiedDisplayName\s*=\s*"([^"]*)"', match.group(2))
        if name and name.group(1).decode("latin1").lower().startswith("unidentified"):
            result.add(int(match.group(1)))
    return result


def access_info(
    item_id: int,
    source_kinds: set[str],
    drops: dict[int, dict[str, Any]],
    map_drops: dict[int, set[str]],
    mob_maps: dict[int, set[str]],
    map_kind: dict[str, str],
    instance_maps: set[str],
    mob_meta: dict[int, dict[str, Any]],
    high_hp_threshold: int,
) -> dict[str, Any]:
    """Classify an item's access and farmability from its sources.

    This is metadata, not a category: an item can carry several restriction tags
    at once, and the consumer decides which ones matter.
    """
    drop_entry = drops.get(item_id, {})
    drop_mobs = drop_entry.get("mobs", set())
    mvp_mobs = drop_entry.get("mvp_mobs", set())
    spawn_mobs = {mob_id for mob_id in drop_mobs if mob_maps.get(mob_id)}
    drop_maps = set(drop_entry.get("maps", set())) | set(map_drops.get(item_id, set()))

    map_classes: dict[str, set[str]] = {"normal": set(), "guild": set(), "instance": set()}
    for map_name in drop_maps:
        map_classes[classify_map(map_name, map_kind, instance_maps)].add(map_name)

    normal_maps = map_classes["normal"]
    guild_maps = map_classes["guild"]
    instance_drop_maps = map_classes["instance"]

    # Use the easiest source with a known spawn. An item with one hard mob and
    # one easy mob is not a hard item; the player can farm the easy one.
    source_mobs = spawn_mobs or drop_mobs
    hp_values = [
        as_int(mob_meta.get(mob_id, {}).get("hp_effective"))
        for mob_id in source_mobs
        if as_int(mob_meta.get(mob_id, {}).get("hp_effective")) > 0
    ]
    level_values = [
        as_int(mob_meta.get(mob_id, {}).get("level"))
        for mob_id in source_mobs
        if as_int(mob_meta.get(mob_id, {}).get("level")) > 0
    ]
    min_hp = min(hp_values) if hp_values else None
    max_hp = max(hp_values) if hp_values else None
    min_level = min(level_values) if level_values else None
    max_level = max(level_values) if level_values else None

    boss_only = bool(drop_mobs) and all(
        mob_id in mvp_mobs or str(mob_meta.get(mob_id, {}).get("class") or "") == "Boss"
        for mob_id in drop_mobs
    )
    no_spawn = bool(drop_mobs) and not spawn_mobs
    high_hp = bool(min_hp and min_hp >= high_hp_threshold)
    high_hp_source = bool(max_hp and max_hp >= high_hp_threshold)

    if normal_maps:
        farm_access = "normal"
    elif guild_maps:
        farm_access = "guild"
    elif instance_drop_maps:
        farm_access = "instance"
    elif drop_mobs:
        farm_access = "unknown"
    elif "npc_shop" in source_kinds:
        farm_access = "npc"
    elif "cash_shop" in source_kinds:
        farm_access = "cash"
    elif "craft" in source_kinds:
        farm_access = "craft"
    elif "quest_reward" in source_kinds:
        farm_access = "quest"
    elif source_kinds & {"group", "package"}:
        farm_access = "group"
    else:
        farm_access = "none"

    restrictions: list[str] = []
    if not normal_maps:
        if guild_maps:
            restrictions.append("guild_only")
        elif instance_drop_maps:
            restrictions.append("instance_only")
        elif drop_mobs and no_spawn:
            restrictions.append("no_spawn")
        elif drop_mobs:
            restrictions.append("unknown_spawn")
    if boss_only:
        restrictions.append("boss_only")
    if high_hp:
        restrictions.append("high_hp")
    elif high_hp_source:
        restrictions.append("high_hp_source")
    if "quest_reward" in source_kinds:
        restrictions.append("quest_source")
    if "instance_reward" in source_kinds:
        restrictions.append("instance_source")

    return {
        "best": farm_access,
        "normalMaps": len(normal_maps),
        "guildMaps": len(guild_maps),
        "instanceMaps": len(instance_drop_maps),
        "dropMobs": len(drop_mobs),
        "spawnMobs": len(spawn_mobs),
        "bossOnly": boss_only,
        "minMobHp": min_hp,
        "maxMobHp": max_hp,
        "minMobLevel": min_level,
        "maxMobLevel": max_level,
        "highHp": high_hp,
        "highHpSource": high_hp_source,
        "noSpawn": no_spawn,
        "restrictions": restrictions,
        # Rule used by market/NPC tools: normal spawn, non-boss, and at least
        # one source below the high-HP threshold. It is exposed as data so the
        # policy can change without reclassifying items by hand.
        "commonFarmEligible": bool(normal_maps) and not boss_only and not high_hp,
    }


def build_taxonomy(high_hp_threshold: int = HIGH_HP_THRESHOLD) -> dict[str, Any]:
    items = load_items()
    aegis_map, display_map = load_name_maps(items)
    instance_maps = load_instance_maps()
    mob_maps, map_kind = load_spawns(instance_maps)

    mobs = {}
    for path in MOB_FILES:
        for row in body(path):
            mob_id = as_int(row.get("Id"), -1)
            if mob_id >= 0:
                mobs[mob_id] = row
    hp_rates = load_hp_rates()
    mob_meta = {}
    for mob_id, row in mobs.items():
        raw_hp = as_int(row.get("Hp"))
        monster_class = str(row.get("Class") or "")
        hp_rate = hp_rates["mvp_hp_rate"] if monster_class == "Boss" else hp_rates["monster_hp_rate"]
        mob_meta[mob_id] = {
            "level": as_int(row.get("Level")),
            "hp": raw_hp,
            "hp_effective": raw_hp * hp_rate // 100,
            "class": monster_class,
        }
    drops = parse_drops(mobs.values(), aegis_map)
    map_drops = load_map_drops(aegis_map)

    for item_id, entry in drops.items():
        for mob_id in entry["mobs"]:
            for map_name in mob_maps.get(mob_id, set()):
                entry["maps"].add(map_name)

    skills = load_skill_costs(aegis_map)
    cash = load_cash(aegis_map)
    group_members, groups = load_groups(aegis_map)
    package_members = load_packages(aegis_map)
    combos = load_combos(aegis_map)
    laphine_materials, laphine_rewards = load_laphine(aegis_map, groups)
    produce_outputs, produce_materials = load_produce()
    script_refs = script_references(active_script_files(), aegis_map, display_map, set(items))
    image_index = load_image_index()
    unidentified_items = load_unidentified_items()

    master_npc: set[int] = set()
    master_prices: dict[int, int] = {}
    if MASTER_LIST.exists():
        master = json.loads(MASTER_LIST.read_text(encoding="utf-8"))
        for row in master:
            item_id = as_int(row.get("item_id"), -1)
            if item_id < 0:
                continue
            server = row.get("server") or {}
            if server.get("npc_buyable"):
                master_npc.add(item_id)
            price = (row.get("price") or {}).get("reference")
            if price is not None:
                master_prices[item_id] = as_int(price)

    categories: dict[str, set[int]] = defaultdict(set)
    item_meta: dict[str, dict[str, Any]] = {}

    quest_referenced = script_refs.get("quest_refs", set())
    instance_referenced = script_refs.get("instance_refs", set())
    npc_referenced = script_refs.get("npc_refs", set())
    quest_rewards = script_refs.get("quest_rewards", set())
    instance_rewards = script_refs.get("instance_rewards", set())
    npc_rewards = script_refs.get("npc_rewards", set())
    script_craft_materials = script_refs.get("craft_material_refs", set())
    shop_refs = script_refs.get("shop_refs", set()) | master_npc

    for item_id, item in items.items():
        source_kinds: set[str] = set()
        drop_kind: set[str] = set()
        if item_id in drops:
            source_kinds.add("mob_drop")
            for map_name in drops[item_id]["maps"]:
                drop_kind.add(classify_map(map_name, map_kind, instance_maps))
        if item_id in map_drops:
            source_kinds.add("map_drop")
            for map_name in map_drops[item_id]:
                drop_kind.add(classify_map(map_name, map_kind, instance_maps))
        if item_id in shop_refs:
            source_kinds.add("npc_shop")
        if item_id in cash:
            source_kinds.add("cash_shop")
        if item_id in quest_rewards:
            source_kinds.add("quest_reward")
        if item_id in instance_rewards:
            source_kinds.add("instance_reward")
        if item_id in npc_rewards:
            source_kinds.add("script_reward")
        if item_id in produce_outputs or item_id in laphine_rewards:
            source_kinds.add("craft")
        if item_id in group_members:
            source_kinds.add("group")
        if item_id in package_members:
            source_kinds.add("package")

        drop_sources = source_kinds & {"mob_drop", "map_drop"}
        if drop_sources:
            if "normal" in drop_kind:
                source_kinds.add("normal_drop")
            if "guild" in drop_kind:
                source_kinds.add("guild_drop")
            if "instance" in drop_kind:
                source_kinds.add("instance_drop")
            if not drop_kind:
                source_kinds.add("unknown_drop")

        access = access_info(
            item_id,
            source_kinds,
            drops,
            map_drops,
            mob_maps,
            map_kind,
            instance_maps,
            mob_meta,
            high_hp_threshold,
        )

        direct_sources = source_kinds - {"group", "package"}
        references = {
            "quest": item_id in quest_referenced,
            "instance": item_id in instance_referenced,
            "npc": item_id in npc_referenced,
        }
        scripted = item["script"]
        skill_cost = item_id in skills
        in_combo = item_id in combos
        craft_material = (
            item_id in produce_materials
            or item_id in laphine_materials
            or item_id in script_craft_materials
        )
        npc_shop = item_id in shop_refs

        used_by_content = (
            any(references.values())
            or scripted
            or skill_cost
            or in_combo
            or craft_material
            or npc_shop
            or item_id in cash
        )
        used = used_by_content or item_id in group_members or item_id in package_members

        is_unobtainable = not direct_sources and item_id not in group_members and item_id not in package_members
        only_restricted = bool(source_kinds) and source_kinds <= {
            "mob_drop",
            "map_drop",
            "instance_drop",
            "instance_reward",
            "quest_reward",
            "unknown_drop",
        }
        drop_only_restricted = bool(drop_sources) and drop_kind <= {"instance", "guild"} and source_kinds <= {
            "mob_drop",
            "map_drop",
            "instance_drop",
            "guild_drop",
        }
        instance_or_guild_drop_only = drop_only_restricted and bool(drop_kind & {"instance", "guild"})
        quest_only = source_kinds == {"quest_reward"}
        instance_only = bool(source_kinds) and source_kinds <= {
            "mob_drop",
            "map_drop",
            "instance_drop",
            "instance_reward",
        } and bool(source_kinds & {"instance_drop", "instance_reward"})

        junk_base = (
            item["type"] == "Etc"
            and item["sell"] <= 2000
            and not used_by_content
            and not is_unobtainable
            and bool(drop_sources)
        )
        if item["untradeable"]:
            categories["untradeable"].add(item_id)
        is_junk = (
            junk_base
            and not item["untradeable"]
            and item_id not in group_members
            and item_id not in package_members
        )
        if junk_base:
            categories["junk_npc_unused"].add(item_id)

        flags: list[str] = []
        if references["quest"]:
            flags.append("quest_referenced")
            categories["quest_referenced"].add(item_id)
        if references["instance"]:
            flags.append("instance_referenced")
            categories["instance_referenced"].add(item_id)
        if references["npc"]:
            flags.append("npc_referenced")
            categories["npc_referenced"].add(item_id)
        if skill_cost:
            flags.append("skill_cost")
            categories["skill_cost"].add(item_id)
        if scripted:
            flags.append("scripted")
            categories["scripted"].add(item_id)
        if scripted and item["type"] in CONSUMABLE_TYPES:
            categories["consumable_scripted"].add(item_id)
        if in_combo:
            flags.append("used_in_combo")
            categories["used_in_combo"].add(item_id)
        if craft_material:
            flags.append("craft_material")
            categories["craft_material"].add(item_id)
        if item_id in produce_outputs or item_id in laphine_rewards:
            categories["craft_output"].add(item_id)
        if npc_shop:
            categories["npc_shop"].add(item_id)
        if item_id in cash:
            categories["cash_shop"].add(item_id)
        if item_id in drops:
            categories["mob_drop"].add(item_id)
        if item_id in map_drops:
            categories["map_drop"].add(item_id)
        if item_id in group_members:
            categories["group_member"].add(item_id)
        if item_id in package_members:
            categories["package_member"].add(item_id)
        if is_unobtainable:
            categories["unobtainable"].add(item_id)
        images = image_index.get(item_id)
        tracked_no_image = (
            bool(images)
            and item_id not in unidentified_items
            and not (images.get("icon") and images.get("collection"))
        )
        if tracked_no_image and is_unobtainable:
            categories["unobtainable_no_image"].add(item_id)
        if tracked_no_image and not is_unobtainable:
            categories["obtainable_no_image"].add(item_id)
        if not direct_sources and (item_id in group_members or item_id in package_members):
            categories["group_or_package_only"].add(item_id)
        if only_restricted:
            categories["instance_or_quest_only"].add(item_id)
        if quest_only:
            categories["quest_only"].add(item_id)
        if instance_only:
            categories["instance_only"].add(item_id)
        if instance_or_guild_drop_only:
            categories["instance_or_guild_drop_only"].add(item_id)
        if "instance" in drop_kind and not {"normal", "guild"} & drop_kind:
            categories["instance_drop_only"].add(item_id)
        if "guild" in drop_kind and not {"normal", "instance"} & drop_kind:
            categories["guild_dungeon_drop_only"].add(item_id)
        if is_junk:
            categories["junk"].add(item_id)
            if item["sell"] <= 500:
                categories["junk_low"].add(item_id)
            elif item["sell"] <= 1000:
                categories["junk_mid"].add(item_id)
            else:
                categories["junk_high"].add(item_id)

        item_meta[str(item_id)] = {
            "aegis": item["aegis"],
            "name": item["name"],
            "type": item["type"],
            "sell": item["sell"],
            "sources": sorted(source_kinds),
            "flags": flags,
            "access": access,
            "marketPrice": master_prices.get(item_id, 0),
        }

    ordered = {key: sorted(value) for key, value in sorted(categories.items())}
    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": {
            "items": [str(path.relative_to(ROOT)) for path in ITEM_FILES if path.exists()],
            "mobs": [str(path.relative_to(ROOT)) for path in MOB_FILES if path.exists()],
            "mapDrops": [str(path.relative_to(ROOT)) for path in MAP_DROP_FILES if path.exists()],
            "skills": [str(path.relative_to(ROOT)) for path in SKILL_FILES if path.exists()],
            "instances": [str(path.relative_to(ROOT)) for path in INSTANCE_FILES if path.exists()],
            "scriptsRoot": "npc/re/scripts_main.conf",
            "spawns": str(SPAWNS.relative_to(ROOT.parent)) if SPAWNS.exists() else None,
            "masterList": str(MASTER_LIST.relative_to(ROOT.parent)) if MASTER_LIST.exists() else None,
            "itemImages": str(IMAGE_INDEX.relative_to(ROOT.parent)) if IMAGE_INDEX.exists() else None,
            "rules": {
                "highHpThreshold": high_hp_threshold,
                "hpRates": hp_rates,
            },
        },
        "counts": {key: len(value) for key, value in ordered.items()},
        "categories": ordered,
        "items": item_meta,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the OzRo item taxonomy")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--high-hp-threshold",
        type=int,
        default=HIGH_HP_THRESHOLD,
        help="Effective mob HP at or above which a drop source is flagged as high_hp",
    )
    args = parser.parse_args()
    taxonomy = build_taxonomy(high_hp_threshold=args.high_hp_threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(taxonomy, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(taxonomy['items'])} items -> {args.output}")
    for key, value in taxonomy["counts"].items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
