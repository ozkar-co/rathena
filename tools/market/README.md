# Market tools

Sample pipeline for the future OzRo market master. The taxonomy is an
intermediate artifact; the master is the source of truth.

## Build the sample

```bash
python3 tools/market/build_sample.py
```

Outputs:

- `data/market/samples/general.jsonl`
- `data/market/samples/edge.jsonl`
- `data/market/samples/summary.json`
- `data/market/samples/REPORT.md`

## Inputs

- `ozro-site/assets/items/taxonomy.json`
- `conf/import/battle_conf.txt` (drop rates + HP rates)
- canonical spawns from `tools/mob_spawns.py`
- `ragnabots/staging/market/pricing/master_list.json` (historical reference only)

## Decisions in this pass

- `supplyOpen = field + dungeon`; boss/instance/guild/quest/event/other are separate.
- Effective HP uses `monster_hp_rate`/`mvp_hp_rate` (currently 2x).
- `marketEligible` and `priceStatus` separate catalog items from priced items.
- Synthetic prices use type median + supply/demand/difficulty multipliers and a
  general source-quality factor.
- `buyCeiling` is conservative; the `high` is never used for NPC purchases.
