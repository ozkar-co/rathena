# Eventos automáticos y cronograma

Documento de trabajo para eventos automáticos pensados para **3 jugadores**. La recompensa base será **OzCoin**; la tienda de canje queda pendiente.

## Eventos seleccionados

| Evento | Estado | Notas |
|--------|--------|-------|
| Find the Mushroom | `en-repo` | `npc/custom/events/mushroom_event.txt`. Ya tiene lógica automática; ajustar premio y frecuencia. |
| Devil Square | `en-repo` | `npc/custom/events/devil_square.txt`. Oleadas de mobs; revisar nivel, costo y recompensa. |
| Floating Rates (happy hour) | `en-repo` | `npc/custom/etc/floating_rates.txt`. Adaptar a una ventana fija de rates. |
| Eventos estacionales | `en-repo` | `npc/events/*` y `npc/custom/events/holiday/*`. Revisar cada uno antes de sumarlo al cronograma. |
| Búsqueda del cofre | `nuevo` | Un cofre en un field contiguo a una ciudad aleatoria. Se anuncia la ciudad, hay tiempo límite y desaparece. Solo da zeny. |
| Poring con nombre correcto | `revisar` | Evento de matar al Poring con el nombre indicado. Falta confirmar el script; no se encontró en el repo. |
| Trivia | `nuevo` | Requiere seleccionar muy bien preguntas y respuestas. Puede usar datos del ranking para que el jugador consulte la web. |
| Escondite | `nuevo` | Un NPC da pistas y los jugadores deben encontrarlo. |
| La Purga | `nuevo` | Ventana horaria en días fijos o aleatorios: ciudades principales en PvP + noche. Avisos previos y ambientación para que quien no quiera pelear se aleje. |

## A revisar

| Evento | Estado | Notas |
|--------|--------|-------|
| Cluckers | `en-repo` | `npc/custom/events/cluckers.txt`. Hoy lo inicia un GM; evaluar automatizarlo. |
| MVP Ladder | `en-repo` | `npc/custom/events/mvp_ladder.txt`. Cambiar el enfoque: ver hasta dónde llega la party, con MVPs modificados (menos vida, sin drop). |
| Monster Arena | `en-repo` | `npc/custom/etc/monster_arena.txt`. Evaluar apuestas solo con zeny. |
| Geffen Magic Tournament | `en-repo` | `npc/custom/official/GeffenMagicTournament.txt`. Revisar si funciona bien con pocos jugadores. |

## OzCoin

- Los eventos seleccionados pagan **OzCoin**, salvo Búsqueda del cofre (solo zeny) y Floating Rates (solo rates).
- Montos, límites por cuenta y tienda de canje quedan pendientes.
- Evitar que el mismo evento se pueda farmear con alts.

## Cronograma semanal (borrador)

Hora del servidor; falta confirmar zona horaria.

| Día | Hora | Evento | Duración | Recompensa |
|-----|------|--------|----------|------------|
| Lunes | 21:00 | Find the Mushroom | 10–15 min | OzCoin |
| Martes | 21:00 | Devil Square | 30 min | OzCoin |
| Miércoles | 21:00 | Trivia | 15–20 min | OzCoin |
| Jueves | 21:00 | Escondite | 15–20 min | OzCoin |
| Viernes | 21:00 | Búsqueda del cofre | 10–15 min | Zeny |
| Sábado | 21:00 | Poring con nombre correcto | 10–15 min | OzCoin |
| Domingo | 20:00 | Floating Rates (happy hour) | 60 min | Rates |

- Los eventos estacionales reemplazan el evento del día cuando corresponda.
- Find the Mushroom, Devil Square y Floating Rates hoy tienen lógica automática propia; habrá que ajustarlos para que respeten el cronograma.
- El cronograma debe ser la única fuente para el bloque **Próximo Evento** de la web y para los disparadores in-game.

## La Purga (evento automático)

Evento de ventana horaria: durante unas horas, en días fijos o aleatorios, las **ciudades principales** pasan a modo PvP y el mundo entra en **noche**. Quien quiera pelear va a las ciudades; quien no, se aleja a fields, dungeons o maps seguros fuera de ciudad.

### Intención

- Crear un momento semanal (o semi-aleatorio) de tensión social sin forzar a nadie a pelear.
- Concentrar el combate en puntos conocidos (ciudades principales), no en todo el mapa.
- Que el aviso y la ambientación den tiempo y señal clara para decidir: pelear o salir.

### Calendario y ventana

- **Días:** fijos (ej. viernes/sábado noche) o un día aleatorio de la semana anunciado con antelación.
- **Duración:** unas horas (borrador: 1–2 h). No solapa el evento corto de las 21:00 del cronograma, o lo reemplaza ese día.
- **Hora:** ventana nocturna del servidor (ej. 22:00–00:00). Confirmar zona horaria junto al resto del cronograma.

### Fases

| Fase | Duración (borrador) | Qué pasa |
|------|---------------------|----------|
| Aviso temprano | ~15–30 min antes | Broadcast + mensaje en chat: día/hora, ciudades afectadas, “salí de ciudad si no querés PvP”. |
| Aviso final | ~5 min antes | Countdown corto; cielo empieza a oscurecer si es viable técnicamente. |
| Activa | 1–2 h | Ciudades principales en PvP; modo noche; ambientación (mensaje periódico, sonido/efecto si hay). |
| Cierre | al terminar | PvP se desactiva en ciudades; noche vuelve a ciclo normal; broadcast de fin. |

### Alcance del PvP

- Solo **ciudades principales** (definir lista: Prontera, Geffen, Payon, Morroc, Aldebaran, etc.).
- Fuera de esas maps: sin PvP de evento (comportamiento normal del servidor).
- Sin PK forzado en fields/dungeons: la Purga es urbana a propósito.
- Pendiente: si los `@town` / warps a ciudad durante la Purga deben avisar o bloquear teleport a ciudad en PvP.

### Ambientación

- **Noche:** forzar night mode en el servidor (o al menos en las maps de ciudad) mientras el evento esté activo.
- **Avisos:** broadcasts claros en español, con minutos restantes al entrar y a mitad de ventana.
- **Señal visual/sonora:** si el cliente lo permite, efecto de cielo, música o anuncio de GM-style al inicio/fin.
- Objetivo: que un jugador distraído entienda “esto es Purga” sin leer un wiki.

### Participación voluntaria

- No hay inscripción: estar en ciudad principal durante la ventana = estás en PvP.
- Quien no quiera pelear: salir a field, dungeon, casa, o ciudad no listada (si alguna queda fuera).
- Quien quiera pelear: ir a las ciudades principales y buscar combate.
- No castigar a quien se queda afuera (sin reward obligatorio por matar; ver recompensas abajo).

### Recompensas (borrador)

- Opción A: solo bragging / ranking de kills de la noche (sin OzCoin).
- Opción B: OzCoin o loot menor por kill / por sobrevivir X minutos en ciudad, con tope por cuenta para evitar alt-farm.
- Evitar que farmear alts en ciudad vacía pague igual que un fight real.
- Pendiente: dropeo de equipo, safe zones dentro de ciudad (ej. interior de casas), y reglas de party/guild.

### Relación con PvP / Battleground

- Si Battleground queda deshabilitado por falta de jugadores, La Purga cubre el hueco de “contenido vs jugadores” sin sala de BG.
- Otras ideas a evaluar aparte: duelo 1v1, rey de la colina o torneo corto.
- El equipo pensado para BG sigue teniendo sentido aquí: sirve contra humanos.

### Pendientes técnicos

- Cómo marcar maps de ciudad como PvP solo durante la ventana (mapflag temporal vs. script).
- Forzar noche sin romper el ciclo día/noche del resto del día.
- Broadcasts programados y countdown fiable con pocos jugadores online.
- Lista definitiva de maps “ciudad principal” y exclusiones (casas, interiors, woE castles).
- Si el día es aleatorio: anuncio en web (“Próximo Evento” / banner) el mismo día o con 24 h de anticipación.
