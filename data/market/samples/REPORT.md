# Muestra de la master de mercado

Semilla: `20261118`. Los datos completos están en `general.jsonl` y `edge.jsonl`.

## Fuentes y rates

- Items en la taxonomía: 29061
- Items con supply abierto: 1620
- Items con histórico: 5858
- Precio `market`: 5847
- Precio `synthetic`: 23209
- Precio `manual`: 5
- `not_applicable`: 0
- `marketEligible`: 9622
- Clampeados por ancla: 1266
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
| `['no_source', 'not_market_eligible', 'unobtainable']` | 7 |
| `['untradeable']` | 7 |
| `['boss_only']` | 5 |
| `['custom', 'manual_price']` | 5 |
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
| `['no_source', 'unobtainable']` | 1 |
| `['not_market_eligible', 'untradeable']` | 1 |
| `['npc_shop', 'priced_low_confidence']` | 1 |

## Señales detectadas

### Sintéticos más caros

| Item | Tipo | mid | supply abierto | review |
|---|---|---:|---:|---|
| Bubble Gum Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |
| Assumptio 5 Scroll Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |
| Aspersio Scroll Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |
| Lex Aeterna Scroll Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |
| Blessing Scroll 10 Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |
| Increase Agility Scroll 10 Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |
| Ramen Hat Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |
| Light Blue Potion Box | Cash | 5,330,000 | 0.0000 | no_open_supply, not_market_eligible, synthetic_price |

### Precio de mercado por encima del techo NPC

| Item | mid | ceiling | fuente |
|---|---:|---:|---|
| (ninguno en la muestra completa) | | | |

### Sin supply abierto y precio alto

| Item | mid | access | sources |
|---|---:|---|---|
| Haedonggum | 1,820,000 | craft | craft, group |
| Edge | 6,540,000 | unknown | group, mob_drop, quest_reward, unknown_drop |
| Solar Sword | 48,030,000 | group | group |
| Byeollungum | 10,060,000 | normal | group, mob_drop, normal_drop, quest_reward |
| Immaterial Sword | 36,460,000 | unknown | group, mob_drop, quest_reward, unknown_drop |
| Bloody Eater | 2,020,000 | normal | group, mob_drop, normal_drop |
| Violet Fear | 73,210,000 | group | group, instance_reward |
| Alca Bringer | 1,720,000 | unknown | group, mob_drop, unknown_drop |

## Decisiones aplicadas en esta muestra

- `supplyOpen` excluye boss, instancia, guild, quest y event; usa field + dungeon.
- El HP efectivo aplica `monster_hp_rate`/`mvp_hp_rate` (2x).
- El precio sintético usa type_p40 + multiplicadores de supply, demanda, dificultad, factor de fuente (group 0.70, craft 0.90, quest/instancia 0.80, sin fuente 0.50) y factor de equipo.
- Items sin fuente usan min(type_p10, 1M) * 0.50.
- `npcBuyPrice`: sintético 45% del mid con cap de 50% de la mediana del tipo; market high 75%; medium 60% con cap de 1 mediana; low 45% / low 75%; manipulación 35% / low 70%.
- `npcSellPrice` usa margen y se limita a 1.10–1.50x del `npcBuyPrice`.
- La manipulación se marca con CV > 3 o `atlantis_extreme_max`, sin listas de excepciones.
- Los tags vienen de categorías de taxonomía + restricciones de acceso.
