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
| Bounty Boards | `bounty/*.txt` | Misiones de caza por ciudad (26 ciudades) |
| Quests repetibles | `repeteables/*.txt` | EXP repetible por monstruo (18 quests) |

## En repo, desactivados

| NPC | Archivo | Función | Notas |
|-----|---------|---------|-------|
| Dungeon Warper | `dungeon_warper.txt` | Teleport a dungeons | QoL solo/LAN |
| Hunting Missions | `hunting_missions.txt` | Misiones caza aleatorias + shop | Candidato daily loop; balancear antes |

## Reformulaciones prioritarias

### Gambler `reformular` (reemplazo completo)

- No se usa más **Special Gold** como moneda.
- El Gambler se reemplaza por un NPC que entrega **refine safe** usando monedas OzRo de distintos tiers.
- El refine safe debe ser **“si falla, no se rompe”**, no un item que garantice subir de nivel fijo.
- El comportamiento anterior (llevar directo a un nivel) desbalanceó el juego; no se repite.
- Costos y tiers quedan pendientes de definir junto con el resto de la economía.

## Monedas OzRo

### Monedas OzRo `tiers`

- Existen 4 tiers: **bronce, plata, oro y platino** (`Ozro_Bronze_Coin`, `Ozro_Silver_Coin`, `Ozro_Gold_Coin`, `Ozro_Platinum_Coin`).
- No hace falta definir todos los usos ahora: se irán usando a medida que se implementen NPCs y contenido de nivel más alto.
- El bronce ya se obtiene en la economía actual; los tiers altos quedan reservados para contenido más pro.
- Cada tier debe tener una fuente, un sink y un límite; no agregar monedas decorativas.

## Card Collector: datos existentes

- El Card Collector actual **ya tiene datos de jugadores**; cualquier cambio debe preservarlos.
- Revisar compatibilidad antes de tocar variables, categorías o formato de guardado.
- No cambiar nombres de variables persistentes (`#CARD_*`) sin migración.
- Es una pieza fundamental de la meta por cuenta; no romperla ni perder progreso.

## Contenido Hercules: referencia, no port

| NPC / sistema | Decisión |
|---------------|----------|
| Ox Hunter (Ushi) | `descartado` — sprite elegido al azar; historia incompatible y quedó a medio implementar |
| Ox Merchant (Kuma) | `descartado` — misma razón; no usar Ox Coins |
| Crimson Weapons (cadena) | `descartado` como port — hoy las Crimson se consiguen por vías oficiales |
| Marcus | `descartado` como port — queda como ejemplo de lore para desbloquear objetos |
| Gambler | `reformular` — reemplazo por refine safe con monedas OzRo |
| Card Trader | `pendiente` — revisar si se implementa propio |
| Old Blacksmith | `pendiente` — usar monedas OzRo, no Special Gold |
| Cash Point Merchant / points | `reformular` — los points existían porque no sabíamos modificar drops; hoy sí se puede |
| Blessed Ores crafter | `pendiente` — quest con lore |
| Bloody Branch Manufacturer | `pendiente` — NPC custom |
| Vendedor Viajero | `pendiente` — items de invocación y stock limitado; ver [15-vendedor-viajero.md](./15-vendedor-viajero.md) |

## Planificados

### Mercado OzRo Coin

- Moneda con tiers; cada tier con recompensas distintas.
- Requisito para ciertas quests o items especiales.
- Compra/venta por zeny con precio dinámico si se conecta con Stock Market.
- Generaliza el concepto de monedas por actividad, pero con lore propio.


## Otras evoluciones pendientes

### Kaz el Cronista `reformular`

- Detectar nivel del PJ activo.
- conoce la ubicacion del vendedor viajero

### Card Collector `expandir`

- Reformar tienda de cartas (precios, misiones de obtención).
- Más lore de coleccionista.
- La idea de cambiar cartas por una cifra absurda → carta inobtenible aleatoria queda `reformular`; evaluar como sink extremo.
- **No perder los datos existentes.**

### Sabio de los Elementos `expandir`

- Hoy: Fuego, Viento, Agua, Tierra (30 min).
- Futuro (quest): desbloquear **Holy** (`SC_ASPERSIO`), **Ghost** (`SC_GHOSTWEAPON`) y **Shadow** (`SC_SHADOWWEAPON`).
- Quest que alargue la duración del endow.

### Kessinger (Soul Linker) `expandir`

- Hoy: 20 min de vínculo.
- Futuro (quest): alargar la duración del soul link para el PJ.

## Scripts genéricos rAthena (comentados en `scripts_custom.conf`)

Útiles para OzRo — evaluar activación:

| Script | Ubicación | Relevancia |
|--------|-----------|------------|
| Floating rates | `npc/custom/etc/floating_rates.txt` | Evento automático rates |
| Monster arena | `npc/custom/etc/monster_arena.txt` | Competencia PvE |
