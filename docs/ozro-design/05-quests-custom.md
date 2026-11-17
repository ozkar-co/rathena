# Quests custom

## Principio de diseño

Las quests deben ser **lore-friendly**. Se puede tomar inspiración de servidores con más recorrido (**Xatiya**, **Atlantis**, etc.) e ir migrando ideas según las descripciones publicadas, pero el contenido de Hercules **no se porta**.

La fuente de verdad técnica es la documentación oficial de rAthena (`doc/script_commands.txt`, `doc/item_db.txt`) para la versión actual.

## Crimson Weapons `descartado` como port

**Decisión 2026-11-16:** no se porta la cadena de Crimson de Hercules.

- En Hercules las Crimson estaban rotas; por eso se armó una quest con lore para poder obtenerlas.
- En rAthena actual ya se consiguen por vías oficiales, así que la quest dejó de ser necesaria.
- La lore de Marcus y la cadena queda como **referencia de diseño**: fue un buen ejemplo de cómo una historia puede desbloquear objetos nuevos.
- A futuro se puede heredar esa idea para fabricar objetos que normalmente se conseguían por donación, usando **partes especiales custom**.
- Ya sabemos modificar drops de mobs; no hace falta inventar “points” para justificar la obtención de items.

### Lore de referencia (no implementar como port)

- La traición del mercader.
- El pasado del asesino del katar.
- La conexión secreta del wizard con la esencia.
- Las decisiones morales del jugador.
- La redención de Marcus.
- Punto de inicio original: guardia al noreste de la plaza principal de **Izlude**.

### Futuro: fabricación con lore `pendiente`

- Crear objetos custom como **“partes especiales”** que se obtengan de drops, quests o actividades.
- Usarlas en cadenas de crafting con lore, no en tiendas planas.
- Apuntar a objetos que antes eran de donación o de eventos, no a power creep.
- La dificultad debe estar en conseguir materiales y desbloquear la historia, no en RNG de romper equipo.

---

## Otras quests custom planificadas

### Equipo “pro” con lore `pendiente`

Diseñar cada quest y darle lore. Alineado con **challenges por cuenta** — no regalar equip de wiki.

### Hungry Weapons `reformular`

Armas encantadas que “piden” cacerías; al completar suben de nivel y daño. Similar a armas que evolucionan — ver backlog.

### Quest desbloquea cacería del tesoro `pendiente`

Serie de pistas por el mundo → explorador → llaves + ubicación del tesoro. Conectar con Treasure Hunter (evento semanal).

### Blessed Ores `pendiente`

Quest con lore para crear Blessed Ores en lugar de Safe tickets.

### Partes especiales / fabricación de objetos de donación `pendiente`

- Objetos custom que se obtienen por drops, quests o crafting.
- Se usan como componentes para fabricar equipo especial que antes era de donación.
- Debe tener lore y una cadena de desbloqueo; no una tienda directa.
- Evaluar qué objetos del juego actual conviene convertir en fabricables.

### Objetos custom con skills de otros jobs `reformular`

Consumibles fabricados por el job con quest y requisito de nivel, para no usar cuentas dobles. Ver **pergaminos de habilidad** en [03-sistemas-core.md](./03-sistemas-core.md).

### Ritual oscuro (Alma / SoulStone) `reformular`

- Subir un PJ a **nivel 70**, sacrificarlo → vuelve a **Novice 1/1**.
- El alma queda **atada a la cuenta**; otro PJ puede **consumirla a cambio de EXP**.
- **Cooldown:** 1 semana. **Requisito:** exige un job específico.
- Tensión: ¿choca con la filosofía de reset fácil? Ver [03-sistemas-core.md](./03-sistemas-core.md).

---

## Quests repetibles y bounties

Ya activas — base para materiales de craft/challenges:

- 18 repetibles en `npc/custom/ozro/repeteables/`
- 26 bounty boards en `npc/custom/ozro/bounty/`

### Ajustes pendientes del doc viejo

- [ ] Bajar precios de Hunting Missions a la mitad (cuando se reactive).
- [ ] Daily hunting con racha de recompensas crecientes.

---

## Comentarios

<!-- Borrador libre para ideas de quests; luego organizar arriba -->
