# MVP Tracker, Journal y Almas de MVP

**Estado:** tracker, Journal y reclamo de Almas implementados; invocador pendiente
**Prioridad:** alta  
**Objetivo:** registrar kills y asistencias por MVP, mostrar el historial y convertir ese progreso en Almas de MVP de forma repetible.

> **Regla principal:** no renombrar las variables existentes. Las kills y asistencias viejas tienen que seguir contando.

## Variables

### Variables que NO se tocan

| Variable | Alcance | Uso |
|----------|---------|-----|
| `MVP_KILL_<id>` | Personaje | Golpes finales contra ese MVP |
| `MVP_SUPP_<id>` | Personaje | Asistencias de party contra ese MVP |

Se leen y escriben con `getd` / `setd`, igual que en el script viejo de Hercules. El alcance sigue siendo por personaje; cambiar a cuenta perdería el historial existente.

### Variable nueva

| Variable | Alcance | Uso |
|----------|---------|-----|
| `MVP_SOUL_CLAIMED` | Personaje | Total de Almas ya reclamadas |

No hace falta un contador de puntos: los puntos se calculan desde `MVP_KILL_<id>` y `MVP_SUPP_<id>` cada vez que el Journal los necesita. Así el historial viejo cuenta desde el primer día.

## Componentes

### 1. MVP Tracker (NPC invisible) `implementado`

- Archivo: `npc/custom/ozro/mvp_tracker.txt`.
- Script global con `OnNPCKillEvent`.
- Detecta MVP con `getmonsterinfo(killedrid, MOB_MVPEXP)` y `MD_MVP`.
- Incrementa `MVP_KILL_<id>` al killer.
- Si el killer está en party, recorre los miembros en el mismo mapa y suma `MVP_SUPP_<id>`.
- No entrega premios ni anuncia nada: solo trackea.
- **Pendiente:** excluir mapas de invocación, arena o sala de branches cuando existan.
- No necesita escribir `mvplog`: el server ya lo registra y el radar de la web lo usa.

### 2. Journal (NPC visible) `implementado`

- Ubicación: Prontera (150, 180).
- Archivo: `npc/custom/ozro/mvp_journal.txt`.
- Muestra:
  - Total de golpes finales.
  - Total de asistencias.
  - MVPs únicos cazados/asistidos.
  - MVP más cazado y MVP más asistido.
  - Lista paginada por MVP con kills y asistencias.
  - Puntos de Alma pendientes y reclamo repetible.
- No hay tiers ni recompensas de una sola vez. Todo el valor sale del farmeo de MVPs.

### 3. Almas de MVP

- Item actual: `MVP_Soul` (`35005`, “Alma de MVP”).
- **Killer y party en el mismo mapa suman los puntos completos.** Con 3 jugadores, un MVP puede generar 3 veces los puntos; es intencional para que el soporte también reciba recompensa.
- El multicuenta/doble login puede multiplicar puntos. Se acepta por ahora; si se rompe la economía, se ajusta.
- Los puntos se reclaman en el Journal y se convierten 1:1 en items `Alma de MVP`.
- El reclamo es repetible y sin cap.
- Si el inventario está lleno, no se entrega el reclamo hasta que haya espacio.
- Uso futuro:
  - Invocador de MVPs en un mapa fijo.
  - Ingrediente para fabricar Bloody Branches.
- Decisión pendiente: si el Alma es tradeable o account-bound. Por ahora se puede dejar tradeable.

### Puntos por kill según dificultad

Usar `MvpExp` del mob como medida de dificultad:

| Dificultad | MvpExp | Puntos por kill | Costo de invocación |
|------------|-------:|----------------:|--------------------:|
| Normal | < 500.000 | 1 | 1 |
| Grande | 500.000–1.500.000 | 5 | 5 |
| Enorme | > 1.500.000 | 10 | 10 |

- La mayoría de los MVPs queda en 1 punto: **39 de los 63 MVPs naturales**.
- Los MVPs grandes dan y cuestan más: 12 en 5 puntos y 12 en 10 puntos.
- Los guild dungeons cuentan como naturales.
- Para MVPs con `MvpExp` 0 se usa el nivel: <120 = 1, 120–179 = 5, >=180 = 10.
- Los 58 MVPs restantes de la DB son de instancia, invocación, evento u otros y no entran en este ciclo.
- Las kills en mapas de invocación/branches **no** entregan puntos ni cuentan para el Tracker.

### Cálculo de Almas

El cálculo es **por MVP, nunca sobre el total global**:

```
total = 0
para cada MVP natural:
    total = total + ((MVP_KILL_<id> + MVP_SUPP_<id>) × puntosDeEseMVP)
```

Ejemplo:

| MVP | Dificultad | Kills | Asistencias | Puntos |
|-----|-----------:|------:|------------:|-------:|
| Golden Thief Bug | 1 | 10 | 0 | 10 × 1 = 10 |
| Ifrit | 10 | 1 | 0 | 1 × 10 = 10 |
| **Total** | | | | **20** |

No son 11 eventos × 10 = 110, ni 200. Cada MVP se multiplica solo por su propia dificultad y después se suman los resultados.

- El killer suma por `MVP_KILL`.
- Cada miembro de party en el mismo mapa suma por `MVP_SUPP`.
- `MVP_SUPP` ya incluye las asistencias históricas, así que también generan Almas.
- El Journal suma todos los MVPs y resta `MVP_SOUL_CLAIMED`.
- Al reclamar, entrega esa diferencia como Almas y suma el total a `MVP_SOUL_CLAIMED`.

## Invocador futuro

- Mapa fijo del overworld por ahora; instancia/arena privada más adelante.
- Lista de MVPs invocables con costo en Almas, espejando la dificultad:
  - Normal: 1 Alma.
  - Grande: 5 Almas.
  - Enorme: 10 Almas.
  - Jefes especiales: más de 10 Almas si se agregan.
- El jugador elige un MVP fijo; no es RNG puro como Bloody Branch.
- Los MVPs invocados en el mapa de invocación **no cuentan** para el Tracker.
- Decidir si dejan drops normales, drops de MVP reducidos o ningún drop de MVP para evitar loops.

## Bloody Branches

- Las Almas de MVP serán ingrediente de la receta de `Bloody_Dead_Branch`.
- La receta exacta queda pendiente; no implementar hasta definir el costo.
- Las kills de branches se deben probar en el mapa/sala de invocación para que no alimenten el Tracker.

## Lista de MVPs

- La DB tiene **121 mobs con `MvpExp`**.
- Los MVPs naturales (spawn no-instancia) son **75 entradas de spawn**, pero solo **63 IDs únicos**: algunos MVPs aparecen en varios mapas.
- La página del radar muestra ~74 entradas porque cuenta por mapa; para variables y cálculo de Almas hay que usar los **63 IDs únicos**.
- La diferencia entre 74 y 75 es un duplicado/filtro del spawn; no cambia el conteo único.
- El script viejo de Hercules tenía 58 MVPs; no se usa como denominador actual.
- Para el Tracker conviene detectar por `MOB_MVPEXP`/`MD_MVP` y guardar `MVP_KILL_<id>` de cualquier MVP.
- El Journal puede mostrar todos los MVPs con registros, aunque el cálculo de Almas use solo los naturales.
- Si se agrega o elimina un spawn, hay que regenerar la lista de naturales.

## Pruebas

- Kill individual de un MVP: sube `MVP_KILL_<id>`.
- Kill en party: killer recibe kill; miembros en el mismo mapa reciben `MVP_SUPP_<id>`.
- Miembro en otro mapa no recibe asistencia.
- El Journal calcula puntos con datos viejos sin migración.
- Reclamar Almas reinicia el pendiente y suma a `MVP_SOUL_CLAIMED`.
- Si no hay espacio, no se entrega el reclamo.
- Reinicio del server: variables y reclamos persisten.
