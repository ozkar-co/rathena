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
| Garrett el Recolector | `trasher.txt` | 5 ofertas diarias + 1 misión de 6h por cuenta |
| Bounty Boards | `bounty/*.txt` | Misiones de caza por ciudad (26 ciudades) |
| Quests repetibles | `repeteables/*.txt` | EXP repetible por monstruo (18 quests) |

## En repo, desactivados

| NPC | Archivo | Función | Notas |
|-----|---------|---------|-------|
| Dungeon Warper | `dungeon_warper.txt` | Teleport a dungeons | QoL solo/LAN |
| Hunting Missions | `hunting_missions.txt` | Misiones caza aleatorias + shop | Candidato daily loop; balancear antes |

## Reformulaciones prioritarias

### Garrett el Recolector `implementado`

Objetivo: convertir a Garrett en el punto de entrada de la economía de basura, con precios calculados por rareza de oferta y no por el mercado.

- Todo el NPC es **por cuenta**, no por personaje. El cap diario es de **500.000 zeny por cuenta**.
- **Ofertas diarias:** 5 items con precio unitario visible. El jugador decide si los busca; se puede vender hasta agotar el cap.
- **Misión:** una por día, con ventana de 6 horas. Se elige entre contratos `common`, `uncommon` y `rare`.
- Mientras hay misión activa, Garrett **no permite vender**; solo muestra tiempo restante y progreso.
- La misión se puede **cancelar**. Al cancelar o fallar, no se puede tomar otra hasta el día siguiente, pero las ofertas diarias se desbloquean.
- Si al hablar tiene la cantidad pedida en el inventario, Garrett ofrece cerrar la misión y paga. No importa cómo consiguió los items.
- La misión paga **fuera del cap diario**, con multiplicador sobre el precio unitario; el tope y los valores exactos se definen antes de implementar.
- **Rareza por oferta**, no por precio de mercado: drop rate efectivo × cantidad de spawn × factor de acceso.
- Los items **sin spawn conocido** (instancia/evento/mob dinámico) salen del pool diario y quedan para misiones especiales.
- Tiers: `abundant`, `common`, `uncommon`, `rare`. `very_rare` queda solo para eventos/misiones especiales.
- Las cantidades de misión se precalculan en una tabla, limitadas por **peso** y por el tope de pago; no se calculan en el NPC en tiempo real.
- La tabla está en `ozro-site/assets/items/garrett-missions.json` y el script se genera con `tools/generate_garrett_npc.py`.
- Propuesta actual: 39 contratos (14 common, 16 uncommon, 9 rare), pago mínimo 500.000 y máximo 1.500.000, multiplicador 1,5, peso máximo 5.000. Cantidades: common 119–150, uncommon 49–70, rare 18–25.

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
- Mantener los nombres `MVP_KILL_<id>` y `MVP_SUPP_<id>` para no perder el historial.
- Plan detallado de puntos de Alma, reclamo e invocador en [12-mvp-tracker-journal.md](./12-mvp-tracker-journal.md).

## Monedas OzRo y Alma de MVP

### Monedas OzRo `tiers`

- Existen 4 tiers: **bronce, plata, oro y platino** (`Ozro_Bronze_Coin`, `Ozro_Silver_Coin`, `Ozro_Gold_Coin`, `Ozro_Platinum_Coin`).
- No hace falta definir todos los usos ahora: se irán usando a medida que se implementen NPCs y contenido de nivel más alto.
- El bronce ya se obtiene con Garrett; los tiers altos quedan reservados para contenido más pro.
- Cada tier debe tener una fuente, un sink y un límite; no agregar monedas decorativas.

### Alma de MVP `pendiente`

- Se obtiene al cazar MVPs naturales: 1/3/5/10/20 puntos según el tier fijo por ID. Killer y party en el mismo mapa suman; el Journal los convierte en Almas.
- Uso futuro: invocador de MVPs y receta de Bloody Branches.
- No debe generar un loop infinito (matar MVP → alma → invocar el mismo MVP → alma); las kills en el mapa de invocación no deben contar.
- Ver [12-mvp-tracker-journal.md](./12-mvp-tracker-journal.md).

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
| `#GARRETT_DAY` | Cuenta | Día de ofertas y contratos |
| `#GARRETT_SPENT` | Cuenta | Gasto diario (cap 500.000) |
| `#GARRETT_OFFER0..4` / `#GARRETT_PRICE0..4` | Cuenta | 5 ofertas diarias |
| `#GARRETT_SOLD0..4` | Cuenta | Primer trato de cada oferta |
| `#GARRETT_CONTRACT_ITEM0..2` / `_QTY` / `_PAY` | Cuenta | Contratos del día |
| `#GARRETT_MISSION_ACTIVE` / `_ITEM` / `_QTY` / `_PAY` / `_END` / `_DAY` | Cuenta | Misión activa |
| `#GARRETT_TRADES` / `#GARRETT_TOTAL_SPENT` / `#GARRETT_UNIQUE_TRADES` | Cuenta | Historial de tratos |
| `#GARRETT_MISSIONS_DONE` / `#GARRETT_MISSION_EARNED` | Cuenta | Historial de misiones |
| `OZRO_KARMA` | Personaje | Reputación/karma firmado |
| `$OZRO_DEATHS_TOTAL` | Global servidor | Muertes registradas |

> Las viejas variables `TRSH_*` quedan en la base pero el script nuevo no las usa; no se borran para conservar el historial.

## Comentarios

<!-- Borrador libre para ideas nuevas; luego organizar arriba -->
