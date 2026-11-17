# Quests de cambio de job

**Última revisión:** 2026-11-17
**Estado:** `pendiente`

Objetivo: que el cambio de job sea parte de la progresión (no un simple click), usando las quests con pasos reales, traducidas al español y con dificultad ajustada a un servidor de 3 jugadores sin mercado.

---

## Estado técnico verificado (2026-11-17)

### Primer job (1-1)

| Versión | Archivos | Comportamiento | Estado |
|---------|----------|----------------|--------|
| Renewal | `npc/re/jobs/1-1/*.txt` (6) | Hablar con el NPC y cambio inmediato, sin pruebas | **Activos** (`npc/re/scripts_jobs.conf:6-12`) |
| Pre-renewal | `npc/pre-re/jobs/1-1/*.txt` (6) | Quest completa con varios pasos y pruebas | **Activos solo en pre-re** (`npc/pre-re/scripts_jobs.conf:7-12`) |

Los archivos de pre-re existen en el repo y son los que tienen las pruebas por pasos:

| Job | Archivo | Líneas |
|-----|---------|--------|
| Acolyte | `npc/pre-re/jobs/1-1/acolyte.txt` | 470 |
| Archer | `npc/pre-re/jobs/1-1/archer.txt` | 248 |
| Mage | `npc/pre-re/jobs/1-1/mage.txt` | 699 |
| Merchant | `npc/pre-re/jobs/1-1/merchant.txt` | 1.156 |
| Swordman | `npc/pre-re/jobs/1-1/swordman.txt` | 642 |
| Thief | `npc/pre-re/jobs/1-1/thief.txt` | 539 |
| **Total** | | **3.754** |

### Resto de jobs

| Grupo | Archivos | Estado |
|-------|----------|--------|
| 1-1 expandido | `npc/jobs/1-1e/{gunslinger,ninja,taekwon}.txt`, `npc/re/jobs/1-1e/taekwon.txt` | **Activos** |
| 2-1 / 2-2 | 13 archivos en `npc/jobs/2-1/` y `npc/jobs/2-2/` | **Activos** (`npc/scripts_jobs.conf:10-33`) |
| Transcendidos 2-1a / 2-2a | 13 archivos | **Activos** (`npc/scripts_jobs.conf:17-41`) |
| 2-1e / 2-2e | `StarGladiator.txt`, `SoulLinker.txt` | **Activos** |
| 2e | `npc/re/jobs/2e/{kagerou_oboro,rebellion}.txt` | **Activos** |
| 3-1 / 3-2 | 13 archivos en `npc/re/jobs/3-1/` y `npc/re/jobs/3-2/` | **Activos** (`npc/re/scripts_jobs.conf:20-34`) |
| Doram | `npc/re/jobs/doram/spirit_handler.txt` | **Activo** |
| Novice / Super Novice | `npc/jobs/novice/supernovice.txt`, `npc/re/jobs/novice/supernovice_ex.txt` | **Activos** |
| Valkyrie (rebirth) | `npc/jobs/valkyrie.txt` | **Activo** |
| Novice Academy | `npc/re/jobs/novice/academy.txt` | **Desactivado** (`npc/re/scripts_jobs.conf:36`) |
| Quest de Novice | `npc/re/jobs/novice/novice.txt` | **Desactivado** (`npc/re/scripts_jobs.conf:37`) |
| Tutoriales de primera clase | `npc/quests/first_class/*.txt` (7) + `npc/re/quests/first_class/tu_archer.txt` | **Activos** |
| Jobmaster (cambio sin quest) | `npc/custom/jobmaster.txt` | **Desactivado** (`npc/scripts_custom.conf:11`) |

Consecuencias:

- El Jobmaster está apagado, así que el cambio de job ya depende de las quests.
- Las quests 1-1 de renewal son **de un solo paso**; las de pre-re son las que tienen pruebas.
- La Novice Academy está desactivada junto con sus warps/mobs (commit `8dd90b970`); no es parte de esta idea.

---

## Idea 1 — Usar las quests de primer job de pre-re `pendiente`

Se documenta la idea tal como surgió: **volver a habilitar las quests de first job solo si es fácil**. Aclaración: no se trata de reactivar algo inexistente, sino de **usar en renewal los archivos de pre-re** que ya están en el repo.

### Viabilidad (verificada)

| Punto | Resultado |
|-------|-----------|
| Archivos fuente | Existen: `npc/pre-re/jobs/1-1/*.txt` |
| IDs de quest | `1001`–`1014` ya existen en `db/re/quest_db.yml` |
| Mapas usados | Todos están en `conf/maps_athena.conf` (`job_sword1`, `job_thief1`, `izlude_in`, `prt_church`, `geffen_in`, etc.) |
| Funciones | `F_CanChangeJob` y `F_ClearJobVar` están en `npc/other/Global_Functions.txt` |
| `F_ToHigh` | Ya no se usa (los encabezados lo indican) |
| `F_MercKafra` | Definida dentro de `npc/pre-re/jobs/1-1/merchant.txt`; `kafras.txt` solo la llama con `!checkre(0)` |
| Monstruos/NPCs de prueba | Cada archivo define sus NPCs; swordman/thief spawnear monstruos propios y otros piden drops del mundo (archer, mage, merchant) |
| Dificultad de activación | **Fácil**: cambiar 6 líneas de include |
| Dificultad de validación | **Media**: probar las 6 quests en producción |

### Cambio necesario

En `npc/re/scripts_jobs.conf`, comentar las 6 líneas de `npc/re/jobs/1-1/` y agregar las 6 de `npc/pre-re/jobs/1-1/`.

**No cargar ambas versiones a la vez:** ocupan los mismos NPCs y coordenadas (por ejemplo, el Archer Guildsman en `payon_in02,64,71`), así que se duplicarían.

### Riesgos y pendientes

- [ ] Probar cada test con un PJ Novice nuevo en producción.
- [ ] Verificar que el cambio de job y las skills entregadas sean correctos (incluye High Novice y Baby Classes).
- [ ] Revisar si dos jugadores haciendo la prueba a la vez se molestan en los mapas compartidos (`job_sword1`, `job_thief1`).
- [ ] Revisar que las variables de quest no choquen con otras quests.
- [ ] Confirmar que el balance de las pruebas (stats bajos, mobs de test) sigue siendo razonable en renewal con rates 5x.
- [ ] Decidir si se mantiene además el tutorial `first_class` o si se desactiva para no duplicar el flujo de Novice.

**Recomendación:** sí es fácil de habilitar; el trabajo real está en probar las 6 quests y ajustar el balance. Si se habilita, es la versión que conviene traducir.

---

## Idea 2 — Traducir y balancear las quests de cambio de job `pendiente`

### Alcance

Son **58 archivos** y ~**60.000 líneas** de diálogo (más ~9.500 si se incluyen los tutoriales), así que es un proyecto grande y necesariamente **archivo por archivo**. Incluye:

- 1-1 de pre-re (6 archivos, 3.754 líneas) — la versión con pruebas
- 1-1 expandido (4 archivos)
- 2-1 / 2-2 y transcendidos (30 archivos)
- 2e / 2-1e / 2-2e (4 archivos)
- Rebirth y Super Novice (3 archivos)
- 3-1 / 3-2 (13 archivos)
- Doram (1 archivo)
- Tutoriales `first_class` (8 archivos, si se incluyen en el alcance)

### Orden sugerido

1. **Fase 1 — Nuevos jugadores:** 1-1 de pre-re, tutoriales `first_class`, Super Novice y Valkyrie.
2. **Fase 2 — Segundo job:** 2-1, 2-2, transcendidos, Soul Linker y Star Gladiator.
3. **Fase 3 — Tercer job:** 3-1, 3-2 y Doram (es la mayor parte del texto).
4. **Fase 4 — Expansiones:** Kagerou/Oboro, Rebellion, Ninja y Gunslinger.

### Reglas de traducción

- Traducir solo los textos visibles (`mes`, `select`, `mes` de menús); **no** tocar IDs, variables, nombres de NPC, `callfunc`, `getitem`, `delitem` ni coordenadas.
- Mantener el español en **ISO-8859-1/Latin-1**: el cliente actual muestra tildes, eñes y signos de apertura. No introducir UTF-8.
- Conservar la codificación del archivo original y no reinterpretar los nombres de recursos coreanos.
- Conservar los códigos de color (`^000000`, etc.) y los saltos/`next` en el mismo orden.
- Traducir una quest completa antes de pasar a la siguiente; no dejar archivos a medias.

### Reglas de balance ("más fáciles")

Revisar por archivo:

- [ ] **Items requeridos:** que se puedan obtener sin mercado (drops del server, NPCs, craft, repetibles).
- [ ] **Cantidades:** bajar si implican grindeo largo (ej. decenas de drops raros).
- [ ] **RNG:** eliminar tiradas que puedan fallar o garantizar el resultado.
- [ ] **Viajes:** acortar recorridos, agregar pistas o reducir vueltas entre mapas.
- [ ] **Recompensas:** coherentes con el esfuerzo; no regalar equipo que rompa la progresión.
- [ ] **Requisitos de nivel/skill:** alineados con los rates 5x y la progresión real de 3 jugadores.
- [ ] **Prueba en producción** al terminar cada quest.

### Riesgo de traducir in-place

Editar los archivos oficiales de rAthena genera conflictos al actualizar upstream. Antes de empezar hay que decidir:

- **A)** Traducir in-place y aceptar la divergencia (más simple, más conflicto).
- **B)** Mantener los archivos oficiales y crear una capa custom de duplicados (más limpio para updates, más trabajo y riesgo de NPCs duplicados).

Se deja como decisión abierta hasta la primera quest.

### Seguimiento por grupo

Marcar cada archivo al revisarlo. Estado inicial: todo `pendiente`.

| Grupo | Archivos | Traducido | Balanceado |
|-------|----------|-----------|------------|
| 1-1 pre-re | acolyte, archer, mage, merchant, swordman, thief | `pendiente` | `pendiente` |
| 1-1 expandido | gunslinger, ninja, taekwon (common) + taekwon (re) | `pendiente` | `pendiente` |
| 2-1 | assassin, blacksmith, hunter, knight, priest, wizard | `pendiente` | `pendiente` |
| 2-1a | AssassinCross, HighPriest, HighWizard, LordKnight, Sniper, WhiteSmith | `pendiente` | `pendiente` |
| 2-1e | StarGladiator | `pendiente` | `pendiente` |
| 2-2 | alchemist, bard, crusader, dancer, monk, rogue, sage | `pendiente` | `pendiente` |
| 2-2a | Champion, Clown, Creator, Gypsy, Paladin, Professor, Stalker | `pendiente` | `pendiente` |
| 2-2e | SoulLinker | `pendiente` | `pendiente` |
| 2e | kagerou_oboro, rebellion | `pendiente` | `pendiente` |
| 3-1 | archbishop, guillotine_cross, mechanic, ranger, rune_knight, warlock | `pendiente` | `pendiente` |
| 3-2 | genetic, minstrel, royal_guard, shadow_chaser, sorcerer, sura, wanderer | `pendiente` | `pendiente` |
| Rebirth / SN | valkyrie, supernovice, supernovice_ex | `pendiente` | `pendiente` |
| Doram | spirit_handler | `pendiente` | `pendiente` |
| Tutoriales `first_class` | tu_acolyte, tu_archer (x2), tu_magician01, tu_ma_th01, tu_merchant, tu_sword, tu_thief01 | `pendiente` | `pendiente` |

---

## Decisiones abiertas

- Si se habilita la 1-1 de pre-re, si se desactiva o mantiene el tutorial `first_class`.
- Traducción in-place vs. capa custom de duplicados.
- Si los tutoriales `first_class` y las skill quests entran en el alcance o se dejan en inglés.
- Si se traduce todo el 3-1/3-2 o solo los jobs que se juegan.

## Comentarios

<!-- Borrador libre para notas de job quests; luego organizar arriba -->
