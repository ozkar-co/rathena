# Esquema del master de mercado

**Estado:** contrato v2 (previo al master completo)  
**Canon:** `data/market/canon.yml`  
**Technical spec:** `data/market/SPEC.md`  
**Muestra:** `data/market/samples/`  
**Herramientas:** `tools/market/`

---

## 1. Archivos

| Archivo | Rol |
|---|---|
| `data/market/canon.yml` | Decisiones aprobadas y precios manuales. |
| `data/market/components.yml` | Tablas de refine/cartas/slots/encantamientos. |
| `data/market/samples/general.jsonl` | Muestra de items market-eligible. |
| `data/market/samples/edge.jsonl` | Casos borde. |
| `data/market/samples/composed.jsonl` | Ejemplos de objetos compuestos. |
| `data/market/samples/summary.json` | Conteos y distribución. |
| `tools/market/build_sample.py` | Generador de la muestra. |
| `tools/market/valuation.py` | Contrato `compose_value`. |

La taxonomía (`ozro-site/assets/items/taxonomy.json`) es un insumo intermedio. El master final será la fuente de verdad.

---

## 2. Registro base

Cada fila de item tiene:

```json
{
  "schemaVersion": 1,
  "itemId": 7003,
  "name": "Anolian Skin",
  "aegis": "Anolian_Skin",
  "type": "Etc",
  "slots": 0,
  "refineable": false,
  "custom": false,
  "npcEligible": true,
  "marketEligible": true,
  "tags": ["mob_drop", "normal_drop"],
  "sources": ["mob_drop", "normal_drop"],
  "access": {},
  "groupInfo": {},
  "craftRecipe": null,
  "craftCost": null,
  "cash": null,
  "supply": {},
  "demand": {},
  "npc": {},
  "price": {},
  "reviewReasons": []
}
```

### 2.1 `access`

| Campo | Significado |
|---|---|
| `best` | Mejor acceso: normal, guild, instance, npc, cash, craft, quest, group, unknown, none. |
| `normalMaps` / `guildMaps` / `instanceMaps` | Mapas de drop por tipo. |
| `dropMobs` / `spawnMobs` | Mobs que dropean y cuántos tienen spawn. |
| `bossOnly` | Todos los mobs de drop son boss/MVP. |
| `minMobHp` / `maxMobHp` | HP efectivo (2x) de las fuentes con spawn. |
| `highHp` / `highHpSource` | Fuente más fácil / alguna fuente supera el umbral. |
| `noSpawn` | Hay drop mobs sin spawn conocido. |
| `restrictions` | Tags: `instance_only`, `guild_only`, `quest_source`, `boss_only`, `high_hp`, `high_hp_source`, `no_spawn`. |
| `commonFarmEligible` | Mapa normal, no boss-only, no high-HP. |

### 2.2 `supply`

| Campo | Significado |
|---|---|
| `open` | Flujo de field + dungeon. |
| `total` | Flujo de todas las fuentes, incluyendo boss/instancia/guild/quest. |
| `percentile` | Percentil de `open` entre items con supply. |
| `abundanceTier` | abundant, common, uncommon, scarce, rare, none. |
| `difficulty` / `difficultyPercentile` / `difficultyTier` | Costo relativo de farmeo. |

Flujo:

```
eff_rate = min(10000, base_rate * rate_mult) / 10000
flow = spawn_amount * eff_rate * access_factor * 60 / max(delay_seconds, 1)
supplyOpen = field + dungeon
```

### 2.3 `demand`

| Campo | Significado |
|---|---|
| `salesLatam` / `salesAtlantis` | Ventas acumuladas de cada fuente. |
| `soldForRank` | Ventas usadas para ranking histórico. |
| `residual` | Demanda residual combinada. |
| `latamResidual` / `atlantisResidual` | Residual por fuente. |
| `sources` | 0, 1 o 2 fuentes con ventas. |
| `percentile` / `tier` | Percentil y tier de demanda. |
| `marketPressure` | `demandPercentile - supplyPercentile`. |
| `stockHint` | low, normal, high, unknown. |
| `restockWeight` | 0,1–0,9 para stock/frecuencia futura. |

La demanda residual se calcula contra la mediana de ventas del mismo `(tipo, abundanceTier)`, con fallback por tipo. LATAM y Atlantis se ponderan por `log1p(total_sold)`.

### 2.4 `price`

| Campo | Significado |
|---|---|
| `status` | market, synthetic, manual. |
| `baseMethod` | historical, type_p40, no_source_cap, craft_cost, manual. |
| `historicalReference` / `historicalConfidence` / `historicalCv` | Histórico crudo. |
| `manipulationSuspected` | CV > 3 o `atlantis_extreme_max`. |
| `base` / `sourceFactor` / `gearFactor` | Base y factores aplicados. |
| `rawMid` / `clamped` | Mid antes de anclas y si fue clampeado. |
| `supplyMultiplier` / `demandMultiplier` / `difficultyMultiplier` | Ajustes. |
| `low` / `mid` / `high` | Banda canónica. |
| `npcBuyPrice` | Lo que el NPC paga al jugador. |
| `npcSellPrice` | Lo que el NPC cobra al jugador. |
| `sellMargin` | Margen usado para la venta. |
| `floor` / `ceiling` | Anclas NPC. |

Fórmula sintética:

```
base = type_p40 * sourceFactor * groupFactor * gearFactor
raw  = base * supplyMult * demandMult * difficultyMult
mid  = clamp(raw, floor, ceiling)
```

- `sourceFactor`: group/craft/quest/instancia/guild/unknown/none.
- `groupFactor`: `0.60 + 0.10 * (1 - bestGroupShare)`.
- `gearFactor`: slots, ataque/defensa y nivel mínimo; clamp 0,70–2,00.
- Sin fuente: `min(type_p10, 1.000.000) * 0,50`.
- Cap sintético: `type_p90`.
- Craft: `craftCost = suma(materiales * 1,15)`; si es mayor que el mid sintético, se usa como base.

### 2.5 Compra y venta

```
npcBuyPrice = política conservadora por status/confianza
candidate   = mid * (1 + sellMargin)
npcSellPrice = max(npcBuyPrice * 1.10, min(candidate, npcBuyPrice * 1.50))
```

La venta nunca usa el `high`. El spread se mantiene entre 1,10x y 1,50x del buy.

---

## 3. Tags

Los tags son meta-categorías múltiples:

- fuente: `mob_drop`, `normal_drop`, `instance_drop`, `guild_drop`, `npc_shop`, `cash_shop`, `quest_source`, `craft`, `group`.
- acceso: `instance_only`, `guild_only`, `boss_only`, `high_hp`, `no_spawn`.
- comercio: `untradeable`, `unobtainable`.
- uso: `craft_material`, `craft_output`, `used_in_combo`, `scripted`, `skill_cost`.
- calidad: `manipulation_suspected`, `synthetic_price`, `manual_price`, `no_source`.

Un item puede tener varios. Ningún tag es una exclusión automática.

---

## 4. Objetos compuestos

`tools/market/valuation.py`:

```python
compose_value(base_mid, refine, card_mids, slots, enchant_value)
```

```
baseValue   = base_mid * refineFactor
cardValue   = sum(card_mids) * 0.85
raw         = baseValue + cardValue + enchantValue
cap         = base_mid * 5 + cardValue * 1.5
value       = min(raw, cap)
```

- `refineFactors` en `components.yml` (+0 a +10).
- `enchantValue` es placeholder hasta mapear encantamientos.
- No se enumeran combinaciones; se calculan.

---

## 5. Reglas para consumidores

### NPC que compra

- Usar `npcBuyPrice`, nunca `mid` ni `high`.
- Si `status=synthetic`, respetar el cap y el spread.
- Si `manipulationSuspected`, usar la política reducida.
- Si `stockHint=low`, considerar stock menor o reposición más lenta.

### NPC que vende

- Usar `npcSellPrice`.
- No superar el precio de NPC shop o item mall si existe.
- Para items `manual`, usar el valor canónico.

### Web

- Mostrar `low/mid/high` con `status` y confianza.
- No mostrar precios sintéticos como si fueran históricos.

### Eventos y quests

- Presupuestar con `mid` y banda, no con `high`.
- Para recompensas de items sin mercado, usar `npcSellPrice` como referencia.

---

## 6. Regeneración

```bash
python3 tools/market/build_sample.py
```

La muestra no es el master final. El siguiente paso es `build_master.py`, que debe reutilizar `common.py`, `valuation.py` y `canon.yml`.
