# Sistemas core (prioritarios)

Sistemas que unifican el diseño. El **Card Collector** es el modelo a seguir.

## 1. Meta por cuenta `implementado` (parcial) → expandir

### Qué ya funciona

**Card Collector** (`npc/custom/ozro/card_collector.txt`):
- Variables de cuenta: `#CARD_SEEN_*`, `#CARD_CT_*`
- Progreso % por categoría
- Meta largo plazo, no depende de nivel ni de estar online con otros

### Qué falta

| Variable / concepto | Uso propuesto | Estado |
|-------------------|---------------|--------|
| `#PRESTIGE` | Puntos de prestigio (challenges, lore, eventos) | `pendiente` |
| `#CHALLENGE_ACTIVE` | Challenge en curso | `pendiente` |
| `#CHALLENGE_DONE_*` | Challenges completados | `pendiente` |
| `#LORE_ARC_*` | Arcos oficiales completados | `pendiente` |
| `#MAIN_ACCOUNT` | Flag cuenta principal (opcional) | `pendiente` |

### Política de cuentas

- **Objetivo:** Una cuenta principal por jugador real.
- **Problema actual:** ~3 cuentas c/u + multi-login para party → entorpece todo.
- **Enfoque:** Recompensas significativas solo en cuenta principal; alts sin multiplicar prestigio/colección/challenges.
- **No prohibir** multi-cuenta de golpe; hacer que no compense para metas.

## 2. Challenges por cuenta `pendiente` — **prioridad alta**

> Llevar un PJ con restricciones de build/dificultad a nivel alto, con cosas que hacer en cada rango. Equipo único por cadena determinista, no RNG ni pay2win.

### Estructura propuesta

```
Challenge (por cuenta)
├── ID y nombre (ej. "El Camino del Acolyte")
├── Restricciones
│   ├── Clase(s) permitida(s)
│   ├── Equip (solo white, sin MVP cards, etc.)
│   ├── Party (solo / máx 2 / libre)
│   └── Reset (permitido / prohibido durante challenge)
├── Hitos por nivel
│   ├── Nv 30 → quest / craft / bounty específica
│   ├── Nv 50 → ...
│   └── Nv 70+ → instancia / boss / arco lore
├── Recompensas (cosméticas / prestigio, no power creep)
│   ├── Título / fame
│   ├── Headgear trofeo (stats modestos o ninguno)
│   ├── Acceso a "casa" / vitrina
│   └── Puntos `#PRESTIGE`
└── Visible en web (perfil de cuenta)
```

### Equipamiento sin RNG

Cadena por tier (por hito de challenge):

1. Farmear materiales (bounties, repetibles, mobs del bracket)
2. NPC artesano → pieza base (barter)
3. Quest corta → mejora (+refine acotado, slot, bonus modesto)
4. Pieza final = trofeo del challenge (item existente al inicio; custom más adelante)

### Piloto sugerido

Primer challenge a definir según feedback de juego:
- Clase, nivel objetivo, restricciones
- 4–5 hitos
- 1 recompensa cosmética clara

**Comentarios:**

<!-- Definir aquí el primer challenge piloto -->

## 3. Loop entre vacaciones `pendiente`

Actividades de **15–30 min** con progreso real:

| Actividad | Esfuerzo | Progreso |
|-----------|----------|----------|
| Registrar cartas | 2 min | % colección |
| 1 bounty o repetible | 10–15 min | Materiales / zeny |
| Consultar cronista | 3 min | Siguiente paso lore |
| Instancia solo (tuneada) | 20 min | Hito challenge |
| Ver perfil en web | 0 min in-game | Social / motivación |

## 4. Competencia justa entre jugadores `reformular`

**Dejar de usar como meta principal:** zeny total, MVP kills, EXP máxima.

**Métricas por cuenta:**

| Categoría | Mide | Justicia |
|-----------|------|----------|
| Colección cartas | % archivo | Ya implementado |
| Challenges | Completados | No depende de tiempo de farm |
| Arcos lore | Capítulos | Exploración |
| Variedad | N clases > nivel X | Incentiva resets/roles |
| Soporte | Puntos heal/buff en MVP | No solo DPS |
| Prestigio total | Suma ponderada | Meta global |

## 5. Casa / vitrina (sin client) `pendiente`

RO no tiene housing real sin client. Alternativas server-side:

1. **Instancia privada por cuenta** — mapa con warp exclusivo; NPCs muestran progreso
2. **Títulos visibles** — fame o variables al clickear personaje
3. **Headgears trofeo** — recompensa challenge, sin stats absurdos
4. **Museo NPC** en Prontera — vitrina de los 3 jugadores
5. **Web** — perfil principal (ver [07-web-api.md](./07-web-api.md))

Ideas del doc viejo a integrar:
- Decorar con dolls del juego
- Storage ampliado / cofres múltiples (viable con pocos jugadores)
- Contratar NPCs de servicio (pagar mantenimiento)
- Vitrina de cartas para enseñar a otros

## 6. Economía cerrada `pendiente`

Sin jugadores vendiendo, el mercado = NPCs:

- **Monedas OzRo por tiers** (bronce, plata, oro, platino). No hace falta definir todos los usos ahora; se van habilitando a medida que se implementa contenido de nivel más alto.
- **Garrett** como entrada de la economía de basura: 5 ofertas diarias y 1 misión por cuenta, con rareza por oferta. `ragnabots` quedó deprecado; no se usa como fuente principal de precios.
- **Tasador / casa de empeño** para objetos que no son chatarra: tasación, negociación y consignación. Ver [13-mercado-npc-tasador.md](./13-mercado-npc-tasador.md).
- **Alma de MVP** se obtiene al cazar MVPs naturales (1/3/5/10/20 puntos según el tier fijo por ID; killer y party suman), reclamables en El Guardián de Almas; uso futuro en el invocador y en la receta de Bloody Branches.
- **Barter shops**: `descartado` — se quitan para simplificar; el equip se obtiene por craft/quests específicas.
- `points2zeny.txt` — puente cash ↔ zeny (revisar ratio); los points existían porque antes no sabíamos modificar drops.
- `card_collector` + trader de cartas — sinks/faucets; **preservar los datos existentes**.
- **Resurrection con costo de item**: igual que Call Homunculus, que ya gasta `Germination_Breed` + `Yggdrasilberry_Dew`; debe ser caro pero no prohibitivo. Definir item/cantidad y si aplica solo a `ALL_RESURRECTION` o también a `AM_RESURRECTHOMUN`.
- Materiales de bounties/repetibles → craft de equip challenge.
- **No regalar** items de builds de internet ni objetos de donación sin una cadena de lore/crafting.

## 7. Reset de personaje `implementado` → simplificar

**Actual:** `resetnpc.txt` — Canalizadora Mística, birthstone + 100k zeny.

**Tensión:** Reset difícil vs. incentivo multi-PJ.

**Dirección:** Reset barato/fácil; dificultad en challenges y progresión de equip. El doc viejo tenía reset **una vez por personaje** — hoy es repetible con birthstone.

### Pergaminos de habilidad (item custom) `pendiente`

Para reducir la doble cuenta: consumibles **fabricables** (como el Alquimista fabrica pociones) que dan acceso puntual a skills de otro job. Se craftean recolectando items; **sin penalizaciones fuertes** — la dificultad está en conseguir los materiales. Relacionado con los sets custom del [backlog](./08-ideas-backlog.md) y con [05-quests-custom.md](./05-quests-custom.md).

## 8. Qué dejar de hacer

- [ ] Regalar items endgame de wikis
- [ ] Competir solo por MVP kills / zeny
- [ ] Rush a max level como única meta
- [ ] Esperar balance perfecto antes de jugar
- [ ] Implementar contenido nuevo antes de balancear lo que ya está activo
- [ ] Agregar sistemas/ventanas que no aporten a la jugabilidad

## 9. Orden de trabajo

- **No hay server de prueba.** Se prueba directo en producción con los 3 jugadores; si algo falla, se corrige o se apaga el server.
- Antes de agregar NPCs/quests nuevas, balancear bounties, repetibles, Garrett y monedas existentes.
- Bounties que dan casi 1 nivel se aceptan; las que dan 2 niveles se corrigen.
- Las repetibles se mantienen para que los PJ nuevos puedan subir con ayuda de los fuertes.
- El zeny de bounty debe escalar por nivel/banda, no ser un monto fijo.
- Cada bloque implementado se borra de la documentación y se registra en el changelog público y en el git log.

## Comentarios

<!-- Borrador libre para ideas de sistemas; luego organizar arriba -->
