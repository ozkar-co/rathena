# Muestra de la master de mercado

**Estado:** muestra iterada v2 (no es el master final)
**Fecha:** 2026-11-18  
**Herramientas:** `tools/market/common.py`, `tools/market/build_sample.py`  
**Datos:** `data/market/samples/general.jsonl`, `edge.jsonl`, `summary.json`, `REPORT.md`  
**Canon:** `data/market/canon.yml`

---

## 1. Qué se construyó

`build_sample.py` cruza:

- `taxonomy.json` como catálogo intermedio (identidad, fuentes, tags, acceso);
- `conf/import/battle_conf.txt` para rates de drop y HP actuales;
- spawns canónicos generados con `tools/mob_spawns.py`;
- `mob_db`/`item_db` del servidor para HP, defensa, slots, refine y stats de equipo;
- `master_list.json` solo como histórico de precio/ventas;
- `data/market/canon.yml` para precios manuales y políticas.

Comando:

```bash
python3 tools/market/build_sample.py
```

Salida:

- `general.jsonl`: 150 items de la población market-eligible.
- `edge.jsonl`: 119 casos borde con `edgeTags`.
- `composed.jsonl`: 48 ejemplos de objetos compuestos (refine + cartas).
- `summary.json`: conteos, rates, tipos de spawn y distribución.
- `REPORT.md`: reporte generado.

---

## 2. Decisiones aplicadas

### 2.1 Fuentes canónicas

- Rates desde `conf/import/battle_conf.txt`, no desde el snapshot viejo de ragnabots.
- HP efectivo con `monster_hp_rate` y `mvp_hp_rate` (hoy 200%, es decir, 2x).
- Spawns desde `tools/mob_spawns.py`, con `delay`, `is_boss` e `is_instance`.

### 2.2 Tipos de spawn

| Tipo | Líneas |
|---|---:|
| `field` | 1.161 |
| `dungeon` | 1.521 |
| `boss` | 75 |
| `guild` | 61 |
| `instance` | 53 |
| `quest` | 479 |
| `other` | 306 |
| `event` | 0 |

`supplyOpen` usa solo `field + dungeon`. Boss, instancia, guild, quest, event y other se guardan aparte.

### 2.3 Precio canónico para todos los items

Ahora **todos los items tienen precio**. No hay `not_applicable`:

- `market`: hay precio histórico.
- `manual`: precio fijo definido en `canon.yml`.
- `synthetic`: calculado con la fórmula canónica.

Precios manuales:

| Item | Precio |
|---|---:|
| Moneda de Bronce | 100.000z |
| Moneda de Plata | 1.000.000z |
| Moneda de Oro | 10.000.000z |
| Moneda de Platino | 100.000.000z |
| Alma de MVP | 500.000z |

Fórmula sintética:

1. Base `type_p40`: percentil 40 de los precios históricos del mismo tipo, no la mediana. Es más conservador.
2. Factor de calidad de fuente:

| Mejor acceso | Factor |
|---|---:|
| `group` | 0,60–0,70 |
| `craft` | 0,90 |
| `quest` / `instance` | 0,80 |
| `guild` | 0,70 |
| `unknown` / `none` | 0,50 |
| `normal` / `npc` / `cash` | 1,00 |

3. Factor de equipo para armas/armaduras/shadow: slots, ataque/defensa y nivel mínimo.
4. Factor de grupo: `0,60 + 0,10 * (1 - bestGroupShare)`.
5. Multiplicadores de supply abierto, demanda residual y dificultad.
6. Cap `type_p90` para sintéticos con fuente.
7. Cap para items sin fuente: `min(type_p10, 1.000.000) * 0,50`.
8. Costo de receta cuando `produce_db` tiene materiales: `craftCost = suma(materiales * 1,15)`.
9. `mid` clampeado por anclas NPC (`Buy`/`Sell`).

### 2.4 Compra y venta NPC

Cada item tiene dos precios:

- `npcBuyPrice`: lo que el NPC paga al jugador.
- `npcSellPrice`: lo que el NPC cobra al jugador.

`npcBuyPrice` usa la política conservadora:

| Caso | Compra NPC |
|---|---|
| Sintético | 45% del mid, cap 50% de la mediana del tipo |
| Market high | 75% del mid |
| Market medium | 60% del mid, cap 1 mediana |
| Market low | 45% del mid y 75% del low, cap 50% de la mediana |
| Manipulación | 35% del mid y 70% del low, cap 50% de la mediana |
| Manual | 100% del valor |

`npcSellPrice` se calcula con un margen y se limita para evitar spreads absurdos:

```
candidate = mid * (1 + margen)
npcSellPrice = max(npcBuyPrice * 1.10, min(candidate, npcBuyPrice * 1.50))
```

Margen: market high 10%, medium 20%, low 30%, sintético 35%, manipulación 50%, manual 0%.

### 2.5 Demanda, oferta y stock

Además de precio, cada item guarda:

- `demand.percentile` y `demand.tier`;
- `supply.percentile` y `supply.abundanceTier`;
- `demand.marketPressure = demandPercentile - supplyPercentile`;
- `demand.stockHint` (`low`, `normal`, `high`, `unknown`);
- `demand.restockWeight` (0,1–0,9).

La demanda combina LATAM y Atlantis: se calcula el residual por fuente y se pondera por `log1p(total_sold)`. Si solo hay una fuente, usa esa.

Eso permite que un NPC futuro decida stock o frecuencia sin recalcular todo.

### 2.6 Objetos compuestos

`composed.jsonl` usa `data/market/components.yml` y `tools/market/valuation.py`:

```
valor = base * refineFactor + cartas * liquidityDiscount + enchantValue
```

- `refineFactors`: +0 a +10.
- `liquidityDiscount`: 0,85.
- Cap: base * 5 + cartas * 1,5.
- No se enumeran combinaciones; se valoran con la función.
- `enchantValue` queda como placeholder hasta mapear encantamientos.

### 2.7 Tags

Los tags salen de categorías de taxonomía + restricciones de `access`. Un item puede tener varios: `group`, `craft`, `instance_only`, `guild_only`, `boss_only`, `high_hp`, `npc_shop`, `unobtainable`, `untradeable`, etc.

---

## 3. Cobertura global

| Métrica | Valor |
|---|---:|
| Items totales | 29.061 |
| `market` | 5.847 |
| `synthetic` | 23.209 |
| `manual` | 5 |
| `not_applicable` | 0 |
| `marketEligible` | 9.622 |
| `marketEligibleMarket` | 5.652 |
| `marketEligibleSynthetic` | 3.970 |
| Con supply abierto | 1.620 |
| Market-eligible con supply abierto | 1.615 |
| Market-eligible sin supply abierto | 8.007 |
| Clampeados por ancla NPC | 1.265 |
| Manipulación sospechada | 166 |

La mayor parte del catálogo tiene precio sintético. El modelo de abundancia solo cubre 1.615 items market-eligible; para 8.007 el precio se apoya en el tipo y la calidad de fuente.

---

## 4. Muestra general

150 items market-eligible:

| Estado | n |
|---|---:|
| `market` | 101 |
| `synthetic` | 49 |

| Mejor acceso | n |
|---|---:|
| `group` | 57 |
| `normal` | 33 |
| `craft` | 23 |
| `npc` | 14 |
| `unknown` | 10 |
| `none` | 6 |
| `instance` | 4 |
| `quest` | 3 |

- 123 de 150 no tienen supply abierto.
- 37 de los 49 sintéticos son `group`.
- Solo 2 sintéticos tienen supply abierto.
- Demanda: 66 sin fuente, 64 con una fuente y 20 con LATAM + Atlantis.
- Factor de grupo: bestShare mediano 0,02; el factor queda cerca de 0,70.
- Craft: solo 1 item de la muestra general tiene receta en `produce_db`; en edge hay 12.

Precios medianos:

| Estado | mid | compra NPC | venta NPC |
|---|---:|---:|---:|
| `market` | 889.000z | 176.000z | 264.000z |
| `synthetic` | 700.000z | 315.000z | 472.000z |

Después de usar `type_p40` y el factor de fuente, el sintético quedó **por debajo** del mercado en la mediana. El spread compra/venta quedó en un rango razonable (1,5x–2,0x), no en 9x como antes.

---

## 5. Casos borde

119 items, más 48 ejemplos compuestos. Categorías principales:

| Caso | n | Lectura |
|---|---:|---|
| `craft_best` | 8 | Falta costo de receta; el factor 0,90 es provisorio. |
| `guild_only` | 8 | Sin supply abierto; precio histórico y caps. |
| `instance_only` | 7 | Igual que guild. |
| `boss_only` | 5 | Muchos tienen además NPC shop o quest; el tag no es exclusión. |
| `high_hp` | 7 | HP extremo o sin spawn; el modelo los marca. |
| `group_only` | 7 | El mayor riesgo de sobrevaloración. |
| `no_price_with_open_supply` | 8 | Donde el sintético tiene mejor sustento. |
| `manipulation_suspected` | 4+ | Red Potion/Herb y similares; detector general. |
| `custom` / `manual_price` | 5 | Monedas OzRo y Alma de MVP. |
| `untradeable` | 7 | Deben tener precio, pero no se compran/venden entre jugadores. |
| `unobtainable` / `no_source` | 7 | Precio sintético con cap de fuente. |
| `max_open_supply` | 5 | Hierbas, Fly Wing, Zargon, Sticky Mucus. |
| `min_open_supply` | 8 | Cartas con supply casi cero. |
| `price_top_1pct` | 8 | Pet eggs y equipo caro. |
| `price_bottom_1pct` | 8 | Pociones, manzanas, flechas. |

### Señales concretas

- **Group-only:** sigue siendo el caso más débil. El factor 0,70 y `type_p40` lo contienen, pero no reemplazan una probabilidad real de grupo.
- **Instancia/guild:** no tienen supply abierto; el precio histórico manda, pero el NPC necesita caps.
- **Boss-only:** el tag es una advertencia, no un bloqueo.
- **No-source:** el cap `min(type_p10, 1M) * 0,5` evita los 50M de pet eggs sin fuente.
- **Custom:** las monedas quedaron con precio manual; no dependen del modelo.
- **Manipulación:** Red Potion, hierbas y Apple se marcan; el `npcBuyPrice` los contiene.
- **NPC anchors:** 1.265 items fueron clampeados; el precio externo y el precio NPC no siempre coinciden.
- **Compuestos:** en bases baratas la carta domina el valor; en bases caras el refine casi no mueve el precio. Las tablas son placeholders y necesitan validación.
- **Craft:** el costo de receta solo aplica a `produce_db`; Laphine y tasas de éxito siguen fuera.
- **Sintético de grupo:** el cap `type_p90` y el factor 0,60–0,70 evitan los valores extremos, pero el prior sigue siendo grueso.

---

## 6. Umbral de HP

El umbral de HP no es un precio ni una exclusión. Es un **tag de dificultad de fuente**.

Cómo funciona:

1. Se toma el HP de `mob_db`.
2. Se aplica el rate del servidor: `monster_hp_rate` o `mvp_hp_rate` (hoy 2x).
3. Para cada item, se miran los mobs que lo dropean y que tienen spawn conocido.
4. Se usa el **mínimo HP** de esas fuentes: la más fácil.
5. Si el mínimo HP efectivo es mayor o igual al umbral, `highHp=true`.
6. Si el máximo supera el umbral pero el mínimo no, `highHpSource=true`.

Umbral actual: **10.000.000 de HP efectivo** (5.000.000 raw con 2x). Es configurable con `--high-hp-threshold`.

Para qué se usa:

- `commonFarmEligible`: mapa normal, no boss-only y no `high_hp`.
- Cola de revisión: fuentes extremas o posiblemente no farmeables.
- Futuro stock/eligibilidad de NPC: un item `high_hp` no debería entrar como farmeo común.
- No cambia el precio directamente; el precio usa `difficulty` y `supply`.

Por qué mínimo y no máximo: si un item cae de un mob de 500k HP y de un boss de 100M, el jugador puede farmear el mob barato. Lo que importa es la fuente más accesible.

Por qué HP y no nivel: el nivel es engañoso; un mob de nivel alto con poco HP puede ser más fácil que uno de nivel medio con HP y defensa altos.

Estado actual: 156 items `high_hp` y 105 `high_hp_source`.

---

## 7. Decisiones tomadas para esta iteración

1. **Todos los items tienen precio.** `not_applicable` desaparece.
2. **Precios manuales** para monedas OzRo y Alma de MVP.
3. **Sintético con `type_p40`**, no mediana.
4. **Factor de fuente** para group/craft/quest/instancia/sin fuente.
5. **Factor de equipo** por slots, ataque/defensa y nivel mínimo.
6. **Cap de items sin fuente** para evitar precios absurdos.
7. **Compra y venta NPC separadas**, con spread controlado.
8. **Presión de mercado, stockHint y restockWeight** para stock/frecuencia futura.
9. **Tags múltiples**, sin reglas especiales por item.
10. **Muestra general market-eligible**; los casos raros y no elegibles van a la muestra borde.
11. **Demanda combinada LATAM + Atlantis**.
12. **Factor de grupo y costo de craft** donde hay datos.
13. **Objetos compuestos** con tablas y contrato de valoración.

---

## 8. Riesgos y pendientes

- **Group/package:** 8.007 market-eligible sin supply abierto. El sintético por tipo es el fallback, pero no distingue bien dentro del grupo.
- **Craft:** `produce_db` cubre pocos casos; Laphine y tasas de éxito siguen pendientes.
- **Item mall:** no hay conversión a zeny; el techo queda en NPC/manual.
- **Pet eggs y equipo caro:** el `mid` puede ser alto; el `npcBuyPrice` lo contiene, pero conviene revisar.
- **Custom:** los precios manuales son canon; si cambia la economía, se actualizan en `canon.yml`.
- **Umbral de HP:** 10M efectivo; confirmar si queda como canon.
- **Demanda:** residual por tipo/abundancia; faltan pesos LATAM/Atlantis.
- **Compuestos:** las tablas son placeholder; faltan encantamientos reales y validación contra mercado.

---

## 9. Próximos pasos

1. Revisar la muestra completa y ajustar `canon.yml`.
2. Decidir si group/package/craft se modelan mejor o se acepta el prior actual.
3. Definir la regla de pet eggs/equipo sin fuente.
4. Confirmar el umbral de HP.
5. Construir `build_master.py` con esta misma lógica y generar los artefactos JSON/SQL/NPC.
