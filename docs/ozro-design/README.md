# OzRo — Diseño del servidor

Documentación viva de ideas, sistemas y decisiones para el servidor privado OzRo (rAthena).

> **Filosofía:** No esperar a tener el servidor balanceado y listo para disfrutarlo. Ir armando, probando y ajustando mientras se juega. La retroalimentación de cada sesión alimenta el diseño.

## Cómo usar estos documentos

Cada archivo es independiente y editable. Convenciones:

| Etiqueta | Significado |
|----------|-------------|
| `implementado` | Activo en el servidor |
| `en-repo` | Script existe pero está desactivado o incompleto |
| `pendiente` | Por hacer |
| `reformular` | Idea válida pero hay que replantearla |
| `probar` | Implementado a medias; falta jugar y ajustar |
| `descartado` | Ya no aplica o se rechazó |
| `hercules` | Existía en Hercules; solo referencia, no se porta |

La sección **Comentarios** al final de cada archivo es un borrador libre: se apuntan ideas sueltas al jugar y luego se **organizan** dentro de las secciones estructuradas del propio documento.

## Flujo de trabajo

- **Ideas nuevas:** apuntarlas en *Comentarios* del archivo que corresponda; después moverlas a la tabla o sección adecuada.
- **Al implementar algo:** borrar el bloque de planificación del doc y registrarlo en el **changelog público** (lo general) y en el **git log** (lo técnico). La doc se vacía a medida que el servidor crece; cuando quede vacía, el contenido custom está terminado.
- **Al crear contenido nuevo, actualizar la web:**
  - Sección **Info** del sitio → solo el *listado* de NPCs custom y quests custom.
  - Sección **Enciclopedia** → guías y detalles específicos (si aplica).

## Índice

| Archivo | Contenido |
|---------|-----------|
| [01-vision-y-contexto.md](./01-vision-y-contexto.md) | Quiénes somos, cómo jugamos, problemas y principios de diseño |
| [02-configuracion-servidor.md](./02-configuracion-servidor.md) | Rates, reglas y personalizaciones técnicas |
| [03-sistemas-core.md](./03-sistemas-core.md) | Sistemas prioritarios: challenges, meta por cuenta, loops diarios |
| [04-npcs.md](./04-npcs.md) | NPCs custom: activos, reformulaciones, monedas y contenido pendiente |
| [05-quests-custom.md](./05-quests-custom.md) | Quests custom, crafting con lore y balance de bounties |
| [06-arcos-oficiales.md](./06-arcos-oficiales.md) | Lore oficial curado por temporadas; guías y ajustes |
| [07-web-api.md](./07-web-api.md) | Integración web, rankings, perfil de cuenta |
| [08-ideas-backlog.md](./08-ideas-backlog.md) | Lluvia de ideas antigua reformulada y priorizada |
| [09-estado-tecnico-y-estabilidad.md](./09-estado-tecnico-y-estabilidad.md) | Revisión técnica: rev, cliente, PACKETVER, skills y mapas faltantes antes de congelar |
| [10-cliente-organizacion-y-pruebas.md](./10-cliente-organizacion-y-pruebas.md) | Cómo ordenar el cliente, separar base/custom y probar el cliente actual sin romper lo que funciona |
| [12-mvp-tracker-journal.md](./12-mvp-tracker-journal.md) | Tracker, El Guardián de Almas y Almas de MVP: variables, puntos, invocador y branches |
| [13-mercado-npc-tasador.md](./13-mercado-npc-tasador.md) | Mercado NPC sin bots: tasador, consignación y casa de empeño |
| [14-arena-mvp-invocador.md](./14-arena-mvp-invocador.md) | Arena de MVP en instancia: mapa, entrada, spawner y costos en Almas |
| [15-vendedor-viajero.md](./15-vendedor-viajero.md) | Vendedor viajero: items de invocación, stock limitado, precios y reposición |

## Repos relacionados

- **Servidor:** `rathena/` — scripts en `npc/custom/ozro/`, config en `conf/import/`
- **API:** `ozro-backup/src/api/server.js`
- **Web:** `ozro-site/`
- **Bots comerciales:** `ragnabots/` — **DEPRECADO**; solo datos históricos de referencia

## Decisiones recientes

<!-- Actualizar aquí cuando se tomen decisiones importantes -->

- **2026-07:** Meta de progreso por **cuenta principal**, no por personaje. Incentivar una cuenta por jugador en lugar de multi-cuenta para suplir party.
- **2026-07:** Arcos oficiales se curan poco a poco; buscar guías en internet y crear pistas/ayudas según se vayan jugando.
- **2026-07:** Sin cambios al client por ahora. Todo server-side + web.
- **2026-07:** Crimson Weapons — en Hercules estaban rotas; en rAthena ya se pueden conseguir. La idea inicial era reactivar el flujo con Marcus, pero quedó **superada el 2026-11-16**: no se porta la cadena; la lore queda como referencia para futuras fabricaciones.
- **2026-11:** Congelar la base en rAthena de enero 2026 + cliente actual. Antes de balancear/traducir/crear contenido: alinear `PACKETVER` y recortar lo que el cliente no soporte. Ver [09-estado-tecnico-y-estabilidad.md](./09-estado-tecnico-y-estabilidad.md).
- **2026-11:** No reconstruir el cliente desde cero por ahora. No tocar el cliente ni comprar el 20210406 hasta que algo se rompa; seguir con el actual. El custom vive en `ozro-cli/patch/`. Ver [10-cliente-organizacion-y-pruebas.md](./10-cliente-organizacion-y-pruebas.md).
- **2026-11-16:** El contenido de Hercules **no se porta**: queda como referencia de ideas y lore. Todo NPC nuevo debe ser lore-friendly.
- **2026-11-16:** Primero balancear lo que ya está activo (bounties, repetibles, Garrett, monedas) y después agregar contenido nuevo.
- **2026-11-16:** Monedas OzRo por tiers (bronce/plata/oro/platino); usos de tiers altos se definen a medida que crece el contenido. El Alma de MVP se obtiene al cazar MVPs naturales (1/3/5/10/20 puntos según el tier fijo por ID; killer y party suman) y se reclama en El Guardián de Almas.
- **2026-11-16:** Arena MVP implementada en modo solo para T1, T2 y T3 accesible, con la Tejedora de Ecos en Sueños Tejidos y costo en Almas + keys. T4/T5 fuera de invocación. Ver [14-arena-mvp-invocador.md](./14-arena-mvp-invocador.md).
- **2026-11-16:** Garrett implementado con ofertas diarias y una misión por cuenta. El mercado NPC sin bots se resolverá con vending y un tasador/casa de empeño; `ragnabots` queda deprecado. El Gambler se reemplaza por refine safe con monedas OzRo (“si falla, no se rompe”).
- **2026-11-16:** No hay server de prueba; se prueba directo en producción con los 3 jugadores.
- **2026-11-16:** Lo implementado se borra de la documentación y queda en el changelog público (general) y en el git log (detalle técnico).
