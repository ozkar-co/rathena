# MVP Tracker, Journal y Almas de MVP

**Estado:** `pendiente`  
**Prioridad:** alta  
**Objetivo:** registrar kills y asistencias por MVP, mostrar progreso, entregar recompensas por tiers y abrir la economía del Alma de MVP.

> **Regla principal:** no renombrar las variables existentes. Las kills y asistencias viejas tienen que seguir contando.

## Variables que NO se tocan

| Variable | Alcance | Uso |
|----------|---------|-----|
| `MVP_KILL_<id>` | Personaje | Golpes finales contra ese MVP |
| `MVP_SUPP_<id>` | Personaje | Asistencias de party contra ese MVP |

Se leen y escriben con `getd` / `setd`, igual que en el script viejo de Hercules. El alcance sigue siendo por personaje; cambiar a cuenta perdería el historial existente.

Variables nuevas, solo para recompensas:

| Variable | Alcance | Uso |
|----------|---------|-----|
| `MVP_TIER_1_CLAIMED` ... `MVP_TIER_5_CLAIMED` | Personaje | Evita reclamar el mismo tier dos veces |

## Componentes

### 1. MVP Tracker (NPC invisible)

- Script global con `OnNPCKillEvent`.
- Detecta MVP con `getmonsterinfo(killedrid, MOB_MVPEXP)` y/o lista de MVPs.
- Incrementa `MVP_KILL_<id>` al killer.
- Si el killer está en party, recorre los miembros en el mismo mapa y suma `MVP_SUPP_<id>`.
- Anuncia la caza de MVPs naturales.
- **No cuenta** kills en mapas de invocación, arena o sala de branches. Lista de mapas excluidos configurable.
- No necesita escribir `mvplog`: el server ya lo registra y el radar de la web lo usa.

### 2. Journal (NPC visible)

- Una instancia principal en Prontera; se puede duplicar en otra ciudad si hace falta.
- Muestra:
  - Total de golpes finales.
  - Total de asistencias.
  - MVPs únicos cazados/asistidos.
  - MVP más cazado y MVP más asistido.
  - Lista paginada por MVP con kills y asistencias.
  - Progreso de tiers y botón de reclamo.
- Los tiers se calculan leyendo las variables viejas, así que el historial previo cuenta desde el primer día.

### 3. Almas de MVP

- Item actual: `MVP_Soul` (`35005`, “Alma de MVP”).
- Fuente principal: recompensas de tiers del Journal.
- Uso futuro:
  - Invocador de MVPs en un mapa fijo.
  - Ingrediente para fabricar Bloody Branches.
- Decisión pendiente: si el Alma es tradeable o account-bound. Por ahora se puede dejar tradeable.

## Tiers propuestos

Los tiers son **acumulativos** y se reclaman una vez por personaje.

| Tier | Golpes finales | Asistencias | MVPs únicos | Recompensa |
|------|---------------:|------------:|------------:|------------|
| 1 | 5 | 10 | — | 25.000 zeny + 3 Ozro Bronze |
| 2 | 25 | 50 | 5 | 1 Alma de MVP + 50.000 zeny |
| 3 | 75 | 150 | 15 | 2 Almas de MVP + 100.000 zeny |
| 4 | 150 | 300 | 30 | 3 Almas de MVP + 1 Ozro Silver |
| 5 | 300 | 600 | 45 | 5 Almas de MVP + 1 Ozro Gold |

- “Golpes finales **o** asistencias”: el jugador avanza por cualquiera de las dos vías.
- Los MVPs únicos se cuentan sumando kills y asistencias por ID distinto.
- Los valores son una primera propuesta; se ajustan después de ver el historial real.

## Invocador futuro

- Mapa fijo del overworld por ahora; instancia/arena privada más adelante.
- Lista de MVPs invocables con costo en Almas:
  - MVP fácil: 1 Alma.
  - MVP medio: 2–3 Almas.
  - MVP difícil: 4–5 Almas.
- El jugador elige un MVP fijo; no es RNG puro como Bloody Branch.
- Los MVPs invocados en el mapa de invocación **no cuentan** para el Tracker ni para los tiers.
- Decidir si dejan drops normales, drops de MVP reducidos o ningún drop de MVP para evitar loops.

## Bloody Branches

- Las Almas de MVP serán ingrediente de la receta de `Bloody_Dead_Branch`.
- La receta exacta queda pendiente; no implementar hasta definir el costo.
- Las kills de branches se deben probar en el mapa/sala de invocación para que no alimenten el Tracker.

## Lista de MVPs

- El script viejo de Hercules tenía 58 MVPs; la lista actual del server es más grande.
- Para el Tracker conviene detectar por `MOB_MVPEXP` y guardar `MVP_KILL_<id>` de cualquier MVP.
- Para los tiers de “MVPs únicos” usar la lista de MVPs naturales que ya usa el radar de la web, no la lista vieja.
- El Journal puede mostrar todos los MVPs con registros, aunque el denominador de únicos use solo los naturales.

## Orden de implementación

1. Generar la lista de MVPs actuales y los datos de tiers.
2. Implementar el Tracker invisible conservando `MVP_KILL_<id>` y `MVP_SUPP_<id>`.
3. Implementar el Journal: resumen, lista por MVP y reclamo de tiers.
4. Entregar Almas de MVP por tiers.
5. Agregar el Invocador en mapa overworld y excluir ese mapa del Tracker.
6. Definir la receta de Bloody Branch y la sala/instancia.
7. Evaluar estadísticas por personaje en la web.

## Pruebas

- Kill individual de un MVP: sube `MVP_KILL_<id>`.
- Kill en party: killer recibe kill; miembros en el mismo mapa reciben `MVP_SUPP_<id>`.
- Miembro en otro mapa no recibe asistencia.
- Los tiers leen datos viejos y se reclaman una sola vez.
- Un MVP invocado o de branch en el mapa excluido no modifica variables.
- Reinicio del server: variables y reclamos persisten.
