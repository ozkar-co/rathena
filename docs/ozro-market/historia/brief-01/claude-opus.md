# Propuesta de rediseño — Mercado de OzRo

Respuesta al brief de revisión externa del MarketSimulator y del NPC tasador (rAthena, Renewal, rates custom).

## Resumen

Hoy el modelo mezcla unidades distintas, y un booleano decide si un item usa el histórico o un percentil del tipo. La propuesta tiene tres partes:

- **Una sola unidad para todo:** las horas de juego que cuesta conseguir una unidad.
- **Un solo modelo estadístico para los 29k items.** El histórico pasa a ser evidencia que corrige el precio, no el precio mismo.
- **Tres ejes en lugar de booleanos:** cómo se obtiene, cómo se transfiere y en qué estado está su mercado.

---

## 0. Primero, arreglar la ingesta

Sin este paso nada de lo demás es confiable.

```python
# Mal: mobs[id] = row   → el import borra HP, nivel y drops
def merge_mob(base: dict, patch: dict) -> dict:
    out = dict(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge_mob(out[k], v)
        else:
            out[k] = v          # solo pisa los campos presentes en el import
    return out

for row in import_rows:
    mobs[row["Id"]] = merge_mob(mobs.get(row["Id"], {}), row)
```

Además de ese arreglo:

- **Variantes de evento:** no deben reemplazar al mob canónico. La fuente de un item es el *conjunto* de mobs que lo dropean (GTB 1086 **y** 2306), cada uno con su spawn. Si uno no tiene spawn, simplemente no aporta flujo; no anula la ruta.
- **Mapas desconocidos** (`alb_ship`): clasificarlos por `mapflag` (town / pvp / gvg / instance). Si no hay dato, que cuenten como `field` y queden en un reporte de "mapas sin clasificar", en vez de caer en `other` con flujo 0.
- **Tests de ingesta que hagan fallar el build:**
  - todo mob con spawn tiene HP > 0;
  - toda carta de MVP tiene al menos un mob fuente con spawn;
  - el número de mobs con drops no baja al aplicar el import;
  - un diff de conteos contra la corrida anterior.

---

## 1. Ontología: tres ejes independientes

### 1.1 Transferencia

Sale directo de los flags de `Trade` en rAthena, cada uno con su significado real:

| Flag | Efecto correcto |
|---|---|
| `NoTrade` (sin `TradePartner`) | No hay comercio entre jugadores. Es el **único** flag que saca al item del mercado. |
| `NoSell` | El NPC no lo compra: `npcBuyPrice = null`. |
| `NoDrop` | No se puede tirar al suelo. Para el precio no importa. |
| `NoStorage`, `NoGuildStorage`, `NoMail`, `NoCart`, `NoAuction` | Penalizan la **liquidez**: descuento chico y más varianza. No excluyen. |
| Bound (cuenta / personaje) | `no_transfer`. |

### 1.2 Adquisición

Es una lista de rutas. Cada ruta tiene:

```
{tipo, costo_horas, costo_zeny, insumos, p_exito, destructiva, fuente_del_dato}
```

Tipos posibles: `farm`, `mvp`, `craft`, `quest`, `box`, `npc_shop`, `cash`, `event`, `legacy`, `unknown_parse`.

Que no haya ninguna ruta es información, no un valor neutro. `unknown_parse` describe la cobertura del parser, no una propiedad del item, y debe salir en su propio reporte.

### 1.3 Estado del mercado

- `active`: hay evidencia de ventas suficiente;
- `thin`: hay entre 1 y 2 ventas;
- `legacy`: hay evidencia pero ninguna ruta;
- `none`: no hay ni evidencia ni ruta.

### 1.4 Reglas que quedan

```
marketEligible = transferible_entre_jugadores AND (tiene_ruta OR tiene_evidencia)
npcBuyPrice    = null si NoSell; si no, ≤ Sell configurado (nunca por encima)
```

Con esto:

- Bouquet entra al mercado, porque solo tiene `NoDrop`.
- Thanos Spear deja de ser "unobtainable" y pasa a `legacy` o `unknown_parse`.
- Desaparecen los 4,434 casos NoSell a los que el NPC les pagaba.

---

## 2. La primitiva: horas de juego por unidad

Todo se lleva a **h = horas que un jugador dedicado tarda en conseguir una unidad**.

### Farm normal

```
kills/h = min( 3600 / (TTK + t_búsqueda),
               cantidad × 3600 / respawn / competidores )
h       = 1 / (kills/h × drop_efectivo)
```

- TTK (tiempo por kill) = HP_ef / DPS_ref(nivel del mob), con DEF y MDEF incluidas en HP_ef.
- El drop efectivo debe usar los rates custom y los topes min/max de drop de rAthena.

### MVP / time gate

```
h = respawn_h × competidores / drop_efectivo
```

- **GTB:** 1 h / 0.01% → unas 10,000 h ÷ multiplicador de rate.
- **Ifrit:** 11 h → unas 110,000 h. Ahora es más caro **por construcción**, sin empatar con GTB.
- **Monster Coin:** mob nivel 1, drop 100%, 25 spawns → h ≈ 0.001. Basura, como debe ser.

El zeny por hora del servidor no hace falta conocerlo item por item: se ajusta con los datos (sección 3).

---

## 3. Un solo modelo, sin acantilado

Es una regresión jerárquica en log, ajustada sobre los ~5,800 items con historia y aplicada a todos:

```
log m_{i,s} = a_s + β·log(h_i) + γ_clase(i) + u_i + ε_{i,s}
```

| Término | Significado |
|---|---|
| `a_s` | Nivel de precios de cada fuente (LATAM, Atlantis). Absorbe la inflación y el zeny/hora de cada servidor. |
| `β` | Elasticidad precio–costo. Se espera un valor < 1, del orden de 0.5–0.8. |
| `γ_clase` | Efecto de clases finas y anidadas; las clases chicas se acercan a su clase padre. |
| `u_i` | La **demanda** del item, con media 0 y encogida según el tamaño de muestra. |
| `ε` | Error con distribución **t de Student** (ν≈4), no normal. |

**Clases finas** (ejemplos):

- Card × {normal, boss, MVP} × ranura;
- Etc × {material de craft, ingrediente de quest, basura de mob de bajo nivel};
- Equipo × slots × nivel requerido.

**Por qué t de Student:** un desacuerdo de 20x entre fuentes se absorbe solo, sin elegir una fuente en silencio.

**Ancla de OzRo:** `a_OzRo` es **un único parámetro global, explícito y versionado** que define el nivel absoluto de la economía. Ese nivel es la parte que de verdad no se conoce, y queda en un solo lugar en lugar de repartido en 29k precios.

### 3.1 Posterior por item

- Con 0 ventas, el precio es prácticamente la predicción del modelo y la banda queda ancha automáticamente.
- Con muchas ventas consistentes, domina la evidencia.
- La varianza de cada observación es `σ²/n_ventas + τ²`, donde τ es la dispersión entre servidores (se estima con los 898 pares en desacuerdo).

**Ejemplos:**

- **Menblatt:** el costo dice que es mucho más caro que Frilldora, y LATAM (1.5M) contra Atlantis (30.2M) es un conflicto marcado. El posterior queda por encima de Frilldora.
- **Ice Pick:** 2 ventas pesan poco y la estimación se acerca a la clase.

```python
from math import exp

SIGMA = 0.6   # dispersión de una venta individual (log), a estimar
TAU   = 0.5   # dispersión entre servidores (log), a estimar

def posterior(prior_mu, prior_sd, obs):  # obs: [(log_m, n, bias_s)]
    # aproximación normal; con t de Student usar IRLS o un MCMC corto
    prec, num = 1 / prior_sd**2, prior_mu / prior_sd**2
    for log_m, n, b in obs:
        var = SIGMA**2 / max(n, 1) + TAU**2
        prec += 1 / var
        num += (log_m - b) / var
    mu, sd = num / prec, prec**-0.5
    return {"p10": exp(mu - 1.2816 * sd),
            "p50": exp(mu),
            "p90": exp(mu + 1.2816 * sd)}
```

Los valores de `SIGMA` y `TAU` son marcadores de posición; deben salir del ajuste.

---

## 4. Rutas compuestas

- **Craft destructivo** (el insumo se pierde si falla):
  ```
  C = (P_base + zeny + Σ insumos) / p
  ```
  - Pantie[1]: (P_pantie + 1M + P_elunium) / 0.05 ≈ 20M o más.
  - Si el insumo **no** se pierde: `C = P_base + (zeny + insumos) / p`.
- **Varias rutas:** el costo del item es el **mínimo** entre sus rutas, porque la ruta más barata pone el techo por arbitraje. Ese mínimo entra como h en el modelo.
- **Cajas y grupos:**
  - costo de obtener el item i = costo_caja / p_i;
  - valor esperado de la caja = Σ p_i·P_i (sirve como chequeo de consistencia).
- **Cash shop:** costo = precio cash × tasa zeny/cash, que es un parámetro global ajustado con los datos.
- **Quests:** suma de insumos + zeny + horas. Si la recompensa es bound, no entra al mercado.
- **Circularidad:**
  - Armar un grafo de recetas y calcular en orden topológico.
  - Si hay ciclos (canjes A↔B, refine loops), hacer una iteración de punto fijo amortiguada (`P ← 0.5·P + 0.5·f(P)`, que converge porque `p < 1` y hay costos positivos).
  - Si no converge, cortar el ciclo y marcarlo en el reporte.

---

## 5. Salida y seguridad del NPC tasador

### 5.1 Formato de salida

- p10/p50/p90 en log-normal, que ya es asimétrico.
- Registro de procedencia por item:
  - ruta elegida y sus horas;
  - fuentes, n y peso de cada una;
  - clase, demanda u_i y overrides aplicados.
- **Precios multimodales** (variantes con refine o cartas): separarlos en variantes propias (item + refine + cartas), en lugar de forzar una sola distribución.

### 5.2 El tasador es una fuente de zeny y por eso un vector de exploit

- Si el tasador compra, paga como máximo `k × p10` (k ≤ 0.5), solo para estado `active` y con tope diario.
- Nunca por encima de `Sell` si el item es NoSell.
- Invariante sin excepciones: compra del NPC < venta del NPC del mismo item, contando Overcharge/Discount (hasta 24%).

---

## 6. Validación sin ground truth

1. **Holdout:**
   - Ocultar la historia del 20% de los items con mercado y predecirlos solo con costo + clase.
   - Medir el error en log.
   - Medir la **cobertura**: cerca del 80% de los reales debería caer entre p10 y p90.
   - Esto reemplaza al ground truth que no existe.
2. **Monotonía:**
   - dentro de una clase, si h_A > h_B, entonces p50_A ≥ p50_B, salvo que u_A − u_B lo explique dentro de su intervalo;
   - las violaciones salen en un reporte, no se ocultan.
3. **Invariantes:**
   - ningún item transferible con ventas queda fuera del mercado;
   - craft ≤ costo de su receta × (1 + margen);
   - consistencia del valor esperado de las cajas;
   - compra del NPC < venta del NPC.
4. **Estrés:**
   - si se duplica `item_rate`, los items solo-drop deben bajar ~2^β y los items de NPC shop no deben moverse;
   - si cambia `a_OzRo`, todo escala igual.
5. **Diff entre corridas:** reporte de los 200 cambios más grandes, para revisión.

---

## 7. Fórmula / manual / LLM

### Determinista

Ingesta, rutas, costos, regresión, posterior, NPC y tests.

### LLM (2–5 USD), pasada única, guardada en caché por hash

- Etiquetar el rol de los items Etc y la clase de los items que el parser no puede ubicar. La salida son etiquetas, no precios. Es la mayor ganancia por dólar.
- Revisar los ~300 casos con más varianza × impacto económico. La salida es una justificación más un multiplicador acotado entre 0.5x y 2x.
- Todo lo que produzca se guarda como overrides versionados con su razón. **Nunca escribe un precio directo.**

### Manual

- `a_OzRo` y la tasa zeny/cash.
- Overrides puntuales con motivo y fecha en un archivo versionado.

---

## 8. Respuestas cortas a las 10 preguntas

1. **Costo de adquisición:** sí, es la primitiva correcta, medido en horas. El zeny/hora no se estima: se ajusta como `a_s` por fuente, y para OzRo queda un solo parámetro explícito.
2. **Items legacy, de evento o sin ruta:**
   - sin evidencia → "sin precio", que es una salida válida;
   - con evidencia → `legacy`, con el precio de la evidencia y varianza extra.
3. **Dos servidores en desacuerdo:** modelo jerárquico con sesgo por fuente y verosimilitud t de Student. No mediana, no elegir una.
4. **Demanda con muestras chicas:** u_i se encoge hacia la clase según n. "Nunca listado" es un dato faltante, no un cero.
5. **Upgrade destructivo:** costo esperado `(P_base + costo) / p`, en orden topológico. Los ciclos se resuelven con punto fijo amortiguado.
6. **Complementos y sustitutos:**
   - sustitutos → mínimo entre rutas y clases compartidas;
   - complementos (cartas + gear con slots, combos) → v2 (ver sección 9).
7. **Banda o distribución:** p10/p50/p90 en log-normal. Lo multimodal se resuelve separando variantes.
8. **Validar sin ground truth:** holdout con cobertura, monotonía, invariantes, estrés y diff entre corridas.
9. **División del trabajo:** ver sección 7. El LLM clasifica y audita, nunca fija precios.
10. **Prioridad con 2–5 USD:** primero ingesta + ontología + modelo; el LLM solo para etiquetar clases y revisar outliers.

---

## 9. Lo que queda explícitamente sin resolver en la v1

- Valor de combos y sets.
- Precios por nivel de refine.
- Random options y enchants.
- Cambios del meta.
- El nivel absoluto real de la economía de OzRo.

Para lo último, la solución es usar los logs de vending propios después del lanzamiento como una fuente más en el mismo modelo. Así el ancla externa pierde peso sola.

---

## 10. Orden de trabajo

1. Ingesta y tests.
2. Ontología.
3. Horas por ruta.
4. Regresión y posterior.
5. Rutas compuestas.
6. Validación.
7. LLM.