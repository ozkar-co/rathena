# Revisión externa — Mercado de OzRo

He leído el brief completo. Antes de responder las preguntas, permíteme ordenar el diagnóstico porque creo que hay una jerarquía distinta a la que sugiere el documento, y eso cambia qué responder primero.

## 1. Diagnóstico: el brief acierta, pero el orden de prioridades está invertido

El documento presenta P1–P6 como problemas paralelos. No lo son. Hay una **cadena causal**:

```
Ingesta rota (P5-bug, §5)
   → cobertura de fuentes mal medida
      → "obtainable" se vuelve un proxy de "parseado" (P6)
         → colapso de ejes ortogonales en booleanos (P6)
            → imposibilidad de modelar costo de adquisición (P2)
               → base de precio sin unidad común (P1)
                  → prior de tipo como parche (P3)
                     → evidencia histórica como punto (P4)
                        → multiplicadores topados que no pueden corregir 10x–100x
```

Consecuencia práctica: **arreglar P1 (la fórmula) sin arreglar §5 y P6 reproduce el mismo resultado con otra aritmética.** El caso GTB/Ifrit no es un fallo de fórmula; es que el dato de HP/spawn no existe en el dataset. Ninguna primitiva nueva lo va a recuperar. El brief lo intuye ("arreglar la fórmula sin arreglar la procedencia no va a dar confianza") pero lo trata como nota al pie. Debería ser el **paso 0**.

## 2. Sobre la pregunta central: ¿es el costo esperado de adquisición la primitiva correcta?

**Sí, pero con una corrección importante: no es una primitiva, es una *familia* de primitivas por ruta, y su salida natural no es un escalar sino una distribución.**

### Por qué el costo esperado es correcto
- Es la única magnitud conmensurable entre rutas heterogéneas (drop, craft, quest, box, cash, event). Todo se puede expresar en `zeny + tiempo·(zeny/hora) + riesgo·(valor del item perdido)`.
- Es monótona con rareza *por construcción*: una ruta más rara/cara produce mayor costo esperado, salvo que la demanda lo compense. Eso satisface directamente el criterio de éxito #2.
- Resuelve los tres casos patológicos de un golpe: Pantie[1] (5% destructivo → costo esperado ≈ 20x base), GTB (1/hora → costo de tiempo domina), Ifrit (1/11h → aún más).

### La corrección: costo esperado *condicionado a ruta*, no agregado
No calcules un único `acquisition_cost` por item. Calcula `cost(item, route)` para cada ruta viable, y expón **la ruta mínima como cota inferior y la distribución de rutas como banda**. Un item con dos rutas (drop 0.1% + craft 5% destructivo) tiene dos costos y el precio de mercado no es el promedio: es el mínimo de las rutas *efectivamente accesibles al jugador marginal*. Cuál es "el jugador marginal" es una decisión de modelado que debe quedar explícita y versionada.

### Cómo estimar zeny/hora sin conocer la economía
No necesitas conocer la economía para estimar costo de oportunidad. Necesitas **una unidad de cuenta interna**. Tres opciones, en orden de preferencia:

1. **Zenny/hora implícito del propio dataset**: usa los items con referencia histórica *y* ruta conocida para calibrar. Si un item con costo esperado `C` tiene precio de mercado `P`, entonces `P ≈ C + margen`. Con ~5,847 items de referencia puedes regresar `zeny/hora` como un parámetro global (o por bracket de nivel) que minimice error. Es un parámetro, no un supuesto.
2. **Ancla externa declarada**: fija `zeny/hora` explícitamente (p.ej. "un jugador nivel 150 farmea X zeny/hora en maps canónicos") y trátalo como supuesto versionado. Auditable, reproducible, y si cambia, se re-corre.
3. **Sin unidad de tiempo**: si no quieres comprometerte, colapsa todo a "costo en zeny de materiales + costo de oportunidad relativo", y deja el tiempo como *factor de escasez ordinal* (1 spawn/hora >> 1 spawn/10min) sin convertirlo a zeny. Pierdes resolución pero ganas honestidad.

Recomiendo (1) con (2) como fallback declarado. El brief ya tiene el material: los 5,847 items de referencia son tu conjunto de calibración.

## 3. Sobre "sin precio" como salida válida

**Sí, y el brief debería tratarlo como ciudadano de primera clase, no como excepción.**

Hoy el modelo tiene un "acantilado" (5,847 market vs 23,209 synthetic) que es en realidad un **colapso de tres estados en dos**. La salida correcta tiene al menos cuatro estados:

| Estado | Condición | Salida |
|---|---|---|
| `priced` | ruta conocida + evidencia de demanda suficiente | p10/p50/p90 |
| `banded` | ruta conocida, muestra chica (0–2 ventas) | banda ancha explícita |
| `reference_only` | sin ruta parseada, con referencia histórica | precio = referencia, marcado como no derivado |
| `unpriced` | sin ruta, sin referencia, o legacy/event | **sin precio**, con razón (`legacy`, `event`, `parse_gap`, `no_source`) |

Esto resuelve directamente:
- El criterio de éxito #3 (muestra chica → banda ancha o sin precio).
- El caso "unobtainable con referencia" (P6): pasa a `reference_only`, no a `marketEligible` silencioso.
- La honestidad sobre GTB/Ifrit: si el spawn real no está en el dataset, el estado es `unpriced` con razón `parse_gap`, no 500k inventado.

El "sin precio" no es un fracaso del modelo; es el modelo diciendo la verdad. Un MarketSimulator puede manejar `None`; lo que no puede manejar es un 500k falso que se propaga a la economía.

## 4. Sobre combinar dos servidores con desacuerdos de 20x

El brief ya identificó el problema (898 items con >2x de desacuerdo, 2 ventas = "medium confidence"). La respuesta corta: **no combines en un punto; combina en una distribución y propaga la incertidumbre.**

Orden de preferencia:

1. **Mediana geométrica robusta con rechazo por inconsistencia**: para cada item, si `|log(P_latam) − log(P_atlantis)| > log(umbral)` (p.ej. umbral 3x), no promedies: marca `source_disagreement` y ensancha la banda o degrada a `banded`. Nunca elijas una fuente en silencio (el bug de Menblatt: LATAM 1.5M vs Atlantis 30.2M, el modelo eligió LATAM).
2. **Bayes jerárquico ligero**: prior por (tipo, rareza, ruta) calibrado con los items de bajo desacuerdo; likelihood por fuente con varianza estimada de su desacuerdo histórico. La salida es una posterior, no un punto. Con 2–5 USD de LLM no necesitas MCMC: una aproximación laplace o un modelo log-normal por clase basta.
3. **Peso por evidencia**: `n_ventas` entra como peso, no como umbral binario. 2 ventas → banda ancha; 50 ventas consistentes → banda angosta. El desacuerdo entre fuentes entra como varianza, no como selección.

Lo que **no** haría: promedio aritmético (sensible a outliers como los 650M de Ice Pick), ni "elegir la fuente con más ventas" (el bug actual), ni LLM como árbitro de precios (el brief ya lo prohíbe en §8).

## 5. Sobre demanda con datos censurados y 0–2 ventas

Tres observaciones:

- **0 ventas ≠ 0 demanda.** Es censura por debajo del umbral de observación. Modela como `P(ventas > 0 | features)` (modelo de hurdle) y `E[ventas | ventas > 0]` por separado. La demanda del item es el producto, con incertidumbre.
- **La demanda no debe entrar como multiplicador topado (±25%).** Eso es lo que impide corregir 10x. Debe entrar como **componente de la distribución de precio**, informada por la evidencia, no como ajuste post-hoc.
- **Con 0–2 ventas, la demanda es esencialmente no identificable.** La salida honesta es banda ancha + `low_confidence`, no un punto. Esto ya está en el criterio #3; el punto es hacerlo operativo en el esquema de salida, no solo en la intención.

## 6. Sobre el upgrade destructivo del 5% y la circularidad

**Sí, es un problema de punto fijo, y la forma correcta de resolverlo es por *estratificación por ruta*, no por iteración global.**

La circularidad aparece solo si intentas calcular `P(Pantie[1])` a partir de `P(Pantie)` y `P(Pantie)` a partir de `P(Pantie[1])` simultáneamente. Pero no son el mismo bien: `Pantie` y `Pantie[1]` son **sustitutos imperfectos con rutas distintas**. La ruta de `Pantie[1]` es `craft(Pantie, Elunium, 1M zeny, 5%)`, cuyo costo esperado es:

```
C(Pantie[1]) = [C(Pantie) + C(Elunium) + 1M] / 0.05
             = 20·[C(Pantie) + C(Elunium) + 1M]
```

Esto es **lineal en C(Pantie)**, no circular, siempre que `C(Pantie)` se calcule por su *propia* ruta (drop/craft) y no por su precio de mercado. La circularidad solo surge si confundes `costo de adquisición` con `precio de mercado`. Son magnitudes distintas:

- `C(item)`: costo de poner una unidad en el mercado (por ruta).
- `P(item)`: precio al que se transa (costo + margen + demanda).

La regla: **calcula `C` bottom-up por ruta (DAG, sin ciclos), y `P` top-down desde `C` + evidencia de demanda.** Si hay ciclos reales en rutas (item A se craftea con B, B con A), detectarlos y marcarlos `cyclic_route` → `unpriced` o banda máxima. No inventes un punto fijo iterativo; el punto fijo solo tiene sentido si hay un mecanismo de equilibrio económico que no tienes.

Para Pantie[1] esto da `≈ 20.2M` como pedía el brief, y para Pantie[0] da su costo por drop, y la relación entre ambos es monótona por construcción. Eso satisface el criterio #2 sin iteración.

## 7. Sobre complementarios, sustitutos, slots, refine, combos

Aquí seré directo: **es el problema de mayor riesgo de sobre-ingeniería y el de menor retorno inmediato.** Con 2–5 USD y una corrida, no lo resuelvas. Modela:

- Slots y refine como **modificadores de la ruta** (`[1]` tiene ruta de socket enchant, `+7` tiene ruta de refine con riesgo), no como items separados con precio propio. Eso ya captura el 80% del efecto (Pantie[1] ≈ 20x Pantie[0]).
- Combos y complementarios como **nota de auditoría** (`combo_with: [...]`), sin precio derivado. Un LLM puede poblarlos en una pasada única y barata, marcados como `llm_annotated`, sin que afecten el precio.
- Cajas/grupos: sí modelar (ya está en §5 del brief), porque son rutas de adquisición con odds conocidas. Eso es costo esperado puro.

Lo que **no** haría: un modelo de equilibrio general de sustitutos. No hay datos para calibrarlo y el brief explícitamente no quiere pureza determinista a costa de correctness.

## 8. Sobre la salida: mid con banda simétrica vs distribución p10/p50/p90

**Distribución asimétrica, no banda simétrica.** Razones:

- Los precios de items son log-normales por construcción (producto de factores positivos). Una banda simétrica en zeny subestima la cola alta (Ice Pick: 2 ventas a 650M vs media 258M) y sobreestima la baja.
- La incertidumbre es multimodal por ruta (drop vs craft vs event pueden dar precios distintos). Un p10/p50/p90 por ruta, agregado por mezcla, captura eso; una banda simétrica no.
- El MarketSimulator necesita p10/p50/p90 para simular colas de compra/venta; un mid simétrico le da una sola curva.

Formato recomendado por item:
```json
{
  "item_id": 1234,
  "state": "priced|banded|reference_only|unpriced",
  "p10": ..., "p50": ..., "p90": ...,
  "route": "drop|craft|quest|box|event|legacy|none",
  "cost_expected": ..., "cost_breakdown": {...},
  "demand_evidence": {"n_sales": ..., "sources": [...], "disagreement": ...},
  "confidence": "high|medium|low|none",
  "reason": "parse_gap|source_disagreement|small_sample|cyclic_route|...",
  "provenance": {"inputs_hash": ..., "seed": ..., "version": ...}
}
```

`p50` solo existe si `state ∈ {priced, banded, reference_only}`. `unpriced` no tiene p50, y eso es correcto.

## 9. Sobre validar sin ground truth

Invariantes y tests, en orden de valor:

1. **Monotonía por ruta** (el más importante): dentro de una clase, si `cost_expected(A) > cost_expected(B)` y la demanda es comparable, entonces `p50(A) ≥ p50(B)`. Test automático sobre todos los pares de la misma clase. Falla → bug.
2. **Consistencia de estados**: `unpriced` no tiene precio; `reference_only` tiene precio = referencia exacta; `banded` tiene `p90/p10 > umbral`. Test de esquema.
3. **No-regresión de casos conocidos**: GTB, Ifrit, Pantie[1], Monster Coin, Menblatt/Frilldora, Ice Pick. No como overfitting (el brief lo prohíbe), sino como **smoke tests**: si el pipeline corre y estos seis no se mueven a un estado absurdo, el pipeline no está roto. Los valores exactos no se fijan.
4. **Estrés de ingesta**: correr el loader contra `mob_db.yml` con las 67 filas y verificar que no borra HP/drops de los 66 mobs (el bug de §5). Test de regresión de datos, no de fórmula.
5. **Auditoría de procedencia**: para una muestra aleatoria de 100 items, verificar que `provenance.inputs_hash` reproduce el precio al re-correr. Test de reproducibilidad (criterio #5).
6. **Sensibilidad a supuestos**: correr con `zeny/hora` en ±50% y verificar que el ranking de precios (no los valores) es estable. Si el ranking se rompe, el modelo depende de un supuesto no identificable.

Lo que **no** haría: comparar contra los dos servidores externos como ground truth. El brief ya lo dice: son referencia, no verdad.

## 10. División fórmula / manual / LLM

| Componente | Motor | Justificación |
|---|---|---|
| Ingesta y merge de `mob_db`, `item_db`, spawns, recetas | Determinista | Auditable, testeable, es donde está el bug de §5 |
| Costo esperado por ruta (`C`) | Determinista | DAG, sin ciclos, reproducible desde inputs |
| Calibración de `zeny/hora` y priors por clase | Determinista (regresión) | Parámetros versionados, no supuestos ocultos |
| Demanda (hurdle + banda) | Determinista | Datos censurados, no requiere LLM |
| Combinación de fuentes históricas | Determinista (robusta/Bayes ligero) | El desacuerdo es varianza, no selección |
| `p10/p50/p90` y estado | Determinista | Regla explícita |
| Overrides manuales | Manual, versionado | El brief ya lo exige (§6) |
| Anotación de combos, legacy/event, sin fuente | LLM, una pasada, marcado `llm_annotated` | Barato, no afecta precio, población de metadatos |
| Redacción de `reason` y notas de auditoría | LLM, opcional | Cosmético, auditable |

**Regla dura: el LLM nunca produce un número que entre a `p50`.** Solo produce etiquetas, razones y anotaciones. Eso respeta §8 y el criterio de presupuesto.

## 11. Con 2–5 USD y una corrida: qué haría primero

Orden estricto, porque el brief pide "qué dejarían explícitamente sin resolver":

1. **Arreglar la ingesta** (§5): merge de `mob_db.yml` en vez de overwrite; recuperar GTB/Ifrit reales; clasificar `alb_ship`; re-correr el dataset. **Sin esto, nada más importa.** Costo: horas de ingeniería, $0 de LLM.
2. **Reformular la ontología** (P6): separar `Adquisición` / `Transferencia` / `Mercado` como ejes, no booleanos. Implementar `NoSell ≠ NoTrade`, canales de liquidez (`NoStorage`, `NoMail`), y la categoría `legacy/event/removed`. Costo: diseño + código, $0 de LLM.
3. **Implementar costo esperado por ruta** (P2) como DAG determinista, con `zeny/hora` calibrado por regresión sobre los 5,847 items de referencia. Costo: código, $0 de LLM.
4. **Cambiar la salida a estados + p10/p50/p90** (§3, §8) con `provenance` obligatoria. Costo: código, $0 de LLM.
5. **Correr la pasada LLM única** solo para: anotar combos, clasificar `legacy/event/removed` donde la ingesta no alcanza, y redactar `reason`. Presupuesto: $2–5. Marcado `llm_annotated`.
6. **Correr los invariantes** (§9): monotonía, consistencia de estados, no-regresión de los seis casos, estrés de ingesta, reproducibilidad.

**Lo que dejaría explícitamente sin resolver:**
- Equilibrio general de sustitutos/complementarios (demasiado caro, sin datos).
- Punto fijo iterativo para rutas cíclicas (detectar y marcar `unpriced`; no inventar).
- Demanda con 0–2 ventas más allá de banda ancha (no identificable).
- Validación contra ground truth (no existe; usar invariantes).
- Precio de items `legacy/event` sin ruta (salida: `unpriced` con razón; no inventar).
- Refine/slots como items separados (modelar como modificador de ruta, no como precio propio).

## 12. Lo que cambiaría del brief mismo

Tres observaciones meta, porque el brief pide revisión externa y no solo respuestas:

- **El brief subestima §5 (ingesta) y P6 (ontología) frente a P1 (fórmula).** La cadena causal va de datos a ontología a fórmula, no al revés. Reordenar las secciones ayudaría a que el revisor externo no gaste esfuerzo en la fórmula antes de arreglar la base.
- **El brief trata "sin precio" como taboo implícito.** En §6 dice "¿'Sin precio' es una salida válida?" como pregunta, pero el criterio #3 ya lo implica. Elevarlo a decisión de diseño explícita (estado `unpriced`) simplifica todo lo demás.
- **El brief pide "no overfitting a los seis casos" pero los seis casos son el mejor smoke test que tienen.** La distinción es: no fijar los *valores* de los seis, pero sí usarlos como *no-regresión de estado* (GTB no puede ser `priced` con p50=500k; Pantie[1] no puede ser `priced` con p50 < 20x Pantie[0]). Eso es invariante, no overfitting.

## Resumen ejecutivo

1. **La primitiva correcta es costo esperado de adquisición por ruta, no agregado.** Calibra `zeny/hora` por regresión sobre los 5,847 items de referencia; declara el supuesto y versiónalo.
2. **"Sin precio" es una salida válida y necesaria.** Cuatro estados (`priced`, `banded`, `reference_only`, `unpriced`) con razón explícita.
3. **Combina fuentes históricas en distribución, no en punto.** Mediana geométrica robusta + rechazo por desacuerdo + peso por evidencia. Nunca elijas fuente en silencio.
4. **Demanda como hurdle con banda, no como multiplicador topado.** 0–2 ventas → banda ancha, no punto.
5. **Upgrade destructivo es lineal en el costo del base, no circular**, si separas `C` (bottom-up por ruta) de `P` (top-down con demanda). Ciclos reales → `unpriced`, no punto fijo iterativo.
6. **Salida p10/p50/p90 asimétrica con `provenance` obligatoria**, no mid simétrico.
7. **Valida con invariantes** (monotonía, consistencia de estados, no-regresión de estado de los seis casos, estrés de ingesta, reproducibilidad), no con ground truth.
8. **LLM solo para metadatos y razones, nunca para números que entren a `p50`.** Presupuesto $2–5 alcanza para una pasada de anotación.
9. **Orden de ejecución: ingesta → ontología → costo esperado → estados/provenance → LLM → invariantes.** Lo demás se deja explícitamente sin resolver.
10. **El brief acierta en el diagnóstico pero invierte la prioridad.** Datos y ontología antes que fórmula. Los seis casos son smoke tests de estado, no de valor.