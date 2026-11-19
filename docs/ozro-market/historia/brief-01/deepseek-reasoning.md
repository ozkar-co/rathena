# Respuesta al brief — Mercado de OzRo

## Diagnóstico central

El modelo no tiene un problema de calibración de multiplicadores; tiene un problema de **especificación econométrica**. Está estimando una sola ecuación de precio con variables que no son reducibles a una escala común (flujo de spawn, HP, residual de ventas, percentil de tipo) y aplicando clamps de ±15%, ±25%, 0.5–2.0 sobre una base que puede estar equivocada por 10x–100x. Ningún clamp corrige un error de base de ese tamaño: los clamps garantizan que el error se propague, no que se corrija. Por eso el caso Ice Pick[1] “funciona” por accidente (2 ventas ruidosas a 650M) y Menblatt vs Frilldora falla por diseño (la referencia histórica manda, no la fórmula).

El “acantilado” (5,847 con punto histórico vs 23,209 con prior de tipo) es la manifestación estadística de un **modelo de dos regímenes sin puente**: un régimen con evidencia ruidosa y otro con un prior casi no informativo (percentil 40 de un tipo que mezcla Jellopy con Etel Dust). La rareza no puede cruzar el acantilado porque la fórmula no tiene un mecanismo continuo basado en costo.

La salida no es refinar los multiplicadores. Es **cambiar la primitiva**: pasar de “flujo de spawn + residual + percentil” a **costo esperado de adquisición** como variable latente, con la demanda modulando el markup sobre ese costo. Es el modelo estándar de organización industrial (COGS + markup) y es el único que puede dar cuenta de GTB, Ifrit, Pantie[1] e Ice Pick[1] con la misma regla.

---

## La primitiva correcta

Para cada item *i*, el precio de equilibrio en un mercado competitivo con libre entrada satisface:

**p_i = max( A_i(p), p_i^demanda )**

donde **A_i(p)** es el costo esperado de poner una unidad en el mercado (costo de materiales + zeny + costo de oportunidad del tiempo / tasa de obtención por hora), y **p_i^demanda** es el precio que vacía el mercado dada la demanda latente. Si la oferta es elástica (fácil de farmear), p_i → A_i por la condición de cero beneficio. Si es inelástica (time gates, drop 0.01%, 1 spawn/hora), p_i puede superar A_i sustancialmente: la renta diferencial va al que ya tiene el item, no al que lo produce. Esto es exactamente el caso GTB/Ifrit, y el modelo actual no puede verlo porque no modela ni A_i ni la inelasticidad.

**A_i** se construye como:
- **Farmed:** A_i = (tiempo de kill × zeny/hora + riesgo) / (drop efectivo × unidades por kill) + costo de acceso al mapa.
- **Crafted:** A_i = (Σ costo_inputs + zeny_costo) / success_rate + costo_oportunidad_tiempo (para destructivos, como Pantie[1]).
- **Quested:** A_i = costo de materiales + zeny + valor del tiempo de la quest.
- **Group/box:** A_i = costo del grupo / probabilidad de obtención.
- **Event/legacy/unknown:** A_i = no identificado → salida “unpriced” o banda ancha.

---

## Respuestas a las 10 preguntas

### 1. ¿Es el costo esperado de adquisición la primitiva correcta?

Sí, pero el par correcto es **(A_i, evidencia de demanda)**, no A_i solo. En un mercado competitivo p_i ≈ A_i solo si la oferta es elástica; si es inelástica, p_i > A_i y la brecha es información (rareza, time gate), no error.

**Cómo estimar zeny/hora sin conocer la economía:** tres métodos, en orden de preferencia.
1. **Revelación por trading:** para items a la vez farmeables y tradeados, la razón precio/flujo observado da un estimador de zeny/hora. Mediana robusta de esa razón.
2. **Numeraire auto-consistente:** expresar todo en unidades de un bien líquido (Elunium, White Potion, una carta común) y fijar ese bien exógenamente. El resto de precios se derivan relativos.
3. **Punto fijo con damping** (ver pregunta 5).

El punto fijo es el método formalmente correcto; los otros dos son inicializaciones. Sin ground truth, el mejor resultado es un **equilibrio auto-consistente**, y eso hay que declararlo explícitamente.

### 2. Items sin mercado y sin ruta (legacy/event)

**“Sin precio” es una salida válida y debe ser explícita.** Un item sin ruta de oferta y sin evidencia de demanda tiene precio indeterminado; cualquier número es fabricación. Salida de tres niveles:

- **Priced** (alta confianza): ruta + evidencia.
- **Band only** (baja confianza): ruta O evidencia, no ambas.
- **Unpriced** (explícito, con razón: “no route”, “no evidence”, “legacy”, “event-only”).

Esto cumple el criterio de éxito “ningún item con ventas históricas queda fuera del mercado por un booleano”: si hay ventas, hay evidencia, y debe entrar como banda. Si no hay ni ruta ni evidencia, el MarketSimulator debe tratar el item como no comerciable o precio manual, no como precio inventado.

### 3. Dos servidores históricos con desacuerdos de 20x

**No promediar.** Promediar 1.5M y 30.2M da 15.85M, que no es el precio de ninguno de los dos y probablemente no es el precio de nada. La estrategia correcta es **modelo jerárquico bayesiano en log-espacio**:

```
log p_i ~ Normal(μ_i, σ_i)
μ_i     ~ prior de arquetipo de adquisición (no de "tipo")
σ_i     = f(desacuerdo entre fuentes, número de ventas)
```

Propiedades:
- El desacuerdo **es información, no ruido**: 20x implica σ_i grande, es decir, banda ancha. La salida debe reflejar esa incertidumbre, no ocultarla.
- **Mediana geométrica robusta** para el punto central, con rechazo de fuentes con < N ventas y desacuerdo > k×.
- **No fijar una fuente por item** (el sesgo de selección silencioso en Menblatt es el ejemplo). Modelar la calidad de la fuente como parámetro; dejar que el modelo aprenda qué fuente es más fiable por clase.
- Si ambas fuentes tienen muestra chica (<5 ventas), no hay punto: hay banda ancha o unpriced.

La elección silenciosa de LATAM para Menblatt es exactamente el tipo de decisión que un bayesiano jerárquico evita: no se elige la fuente que produce el número deseado.

### 4. Demanda con datos censurados y 0–2 ventas

Es un problema de **datos censurados** (Tobit / conteo inflado en cero). La observación es `ventas = min(D, S)`, donde D es demanda latente y S es oferta disponible. Cero ventas no significa cero demanda; significa que D o S estaban por debajo del umbral de detección.

Modelo recomendado:
- **Poisson / Binomial Negativa inflada en cero** condicionada en S (oferta observada).
- **Empirical Bayes / shrinkage** hacia el prior de arquetipo, con varianza que refleje el tamaño de muestra. Esto es lo que hace un modelo jerárquico; no es un parche.
- **Salida:** para n < 5 ventas, banda ancha (P10–P90 amplio) o unpriced; nunca un punto de “media confianza”.

La distinción entre “no se vendió porque no había” y “no se vendió porque no se demandó” es crucial y el modelo actual no la hace.

### 5. Upgrade destructivo del 5% y circularidad

Sí, es un **problema de punto fijo**, y la solución estándar es:

1. **Orden topológico del grafo de craft.** Si es un DAG (la mayoría lo son), se precian primero los items base y luego los derivados en orden de dependencia. No hay circularidad.
2. **Ciclos** (item que se usa para craftear otro que se usa para craftear el primero, o zeny/hora que depende del output): **iteración de punto fijo con damping**: p^(t+1) = (1−α)p^(t) + α·F(p^(t)), α ≈ 0.3–0.5, hasta que ||p^(t+1) − p^(t)|| < ε. La condición de convergencia es que el radio espectral del Jacobiano de F sea < 1/(1−α); con damping fuerte se cumple en la práctica.
3. **Costo esperado de craft destructivo:** A_i = (Σ costo_inputs + zeny_costo) / success_rate + costo_oportunidad_tiempo. Para Pantie[1]: (P_pantie + 1M + P_elunium)/0.05 ≈ 20.2M, consistente con el brief.
4. **Anti-circularidad económica:** el zeny/hora se estima una vez (o iterativamente con damping fuerte), no se recalcula por item. Así se rompe el ciclo precio → zeny/hora → precio.

La clave: **el punto fijo es sobre el vector de precios, no sobre cada precio aislado.** Es el modelo de Leontief / equilibrio general, y converge bajo damping.

### 6. Bienes complementarios y sustitutos

**Modelo hedónico** es la respuesta estándar de organización industrial:

```
log p_i = β·X_i + γ·(slot) + δ·(refine) + ε_i
```

donde X_i son atributos (tipo, ATK, DEF, nivel requerido, etc.), con coeficientes por clase.
- **Complementos** (carta + slot, Elunium + refine): el valor del slot es una función del precio de las cartas compatibles. Modelar como **valor del slot = cuantil alto de precios de cartas compatibles** (lo que hace el mercado real: un slot vale lo que vale la mejor carta que puedes meter).
- **Sustitutos** (dos cartas con efecto similar): modelo de participación de demanda (logit / AIDS) o elasticidad cruzada estimada de los datos históricos.

**Para el primer pase: ignorar complementos/sustitutos y documentarlo como limitación conocida.** El impacto es de segundo orden comparado con los errores de 10x–100x de P1–P3. Atacarlos primero es sobre-ingeniería.

### 7. Mid con banda vs distribución

**Distribución, sin duda.** Salida: **log-normal (o mezcla) por item**, reportada como P10 / P50 / P90.
- La incertidumbre es **asimétrica en nivel** (1M o 10M, nunca −9M) y **simétrica en log-espacio**. Una banda simétrica en nivel (mid ± x%) es estadísticamente incorrecta.
- **Multimodalidad genuina:** un item con rutas drop OR craft OR quest puede tener precios genuinamente distintos por ruta. Modelar como **mezcla de log-normales**, una por ruta, ponderadas por probabilidad de ruta.
- La banda debe ser **función de la evidencia**: ancha para baja evidencia, estrecha para alta. Un bayesiano jerárquico lo hace automáticamente.
- El MarketSimulator consume P10/P50/P90; el NPC tasador usa P50 con colchón.

Un mid puntual sin banda es **falsa precisión**, exactamente el problema que el brief identifica en Ice Pick[1].

### 8. Validación sin ground truth

Sin ground truth, la validación es por **invariantes + backtesting cruzado + stress tests**.

**Invariantes (tests automáticos):**
- **Monotonía:** dentro de clase, ruta más rara/cara ⇒ precio ≥. Test exhaustivo.
- **No-arbitraje:** NPC buy ≤ P50 ≤ techo; si no, hay arbitraje.
- **Craft:** P50(crafted) ≥ (Σ costo_inputs)/success_rate.
- **Slot:** P50(item[1]) ≥ P50(item[0]).
- **Refine:** P50(+1) ≥ P50(+0).
- No-negatividad y finitud.

**Backtesting cruzado:**
- Usar precios de LATAM para predecir Atlantis y viceversa; medir error en items con alta confianza en ambos. Da un **error de generalización** estimado.
- Cross-validation por item: hold-out aleatorio de items con evidencia, predecir con el resto.

**Stress tests:**
- Perturbar drop rate, spawn, HP ±50%; medir sensibilidad del precio. Items con sensibilidad > umbral se marcan como “frágiles”.
- Perturbar zeny/hora ±50%; verificar que el ranking es estable.

**Lo que no se puede validar:** el nivel absoluto de precios. Solo la estructura (ranking, ratios, monotonía). Esto debe documentarse explícitamente.

### 9. División fórmula / manual / LLM

**Determinista (fórmula):** cálculo de A_i (dado rutas y costos), punto fijo y convergencia, monotonía y no-arbitraje, precio NPC desde config, checks de invariantes.

**LLM (una pasada, auditada, $2–5):**
- **Clasificación ontológica** de ~18k items en arquetipos de adquisición (farmed / crafted / quested / event / legacy / unknown) desde descripciones, scripts y metadata. Esto es el trabajo de P6: separar los ejes, no colapsarlos en booleanos. Es la inversión de mayor retorno del brief.
- **Parseo de recetas/quests** desde texto (socket_enchant2.txt, quests, grupos).
- **Sanity check** de outliers: cola de revisión humana, no decisión automática.
- **Documentación** de overrides.

**Manual:** overrides explícitos, versionados, con justificación (los 5 actuales, más los que surjan); calibración de parámetros globales (zeny/hora, numeraire, priors de clase).

**Nunca:** LLM emitiendo precios directamente como caja negra. Es exactamente lo que el brief prohíbe, con razón.

### 10. Qué haría primero con $2–5 y una corrida

**Prioridad en orden:**

1. **Arreglar el bug de mob_db** (P5 del brief): 67 filas, 66 pisadas por `mobs[id] = row` en vez de merge. Es el fix más barato y de mayor impacto en calidad de datos. Sin esto, 100 items (43 cartas MVP) están mal y ninguna fórmula los salva. **Costo: horas de ingeniería, $0 de LLM.**

2. **Reformular la ontología** (P6): separar adquisición / transferencia / mercado en tres ejes. LLM en una pasada (~$1–2) para clasificar los 18k items en arquetipos desde descripciones y scripts. Auditar una muestra. Elimina el “acantilado” conceptual y es prerequisito de todo lo demás.

3. **Modelo de costo de adquisición para los ~100–200 items que importan**: cartas MVP, crafts destructivos (Pantie[1]), quests caras, time gates (GTB, Ifrit). Ahí están los errores de 10x–100x. No hace falta para los 23k; hace falta hacerlo bien para los que mueven la economía.

4. **Punto fijo + bandas P10/P50/P90** con el modelo jerárquico bayesiano. Damping, convergencia, invariantes.

5. **Dejar explícitamente sin resolver** (documentar como limitaciones conocidas):
   - Demanda fina para items oscuros (0–2 ventas): unpriced o banda ancha.
   - Complementos/sustitutos (hedónico completo): segundo pase.
   - Multimodalidad de rutas: mezcla, sin calibrar finamente.
   - Nivel absoluto de precios: no validable sin ground truth; solo estructura.

**Qué NO haría:** refinar la fórmula actual (P1: unidades incompatibles), parchear item por item (overfitting a 6 casos), usar LLM para emitir precios (caja negra), buscar pureza determinista a costa de correctness.

---

## Lo que el brief acierta y lo que subestima

**Acierta:** el diagnóstico P1–P6 es correcto y bien articulado. La hipótesis de P6 (el error es formular con booleanos, no los valores) es la observación más valiosa del brief. Los criterios de éxito son sólidos.

**Subestima:**
- **La gravedad del bug de mob_db.** No es “no el problema principal”; es un **problema de procedencia** que invalida cualquier inferencia sobre los 100 items afectados (incluidas 43 cartas MVP). Debe ser P0, no P5.
- **La necesidad de un numeraire explícito.** Sin él, el punto fijo del zeny/hora no tiene solución única.
- **Que “sin precio” es una decisión de producto, no un fallo.** El MarketSimulator y el NPC tasador deben manejar `unpriced` explícitamente.

**Lo que falta en el brief:**
- Un **modelo de elasticidad** explícito. La demanda no es solo “residual de ventas”; es función del precio. Sin elasticidad, el markup sobre costo no está identificado.
- Una **política de overrides** (quién, cuándo, con qué evidencia, cómo se versiona). El brief lo menciona pero no lo especifica.
- Un **plan de convergencia** del punto fijo (criterio, damping, número de iteraciones, tolerancia).

---

**Resumen ejecutivo:** el modelo actual es un promedio ponderado de señales incompatibles con clamps que no pueden corregir errores de base. La reformulación correcta es un modelo estructural de costo de adquisición con punto fijo y un bayesiano jerárquico para las bandas. La inversión de mayor retorno no es la fórmula: es (a) arreglar la ingesta de mob_db, (b) reformular la ontología con LLM en una pasada, y (c) modelar bien el costo de adquisición de los ~100–200 items que mueven la economía. Todo lo demás es segundo orden.