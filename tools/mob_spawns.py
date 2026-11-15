#!/usr/bin/env python3
"""Generate permanent mob spawn data from active rAthena NPC scripts.

The generator reads the same script set as the server, resolves mob Aegis
names through mob_db.yml, marks instance maps and writes:

  mob_spawn.sql          importable MariaDB table for the website API
  web/spawns/maps.json   index with one entry per map
  web/spawns/maps/*.json spawn points for one map
  web/spawns/mobs/*.json spawn points for one mob
  report.json            unresolved names/maps and parse errors

Only top-level permanent spawn commands are exported. Dynamic monster
summons inside script blocks are intentionally ignored because they have no
stable map spawn definition.

Usage:
  python3 tools/mob_spawns.py --out /tmp/ozro-spawns
  python3 tools/mob_spawns.py --out /tmp/ozro-spawns --conf npc/pre-re/scripts_main.conf
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a build-time dependency
    yaml = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from npc_inventory import read_script, resolve_script_files, strip_comments  # noqa: E402

SPAWN_RE = re.compile(
    r"^\s*([^,\t]+)"
    r"(?:,(-?\d+))?"
    r"(?:,(-?\d+))?"
    r"(?:,(-?\d+))?"
    r"(?:,(-?\d+))?"
    r"\s*\t\s*(monster|boss_monster)\s*\t"
    r"([^\t]*)\s*\t\s*(.+?)\s*$",
    re.IGNORECASE,
)

INSTANCE_MAP_RE = re.compile(r"^(?:\d+@|@)")

SQL_TABLE = """\
DROP TABLE IF EXISTS `mob_spawn`;
CREATE TABLE `mob_spawn` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `mob_id` int(10) unsigned NOT NULL,
  `map` varchar(24) NOT NULL,
  `x` smallint(6) NOT NULL DEFAULT 0,
  `y` smallint(6) NOT NULL DEFAULT 0,
  `xs` smallint(6) NOT NULL DEFAULT 0,
  `ys` smallint(6) NOT NULL DEFAULT 0,
  `amount` int(10) unsigned NOT NULL DEFAULT 0,
  `delay` int(10) unsigned NOT NULL DEFAULT 0,
  `delay2` int(10) unsigned NOT NULL DEFAULT 0,
  `is_boss` tinyint(1) NOT NULL DEFAULT 0,
  `is_instance` tinyint(1) NOT NULL DEFAULT 0,
  `source_file` varchar(255) NOT NULL,
  `source_line` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_mob_spawn_mob` (`mob_id`, `is_instance`),
  KEY `idx_mob_spawn_map` (`map`, `mob_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def load_yaml(path: str) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML no está instalado (pip install pyyaml)")
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def body_entries(data: dict) -> list[dict]:
    body = data.get("Body") or []
    return [entry for entry in body if isinstance(entry, dict)]


def load_mob_names(root: str, explicit: str | None) -> tuple[dict[str, int], str | None]:
    if explicit:
        candidates = [explicit]
    else:
        candidates = [
            "db/re/mob_db.yml",
            "db/pre-re/mob_db.yml",
            "db/mob_db.yml",
        ]

    path = next((os.path.join(root, rel) for rel in candidates if os.path.isfile(os.path.join(root, rel))), None)
    if not path:
        return {}, None

    names: dict[str, int] = {}
    for entry in body_entries(load_yaml(path)):
        aegis = entry.get("AegisName")
        mob_id = entry.get("Id")
        if aegis is not None and mob_id is not None:
            names[str(aegis)] = int(mob_id)

    # Imports override base records by id.
    import_path = os.path.join(root, "db/import/mob_db.yml")
    if os.path.isfile(import_path):
        for entry in body_entries(load_yaml(import_path)):
            aegis = entry.get("AegisName")
            mob_id = entry.get("Id")
            if aegis is not None and mob_id is not None:
                names[str(aegis)] = int(mob_id)

    return names, os.path.relpath(path, root)


def load_instance_maps(root: str) -> set[str]:
    maps: set[str] = set()
    for rel in ("db/re/instance_db.yml", "db/import/instance_db.yml", "db/instance_db.yml"):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        for entry in body_entries(load_yaml(path)):
            enter = entry.get("Enter") or {}
            if isinstance(enter, dict) and enter.get("Map"):
                maps.add(str(enter["Map"]))
            additional = entry.get("AdditionalMaps") or {}
            if isinstance(additional, dict):
                maps.update(str(name) for name in additional)
    return maps


def load_map_index(root: str) -> set[str]:
    path = os.path.join(root, "db/map_index.txt")
    if not os.path.isfile(path):
        return set()
    maps: set[str] = set()
    for raw in read_script(path).splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        maps.add(line.split()[0])
    return maps


def parse_spawns(files: list[str], root: str, mob_names: dict[str, int]):
    spawns: list[dict] = []
    errors: list[dict] = []
    unresolved_mobs: Counter[str] = Counter()

    for path in files:
        rel = os.path.relpath(path, root)
        for line_number, raw in enumerate(read_script(path).splitlines(), 1):
            if "\tmonster\t" not in raw.lower() and "\tboss_monster\t" not in raw.lower():
                continue

            line = strip_comments(raw).strip()
            if not line:
                continue

            match = SPAWN_RE.match(line)
            if not match:
                errors.append({"file": rel, "line": line_number, "reason": "invalid spawn line", "text": raw.strip()[:200]})
                continue

            map_name = match.group(1).strip()
            x = int(match.group(2) or 0)
            y = int(match.group(3) or 0)
            xs = int(match.group(4) or 0)
            ys = int(match.group(5) or 0)
            command = match.group(6).lower()
            spawn_name = match.group(7).strip()
            args = match.group(8).strip()

            fields = args.split(",", 2)
            if len(fields) < 2:
                errors.append({"file": rel, "line": line_number, "reason": "missing mob id/amount", "text": raw.strip()[:200]})
                continue

            mob_token = fields[0].strip()
            try:
                amount = int(fields[1].strip())
            except ValueError:
                errors.append({"file": rel, "line": line_number, "reason": "invalid amount", "text": raw.strip()[:200]})
                continue

            if mob_token.isdigit() or (mob_token.startswith("-") and mob_token[1:].isdigit()):
                mob_id = int(mob_token)
            else:
                mob_id = mob_names.get(mob_token)
                if mob_id is None:
                    unresolved_mobs[mob_token] += 1
                    continue

            # delay1/delay2 are optional; the event field may contain commas.
            delay = 0
            delay2 = 0
            if len(fields) > 2:
                tail = fields[2]
                tail_fields = tail.split(",", 2)
                if tail_fields and tail_fields[0].strip():
                    try:
                        delay = int(tail_fields[0].strip())
                    except ValueError:
                        delay = 0
                if len(tail_fields) > 1 and tail_fields[1].strip():
                    try:
                        delay2 = int(tail_fields[1].strip())
                    except ValueError:
                        delay2 = 0

            spawns.append(
                {
                    "mobId": mob_id,
                    "map": map_name,
                    "x": x,
                    "y": y,
                    "xs": xs,
                    "ys": ys,
                    "amount": amount,
                    "delay": delay,
                    "delay2": delay2,
                    "boss": command == "boss_monster",
                    "spawnName": spawn_name,
                    "sourceFile": rel,
                    "sourceLine": line_number,
                }
            )

    return spawns, errors, unresolved_mobs


def sql_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


def write_sql(path: str, spawns: list[dict], instance_maps: set[str]) -> None:
    rows = []
    for spawn in spawns:
        is_instance = 1 if spawn["map"] in instance_maps or INSTANCE_MAP_RE.match(spawn["map"]) else 0
        rows.append(
            "({mob},{map},{x},{y},{xs},{ys},{amount},{delay},{delay2},{boss},{instance},'{file}',{line})".format(
                mob=spawn["mobId"],
                map=f"'{sql_escape(spawn['map'])}'",
                x=spawn["x"],
                y=spawn["y"],
                xs=spawn["xs"],
                ys=spawn["ys"],
                amount=spawn["amount"],
                delay=spawn["delay"],
                delay2=spawn["delay2"],
                boss=1 if spawn["boss"] else 0,
                instance=is_instance,
                file=sql_escape(spawn["sourceFile"]),
                line=spawn["sourceLine"],
            )
        )

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("-- Generated by tools/mob_spawns.py. Do not edit manually.\n")
        handle.write(SQL_TABLE)
        handle.write("\n")
        if rows:
            handle.write(
                "INSERT INTO `mob_spawn` "
                "(`mob_id`,`map`,`x`,`y`,`xs`,`ys`,`amount`,`delay`,`delay2`,`is_boss`,`is_instance`,`source_file`,`source_line`) VALUES\n"
            )
            handle.write(",\n".join(rows))
            handle.write(";\n")


def write_web(
    out_dir: str,
    spawns: list[dict],
    mob_names_by_id: dict[int, str],
    aegis_by_id: dict[int, str],
    instance_maps: set[str],
) -> dict:
    generated_at = datetime.now(timezone.utc).isoformat()
    web_dir = os.path.join(out_dir, "web", "spawns")
    maps_dir = os.path.join(web_dir, "maps")
    mobs_dir = os.path.join(web_dir, "mobs")
    os.makedirs(maps_dir, exist_ok=True)
    os.makedirs(mobs_dir, exist_ok=True)

    for directory in (maps_dir, mobs_dir):
        for stale in os.listdir(directory):
            if stale.endswith(".json"):
                os.remove(os.path.join(directory, stale))

    def is_instance(map_name: str) -> bool:
        return map_name in instance_maps or bool(INSTANCE_MAP_RE.match(map_name))

    by_map: dict[str, list[dict]] = defaultdict(list)
    by_mob: dict[int, list[dict]] = defaultdict(list)

    for spawn in spawns:
        entry = {
            "mobId": spawn["mobId"],
            "mobName": mob_names_by_id.get(spawn["mobId"], str(spawn["mobId"])),
            "mobAegis": aegis_by_id.get(spawn["mobId"]),
            "map": spawn["map"],
            "x": spawn["x"],
            "y": spawn["y"],
            "xs": spawn["xs"],
            "ys": spawn["ys"],
            "amount": spawn["amount"],
            "delay": spawn["delay"],
            "delay2": spawn["delay2"],
            "boss": spawn["boss"],
            "instance": is_instance(spawn["map"]),
        }
        by_map[spawn["map"]].append(entry)
        by_mob[spawn["mobId"]].append(entry)

    map_rows = []
    for map_name, entries in sorted(by_map.items()):
        entries.sort(key=lambda item: (-item["amount"], item["mobId"], item["x"], item["y"]))
        with open(os.path.join(maps_dir, f"{map_name}.json"), "w", encoding="utf-8") as handle:
            json.dump(entries, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")

        map_rows.append(
            {
                "map": map_name,
                "mapName": map_name,
                "points": len(entries),
                "species": len({item["mobId"] for item in entries}),
                "amount": sum(item["amount"] for item in entries),
                "boss": any(item["boss"] for item in entries),
                "instance": is_instance(map_name),
            }
        )

    for mob_id, entries in sorted(by_mob.items()):
        entries.sort(key=lambda item: (item["instance"], item["map"], -item["amount"]))
        with open(os.path.join(mobs_dir, f"{mob_id}.json"), "w", encoding="utf-8") as handle:
            json.dump(entries, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")

    index = {
        "schemaVersion": 1,
        "generatedAt": generated_at,
        "maps": map_rows,
    }
    with open(os.path.join(web_dir, "maps.json"), "w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")

    with open(os.path.join(web_dir, "spawns.json"), "w", encoding="utf-8") as handle:
        json.dump(
            {
                "schemaVersion": 1,
                "generatedAt": generated_at,
                "spawns": [
                    {
                        "mobId": spawn["mobId"],
                        "map": spawn["map"],
                        "x": spawn["x"],
                        "y": spawn["y"],
                        "xs": spawn["xs"],
                        "ys": spawn["ys"],
                        "amount": spawn["amount"],
                        "boss": spawn["boss"],
                        "instance": is_instance(spawn["map"]),
                    }
                    for spawn in spawns
                ],
            },
            handle,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        handle.write("\n")

    return index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))), help="rAthena root")
    parser.add_argument("--conf", default="npc/re/scripts_main.conf", help="active script config")
    parser.add_argument("--mob-db", default=None, help="explicit mob_db.yml path")
    parser.add_argument("--out", default="/tmp/ozro-spawns", help="output directory")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    conf_path = os.path.join(root, args.conf)
    if not os.path.isfile(conf_path):
        print(f"error: no existe {conf_path}", file=sys.stderr)
        return 1

    files = resolve_script_files(root, args.conf)
    mob_names, mob_db_path = load_mob_names(root, args.mob_db)
    if not mob_names:
        print("error: no se encontró mob_db.yml o no contiene mobs", file=sys.stderr)
        return 1

    names_by_id: dict[int, str] = {}
    aegis_by_id: dict[int, str] = {}
    for aegis, mob_id in mob_names.items():
        names_by_id.setdefault(mob_id, aegis)
        aegis_by_id.setdefault(mob_id, aegis)

    # Read display names as well; Aegis names are the fallback.
    display_sources = [mob_db_path, "db/import/mob_db.yml"]
    for rel in display_sources:
        if not rel:
            continue
        path = rel if os.path.isabs(rel) else os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        for entry in body_entries(load_yaml(path)):
            if entry.get("Id") is not None and entry.get("Name"):
                names_by_id[int(entry["Id"])] = str(entry["Name"])

    instance_maps = load_instance_maps(root)
    map_index = load_map_index(root)
    spawns, errors, unresolved_mobs = parse_spawns(files, root, mob_names)

    os.makedirs(args.out, exist_ok=True)
    sql_path = os.path.join(args.out, "mob_spawn.sql")
    write_sql(sql_path, spawns, instance_maps)
    index = write_web(args.out, spawns, names_by_id, aegis_by_id, instance_maps)

    missing_maps = sorted({spawn["map"] for spawn in spawns if map_index and spawn["map"] not in map_index})
    report = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceConf": args.conf,
        "mobDb": mob_db_path,
        "counts": {
            "scriptFiles": len(files),
            "spawns": len(spawns),
            "maps": len(index["maps"]),
            "mobs": len({spawn["mobId"] for spawn in spawns}),
            "instanceSpawns": sum(1 for spawn in spawns if spawn["map"] in instance_maps or INSTANCE_MAP_RE.match(spawn["map"])),
        },
        "unresolvedMobs": dict(sorted(unresolved_mobs.items())),
        "mapsMissingFromMapIndex": missing_maps,
        "parseErrors": errors,
    }
    with open(os.path.join(args.out, "report.json"), "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    counts = report["counts"]
    print(f"Archivos activos:  {counts['scriptFiles']}")
    print(f"Spawns:            {counts['spawns']}")
    print(f"Mapas:             {counts['maps']}")
    print(f"Mobs:              {counts['mobs']}")
    print(f"Spawns instancia:  {counts['instanceSpawns']}")
    print(f"Mobs sin resolver: {len(unresolved_mobs)}")
    print(f"Mapas no indexados:{len(missing_maps)}")
    print(f"Errores de parseo: {len(errors)}")
    print(f"Salida:            {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
