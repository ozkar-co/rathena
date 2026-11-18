#!/usr/bin/env python3
"""Extract an inventory of active NPCs from rAthena scripts.

Reads the renewal script configuration, parses NPC declarations and
duplicate() placements, and writes JSON/CSV plus an unresolved report.

The game scripts are read as ISO-8859-1; the generated JSON/CSV are UTF-8.
This is a one-shot data extraction, not part of the server runtime.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
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

DECL_KINDS = {
    "script",
    "shop",
    "cashshop",
    "itemshop",
    "pointshop",
    "marketshop",
    "duplicate",
    "warp",
    "warp2",
    "npc",
}

PLACEMENT_RE = re.compile(r"^([A-Za-z0-9_@]+),(-?\d+),(-?\d+)(?:,(-?\d+))?$")
DUPLICATE_RE = re.compile(r"^duplicate\(\s*([^)]+?)\s*\)$", re.IGNORECASE)
QUEST_SET_RE = re.compile(r"\bsetquest\s+(\d+)")
QUEST_COMPLETE_RE = re.compile(r"\bcompletequest\s+(\d+)")
QUEST_CHECK_RE = re.compile(r"\bcheckquest\s*\(\s*(\d+)")
SHOP_KINDS = {"shop", "cashshop", "itemshop", "pointshop", "marketshop"}
SHOP_ITEM_RE = re.compile(r"(\d+)\s*:\s*(-?\d+)(?:\s*:\s*(-?\d+))?")
CALLSHOP_RE = re.compile(r"\bcallshop\s*\(?\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
OZRO_CUSTOM_RE = re.compile(r"(?:^|/)npc/custom/ozro/")


def read_script(path: str) -> str:
    # rAthena scripts are byte-oriented; ISO-8859-1 maps every byte 1:1.
    with open(path, "r", encoding="latin-1", errors="replace") as handle:
        return handle.read()


def resolve_script_files(root: str, conf_rel: str) -> list[str]:
    """Resolve npc:/import: entries in load order, ignoring missing files."""
    root = os.path.abspath(root)
    seen: set[str] = set()
    ordered: list[str] = []

    def walk(rel: str) -> None:
        path = rel if os.path.isabs(rel) else os.path.join(root, rel)
        path = os.path.normpath(path)
        if path in seen or not os.path.isfile(path):
            return
        seen.add(path)
        for raw in read_script(path).splitlines():
            line = raw.split("//", 1)[0].strip()
            if not line:
                continue
            if line.startswith("npc:"):
                value = line[4:].strip()
                if value:
                    ordered.append(value)
            elif line.startswith("import:"):
                walk(line[7:].strip())

    walk(conf_rel)

    resolved: list[str] = []
    seen_files: set[str] = set()
    for rel in ordered:
        path = os.path.normpath(rel if os.path.isabs(rel) else os.path.join(root, rel))
        if os.path.isfile(path) and path not in seen_files:
            seen_files.add(path)
            resolved.append(path)
    return resolved


def variant_for(rel_path: str) -> str:
    normalized = "/" + rel_path.replace(os.sep, "/") + "/"
    if "/custom/" in normalized:
        return "custom"
    if "/re/" in normalized:
        return "re"
    if "/pre-re/" in normalized:
        return "pre-re"
    return "base"


def is_ozro_custom(rel_path: str) -> bool:
    normalized = "/" + rel_path.replace(os.sep, "/")
    return bool(OZRO_CUSTOM_RE.search(normalized))


def parse_shop_items(field: str) -> list[dict]:
    items: list[dict] = []
    for match in SHOP_ITEM_RE.finditer(field):
        item = {"itemId": int(match.group(1)), "price": int(match.group(2))}
        if match.group(3) is not None:
            item["stock"] = int(match.group(3))
        items.append(item)
    return items


def load_item_ids(root: str) -> dict[str, int]:
    if yaml is None:
        return {}
    ids: dict[str, int] = {}
    for rel in (
        "db/re/item_db.yml",
        "db/re/item_db_equip.yml",
        "db/re/item_db_etc.yml",
        "db/re/item_db_usable.yml",
        "db/import/item_db.yml",
    ):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        for entry in data.get("Body") or []:
            if not isinstance(entry, dict):
                continue
            aegis = entry.get("AegisName")
            item_id = entry.get("Id")
            if aegis is not None and item_id is not None:
                ids[str(aegis)] = int(item_id)
    return ids


def load_barters(root: str, item_ids: dict[str, int]) -> dict[str, dict]:
    """Load active barter shops, following Footer.Imports in load order."""
    if yaml is None:
        return {}

    seen: set[str] = set()
    barters: dict[str, dict] = {}

    def add_items(name: str, entries: list) -> None:
        shop = barters.setdefault(name, {"type": "barter", "items": []})
        for entry in entries or []:
            if not isinstance(entry, dict) or not entry.get("Item"):
                continue
            item = {"item": str(entry["Item"])}
            item_id = item_ids.get(item["item"])
            if item_id is not None:
                item["itemId"] = item_id
            for key, output in (("Stock", "stock"), ("Zeny", "zeny"), ("Refine", "refine")):
                if entry.get(key) is not None:
                    item[output] = int(entry[key])
            required = []
            for req in entry.get("RequiredItems") or []:
                if not isinstance(req, dict) or not req.get("Item"):
                    continue
                req_entry = {"item": str(req["Item"])}
                req_id = item_ids.get(req_entry["item"])
                if req_id is not None:
                    req_entry["itemId"] = req_id
                if req.get("Amount") is not None:
                    req_entry["amount"] = int(req["Amount"])
                if req.get("Refine") is not None:
                    req_entry["refine"] = int(req["Refine"])
                required.append(req_entry)
            if required:
                item["requiredItems"] = required
            shop["items"].append(item)

    def walk(rel: str) -> None:
        path = os.path.normpath(os.path.join(root, rel))
        if path in seen or not os.path.isfile(path):
            return
        seen.add(path)
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        for entry in data.get("Body") or []:
            if isinstance(entry, dict) and entry.get("Name"):
                add_items(str(entry["Name"]), entry.get("Items"))
        imports = (data.get("Footer") or {}).get("Imports") or []
        for entry in imports:
            target = entry.get("Path") if isinstance(entry, dict) else entry
            if target:
                walk(str(target))

    walk("npc/barters.yml")
    return {name: shop for name, shop in barters.items() if shop["items"]}


def shop_for(kind: str, field: str, body: str, barters: dict[str, dict]) -> dict | None:
    if kind in SHOP_KINDS:
        items = parse_shop_items(field)
        return {"type": kind, "items": items} if items else None

    if kind == "script":
        items: list[dict] = []
        shop_type = "barter"
        for name in dict.fromkeys(CALLSHOP_RE.findall(body)):
            shop = barters.get(name)
            if shop:
                items.extend(shop["items"])
        if items:
            return {"type": shop_type, "items": items}
    return None


def strip_comments(body: str) -> str:
    """Remove // and /* */ comments without touching quoted strings."""
    out: list[str] = []
    i = 0
    in_str = False
    escaped = False
    in_line_comment = False
    in_block_comment = False
    length = len(body)
    while i < length:
        char = body[i]
        nxt = body[i + 1] if i + 1 < length else ""
        if in_line_comment:
            if char == "\n":
                in_line_comment = False
                out.append(char)
        elif in_block_comment:
            if char == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_str:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_str = False
        else:
            if char == "/" and nxt == "/":
                in_line_comment = True
                i += 1
            elif char == "/" and nxt == "*":
                in_block_comment = True
                i += 1
            else:
                if char == '"':
                    in_str = True
                out.append(char)
        i += 1
    return "".join(out)


def extract_block(text: str, start: int) -> str:
    """Return the first {...} block at/after start, skipping strings/comments."""
    begin = text.find("{", start)
    if begin < 0:
        return ""
    depth = 0
    i = begin
    in_str = False
    escaped = False
    in_line_comment = False
    in_block_comment = False
    length = len(text)
    while i < length:
        char = text[i]
        nxt = text[i + 1] if i + 1 < length else ""
        if in_line_comment:
            if char == "\n":
                in_line_comment = False
        elif in_block_comment:
            if char == "*" and nxt == "/":
                in_block_comment = False
                i += 1
        elif in_str:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_str = False
        else:
            if char == "/" and nxt == "/":
                in_line_comment = True
                i += 1
            elif char == "/" and nxt == "*":
                in_block_comment = True
                i += 1
            elif char == '"':
                in_str = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[begin : i + 1]
        i += 1
    return text[begin:]


def strip_strings(text: str) -> str:
    """Replace quoted string contents with empty quotes."""
    out: list[str] = []
    in_str = False
    escaped = False
    for char in text:
        if in_str:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_str = False
                out.append('""')
        else:
            if char == '"':
                in_str = True
            else:
                out.append(char)
    return "".join(out)


def code_only(body: str) -> str:
    return strip_strings(strip_comments(body))


def classify(kind: str, name: str, body: str) -> str:
    if kind in {"shop", "cashshop", "itemshop", "pointshop", "marketshop"}:
        return "tienda"
    if kind in {"warp", "warp2"}:
        return "warp"

    clean = code_only(body).lower()
    if re.search(r"\b(setquest|completequest|checkquest|questinfo)\b", clean):
        return "quest"
    if re.search(r"\b(cashshop|marketshop|itemshop|pointshop|shop|callshop)\b", clean):
        return "tienda"
    if re.search(r"\bwarp\b", clean):
        return "warp"
    if "kafra" in name.lower():
        return "kafra"
    if re.search(r"\b(openstorage|storage)\b", clean):
        return "almacen"
    if re.search(r"\b(heal|percentheal|sc_start|bonus_script)\b", clean):
        return "soporte"
    if re.search(r"\b(mes|menu|next|select)\b", clean):
        return "dialogo"
    return "otro"


def quests_in(body: str) -> dict[str, list[int]]:
    clean = code_only(body)
    return {
        "given": sorted({int(value) for value in QUEST_SET_RE.findall(clean)}),
        "completed": sorted({int(value) for value in QUEST_COMPLETE_RE.findall(clean)}),
        "checked": sorted({int(value) for value in QUEST_CHECK_RE.findall(clean)}),
    }


def normalize_label(value: str) -> str:
    value = value.strip()
    if value.startswith("::"):
        value = value[2:]
    elif value.startswith(":"):
        value = value[1:]
    return value.strip()


def label_from_name(name: str) -> str:
    """NPC labels may be `::Label` or `Display#tag::Label`; otherwise the name is the label."""
    if "::" in name:
        return normalize_label(name.rsplit("::", 1)[1])
    return normalize_label(name)


def display_name(name: str) -> str:
    return name.split("::", 1)[0].strip()


def split_decl(line: str) -> list[str]:
    return line.split("\t")


def prettify_map(map_name: str) -> str:
    if not map_name or map_name[0].isdigit() or "@" in map_name or "_" in map_name:
        return map_name
    return map_name[:1].upper() + map_name[1:]


def parse_file(
    path: str, root: str, barters: dict[str, dict]
) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (definitions, placements, errors) found in one active script."""
    rel = os.path.relpath(path, root)
    text = read_script(path)
    lines = text.splitlines()
    offsets: list[int] = []
    offset = 0
    for line in text.splitlines(keepends=True):
        offsets.append(offset)
        offset += len(line)

    definitions: list[dict] = []
    placements: list[dict] = []
    errors: list[dict] = []

    for index, raw in enumerate(lines):
        line = raw.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("//"):
            continue

        parts = split_decl(line)
        if len(parts) < 2:
            continue

        head = parts[0].strip()
        kind_raw = parts[1].strip()
        kind_match = re.match(r"^([A-Za-z]+(?:\([^)]*\))?)", kind_raw)
        if not kind_match:
            continue
        kind = kind_match.group(1).split("(")[0].lower()
        if kind not in DECL_KINDS:
            continue

        is_template = head == "-"
        if not is_template and not PLACEMENT_RE.match(head):
            continue

        raw_name = parts[2].strip() if len(parts) > 2 else ""
        name = display_name(raw_name)
        field = parts[3].split("//", 1)[0].strip() if len(parts) > 3 else ""
        sprite = field.split(",")[0].strip() if field else ""
        if kind in {"warp", "warp2"}:
            sprite = ""

        label: str | None = None
        duplicate_label: str | None = None

        if kind == "duplicate":
            duplicate_match = DUPLICATE_RE.match(kind_raw)
            if duplicate_match:
                duplicate_label = normalize_label(duplicate_match.group(1))
            # A duplicate registers its own name as a label, while pointing
            # at another label through duplicate(...).
            label = label_from_name(raw_name) if raw_name else duplicate_label
        else:
            label = label_from_name(raw_name) if raw_name else None

        body = ""
        if kind == "script":
            body = extract_block(text, offsets[index])
        quests = quests_in(body)

        entry = {
            "file": rel,
            "line": index + 1,
            "kind": kind,
            "name": name,
            "label": label,
            "duplicateLabel": duplicate_label,
            "sprite": sprite or None,
            "variant": variant_for(rel),
            "function": classify(kind, name, body),
            "quests": quests,
            "isTemplate": is_template,
            "isCustom": is_ozro_custom(rel),
            "shop": shop_for(kind, field, body, barters),
        }

        if is_template:
            definitions.append(entry)
            continue

        placement_match = PLACEMENT_RE.match(head)
        if not placement_match:
            errors.append({"file": rel, "line": index + 1, "reason": "invalid placement"})
            continue

        entry.update(
            {
                "map": placement_match.group(1),
                "x": int(placement_match.group(2)),
                "y": int(placement_match.group(3)),
                "dir": int(placement_match.group(4)) if placement_match.group(4) is not None else None,
            }
        )
        placements.append(entry)

        # Any placed NPC can be a duplicate target by its label/name,
        # including duplicates (the target may be another duplicate).
        if label:
            definitions.append(entry)

    return definitions, placements, errors


def stable_id(record: dict) -> str:
    key = "|".join(
        str(record.get(field) or "")
        for field in ("groupLabel", "label", "nameBase", "map", "x", "y", "dir", "sprite")
    )
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        help="rAthena repository root (default: parent of tools/)",
    )
    parser.add_argument(
        "--conf",
        default="npc/re/scripts_main.conf",
        help="entry script config (default: npc/re/scripts_main.conf)",
    )
    parser.add_argument(
        "--out",
        default="/tmp/ozro-npc-inventory",
        help="output directory (default: /tmp/ozro-npc-inventory)",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isfile(os.path.join(root, args.conf)):
        print(f"error: no existe {os.path.join(root, args.conf)}", file=sys.stderr)
        return 1

    files = resolve_script_files(root, args.conf)
    barters = load_barters(root, load_item_ids(root))

    definitions: list[dict] = []
    placements: list[dict] = []
    errors: list[dict] = []

    for path in files:
        try:
            defs, placed, errs = parse_file(path, root, barters)
        except OSError as error:
            errors.append({"file": path, "reason": f"read error: {error}"})
            continue
        definitions.extend(defs)
        placements.extend(placed)
        errors.extend(errs)

    template_definitions = [item for item in definitions if item["isTemplate"]]
    defs_by_label: dict[str, list[dict]] = defaultdict(list)
    for definition in definitions:
        if definition["label"]:
            defs_by_label[definition["label"]].append(definition)

    used_labels = {placement.get("duplicateLabel") for placement in placements}
    duplicate_labels: dict[str, list[dict]] = {}
    for label, items in defs_by_label.items():
        if label not in used_labels:
            continue
        non_duplicates = [item for item in items if item["kind"] != "duplicate"]
        if len(non_duplicates) > 1:
            duplicate_labels[label] = non_duplicates

    def resolve_definition(label: str | None, variant: str) -> dict | None:
        """Follow duplicate() chains to the first non-duplicate definition."""
        seen: set[str] = set()
        current = label
        while current:
            if current in seen:
                return None
            seen.add(current)
            candidates = defs_by_label.get(current, [])
            if not candidates:
                return None
            non_duplicates = [item for item in candidates if item["kind"] != "duplicate"]
            pool = non_duplicates or candidates
            same_variant = [item for item in pool if item["variant"] == variant]
            chosen = (same_variant or pool)[-1]
            if chosen["kind"] != "duplicate":
                return chosen
            current = chosen.get("duplicateLabel")
        return None

    unresolved_placements: list[dict] = []
    records: dict[tuple, dict] = {}

    for placement in placements:
        if placement["kind"] == "duplicate":
            label = placement["duplicateLabel"]
            resolved = resolve_definition(label, placement["variant"])
            if resolved is None:
                unresolved_placements.append(
                    {
                        "file": placement["file"],
                        "line": placement["line"],
                        "label": label,
                        "name": placement["name"],
                        "reason": "duplicate label not found",
                    }
                )
                continue
            placement["function"] = resolved["function"]
            placement["quests"] = resolved["quests"]
            placement["sprite"] = placement["sprite"] or resolved["sprite"]
            placement["shop"] = resolved.get("shop")
            placement["isCustom"] = placement["isCustom"] or resolved["isCustom"]
            placement["definitionFile"] = resolved["file"]
            placement["definitionLine"] = resolved["line"]
            placement["resolvedLabel"] = resolved.get("label")

        name_base = placement["name"].lstrip("#").split("#", 1)[0] or placement["name"]
        group_label = (
            placement.get("resolvedLabel") or placement.get("label")
            if placement["kind"] == "duplicate"
            else name_base
        )
        key = (
            group_label,
            placement["x"],
            placement["y"],
            placement["dir"],
            placement["sprite"],
            placement["function"],
        )
        record = records.get(key)
        if record is None:
            record = {
                "id": "",
                "name": placement["name"],
                "nameBase": name_base,
                "label": placement.get("resolvedLabel") or placement.get("label"),
                "groupLabel": group_label,
                "map": placement["map"],
                "mapName": prettify_map(placement["map"]),
                "maps": [placement["map"]],
                "x": placement["x"],
                "y": placement["y"],
                "dir": placement["dir"],
                "sprite": placement["sprite"],
                "visible": placement["sprite"] not in {
                    None,
                    "",
                    "-1",
                    "HIDDEN_WARP_NPC",
                    "WARPNPC",
                    "CLEAR_NPC",
                    "INVISIBLE",
                },
                "isInstance": bool(re.match(r"^\d+@", placement["map"])),
                "isCustom": placement["isCustom"]
                or is_ozro_custom(placement.get("definitionFile") or ""),
                "function": placement["function"],
                "quests": placement["quests"],
                "shop": placement.get("shop"),
                "source": placement["file"],
                "sourceLine": placement["line"],
                "placementFile": placement["file"],
                "placementLine": placement["line"],
                "placements": 0,
                "variant": placement["variant"],
            }
            if placement["kind"] == "duplicate":
                record["source"] = placement.get("definitionFile") or placement["file"]
                record["sourceLine"] = placement.get("definitionLine") or placement["line"]
            records[key] = record
        else:
            if placement["map"] not in record["maps"]:
                record["maps"].append(placement["map"])
            if placement["name"] and placement["name"] != record["name"]:
                # Keep the shortest/cleanest name for display.
                if len(placement["name"]) < len(record["name"]):
                    record["name"] = placement["name"]
            if placement.get("shop"):
                record["shop"] = placement["shop"]
            record["isCustom"] = record["isCustom"] or placement["isCustom"]
        record["placements"] += 1

    npcs: list[dict] = []
    for record in records.values():
        record["maps"].sort()
        # Prefer the map name without a channel suffix as the canonical one.
        canonical = sorted(record["maps"], key=lambda value: (len(value), value))[0]
        record["map"] = canonical
        record["mapName"] = prettify_map(canonical)
        record["channels"] = record["maps"] if len(record["maps"]) > 1 else []
        record["id"] = stable_id(record)
        npcs.append(record)

    npcs.sort(key=lambda item: (item["map"], item["nameBase"].lower(), item["id"]))
    for record in npcs:
        record.pop("maps", None)

    unresolved_definitions = [
        {
            "file": definition["file"],
            "line": definition["line"],
            "label": definition["label"],
            "name": definition["name"],
            "reason": "template never referenced by duplicate()",
        }
        for definition in template_definitions
        if definition["label"] and definition["label"] not in used_labels
    ]

    function_counts = Counter(item["function"] for item in npcs)
    payload = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceRoot": root,
        "sourceConf": args.conf,
        "counts": {
            "scriptFiles": len(files),
            "definitions": len(template_definitions),
            "placements": len(placements),
            "npcs": len(npcs),
            "unresolvedPlacements": len(unresolved_placements),
            "unresolvedDefinitions": len(unresolved_definitions),
            "duplicateLabels": len(duplicate_labels),
            "functions": dict(sorted(function_counts.items())),
            "custom": sum(1 for item in npcs if item["isCustom"]),
            "shops": sum(1 for item in npcs if item.get("shop")),
        },
        "npcs": npcs,
    }

    os.makedirs(args.out, exist_ok=True)
    inventory_path = os.path.join(args.out, "inventory.json")
    min_path = os.path.join(args.out, "inventory.min.json")
    unresolved_path = os.path.join(args.out, "unresolved.json")
    csv_path = os.path.join(args.out, "inventory.csv")

    with open(inventory_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(min_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")

    unresolved = {
        "schemaVersion": 1,
        "generatedAt": payload["generatedAt"],
        "counts": {
            "placements": len(unresolved_placements),
            "definitions": len(unresolved_definitions),
            "duplicateLabels": len(duplicate_labels),
            "parseErrors": len(errors),
        },
        "placementsWithoutDefinition": unresolved_placements,
        "definitionsWithoutPlacement": unresolved_definitions,
        "duplicateLabels": {
            label: [
                {"file": item["file"], "line": item["line"], "variant": item["variant"]}
                for item in items
            ]
            for label, items in sorted(duplicate_labels.items())
        },
        "parseErrors": errors,
    }
    with open(unresolved_path, "w", encoding="utf-8") as handle:
        json.dump(unresolved, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    with open(csv_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "id",
                "name",
                "map",
                "x",
                "y",
                "dir",
                "sprite",
                "visible",
                "isInstance",
                "function",
                "quests",
                "isCustom",
                "shopItems",
                "source",
                "sourceLine",
                "placementFile",
                "placementLine",
                "placements",
                "channels",
            ]
        )
        for item in npcs:
            writer.writerow(
                [
                    item["id"],
                    item["name"],
                    item["map"],
                    item["x"],
                    item["y"],
                    item["dir"] if item["dir"] is not None else "",
                    item["sprite"] or "",
                    "1" if item["visible"] else "0",
                    "1" if item["isInstance"] else "0",
                    item["function"],
                    ";".join(
                        f"{kind}:{','.join(map(str, ids))}"
                        for kind, ids in item["quests"].items()
                        if ids
                    ),
                    "1" if item["isCustom"] else "0",
                    len(item["shop"]["items"]) if item.get("shop") else 0,
                    item["source"],
                    item["sourceLine"],
                    item["placementFile"],
                    item["placementLine"],
                    item["placements"],
                    ",".join(item["channels"]),
                ]
            )

    # Web-friendly split: one file per map plus a small index.
    web_dir = os.path.join(args.out, "web")
    npcs_dir = os.path.join(web_dir, "npcs")
    os.makedirs(npcs_dir, exist_ok=True)
    for stale in os.listdir(npcs_dir):
        if stale.endswith(".json"):
            os.remove(os.path.join(npcs_dir, stale))

    by_map: dict[str, list[dict]] = defaultdict(list)
    for item in npcs:
        by_map[item["map"]].append(item)

    map_rows: list[dict] = []
    for map_name, items in sorted(by_map.items()):
        rows: list[dict] = []
        for item in items:
            row = {
                "id": item["id"],
                "name": item["name"],
                "x": item["x"],
                "y": item["y"],
                "dir": item["dir"],
                "sprite": item["sprite"],
                "function": item["function"],
                "visible": item["visible"],
                "isInstance": item["isInstance"],
            }
            if item["isCustom"]:
                row["isCustom"] = True
            quests = {key: value for key, value in item["quests"].items() if value}
            if quests:
                row["quests"] = quests
            if item.get("shop"):
                row["shop"] = item["shop"]
            rows.append(row)
        with open(
            os.path.join(npcs_dir, f"{map_name}.json"), "w", encoding="utf-8"
        ) as handle:
            json.dump(rows, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")
        map_rows.append(
            {
                "map": map_name,
                "mapName": prettify_map(map_name),
                "total": len(items),
                "visible": sum(1 for item in items if item["visible"]),
                "custom": sum(1 for item in items if item["isCustom"]),
                "instance": any(item["isInstance"] for item in items),
            }
        )

    with open(os.path.join(web_dir, "maps.json"), "w", encoding="utf-8") as handle:
        json.dump(
            {
                "schemaVersion": 1,
                "generatedAt": payload["generatedAt"],
                "maps": map_rows,
            },
            handle,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        handle.write("\n")

    counts = payload["counts"]
    print(f"Archivos activos:       {counts['scriptFiles']}")
    print(f"Definiciones:           {counts['definitions']}")
    print(f"Placements:             {counts['placements']}")
    print(f"NPCs únicos:            {counts['npcs']}")
    print(f"Sin definición:         {counts['unresolvedPlacements']}")
    print(f"Sin placement:          {counts['unresolvedDefinitions']}")
    print(f"Labels duplicados:      {counts['duplicateLabels']}")
    print(f"NPCs custom de OzRo:    {counts['custom']}")
    print(f"NPCs con tienda:        {counts['shops']}")
    print(f"Funciones:              {counts['functions']}")
    print(f"Salida:                 {args.out}")
    print(f"Web:                    {web_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
