Este diagnóstico es de una calidad técnica excelente: el problema central no es que la fórmula de multiplicadores esté mal calibrada, sino que **el modelo actual carece de una unidad económica común, confunde ausencia de dato con ausencia de valor o escasez, y mezcla reglas de dominio de rAthena con lógica estadística**.

A continuación te entrego una respuesta estructurada desde la economía aplicada y la estadística a cada una de las 10 preguntas del brief, manteniendo la trazabilidad, la consistencia matemática y los criterios de éxito de OzRo.

---

### 1. Costo esperado de adquisición y costo de oportunidad ($w$, zeny/hora)

**¿Es la primitiva correcta?**
Sí, como **piso económico de oferta de largo plazo** (o *reserva de oferta*), no como precio de equilibrio único. En una economía con *crafting*, *farming*, *time gates* y comercio entre jugadores:

* Si un ítem es comerciable y replicable/farmeable sin restricciones absolutas, su precio de equilibrio tiende a situarse alrededor o por encima de su **costo marginal esperado de adquisición** (más una prima de riesgo/tiempo), salvo que la demanda sea insuficiente para absorber el costo mínimo de producción o que existan fuentes alternativas más baratas (sustitutos).
* En ítems de oferta estrictamente limitada por *time gates* o eventos (p. ej., cartas MVP o *time-gated spawns*), el costo de adquisición define el **esfuerzo mínimo de obtención**, pero el precio de mercado queda fuertemente determinado por la **escasez absoluta frente a la demanda** (*scarcity rent* / renta de escasez).

**¿Cómo estimar el costo de oportunidad ($w$, en zeny/hora) con economía desconocida?**
No necesitas conocer el PBI del servidor desde el día uno; puedes **anclar $w$ endógenamente (o por calibración relativa)** usando ítems de referencia observables o reglas del propio juego:

1. **Anclaje por *NPC sell / farmeo base* (piso de liquidez):** Si un jugador farmea monstruos de nivel medio/bajo que sueltan *loot* vendible a NPC o materiales básicos con referencia de mercado, puedes estimar el rendimiento bruto por hora de un personaje/setup estándar y definir $w_0$ como una tasa horaria de referencia del servidor.
2. **Estimación conjunta / punto débil con ítems de referencia:** Si tienes un conjunto pequeño de ítems con precios observables confiables (por ejemplo, ítems de *quest*/craft con costo conocido de materiales + *zeny* fijo), puedes inferir implícitamente el valor del tiempo de *farming* en los tramos donde el precio de mercado excede el costo material directo:

$$\text{Costo implícito de tiempo} \approx \max\Big(0,\; P_{\text{mercado}} - C_{\text{materiales, zeny}}\Big)$$



Dividiendo ese excedente entre las horas esperadas de *grinding* (ajustadas por probabilidad de *drop*, tiempo de *kill*/viaje y riesgo) obtienes observaciones empíricas de $w$ por nivel/zona.
3. **Estructura por estrato de dificultad / acceso:** En lugar de un único $w$ plano para todo el servidor, define $w(s)$ como función del estrato de dificultad y riesgo del mapa/instancia (por ejemplo: *field* bajo, *dungeon* medio, zona de alto riesgo / *MVP* / *time gate*), donde:

$$E[\text{Costo de obtención}] = \underbrace{\sum_k p_k \cdot C_k}_{\text{zeny/ítems directos}} + w(s) \cdot \underbrace{E[T_{\text{obtención}}]}_{\text{horas esperadas}} + \text{Prima de riesgo / } \text{time gate}$$



donde $E[T_{\text{obtención}}]$ incorpora *respawn* efectivo, competencia/acceso, *kill time* y probabilidad de éxito.

---

### 2. Ítems sin mercado y sin ruta (`legacy` / `event` / `unobtainable`)

**¿“Sin precio” es una salida válida?**
**Sí, absolutamente.** En estadística y economía aplicada, inventar un número para una observación no observada o estructuralmente ausente del mercado introduce **sesgo de imputación** y falsa precisión. Es mucho más honesto y seguro para el simulador devolver `price = null` (o `status = "no_market_no_route"`) con una explicación explícita de por qué no se valora.

Cómo separar los casos sin mezclarlos:

* **Ruta activa pero sin ventas (`active_route_no_sales`):** Tiene fuente verificada en el servidor (drop/craft/quest/NPC), pero no hay historial de ventas. Puede recibir un **precio estimado por costo/prior** con *banda muy amplia* y baja confianza (`low_confidence`), o un precio de referencia de simulación marcado como `synthetic_untraded`.
* **Sin ruta activa y sin ventas (`legacy_or_event_unverified`):** No aparece en fuentes parseadas ni tiene ventas fiables. La salida correcta es **sin precio de mercado** (`null`), indicando `reason: "no_source_and_no_sales"`. Para el NPC tasador, si no tiene `NoSell` y tiene `Sell > 0` configurado en `item_db`, se usa la regla del NPC del servidor (`Sell`), no un precio de mercado inventado.
* **Sin ruta activa pero con ventas históricas (`unparsed_source_with_sales`):** Como ocurre con ítems cuya fuente no fue parseada pero sí se comerciaron. Aquí la evidencia de mercado existe, pero debe tratarse con cautela (banda amplia si la muestra es pequeña o el desacuerdo es alto), **nunca** bloqueada por un booleano erróneo de `unobtainable`.

---

### 3. Combinar dos servidores históricos con desacuerdos de 20x

Cuando dos servidores (LATAM y Atlantis) tienen *rates*, economías o poblaciones distintas, un desacuerdo de 20x no es simple ruido gaussiano: es **heterogeneidad estructural de régimen** (o un dato atípico/poca muestra).

Un enfoque estadístico sólido y auditable:

1. **Filtro mínimo de soporte muestral:** Exigir un tamaño mínimo efectivo de ventas (por ejemplo, $n \ge N_{\min}$, o ponderar por información efectiva $\propto n$) antes de tratar una serie como evidencia fuerte. Con $n = 1\text{--}2$, el estimador debe tener varianza alta (banda ancha) o degradarse a prior.
2. **Media geométrica ponderada en log-precio (con penalización por discrepancia):** Trabajar en $\log(P)$ es natural porque los precios son positivos y multiplicativos. Si $\mu_A = \log P_A$ y $\mu_B = \log P_B$ con pesos de fiabilidad $w_A, w_B$ (basados en tamaño muestral, dispersión y calidad de fuente):

$$\hat{\mu} = \frac{w_A \mu_A + w_B \mu_B}{w_A + w_B}, \qquad \hat{P}_{\text{comb}} = \exp(\hat{\mu})$$


3. **Detección explícita de inconsistencia (regla de desacuerdo):** Medir la brecha relativa o log-diferencia $\Delta = \vert{}\mu_A - \mu_B\vert{}$ (por ejemplo, $\exp(\Delta) > 2\text{x}$ o $> 3\text{x}$ con muestras relevantes):
* Si el desacuerdo es grande y ambos tienen muestra decente, **no elijas uno en silencio**: marca `conflict_flag = true`, amplía fuertemente el intervalo de incertidumbre (`p10`–`p90`) y, si hay información de ruta/costo local en OzRo, usa esa información como ancla de desambiguación (por ejemplo, si el costo local implica un piso o techo distinto).
* Si un servidor tiene muestra muy pequeña ($n \le 2$) y el otro tiene muestra robusta, da peso dominante al de mayor soporte y marca `small_sample_warning`.


4. **Enfoque bayesiano jerárquico (conceptual):** Tratar el log-precio verdadero del ítem en OzRo como $\theta_i$, con un prior jerárquico del estrato/clase $\mu_{\text{clase}, i}$ y verosimilitudes de cada fuente histórica con varianza inflada cuando hay discrepancia entre fuentes. Así, la incertidumbre se propaga de forma transparente.

---

### 4. Demanda con datos censurados y muestras pequeñas ($0\text{--}2$ ventas)

En mercados de ítems raros o especializados, observar **0, 1 o 2 ventas** en una ventana dada es típico de un proceso de conteo de baja tasa (Poisson o Binomial Negativa) y a menudo está **censurado** (por ejemplo, falta de liquidez, *stock* agotado, precio fuera de rango o ventana corta de observación).

* **No usar residuales crudos con $n \in \{0, 1, 2\}$ como señal precisa de demanda:** Un ítem con 2 ventas donde una fue alta parece tener "alta demanda" si divides por $n=2$, cuando en realidad la varianza muestral es enorme.
* **Contracción empírica de Bayes (*Empirical Bayes shrinkage*):** Modela la tasa de demanda $\lambda_i$ (o propensión a venderse) con un prior de su grupo/estrato (por ejemplo, *tipo + rareza/tier*) y contrae las estimaciones de muestra chica hacia el prior:

$$\hat{\lambda}_i^{\text{EB}} = \frac{n_i \bar{x}_i + k \cdot \mu_{\text{grupo}}}{n_i + k}$$



donde $k$ controla qué tanta evidencia propia se exige antes de apartarse del prior del grupo.
* **Representar la incertidumbre explícitamente:** Cuando $n$ es pequeño o hay censura, el resultado debe reflejar **alta dispersión** (intervalo amplio entre `low` y `high` / `p10` y `p90`) y una etiqueta de confianza baja (`low` / `insufficient_sample`), evitando presentar una estimación puntual como si fuera segura.

---

### 5. Preciar un upgrade destructivo del 5% y evitar circularidad

Tomemos el caso de `Pantie[1]`: éxito con probabilidad $p = 0.05$ (destructivo: si falla, se pierde el ítem base), más costo fijo $C_{\text{fix}}$ (ej. 1M zeny + 1 Elunium).

**¿Cómo se calcula el costo esperado?**
Si cada intento cuesta $C_{\text{fix}}$ más el valor del ítem base $V_{\text{base}}$ y tiene probabilidad $p$ de éxito (ensayos geométricos independientes):


$$\text{Número esperado de intentos} = \frac{1}{p}$$

$$\text{Costo esperado de material + fijo} = \frac{V_{\text{base}} + C_{\text{fix}}}{p}$$


Con $p = 0.05$, $C_{\text{fix}} = 1\text{M} + \text{Elunium}$, y un valor base de ejemplo:


$$\text{Costo esperado} = 20 \cdot (V_{\text{base}} + 1\text{M} + P_{\text{Elunium}})$$


(A ello se suma, si aplica, el costo de oportunidad del tiempo/intentos y una prima de aversión al riesgo/varianza).

**¿Es un problema de punto fijo y cómo evitar circularidad?**
Sí, **puede ser un sistema acoplado / punto fijo** si el ítem base (`Pantie`) tiene precio endógeno o si varios ítems dependen entre sí en un grafo de recetas/mejoras. Para evitar circularidad y ciclos infinitos:

1. **Orden topológico (DAG) siempre que el grafo de recetas/upgrades sea acíclico:** Si `Pantie` es un ítem base y `Pantie[1]` es un derivado/upgrade, resuelve primero `Pantie` (y materiales como `Elunium`) y luego evalúa `Pantie[1]`.
2. **Si existe retroalimentación o dependencia mutua:** Resuelve por **iteración de punto fijo** (por ejemplo, Gauss-Seidel / Jacobi amortiguado) con un tope máximo de iteraciones y criterio de convergencia ($\vert{}\hat{P}^{(t+1)} - \hat{P}^{(t)}\vert{} < \epsilon$), o ancla el ítem base a su señal de mercado/costo cuando esté disponible para romper la circularidad.
3. **Regla de no-arbitraje débil (cuando aplica):** En un mercado líquido con oferta libre, el precio de equilibrio de un derivado destructivo tiende a situarse en torno a su costo esperado de producción (más margen por riesgo); si el mercado observa un precio distinto por escasez o demanda específica, se reporta la brecha entre **precio de mercado** y **costo de reposición** en vez de forzar una igualdad ciega.

---

### 6. Bienes complementarios y sustitutos (cartas, *slots*, *refine*, cajas, combos)

En economía, **complementos** y **sustitutos** no se modelan con un multiplicador suelto de "demanda", sino mediante **relaciones estructurales explícitas**:

* **Complementos (ej. Carta + equipo con *slot*, o componentes de un *combo*):**
El valor de uso de una carta depende de la disponibilidad y utilidad del equipo *slotted* compatible (y viceversa). Si nadie usa el equipo con *slot* o el *combo* está incompleto, la utilidad marginal del complemento cae; si un *combo* o *slot* es meta, la demanda conjunta sube.
* *Enfoque práctico:* Definir un **índice de compatibilidad / utilidad de slot** (cuántos ítems *slotted* útiles o *combos* activos requieren ese ítem) y ligarlo al componente de demanda/utilidad, nunca mezclándolo con el costo de extracción del ítem.


* **Sustitutos (ej. dos cartas o armas que cumplen un rol similar, o versiones *event* vs *normal*):**
Si dos ítems son sustitutos cercanos en rendimiento, el precio del sustituto más caro está acotado superiormente por el precio del sustituto más barato **ajustado por su diferencial de rendimiento/utilidad** (a menos que haya barreras de acceso o preferencias específicas).
* *Enfoque práctico:* Agrupar ítems por **rol funcional / tier de poder** (ej. armas físicas de tier X, cartas de daño elemental, etc.) y usar el precio/utilidad de los sustitutos cercanos para detectar *outliers* (ítems inflados sin ventaja real o infravalorados frente a un equivalente casi idéntico).


* **Cajas / grupos (`group/box`):**
El valor esperado de una caja es la suma ponderada por probabilidades de sus contenidos (descontando fricción/varianza si es aleatoria):

$$E[V_{\text{caja}}] = \sum_{j} \pi_j \cdot V_j$$



(siempre que los contenidos $V_j$ ya estén estimados o acotados).

---

### 7. Salida correcta: ¿punto con banda simétrica o distribución (`p10` / `p50` / `p90`)?

**La salida correcta es una distribución cuantílica (`p10`, `p50`, `p90`) —con `p50` como referencia central y `mid` derivado de forma transparente— en lugar de un punto con banda simétrica.**

¿Por qué?

1. **Los precios y la incertidumbre de mercado son asimétricos:** Un ítem muy barato tiene un piso natural cercano a cero o a su valor NPC, pero hacia arriba puede tener colas largas (escasez extrema, *meta*, *MVP card*, baja liquidez). Una banda simétrica $\pm \delta$ es irreal en precios positivos.
2. **La incertidumbre es multimodal o de régimen:** Cuando hay desacuerdo entre fuentes (ej. 20x) o mezcla de escenarios (ej. con o sin *drop* activo / *time gate*), los cuantiles `p10`, `p50` y `p90` (junto con los flags de confianza y origen) permiten al `MarketSimulator` y al NPC tasador simular escenarios realistas y medir riesgo sin colapsar todo a un falso promedio exacto.

---

### 8. Validación sin *ground truth*: invariantes, monotonía y pruebas de estrés

Sin "verdad absoluta" de OzRo, la validación debe ser **estructural, económica y de consistencia interna**:

1. **Tests de monotonía (dentro de estratos comparables):**
* Si todo lo demás es constante, mayor dificultad de obtención / menor probabilidad de éxito / menor tasa de aparición debe producir un costo esperado mayor o igual, y una tendencia de precio no decreciente (salvo caída clara de demanda/utilidad).
* Un ítem con 0 ventas o muestra minúscula debe tener un **ancho de banda (`p90 - p10`) mayor o igual** que un ítem equivalente con muestra amplia y consistente.


2. **Invariantes ontológicos y de canales:**
* Ningún ítem con `NoTrade` (o sin canal de comercio entre jugadores) debe marcarse como comerciable en el mercado de jugadores (`player_trade`).
* Ningún ítem con `NoSell` debe recibir un precio de compra del NPC por encima de lo permitido por su configuración `Sell` del servidor.
* Todo ítem con ventas o referencia válida debe tener trazabilidad completa (`sources`, `cost_breakdown`, `confidence`, `flags`).


3. **Pruebas de estrés (sensibilidad y perturbaciones):**
* **Simulación de fallos de ingesta:** Eliminar artificialmente un subconjunto de `mob_db` o spawns y verificar que el sistema degrade con `null` / banda amplia / alerta de procedencia en vez de colapsar silenciosamente en un número arbitrario (como 500k o 18k).
* **Perturbación de $w$ (zeny/hora):** Multiplicar/dividir $w$ por $0.5\times$ y $2\times$ y comprobar qué ítems son sensibles al costo de tiempo vs cuáles están dominados por *time gates* o referencias.
* **Inyección de *outliers* en referencias:** Meter una venta extrema de 1 unidad a $100\times$ y verificar que no domina la estimación central ni oculta la incertidumbre.



---

### 9. División entre fórmula / LLM / overrides manuales

La división más limpia, auditable y mantenible es:

* **Capa determinista (código / estadística / reglas de dominio — ~85–90% del trabajo):**
* Ingesta limpia, fusión de tablas sin sobrescritura destructiva, ontología separada de *adquisición*, *transferencia* y *mercado*.
* Cálculo de costos esperados, probabilidades compuestas, *upgrades* destructivos, cuantiles (`p10`/`p50`/`p90`), agregación de referencias históricas y reglas duras de elegibilidad/NPC.
* *Por qué:* Reproducible, auditable, barato y libre de alucinaciones numéricas.


* **Capa de LLM (asistencia semántica y clasificación acotada — una pasada auditada):**
* Clasificar o etiquetar ambigüedades textuales/semánticas donde las reglas puras son frágiles (por ejemplo, distinguir si un ítem sin fuente parece de *evento*, *quest antigua* o *legacy* a partir de nombres/descripciones/contexto, o detectar anomalías semánticas en grupos de ítems), **siempre devolviendo etiquetas estructuradas + justificación**, nunca como oráculo final de precios numéricos sin validación.


* **Overrides manuales (explícitos, versionados y mínimos):**
* Solo para casos excepcionales verificados (ej. ítems críticos de economía o *bugs* puntuales), guardados en un archivo versionado con `item_id`, `valor/rango`, `motivo`, `autor` y `fecha`, nunca parches ocultos en el código.



---

### 10. Plan de acción con presupuesto de 2–5 USD (una pasada LLM)

Con **2–5 USD** y una sola corrida de LLM, la prioridad absoluta es **maximizar fiabilidad estructural y trazabilidad**:

1. **Primero — Arreglar la ingesta y la ontología antes de gastar el presupuesto:**
Corregir la fusión de `mob_db.yml` (no sobrescribir campos existentes al cargar `DamageTaken`), corregir el mapeo de mapas/zonas (como `alb_ship`) y separar los tres ejes (*adquisición*, *transferencia*, *mercado*). Si alimentas un modelo nuevo con datos corruptos, ningún LLM lo salva.
2. **Segundo — Motor estadístico/económico base sin LLM:**
Implementar el cálculo de costo esperado por ruta, el tratamiento de *upgrades* destructivos, la combinación robusta de referencias históricas (con penalización por desacuerdo y soporte muestral), el manejo de `null` ("sin precio") cuando no hay mercado ni ruta, y la salida en cuantiles (`p10`, `p50`, `p90`) con trazabilidad completa.
3. **Tercero — Usar los 2–5 USD de LLM en una pasada focalizada y auditable:**
Enviar solo los ítems ambiguos o de difícil clasificación (por ejemplo, ítems sin fuente ni ventas históricas para desambiguar `legacy` vs `event` vs `unparsed_source`, o ítems con fuerte desacuerdo entre fuentes para generar notas de auditoría y señales de revisión), exigiendo salida JSON estructurada y guardando el *prompt*, respuesta y *seed* para reproducibilidad.
4. **Qué dejar explícitamente sin resolver en esta iteración:**
* **El equilibrio dinámico completo de la economía viva de OzRo** (inflación real, *sinks* de *zeny* en tiempo real, comportamiento estratégico de clanes/MVP y *market makers* activos): sin datos de mercado propios del servidor en producción, se modela como estructura de costos, escasez y rangos de incertidumbre, y se refina cuando haya telemetría real del mercado de OzRo.
* **Equilibrios complejos de *combos* / *meta* multidimensionales** que requieran simulación agente-por-agente o grafos de utilidad cruzada de alto orden.
