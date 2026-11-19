**Sí: el costo esperado de adquisición es la primitiva correcta.** El flujo de spawn es un proxy incompleto y a menudo engañoso. Lo que realmente determina el precio de equilibrio de largo plazo en una economía de juego es cuánto cuesta (en tiempo + zeny + riesgo + material consumido) poner una unidad adicional en el mercado.

### 1. Costo esperado de adquisición como primitiva

La pregunta correcta es:

> ¿Cuál es el costo esperado (en zeny equivalentes) de obtener una unidad neta de este item por la ruta más barata disponible?

Componentes que deben entrar en esa función de costo:

- **Time gates** (1 spawn/hora, 1/11h, cooldowns de instancia).
- **Probabilidad efectiva** (drop rate × rates del servidor × chance de éxito del craft/enchant).
- **Consumo destructivo** (el caso Pantie[1] es el ejemplo perfecto: 5% de éxito + se consume el item base → multiplicador ~20× sobre el costo del base + materiales + zeny).
- **Costo de oportunidad del tiempo** (zeny/hora del jugador promedio o del bot promedio en ese mapa).
- **Costo de entrada** (instancias, quests, tickets, materiales previos).
- **Riesgo** (muerte, PvP, mapa peligroso) — se puede modelar como un multiplicador o como un costo de reparación/seguro implícito.

El problema de que la economía del servidor sea desconocida se resuelve con un **parámetro de calibración global** (zeny_por_hora_efectivo) que se ajusta una sola vez para que los items con buena evidencia histórica caigan aproximadamente donde deben. No hace falta conocer la economía real; hace falta que el ranking de costos relativos sea correcto y que la escala global sea plausible.

### 2. Items sin mercado y sin ruta (legacy / event / removed)

**“Sin precio” es una salida válida y deseable.**

Categorías recomendadas:

- `active_market` → tiene evidencia de ventas + ruta de adquisición.
- `thin_market` → pocas ventas o solo referencia externa ruidosa → banda ancha o solo “referencia histórica”.
- `no_market` / `legacy` / `event_only` / `unobtainable` → no se emite precio de mercado. Se puede emitir un “costo de adquisición estimado si existiera ruta” solo para auditoría, pero no se publica como precio de mercado.

Forzar un número cuando no hay ni oferta ni demanda observada es inventar.

### 3. Combinar dos fuentes históricas con desacuerdos de 20×

Reglas prácticas:

- Exigir un mínimo de observaciones (ej. ≥ 15–20 ventas combinadas) para usar como ancla fuerte.
- Usar mediana geométrica o promedio logarítmico ponderado por número de ventas y por “confianza de la fuente”.
- Detectar y marcar outliers (ratio > 5–8× entre fuentes) como `inconsistent_reference`.
- Nunca dejar que 2 ventas de una sola fuente definan un punto de “medium confidence”. Con 0–2 ventas el resultado debe ser banda muy ancha o “sin precio de mercado”.

La referencia histórica debe tratarse como **evidencia bayesiana**, no como punto fijo.

### 4. Demanda con datos censurados y muestras pequeñas

Con 0–2 ventas no se puede estimar demanda de forma confiable. Opciones:

- Usar un prior de demanda por clase de item (tipo × rareza × utilidad) y dejar que la evidencia actualice muy poco.
- Modelar la demanda como residual solo cuando hay volumen suficiente.
- Para el resto, dejar que el precio sea dominado por el costo de adquisición + un factor de utilidad/rareza percibida.

### 5. Upgrades destructivos (caso Pantie[1] / socket enchant)

Es un problema de punto fijo, pero se puede resolver de forma iterativa o con orden topológico:

1. Preciar primero todos los items base (sin dependencias de craft/enchant).
2. Luego los crafts/enchants que solo consumen items ya preciados.
3. Iterar un número fijo de veces (2–4) hasta convergencia o hasta un umbral de cambio.

Para el caso 5% de éxito + consumo del item:

\[
\text{costo esperado} = \frac{\text{precio base} + \text{materiales} + \text{zeny}}{0.05}
\]

Ese costo esperado se convierte en el piso del precio del item upgeado (más un margen de utilidad/riesgo).

### 6. Complementarios y sustitutos

Esto es más difícil y probablemente debe quedarse en una capa posterior o semi-manual/LLM auditada:

- Cartas del mismo slot / mismo set.
- Gear con y sin slots.
- Refines.
- Cajas y sus contenidos esperados.

Se puede empezar con reglas simples de monotonía (“el item con slot nunca puede valer menos que el mismo sin slot + costo esperado del enchant”) y dejar las interacciones más finas para una pasada posterior.

### 7. Forma de la salida

Preferible una distribución (o al menos p10 / p50 / p90) que un punto medio con banda simétrica. La incertidumbre es casi siempre asimétrica y a veces multimodal (especialmente cuando hay referencias históricas conflictivas o rutas muy distintas).

### 8. Validación sin ground truth

Invariantes y tests de monotonía que sí se pueden exigir:

- Dentro de la misma clase de utilidad, una ruta estrictamente más cara/rara no puede producir precio medio más bajo (salvo evidencia fuerte de demanda que lo justifique).
- Items con supply real = 0 y sin referencia histórica no reciben precio de mercado activo.
- Ningún item con evidencia histórica decente queda excluido por un booleano de parsing.
- El ranking de cartas MVP / mini-boss / normal debe respetar grosso modo la dificultad + rareza de spawn.
- Tests de estrés: subir/bajar rates globales y ver que los precios se mueven en la dirección esperada y con magnitudes razonables.

### 9–10. División fórmula / manual / LLM y priorización con presupuesto 2–5 USD

**Orden recomendado de ataque:**

1. **Arreglar la ingesta de datos** (el bug de `mob_db.yml` es crítico y barato). Sin datos correctos de HP, spawns y drops, cualquier modelo es teatro.
2. **Separar los ejes ontológicos** (Adquisición / Transferencia / Mercado) en lugar de booleanos colapsados. Esto elimina de raíz muchos de los síntomas que mostraron.
3. **Construir un grafo de rutas de adquisición** con costo esperado (incluyendo time gates y probabilidad destructiva).
4. **Usar la evidencia histórica solo como ancla bayesiana** con mínimos de muestra y detección de inconsistencia.
5. **Emitir “sin precio”** cuando no haya ni ruta ni evidencia decente.
6. Una sola pasada de LLM (si se usa) solo para:
   - clasificar items legacy/event/unknown,
   - sugerir factores de utilidad/demanda residual en clases difíciles,
   - proponer overrides manuales versionados.
   Nunca como generador opaco de precios.

Lo que dejaría explícitamente sin resolver en la primera versión seria: modelado fino de complementarios/sustitutos y estimación sofisticada de demanda con datos muy censurados. Esas capas se pueden añadir después una vez que el costo de adquisición + ontología limpia ya den un ranking decente.

---

**Resumen de la hipótesis central del brief (que comparto):**

El error de fondo no está en los valores de los booleanos ni en los exponentes de los multiplicadores. Está en haber formulado el problema con unidades incompatibles y con booleanos que colapsan propiedades ortogonales. Una vez que se cambia la primitiva a **costo esperado de adquisición por ruta** y se separan Adquisición / Transferencia / Estado de mercado, la mayoría de los síntomas grotescos (Menblatt vs Frilldora, Monster Coin, GTB/Ifrit, Pantie, oferta cero tratada como neutra, etc.) se vuelven mucho más tratables o desaparecen.

Si quieren, en un siguiente mensaje puedo proponer una estructura de datos concreta (campos mínimos por item) y un esbozo del pipeline de pricing que respete las restricciones de trazabilidad y presupuesto.