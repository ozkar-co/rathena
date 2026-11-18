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
- `data/market/canon.yml` (manual prices and policies)

## Decisions in this pass

- All items receive a canonical price: `market`, `synthetic` or `manual`.
- `supplyOpen = field + dungeon`; boss/instance/guild/quest/event/other are separate.
- Effective HP uses `monster_hp_rate`/`mvp_hp_rate` (currently 2x).
- Synthetic base is `type_p40` plus source-factor and gear-factor adjustments.
- Items without source use `min(type_p10, 1M) * 0.50`.
- `npcBuyPrice` and `npcSellPrice` are separate, with a controlled spread.
- `marketPressure`, `stockHint` and `restockWeight` are stored for future NPC stock logic.
