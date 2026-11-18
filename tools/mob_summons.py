#!/usr/bin/env python3
"""Generate summon lists for boss/MVP mobs from rAthena mob skills.

Reads the renewal and import mob_skill_db files and writes a small JSON
index consumed by the website. Only bosses and MVPs are exported, as
requested for the mob encyclopedia.

Usage:
  python3 tools/mob_summons.py
  python3 tools/mob_summons.py --out ../ozro-site/assets/mobs/summons.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a build-time dependency
    yaml = None

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from npc_inventory import read_script, strip_comments  # noqa: E402

SUMMON_SKILLS = {"NPC_SUMMONSLAVE", "NPC_SUMMONMONSTER", "NPC_DEATHSUMMON"}
DEFAULT_OUT = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "ozro-site",
        "assets",
        "mobs",
        "summons.json",
    )
)


def load_mobs(root: str) -> dict[int, dict]:
    if yaml is None:
        raise RuntimeError("PyYAML no está instalado (pip install pyyaml)")

    mobs: dict[int, dict] = {}
    for rel in ("db/re/mob_db.yml", "db/import/mob_db.yml"):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        for entry in data.get("Body") or []:
            if not isinstance(entry, dict) or entry.get("Id") is None:
                continue
            mob = mobs.setdefault(
                int(entry["Id"]),
                {"aegis": None, "name": None, "class": None, "mvp": False, "mvpExp": 0},
            )
            if entry.get("AegisName") is not None:
                mob["aegis"] = entry["AegisName"]
            if entry.get("Name") is not None:
                mob["name"] = entry["Name"]
            if entry.get("Class") is not None:
                mob["class"] = entry["Class"]
            modes = entry.get("Modes")
            if isinstance(modes, dict) and modes.get("Mvp") is not None:
                mob["mvp"] = bool(modes["Mvp"])
            if entry.get("MvpExp") is not None:
                mob["mvpExp"] = int(entry["MvpExp"])
    return mobs


def parse_summons(path: str) -> dict[int, dict]:
    result: dict[int, dict] = {}
    for raw in read_script(path).splitlines():
        line = strip_comments(raw).strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(",")
        if len(parts) < 17:
            continue
        skill_name = parts[1].strip().split("@")[-1].upper()
        if skill_name not in SUMMON_SKILLS:
            continue
        try:
            mob_id = int(parts[0])
            amount = int(parts[4] or 0)
        except ValueError:
            continue
        summoned = []
        for value in parts[12:17]:
            token = value.strip()
            if token.isdigit() and int(token) > 0:
                summoned.append(int(token))
        if not summoned:
            continue
        condition = parts[10].strip() or "always"
        entry = result.setdefault(mob_id, {})
        for summoned_id in summoned:
            item = entry.setdefault(
                summoned_id,
                {"mobId": summoned_id, "amount": amount, "conditions": set()},
            )
            item["amount"] = max(item["amount"], amount)
            item["conditions"].add(condition)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="rAthena repository root (default: parent of tools/)",
    )
    parser.add_argument("--out", default=DEFAULT_OUT, help="output JSON path")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    mobs = load_mobs(root)

    raw: dict[int, dict] = {}
    for rel in ("db/re/mob_skill_db.txt", "db/import/mob_skill_db.txt"):
        path = os.path.join(root, rel)
        if os.path.isfile(path):
            for mob_id, summons in parse_summons(path).items():
                raw.setdefault(mob_id, {}).update(summons)

    payload: dict[str, dict] = {}
    for mob_id, summons in sorted(raw.items()):
        mob = mobs.get(mob_id, {})
        if not (mob.get("mvp") or mob.get("mvpExp", 0) > 0 or str(mob.get("class", "")).lower() == "boss"):
            continue
        entries = []
        for summoned_id, item in sorted(summons.items()):
            summoned = mobs.get(summoned_id, {})
            entries.append(
                {
                    "mobId": summoned_id,
                    "mobAegis": summoned.get("aegis"),
                    "mobName": summoned.get("name") or str(summoned_id),
                    "amount": item["amount"],
                    "conditions": sorted(item["conditions"]),
                }
            )
        payload[str(mob_id)] = {
            "name": mob.get("name") or str(mob_id),
            "aegis": mob.get("aegis"),
            "list": entries,
        }

    output = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "db/re/mob_skill_db.txt + db/import/mob_skill_db.txt",
        "counts": {"summoners": len(payload)},
        "summons": payload,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")

    print(f"Boss/MVP con invocaciones: {len(payload)}")
    print(f"Salida:                    {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
