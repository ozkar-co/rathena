# Propuesta técnica
## Diseño de una economía sintética para OzRo

**Versión:** Propuesta de arquitectura y modelado  
**Alcance:** MarketSimulator, sistema de valoración y NPCs de compra, venta e intercambio.  
**Contexto:** Ragnarok Online, rAthena Renewal, rates custom, cuatro jugadores y ausencia de mercado orgánico.

---

# 1. Resumen ejecutivo

## 1.1. El problema real

OzRo no necesita un modelo que intente descubrir cuánto pagarían otros jugadores por cada objeto. No existe una población suficiente para que ese precio emerja, ni se espera que llegue a existir.

El sistema debe construir artificialmente las funciones económicas que normalmente proporciona una comunidad:

- Permitir que un jugador convierta objetos que no necesita en valor económico.
- Permitir que ese valor se convierta en objetos que sí necesita.
- Proporcionar acceso razonable a objetos difíciles de conseguir.
- Mantener una progresión coherente entre niveles y etapas del juego.
- Evitar que la economía genere zeny ilimitado o permita arbitrajes.
- Conservar el valor de la exploración, el combate, el crafteo y los drops.
- Evitar que la suerte individual determine por completo el progreso.

Esto coincide con los dos objetivos centrales del brief: liquidez para los objetos que salen y suministro para los objetos que se necesitan. La economía debe compensar la ausencia de la población que normalmente redistribuiría los objetos.

Por tanto, la solución no debería llamarse simplemente un estimador de precios.

Debe entenderse como un **sistema de economía sintética con un mercado administrado por NPCs**.

## 1.2. Arquitectura recomendada

Propongo cinco componentes principales, conectados pero independientes:

| Componente | Responsabilidad |
|---|---|
| 1. Modelo del mundo | Describe objetos, mobs, spawns, recetas, quests, restricciones y fuentes. |
| 2. Modelo de adquisición | Estima cuánto esfuerzo, tiempo, zeny y riesgo requiere obtener cada objeto. |
| 3. Modelo de progresión y utilidad | Determina qué objetos necesita un personaje y cuánto contribuyen a su avance. |
| 4. Motor económico | Establece valores de referencia, escasez sintética, inventarios, presupuestos y políticas de mercado. |
| 5. Simulador y NPCs | Simula el comportamiento económico y ejecuta las políticas de compra, venta e intercambio. |

La separación más importante es esta:

**El costo de conseguir un objeto no es necesariamente su precio de mercado, y su precio de mercado no tiene que ser idéntico al precio que un NPC está dispuesto a pagar o cobrar.**

El sistema debe calcular esas magnitudes por separado.

## 1.3. Decisiones principales

| Tema | Decisión recomendada |
|---|---|
| Unidad económica | Hora estándar de juego, convertida a zeny mediante un parámetro global. |
| Dificultad de adquisición | Modelada mediante perfiles de jugadores, rutas y capacidad efectiva de farmeo. |
| Escasez | Calculada a partir de oferta efectiva, necesidad sintética e inventario disponible. |
| Utilidad | Incluir una clasificación funcional desde la primera versión; cuantificarla progresivamente. |
| Demanda | Sintética y derivada de progresión, builds, recetas y consumo. No simular ventas observadas inexistentes. |
| Precios históricos | Referencias externas para contrastar relaciones y órdenes de magnitud, no objetivos absolutos. |
| Precio de referencia | Derivado del esfuerzo de adquisición, limitado por objetivos de progresión. |
| NPC comprador | Compra con presupuesto e inventario limitados. |
| NPC vendedor | Vende desde un inventario controlado, con reposición sintética explícita. |
| Intercambio | Recomiendo añadir un saldo de intercambio no convertible a zeny. |
| LLM | Extracción estructurada de información; nunca asignación autónoma de precios. |
| Validación | Simulación de progresión, rentabilidad, inventarios, emisión monetaria y arbitraje. |

---

# A. Diagnóstico

## A.1. Qué puede determinarse con los datos disponibles

El brief contiene suficiente información para comenzar a construir una primera versión del modelo del mundo y del modelo de adquisición.

Los principales datos disponibles son:

| Fuente | Datos disponibles | Aplicación |
|---|---|---|
| `item_db` | 29.061 objetos, tipos, slots, scripts, niveles y flags | Identidad, características y restricciones de objetos. |
| `mob_db` | 2.675 mobs, características de combate y drops declarados | Modelado de fuentes y dificultad. |
| Spawns | 3.656 spawns parseados, 405 mapas y 1.223 mobs distintos con spawn | Disponibilidad y capacidad de suministro. |
| Grupos | 2.973 grupos y 3.082 subgrupos | Fuentes indirectas de objetos. |
| `produce_db` | 293 recetas | Costos de fabricación. |
| Socket enchant | 39 recetas | Rutas de modificación y mejora. |
| Scripts | Quests, instancias y NPCs | Fuentes, requisitos, time gates y procesos especiales. |
| Histórico externo | 5.858 registros LATAM y Atlantis | Referencia comparativa. |

Los datos están documentados en el brief, pero el propio documento advierte que los spawns parseados no han sido verificados individualmente y que los flags declarados no garantizan por sí solos el comportamiento efectivo del servidor.

Esto permite construir:

1. Un catálogo inicial de objetos.
2. Un grafo de fuentes y rutas de adquisición.
3. Un modelo inicial de dificultad de combate.
4. Una estimación de disponibilidad por fuente.
5. Un modelo de costos para recetas conocidas.
6. Una clasificación inicial de objetos y restricciones.

No permite determinar automáticamente:

- Cuánto debería tardar un jugador en conseguir un equipo.
- Cuánto debería costar ese equipo.
- Qué objetos son importantes para las builds que se juegan.
- Cuánto zeny debería generar una hora de actividad.
- Cuánta existencia debería tener un NPC.
- Cuánta oferta virtual necesita el sistema para reproducir una economía funcional.

Esas magnitudes deben establecerse mediante decisiones de diseño.

## A.2. Qué debe decidirse por diseño

Hay cinco decisiones que condicionan todo el sistema.

### 1. La velocidad de progresión

Hay que decidir cuánto debería tardar un jugador en alcanzar determinadas etapas.

Por ejemplo:

- Tiempo para obtener el primer equipo funcional.
- Tiempo para completar un equipo intermedio.
- Tiempo para conseguir una mejora importante.
- Tiempo para preparar un personaje para contenido avanzado.
- Tiempo para alcanzar una build especializada.

No es necesario fijar un tiempo para cada uno de los miles de objetos. Se deben establecer objetivos por etapas y categorías de progresión.

### 2. El poder adquisitivo de una hora

Hay que establecer una equivalencia entre esfuerzo y zeny.

Sin esta decisión, el modelo puede calcular que un objeto exige diez horas de farmeo, pero no puede determinar qué significa económicamente ese esfuerzo.

### 3. La disponibilidad artificial

Hay que decidir qué objetos podrá suministrar el mercado sintético, en qué cantidades y con qué frecuencia.

No todos los objetos deben estar disponibles de manera ilimitada.

### 4. La utilidad de los objetos

No todos los objetos tienen el mismo propósito.

Un material necesario para fabricar un arma clave, una carta de colección y una poción consumible pueden tener dificultades de adquisición similares, pero no cumplen la misma función en la progresión.

### 5. El comportamiento de los NPCs

Los NPCs deben trabajar sobre una misma contabilidad económica. No pueden ser sistemas independientes que asignen precios sin considerar las consecuencias de sus operaciones.

## A.3. Los mayores riesgos

| Riesgo | Consecuencia | Prioridad |
|---|---|---|
| Datos incorrectos de fuentes y spawns | Precios y disponibilidad incorrectos | Crítica |
| Interpretación incorrecta de rates | Cálculos de suministro incorrectos | Crítica |
| Perfiles de jugadores irreales | Dificultad de adquisición mal estimada | Alta |
| No modelar la utilidad | Objetos raros sin relevancia reciben demasiado valor | Alta |
| No controlar la emisión de zeny | Inflación y acumulación monetaria | Crítica |
| NPCs con políticas independientes | Arbitraje y ciclos de beneficio | Crítica |
| Oferta artificial ilimitada | Desaparece el valor del farmeo | Alta |
| Confundir ausencia de datos con imposibilidad de adquisición | Objetos mal clasificados | Alta |

---

# B. Conjunto de parámetros

La recomendación es no comenzar con una fórmula general de precios.

Primero hay que definir qué magnitudes existen, qué representan, cómo se calculan y qué consecuencias tienen.

El siguiente catálogo es el conjunto mínimo que considero suficiente para una primera implementación seria.

## B.1. Parámetros del mundo y de las fuentes

| Campo | Significado | Unidad | Origen | Sensibilidad |
|---|---|---|---|---|
| `item_id` | Identificador del objeto | ID | Dato | Crítica |
| `route_id` | Identificador de una ruta de adquisición | ID | Derivado | Alta |
| `route_type` | Farm, craft, quest, MVP, evento, NPC, etc. | Categoría | Dato/derivado | Alta |
| `source_id` | Mob, NPC, quest, receta o instancia | ID | Dato | Alta |
| `drop_probability` | Probabilidad efectiva de obtener el objeto | Probabilidad | Derivado | Crítica |
| `drop_quantity` | Cantidad esperada por éxito | Unidades | Dato/derivado | Media |
| `spawn_capacity` | Capacidad máxima de generación de la fuente | Unidades/hora | Derivado | Crítica |
| `access_requirement` | Condiciones necesarias para acceder a la fuente | Requisitos | Dato/derivado | Alta |
| `time_gate` | Restricción temporal de la fuente | Tiempo | Dato | Alta |

## B.2. Parámetros de los jugadores simulados

| Campo | Significado | Unidad | Origen | Sensibilidad |
|---|---|---|---|---|
| `profile_id` | Perfil de jugador | ID | Decisión | Alta |
| `combat_capability` | Capacidad de combate del perfil | Score o métricas de combate | Derivado | Crítica |
| `kill_time` | Tiempo promedio para eliminar un mob | Segundos | Simulación | Crítica |
| `travel_time` | Tiempo de desplazamiento y preparación | Segundos | Estimado/derivado | Media |
| `death_probability` | Probabilidad de morir durante la actividad | Probabilidad | Simulación | Alta |
| `accessibility` | Capacidad de acceder a una ruta | Booleano o probabilidad | Derivado | Alta |
| `activity_hours` | Tiempo disponible para jugar | Horas/día | Decisión/supuesto | Alta |
| `profile_weight` | Peso del perfil en la simulación | Proporción | Decisión | Alta |

## B.3. Parámetros económicos

| Campo | Significado | Unidad | Origen | Sensibilidad |
|---|---|---|---|---|
| `zeny_per_hour` | Valor económico de una hora estándar | Zeny/hora | Decisión | Crítica |
| `acquisition_hours` | Horas activas para conseguir una unidad | Horas | Derivado | Crítica |
| `acquisition_cost` | Costo total esperado de una ruta | Zeny equivalentes | Derivado | Crítica |
| `synthetic_utility` | Contribución del objeto a la progresión | Horas ahorradas o índice | Derivado/decisión | Alta |
| `synthetic_demand` | Necesidad proyectada del objeto | Unidades/periodo | Derivado | Alta |
| `effective_supply` | Oferta efectiva del objeto | Unidades/periodo | Derivado | Crítica |
| `scarcity_ratio` | Relación entre necesidad y disponibilidad | Ratio | Derivado | Alta |
| `target_time` | Tiempo de adquisición deseado para una etapa | Horas | Decisión | Crítica |

## B.4. Parámetros de los NPCs

| Campo | Significado | Unidad | Origen | Sensibilidad |
|---|---|---|---|---|
| `reference_price` | Valor económico de referencia | Zeny | Derivado | Crítica |
| `bid_price` | Precio al que el NPC compra | Zeny o créditos | Derivado | Alta |
| `ask_price` | Precio al que el NPC vende | Zeny o créditos | Derivado | Alta |
| `spread` | Diferencia relativa entre compra y venta | Ratio | Decisión | Alta |
| `npc_stock` | Inventario disponible | Unidades | Simulado | Alta |
| `target_stock` | Inventario deseado | Unidades | Decisión/derivado | Alta |
| `restock_rate` | Reposición del inventario | Unidades/periodo | Derivado/decisión | Alta |
| `npc_budget` | Presupuesto de compra | Zeny | Decisión/estado | Crítica |
| `transaction_cap` | Límite de operaciones | Unidades/periodo | Decisión | Media |

## B.5. Parámetros de calidad y procedencia

| Campo | Significado | Unidad | Origen | Sensibilidad |
|---|---|---|---|---|
| `evidence_source` | Archivo, script, histórico o regla que sustenta un dato | Referencia | Dato | Alta |
| `evidence_grade` | Calidad de la evidencia | A/B/C/D | Derivado/revisión | Alta |
| `confidence` | Confianza en la estimación | 0–1 | Derivado | Alta |
| `model_version` | Versión del modelo utilizado | Versión | Sistema | Alta |
| `run_id` | Identificador de corrida | ID | Sistema | Alta |
| `input_snapshot` | Huella de los datos utilizados | Hash | Sistema | Alta |

## B.6. Parámetros que no recomiendo duplicar

Para evitar que el modelo termine acumulando multiplicadores redundantes, no mantendría todos estos valores como magnitudes independientes:

- Rareza.
- Dificultad.
- Cantidad de fuentes.
- Frecuencia de aparición.
- Número de spawns.
- Probabilidad de drop.
- Escasez.
- Dificultad de farmeo.

Deben alimentar el modelo de adquisición y disponibilidad.

Por ejemplo, si un objeto tiene una probabilidad muy baja, pocos spawns y una ruta difícil, esas características ya deben reflejarse en su tasa efectiva de suministro y sus horas de adquisición.

No tendría sentido multiplicar después el precio por una variable adicional de rareza, otra de dificultad y otra de cantidad de fuentes. Eso contaría varias veces el mismo fenómeno.

---

# C. Ontología económica

La ontología debe describir cómo funciona económicamente un objeto, no solamente qué tipo tiene en `item_db`.

Propongo que cada objeto pueda tener múltiples rutas, roles y restricciones simultáneamente.

## C.1. Entidades principales

| Entidad | Descripción |
|---|---|
| `Item` | Objeto del universo de OzRo. |
| `AcquisitionRoute` | Forma de conseguir un objeto. |
| `Source` | Entidad que entrega, fabrica o permite obtener un objeto. |
| `PlayerProfile` | Perfil de capacidad utilizado en la simulación. |
| `ProgressionStage` | Etapa de desarrollo de un personaje. |
| `Build` | Configuración de clase y equipo que utiliza objetos. |
| `Recipe` | Relación de consumo y producción entre objetos. |
| `MarketPool` | Inventario y presupuesto del mercado sintético. |
| `NPCPolicy` | Reglas de compra, venta o intercambio. |
| `EvidenceRecord` | Evidencia que sustenta un dato o decisión. |
| `EconomicScenario` | Conjunto de parámetros de una simulación. |

## C.2. Eje de adquisición

Un objeto puede tener una o varias rutas:

| Estado | Significado |
|---|---|
| `farmed` | Se obtiene de mobs. |
| `crafted` | Se fabrica mediante una receta. |
| `quested` | Se obtiene mediante una quest. |
| `group_reward` | Se obtiene de un grupo de objetos. |
| `instance` | Se obtiene en instancias. |
| `mvp` | Se obtiene de una fuente MVP o boss. |
| `npc_source` | Lo entrega un NPC. |
| `event` | Depende de un evento. |
| `legacy` | Pertenece a contenido anterior o deshabilitado. |
| `unknown` | No se encontró una fuente confirmada. |
| `none_confirmed` | Se verificó que no existe una ruta activa. |

Una consideración importante:

**`unknown` no significa `none_confirmed`.**

Que un parser no encuentre una fuente no demuestra que el objeto sea imposible de conseguir.

Además, un mismo objeto puede tener varias rutas. Una carta, por ejemplo, podría obtenerse de un mob, una caja o una recompensa especial.

## C.3. Eje de transferencia

Las restricciones deben modelarse independientemente de la adquisición.

Propongo registrar capacidades por canal:

- Comercio entre jugadores.
- Venta a NPC.
- Compra a NPC.
- Drop al suelo.
- Storage.
- Cart.
- Mail.
- Auction.
- Guild Storage.

Esto evita interpretar todas las restricciones como si significaran lo mismo.

Los flags declarados en `item_db` son un punto de partida, pero el comportamiento efectivo debe verificarse en la configuración y los scripts del servidor. El propio brief advierte esta limitación.

## C.4. Eje de mercado

| Estado | Significado |
|---|---|
| `active` | El objeto participa activamente en el mercado sintético. |
| `thin` | Tiene oferta limitada o reposición lenta. |
| `stockout` | Su inventario está temporalmente agotado. |
| `no_evidence` | Existe información insuficiente para establecer una valoración fiable. |
| `not_traded` | No participa en las operaciones del sistema. |
| `restricted` | Tiene restricciones específicas de compra o venta. |

Este estado describe el mercado diseñado por OzRo, no un mercado real.

## C.5. Eje de utilidad

Propongo clasificar cada objeto por uno o varios roles:

| Rol | Ejemplo de aplicación |
|---|---|
| `progression` | Equipo que permite avanzar a otra etapa. |
| `combat` | Objeto que mejora daño, defensa o supervivencia. |
| `consumable` | Pociones, comidas y materiales de uso recurrente. |
| `crafting_input` | Material necesario para fabricar otros objetos. |
| `upgrade_input` | Objeto necesario para refinar o mejorar equipo. |
| `quest_requirement` | Objeto que desbloquea contenido. |
| `content_access` | Objeto que permite entrar a una instancia o actividad. |
| `build_specific` | Objeto importante para una clase o build concreta. |
| `convenience` | Objeto que mejora comodidad o eficiencia. |
| `collection` | Objeto de colección o completismo. |
| `cosmetic` | Objeto principalmente estético. |

La categoría `Etc`, `Armor` o `Card` de rAthena no reemplaza esta clasificación. Describe el tipo técnico del objeto, no su importancia económica.

## C.6. Eje de evidencia

Cada dato relevante debería tener procedencia.

Recomiendo estos niveles:

- **A — Verificado:** se comprobó en configuración, script o juego.
- **B — Derivado:** se calculó a partir de datos verificados.
- **C — Inferido:** se dedujo de scripts, patrones o relaciones incompletas.
- **D — Supuesto:** se asignó mediante una decisión de diseño.

El modelo debe poder explicar por qué considera que un objeto es caro, escaso, útil o comerciable.

---

# D. Modelado de parámetros

Esta sección establece cómo calcular las magnitudes del sistema.

## D.1. Modelo de capacidad de los jugadores

### Problema de la hipótesis de distribución poblacional

La hipótesis de cruzar una distribución de capacidad de jugadores con dificultad de mobs es razonable como punto de partida, pero tiene una limitación importante.

No existe una población real de jugadores que permita estimar esa distribución.

Suponer que la mayoría está en niveles medios-bajos puede producir un modelo convincente matemáticamente, pero no necesariamente representa cómo juegan las cuatro personas de OzRo.

Por ello, recomiendo no modelar una población MMO ficticia como si fuera un dato real.

En su lugar, utilizar perfiles de capacidad explícitos.

### Perfiles recomendados

| Perfil | Función |
|---|---|
| `beginner` | Personaje en progresión inicial. |
| `intermediate` | Personaje con equipo funcional. |
| `advanced` | Personaje con capacidad para contenido avanzado. |
| `specialized` | Personaje optimizado para una actividad concreta. |

Estos perfiles no deben convertirse en una distribución fija del servidor.

Idealmente, se construyen a partir de los cuatro personajes reales, con sus clases, niveles y equipo. Cuando esa información no esté disponible, se utilizan escenarios sintéticos.

Cada perfil debe tener:

- Nivel.
- Clase.
- Build.
- Ataque efectivo.
- Defensa efectiva.
- Supervivencia.
- Velocidad de movimiento.
- Velocidad de eliminación.
- Capacidad de curación.
- Habilidad o eficiencia operativa.
- Acceso a mapas e instancias.
- Horas disponibles para jugar.

El modelo debe permitir simular tanto jugadores individuales como grupos.

### Capacidad de eliminar un mob

Para un perfil `k` y un mob `m`:

`kill_time(k,m) = tiempo esperado para eliminar m con el perfil k`

La estimación puede construirse mediante una simulación de combate o una aproximación inicial basada en daño, HP, defensa, habilidades y supervivencia.

No recomiendo usar únicamente el nivel del mob como medida de dificultad.

Un mob de nivel bajo puede ser difícil para una clase concreta, mientras que uno de nivel superior puede ser fácil para otra.

Por eso, la dificultad debe depender de la relación entre personaje y enemigo:

`difficulty(k,m) = f(capacidad_k, características_m, interacción de combate)`

La salida importante no es un score abstracto de dificultad, sino la capacidad de farmeo resultante.

## D.2. Accesibilidad y pool efectivo de farmeo

Un mob puede existir en el servidor y aun así no estar disponible para un perfil.

Por ejemplo:

- El perfil no tiene acceso al mapa.
- El mob requiere una instancia.
- El mob es demasiado peligroso.
- El spawn está limitado.
- El mob aparece detrás de una quest.
- El personaje no puede eliminarlo de manera rentable.

Definimos:

`A(k,m) = 1` si el perfil puede acceder y farmear la fuente.

`A(k,m) = 0` si no puede hacerlo.

En casos probabilísticos se puede utilizar un valor entre cero y uno, pero para la primera versión recomiendo mantener una clasificación clara de accesibilidad y dejar la probabilidad para el riesgo de muerte o éxito.

El pool efectivo de una fuente es el conjunto de perfiles capaces de explotarla.

Esto es más útil que contar mobs o spawns de manera aislada.

## D.3. Tasa efectiva de suministro

Para cada perfil `k` y mob `m`:

`kills_per_hour(k,m) = cantidad esperada de mobs eliminados por hora`

La tasa potencial de suministro del objeto `i` es:

`S(i,m,k) = kills_per_hour(k,m) × expected_drop(i,m)`

Donde:

- `S` se expresa en unidades por hora activa.
- `expected_drop` representa la cantidad esperada del objeto por eliminación.

La probabilidad efectiva debe considerar los rates custom, las reglas de rAthena, límites, multiplicadores, excepciones y comportamiento efectivo del servidor.

No recomiendo multiplicar directamente el valor de `Drop` de la base de datos por un rate global sin reproducir las reglas reales del emulador.

El brief contiene rates diferentes para objetos comunes, equipo, healing, cartas y MVP cards. Son parte esencial del cálculo y deben procesarse según las reglas efectivas de rAthena.

### Límite de los spawns

La cantidad de jugadores que pueden eliminar mobs no siempre determina cuánto suministro se genera.

Un spawn puede convertirse en el cuello de botella.

Por ello:

`K_effective(m) = min(K_player_capacity(m), K_spawn_capacity(m))`

Donde:

- `K_player_capacity` es la capacidad agregada de eliminación.
- `K_spawn_capacity` es el máximo que los spawns pueden producir durante el periodo.

La capacidad del spawn debe calcularse según sus reglas reales de aparición y respawn, no mediante una fórmula universal que suponga que todos los scripts funcionan igual.

Luego:

`S(i,m) = K_effective(m) × expected_drop(i,m)`

Y el suministro total de un objeto:

`S(i) = Σ S(i,m)`

Se suman las fuentes independientes.

### Suministro de los cuatro jugadores

Para un periodo de simulación:

`S_group(i) = Σ [S(i,k) × active_hours(k)]`

Esto estima las unidades que pueden producirse con el tiempo de juego disponible de los perfiles.

Hay que distinguir:

- Horas activas de los jugadores.
- Horas de reloj del servidor.
- Tiempo de respawn.
- Tiempo de espera por una instancia o evento.

No son unidades intercambiables.

Además, si cuatro jugadores comparten un mismo MVP, no se debe multiplicar su suministro por cuatro. Los cuatro pueden colaborar, pero la aparición del MVP sigue estando limitada por el mismo spawn.

## D.4. Horas personales de adquisición

Para una ruta de farmeo simple:

`H_acquisition(i,k,m) = 1 / S(i,m,k)`

La unidad resultante es horas activas esperadas por unidad.

Esta fórmula supone una tasa promedio estable y una probabilidad de drop independiente entre eliminaciones.

Si existen tiempos de preparación, desplazamiento o recuperación:

`H_total = H_farm + H_travel + H_setup + H_recovery`

Se recomienda almacenar estas partes por separado.

No todos los objetos deben tener una única estimación de adquisición. Es preferible guardar resultados por perfil.

Para una valoración común del mercado puede utilizarse un perfil de referencia o un percentil ponderado de los perfiles relevantes.

## D.5. Rutas múltiples de adquisición

Un objeto puede obtenerse por distintas vías:

- Farm.
- Craft.
- Quest.
- Caja.
- Instancia.
- NPC.
- Recompensa de evento.

Para cada perfil se calcula el costo de las rutas accesibles.

Si el jugador puede elegir libremente entre ellas:

`C_best(i,k) = min(C_route(i,r,k))`

Esto representa la alternativa más eficiente disponible para ese perfil.

Pero el modelo debe conservar todas las rutas, no solo la más barata.

Una ruta puede tener menor costo económico y mayor tiempo de espera. Otra puede tener mayor costo y estar siempre disponible.

Por eso recomiendo registrar como mínimo:

- Costo total esperado.
- Horas activas.
- Tiempo de reloj.
- Disponibilidad.
- Límite de intentos.
- Restricciones de acceso.
- Dependencias.
- Confianza de la estimación.

### Producción conjunta

Hay un detalle importante: un mob puede entregar varios objetos en una misma eliminación.

Si el modelo asigna el costo completo de cada eliminación a cada objeto, terminará contando varias veces el mismo esfuerzo.

Para resolverlo, deben distinguirse dos cálculos:

1. **Esfuerzo dirigido:** cuánto tarda un jugador que busca deliberadamente un objeto.
2. **Costo económico asignado:** qué parte del esfuerzo corresponde a cada objeto dentro de una actividad que produce varios resultados.

En la primera versión pueden calcularse ambos, pero la valoración no debe sumar los costos completos de todos los drops como si cada uno requiriera una sesión de farmeo independiente.

## D.6. Costos de rutas destructivas

Las recetas y mejoras con probabilidad de éxito deben modelarse como procesos probabilísticos.

Definimos:

- `p`: probabilidad de éxito por intento.
- `C_success`: costo de un intento exitoso.
- `C_failure`: costo de un intento fallido.

Si los intentos son independientes y la probabilidad se mantiene:

`E[N_attempts] = 1 / p`

El costo esperado hasta obtener el resultado es:

`C_expected = C_success + ((1-p)/p) × C_failure`

Esta es la forma más explícita de contemplar que un intento exitoso y uno fallido podrían consumir recursos diferentes.

Cuando el costo esperado de cada intento sea equivalente:

`C_expected = C_attempt / p`

El costo de un intento debe contemplar:

- Materiales consumidos.
- Equipo o base que puede destruirse.
- Zeny.
- Tiempo activo.
- Costos adicionales por fallo.
- Costos de recuperación, si existen.

Esta distinción es fundamental para no infravalorar procesos de refinamiento, encantamiento o fabricación destructiva.

## D.7. Time gates y fuentes limitadas

Un time gate no debe tratarse como si fuera una hora normal de farmeo.

Ejemplo:

Un MVP aparece cada hora y requiere cinco minutos para eliminarlo.

El jugador no invierte una hora de trabajo activa por intento. Invierte cinco minutos de actividad y debe esperar el siguiente ciclo.

Por eso, se recomienda mantener:

`H_active`: horas activas esperadas.

`T_calendar`: tiempo de reloj esperado.

`Capacity_period`: máximo de unidades que puede producir la fuente durante el periodo.

Si existe una oportunidad cada `G` horas y la probabilidad de obtener el objeto por oportunidad es `p`:

`E[T_calendar] ≈ G / p`

Esta aproximación supone oportunidades independientes, disponibilidad constante y ausencia de competencia externa.

En una implementación real también deben contemplarse:

- Cantidad de spawns.
- Sincronización.
- Horarios de disponibilidad.
- Requisitos de entrada.
- Competencia entre jugadores.
- Probabilidad de eliminar la fuente.

El sistema no debe convertir automáticamente todo el tiempo de espera en costo de mano de obra. La espera debe influir principalmente en la disponibilidad, la capacidad de reposición y la escasez.

## D.8. Escasez

Con cuatro jugadores, la escasez no puede inferirse únicamente de cuántos mobs aparecen o cuántas ventas existen.

Debe relacionarse la oferta con la necesidad prevista.

Definimos:

`D(i) = necesidad sintética del objeto durante un periodo`

`S(i) = suministro efectivo durante el mismo periodo`

`I(i) = inventario disponible`

Una primera medida de presión de disponibilidad es:

`Scarcity(i) = D(i) / max(S(i) + I(i)/T, ε)`

Donde:

- `T` es el horizonte de cobertura del inventario.
- `ε` evita divisiones por cero.

El resultado no es un precio. Es una señal de presión de disponibilidad.

La escasez debe distinguir al menos:

| Situación | Interpretación |
|---|---|
| Suministro abundante | La necesidad está cubierta. |
| Suministro limitado | Puede faltar en determinados momentos. |
| Suministro insuficiente | La necesidad supera la capacidad del sistema. |
| Fuente bloqueada | Existe una fuente, pero no es accesible para los perfiles actuales. |
| Fuente temporal | Existe, pero depende de un time gate. |
| Sin fuente confirmada | No se puede afirmar que el objeto sea obtenible. |

Esto evita confundir un objeto raro con uno verdaderamente inaccesible.

## D.9. Utilidad y demanda sintética

Recomiendo incluir utilidad desde la primera versión, pero de manera progresiva.

No intentaría construir una inteligencia artificial que determine automáticamente qué tan valioso es cada objeto.

Comenzaría por relaciones explícitas.

Por ejemplo:

- Un arma es parte de una build.
- Una carta mejora una configuración.
- Un material permite fabricar un equipo.
- Una quest requiere un objeto.
- Un consumible se utiliza recurrentemente.
- Un objeto desbloquea una instancia.
- Una mejora permite eliminar mobs más rápido.

### Modelo de utilidad recomendado

La mejor medida conceptual sería el tiempo de progresión que un objeto permite ahorrar.

`U(i,k) = H_without(i,k) - H_with(i,k)`

Donde:

- `H_without` representa el tiempo estimado para alcanzar una meta sin el objeto.
- `H_with` representa el tiempo con el objeto.

El resultado son horas ahorradas.

Es una medida mucho más interpretable que un multiplicador arbitrario de utilidad.

Sin embargo, requiere un simulador de combate y progresión suficientemente desarrollado.

Por eso propongo dos etapas:

**Primera versión: utilidad estructural.**

Clasificar los objetos según su función, etapa, dependencia, builds compatibles y recetas.

**Segunda versión: utilidad cuantitativa.**

Calcular cuánto mejora el tiempo de progresión, la capacidad de farmeo, la supervivencia o el acceso a contenido.

### Demanda sintética

La demanda no debe representar ventas ficticias.

Debe representar necesidades previstas.

Para un objeto consumible:

`D_daily(i) = consumo_estimado_por_hora × horas_activas_diarias`

Para un objeto de equipo:

`D_stage(i) = cantidad_necesaria_por_personaje × cantidad_de_progresiones_previstas`

Para un material:

`D(i) = Σ [cantidad_requerida_en_recetas × frecuencia_objetivo_de_fabricación]`

La necesidad de equipo debe calcularse sobre una población objetivo de progresión, no simplemente multiplicando por cuatro.

Los cuatro jugadores pueden tener clases, builds y objetivos diferentes.

La demanda sintética debe permitir expresar:

- Necesidad inmediata.
- Necesidad futura.
- Necesidad recurrente.
- Necesidad específica de una build.
- Necesidad opcional.
- Necesidad de colección.

El sistema debe guardar siempre que esta demanda es sintética, no observada.

## D.10. Unidad económica: zeny por hora estándar

Este es uno de los parámetros más importantes del modelo.

Definimos:

`Z_h = valor económico de una hora estándar de juego`

Unidad: zeny/hora.

Su función es convertir esfuerzo en valor económico.

Por ejemplo, si:

`Z_h = 10.000 zeny/hora`

Entonces una actividad que requiere una hora estándar de esfuerzo tiene un costo económico base de 10.000 zeny.

No estoy proponiendo 10.000 como valor definitivo. Es un número ilustrativo.

El valor real debe calibrarse mediante objetivos de progresión.

### Cómo calibrarlo

Se deben seleccionar varios hitos:

| Hito | Decisión necesaria |
|---|---|
| Primer equipo funcional | Horas objetivo para conseguirlo |
| Equipo intermedio | Horas objetivo para completarlo |
| Mejora importante | Horas objetivo de adquisición |
| Equipo avanzado | Horas objetivo de preparación |
| Acceso a contenido avanzado | Tiempo objetivo de preparación |

Para cada hito se define un presupuesto económico esperado.

La relación entre el presupuesto y el tiempo deseado permite establecer valores de referencia.

La calibración debe comprobarse también contra el ingreso esperado por actividades comunes.

El objetivo es que la economía no produzca una contradicción como esta:

- Un objeto debería requerir tres horas de progresión.
- Pero el modelo asigna un precio equivalente a veinte horas.
- El NPC lo vende a veinte horas de esfuerzo.
- El jugador termina dedicando su tiempo a una actividad económica que no corresponde con la progresión que se quería ofrecer.

`Z_h` debe funcionar como parámetro de diseño global y no como un valor que cada objeto pueda alterar individualmente.

## D.11. Costo de adquisición y valor de referencia

Recomiendo separar tres magnitudes:

### 1. `replacement_cost`

Cuánto cuesta conseguir nuevamente un objeto por una ruta reproducible.

Incluye:

- Recursos.
- Zeny.
- Tiempo activo.
- Probabilidad de éxito.
- Pérdidas por fallos.
- Restricciones de acceso.

### 2. `reference_value`

Valor económico estimado del objeto en el sistema.

Integra el costo de adquisición y los límites de progresión.

### 3. `npc_quote`

Precio concreto que un NPC ofrece para comprar o vender.

Depende del valor de referencia, el inventario, el presupuesto, el spread y las políticas del NPC.

No deben almacenarse como si fueran el mismo dato.

## D.12. Fórmula recomendada para el valor de referencia

La propuesta más práctica es utilizar las horas de adquisición como ancla y los objetivos de progresión como límite.

Definimos:

`H_acq(i) = horas activas esperadas de adquisición para el perfil de referencia`

`H_min(i) = límite inferior de horas asignado a su categoría y etapa`

`H_max(i) = límite superior de horas asignado a su categoría y etapa`

Entonces:

`H_price(i) = clamp(H_acq(i), H_min(i), H_max(i))`

Y:

`P_mid(i) = Z_h × H_price(i)`

Esta es la fórmula central recomendada.

### ¿Qué consigue?

- Un objeto fácil de conseguir no recibe automáticamente un precio absurdo.
- Un objeto extraordinariamente raro no se vuelve necesariamente inaccesible.
- Los objetos de progresión crítica pueden tener un límite superior de adquisición.
- Los objetos opcionales o de colección pueden tener políticas menos restrictivas.
- El sistema no necesita un multiplicador arbitrario de rareza.
- Los objetivos de progresión influyen en el valor de manera explícita.

Los límites `H_min` y `H_max` son decisiones de diseño. Deben definirse por etapa y función, no inventarse para cada objeto individual.

### Excepciones

Si un objeto no tiene una ruta confirmada:

`H_acq(i) = null`

No se debe inventar un costo de adquisición.

Si el equipo decide que debe existir en el mercado sintético, se crea una ruta artificial explícita:

`route_type = virtual_market_supply`

Esa ruta debe tener su propio origen, capacidad, política y costo de reposición.

No debe confundirse con una fuente real del juego.

## D.13. Cómo utilizar los precios históricos externos

Los registros LATAM y Atlantis son útiles, pero no representan el mercado de OzRo.

Recomiendo utilizarlos para:

- Comparar relaciones de precios.
- Detectar objetos que aparecen sistemáticamente fuera de orden.
- Comprobar si determinados materiales suelen tener más valor que otros.
- Detectar diferencias sospechosas entre variantes de un objeto.
- Identificar grupos de objetos que comparten una jerarquía económica.

No deberían determinar directamente los precios de OzRo porque pueden existir diferencias en:

- Rates.
- Población.
- Disponibilidad.
- Progresión.
- Demanda.
- Inflación.
- Versiones.
- Comportamiento de los servidores.

Para aprovecharlos sin convertirlos en verdad, puede utilizarse una combinación logarítmica:

`ln(P_final) = (1-w) × ln(P_internal) + w × ln(P_external_normalized)`

Donde `w` representa la confianza otorgada a la referencia externa.

Mi recomendación es:

- Primera versión: `w = 0`; los precios externos sirven para validación.
- Versión posterior: permitir una ponderación pequeña y configurable cuando exista suficiente comparabilidad.
- Nunca permitir que una referencia externa de baja calidad domine el precio interno.

---

# D.13.1. Ejemplos numéricos

Los siguientes ejemplos son ilustrativos. Sus parámetros no representan valores medidos de OzRo.

Para los tres ejemplos utilizaremos:

`Z_h = 10.000 zeny/hora`

## Ejemplo 1. Farm común

Supongamos:

- Un perfil elimina 30 mobs por hora.
- El objeto tiene una probabilidad efectiva de drop del 5%.
- Cada éxito entrega una unidad.

Entonces:

`S = 30 × 0,05 = 1,5 unidades/hora`

Las horas esperadas por unidad son:

`H_acq = 1 / 1,5 = 0,667 horas`

Costo de adquisición equivalente:

`C = 0,667 × 10.000 = 6.670 zeny`

Si los límites de progresión no modifican ese resultado, el valor de referencia será aproximadamente 6.670 zeny.

Esto no significa que todos los objetos de ese mob deban recibir ese costo completo. Si el mob entrega muchos objetos, el costo de la actividad debe distribuirse correctamente entre los resultados conjuntos.

## Ejemplo 2. Proceso destructivo

Supongamos una mejora con:

- Probabilidad de éxito: 5%.
- Un objeto base de 10.000 zeny.
- Tres materiales de 1.000 zeny cada uno.
- Una tarifa de 2.000 zeny.
- Dos minutos de trabajo por intento.
- Todos los recursos se consumen tanto si el intento tiene éxito como si falla.

El costo de recursos por intento es:

`C_resources = 10.000 + 3.000 + 2.000`

`C_resources = 15.000 zeny`

El valor del tiempo por intento es:

`C_time = 10.000 × (2/60)`

`C_time = 333 zeny`

Costo total por intento:

`C_attempt = 15.333 zeny`

Número esperado de intentos:

`E[N] = 1 / 0,05 = 20`

Costo esperado:

`C_expected = 15.333 × 20`

`C_expected ≈ 306.660 zeny`

La ruta de mejora tiene un costo económico esperado cercano a 306.660 zeny.

Si el proceso conserva algunos materiales cuando falla, la fórmula debe ajustarse utilizando los costos condicionales de éxito y fallo.

## Ejemplo 3. MVP con time gate

Supongamos:

- Un único spawn compartido.
- Un respawn efectivo cada 60 minutos.
- Cinco minutos para eliminar el MVP.
- Probabilidad de obtener el objeto: 10%.
- Una unidad por éxito.

La cantidad máxima de oportunidades es aproximadamente una por hora.

El suministro esperado es:

`S = 1 × 0,10 = 0,1 unidades/hora de reloj`

El tiempo esperado hasta obtener el objeto es:

`T_calendar = 1 / 0,1 = 10 horas`

El tiempo activo esperado es:

`H_active = 5 minutos × 10 intentos`

`H_active = 50 minutos`

Por tanto:

- Tiempo activo esperado: 0,833 horas.
- Tiempo de reloj esperado: aproximadamente 10 horas.
- Suministro esperado: 0,1 unidades por hora de reloj.

Con cuatro jugadores compartiendo el mismo spawn, el suministro no se convierte automáticamente en 0,4 unidades por hora.

Este ejemplo demuestra por qué el modelo debe separar el esfuerzo del jugador de la capacidad real de la fuente.

---

# E. Composición del sistema económico

Una vez calculados los parámetros, se deben construir las salidas económicas.

Recomiendo mantener dos niveles:

1. Valoración de objetos.
2. Política económica de los NPCs.

El primero describe el valor y sus fundamentos. El segundo decide qué operaciones permite el sistema.

## E.1. Motor de valoración

Por cada objeto debería generarse:

- Estado de adquisición.
- Rutas disponibles.
- Costo esperado por ruta.
- Horas activas de adquisición.
- Tiempo de reloj.
- Oferta estimada.
- Utilidad.
- Necesidad sintética.
- Precio de referencia.
- Intervalo de incertidumbre.
- Confianza.
- Evidencia.

El resultado no tiene que ser siempre un precio.

Propongo cuatro estados:

| Estado | Significado |
|---|---|
| `priced` | Hay información suficiente para producir una valoración. |
| `estimated` | Existe una valoración, pero depende de inferencias o supuestos. |
| `indicative_cost` | Se conoce un costo de adquisición, pero no existe una política de mercado definida. |
| `unpriced` | No hay evidencia suficiente ni ruta sintética aprobada. |

Esto evita presentar todos los valores como si tuvieran la misma fiabilidad.

## E.2. Dos alternativas de composición

### Alternativa A: modelo basado principalmente en adquisición

El precio nace del esfuerzo necesario para conseguir el objeto.

`P_mid = Z_h × H_price`

La utilidad se utiliza principalmente para determinar qué objetos deben estar disponibles y cuáles pueden limitarse.

**Ventajas:**

- Simple.
- Explicable.
- Relativamente fácil de implementar.
- Depende de datos del servidor.
- No requiere una simulación compleja de builds.

**Desventajas:**

- Un objeto extremadamente raro pero poco útil podría recibir mucho valor.
- Un objeto esencial podría terminar costando demasiado.
- No garantiza por sí solo una progresión coherente.

Esta alternativa es adecuada para construir una primera valoración funcional.

### Alternativa B: modelo basado en adquisición y progresión

Utiliza el costo de adquisición como ancla, pero establece límites de precio según la función y la etapa del objeto.

`P_mid = Z_h × clamp(H_acq, H_min(role,tier), H_max(role,tier))`

La categoría y la etapa determinan los límites.

Un objeto de progresión esencial puede tener un máximo de adquisición menor que un objeto de colección o una mejora opcional.

**Ventajas:**

- Mantiene el vínculo con el mundo real del servidor.
- Permite controlar el ritmo de progresión.
- Evita que algunos objetos bloqueen el avance por azar.
- No necesita convertir la rareza en una prima ilimitada.
- Permite establecer políticas distintas por categoría.

**Desventajas:**

- Requiere objetivos de progresión.
- Necesita una clasificación de utilidad.
- Algunos objetos requerirán revisión manual.
- Puede generar subsidios económicos cuando el NPC suministra algo por debajo de su costo real de adquisición.

### Recomendación

Adoptaría la alternativa B como arquitectura definitiva.

La alternativa A sería el primer estado operativo mientras se completa la clasificación de utilidad y se definen los hitos de progresión.

No recomiendo un modelo puramente estadístico ni una multiplicación general de costo, rareza, dificultad, demanda y utilidad.

## E.3. El mercado NPC

El mercado sintético debe tener una contabilidad compartida.

No recomiendo implementar un NPC comprador, un NPC vendedor y un tasador como tres sistemas separados que calculan valores de manera independiente.

Pueden existir varios NPCs con interfaces y funciones diferentes, pero todos deben consultar el mismo motor económico.

### NPC 1. Tasador

Responsabilidad:

- Mostrar valor de referencia.
- Explicar rutas de adquisición.
- Mostrar dificultad estimada.
- Mostrar utilidad conocida.
- Indicar incertidumbre.
- Explicar por qué un objeto tiene ese valor.

No debería crear ni destruir dinero.

Es un servicio informativo.

### NPC 2. Comprador

Responsabilidad:

- Comprar objetos de los jugadores.
- Proporcionar liquidez.
- Mantener inventarios objetivo.
- Controlar su presupuesto.
- Aplicar restricciones por objeto.

No debe comprar todo ilimitadamente.

Debe evaluar:

- Precio de referencia.
- Inventario actual.
- Inventario objetivo.
- Necesidad sintética.
- Capacidad de reposición.
- Presupuesto disponible.
- Restricciones de transferencia.

### NPC 3. Vendedor

Responsabilidad:

- Suministrar objetos.
- Mantener inventarios controlados.
- Cubrir necesidades importantes.
- Proporcionar rutas alternativas de adquisición.
- Aplicar disponibilidad por etapa.

No todos los objetos deben estar siempre disponibles.

### NPC 4. Intercambiador

Recomiendo incorporar esta función, aunque inicialmente pueda estar implementada en el mismo NPC comprador.

Su propósito es permitir convertir el valor de objetos innecesarios en objetos que el jugador sí necesita.

Este es uno de los mecanismos más importantes para conseguir la experiencia que busca OzRo.

## E.4. ¿Zeny o créditos de intercambio?

Aquí propongo una decisión adicional.

La economía debe distinguir entre el mercado de zeny y la función de intercambio de objetos.

Si el NPC compra todos los drops pagando zeny, se convierte en una fuente de emisión monetaria.

Cuanto más farmeen los jugadores, más zeny puede ingresar a la economía.

Esto puede generar inflación y hacer que los precios pierdan coherencia.

### Recomendación: sistema de dos saldos

**A. Zeny**

Se utiliza para:

- Compras normales.
- Servicios.
- Tarifas.
- Consumo.
- NPCs tradicionales.
- Operaciones que deban afectar la economía monetaria.

**B. Créditos de intercambio**

Se utilizan para:

- Vender objetos al mercado sintético.
- Acceder a objetos del catálogo de intercambio.
- Convertir excedentes en progreso.
- Resolver problemas de liquidez.

Los créditos deben ser:

- No transferibles entre jugadores.
- No convertibles directamente a zeny.
- Utilizables únicamente en servicios autorizados.
- Emitidos mediante operaciones registradas.
- Gastados al adquirir objetos.

Esto permite que un jugador venda un drop valioso que no necesita y acumule valor para conseguir otra cosa, sin que el proceso tenga que crear zeny.

No recomiendo permitir que los créditos sean convertibles libremente a dinero, porque eso volvería a introducir el problema monetario.

### Alternativa sin créditos

También es posible implementar todo en zeny.

En ese caso, el NPC comprador debe tener un presupuesto real, límites de compra, control de emisión y registro de zeny generado.

Es más sencillo desde el punto de vista de interfaz, pero más difícil de equilibrar.

Para el objetivo de OzRo, recomiendo el modelo híbrido.

## E.5. Precio de compra y venta

Todos los NPCs deben utilizar el mismo precio medio.

Definimos:

`P_mid(i) = valor central actualizado del objeto`

El spread se aplica sobre ese valor.

`P_buy(i) = P_mid(i) × (1 - spread/2)`

`P_sell(i) = P_mid(i) × (1 + spread/2)`

Donde `spread` representa la diferencia relativa entre compra y venta.

Por ejemplo, con un spread del 20%:

- Compra NPC: 90% del valor medio.
- Venta NPC: 110% del valor medio.

El 20% es ilustrativo; el spread definitivo debe calibrarse mediante simulación.

### ¿Por qué aplicar spread?

Porque el sistema debe cubrir:

- Costos de operación.
- Riesgo de inventario.
- Disponibilidad.
- Incertidumbre.
- Servicio de liquidez.
- Diferencia entre vender inmediatamente y comprar bajo demanda.

No lo utilizaría como una penalización arbitraria.

El spread debe ser un parámetro configurable por categoría o servicio.

## E.6. Ajuste por inventario

El inventario debe afectar las cotizaciones.

Un NPC con exceso de un objeto tiene menos incentivo para seguir comprándolo.

Un NPC con poco inventario puede ofrecer mejores condiciones para recuperarlo.

Definimos:

`stock_ratio(i) = current_stock(i) / target_stock(i)`

Una función sencilla para ajustar el precio central es:

`M_stock = clamp(exp(k × (1 - stock_ratio)), M_min, M_max)`

Entonces:

`P_dynamic = P_mid × M_stock`

Donde `k` controla la sensibilidad al inventario.

Esta fórmula es una propuesta de política, no una ley de mercado.

Debe calibrarse para que el ajuste sea moderado y no produzca oscilaciones violentas.

En la primera versión se puede utilizar una política más sencilla por bandas:

| Inventario | Política |
|---|---|
| Muy bajo | Alta prioridad de reposición |
| Bajo | Compra incentivada |
| Normal | Condiciones estándar |
| Alto | Compra reducida |
| Excedente | Suspensión temporal de compra |

La política por bandas es más fácil de depurar y recomiendo comenzar con ella.

## E.7. Inventario sintético y reposición

Esta es la parte que permite emular la presencia de otros jugadores.

El vendedor no depende exclusivamente de lo que los cuatro usuarios hayan vendido.

El mercado tendrá dos fuentes de inventario:

1. Inventario recibido de los jugadores.
2. Inventario sintético que representa la actividad de una población externa simulada.

El segundo debe registrarse explícitamente como oferta artificial.

No debe aparecer como si hubiera sido generado por un mob o una receta real.

La reposición sintética puede calcularse mediante:

`VirtualRestock(i) = max(0, D_target(i) - S_players(i))`

Donde:

- `D_target` es la necesidad objetivo del mercado.
- `S_players` es el suministro que producen los jugadores reales.

La reposición debe limitarse por:

- Máximo de unidades por periodo.
- Inventario máximo.
- Categoría del objeto.
- Etapa de progresión.
- Política de acceso.
- Existencia de una ruta autorizada.

Si se permite que el mercado suministre un objeto sin una fuente real, debe registrarse como una decisión explícita de diseño.

No recomiendo convertir automáticamente cualquier objeto sin fuente identificada en un objeto de venta NPC.

## E.8. Política de disponibilidad por categoría

Propongo estas categorías iniciales:

| Categoría | Comportamiento recomendado |
|---|---|
| Esenciales de progresión | Disponibilidad controlada y precio limitado por etapa. |
| Consumibles comunes | Alta disponibilidad y reposición frecuente. |
| Materiales de craft | Disponibilidad según necesidades de recetas. |
| Equipo intermedio | Inventario limitado o reposición periódica. |
| Equipo avanzado | Reposición lenta y precio elevado, según progresión. |
| MVP y boss items | Disponibilidad limitada, no necesariamente permanente. |
| Cartas raras | Disponibilidad selectiva, con límites estrictos. |
| Coleccionables | Inventario bajo o rotativo. |
| Legacy y eventos | Solo si existe una política explícita de incorporación. |
| Sin fuente confirmada | Sin precio y sin suministro automático. |

Esto evita el problema de convertir el NPC vendedor en una tienda que sustituye por completo el juego.

## E.9. Evitar arbitraje

El sistema debe prevenir operaciones que permitan generar valor simplemente comprando y vendiendo objetos entre NPCs.

Propongo las siguientes reglas:

1. Todos los NPCs usan un mismo libro de precios.
2. Siempre se cumple `P_sell > P_buy`.
3. Todos los intercambios utilizan las mismas valoraciones centrales.
4. No existe conversión directa de créditos a zeny.
5. Las recetas se valoran considerando materiales, tarifas y probabilidades reales.
6. Los objetos ligados o restringidos respetan su política de transferencia.
7. El inventario y el presupuesto se actualizan después de cada transacción.
8. Las operaciones están sujetas a límites y auditoría.
9. No se permite que una secuencia de conversiones termine con más valor del que tenía al inicio.

Además, implementaría una prueba automática de ciclos de arbitraje.

El sistema debe construir un grafo de conversiones:

`Objeto A → Zeny → Objeto B → Objeto C → Objeto A`

Se simulan todos los ciclos relevantes y se verifica que ninguna ruta produzca beneficio positivo garantizado.

El spread debe actuar en todas las rutas de intercambio, no solamente en las operaciones de compra y venta más visibles.

---

# F. Validación y modos de fallo

Como no existe un mercado observado, no se puede validar el modelo buscando que sus precios coincidan con una realidad que no existe.

La validación debe demostrar que la economía se comporta de manera coherente.

## F.1. Invariantes

Estos son los comportamientos que el sistema debe cumplir siempre.

| Invariante | Condición |
|---|---|
| Probabilidad | Una probabilidad efectiva debe estar entre 0 y 1. |
| Suministro | Un suministro no puede ser negativo. |
| Inventario | El inventario nunca puede ser negativo. |
| Presupuesto | El presupuesto de un NPC no puede ser negativo. |
| Compra y venta | El precio de venta debe ser superior al de compra. |
| Fuente | Un objeto sin fuente confirmada no debe aparecer como obtenible real. |
| Restricciones | Los NPCs respetan los canales de transferencia autorizados. |
| Recetas | Las pérdidas por fallo deben formar parte del costo esperado. |
| Progresión | Un objeto esencial no debe quedar bloqueado por una ruta imposible sin alternativa declarada. |
| Emisión monetaria | Toda creación o destrucción de zeny debe quedar registrada. |
| Créditos | Todo crédito emitido debe tener una operación de origen. |
| Procedencia | Todo valor debe poder rastrearse hasta sus datos o decisiones. |

## F.2. Pruebas de monotonía

Las pruebas deben comprobar que el modelo responde correctamente ante cambios controlados.

Por ejemplo:

| Cambio | Resultado esperado |
|---|---|
| Aumenta la probabilidad de drop | Baja o se mantiene el costo de adquisición. |
| Aumenta el número de spawns | Aumenta o se mantiene el suministro. |
| Disminuye el respawn | Aumenta o se mantiene la disponibilidad. |
| Mejora la capacidad del jugador | Disminuyen o se mantienen las horas de adquisición. |
| Aumenta el costo de materiales | Aumenta o se mantiene el costo de craft. |
| Disminuye la probabilidad de éxito | Aumenta o se mantiene el costo esperado. |
| Aumenta la necesidad y no la oferta | Aumenta la presión de disponibilidad. |
| Aumenta el inventario NPC | Disminuye o se mantiene la presión de reposición. |

La monotonía debe aplicarse a las variables donde exista una relación causal clara.

No hay que exigir que todos los precios aumenten siempre con la rareza: un objeto raro puede tener muy poca utilidad.

## F.3. Simulación de progresión

Este debería ser uno de los principales métodos de validación.

Se simulan perfiles de jugadores que recorren diferentes etapas.

Para cada perfil se registra:

- Tiempo de adquisición de equipo.
- Tiempo para fabricar mejoras.
- Tiempo necesario para preparar consumibles.
- Zeny generado.
- Zeny gastado.
- Créditos obtenidos.
- Créditos utilizados.
- Cantidad de objetos suministrados por NPC.
- Cantidad de objetos obtenidos mediante farmeo.
- Número de bloqueos de progresión.
- Actividades más rentables.

El objetivo es comprobar que la economía permite completar una progresión razonable y que no existen actividades desproporcionadamente rentables.

## F.4. Métricas económicas

| Métrica | Qué permite detectar |
|---|---|
| `zeny_emission_per_hour` | Emisión de zeny por hora de juego. |
| `zeny_sink_per_hour` | Destrucción de zeny por tarifas y compras. |
| `net_zeny_flow` | Diferencia entre emisión y destrucción. |
| `progression_hours_by_tier` | Tiempo de avance por etapa. |
| `npc_fill_rate` | Porcentaje de necesidades cubiertas por NPCs. |
| `stockout_rate` | Frecuencia de agotamiento de inventario. |
| `virtual_supply_share` | Cuánto suministro proviene del mercado sintético. |
| `farming_profitability` | Rentabilidad de cada actividad. |
| `market_credit_issuance` | Créditos emitidos. |
| `market_credit_balance` | Créditos acumulados y no utilizados. |
| `arbitrage_gain` | Beneficio máximo de ciclos de conversión. |
| `progression_block_rate` | Frecuencia de situaciones que impiden avanzar. |

## F.5. Pruebas de estrés

Recomiendo simular los siguientes escenarios:

- Rates actuales.
- Rates reducidos a la mitad.
- Rates duplicados.
- Reducción de spawns.
- Aumento de respawn.
- Un jugador avanzado y tres iniciales.
- Cuatro jugadores con capacidades similares.
- Cuatro jugadores con perfiles especializados.
- Una actividad que concentra toda la rentabilidad.
- Caída temporal de una fuente importante.
- Aumento de demanda de materiales.
- Inventario NPC agotado.
- Presupuesto de compra agotado.
- Desactivación de una fuente de objetos.
- Aparición de una nueva ruta de craft.

La economía debe ser estable ante variaciones razonables, no solamente bajo los valores actuales.

## F.6. Incertidumbre

Recomiendo que el sistema produzca rangos en lugar de fingir precisión absoluta.

Para cada objeto:

- `P10`
- `P50`
- `P90`

Representan los percentiles de la distribución de valoración.

La distribución puede calcularse mediante Monte Carlo, muestreando variables inciertas:

- Kill time.
- Probabilidad efectiva.
- Actividad disponible.
- Capacidad de spawn.
- Costos de recetas.
- Parámetros de utilidad.
- Reposición sintética.

La simulación puede ser no determinista, como permite el brief, pero cada corrida debe conservar:

- Semilla aleatoria.
- Versión del modelo.
- Versión de datos.
- Parámetros.
- Resultados.
- Fecha.
- Evidencias utilizadas.

Una corrida no determinista es auditable siempre que sus entradas y resultados se conserven.

## F.7. Auditoría de cada objeto

El sistema debe poder responder preguntas como:

- ¿Por qué este objeto tiene este valor?
- ¿Qué fuente lo produce?
- ¿Cuántas unidades se esperan por hora?
- ¿Qué perfil puede conseguirlo?
- ¿Qué ruta es la más eficiente?
- ¿Qué utilidad tiene?
- ¿Qué precio histórico se utilizó como contraste?
- ¿Qué límite de progresión se aplicó?
- ¿Qué política NPC determinó su precio final?
- ¿Qué parte de su suministro es real y qué parte sintética?

Esta explicación debe formar parte de la salida del sistema, no ser una tarea manual de investigación.

---

# G. Fases de implementación

No construiría todos los componentes simultáneamente.

El orden recomendado reduce el riesgo de implementar una fórmula sofisticada sobre datos incorrectos.

## Fase 0. Integridad y normalización de datos

**Objetivo:** tener una representación confiable del servidor.

Tareas:

- Normalizar `item_db`.
- Normalizar `mob_db`.
- Verificar los rates efectivos.
- Revisar los scripts de spawns.
- Identificar rutas de adquisición.
- Verificar recetas.
- Separar restricciones de adquisición y transferencia.
- Asignar procedencia a los datos.
- Validar una muestra de objetos directamente en el servidor.

**Resultado:** modelo de mundo confiable.

No se deben asignar todavía precios definitivos.

## Fase 1. Modelo de adquisición

**Objetivo:** calcular cuánto esfuerzo requiere obtener un objeto.

Tareas:

- Crear perfiles de jugadores.
- Calcular kill times.
- Calcular accesibilidad.
- Procesar drops efectivos.
- Calcular capacidad de spawns.
- Construir rutas de adquisición.
- Modelar recetas.
- Modelar procesos destructivos.
- Separar tiempo activo y tiempo de reloj.
- Calcular costos de adquisición por perfil.

**Resultado:** catálogo de adquisición.

Esta fase ya permite identificar objetos difíciles, rutas problemáticas y fuentes desproporcionadas.

## Fase 2. Unidad económica y progresión

**Objetivo:** convertir las magnitudes de adquisición en una economía funcional.

Tareas:

- Definir `Z_h`.
- Definir etapas de progresión.
- Clasificar objetos por utilidad.
- Identificar equipo esencial.
- Construir relaciones de builds.
- Establecer límites de adquisición por categoría.
- Definir objetivos de tiempo por etapa.
- Generar valores de referencia.

**Resultado:** primera versión del motor de valoración.

## Fase 3. Mercado sintético

**Objetivo:** reproducir las funciones de liquidez y suministro.

Tareas:

- Crear inventario compartido.
- Crear presupuesto.
- Definir NPC comprador.
- Definir NPC vendedor.
- Definir spreads.
- Crear reposición sintética.
- Crear restricciones y límites.
- Evaluar el sistema de créditos de intercambio.
- Implementar pruebas de arbitraje.

**Resultado:** MarketSimulator funcional.

## Fase 4. Simulación y validación

**Objetivo:** comprobar que la economía cumple los objetivos de diseño.

Tareas:

- Simular perfiles.
- Simular progresión.
- Calcular rentabilidad.
- Medir emisión de zeny.
- Medir cobertura de inventario.
- Evaluar stockouts.
- Ejecutar pruebas de estrés.
- Calcular intervalos de incertidumbre.
- Ajustar parámetros globales.

**Resultado:** economía calibrada y auditable.

## Fase 5. Enriquecimiento semántico

**Objetivo:** mejorar la comprensión de objetos y mecánicas.

Tareas:

- Interpretar scripts de quests.
- Detectar requisitos ocultos.
- Identificar sinergias entre objetos.
- Extraer utilidad desde descripciones.
- Identificar relaciones entre builds.
- Revisar eventos y fuentes especiales.
- Incorporar análisis asistido por LLM.

**Resultado:** modelo de utilidad más completo.

No recomiendo retrasar todo el proyecto hasta completar esta fase.

---

# H. Supuestos y riesgos

## H.1. Supuestos necesarios

La solución propuesta depende de estas condiciones:

1. Los datos de mobs, drops y spawns pueden verificarse y normalizarse.
2. Es posible construir perfiles representativos de los cuatro jugadores.
3. El equipo está dispuesto a definir objetivos de progresión.
4. Se puede establecer un valor global de zeny por hora estándar.
5. El mercado sintético puede mantener inventarios y presupuestos persistentes.
6. Las operaciones de los NPCs pueden quedar registradas.
7. Se acepta que ciertos objetos tengan suministro artificial declarado.
8. Se acepta diferenciar valor de referencia, costo de adquisición y precio transaccional.

Si alguno de estos supuestos no se cumple, el modelo deberá reducir su alcance.

## H.2. Riesgos que no se pueden resolver únicamente con fórmulas

Hay decisiones que no pueden deducirse de `item_db`, `mob_db` o los históricos externos.

Por ejemplo:

- Cuánto debería tardar un jugador en conseguir su primera arma importante.
- Cuánto debe costar un objeto que desbloquea una nueva etapa.
- Qué porcentaje de objetos raros debería estar disponible en el NPC.
- Cuánto debe premiar el sistema a quien consigue un drop excepcional.
- Cuánto debe facilitarse la progresión a un jugador que ha tenido mala suerte.

Son decisiones sobre la experiencia de juego.

El modelo puede hacerlas explícitas, medir sus consecuencias y ayudar a calibrarlas. No puede descubrir una única respuesta objetivamente correcta.

## H.3. Qué no haría

No recomiendo:

- Asignar precios mediante un único multiplicador general.
- Usar el precio histórico externo como precio base definitivo.
- Interpretar la ausencia de una fuente parseada como imposibilidad de adquisición.
- Tratar la rareza como sinónimo de utilidad.
- Contar el tiempo de espera de un MVP como tiempo activo de farmeo.
- Ignorar la capacidad real de los spawns.
- Crear un NPC comprador con presupuesto infinito.
- Crear un NPC vendedor con inventario ilimitado.
- Permitir que cada NPC calcule sus propios precios.
- Usar un LLM para asignar precios finales a miles de objetos.
- Crear una economía completamente basada en zeny sin controlar la emisión.
- Exigir una simulación perfecta antes de poner en funcionamiento una primera versión.

---

# 2. Contrato de salida recomendado

El motor debe generar una estructura unificada por objeto.

Un ejemplo conceptual:

```json
{
  "item_id": 1201,
  "economic_status": "priced",

  "acquisition": {
    "status": "obtainable",
    "routes": [
      {
        "route_id": "farm_1010",
        "source_type": "mob",
        "source_id": 1010,
        "expected_drop": 0.05,
        "active_hours_p50": 0.67,
        "calendar_hours_p50": 0.67,
        "confidence": 0.92
      }
    ],
    "replacement_cost_zeny": 6670
  },

  "utility": {
    "roles": [
      "progression",
      "combat"
    ],
    "progression_tier": "early",
    "utility_status": "structural",
    "utility_score": null
  },

  "market": {
    "synthetic_demand": 10,
    "effective_supply": 12,
    "scarcity_status": "normal",
    "virtual_supply_enabled": true
  },

  "valuation": {
    "reference_price": 6670,
    "p10": null,
    "p50": 6670,
    "p90": null,
    "confidence": 0.86,
    "method": "acquisition_progression"
  },

  "npc_policy": {
    "buyer_enabled": true,
    "seller_enabled": true,
    "bid_price": null,
    "ask_price": null,
    "inventory_target": 20,
    "restock_rate": 5
  },

  "provenance": {
    "model_version": "1.0.0",
    "input_snapshot": "example_hash",
    "run_id": "example_run"
  }
}
```

Los valores son ilustrativos. El contrato real debe incluir los parámetros necesarios para cada objeto, sin exigir que todos tengan información en todos los campos.

La separación entre `acquisition`, `utility`, `market`, `valuation` y `npc_policy` evita que una modificación de política económica obligue a recalcular el modelo de adquisición.

---

# 3. Decisiones que cerraría para la primera versión

Para evitar que la arquitectura siga creciendo sin llegar a una implementación, recomiendo cerrar las siguientes decisiones.

| Decisión | Propuesta definitiva |
|---|---|
| Arquitectura | Modular, por capas, con un modelo de datos compartido. |
| Unidad de esfuerzo | Hora estándar de juego. |
| Conversión económica | `Z_h`, calibrado con objetivos de progresión. |
| Perfiles | Cuatro perfiles configurables, preferiblemente basados en los personajes reales. |
| Dificultad | Capacidad de farmeo por perfil y mob, no nivel aislado. |
| Suministro | Probabilidad efectiva por kill, capacidad del spawn y horas disponibles. |
| Rutas | Se conservan todas; se calcula la ruta más eficiente por perfil. |
| Time gates | Se separan del tiempo activo. |
| Procesos destructivos | Costo esperado por probabilidad y consumo en éxito/fallo. |
| Escasez | Relación entre necesidad sintética, suministro e inventario. |
| Utilidad | Clasificación estructural desde V1 y utilidad cuantitativa después. |
| Demanda | Derivada de progresión, builds, recetas y consumo. |
| Precio base | Costo de adquisición limitado por objetivos de progresión. |
| Histórico externo | Validación y contraste; no ancla principal. |
| NPCs | Comprador, vendedor, tasador e intercambiador, con motor común. |
| Mercado | Inventario y presupuesto compartidos. |
| Liquidez | Créditos de intercambio no convertibles a zeny, más operaciones normales en zeny. |
| Oferta artificial | Explícita, limitada y auditable. |
| Incertidumbre | P10/P50/P90 y confianza. |
| LLM | Extracción de información estructurada, no generación de precios. |
| Validación | Progresión, rentabilidad, inventarios, inflación y arbitraje. |

---

# 4. Conclusión

La economía de OzRo debe entenderse como una simulación de las funciones de un mercado, no como una estimación de precios de un mercado inexistente.

La solución más consistente es un modelo híbrido:

1. **El mundo del servidor define qué puede obtenerse y cómo.**
2. **El modelo de adquisición estima cuánto esfuerzo cuesta conseguirlo.**
3. **El modelo de utilidad identifica qué necesita la progresión y por qué.**
4. **La economía establece cuánto debería representar ese esfuerzo en zeny y en valor de intercambio.**
5. **Los NPCs administran la liquidez y el suministro mediante inventarios, presupuestos y políticas controladas.**
6. **El simulador comprueba que el resultado produce una experiencia de juego razonable.**

La distinción más importante es que el mercado sintético no tiene que reproducir exactamente los precios de un servidor poblado. Tiene que reproducir sus beneficios funcionales: disponibilidad, redistribución, progresión y liquidez.

Un jugador debería poder conseguir algo valioso, aunque no sea el objeto que buscaba, y transformar ese resultado en progreso.

Un jugador tampoco debería quedar bloqueado durante semanas por una mala secuencia de drops cuando existe una alternativa económica razonable.

Pero esa flexibilidad no debe eliminar el valor de jugar, farmear, fabricar y explorar.

**La meta no es hacer que todos los objetos sean fáciles de conseguir. Es hacer que conseguirlos sea una decisión de progresión y no una dependencia absoluta del azar.**

Ese es el criterio que debería guiar todas las fórmulas, los parámetros y las políticas de los NPCs.