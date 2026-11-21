# Reemplazo de WoE: castillos GvE

Documento de trabajo. **No es prioridad.** Idea general cerrada; implementación por etapas, empezando por un v1 mínimo para probar mecánicas.

Estado: `pendiente` (diseño general definido).

## Problema

Con pocos jugadores y una sola guild, la WoE clásica (GvG por Emperium) no tiene sentido. Igual se quiere conservar el valor de **castillos**: hub de guild, Guild Dungeon, cofres, Kafra, guardians e inversión — sin regalarlo.

## Idea central

La “WoE” de OzRo es un **raid GvE de conquista/defensa** en una ventana fija del fin de semana.

- **Entre semana:** el castillo es base social (sin riesgo de perderlo).
- **Fin de semana:** ventana corta y fija (día/hora a definir, un par de horas) de conquista o defensa.
- **Misma mecánica** para ambos casos: si el castillo tiene dueño → defensa; si está vacío → conquista abierta.
- Perder el castillo = **castigo de una semana** sin hub (no es pérdida permanente). Guild level / skills se mantienen. Hay mucho más que hacer en el juego esa semana, incluida prepararse para la próxima.

Multi-castillo está permitido a propósito: conquistar varios es posible; **defenderlos en la misma ventana es muy difícil**. La guild asume el riesgo (amigos/alts el finde, más poder, o mucha inversión en defensa).

## Loop semanal

1. Ventana del finde: pelear (conquistar o defender).
2. Si ganan: hub activo esa semana + beneficios según lo implementado.
3. Entre semana: usar el castillo (Kafra, GD, cofres, NPCs…); invertir en defensa cuando esté permitido.
4. Día previo a la próxima invasión: **no se puede invertir** (si pierden, no pierden una inversión fresca).
5. Inversión aplicada / disponible **al día siguiente** de tomarlo (calendario exacto pendiente de una tablita de 7 días).
6. Siguiente finde: otra vez la ventana. Si no defienden o fallan → pierden hub e inversión de defensa.

## Combate: oleadas por salas y capitanes

- El asedio avanza **por etapas / salas**.
- En cada oleada hay mobs normales y **capitanes**.
- **Solo los capitanes dañan el Emperium**; el resto se puede pegar igual (no se marca al capitán de forma obvia).
- El capitán **habla** (fácil de implementar): entre la montonera cuesta ubicarlo, pero reduce la sensación de RNG puro.
- Si descubren y matan al capitán de la sala → la siguiente etapa es más fácil.
- Si no → en la siguiente hay **más capitanes** (cascada: 1 → 2 → …). Llegar a la Emp con muchos capitanes vivos puede hacer imposible salvarla.
- A veces será fácil, a veces difícil, a veces casi imposible: pueden intentar **otro castillo** o esperar la próxima semana.
- **Guardians no targetean ni dañan capitanes.** Un mob quieto junto a un guardian que no lo ataca es una pista extra si se dan cuenta.

### UX de amenaza

- Se anuncia el nivel de amenaza de la ventana.
- Se revela el **número de capitanes vivos**.
- **Una** alerta si un capitán llega a la Emperium (sin spam).

## Hub y beneficios (visión; no todo en v1)

Desbloqueables / atados a tener el castillo:

| Beneficio | Notas |
|-----------|--------|
| Kafra de castillo | Identidad de hub |
| Guild Dungeon | Acceso mientras el castillo esté en pie |
| Auras de guild en GD | Mod: las auras de castillo también aplican en Guild Dungeon |
| Treasure chests | Ver cofres abajo |
| Guardians | Defensa del finde; no pegan a capitanes |
| Inversión en defensa | Se pierde al perder el castillo; no se invierte el día previo a la invasión |
| NPCs custom | Salas de branches, servicios, etc. |
| Mercenarios limitados | Cupo del castillo; no farm eterno |
| Drops únicos en la ventana | Solo custom, se definen al implementar |
| MVP potenciado | `descartado` |

Keys craft/compra caras: **no en el plan inicial**. Solo se revisan si, ya implementado el sistema, hay quejas recurrentes por falta de acceso. La key de reclamo/salas tampoco es requisito de v1.

## Cofres y cuotas

- **v1:** sin cuotas; cada día cofres del **tier más bajo**.
- **Después:** tiers según cuántos miembros pagaron cuota personal ese día (nadie paga por otro). Más pagos antes del cutoff → mejor tier. Alts en la guild OK: si quieren el tier alto, entran y pagan con cada uno. Softcap de pagos pendiente cuando se implemente.

## Skills de guild (uso previsto)

| Skill / sistema | Rol |
|-----------------|-----|
| GD_APPROVAL | Guild reconocida; requisito blando para reclamar |
| GD_KAFRACONTRACT | Kafra del hub |
| GD_GUARDRESEARCH / GD_GUARDUP | Guardians del asedio |
| GD_DEVELOPMENT | Apoya inversión / calidad de defensa o cofres |
| Auras (Leadership, Glory Wounds, Soul Cold, Hawk Eyes) | En castillo y en **Guild Dungeon** |
| Battle Order / Regeneration / Restore | Kit del GM en la ventana de asedio |
| GD_EMERGENCYCALL | **Solo durante el asedio** |
| Extension / Guild Storage | QoL de guild; storage puede brillar más con hub |

Detalle de balance y restricciones de mapa: al implementar.

## Plan por etapas

### v1 (probar mecánicas)

- Un castillo.
- Ventana fija finde: conquista/defensa.
- Oleadas por sala + capitanes (hablan, solo ellos dañan Emp, cascada si no se limpian).
- Amenaza anunciada + contador de capitanes + una alerta a Emp.
- Al ganar: hub barebones (como mínimo Kafra y/o GD) + cofres tier 1 diarios.
- Al perder: se pierde el hub; guild level se mantiene.
- Sin keys, sin cuotas, sin multi-tier de cofres, sin MVP ritual, sin multi-castillo obligatorio.

### Después (cuando v1 se entienda)

- Guardians + inversión (con cutoff día previo).
- Auras en GD.
- NPCs / salas desbloqueables.
- Tiers de cofres por cuotas.
- Más castillos / tiers de dificultad.
- Evaluar keys solo si hace falta.

## Pendientes al implementar (no bloquean el diseño)

- Día/hora exactos de la ventana y zona horaria.
- Calendario de 7 días: cuándo se puede invertir, cuándo corta, cuándo spawnean cofres.
- Multi-castillo en la misma ventana: oleadas en paralelo vs. elegir un castillo (define qué tan suicida es tener dos).
- Precios de cuotas / inversión / guardians.
- Lista de castillos y tiers de dificultad.
- Feedback del capitán que habla si el chat se tapa en montonera.

## Relación con otros docs

- Idea previa en backlog: [08-ideas-backlog.md](./08-ideas-backlog.md) (apunta aquí).
- PvP urbano automático (distinto de castillos): [16-eventos-automaticos.md](./16-eventos-automaticos.md) — La Purga.
- BG/PvP abierto desactivados en server chico; el combate entre jugadores y el de castillos se resuelven por eventos, no por salas permanentes.
