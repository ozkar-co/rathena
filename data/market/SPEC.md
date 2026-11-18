# Market data technical specification

```
spec: ozro-market
version: 2
status: source_of_truth
canonical: data/market/canon.yml
generator: tools/market/build_sample.py
future_generator: tools/market/build_master.py
canonical_format: JSONL
record_key: itemId
```

---

## 1. Sources

| ID | Path | Role | Required |
|---|---|---|---|
| `taxonomy` | `ozro-site/assets/items/taxonomy.json` | item identity, sources, tags, access | yes |
| `battle_conf` | `conf/import/battle_conf.txt` | drop rates, HP rates | yes |
| `spawns` | `tools/mob_spawns.py` output | canonical spawns with delay/boss/instance | yes |
| `mob_db` | `db/re/mob_db.yml`, `db/import/mob_db.yml` | HP, DEF, MDEF, level, class | yes |
| `item_db` | `db/re/item_db*.yml`, `db/import/item_db.yml` | slots, refineable, ATK, DEF, equip level, Buy/Sell | yes |
| `item_groups` | `db/re/item_group_db.yml`, `db/import/item_group_db.yml` | group membership and rate | optional |
| `produce_db` | `db/re/produce_db.txt`, `db/import/produce_db.txt` | craft recipe materials | optional |
| `cash_shop` | `db/item_cash.yml`, `db/import/item_cash.yml` | cash price metadata | optional |
| `historical` | `ragnabots/staging/market/pricing/master_list.json` | historical price/sales reference | optional |
| `canon` | `data/market/canon.yml` | manual prices and policies | yes |
| `components` | `data/market/components.yml` | refine/card/slot/enchant tables | yes |

`historical` is reference only. It is not an absolute price source for OzRo.

---

## 2. Record schema

Each JSONL row:

```json
{
  "schemaVersion": 1,
  "itemId": 0,
  "name": "",
  "aegis": "",
  "type": "",
  "slots": 0,
  "refineable": false,
  "custom": false,
  "npcEligible": true,
  "marketEligible": true,
  "tags": [],
  "sources": [],
  "access": {},
  "groupInfo": {},
  "craftRecipe": null,
  "craftCost": null,
  "cash": null,
  "spawnSupply": {},
  "supply": {},
  "demand": {},
  "npc": {},
  "price": {},
  "reviewReasons": []
}
```

### 2.1 Identity

| Field | Type | Notes |
|---|---|---|
| `itemId` | int | primary key, stable |
| `name` | string | display name |
| `aegis` | string | AegisName |
| `type` | string | item type from `item_db` |
| `slots` | int | card slots |
| `refineable` | bool | from `item_db` |
| `custom` | bool | loaded from `db/import/item_db.yml` |
| `npcEligible` | bool | true for all items; NPC can buy/sell any item |
| `marketEligible` | bool | tradeable and (obtainable or has historical price) and (has source or historical price) |

### 2.2 `tags`

List of strings. Derived from taxonomy categories + `access.restrictions`. A row can have multiple tags.

Tag groups:

```
source: mob_drop, normal_drop, instance_drop, guild_drop, npc_shop, cash_shop, quest_source, craft, group
access: instance_only, guild_only, boss_only, high_hp, high_hp_source, no_spawn
trade: untradeable, unobtainable
use: craft_material, craft_output, used_in_combo, scripted, skill_cost
quality: manipulation_suspected, synthetic_price, manual_price, no_source, not_market_eligible
```

### 2.3 `access`

| Field | Type | Definition |
|---|---|---|
| `best` | enum | `normal`, `guild`, `instance`, `npc`, `cash`, `craft`, `quest`, `group`, `unknown`, `none` |
| `normalMaps` | int | known normal drop maps |
| `guildMaps` | int | known guild drop maps |
| `instanceMaps` | int | known instance drop maps |
| `dropMobs` | int | distinct drop mobs |
| `spawnMobs` | int | drop mobs with known spawn |
| `bossOnly` | bool | all drop mobs are boss/MVP |
| `minMobHp` | int/null | minimum effective HP among spawn-capable drop mobs |
| `maxMobHp` | int/null | maximum effective HP among spawn-capable drop mobs |
| `minMobLevel` / `maxMobLevel` | int/null | levels of spawn-capable drop mobs |
| `highHp` | bool | `minMobHp >= high_hp_threshold` |
| `highHpSource` | bool | `maxMobHp >= high_hp_threshold` and `highHp == false` |
| `noSpawn` | bool | `dropMobs > 0` and `spawnMobs == 0` |
| `restrictions` | string[] | derived restriction tags |
| `commonFarmEligible` | bool | `normalMaps > 0 and not bossOnly and not highHp` |

Effective HP:

```
hp_effective = hp_db * hp_rate / 100
hp_rate = mvp_hp_rate if mob.Class == "Boss" else monster_hp_rate
```

### 2.4 `supply`

| Field | Type | Definition |
|---|---|---|
| `open` | float | `field + dungeon` flow |
| `total` | float | sum of all flow types |
| `percentile` | float/null | percentile of `open` among items with `open > 0` |
| `abundanceTier` | enum | `abundant`, `common`, `uncommon`, `scarce`, `rare`, `none` |
| `difficulty` | float/null | flow-weighted mean threat |
| `difficultyPercentile` | float/null | percentile of `difficulty` |
| `difficultyTier` | enum | `easy`, `medium`, `hard`, `extreme`, `unknown` |

### 2.5 `spawnSupply`

Keys: `field`, `dungeon`, `other`, `boss`, `instance`, `guild`, `quest`, `event`.

Values are the computed flow for that spawn type.

### 2.6 `demand`

| Field | Type | Definition |
|---|---|---|
| `salesLatam` | int/null | LATAM total sold |
| `salesAtlantis` | int/null | Atlantis total sold |
| `soldForRank` | int/null | historical rank sales |
| `residual` | float/null | combined residual |
| `latamResidual` | float/null | LATAM residual |
| `atlantisResidual` | float/null | Atlantis residual |
| `sources` | int | number of sources with sales: 0, 1, 2 |
| `percentile` | float/null | percentile of combined residual |
| `tier` | enum | `high`, `medium`, `low`, `none`, `unknown` |
| `marketPressure` | float/null | `demandPercentile - supplyPercentile` |
| `stockHint` | enum | `low`, `normal`, `high`, `unknown` |
| `restockWeight` | float/null | `clamp(0.5 + marketPressure/200, 0.1, 0.9)` |

### 2.7 `npc`

| Field | Type | Definition |
|---|---|---|
| `sellToPlayer` | int | `item_db.Buy` |
| `buyFromPlayer` | int | `item_db.Sell` |
| `shop` | bool | item appears in an NPC shop |

### 2.8 `price`

| Field | Type | Definition |
|---|---|---|
| `status` | enum | `market`, `synthetic`, `manual` |
| `baseMethod` | enum | `historical`, `type_p40`, `no_source_cap`, `craft_cost`, `manual` |
| `historicalReference` | int/null | raw historical reference |
| `historicalSource` | string/null | historical source id |
| `historicalConfidence` | string/null | high/medium/low/server |
| `historicalCv` | float/null | Atlantis CV |
| `manipulationSuspected` | bool | CV > 3 or `atlantis_extreme_max` |
| `base` | int | base before multipliers |
| `sourceFactor` | float | source-quality factor |
| `gearFactor` | float | equipment factor |
| `rawMid` | int | raw before anchors |
| `clamped` | bool | raw outside floor/ceiling |
| `supplyMultiplier` | float | supply adjustment |
| `demandMultiplier` | float | demand adjustment |
| `difficultyMultiplier` | float | difficulty adjustment |
| `low` / `mid` / `high` | int | canonical band |
| `npcBuyPrice` | int | NPC pays player |
| `npcSellPrice` | int | NPC charges player |
| `sellMargin` | float | margin used for `npcSellPrice` |
| `floor` / `ceiling` | int/null | NPC anchors |
| `uncertainty` | float | band uncertainty |

---

## 3. Formulas

### 3.1 Drop rate

```
category = map(item.type)
mult = mvp_rate(category)       if drop.mvp
       boss_rate(category)      if spawn.boss or mob.Class == "Boss"
       normal_rate(category)
eff_rate = min(10000, base_rate * mult // 100) / 10000
```

Rate categories:

```
Card -> card
Healing -> heal
Usable, DelayConsume, Cash -> use
Weapon, Armor, ShadowGear, Shadowgear, Ammo -> equip
other -> common
```

### 3.2 Supply flow

```
delay_s = spawn.delay / 1000 if spawn.delay > 0 else 10
flow = spawn.amount * eff_rate * access_factor * 60 / max(delay_s, 1)
```

Access factors:

```
field 1.00
dungeon 0.85
quest 0.40
instance 0.15
guild 0.10
event 0.00
other 0.50
```

```
supplyOpen = flow[field] + flow[dungeon]
supplyTotal = sum(flow.values())
```

### 3.3 Difficulty

```
threat = log1p(hp_effective)
       * (1 + def/100 + mdef/200)
       * (1 + 0.5 * is_boss)
       * (1 + 0.2 * max(0, level - 100) / 50)
```

`difficulty` is the flow-weighted mean of `threat` over source spawns.

### 3.4 Demand residual

For each source `s in {latam, atlantis}`:

```
key = (type, abundanceTier)
expected_s = median(log1p(sold_s) for same key)
fallback_s = median(log1p(sold_s) for same type)
residual_s = log1p(sold_s) - expected_s   (fallback if key missing)
```

Combine:

```
weights = log1p(sold_s) capped at 15
residual = sum(residual_s * weight_s) / sum(weight_s)
```

### 3.5 Price base

Historical:

```
base = historicalReference
baseMethod = "historical"
```

Manual:

```
base = canon.pricing.manual_prices[itemId]
baseMethod = "manual"
```

Synthetic:

```
sourceFactor = source_factor[access.best]
groupShare = groupInfo.bestShare
groupFactor = 0.60 + 0.10 * (1 - groupShare)       if access.best == "group"
gearFactor = clamp(
    1 + 0.08*slots + 0.05*log1p(max(0, atk+def)) + 0.10*max(0, equipLevelMin-50)/50,
    0.70,
    2.00
)                                                   if type in equipment
base = type_p40 * sourceFactor * groupFactor * gearFactor
baseMethod = "type_p40"
```

No source:

```
base = min(type_p10, 1000000) * 0.50
sourceFactor = 0.50
baseMethod = "no_source_cap"
```

Source factors:

```
group 0.70
craft 0.90
quest 0.80
instance 0.80
guild 0.70
unknown 0.50
none 0.50
normal 1.00
npc 1.00
cash 1.00
```

### 3.6 Price multipliers

```
medianOpenSupply = median(supplyOpen for supplyOpen > 0)

supplyMultiplier = clamp((medianOpenSupply / supplyOpen) ** 0.25, 0.5, 2.0)  if supplyOpen > 0 else 1.0
demandZ = ((demandPercentile or 50) - 50) / 50
demandMultiplier = clamp(1 + 0.25 * demandZ, 0.7, 1.5)
difficultyZ = ((difficultyPercentile or 50) - 50) / 50
difficultyMultiplier = clamp(1 + 0.15 * difficultyZ, 0.8, 1.5)

raw = base * supplyMultiplier * demandMultiplier * difficultyMultiplier
mid = clamp(raw, floor, ceiling)
```

Synthetic cap:

```
if status == "synthetic" and has_source:
    mid = min(mid, type_p90)
```

### 3.7 NPC anchors

```
floor = npc.buyFromPlayer * 1.05  if npc.buyFromPlayer > 0 else 1
ceiling = npc.sellToPlayer * 0.95 if npc.shop and npc.sellToPlayer > 0 else +inf
```

### 3.8 NPC buy price

```
manual:        mid
synthetic:     min(mid * 0.45, typeMedian * 0.50)
manipulation:  min(mid * 0.35, low * 0.70, typeMedian * 0.50)
market high:   mid * 0.75
market medium: min(mid * 0.60, typeMedian)
market server: min(mid * 0.60, npc.buyFromPlayer)
market low:    min(mid * 0.45, low * 0.75, typeMedian * 0.50)

npcBuyPrice = min(candidate, ceiling * 0.95, high * 0.80)
npcBuyPrice = max(floor, npcBuyPrice)
```

### 3.9 NPC sell price

```
sellMargin:
    manual 0.00
    market high 0.10
    market medium/server 0.20
    market low 0.30
    synthetic 0.35
    manipulation 0.50

candidate = mid * (1 + sellMargin)
npcSellPrice = max(npcBuyPrice * 1.10, min(candidate, npcBuyPrice * 1.50))
npcSellPrice = min(npcSellPrice, ceiling)
npcSellPrice = max(npcSellPrice, npcBuyPrice * 1.05)
```

### 3.10 Price band

```
uncertainty:
    high 0.15
    medium 0.30
    low 0.50
    server 0.20
    synthetic >= 0.50

low = max(floor, mid * (1 - uncertainty))
high = min(ceiling, mid * (1 + uncertainty))
if high <= low: high = low * 1.05
```

### 3.11 Stock

```
marketPressure = demandPercentile - supplyPercentile
stockHint = low    if marketPressure > 25
            high   if marketPressure < -25
            normal otherwise
restockWeight = clamp(0.5 + marketPressure/200, 0.1, 0.9)
```

### 3.12 Composed items

```
baseValue = baseMid * refineFactor
cardValue = sum(cardMids) * 0.85
raw = baseValue + cardValue + enchantValue
cap = baseMid * 5 + cardValue * 1.5
value = min(raw, cap)
```

`refineFactor` from `data/market/components.yml`:

```
+0 1.00  +1 1.03  +2 1.07  +3 1.12  +4 1.18
+5 1.25  +6 1.34  +7 1.45  +8 1.58  +9 1.74  +10 1.93
```

---

## 4. Enums

```
price.status: market | synthetic | manual
price.baseMethod: historical | type_p40 | no_source_cap | craft_cost | manual
access.best: normal | guild | instance | npc | cash | craft | quest | group | unknown | none
abundanceTier: abundant | common | uncommon | scarce | rare | none
difficultyTier: easy | medium | hard | extreme | unknown
demand.tier: high | medium | low | none | unknown
stockHint: low | normal | high | unknown
```

---

## 5. Invariants

```
itemId is unique and positive
price.status in {market, synthetic, manual}
low <= mid <= high
npcBuyPrice <= mid
npcSellPrice >= npcBuyPrice
npcSellPrice <= ceiling if ceiling is not null
manual prices equal canon.pricing.manual_prices[itemId]
market -> historicalReference > 0
synthetic -> baseMethod in {type_p40, no_source_cap, craft_cost}
untradeable items can be priced but are not player-tradeable
instance_only/guild_only items are not commonFarmEligible
highHp == (minMobHp >= high_hp_threshold)
```

---

## 6. Storage

### 6.1 Canonical

`data/market/master.jsonl` (future full build) or the current sample JSONL. One row per `itemId`, sorted by `itemId`.

### 6.2 Web database

The website already uses the game DB. Recommended projection:

```sql
CREATE TABLE ozro_market_item (
  item_id INT UNSIGNED NOT NULL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  type VARCHAR(32) NOT NULL,
  price_status ENUM('market','synthetic','manual') NOT NULL,
  low BIGINT UNSIGNED NOT NULL,
  mid BIGINT UNSIGNED NOT NULL,
  high BIGINT UNSIGNED NOT NULL,
  npc_buy BIGINT UNSIGNED NOT NULL,
  npc_sell BIGINT UNSIGNED NOT NULL,
  supply_open DOUBLE NOT NULL,
  supply_percentile DOUBLE NULL,
  abundance_tier VARCHAR(16) NOT NULL,
  difficulty_percentile DOUBLE NULL,
  difficulty_tier VARCHAR(16) NOT NULL,
  demand_percentile DOUBLE NULL,
  demand_tier VARCHAR(16) NOT NULL,
  market_pressure DOUBLE NULL,
  stock_hint VARCHAR(16) NOT NULL,
  restock_weight DOUBLE NULL,
  market_eligible TINYINT(1) NOT NULL,
  npc_eligible TINYINT(1) NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE ozro_market_item_tag (
  item_id INT UNSIGNED NOT NULL,
  tag VARCHAR(48) NOT NULL,
  PRIMARY KEY (item_id, tag),
  KEY idx_tag (tag)
);
```

SQL is a generated projection, not the source of truth. The canonical data remains JSONL + `canon.yml`.

### 6.3 NPC

- Curated NPCs: generated static arrays/constants in the script. Safer and self-contained.
- Dynamic lookup (tasador/search): read-only `SELECT` from `ozro_market_item` via `query_sql`, with item_id PK.
- Do not query the table in tight loops or per dialog page.

---

## 7. Regeneration

```bash
python3 tools/market/build_sample.py
```

Future full build:

```bash
python3 tools/market/build_master.py
```

Outputs must be deterministic. Manual changes go only in `canon.yml` and `components.yml`.
