# Precio de mercado maestro

**Estado:** `pendiente` (análisis y plan, sin implementación)  
**Fecha:** 2026-11-18  
**Contexto:** `ragnabots` quedó deprecado como bot, pero sus datos de mercado siguen siendo la única referencia histórica disponible. Se necesita una clasificación maestra de items con precio, abundancia, dificultad y demanda para reemplazar las tablas ad hoc de Garrett y alimentar al vendedor viajero, al tasador, la web, eventos y recompensas.

**Relacionado:** [13-mercado-npc-tasador.md](./13-mercado-npc-tasador.md), [15-vendedor-viajero.md](./15-vendedor-viajero.md), [04-npcs.md](./04-npcs.md)

---

## 1. Resumen ejecutivo

La base ya existe y es mejor de lo que parece: `ragnabots/staging/market/pricing/master_list.json` cruza 5.858 items con precio histórico, ventas, rareza y datos de drop del servidor. Lo que falta no es recolectar de nuevo, sino **limpiar, completar y congelar** esa información en una capa estable.

La propuesta es construir un **master de mercado** con cuatro señales separadas:

1. **Abundancia:** cuánto entra al mundo por unidad de tiempo (spawn × drop × rates × acceso).
2. **Dificultad:** cuánto cuesta farmearlo (HP, defensa, nivel, tipo de mapa, boss/instancia).
3. **Demanda:** cuánto se mueve, corregida por la abundancia para no confundir “se vende mucho” con “hay mucho”.
4. **Precio histórico:** mediana LATAM y promedio Atlantis, tratados con robustez y calibrados contra anclas NPC de OzRo.

El master integra la taxonomía y se convierte en la **fuente de verdad**. `taxonomy.json` queda como insumo/vista generada para compatibilidad, no como una lista separada que haya que mantener a mano.

**Veredicto de viabilidad:**

| Pieza | Viabilidad | Comentario |
|---|---|---|
| Clasificación base (identidad, fuentes, acceso, utilidad) | **Alta** | Los datos ya están; falta consolidarlos y corregir accesos. |
| Abundancia y dificultad | **Alta-media** | Hay spawn y HP para casi todo; el acceso a mapas requiere overrides. |
| Demanda | **Media** | `total_sold` no tiene ventana temporal y está confundido con oferta. |
| Precio histórico limpio | **Media-alta** | 5.847 items con precio; solo 1.421 con desviación real. |
| Precio absoluto para los 9k items | **Media-baja** | Muchos sin mercado; requieren modelo intrínseco y revisión manual. |
| Objetos compuestos (refine/cartas/encantamientos) | **Media-baja** | Cartas y slots son factibles; refine y encantamientos necesitan tablas manuales. |
| Tasador con consignación | **Baja-media** | El precio es solo una parte; persistencia y anti-dupe son otro sistema. |

**Recomendación:** empezar por el master de items base, sin objetos compuestos. Reemplazar Garrett recién cuando el master pase validación. Dejar tasador y consignación para después.

---

## 2. Qué existe hoy

### 2.1 Fuentes utilizadas

| Fuente | Archivo | Qué aporta | Límite |
|---|---|---|---|
| Precio maestro | `ragnabots/staging/market/pricing/master_list.json` | Precio, stats, rareza, drop, usos, anclas NPC | Generado una vez; mezcla criterios |
| LATAM | `ragnabots/staging/market/latam_tools/curated/ranked_market.json` | `offers_median`, `offers_min`, `market_avg`, `total_sold` | Sin desviación; economía bRO |
| Atlantis | `ragnabots/staging/market/atlantis_playro/curated/ranked_atlantis.json` | `avg`, `min`, `max`, `std_dev`, `total_sold` | Servidor privado viejo; promedios con outliers |
| Dropeables | `ragnabots/staging/market/atlantis_playro/curated/droppable.json` | item → mobs, tipo de drop | Solo cobertura Atlantis |
| Grindable | `ragnabots/staging/market/atlantis_playro/curated/grindable.json` | drop + spawn normal, mapas, cantidades | 926 items |
| Spawns | `ragnabots/staging/market/spawns/spawns_normal.json` | 3.173 líneas normales, 1.132 mobs, 357 mapas | Boss excluidos; 90,7% con `delay1` |
| NPC shops | `ragnabots/staging/market/npc_shops/npc_buyable_compact.json` | 923 items con precio y mapas | Precio típico, no siempre único |
| Rates | `conf/import/battle_conf.txt` | common 5x, heal/use 10x, equip 15x, card normal 10x/boss 100x, mvp 5x; HP 2x | Fuente actual; el snapshot `ragnabots/data/raw/server_rates.json` está desactualizado |
| Taxonomía | `ozro-site/assets/items/taxonomy.json` | 29.061 items, fuentes, flags, usos, precio de mercado | Clasificación conservadora; `unobtainable` tiene falsos positivos |
| DB del servidor | `db/re/item_db*.yml`, `db/re/mob_db.yml` | Identidad, slots, refine, HP, defensa, level | `Class` solo en 830 de 2.675 mobs |

### 2.2 Cobertura actual

| Métrica | Valor | Lectura |
|---|---:|---|
| Items en taxonomía | 29.061 | Catálogo completo |
| Tradeables + obtenibles | **8.871** | Universo razonable para el master |
| Con precio histórico | 4.907 | 55% del universo tradeable/obtenible |
| Sin precio histórico | 3.964 | Necesitan modelo intrínseco o precio manual |
| Registros en `master_list` | 5.858 | 4.907 caen en tradeable/obtenible |
| `master_list` con precio | 5.847 | 11 sin precio (5 monedas OzRo + 6 casos) |
| Con stats Atlantis | 1.421 | Únicos con `std_dev` real |
| Con `supply_tier` | 1.519 | 4.339 sin datos de drop |
| Grindables | 1.519 | Drop + spawn normal |
| Solo MVP drop | 12 | No farmeables en mapa normal |
| NPC-buyable | 923 | Ancla de precio y techo |
| Rareza `unknown` | 422 | Sin mercado ni drop suficiente |

### 2.3 Hallazgos del análisis

**a. El precio histórico tiene outliers severos.** No alcanza con promediar. Hay 163 items con coeficiente de variación (`std_dev / avg`) mayor a 3. Ejemplos:

| Item | `avg` Atlantis | `std_dev` | CV | Ventas |
|---|---:|---:|---:|---:|
| Strawberry | 1.369 | 662.385 | 483,8 | 1.515.598 |
| Red Potion | 50 | 18.511 | 370,2 | 229.735 |
| Arrow | 18 | 2.178 | 121,0 | 99.993 |
| Jellopy | 445 | 11.678 | 26,2 | 2.406.372 |

El promedio de Atlantis no sirve como precio puntual en esos casos. Hay que usar mediana, bandas recortadas, CV y flags de outlier.

**b. La distribución de precios está dominada por equipo y cartas.** En los 5.847 items con precio: mediana 1.399.999z, p90 40M, p99 424,9M. Eso no es “el precio típico de un material”. Cualquier modelo global sin categoría va a estar sesgado.

| Tipo | n | Mediana |
|---|---:|---:|
| Armor | 1.592 | 4.488.888 |
| Shadowgear | 389 | 4.000.000 |
| ShadowGear | 241 | 2.890.000 |
| Card | 842 | 1.500.000 |
| Weapon | 940 | 1.000.000 |
| Etc | 981 | 100.000 |
| Healing | 133 | 4.000 |

**c. La abundancia correlaciona negativo con el precio, pero la demanda cruda no.** Spearman sobre items con ambos datos:

| Relación | ρ | n |
|---|---:|---:|
| `supply_score` vs precio | **-0,537** | 1.518 |
| `best_effective_rate_pct` vs precio | -0,478 | 2.131 |
| `total_sold` vs precio | -0,244 | 5.163 |
| Dentro de `Etc`: supply vs precio | -0,408 | 319 |
| Dentro de `Etc`: sold vs precio | -0,553 | 865 |
| Dentro de `Card`: sold vs precio | +0,159 | 826 |

La señal de abundancia funciona. La señal de ventas crudas está contaminada: los materiales comunes venden mucho porque abundan, no porque tengan más demanda. Hay que usar **demanda residual** (ventas esperadas dado el tipo y la abundancia) y no `total_sold` directo.

**d. Los generadores específicos de Garrett se eliminaron.** `tools/generate_garrett_missions.py`, `tools/generate_garrett_npc.py` y `garrett-missions.json` ya no existen. La clasificación de acceso dejó de ser una lista de IDs de Garrett: `taxonomy.json` ahora expone un objeto `access` por item, calculado con reglas (mapa normal, guild, instancia, quest, boss, HP). `trasher.txt` conserva sus arrays legacy hasta que el master lo reemplace, pero ya no tiene generador propio.

**e. Hay 803 items marcados `unobtainable` que sí tienen precio de mercado.** La taxonomía es conservadora. No se pueden excluir sin revisar; conviene guardar `unobtainable` como flag y no como sentencia.

**f. Los rates de OzRo cambian la abundancia.** Card normal 10x / boss 100x, equip 15x, heal/use 10x, common 5x; HP 2x. Cualquier cálculo de oferta que use `base_rate` sin aplicar el multiplicador va a subestimar mucho ciertos items.

**g. Hay outliers que no son ruido: son manipulación de mercado.** El caso Strawberry no es un error de datos. En LATAM se usaban items baratos para mover dinero entre cuentas y para reservar “plazas” de merchant: se ponía un solo objeto a precio absurdo; al venderse todo el personaje se deslogueaba y la plaza quedaba libre, así que algunos tomaban buenas ubicaciones y las “vendían” con una publicación alta. Eso produce `avg` y `max` enormes con `median` bajo. Casos observados: Strawberry, Red Potion, Arrow, Jellopy y otros consumibles/materiales de volumen.

Reglas de detección y tratamiento:

- `max / avg` muy alto, `cv` muy alto y `total_sold` alto ⇒ sospecha de manipulación, no de item caro.
- Si `median` es baja pero `avg`/`max` son absurdos, usar la mediana y descartar el promedio para precio.
- Si `offers_min` es 0 o casi 0 y hay un `max` enorme, marcar `manipulation_suspected`.
- No usar `max` ni `avg` para fijar precios de NPC en esos items.
- Documentar **ejemplos conocidos** para validar el detector; no crear excepciones por ID. Si un caso escapa a las reglas generales, se analiza en el futuro.
- Si en el futuro se accede a listings individuales, detectar publicaciones de 1 unidad a precio > N× la mediana y excluirlas antes de calcular estadísticas.

**h. El snapshot de rates de ragnabots está desactualizado.** `ragnabots/data/raw/server_rates.json` dice card 100x y no incluye HP. La configuración actual (`conf/import/battle_conf.txt`) tiene card normal 10x, card boss/MVP 100x y HP 2x (`monster_hp_rate`/`mvp_hp_rate` 200). El master debe leer la configuración actual, no el snapshot.

---

## 3. Problema a resolver

Se necesita una **única fuente de verdad** que responda, por item:

- ¿Existe y es comerciable?
- ¿De dónde sale y qué tan accesible es?
- ¿Qué tan abundante es en OzRo con los rates actuales?
- ¿Qué tan difícil es farmearlo?
- ¿Tiene demanda real o solo se mueve porque sobra?
- ¿Cuánto vale en zeny, con qué rango y con qué confianza?
- ¿Para qué sirve: vending NPC, tasador, viajero, quest, evento, drop custom?
- ¿Qué items necesitan precio manual o revisión?

Y que sea consumible por:

- scripts NPC (rAthena, sin leer JSON en runtime);
- web (`ozro-site`);
- herramientas de eventos y recompensas;
- análisis futuros.

---

## 4. Principios de diseño

1. **Separar señales.** Abundancia, dificultad, demanda y precio histórico son campos distintos. No colapsarlos en un solo “score” opaco.
2. **El precio histórico es una señal, no una verdad.** LATAM y Atlantis no son OzRo. Se calibran y se limitan con anclas del servidor.
3. **Nunca un promedio simple.** Mediana, bandas, CV, recorte y flags.
4. **La ausencia de datos es un dato.** `unknown` es válido; no inventar precio para todo.
5. **Lo manual es explícito y auditable.** Overrides en YAML con razón, fecha y fuente. No editar archivos generados.
6. **Determinismo.** Misma entrada + mismas reglas = mismo output, salvo `generatedAt`.
7. **Compatibilidad.** IDs de item, no nombres. La taxonomía sigue siendo el catálogo técnico.
8. **El master no es inmutable.** “No tocarlo más” es deseable, pero la economía cambia. Se versiona y se regenera; lo que no se toca a mano son los generados.

---

## 5. Universo y granularidad

### 5.1 Universo propuesto

El master debe ser un **catálogo de decisiones**, no solo una lista de items comprables. Incluir los 29.061 items de la taxonomía, con campos que digan si tienen precio, si son comerciables y para qué sirven.

Cada fila debe llevar, como mínimo:

- `tradeable`, `obtainable`, `marketEligible`, `priceable`;
- `tags` (lista de meta-categorías, puede haber varias);
- `sources` y `access`;
- `priceStatus` (`market`, `synthetic`, `manual`, `unknown`).

El **universo de mercado activo** es una vista filtrada, no el master completo:

- items tradeables y obtenibles (8.871);
- items con precio histórico aunque estén marcados `unobtainable` (803 casos a revisar);
- items vendidos por NPC shop (950);
- items custom de OzRo (35001–35005 y futuros);
- items referenciados por quests, craft o eventos.

Los items `untradeable` o sin fuente no se eliminan: se guardan con `marketEligible=false` pero con `priceStatus=synthetic` (o `manual`/`unknown`). Todos tienen un precio canónico; la elegibilidad solo indica si hoy tiene sentido comercializarlo.

No incluir como filas:

- combinaciones de refine/cartas/encantamientos (se valoran con una función aparte);
- instancias concretas de un item con cartas/refine (no son un item ID).

Cada fila puede ser `market_eligible=true` y `priceable=false` si falta información.

### 5.2 Granularidad

Una fila por `item_id`. Los objetos compuestos no generan filas nuevas; se calculan con:

```
valor(instancia) = f(item_base, refine, cartas, slots, encantamientos, opciones)
```

Eso evita una explosión combinatoria y mantiene el master estable.

---

## 6. Modelo de clasificación

### 6.1 Identidad

Campos mínimos:

```json
{
  "id": 7003,
  "name": "Anolian Skin",
  "aegis": "Anolian_Skin",
  "type": "Etc",
  "subtype": null,
  "slots": 0,
  "refineable": false,
  "weight": 10,
  "trade": "free",
  "custom": false
}
```

`trade` propuesto: `free`, `restricted`, `untradeable`, `quest_bound`.

### 6.2 Fuentes y acceso

Cada item tiene un conjunto de fuentes:

- `mob_drop` (normal, MVP, boss)
- `map_drop` (global/específico)
- `npc_shop`
- `cash_shop`
- `quest_reward`
- `instance_reward`
- `script_reward`
- `craft`
- `group`
- `package`
- `event`

Además, una **clase de acceso** que resume la mejor fuente:

| `access_class` | Significado | `access_factor` propuesto |
|---|---|---:|
| `open` | Mapa normal, spawn abierto | 1,00 |
| `dungeon` | Dungeon normal con acceso estándar | 0,80 |
| `restricted` | Mapa de quest, evento o acceso condicionado | 0,40 |
| `instance` | Solo instancia | 0,15 |
| `guild` | Solo castillo/guild dungeon | 0,10 |
| `quest` | Solo recompensa de quest única | 0,15 |
| `event` | Solo evento temporal | 0,00 (fuera de temporada) |
| `npc` | Solo compra NPC | 1,00 (pero con techo de precio) |
| `none` | Sin fuente conocida | 0,00 |

Reglas:

- Si hay varias fuentes, se usa la mejor clase para `access_class`, pero se guardan todas.
- `instance`, `guild`, `quest` y `event` no deben entrar automáticamente al tasador ni al vendedor viajero.
- `boss_only` es un flag aparte, no una clase de acceso.
- Los overrides manuales pueden cambiar `access_class` y `access_factor` con razón.

#### Implementación en la taxonomía

`taxonomy.json` ya calcula un objeto `access` por item con estas reglas, sin listas de IDs:

```json
{
  "best": "normal",
  "normalMaps": 2,
  "guildMaps": 0,
  "instanceMaps": 0,
  "dropMobs": 6,
  "spawnMobs": 4,
  "bossOnly": false,
  "minMobHp": 3878,
  "maxMobHp": 166150,
  "minMobLevel": 57,
  "maxMobLevel": 109,
  "highHp": false,
  "highHpSource": false,
  "noSpawn": false,
  "restrictions": [],
  "commonFarmEligible": true
}
```

Reglas:

- `best` usa la mejor fuente conocida, no una categoría fija.
- `highHp` se calcula con la **fuente más fácil** (mínimo HP efectivo de los mobs con spawn). Si hay un mob barato y uno caro, el item no es `high_hp`.
- `highHpSource` marca que alguna fuente supera el umbral, aunque haya una más fácil.
- El umbral por defecto es `10.000.000` de HP **efectivo** y se puede cambiar con `--high-hp-threshold`; no está hardcodeado por item.
- El HP efectivo aplica `monster_hp_rate` y `mvp_hp_rate` de `conf/import/battle_conf.txt` (hoy 200%, es decir, 2x).
- `commonFarmEligible` es la regla tipo Garrett: mapa normal, no boss-only y no `high_hp`. Es un dato calculado, no una lista.
- `restrictions` es una lista de tags (`instance_only`, `guild_only`, `quest_source`, `boss_only`, `high_hp`, etc.). Un item puede tener varios.
- Estos campos son información extra; no reemplazan las categorías existentes ni obligan a un consumidor a usarlos.

### 6.3 Utilidad

Reutilizar la taxonomía, pero con una clasificación más legible:

| `utility_class` | Ejemplos | Uso de precio |
|---|---|---|
| `material` | Anolian Skin, Rough Oridecon | Tasador, viajero, quests |
| `consumable` | Pociones, comidas, pergaminos | Viajero, eventos |
| `equipment` | Armas, armaduras, shadow gear | Tasador, web |
| `card` | Cartas | Tasador, web |
| `ammo` | Flechas, balas | Viajero |
| `craft_input` | Material de crafting | Quests, tasador |
| `quest_item` | Item de turn-in | No tasador |
| `collectible` | Coleccionables, monedas | Eventos, web |
| `junk` | Chatarra | Garrett / compra de basura |
| `event` | Item de evento | Fuera de temporada |
| `unknown` | Sin clasificar | Revisión manual |

Campos de uso de contenido:

```json
{
  "content_uses": ["quest", "craft", "npc_shop"],
  "used_by_content": true,
  "is_junk": false,
  "is_combo_piece": false,
  "is_skill_cost": false,
  "quest_only": false,
  "instance_only": false
}
```

### 6.4 Abundancia

Objetivo: estimar cuánto entra al mundo por unidad de tiempo, no cuánto drop hay “en teoría”.

Para cada fuente de mob:

```
eff_rate = min(10000, base_rate * rate_mult[type]) / 10000
flow     = spawn_amount * eff_rate * access_factor / max(delay_seconds, 1)
supply   = Σ flow
```

Donde:

- `base_rate` está en diezmilésimos (10000 = 100%).
- `rate_mult` sale de `conf/import/battle_conf.txt` según el tipo de item: common 5x, heal/use 10x, equip 15x, card normal 10x/boss 100x, mvp 5x. No usar `ragnabots/data/raw/server_rates.json`, que está desactualizado.
- `delay_seconds` es `delay1 / 1000` del spawn; si falta, usar la mediana (10s) y bajar la confianza.
- `access_factor` sale de la tabla anterior.

Luego:

- `supply_percentile`: percentil de `supply` dentro del universo (o dentro del tipo; guardar ambos).
- `abundance_tier`: `abundant` ≥ p75, `common` ≥ p50, `uncommon` ≥ p25, `scarce` ≥ p10, `rare` < p10.
- `source_diversity`: cantidad de mobs y mapas distintos.
- `supply_confidence`: según cobertura de drop rate, spawn, delay y cantidad de fuentes.

**Importante:** `supply` no se divide por dificultad. Son señales separadas. Un item puede ser abundante pero difícil (mucho HP) o escaso pero fácil (poco spawn).

### 6.5 Dificultad

Objetivo: estimar el costo relativo de farmear, sin depender solo del nivel.

Propuesta de `threat` por mob:

```
threat = log1p(hp_effective)
       * (1 + def / 100 + mdef / 200)
       * (1 + 0.5 * boss)
       * (1 + 0.2 * max(0, level - 100) / 50)
```

- `hp_effective` es el HP de `mob_db` multiplicado por `monster_hp_rate`/`mvp_hp_rate` (hoy 2x). Es la señal principal; el nivel solo ajusta en el extremo alto.
- `boss` incluye MVP y mobs de clase Boss.
- `def`/`mdef` faltan en ~337/397 mobs; si faltan, usar 0 y bajar confianza.
- `Class` solo está en 830 de 2.675 mobs; no usarlo como única señal.

Luego:

- `difficulty_index`: percentil de `threat` entre los mobs que dropean el item, ponderado por `flow`.
- `difficulty_tier`: `easy` < p50, `medium` < p75, `hard` < p90, `extreme` ≥ p90.
- `unfarmable`: no hay spawn normal, solo instancia/guild/quest/event, o el mob no tiene spawn alcanzable.
- `access_class` se guarda aparte; no se mezcla con `difficulty_tier`.

Casos que el modelo puede marcar para revisión (sin listas manuales):

- mobs con HP/defensa extrema aunque el nivel parezca bajo;
- mobs de evento o mapas bloqueados;
- mobs con spawn solo por script/NPC;
- plantas y mobs especiales que no cuentan como farmeo real.

### 6.6 Demanda

`total_sold` no es demanda pura: es ventas acumuladas durante la vida de otro servidor. Los materiales comunes venden mucho porque abundan. Para separar demanda de oferta:

1. Calcular `demand_raw` = percentil de `log1p(total_sold)` **dentro del tipo** (Etc, Card, Weapon, etc.).
2. Calcular `expected_sold` = mediana de `total_sold` dentro de `(tipo, decil de supply)`.
3. `demand_residual = log1p(total_sold) - log1p(expected_sold)`.
4. `demand_percentile` = percentil del residual.
5. Repetir para LATAM y Atlantis; combinar con peso por cantidad de ventas y confianza de fuente.
6. Si falta `supply`, usar `demand_raw` con confianza baja.
7. Si falta `total_sold` en ambas fuentes, `demand_tier = unknown`.

Tiers propuestos:

| `demand_tier` | Percentil residual |
|---|---:|
| `high` | ≥ 75 |
| `medium` | 40–75 |
| `low` | 10–40 |
| `none` | < 10 |
| `unknown` | sin datos |

Además guardar:

- `liquidity_tier` (`liquid`, `normal`, `thin`, `illiquid`) del master actual;
- `sales_latam`, `sales_atlantis` crudos;
- `demand_confidence`.

La utilidad también es un prior de demanda: consumibles de uso real, cartas meta y materiales de crafting no se comportan como items decorativos. Eso puede ir en overrides o en un multiplicador por `utility_class`.

### 6.7 Precio histórico

#### Regla de selección

```
1. LATAM offers_median        (vending activo)
2. LATAM market_avg           (histórico, sin tiendas abiertas)
3. Atlantis avg robusto       (con penalización por CV)
4. NPC shop typical           (solo items sin mercado)
5. null                       (precio manual)
```

No mezclar economías en la banda principal.

#### Limpieza LATAM

- Si `offers_min` es 0 o menor al 10% de `offers_median`, marcar `latam_min_suspicious`.
- Si `market_avg / offers_median` está fuera de 0,3–3, marcar `latam_history_gap`.
- Preferir `offers_median` sobre `market_avg` cuando hay vending activo.
- Si no hay `offers`, usar `market_avg` con confianza menor.

#### Limpieza Atlantis

- `cv = std_dev / avg`.
- `max_ratio = max / avg`.
- Si `cv > 1,5`, bajar confianza; si `cv > 3`, no usar Atlantis como única referencia.
- Banda propuesta: `[max(min, avg - std_dev), min(max, avg + std_dev)]`, luego recortar a `[avg/5, avg*5]`.
- Si la banda queda inválida (`low > high`), usar `[min, max]` recortado.
- Si `total_sold < 10`, marcar `low_observations`.
- No usar `avg` de Atlantis para items con CV extremo sin revisión.

#### Manipulación y artefactos

Además de los outliers estadísticos, hay artefactos de mercado:

- publicaciones de 1 unidad a precio absurdo para reservar plaza de merchant;
- items baratos usados para transferir dinero entre cuentas;
- `max` alto con `median` baja y `total_sold` alto.

Para esos casos:

- no usar `avg` ni `max` como referencia;
- usar `offers_median` o el percentil bajo;
- marcar `manipulation_suspected` y `needs_review`;
- documentar el caso conocido con una nota, no con una categoría de item.

Ejemplos para validar el detector: Strawberry, Red Potion, Arrow, Jellopy y cualquier consumible/material de volumen con `cv > 3` y `total_sold` alto. No son listas de excepciones.

#### Cruce LATAM ↔ Atlantis

```
ratio = latam_effective / atlantis_avg
good      = 0,5–2,0
weak      = 0,3–3,0
divergent = fuera de 0,3–3,0
```

- `good`: usar media geométrica ponderada.
- `weak`: preferir LATAM y bajar confianza.
- `divergent`: no promediar; elegir LATAM activo si existe, si no marcar `needs_review`.

#### Calibración a OzRo

Los precios externos no son zeny de OzRo. Propuesta:

1. Elegir una canasta de items con `npc_shop_typical` y precio histórico de confianza alta/media.
2. Calcular `scale = median(npc_shop_typical / historical_ref)` por categoría (o global si no hay suficientes).
3. Recortar `scale` a `[0,25, 4,0]`.
4. `historical_ozro = historical_ref * scale_categoria`.
5. Guardar siempre `historical_ref` crudo y `economy_scale` aplicado.

Esto no convierte el precio externo en verdad; lo pone en una escala usable y auditable.

#### Anclas del servidor

Nombrar sin ambigüedad:

- `npc_sell_to_player` = campo `Buy` de `item_db` (lo que cobra el NPC).
- `npc_buy_from_player` = campo `Sell` de `item_db` (lo que paga el NPC).

Reglas:

- Si el NPC vende el item: `price_ceiling = npc_sell_to_player * 0,95`.
- Si el NPC compra el item: `price_floor = npc_buy_from_player * 1,05`.
- Si el item está en item mall: el precio del mercado no debe superar el precio equivalente en zeny del mall; si no hay conversión, usar override manual.
- Si el item es craftable: `price_floor = costo de materiales * 0,8` cuando exista receta; si no, no inventar.

### 6.8 Precio modelo

El modelo debe ser explicable. Propuesta inicial, antes de intentar regresiones:

```
base = historical_ozro
       si confidence >= medium
       si no: mediana del tipo * factor_intrinseco

mult_supply     = clamp((median_supply / supply)^0,25, 0,5, 2,0)
mult_demand     = clamp(1 + 0,25 * demand_z, 0,7, 1,5)
mult_difficulty = clamp(1 + 0,15 * difficulty_z, 0,8, 1,5)

raw = base * mult_supply * mult_demand * mult_difficulty
mid = clamp(raw, price_floor, price_ceiling)
```

Donde `demand_z = (demand_percentile - 50) / 50` y `difficulty_z = (difficulty_percentile - 50) / 50`.

Luego:

- `low`/`high` según confianza: high ±15%, medium ±30%, low ±50%.
- `buy_ceiling` (lo que un NPC debería pagar al instante) = `min(mid * 0,75, price_ceiling * 0,95)`.
- `sell_floor` (mínimo aceptable para el jugador) = `max(mid * 0,50, price_floor)`.
- Redondear a números “bonitos” solo en el campo `rounded`; conservar `raw`.
- Si `mid` queda fuera de `[low, high]`, corregir.

Si el modelo heurístico no alcanza, se puede probar una regresión robusta sobre `log(precio)` con `log(supply)`, `demand_residual`, `difficulty`, `utility_class` y dummies de tipo. Pero solo si mejora el backtest; no reemplaza la explicabilidad.

### 6.9 Confianza y overrides

`price_confidence`:

| Nivel | Criterio |
|---|---|
| `high` | 2 fuentes de acuerdo, CV bajo, ventas suficientes, ancla NPC consistente |
| `medium` | 1 fuente sólida o 2 débiles; CV moderado |
| `low` | 1 fuente, CV alto, pocas ventas o sin drop |
| `manual` | Override aprobado |
| `unknown` | Sin datos suficientes |

`needs_manual` se activa si:

- no hay precio histórico y el modelo intrínseco da un valor alto (> 1M);
- hay `divergent` entre fuentes;
- CV > 3;
- item custom;
- item de evento/instancia con posible uso en tasador;
- item `unobtainable` con precio de mercado.

Overrides en `data/market/overrides.yml`:

```yaml
schemaVersion: 1
items:
  35001:
    price:
      mid: 5000000
      low: 4000000
      high: 6000000
      confidence: manual
    reason: "Moneda de Platino OzRo; sin mercado externo"
    source: "diseño"
    date: "2026-11-18"
  7003:
    access:
      class: open
      factor: 1.0
    reason: "Spawn normal confirmado en cmd_fild03 y gl_sew04"
    date: "2026-11-18"
```

Solo el archivo de overrides se edita a mano. Los generados llevan cabecera `DO NOT EDIT`.

---

### 6.10 Precio sintético para los items sin histórico

Sí se puede calcular un **precio de referencia**, pero no un precio de mercado confiable. La correlación abundancia-precio es buena, pero insuficiente para predecir valores absolutos con la precisión que necesita un NPC que paga zeny.

Prueba hecha con los 5.847 items que sí tienen precio, split 80/20 por `item_id` (1.188 items de test), usando la mediana de `log(precio)` por `(tipo, supply_tier, demanda residual)`:

| Modelo | Error absoluto mediano | Dentro de 2x | Dentro de 3x |
|---|---:|---:|---:|
| Mediana global | 7,42x | 19,6% | 30,1% |
| Solo tipo | 6,48x | 22,4% | 33,7% |
| Tipo + supply | 4,50x | 26,3% | 39,0% |
| Tipo + demanda residual | 4,00x | 29,0% | 42,2% |
| Tipo + supply + demanda | **3,39x** | **31,6%** | **45,1%** |

Por segmento:

| Segmento | Modelo | Error mediano | Dentro de 2x |
|---|---|---:|---:|
| Etc/consumibles | tipo + supply + demanda | 3,54x | 31,1% |
| Equipo/cartas | tipo + supply + demanda | 3,33x | 32,4% |

Un error de 3,4x es aceptable para ordenar o mostrar una referencia, y en un servidor de 3–5 jugadores es preferible a no tener precio. La decisión de canon es:

- El precio sintético es **válido como `priceStatus=synthetic`** y puede usarse en NPCs como fallback, no solo como referencia.
- Para NPCs que pagan, usar una política conservadora: `buyCeiling` desde el **low** sintético, con descuento adicional, nunca desde el `high`.
- El `mid` sintético sirve para mostrar, presupuestar y para el tasador en modo estimación; la compra real usa piso conservador.
- Items con `mid` histórico high/medium usan el histórico; el sintético solo ajusta.
- Para equipo/cartas caras, el sintético se mezcla con anclas intrínsecas (NPC, craft, refine, item mall) y se capa por banda.
- Para group/package/quest-only, el sintético usa el prior del tipo y la utilidad; si no hay supply, se aplica un haircut extra y un cap absoluto.
- Nada de revisión manual item por item. Solo se revisan outliers, custom y casos detectados como raros.

En la implementación v1 todos reciben precio. Para los 3.964 sin histórico, el prior usado es:

| Situación | n aproximado | Política |
|---|---:|---|
| Solo `group` | 2.379 | Sintético `type_p40` + factor de fuente + cap; NPC con spread |
| `craft` + `group` | 398 | Sintético con factor craft; costo de materiales pendiente |
| Con `normal_drop` | 406 | Sintético con supply; mejor confianza dentro del bloque |
| Instancia/quest | 144 | Sintético conservador; NPC solo con cap |
| Otros (npc, package, etc.) | resto | Ancla NPC o sintético con cap |

La implementación v1 está detallada en [19-muestra-master.md](./19-muestra-master.md): `type_p40`, factor de fuente, factor de equipo, cap para items sin fuente, `npcBuyPrice` y `npcSellPrice`. El master distingue `market`, `synthetic` y `manual`; todos pueden alimentar NPCs con la política de caps correspondiente.

No se enumeran en el master. Se valoran con una función y tablas auxiliares.

## 7. Objetos compuestos

### 7.1 Fórmula base

```
valor = valorBase
      + premioPorRefine
      + valorDeCartas
      + premioPorSlots
      + valorDeEncantamientos
      + ajusteDeMercado
```

Reglas:

- `valorBase` sale del master.
- Cada carta se valúa con su propio `mid`, no con un precio fijo.
- El valor de una carta insertada no es el 100% de su precio suelto: aplicar descuento de liquidez (0,8–0,95) salvo override.
- `premioPorSlots` compara el mismo item con distintos slots; no duplicar el valor de la carta.
- `premioPorRefine` necesita una curva por tipo de equipo y nivel; no usar una lineal.
- `valorDeEncantamientos` es lo más difícil; usar tablas manuales al principio.
- Evitar que el tasador pague más que el precio esperado de venta.

### 7.2 Etapas

| Etapa | Alcance | Viabilidad |
|---|---|---|
| 1 | Items base only | Alta |
| 2 | Base + cartas | Alta-media |
| 3 | Base + cartas + slots | Media |
| 4 | + refine | Media-baja |
| 5 | + encantamientos/opciones aleatorias | Baja sin tablas manuales |

El master no enumera combinaciones, pero **sí debe incluir las tablas de componentes y un contrato de valoración** para que otro NPC pueda calcular:

```
compose_value(item_base, refine, cartas, slots, encantamientos, opciones)
    -> { low, mid, high, confidence, breakdown }
```

Eso implica guardar, además de los items base:

- valor de cada carta (sale del master);
- curva de refine por tipo de equipo y nivel;
- factor de slots;
- tabla de encantamientos/opciones por grupo y tier;
- descuentos de liquidez y caps.

Para el tasador, empezar por 1–3. Refine y encantamientos quedan para una segunda etapa, tal como dice [13-mercado-npc-tasador.md](./13-mercado-npc-tasador.md), pero el master debe dejar el hueco y las tablas desde el principio.

### 7.3 Refine

Datos disponibles: `db/re/refine.yml`, `db/re/item_randomopt_db.yml`, `db/re/item_randomopt_group.yml`, `db/re/item_enchant.yml`.

Propuesta:

- Curva manual inicial por `(tipo de equipo, nivel)` con multiplicadores sobre el base.
- Validar contra precios de mercado de items refinados (si existen) y contra costo esperado de ores.
- Si no hay datos suficientes, el tasador **no acepta refinados** o usa un piso conservador.

### 7.4 Encantamientos y opciones aleatorias

- `item_randomopt_group.yml` da grupos y probabilidades; `item_randomopt_db.yml` da opciones.
- El valor esperado es `Σ p_i * valor(opción_i)`, pero muchas opciones no tienen precio de mercado.
- Requiere tabla manual de tiers de encantamiento.
- No incluirlo en la primera versión de precios, pero sí dejar la tabla y el contrato de valoración preparados.

---

## 8. Formato y artefactos

### 8.1 Decisión: JSONL canónico + artefactos generados

**Canónico:** `data/market/master.jsonl` (una fila JSON por línea, ordenada por `item_id`).

Por qué JSONL y no SQL/YAML como fuente:

- diffs legibles y por item (un cambio = una línea);
- streaming y bajo consumo de memoria;
- sin dependencia de base de datos para generar;
- fácil de validar y versionar;
- la web y los scripts consumen artefactos generados, no el JSONL directo si no conviene.

**Generados:**

| Archivo | Consumidor | Formato |
|---|---|---|
| `ozro-site/assets/items/market_master.json` | Web | JSON array |
| `sql-files/ozro_market_master.sql` o migración equivalente | Servidor / consultas | SQL |
| `npc/custom/ozro/market_data.txt` | NPCs seleccionados | Arrays rAthena |
| `data/market/master_summary.json` | Análisis | JSON |
| `data/market/validation.md` | Revisión | Markdown |

**Overrides:** `data/market/overrides.yml` (único archivo editado a mano).

Por qué no SQL como fuente: es malo para revisar diffs, requiere migraciones y no lo consume la web directamente. Por qué no YAML: 9k filas, lento y propenso a errores de indentación. SQL y arrays NPC son **salidas**, no la fuente.

### 8.2 Ejemplo de fila

```json
{
  "schemaVersion": 1,
  "id": 7003,
  "name": "Anolian Skin",
  "aegis": "Anolian_Skin",
  "type": "Etc",
  "subtype": null,
  "slots": 0,
  "refineable": false,
  "weight": 10,
  "trade": "free",
  "custom": false,
  "classification": {
    "utility": "material",
    "contentUses": ["quest", "craft"],
    "usedByContent": true,
    "isJunk": false,
    "questOnly": false,
    "instanceOnly": false
  },
  "sources": {
    "kinds": ["mob_drop"],
    "bestAccess": "open",
    "accessFactor": 1.0,
    "mobCount": 6,
    "normalMaps": 2,
    "instanceMaps": 0,
    "guildMaps": 0,
    "npcShop": false,
    "bossOnly": false
  },
  "supply": {
    "dropRateBasePct": 100.0,
    "dropRateEffectivePct": 100.0,
    "spawnAmount": 325,
    "supplyIndex": 228.0,
    "supplyPercentile": 93.0,
    "abundanceTier": "abundant",
    "difficultyIndex": 12.4,
    "difficultyTier": "easy",
    "sourceDiversity": 4,
    "confidence": 0.8
  },
  "demand": {
    "salesLatam": 6254,
    "salesAtlantis": 35528334,
    "liquidity": "liquid",
    "demandRawPercentile": 99.0,
    "demandResidualPercentile": 55.0,
    "demandTier": "medium",
    "confidence": 0.7
  },
  "price": {
    "historical": {
      "latamMedian": null,
      "latamAvg": 3552,
      "atlantisAvg": 3150,
      "atlantisCv": 0.1575,
      "reference": 3552,
      "source": "latam_market_avg",
      "economyScale": 1.0,
      "confidence": 0.766,
      "outlierFlags": []
    },
    "anchors": {
      "npcSellToPlayer": 968,
      "npcBuyFromPlayer": 484,
      "npcShopTypical": null,
      "itemMall": null
    },
    "model": {
      "raw": 3400,
      "rounded": 3500,
      "low": 2890,
      "mid": 3400,
      "high": 3910,
      "buyCeiling": 2550,
      "sellFloor": 1700,
      "confidence": "high",
      "method": "blend_history_supply_demand"
    }
  },
  "uses": {
    "garrett": true,
    "vendedorViajero": false,
    "tasador": true,
    "questReward": false,
    "eventReward": false,
    "web": true
  },
  "quality": {
    "marketEligible": true,
    "priceable": true,
    "needsManual": false,
    "manualOverride": null
  }
}
```

Los nombres exactos pueden ajustarse; lo importante es que el esquema quede versionado y validado.

---

## 9. Herramientas propuestas

No implementar todo de una vez. Estas son las piezas y su orden.

### 9.1 `tools/market/audit_sources.py`

**Rol:** auditoría read-only de las fuentes antes de construir.

Verifica:

- archivos presentes y checksums;
- conteos y duplicados por `item_id`;
- items con precio 0/negativo/nulo;
- items con `avg` y `std_dev` extremos;
- items con `total_sold` ausente;
- cobertura de drop, spawn, HP y acceso;
- items `untradeable`/`unobtainable` con precio;
- diferencias entre taxonomía y master.

Salida: `data/market/audit.json` + resumen Markdown.

### 9.2 `tools/market/build_master.py`

**Rol:** construir el JSONL canónico.

Entradas:

- `conf/import/battle_conf.txt` (rates de drop y HP actuales);
- spawns canónicos generados por `tools/mob_spawns.py`;
- `overrides.yml`;
- item_db/mob_db del servidor;
- datos históricos de mercado congelados (solo referencia).

El builder absorbe la lógica de `generate_item_taxonomy.py`. `taxonomy.json` pasa a ser una salida de compatibilidad generada desde el master, no una fuente separada.

Salidas:

- `master.jsonl`;
- `master_summary.json`;
- `taxonomy.json` de compatibilidad;
- lista de `needs_review` (no revisión item por item).

Debe ser determinista y no consultar red.

### 9.3 `tools/market/price_model.py`

**Rol:** calcular estadísticas robustas, calibración, bandas y backtest.

Incluye:

- medianas y percentiles;
- CV, bandas Atlantis;
- cruce LATAM/Atlantis;
- calibración por anclas NPC;
- evaluación train/test;
- reporte de outliers y errores.

Puede ser una librería importada por `build_master.py` o un paso separado.

### 9.4 `tools/market/validate_master.py`

**Rol:** invariantes y regresión.

Verifica:

- esquema y tipos;
- `id` único y ordenado;
- `low <= mid <= high`;
- `buyCeiling <= mid`;
- `sellFloor <= mid`;
- precios positivos;
- `marketEligible=false` no tiene precio activo;
- `untradeable` no es `tasador=true` ni `vendedorViajero=true`;
- `access_class=instance/guild/quest/event` no es `tasador=true` sin override;
- cobertura y conteos por tier;
- diff contra la versión anterior (items nuevos, eliminados, cambios > X%).

### 9.5 `tools/market/export_site.py`

Genera `market_master.json` para la web, con campos compactos y sin datos internos innecesarios.

### 9.6 `tools/market/export_sql.py`

Genera una tabla `ozro_market_master` (o similar) con índices por `item_id`, `abundance_tier`, `demand_tier`, `price_tier`. Útil para consultas del tasador y de la web si se conecta a la DB.

### 9.7 `tools/market/export_npc.py`

Genera arrays rAthena solo para el subconjunto que cada NPC necesita:

- Garrett: tiers y misiones;
- vendedor viajero: lista curada con stock;
- tasador: items aceptados y bandas de precio.

No meter 9k items en un script NPC. Para el tasador, evaluar `query_sql` contra la tabla generada; para el viajero, arrays pequeños.

### 9.8 `tools/market/simulate_valuation.py`

**Rol:** validar con objetos reales y plausibles.

- Sample de items raros existentes (anonimizado).
- Generación de equipo +7, cartas, combinaciones.
- Comparación contra precio de mercado limpio.
- Revisión de top 1%, bottom 1%, únicos y sin historial.

---

## 10. Validación y criterios de aceptación

### 10.1 Criterios del master base

- [ ] 100% de las filas con `id`, `name`, `type`, `trade`.
- [ ] 100% de los items tradeables/obtenibles tienen al menos una fuente o `no_source` explícito.
- [ ] 100% de los precios activos tienen `low <= mid <= high`.
- [ ] 0 items `untradeable` marcados para tasador/viajero.
- [ ] 0 items `instance/guild/quest/event` marcados para tasador sin override.
- [ ] 100% de los items con precio tienen `price_confidence` y `outlier_flags`.
- [ ] Cobertura de precio > 80% del universo tradeable/obtenible, con `unknown` explícito para el resto.
- [ ] Overrides con razón, fecha y fuente.
- [ ] Build determinista (dos corridas = mismo output salvo `generatedAt`).

### 10.2 Criterios del modelo

- [ ] El precio correlaciona negativo con `supply` dentro de cada tipo (Spearman < -0,2 en los tipos con n suficiente).
- [ ] El precio correlaciona positivo con `demand_residual` (Spearman > 0,1).
- [ ] Ningún precio supera el techo NPC cuando el NPC vende el item.
- [ ] Ningún precio baja del piso NPC cuando el NPC compra el item.
- [ ] Backtest: error absoluto mediano de log-precio aceptable en high/medium; documentar el número, no inventarlo.
- [ ] Top 1% y bottom 1% revisados a mano.
- [ ] Items sin historial no reciben precios altos sin revisión.

### 10.3 Criterios de integración NPC

- [ ] Garrett actual sigue funcionando hasta que el master pase validación.
- [ ] El reemplazo de Garrett usa `master.jsonl` como entrada, no listas hardcodeadas.
- [ ] El vendedor viajero no vende por encima del NPC shop ni del item mall.
- [ ] El tasador no acepta items no comerciables, de instancia, quest o evento.
- [ ] Los scripts generados pasan `tools/npc_textwidth.py` y no superan 8 líneas por página.
- [ ] No se pierden datos persistentes existentes (`#CARD_*`, etc.).

---

## 11. Fases y viabilidad

| Fase | Alcance | Entregable | Estimación |
|---|---|---|---|
| F0 | Auditoría y congelado de fuentes | `audit.json`, fuentes copiadas, decisiones de universo | 0,5–1 día |
| F1 | Esquema y builder de identidad/fuentes | `master.jsonl` sin precios, validador básico | 1–2 días |
| F2 | Abundancia, dificultad y demanda | Tiers y reporte de cobertura | 1–2 días |
| F3 | Precio histórico limpio y modelo | Precios, bandas, confianza, backtest | 1–2 días |
| F4 | Artefactos e integración NPC | JSON web, SQL, arrays NPC, reemplazo de Garrett | 2–3 días |
| F5 | Objetos compuestos | Cartas/slots; refine; encantamientos | 1–2 semanas |
| F6 | Tasador y consignación | Persistencia, anti-dupe, menú, comisión | 1–2 semanas |

**Total master base (F0–F4):** aproximadamente 1–2 semanas de trabajo efectivo, con validación manual incluida. F5 y F6 son proyectos aparte.

### Viabilidad por fase

- **F0–F2:** alta. Los datos existen; el trabajo es de consolidación y criterio.
- **F3:** media-alta. La cobertura histórica es parcial, pero alcanza para una primera versión con confianza estratificada.
- **F4:** alta. Es generación de artefactos y reemplazo de tablas.
- **F5:** media-baja. Cartas y slots sí; refine y encantamientos requieren tablas manuales.
- **F6:** baja-media. El precio no resuelve persistencia, anti-dupe ni experiencia de usuario.

---

## 12. Riesgos y mitigaciones

| Riesgo | Severidad | Probabilidad | Mitigación |
|---|---|---|---|
| LATAM/Atlantis no representan OzRo | Alta | Alta | Calibración con anclas NPC, confianza, overrides, bandas |
| `total_sold` sin ventana temporal | Alta | Alta | Demanda residual por tipo y decil de supply; no usar crudo |
| Outliers en promedios Atlantis | Alta | Alta | Mediana, CV, bandas recortadas, flags, revisión manual |
| Cobertura incompleta (3.964 sin precio) | Alta | Alta | `priceStatus=synthetic`; fallback conservador en NPC, no `priceable=false` |
| Rates custom distorsionan la oferta | Alta | Alta | `eff_rate` con multiplicadores; supply index, no unidades absolutas |
| Accesos mal clasificados (instancia/quest/guild) | Alta | Media | `access_class` central, overrides, auditoría de fuentes |
| `unobtainable` con falsos positivos | Media | Alta | Flag, no exclusión automática; revisar 803 casos |
| Objetos compuestos fuera de control | Alta | Media | Tablas de componentes + contrato; empezar por base y cartas; refine/encantamientos después |
| Precio NPC genera arbitraje | Alta | Media | `buy_ceiling`, spreads, comisión, caps diarios, stock |
| Precio sintético paga de más | Alta | Media | `buyCeiling` desde low, haircut, caps absolutos, monitoreo |
| Manipulación no detectada | Media | Media | Reglas generales de CV/max/offers; ejemplos como validación, no excepciones |
| Formato/runtime NPC | Media | Media | JSONL canónico + SQL/arrays generados; no leer JSON en runtime |
| Mantenimiento y “no tocar más” | Media | Alta | Versionado, regeneración, overrides auditables |
| Anti-dupe/persistencia del tasador | Alta | Alta | Sistema aparte; empezar por compra instantánea conservadora |
| Datos de terceros / procedencia | Baja | Baja | Uso interno, sin scrapear de nuevo, documentar fuente |
| Nombres duplicados/variantes | Media | Media | Usar `item_id`; nombres solo para display |

---

## 13. Decisiones tomadas y pendientes

### Tomadas

- **Master de todos los items**, con `tags`, `marketEligible` y `priceStatus`; el universo de mercado es una vista.
- **Reconstruir** la master list desde fuentes crudas; `master_list.json` anterior queda como referencia, no como base.
- **Sintético como fallback** para NPCs, con piso conservador, haircut y caps; no se revisa item por item.
- **Taxonomía integrada**: la master list es la fuente de verdad; `taxonomy.json` queda como insumo/vista.
- **JSONL canónico** + artefactos generados.
- **Objetos compuestos**: el master debe dejar tablas y contrato de valoración; no se enumeran combinaciones.

### Pendientes

1. **Semántica exacta de precio:** `mid` P2P, `buyCeiling` NPC, `sellFloor`; confirmar spreads.
2. **Calibración externa:** factor global o por categoría; cuánto peso al histórico vs intrínseco.
3. **Demanda:** pesos LATAM/Atlantis y tratamiento de `unknown`.
4. **Umbral de HP efectivo:** 10M actual; confirmar si es el canon.
5. **Grupo/paquete/craft:** nivel de detalle en la v1; probabilidades y costos.
6. **Runtime:** SQL para tasador vs arrays para viajero/Garrett.
7. **Frecuencia de regeneración:** manual, por cambio de rates/drops, o trimestral.
8. **Criterios de revisión manual:** solo outliers/custom, no item por item.

---

## 14. Recomendación de arranque

1. **F0:** congelar fuentes y correr `audit_sources.py`. No cambiar nada del servidor.
2. **F1:** construir el master de identidad, fuentes, acceso y utilidad para los 8.871 items tradeables/obtenibles. Sin precios todavía.
3. **F2:** calcular abundancia y dificultad. Revisar a mano los accesos dudosos (instancia, guild, quest, mobs imposibles).
4. **F3:** limpiar precios históricos y calcular bandas. Generar precios sintéticos como fallback para todos los items; los NPC usan piso conservador, haircut y caps.
5. **F4:** reemplazar las entradas de Garrett y preparar el vendedor viajero. Mantener Garrett actual hasta que la validación pase.
6. **F5/F6:** recién después, objetos compuestos y tasador.

El primer entregable concreto debería ser un **reporte de auditoría** y un **master base sin precios**, para revisar cobertura y accesos antes de discutir fórmulas de precio. Eso reduce el riesgo de construir un modelo sofisticado sobre datos mal clasificados.

---

## 15. Relación con los NPCs existentes

- **Garrett:** los generadores específicos (`generate_garrett_missions.py`, `generate_garrett_npc.py`) y `garrett-missions.json` se eliminaron. `trasher.txt` conserva arrays legacy embebidos hasta que el master lo reemplace. El nuevo generador debe ser genérico (`export_npc.py`) y tomar los datos del master, no una fuente propia de Garrett. Mantener las variables `#GARRETT_*` para no perder progreso.
- **Vendedor viajero:** consume una lista curada de items y stock; el precio sale del master con techo NPC/item mall. No necesita ledger en la primera versión.
- **Tasador:** consume `buy_ceiling`, `low/mid/high` y flags de elegibilidad. La consignación, persistencia y anti-dupe son un sistema aparte; el master solo aporta el valor.
- **Web:** consume `market_master.json`, generado desde el master. `taxonomy.json` queda como vista de compatibilidad o se retira cuando la web migre.
- **Eventos y quests:** usan bandas de precio para presupuestar recompensas, no precios hardcodeados.

---

## 16. Revisión previa a la master

### 16.1 Lo que ya tenemos

- `taxonomy.json` con 29.061 items, fuentes, flags y `access` por item.
- `master_list.json` con 5.858 items, precio histórico, ventas, rareza y drop.
- 4.907 items del universo de mercado con precio; 3.964 sin precio.
- 1.421 items con desviación real de Atlantis; 163 con CV > 3.
- Spawns, mob_db con HP/defensa, rates custom y NPC shops.
- Reglas de acceso ya centralizadas: 263 `instance_only`, 36 `guild_only`, 156 `high_hp`, 555 `boss_only`, 744 `no_spawn`.
- Los generadores específicos de Garrett fueron eliminados.

### 16.2 Gaps que hay que cerrar antes de construir

1. **Fuente de spawns inconsistente.** Hay tres conjuntos:
   - `ozro-site/assets/spawns/spawns.json`: 3.867 líneas, 410 mapas, 1.384 mobs, sin `delay`.
   - `ragnabots/staging/market/spawns/spawns_normal.json`: 3.173 líneas, 357 mapas, 1.132 mobs, con `delay`, sin boss.
   - `tools/mob_spawns.py`: 3.656 líneas, 405 mapas, 1.223 mobs, con `delay`, `is_boss` e `is_instance`.
   El master debe usar **una sola fuente canónica**. Recomendación: `mob_spawns.py` regenerado, no los snapshots.

2. **Boss y spawns especiales.** La taxonomía actual incluye spawns de boss en `mob_maps`; para abundancia normal hay que excluirlos o separarlos. También hay spawns dinámicos de instancia que no aparecen como spawn top-level (solo 1 en el generador canónico).

3. **Grupos y paquetes sin probabilidad.** 2.379 items sin precio son solo `group`. No alcanza con saber que pertenecen a un grupo: hay que saber qué grupo, qué tasa y qué lo dispara. `item_group_db.yml` tiene `Rate`, pero la fuente del grupo no está modelada.

4. **Craft sin costo.** 1.356 items tienen `craft` como mejor acceso. `produce_db` y Laphine dan recetas, pero no el costo esperado con éxito/fallo. Sin eso, el precio intrínseco queda incompleto.

5. **Demanda sin ventana temporal.** `total_sold` es acumulado de toda la vida de otro servidor. El residual por tipo/abundancia ayuda, pero no es “ventas por día”.

6. **Precio sintético con error alto.** El mejor modelo simple da 3,4x de error mediano. Se acepta como fallback, pero con piso conservador, haircut y caps; no se usa el `high` para comprar.

7. **Conflictos de flags.** 803 items con precio están marcados `unobtainable` y 200 marcados `untradeable`. No son errores necesariamente, pero requieren revisión.

8. **Manipulación de mercado.** Strawberry y similares no se arreglan solo con un filtro estadístico; usar reglas generales (`cv`, `max/avg`, `offers_min`, `total_sold`), marcar `manipulation_suspected` y usar los casos conocidos solo como validación.

9. **Objetos compuestos.** Cartas, refine, slots, encantamientos y opciones aleatorias no están cubiertos por una fila de item.

10. **Sin listings individuales.** No hay datos de publicaciones sueltas para detectar “1 unidad a precio absurdo” con precisión; por ahora es heurística sobre agregados.

### 16.3 Decisiones importantes

| # | Decisión | Recomendación |
|---|---|---|
| D1 | ¿Master de 29k items o solo del universo de mercado? | **29k** con `marketEligible` y `priceStatus`; el universo de mercado es una vista. |
| D2 | ¿Reutilizar `master_list.json` o reconstruir? | **Reconstruir** desde fuentes crudas; usar `master_list` solo como control cruzado. |
| D3 | ¿Qué spawns usa el master? | **`mob_spawns.py`** regenerado, con `delay`, `is_boss` e `is_instance`. |
| D4 | ¿Precio puntual o rango? | **Rango** `low/mid/high` con `buyCeiling` y `sellFloor`; nunca un número sin confianza. |
| D5 | ¿Precio sintético para NPC? | **Sí, como fallback** (`synthetic`) con piso conservador, haircut y caps. |
| D6 | ¿Demanda cruda o residual? | **Residual** por tipo y decil de abundancia; crudo solo fallback. |
| D7 | ¿Categorías o tags? | **Tags por item** (`tags`), además de las categorías derivadas. |
| D8 | ¿Grupos/craft en la v1? | **Tags y metadata sí; precio completo no.** Fase posterior. |
| D9 | ¿Formato canónico? | **JSONL** + artefactos generados JSON/SQL/NPC. |
| D10 | ¿Cuándo integran los NPC? | Recién cuando el master pase validación y exista una versión congelada. |

### 16.4 Mejoras posibles

- Agregar `tags` (meta-categorías múltiples) a cada fila, no depender solo de pertenencia a categorías.
- Agregar `priceStatus` y `marketEligible` explícitos.
- Agregar `data/market/canon.yml` con las decisiones aprobadas (rates, umbral de HP, haircut sintético, caps, formato). Es el contrato que futuras herramientas deben respetar.
- Agregar `sourceDetails` para grupo/paquete/craft: grupo, tasa, receta, materiales.
- Separar `supplyNormal`, `supplyBoss`, `supplyInstance` para no mezclar flujos.
- Agregar un archivo de **ejemplos** de manipulación para validar el detector, no una lista de excepciones.
- Agregar un backtest con holdout y un “golden set” de items revisados a mano.
- Agregar un reporte de diff entre versiones del master.
- Generar una vista web filtrada para no enviar 29k filas al cliente.
- Definir una conversión item mall → zeny o dejar el techo en `manual`.

### 16.5 Checklist de salida antes de crear la master

- [ ] Universo decidido (29k vs 8.871).
- [ ] Fuente canónica de spawns decidida.
- [ ] Semántica de `mid`, `low`, `high`, `buyCeiling`, `sellFloor`.
- [ ] Política de precio sintético aprobada.
- [ ] Tratamiento de grupo/paquete/craft definido.
- [ ] Reglas de outlier y manipulación documentadas.
- [ ] Formato canónico y artefactos generados definidos.
- [ ] Criterios de confianza y revisión manual aprobados.
- [ ] Responsable y frecuencia de regeneración definidos.
- [ ] Plan de validación y rollback para NPCs.

---

## 17. Comentarios

- La idea de “clasificación maestra que no se vuelve a tocar” es correcta como objetivo de estabilidad, pero no como promesa literal: los rates, drops y la economía cambian. Lo que debe quedar estable es el esquema y los IDs; los valores se regeneran.
- El mayor riesgo no es el precio: es la clasificación de acceso. Un item de instancia mal clasificado puede hacer que un NPC pague de más y romper la economía.
- El segundo mayor riesgo es la demanda. `total_sold` es ventas acumuladas de otro servidor; sirve como señal relativa, no como “demanda diaria de OzRo”.
- No conviene construir el tasador antes del master. Sería optimizar el menú de un NPC mientras la tabla de precios todavía se mueve.
