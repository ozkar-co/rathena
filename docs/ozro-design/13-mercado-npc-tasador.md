# Mercado NPC: tasador y casa de empeño

**Estado:** `pendiente`  
**Contexto:** `ragnabots` quedó deprecado. No se van a usar bots para emular el mercado; la idea es resolverlo con NPCs.  
**Relacionado:** [04-npcs.md](./04-npcs.md), [07-web-api.md](./07-web-api.md), [15-vendedor-viajero.md](./15-vendedor-viajero.md)

## Objetivo

Dar salida a objetos que no encajan en el vending ni en la compra de chatarra, sin depender de una población grande de jugadores.

- **Vending:** ya existe una solución definida aparte.
- **Tasador / casa de empeño:** para objetos de más valor o de venta lenta.
- La tasación puede tardar minutos u horas: la espera es parte de la experiencia, no un problema técnico.

## Modelo elegido: tasación asíncrona con custodia

El NPC no calcula precios. Recibe un objeto, guarda una copia completa de sus datos y lo destruye; un proceso externo calcula la tasación; el jugador vuelve más tarde a aceptar o rechazar la oferta.

### Flujo

1. El jugador entrega **un solo objeto** al tasador.
2. El NPC guarda el snapshot completo del objeto en una tabla de solicitudes y lo elimina del inventario.
3. Un proceso externo (o la web) calcula el precio y actualiza la solicitud.
4. El jugador vuelve al NPC pasado el tiempo de espera.
5. El NPC muestra la oferta:
   - **Acepta:** recibe el zeny y la solicitud se cierra como pagada.
   - **Rechaza:** el objeto se devuelve por correo al personaje que lo entregó.
6. La web puede ofrecer un **simulador** que muestra el precio sin esperar, pero vender siempre exige pasar por el NPC y esperar.

### Por qué así

- El NPC queda ligero: una escritura al entregar y una lectura indexada al reclamar. No hace polling ni llama a la web desde el map-server.
- El cálculo pesado vive fuera del map-server.
- La espera se puede dosificar por rareza o por precio.
- La web no otorga nada: solo informa, así que no introduce riesgo de duplicación.

## Objetos aceptados

La custodia obliga a poder reconstruir el objeto **exactamente**. Todo lo que no se pueda devolver con fidelidad se rechaza en la primera versión.

| Categoría | ¿Aceptar? | Motivo |
|---|---|---|
| Equipo/ETC comerciable, identificado | Sí | Caso base |
| Cartas, refine y random options | Sí, si la valuación los soporta | `mail` y `getitem4` permiten devolverlos |
| Enchant grade > `ENCHANTGRADE_NONE` | No | `mail` no expone el grade; se perdería al devolver |
| Bound | No | No es comerciable y no debe venderse |
| Rental / `expire_time > 0` | No | Ningún comando script fija el `expire_time` original |
| Stackables con `amount > 1` | No en v1 | La recuperación tras un crash es ambigua |
| Quest / instance / untradeable / unobtainable | No | Regla ya existente del mercado |
| Objetos con script especial o que dependan de `unique_id` | No | El `unique_id` no se conserva al recrear |
| Precio fuera de mínimo/máximo | No | El tasador no compra cualquier cosa a cualquier precio |

Nota sobre **enchant grade**: es el grado de encantamiento del equipo (`ENCHANTGRADE_NONE/D/C/B/A`), un bonus adicional distinto del refine y de las random options. En rAthena aparece como `enchantgrade` en el ítem, en `@inventorylist_enchantgrade[]` y como parámetro de `getitem4`, pero el comando `mail` no lo recibe. Por eso los objetos con grade quedan fuera hasta que exista una devolución que lo conserve.

## Arquitectura

### NPC (map-server)

- Al entregar: valida el objeto, escribe el snapshot y el bloqueo por cuenta, y elimina el objeto.
- Al reclamar: lee **una** solicitud abierta por `account_id` y actúa según el estado.
- Nunca hace polling ni espera activa.
- Las consultas son por clave indexada y con `LIMIT 1`; nada de escaneos ni de traer muchas filas.
- Los IDs vienen de `getinventorylist` y son numéricos: no se concatenan strings del jugador en SQL. Si alguna vez hace falta un string, se usa `escape_sql`.
- La variable de cuenta (`#`) puede usarse para la UI, pero **la fuente de verdad es la tabla**; una variable sucia por un crash no debe bloquear ni desbloquear nada por sí sola.

### Worker externo

- Lee solicitudes en estado `removed` y calcula el precio.
- Actualiza con compare-and-set (`WHERE id = ? AND state = 'removed'`) para no tasar dos veces.
- Es idempotente y puede correr como cron; no necesita estar siempre arriba.
- Si no puede valuar el objeto, lo marca para devolución.

### Web

- El simulador lee **la misma fuente de precio** que el worker. Si muestra un precio distinto al que paga el NPC, se rompe la confianza.
- No escribe en la cola ni otorga items.
- Solo muestra precios de objetos aceptados; no expone datos de otros jugadores.

## Persistencia

### Tabla de solicitudes

Campos mínimos del snapshot:

- `id`, `account_id`, `char_id`, `char_name`.
- `state`.
- `item_nameid`, `amount`, `identify`, `refine`, `attribute`.
- `card0..card3`.
- `option_id1..5`, `option_val1..5`, `option_param1..5`.
- `bound`, `expire_time`, `enchantgrade` (se guardan aunque en v1 se rechacen, para auditoría).
- `fingerprint` del inventario antes de borrar (para recuperación).
- `price`, `requested_at`, `priced_at`, `closed_at`.
- `mail_token` (identificador único para verificar la devolución).

La unicidad de solicitud abierta por cuenta se impone con un índice único sobre una tabla de solicitudes abiertas, archivando las cerradas en una tabla histórica. No se confía solo en una variable de cuenta.

### Bitácora de eventos

Tabla append-only con `request_id`, estado anterior, estado nuevo, actor (`npc`, `worker`, `gm`), timestamp y detalle. Es lo que permite reconstruir qué pasó cuando algo queda raro.

## Máquina de estados

| Estado | Significado | Acción | Recuperación tras crash |
|---|---|---|---|
| `incoming` | Snapshot y bloqueo escritos; el objeto todavía está en el inventario | Eliminar el objeto y pasar a `removed` | Si el objeto exacto sigue presente: reintentar el borrado. Si no está: asumir `removed`. Si es ambiguo (stackable o copias idénticas): `locked` |
| `removed` | El objeto ya salió del inventario | Esperar al worker | Continuar; el worker lo tomará |
| `priced` | Hay oferta | Mostrar oferta al jugador | Continuar |
| `paying` | Se marcó la intención de pagar | Sumar zeny y pasar a `paid` | **No pagar automáticamente**; el GM verifica y completa si hace falta |
| `paid` | Terminal: objeto vendido y zeny entregado | — | — |
| `returning` | Se marcó la intención de devolver | Enviar correo y pasar a `returned` | Buscar `mail_token` en la tabla de correo: si existe, marcar `returned`; si no, el GM reenvía |
| `returned` | Terminal: objeto devuelto por correo | — | — |
| `cancelled` | Terminal: se canceló antes de borrar | — | — |
| `expired` | Venció el plazo sin reclamar | Si el objeto sigue en custodia, iniciar `returning` | Igual que `returning` |
| `locked` | Requiere revisión manual | Bloquear solo a esa cuenta | GM inspecciona snapshot, inventario y bitácora |

### Reglas de transición

- **Marcar antes de actuar** en pagos y devoluciones: primero `paying`/`returning`, después la acción, después `paid`/`returned`.
- **At-most-once** para pagos y correos: ante un crash en medio, se prefiere no pagar/no enviar y que el GM complete, antes que pagar dos veces. La inflación es peor que una revisión manual.
- El borrado del objeto es la última acción de la sección crítica de entrega: `incoming` se escribe antes, `removed` después.
- No hay atomicidad entre el inventario en memoria y SQL; por eso existen `incoming`/`removed` y la recuperación por fingerprint.

### Bloqueo

- El bloqueo es **por cuenta**, no global: un crash deja “ocupado” al jugador afectado, no al NPC entero.
- La consulta de estado filtra por `account_id` y estados abiertos.
- **Límite:** una solicitud abierta por cuenta.
- **Reclamo:** solo el `char_id` que entregó el objeto puede aceptar, rechazar o reclamar el correo.

## Devolución al jugador

rAthena no tiene un comando `rodex_*` en script. La devolución se hace con **`mail`** (`doc/script_commands.txt:5963`), que envía a un `char_id` y funciona con el personaje desconectado.

- Soporta id, amount, refine, bound, cartas y las 5 random options.
- **No** recibe `enchantgrade` ni `expire_time`; de ahí las restricciones de objetos aceptados.
- `MAIL_MAX_ITEM` es 5 en PACKETVER moderno (`src/common/mmo.hpp:196`); una solicitud es un solo objeto, así que sobra.
- Si el inventario está lleno, el objeto queda en el correo; no se pierde.
- El correo caduca: no es custodia permanente. Hay que definir plazo y aviso, y dejar herramienta de GM para reenviar.

Para que la devolución sea verificable, el asunto o cuerpo del correo lleva un token único (`PAWN#<request_id>`). Antes de reenviar, se consulta la tabla de correo por ese token.

## Trazabilidad y operación

- Snapshot inmutable + bitácora de eventos.
- Herramienta de GM para: ver solicitudes por cuenta/personaje, inspeccionar el snapshot, reenviar correo, completar un pago, desbloquear una cuenta.
- En un servidor pequeño se acepta revisar caso por caso; lo que no se acepta es perder la trazabilidad.
- Los casos realmente irreconciliables son pocos: crash en `incoming` con un stackable o copias idénticas, y crash en `paying`.

## Valuación

La idea es cruzar **dificultad de obtención** con **datos de mercado limpios**. El modelo asíncrono no cambia la valuación; solo cambia cuándo y dónde se calcula.

- La rareza interna del servidor sigue siendo la base: drop rate, spawn, acceso, quest/craft, instancia y utilidad.
- La taxonomía de items (`ozro-site/assets/items/taxonomy.json`) puede servir de base.
- Los precios de mercado se pueden usar como **señal secundaria**, no como ancla.
- La oferta puede ser un precio fijo o un rango; la negociación queda para una fase posterior.

### Limpieza de datos de mercado

Antes de usar la lista de precios hay que descartar o corregir:

- Publicaciones de un solo objeto a precio absurdo para “reservar plaza”.
- Precios sin ventas reales o con datos viejos.
- Outliers extremos; usar mediana o media recortada en vez de promedio.
- Items con muy pocas observaciones.
- Diferencia entre precio publicado y precio real de venta.
- Duplicados, nombres ambiguos y variantes del mismo item.

### Objetos compuestos

El tasador no solo verá items base. También debe estimar:

- Cartas.
- Equipo refinado (+1 a +10 o más).
- Equipo con una o varias cartas.
- Equipo con encantamientos u opciones aleatorias.
- Combinaciones de refine + cartas + encantamiento.

La valuación de un objeto compuesto podría ser:

```
valor = valorBase
      + premioPorRefine
      + valorDeCartas
      + premioPorSlots
      + valorDeEncantamientos
      + ajusteDeMercado
```

- Cada carta se valúa con su propia rareza y datos de mercado.
- El refine necesita una curva por tipo de equipo y nivel.
- Los encantamientos y opciones aleatorias son lo más difícil; puede requerir tablas manuales.
- Evitar que el tasador pague más que el precio de venta esperado.

### Simulación y validación

- Probar con objetos raros que los jugadores ya tengan, de forma anonimizada.
- Generar objetos raros pero plausibles: equipo +7, equipo con cartas, combinaciones poco frecuentes.
- Comparar la tasación contra el mercado limpio y contra la dificultad real de farmeo.
- Revisar los extremos de la lista: top 1%, bottom 1%, items únicos y sin historial.
- Si la tasación queda lejos del mercado, ajustar antes de abrir el NPC.

## Fases

### Fase 1 (MVP)

- Solo items base, comerciables, identificados, no stackables, sin grade, sin bound y sin expiración.
- Cola asíncrona, oferta fija, pago en zeny y devolución por correo.
- Una solicitud abierta por cuenta; reclamo por personaje.
- Máquina de estados completa, bitácora y herramienta de GM.
- Simulador web de solo lectura con la misma fuente de precio.

### Fase 2

- Cartas, refine y random options, con valuación y devolución ya probadas.
- Seguir excluyendo grade, bound y expirables mientras no exista una devolución fiel.

### Fase 3

- Negociación, rangos de precio, prórroga y consignación con compradores reales o simulados.
- Solo si la fase 1 demuestra que la operación y la economía aguantan.

## Preguntas abiertas

- ¿La espera es fija o escala con la rareza/precio?
- ¿El worker calcula solo, o hay revisión manual antes de publicar la oferta?
- ¿La oferta es fija o se permite negociar dentro de un rango?
- ¿Cuánto tiempo se guarda una solicitud sin reclamar y cuánto un correo sin abrir?
- ¿La devolución es siempre por correo, o se entrega directo si el jugador está en línea y tiene espacio?
- ¿Qué pasa si el personaje que entregó el objeto se borra o cambia de nombre?
- ¿Qué pasa si el objeto ya no existe en `item_db` cuando toca devolverlo?
- ¿La web muestra el precio exacto o solo una referencia?

## Relación con otras ideas

- No reemplaza la compra de chatarra existente; el tasador maneja objetos de mayor valor.
- No reemplaza el vending: el vending sigue siendo para venta directa entre jugadores.
- Puede conectarse con el mercado de la web para mostrar la referencia de precio y el estado de la solicitud.

## Comentarios

- El modelo de consignación con negociación queda pospuesto; la primera versión es una compra diferida con custodia.
- La espera es deseable, pero el objeto no debería quedar huérfano: definir TTL y aviso.
- El punto no atómico es “inventario en memoria ↔ fila SQL”. La política at-most-once y la bitácora son la red de seguridad.
- Si la devolución por correo resulta poco fiable en el cliente actual, la alternativa es guardar y devolver directo con `getitem4` solo para personajes en línea, y usar correo como respaldo.
