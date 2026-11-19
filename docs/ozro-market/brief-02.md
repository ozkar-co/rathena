# Brief 02 — Economía sintética de OzRo


---

## 1. Contexto

OzRo es un servidor privado de Ragnarok Online, rAthena Renewal, con rates
custom. Lo juegan aproximadamente **cuatro personas**, en modo principalmente
offline/cooperativo.

No existe una población suficiente para formar un mercado orgánico: no hay
price discovery, no hay liquidez, no hay demanda observada y no se espera que
aparezca. El NPC o los NPCs deben suplir las funciones económicas que
normalmente cumpliría una comunidad.

La lógica MMO habitual es: aunque un objeto sea improbable, con suficientes
jugadores a alguien le termina tocando, y el mercado lo redistribuye. Con cuatro
jugadores ese componente estadístico desaparece. La economía sintética debe
emular ese efecto.

El objetivo del proyecto tiene dos caras:

1. **Liquidez para lo que sale.** Un objeto raro o valioso que un jugador
   obtiene no debe terminar en la basura por no haber comprador. Debe poder
   convertirse en valor y, eventualmente, en el objeto que el jugador necesita.
2. **Suministro para lo que se necesita.** Un objeto raro o difícil no debe
   quedar limitado a la suerte o al grindeo personal por no haber quien lo
   provea. Debe existir una ruta razonable para adquirirlo.

Un drop raro que no es el que el jugador necesitaba no debería arruinar la
experiencia. El sistema debe permitir convertirlo en el objeto que sí necesita.

---

## 2. Datos verificables del servidor

Estos datos describen el `item_db`, el `mob_db`, los scripts y los rates. **No
son una taxonomía validada ni un precio.** El dataset derivado actual no se usa
como entrada de este brief.

### 2.1 Universo de objetos

| Dato | Valor |
|---|---|
| Objetos totales en `item_db` | 29,061 |
| Armor | 8,798 |
| Card | 5,582 |
| Etc | 4,125 |
| Weapon | 2,806 |
| Usable | 2,787 |
| Cash | 2,410 |
| ShadowGear | 1,028 |
| DelayConsume | 742 |
| Healing | 463 |
| Ammo | 123 |
| PetEgg / PetArmor | 149 / 45 |
| Sin tipo declarado | 3 |
| Con `Script` | 19,968 |
| Con `EquipLevelMin` | 10,336 |
| Refineables | 6,956 |

Slots declarados: 23,604 objetos con 0, 4,095 con 1, 1,036 con 2, 181 con 3,
145 con 4.

### 2.2 Flags de comercio declarados

| Flag | Objetos |
|---|---|
| `NoTrade` | 6,851 |
| `NoSell` | 4,445 |
| `NoDrop` | 7,132 |
| `NoStorage` | 2,302 |
| `NoMail` | 6,834 |
| `NoCart` | 6,877 |
| `NoAuction` | 6,850 |
| `NoGuildStorage` | 6,847 |
| `Override` | 2 |

Son flags declarados, no necesariamente el comportamiento efectivo de la
configuración del servidor.

### 2.3 Mobs y spawns

| Dato | Valor |
|---|---|
| Mobs en `mob_db` | 2,675 |
| Mobs con `Class: Boss` | 732 |
| Mobs con drops declarados | 1,937 |
| Spawns canónicos parseados | 3,656 |
| Mapas distintos | 405 |
| Mobs distintos con spawn | 1,223 |

Spawns por tipo: field 1,161; dungeon 1,521; boss 75; guild 61; instance 53;
quest 479; other 306.

Los conteos de spawns provienen del parser de scripts y no están verificados
contra el juego uno por uno. Trátalos como datos de partida, no como verdad
absoluta.

### 2.4 Otras fuentes

| Fuente | Valor |
|---|---|
| Grupos de objetos | 2,973 grupos / 3,082 subgrupos |
| Recetas en `produce_db` | 293 |
| Recetas de socket enchant | 39 |
| Scripts de quests e instancias | presentes en `npc/` |
| Precios históricos externos | 5,858 filas de LATAM y Atlantis |

Los precios históricos son referencia, no verdad. No se asume que representen
la economía de OzRo.

### 2.5 Rates custom

| Rate | Valor |
|---|---|
| `item_rate_common` / `_boss` | 500 / 500 (5x) |
| `item_rate_heal` / `_boss` | 1000 / 1000 (10x) |
| `item_rate_use` / `_boss` | 1000 / 1000 (10x) |
| `item_rate_equip` / `_boss` | 1500 / 1500 (15x) |
| `item_rate_card` | 1000 (10x) |
| `item_rate_card_boss` / `_mvp` | 10000 / 10000 (100x) |
| `item_rate_mvp` | 500 (5x) |
| `item_rate_treasure` | 500 (5x) |
| `mvp_hp_rate` | 200 |
| `monster_hp_rate` | 200 |
| `restart_hp_rate` | 50 |

### 2.6 Contrato de salida

El contrato exacto no está cerrado. Se sabe que el sistema debe alimentar un
MarketSimulator y uno o varios NPCs. Los roles y las políticas de esos NPCs
están abiertos.

---

## 3. Preferencias e hipótesis del equipo

No son decisiones cerradas. Evalúalas, critícalas o reemplázalas.

- `PREFERENCIA` — Arquitectura modular o por capas, para poder construir,
  evaluar y ajustar cada parte por separado. Evalúa si es la adecuada frente a
  alternativas.
- `PREFERENCIA` — Puede haber varios NPCs con alcance, objetivos y políticas
  distintas. No asumas un único precio ni una única política.
- `HIPÓTESIS` — La dificultad de adquisición podría estimarse cruzando una
  distribución de capacidad de jugadores simulados con una distribución de
  dificultad de los mobs. La intuición es que la mayor parte de la población
  estará en niveles medios-bajos, que los jugadores de alto nivel y bien
  equipados serán escasos, y que por eso los mobs más difíciles serían además
  más improbables. Evalúa si esto es correcto y cómo formalizarlo.
- `PREFERENCIA` — Hay interés en evaluar el uso de LLM para extraer features de
  utilidad desde descripciones y scripts, o para interpretar mecánicas. Su rol
  está abierto; si se usa, la salida debe quedar registrada y ser auditable.
- `PREFERENCIA` — Se acepta una corrida no determinista si el resultado se
  conserva y se puede auditar.

---

## 4. Lo que no sabemos

Estos datos faltan o no están cerrados. Si tu propuesta los necesita, declara
supuestos explícitos en lugar de inventarlos.

- Distribución real de los jugadores: nivel, equipo, clase, tiempo de juego,
  habilidad.
- Objetivos de progresión: cuánto debería costar, en horas, alcanzar cada tier
  o cada objeto clave.
- Roles, objetivos y políticas de los NPCs.
- Qué significa “utilidad” para OzRo y qué roles de objeto importan
  (progresión, combate, conveniencia, colección, acceso a contenido).
- Objetivos económicos: zeny/hora, inflación, distribución de riqueza, liquidez.
- Contrato de salida para el simulador y para el sitio web.
- Cuánto deben influir los precios externos y en qué (orden, ratios, bandas).
- Si la utilidad entra en la primera versión.
- Criterios de éxito desde el punto de vista de los cuatro jugadores.
- Qué fuentes de datos se consideran fiables y cuáles no.

---

## 5. El problema

> Diseñar una economía sintética para un servidor de cuatro jugadores sin
> mercado observado, que asigne valores, precios y políticas de compra/venta a
> los NPCs, de modo que la progresión, el acceso a objetos raros y la liquidez
> funcionen sin depender de una población grande.

Sub-problemas:

1. **Ontología económica.** Qué entidades, estados, relaciones y canales
   existen. No una taxonomía de tipos de objeto; un modelo de roles económicos,
   rutas, restricciones, utilidad y evidencia.
2. **Parámetros.** Qué magnitudes necesita el sistema, con unidad, origen y
   tipo (dato, decisión, derivado). Cuáles son redundantes.
3. **Adquisición.** Rutas, tiempo, zeny, riesgo, probabilidad, procesos
   destructivos, time gates, acceso, competencia.
4. **Escasez.** Qué significa con cuatro jugadores. Distinguir “no hay fuente”,
   “hay fuente pero es lenta”, “hay inventario legacy”, “nadie puede farmearlo”.
5. **Utilidad.** Si se incluye, cómo se construye sin demanda observada.
6. **Precio y política.** Cómo se combinan costo, escasez, utilidad y
   evidencia; cómo se fija el nivel; cómo se expresa la incertidumbre; cuándo
   no hay precio.
7. **NPCs.** Roles, objetivos, políticas, spreads, caps, emisión de zeny y
   anti-arbitraje.
8. **Validación y robustez.** Sin ground truth: invariantes, simulación,
   estrés, métricas de colapso.
9. **Datos.** Qué se registra, qué se puede reconstruir, qué queda sin valorar.

---

## 6. Lo que se pide

Produce un documento técnico con estas partes. Puedes proponer otro orden si lo
justificas, pero el equipo prefiere que primero se identifiquen los parámetros y
después las fórmulas.

### A. Diagnóstico

- Qué se puede determinar con los datos disponibles.
- Qué debe decidirse por diseño.
- Qué datos faltan y qué supuestos necesitas.
- Dónde ves los mayores riesgos de error.

### B. Conjunto de parámetros

Una tabla con:

| Campo | Contenido |
|---|---|
| nombre | identificador estable |
| significado | qué representa económicamente |
| unidad | hora, zeny, probabilidad, ratio, categoría |
| origen | dato, decisión, derivado |
| cálculo | función o fuente, si aplica |
| sensibilidad | qué pasa si se equivoca |
| redundancia | qué otros parámetros lo reemplazan o solapan |

Primero el catálogo; después las fórmulas.

### C. Ontología

Entidades, estados y relaciones. Propón una o varias alternativas. Justifica
por qué cada eje es independiente. Cubre, como mínimo:

- adquisición;
- transferencia y canales;
- estado de mercado;
- evidencia y procedencia;
- utilidad;
- restricciones de NPC.

### D. Modelado por parámetro

Para cada parámetro, una función o método con unidades y supuestos. Incluye,
si corresponde:

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
- precio o política;
- incertidumbre.

Incluye un ejemplo numérico mínimo para un farm común, un proceso destructivo y
un time gate tipo MVP.

### E. Composición

Cómo se pasa de los parámetros a:

- un valor o banda por objeto;
- una política de tasador;
- una política de comprador;
- una política de vendedor;
- otros NPCs que consideres necesarios.

Propón al menos **dos alternativas** de composición con sus tradeoffs. Explica
cómo se evita que dos NPCs con políticas distintas creen arbitraje.

### F. Validación y modos de fallo

- invariantes que deben cumplirse siempre;
- pruebas de monotonía;
- simulación de la población y de la progresión;
- pruebas de estrés (rates, spawns, población, precios);
- métricas de colapso y umbrales de alerta;
- qué se registra para poder auditar y recalibrar.

### G. Fases

Qué se construye primero, qué se deja para después, qué queda explícitamente
sin valorar o fuera de alcance.

### H. Supuestos y riesgos

Qué tiene que ser cierto para que el modelo funcione. Qué lo haría fallar. Cómo
se detecta temprano.

### Formato

- Español.
- Documento técnico, no ensayo.
- Separa `HECHO`, `DECISIÓN`, `SUPUESTO` y `PROPUESTA`.
- Cada fórmula con unidades y supuestos.
- Cada parámetro con origen y sensibilidad.
- Si una parte depende de datos que faltan, dilo y declara el supuesto.

---

## 7. Preguntas abiertas

No es obligatorio responderlas una por una, pero el documento debería
resolverlas o declararlas abiertas.

1. ¿Cuál es el conjunto mínimo de parámetros? ¿Cuáles se derivan de otros?
2. ¿Qué se puede determinar con los datos disponibles y qué debe decidirse?
3. ¿Cómo se estima la hora de juego? ¿Qué alternativas hay a la hipótesis de
   cruzar jugadores simulados con dificultad de mobs?
4. ¿Cómo se define escasez con cuatro jugadores? ¿Entra la competencia?
5. ¿La utilidad debe estar en la primera versión? Si sí, ¿cómo se construye sin
   demanda observada? Si no, ¿qué se pierde?
6. ¿Qué parámetro fija el nivel absoluto de la economía y cómo se elige?
7. ¿Qué NPCs hacen falta, con qué roles y qué políticas?
8. ¿Cómo se evita el arbitraje entre NPCs y entre rutas?
9. ¿Qué invariantes debe cumplir el sistema para no colapsar?
10. ¿Qué se registra para poder auditar y recalibrar después?
11. ¿Qué haría fallar el modelo y cómo se detecta temprano?
12. ¿Qué se construye primero y qué se deja fuera?

---

## 9. Restricciones

- Cuatro jugadores, sin mercado orgánico ni ground truth.
- La economía debe emular el efecto de una población mayor.
- Debe ser implementable en el ecosistema rAthena / ozro-site.
- Debe ser auditable y explicable.
- Los precios externos son referencia, no verdad.
- No se asume que el dataset derivado actual sea correcto.
- Si se usa un LLM, su salida debe quedar registrada y ser auditable.

---

## 10. Cómo se evaluará la respuesta

- ¿Está aterrizada en los datos y el contexto de OzRo?
- ¿Separa hechos, decisiones, supuestos y propuestas?
- ¿Identifica qué datos faltan en lugar de inventarlos?
- ¿Propone alternativas y tradeoffs, no una sola respuesta?
- ¿Define parámetros antes de fórmulas?
- ¿Las funciones tienen unidades y supuestos?
- ¿La política NPC es operable y no crea arbitraje?
- ¿La validación es posible sin ground truth?
- ¿Queda claro qué se construye primero y qué se deja fuera?
- ¿Evita el overfitting a unos pocos objetos?
- ¿Evita una caja negra de precios?
