# Arena MVP: instancia e invocador

**Estado:** `pendiente`  
**Objetivo:** crear una instancia de party donde el jugador gaste Almas de MVP para invocar un MVP fijo.

## Decisión principal

**Reutilizar un mapa existente como instancia.** No crear un mapa nuevo: eso requeriría editor, GRF, map cache y parche de cliente.

Mapa propuesto: **`quiz_00`**, la vieja arena de MVPs.

- Ya está cargado en `conf/maps_athena.conf`.
- El archivo `npc/custom/etc/mvp_arena.txt` está comentado, así que no tiene NPCs activos.
- La vieja arena usaba entrada en `quiz_00,50,24`.

## Entrada en la DB de instancias

Archivo: `db/import/instance_db.yml`

Propuesta inicial:

```yml
Body:
  - Id: 10001
    Name: OzRo MVP Arena
    TimeLimit: 1800
    IdleTimeOut: 300
    NoNpc: false
    NoMapFlag: true
    Destroyable: true
    Enter:
      Map: quiz_00
      X: 50
      Y: 24
```

- `NoNpc: false`: necesario para copiar nuestro NPC spawner.
- `NoMapFlag: true`: evita copiar el `noskill` de `quiz_00`.
- Los flags que queramos (`nobranch`, `nomemo`, `nosave`) se ponen en `OnInstanceInit`.
- `Id: 10001` es una propuesta; confirmar que no choque con instancias oficiales.

## NPCs

### NPC invocador en la ciudad

- Ubicación a definir; puede ser Prontera o Geffen.
- Solo el **líder de party** puede crear la instancia.
- Flujo:
  1. Elegir MVP invocable.
  2. Verificar y descontar Almas.
  3. `instance_create("OzRo MVP Arena")`.
  4. Si falla, devolver las Almas.
  5. Guardar el MVP elegido con `setinstancevar`.
  6. Disparar el spawn con `donpcevent`.
  7. Entrar con `instance_enter`.
- Si la party ya tiene una instancia activa, avisar y ofrecer entrar, no crear otra.

### NPC spawner dentro de la instancia

- NPC sobre `quiz_00` copiado a la instancia.
- `OnInstanceInit`:
  - Setear `nobranch`, `nomemo`, `nosave` y cualquier otro flag.
  - Preparar el estado de la arena.
- `OnSummon`:
  - Leer `getinstancevar('mvp_id, instance_id())`.
  - Invocar el MVP con:
    `monster instance_mapname("quiz_00"), x, y, ...`
  - Registrar el evento de muerte si hace falta.
- Agregar un NPC/portal de salida para volver a la ciudad.

## Comandos clave

- `instance_create("OzRo MVP Arena")`
- `instance_enter("OzRo MVP Arena")`
- `instance_id(IM_PARTY)`
- `instance_mapname("quiz_00")`
- `instance_npcname("#MVP_Spawner")`
- `setinstancevar('mvp_id, <id>, <instance_id>)`
- `getinstancevar('mvp_id, <instance_id>)`
- `donpcevent instance_npcname("#MVP_Spawner", <instance_id>) + "::OnSummon"`
- `setmapflag instance_mapname("quiz_00"), mf_nobranch`
- `setmapflag instance_mapname("quiz_00"), mf_nomemo`
- `setmapflag instance_mapname("quiz_00"), mf_nosave`

## Costos en Almas

Propuesta inicial, espejando dificultad:

| Dificultad | Costo |
|------------|------:|
| Normal | 1 Alma |
| Grande | 5 Almas |
| Enorme | 10 Almas |

- Definir si paga solo el líder o se reparte entre la party.
- Recomendación: paga el líder, porque es quien crea la instancia.
- La lista de MVPs invocables puede empezar chica y ampliarse después.

## Tracker

- Agregar al `MVP Tracker`:
  ```
  if (instance_id(IM_PARTY) > 0) end;
  ```
- Así ninguna kill dentro de una instancia modifica `MVP_KILL`, `MVP_SUPP` ni genera Almas.
- Esto también excluye MVPs de instancias oficiales; aceptable por ahora.
- Si más adelante se quieren registrar, hacerlo con variables separadas.

## Drops del MVP invocado

Decisión pendiente:

- Sin drops de MVP: más seguro contra loops.
- Drops normales: más divertido, pero puede ser rentable.
- Drops reducidos: opción intermedia.

Recomendación: empezar sin drops de MVP y revisar después.

## Archivos a tocar

- `db/import/instance_db.yml`
- `npc/custom/ozro/mvp_arena.txt` o `mvp_summoner.txt`
- `npc/scripts_custom.conf`
- `npc/custom/ozro/mvp_tracker.txt` (exclusión de instancias)
- Documentación/changelog del sitio cuando esté implementado.

## Pruebas

1. Líder crea la instancia; los miembros entran a la misma.
2. Un no-líder no puede crear.
3. Se descuentan las Almas correctas.
4. Si falla la creación, se devuelven las Almas.
5. El MVP aparece una sola vez.
6. El MVP no se puede volver a invocar sin pagar otra vez.
7. Salir/destroy de la instancia funciona.
8. Matar el MVP dentro de la instancia no modifica el registro del Tracker.
9. Reinicio del server: la instancia se pierde, pero las Almas y el registro quedan.
10. Probar en producción con la party real; no hay test server.

## Dificultad estimada

- Baja: entrada en `instance_db.yml`.
- Baja-media: crear/entrar con party.
- Media: spawner, flags, variables de instancia.
- Media: costos, refund, cooldown, salida.
- Total: **1–2 sesiones de trabajo**, sin tocar el cliente ni crear mapas.

## Pendientes antes de implementar

- Confirmar `quiz_00` y coordenadas de entrada/spawn.
- Definir lista inicial de MVPs invocables.
- Definir si paga el líder o la party.
- Definir drops del MVP invocado.
- Definir tiempo de instancia y cooldown.
- Confirmar que `Id: 10001` no choca con nada.
