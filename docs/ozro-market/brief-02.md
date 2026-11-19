# Brief 02 — Diseño de la economía sintética de OzRo

**Ronda de un solo revisor.** Responde como si fuera la primera vez que ves el
problema. No compares con intentos anteriores y no asumas que el dataset actual
es correcto.

---

## 0. Encargo

No escribas un ensayo. Escribe una **especificación técnica** que pueda
convertirse en módulos, esquemas de datos y pruebas.

Orden obligatorio:

1. Primero, el **conjunto de parámetros** que la economía necesita.
2. Después, la **ontología** (entidades, estados, relaciones).
3. Después, una **función por parámetro**, aislada y con unidades.
4. Después, la **composición** en políticas de precio y de NPC.
5. Al final, **validación, fases y modos de fallo**.

No empieces proponiendo fórmulas de precio. Primero hay que decidir qué
magnitudes existen y cuáles son redundantes.

Marca cada decisión como:

- `DECIDIDO` — ya está fijado en este brief.
- `PROPUESTO` — tu recomendación.
- `ABIERTO` — requiere decisión del equipo.

---

## 1. Contexto

OzRo es un servidor privado de Ragnarok Online, rAthena Renewal, con rates
custom, compartido por aproximadamente **cuatro jugadores**. El juego es
principalmente offline/cooperativo y no existe una población suficiente para
formar un mercado orgánico: no hay price discovery, no hay liquidez, no hay
demanda observada y no se espera que aparezca.

El NPC (o los NPCs) deben suplir las funciones económicas que normalmente
cumpliría una comunidad:

- comprar lo que un jugador obtiene y no necesita;
- vender o proveer lo que un jugador necesita y no puede farmear;
- valorar objetos para orientar decisiones;
- dar liquidez y estabilizar la economía;
- evitar que la progresión dependa de un único drop.

La lógica MMO normal es: aunque un objeto sea improbable, con suficientes
jugadores a alguien le termina tocando, y el mercado lo redistribuye. Con
cuatro jugadores ese componente estadístico desaparece. La economía sintética
debe **emular el efecto de una población mayor**.

---

## 2. Objetivo

Diseñar una economía sintética que cumpla dos funciones simultáneas:

1. **Liquidez para lo que sale.** Un objeto raro o valioso que un jugador
   obtiene no debe terminar en la basura por no haber comprador. Debe poder
   convertirse en valor y, eventualmente, en el objeto que el jugador necesita.
2. **Suministro para lo que se necesita.** Un objeto raro o difícil no debe
   quedar limitado a la suerte o al grindeo personal por no haber quien lo
   provea. Debe existir una ruta razonable para adquirirlo.

El criterio de éxito no es “predecir el precio de otro servidor”. Es que la
progresión, el acceso a objetos raros y la liquidez funcionen sin una comunidad
grande, y que la economía no colapse.

---

## 3. Decisiones ya tomadas

Estas son restricciones duras, no sugerencias.

### 3.1 Unidad de cuenta

La unidad es la **hora de juego**.

La dificultad de adquisición se obtiene cruzando:

- una **distribución de capacidad de jugadores simulados** (nivel, equipo,
  clase, tiempo de juego, habilidad);
- una **distribución determinista de dificultad de los mobs** (HP efectivo,
  DEF/MDEF, daño, mecánicas, acceso, respawn);
- la **probabilidad efectiva de drop** y las rutas alternativas.

La intuición central: la mayor parte de la población simulada estará en
jugadores de nivel medio-bajo; los jugadores de alto nivel y bien equipados
serán escasos. Por eso los mobs más difíciles son **doblemente improbables**:
requieren jugadores capaces, que son pocos, y además tienen baja frecuencia o
baja probabilidad de drop.

De ahí salen dos cantidades distintas:

- **horas personales** que tarda un jugador representativo en conseguir una
  unidad;
- **tasa agregada de suministro** que produce la población simulada.

No confundir ambas.

### 3.2 Arquitectura por capas

La economía se construye en capas separadas. Cada capa se puede construir,
evaluar y ajustar por separado. Sobre las capas se ajusta la regresión o
política particular de cada NPC.

Puede haber **más de tres NPCs**, con alcance, objetivos y políticas distintas
(tasador, comprador, vendedor, bróker, casa de cambio, etc.). No asumas que
todos comparten el mismo precio ni la misma política.

### 3.3 Demanda y utilidad

La demanda **se diseña**, no se estima. No hay ventas internas de las que
inferirla.

Es un problema de diseño cuidadoso. Si no se puede justificar una utilidad
sólida en la v1, se puede excluir del análisis; en ese caso hay que explicar
qué se pierde y cómo se compensa.

### 3.4 Nivel absoluto

El nivel absoluto de la economía **se decide e impone**, no se calibra con
datos de otros servidores. Un modelo directo, explícito y versionado es
preferible a uno que herede el nivel de una economía que OzRo no tiene.

Los datos externos, si se usan, sirven para aprender **estructura relativa**
(órdenes, ratios, rangos, preferencias), no para fijar precios absolutos.

### 3.5 Validación

No hay ground truth y no se espera tenerla. El modelo se construye desde
lógica, economía, estadística e intuición. Debe incluir mecanismos de
**detección temprana de colapso**: inflación, arbitraje, progresión truncada,
objeto dominante, rutas de dinero triviales.

### 3.6 Taxonomía

La taxonomía se define **de nuevo**. No se reutilizan booleanos ni categorías
de intentos anteriores. Se pueden aprovechar las lecciones, pero no el modelo
de datos.

### 3.7 LLM

Un LLM puede usarse para:

- extraer features de utilidad desde descripciones y scripts;
- interpretar mecánicas, recetas, quests y restricciones;
- clasificar casos ambiguos.

No se usa para fijar precios. Una corrida no determinista es aceptable si la
salida queda registrada, versionada y auditable. Presupuesto orientativo:
2–5 USD.

---

## 4. El problema

> Diseñar una economía sintética para un servidor de cuatro jugadores sin
> mercado observado, que asigne valores, precios y políticas de compra/venta a
> los NPCs, de modo que la progresión, el acceso a objetos raros y la liquidez
> funcionen sin depender de una población grande.

Sub-problemas que la especificación debe resolver:

1. **Ontología económica.** Qué entidades, estados, relaciones y canales
   existen. No una taxonomía de tipos de item; un modelo de roles económicos,
   rutas, restricciones, utilidad y evidencia.
2. **Catálogo de parámetros.** Qué magnitudes necesita el sistema, con unidad,
   origen y tipo (dato, decisión, derivado). Cuáles son redundantes.
3. **Adquisición.** Rutas, tiempo, zeny, riesgo, probabilidad, procesos
   destructivos, time gates, acceso, competencia.
4. **Escasez.** Qué significa con cuatro jugadores. Distinguir “no hay fuente”,
   “hay fuente pero es lenta”, “hay inventario legacy”, “nadie puede farmearlo”.
5. **Utilidad.** Si se incluye, cómo se construye sin demanda observada:
   efectos, rol en progresión, recetas, cobertura de builds, sustitutos.
6. **Precio y política.** Cómo se combinan costo, escasez, utilidad y
   evidencia; cómo se fija el nivel; cómo se expresa la incertidumbre; cuándo
   no hay precio.
7. **NPCs.** Roles, objetivos, políticas, spreads, caps, emisión de zeny y
   anti-arbitraje.
8. **Validación y robustez.** Sin ground truth: invariantes, simulación,
   estrés, métricas de colapso.
9. **Datos.** Qué se registra, qué se puede reconstruir, qué queda `unpriced`.

---

## 5. Entregable

Produce un documento con estas secciones, en este orden.

### A. Catálogo de parámetros

Una tabla con, como mínimo:

| Campo | Contenido |
|---|---|
| nombre | identificador estable |
| significado | qué representa económicamente |
| unidad | hora, zeny, probabilidad, ratio, categoría |
| origen | dato, decisión de diseño, derivado |
| cálculo | función o fuente, si aplica |
| sensibilidad | qué pasa si se equivoca |
| redundancia | qué otros parámetros lo reemplazan o solapan |

No propongas fórmulas todavía. Primero el catálogo.

### B. Ontología

Entidades, estados y relaciones. Justifica por qué cada eje es independiente.
Cubre como mínimo:

- adquisición;
- transferencia y canales;
- estado de mercado;
- evidencia y procedencia;
- utilidad;
- restricciones de NPC.

### C. Contratos de capas

Para cada capa:

- inputs;
- outputs;
- supuestos;
- qué se puede ajustar sin romper las demás;
- cómo se prueba de forma aislada.

### D. Funciones por parámetro

Una función por parámetro, con unidades y supuestos. Como mínimo:

- capacidad de un jugador simulado;
- dificultad de un mob;
- clearability y pool efectivo de farmers;
- tasa de suministro agregada;
- horas personales de adquisición;
- escasez;
- costo de una ruta destructiva;
- time gate;
- rutas múltiples y ruta mínima;
- liquidez;
- utilidad, si se incluye;
- nivel absoluto de la economía;
- precio/política;
- incertidumbre.

Incluye un ejemplo numérico mínimo para:

1. un farm común;
2. un proceso destructivo;
3. un time gate tipo MVP.

### E. Composición

Cómo se pasa de las funciones a:

- un valor o banda por item;
- una política de tasador;
- una política de comprador;
- una política de vendedor;
- una política de bróker o casa de cambio, si aplica.

Explica cómo se evita que dos NPCs con políticas distintas creen arbitraje.

### F. Política NPC

Para cada NPC:

- objetivo económico;
- a quién sirve;
- qué compra y qué vende;
- spread;
- caps por item, por cuenta y por día;
- qué hace con `NoSell`, `NoTrade`, items legacy y `unpriced`;
- cómo controla la emisión/destrucción de zeny;
- invariantes anti-arbitraje.

### G. Validación y modos de fallo

- invariantes que deben cumplirse siempre;
- pruebas de monotonía;
- simulación de la población y de la progresión;
- pruebas de estrés (rates, spawns, población, precios);
- métricas de colapso y umbrales de alerta;
- qué se registra para poder auditar y recalibrar.

### H. Fases

Qué se construye primero, qué se deja para v2, qué queda explícitamente
`unpriced` o fuera de alcance.

### I. Supuestos y riesgos

Qué tiene que ser cierto para que el modelo funcione. Qué lo haría fallar.
Cómo se detecta temprano.

---

## 6. Preguntas guía

No es obligatorio responderlas una por una, pero la especificación debe
resolverlas.

1. ¿Cuál es el conjunto mínimo de parámetros? ¿Cuáles se derivan de otros?
2. ¿Cómo se modela la curva de jugadores simulados y la curva de mobs? ¿Cómo se
   cruzan y en qué unidad intermedia?
3. ¿Cómo se define escasez con cuatro jugadores? ¿Entra la competencia?
4. ¿La utilidad debe estar en la v1? Si sí, ¿cómo se construye sin demanda
   observada? Si no, ¿qué se pierde?
5. ¿Qué parámetro único fija el nivel absoluto de la economía y cómo se elige?
6. ¿Cómo se diseñan varios NPCs con políticas distintas sin crear arbitraje?
7. ¿Qué invariantes debe cumplir el sistema para no colapsar?
8. ¿Qué se registra para poder auditar y recalibrar después?
9. ¿Qué haría fallar el modelo y cómo se detecta temprano?
10. ¿Qué se construye primero y qué se deja fuera?

---

## 7. Anti-patrones

No uses:

- un solo booleano para “obtenible” o “comerciable”;
- percentiles de tipo como base de precio;
- una referencia histórica puntual sin calidad de muestra;
- `precio = costo` como identidad;
- un precio para todos los objetos;
- un LLM como generador de precios;
- los precios absolutos de otro servidor como objetivo;
- multiplicadores ajustados sobre una base mal definida;
- una taxonomía heredada de un intento anterior.

---

## 8. Cómo se evaluará la respuesta

- ¿Define parámetros antes de fórmulas?
- ¿Distingue dato, decisión y derivado?
- ¿La ontología separa adquisición, transferencia, mercado, utilidad y
  evidencia?
- ¿Las funciones tienen unidades y supuestos?
- ¿El nivel absoluto queda en un solo lugar explícito?
- ¿La política NPC es operable y no crea arbitraje?
- ¿La validación es posible sin ground truth?
- ¿Queda claro qué se construye primero y qué se deja fuera?
- ¿Aterriza en OzRo o se queda en principios generales?
