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

## PvP y battleground

- Si Battleground queda deshabilitado por falta de jugadores, evaluar PvP abierto con recompensas de equipo de BG, ya que ese equipo sirve contra humanos.
- Otras ideas a evaluar: duelo 1v1, rey de la colina o torneo corto.
