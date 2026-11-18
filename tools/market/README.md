# Market tools

Technical specification: `data/market/SPEC.md`.

## Build the master

```bash
python3 tools/market/build_master.py
```

Outputs:

- `data/market/master.jsonl`
- `data/market/master_summary.json`
- `data/market/sql/ozro_market_data.sql`

## Build Garrett data

```bash
python3 tools/market/propose_garrett.py
```

Writes:

- `ozro-site/assets/items/garrett.json`
- `data/market/samples/garrett_proposal.json`
- `data/market/samples/garrett_proposal.md`

## Inputs

- `ozro-site/assets/items/taxonomy.json`
- `conf/import/battle_conf.txt` (drop rates + HP rates)
- canonical spawns from `tools/mob_spawns.py`
- `ragnabots/staging/market/pricing/master_list.json` (historical reference only)
- `data/market/canon.yml`
- `data/market/components.yml`

## Rules

- All items receive a canonical price: `market`, `synthetic` or `manual`.
- `supplyOpen = field + dungeon`; boss/instance/guild/quest/event/other are separate.
- Effective HP uses `monster_hp_rate`/`mvp_hp_rate` (currently 2x).
- Synthetic base is `type_p40` plus source, group, gear and `type_p90` cap adjustments.
- Items without source use `min(type_p10, 1M) * 0.50`.
- `npcBuyPrice` and `npcSellPrice` are separate, with a controlled spread.
- Garrett excludes cards, `scarce`/`rare` abundance and items used by repeatable
  custom NPCs in `npc/custom/ozro/repeteables/`.
