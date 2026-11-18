#!/usr/bin/env python3
"""Build the full OzRo market master and its SQL projection.

Outputs:
  data/market/master.jsonl
  data/market/master_summary.json
  data/market/sql/ozro_market_data.sql
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from market import build_sample, common  # noqa: E402

DATASET_VERSION = "v2"
OUT_DIR = common.ROOT / "data" / "market"
OUT_JSONL = OUT_DIR / "master.jsonl"
OUT_SUMMARY = OUT_DIR / "master_summary.json"
OUT_SQL = OUT_DIR / "sql" / "ozro_market_data.sql"


def sql_str(value: Any) -> str:
    text = str(value if value is not None else "")
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


def sql_num(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(int(value))


def chunks(values: list[Any], size: int) -> Iterable[list[Any]]:
    for index in range(0, len(values), size):
        yield values[index : index + size]


def main() -> None:
    data = build_sample.load_inputs()
    metrics = build_sample.build_metrics(data)
    build_sample.build_prices(data, metrics)
    build_sample.apply_craft_costs(metrics)

    rows = [build_sample.serialize(metric) for metric in metrics.values()]
    rows.sort(key=lambda row: row["itemId"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUT_JSONL.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    status = Counter(row["price"]["status"] for row in rows)
    tags = Counter(tag for row in rows for tag in row.get("tags", []))
    summary = {
        "schemaVersion": 1,
        "datasetVersion": DATASET_VERSION,
        "items": len(rows),
        "priceStatus": dict(sorted(status.items())),
        "marketEligible": sum(1 for row in rows if row["marketEligible"]),
        "npcEligible": sum(1 for row in rows if row["npcEligible"]),
        "withOpenSupply": sum(1 for row in rows if row["supply"]["open"] > 0),
        "tags": dict(sorted(tags.items())),
        "outputs": {
            "jsonl": str(OUT_JSONL.relative_to(common.ROOT)),
            "sql": str(OUT_SQL.relative_to(common.ROOT)),
        },
    }
    OUT_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    tag_rows = sorted({(row["itemId"], tag) for row in rows for tag in row.get("tags", [])})

    OUT_SQL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_SQL.open("w", encoding="utf-8") as handle:
        handle.write("-- OzRo market master SQL projection\n")
        handle.write(f"-- dataset_version: {DATASET_VERSION}\n")
        handle.write("SET NAMES utf8mb4;\n")
        handle.write("START TRANSACTION;\n")
        handle.write("DELETE FROM `ozro_market_item_tag`;\n")
        handle.write("DELETE FROM `ozro_market_item`;\n")

        columns = (
            "item_id, name, aegis, type, slots, refineable, weight, custom, "
            "price_status, low, mid, high, npc_buy, npc_sell, supply_open, "
            "supply_percentile, abundance_tier, difficulty_percentile, difficulty_tier, "
            "demand_percentile, demand_tier, market_pressure, stock_hint, restock_weight, "
            "market_eligible, npc_eligible, dataset_version"
        )
        for batch in chunks(rows, 500):
            values = []
            for row in batch:
                price = row["price"]
                supply = row["supply"]
                demand = row["demand"]
                values.append(
                    "("
                    + ", ".join(
                        [
                            sql_num(row["itemId"]),
                            sql_str(row["name"]),
                            sql_str(row["aegis"]),
                            sql_str(row["type"]),
                            sql_num(row["slots"]),
                            sql_num(row["refineable"]),
                            sql_num(row["weight"]),
                            sql_num(row["custom"]),
                            sql_str(price["status"]),
                            sql_num(price["low"]),
                            sql_num(price["mid"]),
                            sql_num(price["high"]),
                            sql_num(price["npcBuyPrice"]),
                            sql_num(price["npcSellPrice"]),
                            sql_num(supply["open"]),
                            sql_num(supply["percentile"]),
                            sql_str(supply["abundanceTier"]),
                            sql_num(supply["difficultyPercentile"]),
                            sql_str(supply["difficultyTier"]),
                            sql_num(demand["percentile"]),
                            sql_str(demand["tier"]),
                            sql_num(demand["marketPressure"]),
                            sql_str(demand["stockHint"]),
                            sql_num(demand["restockWeight"]),
                            sql_num(row["marketEligible"]),
                            sql_num(row["npcEligible"]),
                            sql_str(DATASET_VERSION),
                        ]
                    )
                    + ")"
                )
            handle.write(f"INSERT INTO `ozro_market_item` ({columns}) VALUES\n")
            handle.write(",\n".join(values))
            handle.write(";\n")

        for batch in chunks(tag_rows, 1000):
            values = [f"({sql_num(item_id)}, {sql_str(tag)})" for item_id, tag in batch]
            handle.write("INSERT INTO `ozro_market_item_tag` (item_id, tag) VALUES\n")
            handle.write(",\n".join(values))
            handle.write(";\n")

        handle.write("COMMIT;\n")

    print(f"items={len(rows)} market={status.get('market', 0)} synthetic={status.get('synthetic', 0)} manual={status.get('manual', 0)}")
    print(f"jsonl={OUT_JSONL}")
    print(f"sql={OUT_SQL}")
    print(f"summary={OUT_SUMMARY}")


if __name__ == "__main__":
    main()
