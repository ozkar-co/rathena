# NPCs personalizados

**Última revisión:** 2026-11-16
**Config:** `npc/scripts_custom.conf`

> **Regla de documentación:** lo que ya está implementado sale de este archivo y queda registrado en el changelog público y en el git log. Acá solo se mantiene lo pendiente, lo que hay que reformular y las decisiones de diseño.

## Reglas de contenido custom

- Todo NPC nuevo debe ser **lore-friendly** y encajar con el mundo; no agregar contenido solo porque el sprite estaba a mano.
- La fuente de verdad técnica es la documentación oficial de rAthena (`doc/script_commands.txt`, `doc/item_db.txt`, etc.) para esta versión.
- **No se portan NPCs de Hercules.** El repo viejo (`/home/oz/Code/ozro`) queda como referencia de ideas, no como código a migrar.
- No tocar el cliente si no es imprescindible; evitar items que dependan de sprites o iconos que el cliente actual no tenga.
- No hay server de prueba: se prueba directo en producción con los 3 jugadores. Si algo falla, se corrige o se apaga el server.
- Antes de agregar contenido nuevo, **balancear lo que ya está activo**.

## Activos (referencia)

| NPC | Archivo | Función |
|-----|---------|---------|
| Healer | `healer.txt` | Cura + buffs temporales |
| Stylist | `stylist.txt` | Cambio de apariencia |
| Monke | `monke.txt` | Intercambia bananas por frutas aleatorias |
| Canalizadora Mística | `resetnpc.txt` | Reset stats/skills (birthstone + zeny) |
| Sophie | `points2zeny.txt` | Cambio puntos cash ↔ zeny |
| Card Collector | `card_collector.txt` | Archivo de cartas por cuenta, % progreso |
| Card Remover | `card_remover.txt` | Quitar cartas de equip |
| Kaz el Cronista | `chronicler.txt` | Lore básico; conteo jugadores |
| Sabio de los Elementos | `endow_sage.txt` | Endow elemental (zeny + piedra) |
| Ludovico el Sepulturero | `gravekeeper.txt` | Muertes del PJ + contador global |
| Kessinger | `soul_link.txt` | Soul Link de pago |
| Garrett el Recolector | `trasher.txt` | Compra chatarra diaria; reformular |
| Bounty Boards | `bounty/*.txt` | Misiones de caza por ciudad (26 ciudades) |
| Quests repetibles | `repeteables/*.txt` | EXP repetible por monstruo (18 quests) |

## En repo, desactivados

| NPC | Archivo | Función | Notas |
|-----|---------|---------|-------|
| Dungeon Warper | `dungeon_warper.txt` | Teleport a dungeons | QoL solo/LAN |
| Hunting Missions | `hunting_missions.txt` | Misiones caza aleatorias + shop | Candidato daily loop; balancear antes |

## Reformulaciones prioritarias

### Garrett el Recolector `reformular`

Objetivo: convertir a Garrett en el punto de entrada de la economía de basura, con precios ajustados al mercado real.

- La lista de precios sale del repo **ragnabots**, donde se están preparando bots comerciales; se carga cuando esté lista.
- Antes de fijar precios, sacar del pool todos los items que **no son usados por NPCs activos**.
- Dos modos de interacción:
  1. **Junk hunter / dumpster diving:** Garrett pide cantidades altas de basura específica y paga con monedas OzRo, zeny o recursos difíciles de conseguir / piezas de equipo especiales. Similar al funcionamiento actual, pero con misión diaria.
  2. **Bargain:** el jugador ofrece basura y Garrett calcula una oferta variable según el item/cantidad.
- La misión del día es **única por cuenta** y rota; no todos ven la misma.
- El zeny de las recompensas debe **escalar** con el nivel/valor del item; no usar montos planos.
- En la web pública debe estar la lista de basura que Garrett compra, para que los jugadores sepan qué guardar y cuándo conviene vender.
- Revisar el ritmo actual del bronce: hoy se entrega 1 moneda cada ~10 tratos únicos, con máximo 2 tratos/día; eso puede ser demasiado lento para una moneda de entrada.
- **Rareza por oferta**, no por precio de mercado: usar drop rate efectivo × cantidad de spawn × factor de acceso.
- Los items **sin spawn conocido** (instancia/evento/mob dinámico) salen del pool diario y quedan para misiones especiales.
- Tiers calculados: `abundant`, `common`, `uncommon`, `rare`, `very_rare`.
- La selección diaria debe elegir items aleatorios dentro de cada tier, con cantidad y precio de misión por tier; los valores exactos están en revisión.

### Gambler `reformular` (reemplazo completo)

- No se usa más **Special Gold** como moneda.
- El Gambler se reemplaza por un NPC que entrega **refine safe** usando monedas OzRo de distintos tiers.
- El refine safe debe ser **“si falla, no se rompe”**, no un item que garantice subir de nivel fijo.
- El comportamiento anterior (llevar directo a un nivel) desbalanceó el juego; no se repite.
- Costos y tiers quedan pendientes de definir junto con el resto de la economía.

### MVP Tracker + MVP Journal `pendiente` — prioridad alta

- Es el NPC más importante para la dinámica actual: los jugadores compiten por quién mata más MVPs.
- Debe contar **kills y asistencias por MVP**, no solo un total global.
- También debe permitir saber **qué MVPs mata cada jugador**, porque hay gente que se especializa en uno.
- No se porta el script de Hercules: se reimplementa con el estándar actual de rAthena.
- El Journal muestra el progreso; el Tracker registra los eventos de muerte/asistencia.

## Monedas OzRo y Alma de MVP

### Monedas OzRo `tiers`

- Existen 4 tiers: **bronce, plata, oro y platino** (`Ozro_Bronze_Coin`, `Ozro_Silver_Coin`, `Ozro_Gold_Coin`, `Ozro_Platinum_Coin`).
- No hace falta definir todos los usos ahora: se irán usando a medida que se implementen NPCs y contenido de nivel más alto.
- El bronce ya se obtiene con Garrett; los tiers altos quedan reservados para contenido más pro.
- Cada tier debe tener una fuente, un sink y un límite; no agregar monedas decorativas.

### Alma de MVP `pendiente`

- El **colector** (Card Collector) la fabrica; el uso concreto queda pendiente de diseño.
- No debe generar un loop infinito (matar MVP → alma → invocar el mismo MVP → alma).
- Definir más adelante si invoca un MVP concreto, si se consume o si sirve como material de crafting.

## Card Collector: datos existentes

- El Card Collector actual **ya tiene datos de jugadores**; cualquier cambio debe preservarlos.
- Revisar compatibilidad antes de tocar variables, categorías o formato de guardado.
- No cambiar nombres de variables persistentes (`#CARD_*`) sin migración.
- Es una pieza fundamental de la meta por cuenta; no romperla ni perder progreso.

## Bounties y repetibles: balance

- Bounties que dan **casi 1 nivel** no son el problema principal; las que dan **2 niveles** sí.
- El **zeny de bounty debe escalar** por nivel/banda; hoy es un monto fijo.
- Las repetibles ayudan a “arrastrar” personajes nuevos con los PJ fuertes de la party; se mantienen, pero con recompensas controladas.
- Revisar bandas donde la misma recompensa vale mucho a nivel bajo y casi nada al final de la banda.
- Balancear esto **antes** de agregar contenido nuevo.

## Contenido Hercules: referencia, no port

| NPC / sistema | Decisión |
|---------------|----------|
| Ox Hunter (Ushi) | `descartado` — sprite elegido al azar; historia incompatible y quedó a medio implementar |
| Ox Merchant (Kuma) | `descartado` — misma razón; no usar Ox Coins |
| MVP Tracker / Journal | `pendiente` — reimplementar, no portar |
| Crimson Weapons (cadena) | `descartado` como port — hoy las Crimson se consiguen por vías oficiales |
| Marcus | `descartado` como port — queda como ejemplo de lore para desbloquear objetos |
| Gambler | `reformular` — reemplazo por refine safe con monedas OzRo |
| Card Trader | `pendiente` — revisar si se implementa propio |
| Old Blacksmith | `pendiente` — usar monedas OzRo, no Special Gold |
| Cash Point Merchant / points | `reformular` — los points existían porque no sabíamos modificar drops; hoy sí se puede |
| Blessed Ores crafter | `pendiente` — quest con lore |
| Bloody Branch Manufacturer | `pendiente` — NPC custom |
| Traveler Tool Dealer | `pendiente` — lore del dealer ambulante |

## Planificados

### Mercado OzRo Coin

- Moneda con tiers; cada tier con recompensas distintas.
- Requisito para ciertas quests o items especiales.
- Compra/venta por zeny con precio dinámico si se conecta con Stock Market.
- Generaliza el concepto de monedas por actividad, pero con lore propio.

### Mercader de birthstones

- Vende birthstones (insumo del reset); stock/oferta cambia cada día.

### Priest Viajero / Warper con lore `pendiente`

- Warper para volver rápido a mapas de caza/MVP sin depender de acólitos con warp memorizado.
- Debe desbloquearse viajando primero al mapa, con quest/lore y costo de items.
- El vínculo dura un tiempo y hay que renovarlo.
- Puede aparecer en distintas ciudades y habilitar zonas según su historia.

## Otras evoluciones pendientes

### Kaz el Cronista `reformular`

- Detectar nivel del PJ activo.
- Indicar el siguiente paso del arco lore activo.
- Marcar progreso en `#LORE_ARC_*`.
- Sincronizar con la web.

### Card Collector `expandir`

- Reformar tienda de cartas (precios, misiones de obtención).
- Más lore de coleccionista.
- La idea de cambiar cartas por una cifra absurda → carta inobtenible aleatoria queda `reformular`; evaluar como sink extremo.
- **No perder los datos existentes.**

### Monke `probar`

- Doc viejo: “muy roto”; cambiar a entregar cualquier fruta al azar.
- Revisar si ya se ajustó.

### Reset `probar`

- Doc viejo: una vez por personaje.
- Hoy: infinito con birthstone.
- Alinear con la filosofía de reset fácil.

### Sabio de los Elementos `expandir`

- Hoy: Fuego, Viento, Agua, Tierra (30 min).
- Futuro (quest): desbloquear **Holy** (`SC_ASPERSIO`), **Ghost** (`SC_GHOSTWEAPON`) y **Shadow** (`SC_SHADOWWEAPON`).
- Quest que alargue la duración del endow.

### Kessinger (Soul Linker) `expandir`

- Hoy: 20 min de vínculo.
- Futuro (quest): alargar la duración del soul link para el PJ.

### Kafra Staff / Cool Event Corp (votación de dungeon) `pendiente`

- Que no requiera 20 votos: ganar por mayoría simple.
- Elecciones de lunes a miércoles; dungeon activo de jueves a domingo.

## Scripts genéricos rAthena (comentados en `scripts_custom.conf`)

Útiles para OzRo — evaluar activación:

| Script | Ubicación | Relevancia |
|--------|-----------|------------|
| Stock Market | `npc/custom/etc/stock_market.txt` | Economía dinámica sin players |
| Bank | `npc/custom/etc/bank.txt` | Si se deshabilita banco del menú |
| Quest board | `npc/custom/quests/questboard.txt` | Tablón dinámico |
| Floating rates | `npc/custom/etc/floating_rates.txt` | Evento automático rates |
| Marriage | `npc/custom/etc/marriage.txt` | ? |
| Monster arena | `npc/custom/etc/monster_arena.txt` | Competencia PvE |

## Variables de script (NPCs actuales)

| Variable | Alcance | Uso |
|----------|---------|-----|
| `OZRO_KARMA` | Personaje | Reputación/karma firmado |
| `TRSH_TRADES` | Personaje | Ventas totales con Garrett |
| `TRSH_UniqueTrades` | Personaje | Primer trato de cada item del día |
| `TRSH_DoneItem0` / `TRSH_DoneItem1` | Personaje | Flag diario por slot |
| `TRSH_DailySpend` / `TRSH_TotalSpent` / `TRSH_LastDay` | Personaje | Economía diaria de Garrett |
| `TRSH_Item0$` / `TRSH_Item1$` | Personaje | Items del día |
| `$OZRO_DEATHS_TOTAL` | Global servidor | Muertes registradas |

> Al reformular Garrett, conservar o migrar estas variables para no perder progreso ni el historial de tratos.

## Comentarios

<!-- Borrador libre para ideas nuevas; luego organizar arriba -->
