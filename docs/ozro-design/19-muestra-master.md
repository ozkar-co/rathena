# Muestra de la master de mercado

**Estado:** muestra generada (no es el master final)  
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
- `mob_db`/`item_db` del servidor para HP, defensa, slots y refine;
- `master_list.json` solo como histórico de precio/ventas.

Genera una muestra aleatoria de 150 items **market-eligible** y 103 casos borde. No modifica la taxonomía ni el servidor.

Comando:

```bash
python3 tools/market/build_sample.py
```

Salida:

- `general.jsonl`: muestra general de la población con precio potencial.
- `edge.jsonl`: casos borde con `edgeTags`.
- `summary.json`: conteos, rates, tipos de spawn y distribución de la muestra.
- `REPORT.md`: reporte generado con tablas y señales detectadas.

---

## 2. Decisiones aplicadas

### 2.1 Fuentes canónicas

- Los rates se leen de `conf/import/battle_conf.txt`, no del snapshot viejo de ragnabots.
- El HP efectivo aplica `monster_hp_rate` y `mvp_hp_rate` (hoy 200%, es decir, 2x).
- Los spawns se regeneran con `tools/mob_spawns.py`, que incluye `delay`, `is_boss` e `is_instance`.

### 2.2 Tipos de spawn

Cada línea de spawn se clasifica en:

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

`supplyOpen` usa solo `field + dungeon`. Boss, instancia, guild, quest, event y other se guardan aparte. Esto evita inflar la abundancia con fuentes que no son farmeo abierto.

### 2.3 Precio y elegibilidad

- `marketEligible`: item comerciable, con fuente o precio histórico.
- `priceStatus`:
  - `market`: hay precio histórico;
  - `synthetic`: no hay histórico, pero el item es elegible;
  - `not_applicable`: no comerciable o sin fuente/precio.
- El sintético usa mediana del tipo + multiplicadores de supply, demanda y dificultad.
- Se aplica un factor general de calidad de fuente al sintético:

| Mejor acceso | Factor |
|---|---:|
| `group` | 0,70 |
| `craft` | 0,90 |
| `quest` / `instance` | 0,80 |
| `guild` | 0,70 |
| `unknown` / `none` | 0,50 |
| `normal` / `npc` / `cash` | 1,00 |

- `buyCeiling` (lo que un NPC puede pagar):
  - sintético: 45% del mid, cap 50% de la mediana del tipo;
  - market high: 75% del mid;
  - market medium: 60% del mid, cap 1 mediana del tipo;
  - market low: 45% del mid y 75% del low, cap 50% de la mediana;
  - manipulación: 35% del mid y 70% del low, cap 50% de la mediana.

### 2.4 Tags

Los tags salen de las categorías de la taxonomía más las restricciones de `access`. Un item puede tener varios: `group`, `craft`, `instance_only`, `guild_only`, `boss_only`, `high_hp`, `npc_shop`, `unobtainable`, `untradeable`, etc.

---

## 3. Lectura de la muestra general

Población: **9.622 items market-eligible**.

| Métrica | Valor |
|---|---:|
| Items totales en el catálogo | 29.061 |
| `marketEligible` | 9.622 |
| `market` | 5.652 |
| `synthetic` | 3.970 |
| `not_applicable` | 19.244 |
| Con supply abierto | 1.615 |
| Sin supply abierto | 8.007 |
| Clampeados por ancla NPC | 1.004 |
| Manipulación sospechada | 166 |

La muestra general de 150 items quedó:

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

**Hallazgo principal:** 123 de 150 items de la muestra no tienen supply abierto. La mayor parte del precio no va a salir de abundancia de spawn, sino de group/craft/npc o del prior del tipo. El modelo de abundancia es útil para el subconjunto farmeable, pero no alcanza para el total.

En la muestra:

- Los `market` tienen mediana de `mid` 859.000z y de `buyCeiling` 160.000z.
- Los `synthetic` tienen mediana de `mid` 1.050.000z y de `buyCeiling` 473.000z.
- 37 de los 49 sintéticos son `group`.
- Solo 2 sintéticos tienen supply abierto.

El sintético sigue siendo más caro que el mercado en la mediana, aun después del factor de fuente. Es un sesgo esperable por usar la mediana del tipo; conviene mantener el `buyCeiling` conservador y no usar el `mid` sintético como precio de compra.

---

## 4. Lectura de casos borde

La muestra borde tiene 103 items. Categorías principales:

| Caso | n | Lectura |
|---|---:|---|
| `craft_best` | 8 | El precio depende del costo de receta; todavía no está modelado. |
| `guild_only` | 8 | Sin supply abierto; el precio histórico manda, pero el NPC no debería comprar sin cap. |
| `instance_only` | 7 | Igual que guild: el acceso no es farmeo abierto. |
| `boss_only` | 5 | Muchos tienen además NPC shop o quest; el tag no debe ser exclusión automática. |
| `high_hp` | 7 | HP extremo o fuente sin spawn; el modelo los marca, pero no siempre son unfarmeables. |
| `group_only` | 7 | Sintéticos con prior de tipo; son los más sensibles a sobrevaloración. |
| `no_price_with_open_supply` | 8 | Donde el modelo sintético tiene mejor sustento. |
| `manipulation_suspected` | 4+ | Items como Red Potion/Herb muestran CV alto; el detector general funciona. |
| `custom` | 5 | Monedas OzRo: `not_applicable`; requieren canon manual. |
| `max_open_supply` | 5 | Hierbas, Fly Wing, Zargon, Sticky Mucus; precios bajos y abundancia alta. |
| `min_open_supply` | 8 | Cartas con supply casi cero; el percentil las pone en `rare`, pero el redondeo las muestra como 0. |
| `price_top_1pct` | 8 | Pet eggs sin fuente y precios altos; entran por histórico, no por acceso. |
| `price_bottom_1pct` | 8 | Pociones, manzanas, flechas; manipulación o precio NPC. |

### Señales concretas

- **El tag `boss_only` no significa inaccesible.** Varios items con `boss_only` también tienen NPC shop, quest o craft. Sirve como advertencia, no como bloqueo.
- **Los items de instancia/guild no tienen supply abierto.** Tienen precio histórico, pero el modelo de abundancia no aplica. El NPC debe usar caps.
- **Los group-only son el mayor riesgo de sobrevaloración.** El factor 0,70 ayuda, pero el `mid` sigue siendo una mediana de tipo, no una estimación real.
- **Los custom no tienen mercado.** `not_applicable` es correcto; hay que definir su canon aparte.
- **Los pet eggs entran por precio, no por fuente.** Son market-eligible por histórico, pero no tienen acceso; conviene marcarlos para revisión.
- **Las hierbas/pociones con CV alto son manipulación o precio NPC.** El detector las marca, pero el `mid` puede quedar en valores absurdos; el `buyCeiling` las contiene.
- **1.004 items fueron clampeados por anclas NPC.** El precio externo y el precio NPC no siempre son compatibles; el ancla debe mandar.

---

## 5. Decisiones que tomé para esta muestra

1. **Población general = market-eligible**, no los 29k. El catálogo completo queda en el master, pero la muestra de precio se enfoca en items con uso potencial.
2. **`not_applicable` para untradeable/unobtainable sin fuente ni precio.** No se inventa precio para 19.244 items.
3. **`supplyOpen = field + dungeon`.** Boss, instancia, guild, quest, event y other no cuentan como abundancia abierta.
4. **Factor de calidad de fuente para sintéticos.** Group 0,70, craft 0,90, quest/instancia 0,80, sin fuente 0,50.
5. **`buyCeiling` conservador.** Nunca se paga el `high`; sintético 45%, low/manipulación 35–45%, con cap por mediana del tipo.
6. **Manipulación por reglas generales.** CV > 3 o `atlantis_extreme_max`, sin listas de IDs.
7. **Tags múltiples.** Un item puede ser `boss_only`, `npc_shop` y `quest_source` a la vez; el consumidor decide.
8. **Sin reglas especiales por item.** Los casos raros se marcan para revisión, no se parchean con excepciones.

---

## 6. Riesgos y pendientes

- **Group/package:** 8.007 market-eligible sin supply abierto. El sintético por tipo es el fallback, pero no distingue bien dentro del grupo. Pendiente: tasa del grupo y fuente que lo dispara.
- **Craft:** el costo de receta no está incluido. Pendiente: costo de materiales + éxito/fallo.
- **Item mall:** no hay conversión a zeny; el techo queda en NPC/manual.
- **Pet eggs y items sin fuente:** entran por precio histórico; conviene una regla de elegibilidad más estricta o revisión.
- **Custom:** monedas OzRo sin precio; requieren canon manual.
- **Umbral de HP:** 10M efectivo; confirmar si es el canon.
- **Synthetic de equipo:** la mediana del tipo puede sobrevalorar equipo raro; el `buyCeiling` lo contiene, pero el `mid` sigue siendo alto.
- **Demanda:** residual por tipo/abundancia; falta definir pesos LATAM/Atlantis.
- **Compuestos:** el master debe incluir tablas de refine/cartas/slots/encantamientos y el contrato `compose_value`.

---

## 7. Próximos pasos

1. Revisar esta muestra y fijar en `data/market/canon.yml`:
   - factor de fuente;
   - política de `buyCeiling`;
   - umbral de HP;
   - tratamiento de group/craft/item mall.
2. Mejorar group/package y craft en el modelo, o aceptar explícitamente el prior de tipo.
3. Definir la regla para pet eggs/items sin fuente.
4. Construir el master completo con `build_master.py` usando la misma lógica.
5. Generar artefactos JSON/SQL/NPC y recién después integrar NPCs.
