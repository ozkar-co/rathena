# Muestra de la master de mercado

Semilla: `20261118`. Los datos completos están en `general.jsonl` y `edge.jsonl`.

## Fuentes y rates

- Items en la taxonomía: 29061
- Items con supply abierto: 1620
- Items con histórico: 5858
- Precio `market`: 5847
- Precio `synthetic`: 3970
- `not_applicable`: 19244
- `marketEligible`: 9622
- Clampeados por ancla: 1004
- Manipulación sospechada: 166

```json
{
  "item_rate_common": 500,
  "item_rate_common_boss": 500,
  "item_rate_heal": 1000,
  "item_rate_heal_boss": 1000,
  "item_rate_use": 1000,
  "item_rate_use_boss": 1000,
  "item_rate_equip": 1500,
  "item_rate_equip_boss": 1500,
  "item_rate_card": 1000,
  "item_rate_card_boss": 10000,
  "item_rate_card_mvp": 10000,
  "item_rate_mvp": 500,
  "item_rate_treasure": 500,
  "mvp_hp_rate": 200,
  "monster_hp_rate": 200
}
```

## Spawns

Total: 3656 spawns, 405 mapas, 1223 mobs.

| Tipo de spawn | Líneas |
|---|---:|
| `boss` | 75 |
| `dungeon` | 1521 |
| `field` | 1161 |
| `guild` | 61 |
| `instance` | 53 |
| `other` | 306 |
| `quest` | 479 |

## Muestra general

### Tipos

| Valor | n |
|---|---:|
| `Armor` | 38 |
| `Etc` | 38 |
| `Weapon` | 21 |
| `Card` | 18 |
| `Usable` | 8 |
| `Shadowgear` | 7 |
| `ShadowGear` | 6 |
| `DelayConsume` | 5 |
| `Healing` | 3 |
| `Ammo` | 2 |

### Estado de precio

| Valor | n |
|---|---:|
| `market` | 101 |
| `synthetic` | 49 |

### Acceso

| Valor | n |
|---|---:|
| `group` | 57 |
| `normal` | 33 |
| `craft` | 23 |
| `npc` | 14 |
| `unknown` | 10 |
| `none` | 6 |
| `instance` | 4 |
| `quest` | 3 |

### Abundancia

| Valor | n |
|---|---:|
| `none` | 123 |
| `common` | 7 |
| `uncommon` | 7 |
| `abundant` | 6 |
| `scarce` | 4 |
| `rare` | 3 |

### Dificultad

| Valor | n |
|---|---:|
| `unknown` | 116 |
| `easy` | 18 |
| `hard` | 8 |
| `medium` | 6 |
| `extreme` | 2 |

## Casos borde

| Categoría | Items |
|---|---:|
| `['craft_best']` | 8 |
| `['guild_only']` | 8 |
| `['min_open_supply']` | 8 |
| `['no_price_with_open_supply']` | 8 |
| `['price_top_1pct']` | 8 |
| `['group_only']` | 7 |
| `['high_hp']` | 7 |
| `['instance_only']` | 7 |
| `['boss_only']` | 5 |
| `['custom']` | 5 |
| `['max_open_supply']` | 5 |
| `['price_bottom_1pct']` | 5 |
| `['priced_low_confidence']` | 3 |
| `['manipulation_suspected', 'market_eligible', 'market_price', 'npc_shop']` | 2 |
| `['manipulation_suspected', 'priced_low_confidence']` | 2 |
| `['market_eligible', 'market_price', 'npc_shop', 'priced_high_confidence']` | 2 |
| `['priced_high_confidence']` | 2 |
| `['boss_only', 'high_hp']` | 1 |
| `['boss_only', 'market_eligible', 'market_price', 'npc_shop', 'priced_high_confidence']` | 1 |
| `['boss_only', 'priced_low_confidence']` | 1 |
| `['group_only', 'market_eligible']` | 1 |
| `['instance_only', 'price_bottom_1pct']` | 1 |
| `['manipulation_suspected', 'market_eligible', 'market_price', 'max_open_supply', 'priced_high_confidence']` | 1 |
| `['manipulation_suspected', 'market_eligible', 'market_price', 'npc_shop', 'price_bottom_1pct', 'priced_high_confidence']` | 1 |
| `['manipulation_suspected', 'market_price', 'max_open_supply']` | 1 |
| `['manipulation_suspected', 'npc_shop', 'price_bottom_1pct', 'priced_low_confidence']` | 1 |
| `['max_open_supply', 'priced_high_confidence']` | 1 |
| `['npc_shop', 'priced_low_confidence']` | 1 |

## Señales detectadas

### Sintéticos más caros

| Item | Tipo | mid | supply abierto | review |
|---|---|---:|---:|---|
| Memory Book | Armor | 9,490,000 | 0.0459 | synthetic_price |
| Eye Stone Ring | Armor | 9,430,000 | 0.0002 | synthetic_price |
| Sura Gauntlet | Armor | 9,220,000 | 0.0153 | synthetic_price |
| Ghost Bandana | Armor | 9,210,000 | 0.0153 | synthetic_price |
| Pocket Watch | Armor | 9,060,000 | 0.0009 | synthetic_price |
| Cursed Star | Armor | 9,020,000 | 0.1726 | synthetic_price |
| Kandura | Armor | 8,860,000 | 0.3825 | synthetic_price |
| High Fashion Sandals | Armor | 8,790,000 | 0.4131 | synthetic_price |

### Precio de mercado por encima del techo NPC

| Item | mid | ceiling | fuente |
|---|---:|---:|---|
| (ninguno en la muestra completa) | | | |

### Sin supply abierto y precio alto

| Item | mid | access | sources |
|---|---:|---|---|
| Rapier | 1,100,000 | normal | craft, group, mob_drop, normal_drop |
| Haedonggum | 1,820,000 | craft | craft, group |
| Edge | 6,540,000 | unknown | group, mob_drop, quest_reward, unknown_drop |
| Solar Sword | 48,030,000 | group | group |
| Byeollungum | 10,060,000 | normal | group, mob_drop, normal_drop, quest_reward |
| Immaterial Sword | 36,460,000 | unknown | group, mob_drop, quest_reward, unknown_drop |
| Schweizersabel | 1,150,000 | normal | group, mob_drop, normal_drop, quest_reward |
| Muscle Cutter | 1,100,000 | normal | group, mob_drop, normal_drop |

## Decisiones aplicadas en esta muestra

- `supplyOpen` excluye boss, instancia, guild, quest y event; usa field + dungeon.
- El HP efectivo aplica `monster_hp_rate`/`mvp_hp_rate` (2x).
- El precio sintético usa mediana del tipo + multiplicadores de supply, demanda, dificultad y un factor de calidad de fuente (group 0.70, craft 0.90, quest/instancia 0.80, sin fuente 0.50).
- `buyCeiling`: sintético 45% del mid con cap de 50% de la mediana del tipo; market high 75%; medium 60% con cap de 1 mediana; low 45% / low 75%; manipulación 35% / low 70%.
- La manipulación se marca con CV > 3 o `atlantis_extreme_max`, sin listas de excepciones.
- Los tags vienen de categorías de taxonomía + restricciones de acceso.
