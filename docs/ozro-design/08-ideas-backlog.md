# Ideas backlog

Lluvia de ideas del documento antiguo, **reformuladas** y etiquetadas. No es lista de tareas — es inventario para priorizar cuando toque.

**Leyenda:** `implementado` | `en-repo` | `pendiente` | `reformular` | `descartado`

---

## Alta prioridad (alineadas con visión actual)

| Idea | Estado | Notas reformuladas |
|------|--------|-------------------|
| Challenges por cuenta con build/dificultad | `pendiente` | Ver [03-sistemas-core.md](./03-sistemas-core.md) |
| Meta colección cartas + web | `implementado` / `pendiente` | Collector hecho; falta % en web; preservar datos |
| Cronista como guía de lore | `reformular` | Expandir `chronicler.txt` |
| Daily Hunting Quest con racha | `en-repo` | `hunting_missions.txt` desactivado |
| Recompensas por cuenta (prestigio) | `pendiente` | Reducir incentivo multi-cuenta |
| Crimson Weapons + Marcus | `descartado` | No se portan; hoy las Crimson son oficiales. La lore queda como referencia |
| Partes especiales / fabricación de objetos de donación | `pendiente` | Objetos custom para crafting con lore |
| Quests equipo pro con lore | `reformular` | = challenges + cadenas craft, no regalos |
| Restructurar NPC cartas (tienda + misiones) | `reformular` | Extender card_collector sin perder datos |
| Mercado partes equip común (barter) | `descartado` | Se quita el barter para simplificar; el equip se consigue por craft/quests específicas |

---

## Economía y QoL

| Idea | Estado | Notas |
|------|--------|-------|
| Deshabilitar banco/correo del menú → solo NPC | `pendiente` | Más inmersivo; scripts bank en repo |
| Tasador / casa de empeño | `pendiente` | Mercado NPC sin bots para cartas, equipo refinado/cardeado y encantamientos; complejo, para mucho después; ver [13-mercado-npc-tasador.md](./13-mercado-npc-tasador.md) |
| Mercado NPC sin bots | `pendiente` | Vending para venta directa + tasador/consignación para el resto |
| Gambler → refine safe con monedas OzRo | `reformular` | Sin Special Gold; “si falla no se rompe”, no nivel fijo |
| Resurrect con costo de item | `pendiente` | Similar a Call Homunculus (que ya gasta Germination_Breed + Yggdrasilberry_Dew); caro pero no prohibitivo; definir item/cantidad |
| Monedas OzRo por tiers | `pendiente` | Bronce/plata/oro/platino; definir usos a medida que crece el contenido |
| Stock Market NPC | `en-repo` | `npc/custom/etc/stock_market.txt` |
| Blessed Ores en vez de Safe tickets + quest lore | `pendiente` | |
| Incluir más cajas cashshop + World Tour Ticket crafteable | `pendiente` | |
| Deadly Potion, Holy Water en cashshop | `pendiente` | |

---

## Actividades diarias / entre sesiones

| Idea | Estado | Notas |
|------|--------|-------|
| Daily Roulette (web → juego) | `pendiente` | [07-web-api.md](./07-web-api.md) |
| Daily Guess the Monster | `pendiente` | Menos pistas = más premio |
| Fishing (pesca) | `reformular` | Diseñar balance antes |
| Chef (cocina con fallo / puntos ingredientes) | `reformular` | Relacionar con cooking quest oficial |
| Treasure Hunter semanal | `pendiente` | NPC examen monstruo + llave diaria + cofre en mapa random |
| Quest cadena → desbloquea cacería tesoro | `pendiente` | Pistas mundo → explorador |
| Eventos automáticos + calendario | `pendiente` | Ver [16-eventos-automaticos.md](./16-eventos-automaticos.md) |
| NPC errante semanal (misiones/acertijos) | `pendiente` | "¿Dónde está ahora?" |
| Evento diario EXP/drop por dungeon + warp | `pendiente` | Un dungeon completo al día con rates aumentados y warp temporal |
| Retos fuera del juego con impacto in-game | `pendiente` | Se resuelven en la web y otorgan recompensa in-game |
| Minijuego diario web obligatorio | `pendiente` | Login diario en la página + tarea/minijuego para obtener recompensas in-game; racha y calendario. Evitar que sea solo un click. |

---

### Minijuego diario web (idea abierta)

- Login diario en la página + una tarea/minijuego para desbloquear la recompensa in-game.
- Puede tener racha y calendario; la recompensa debe ser útil pero no romper la economía.
- Evitar que sea solo un click: que requiera una decisión o tarea corta.
- Pendiente: tipo de minijuego, anti-multicuenta, recompensas y si la racha se pierde al faltar un día.

---

## Combate, equipamiento y progresión

| Idea | Estado | Notas |
|------|--------|-------|
| Hungry Weapons (arma pide cacerías, sube nivel) | `reformular` | Similar a armas evolutivas |
| Armas que evolucionan con uso/sacrificios | `reformular` | Integrar en challenges |
| Champion mobs (Furious/Swift/etc.) → gemas elementales | `pendiente` | Encantamiento permanente |
| MVP instancia con mutaciones | `pendiente` | Late game grupo pequeño |
| Mazmorras con llaves (daily/trade/kills) | `pendiente` | |
| Instancia oleadas temáticas (zombies, orcos) | `pendiente` | Party pequeña |
| Bloody Branch Manufacturer | `pendiente` | |
| MVP Hunting gacha (items comunes → monedas → gacha) | `reformular` | Riesgo power creep; mejor barter determinista |
| Sets custom con skills de otros jobs + Almas | `reformular` | Solo ultra-late o cosmético |
| Dark Ritual: reset a Novice 1 → SoulStone valiosa | `reformular` | ¿Conflicto con reset fácil? |
| NPC buffs por temporadas (esferas monk, adrenaline) | `pendiente` | Eventos estacionales |
| Old Blacksmith: monedas OzRo → piedras BS | `pendiente` | Depende de bounty rewards; ya no Special Gold |
| MVP room con cleaner | `pendiente` | Sala de MVPs con NPC de limpieza |
| Reemplazo de WoE: GvE / invasiones + castillos | `reformular` | En vez de GvG: invasiones de bichos o eventos PvE para acceder a castillos con pocos jugadores; obliga a defender, se puede perder y hay que renovar. Si algún día hay 6+, GvG chico o battleground. La guild debe servir para algo más que WoE, salvo que la WoE sea PvE. |
| Karma en misiones custom | `pendiente` | Karma +/- por personaje; misiones que exigen karma o dan recompensa según karma |
| Quests de cambio de job traducidas y más fáciles | `pendiente` | Ver [17-quests-de-job.md](./17-quests-de-job.md); incluye usar las quests 1-1 de pre-re (con pruebas) solo si es fácil |

---

### WoE → GvE / castillos (idea abierta)

- Objetivo: que los castillos y la guild tengan sentido con pocos jugadores (3–6).
- En vez de GvG puro: invasiones de bichos o eventos PvE para abrir acceso al castillo.
- El castillo se debe defender; si se pierde, hay que recuperarlo/renovarlo.
- Si algún día hay 6+ jugadores, evaluar un GvG chico o battleground como alternativa.
- La guild debe servir para algo más que WoE (buffs, storage, misiones, economía del castillo), salvo que la WoE sea PvE.
- Pendiente: cómo se dispara la invasión, schedule, decay del castillo, recompensas y anti-solo.

---

## Mascotas y social

| Idea | Estado | Notas |
|------|--------|-------|
| Craft comida mascotas raras | `pendiente` | |
| Intercambio huevos / mercado mascotas | `pendiente` | Incentivar catching |
| Sistema afinidad/reputación NPC | `pendiente` | Diálogos según reputación |
| Matrimonio / eventos sociales | `en-repo` | `marriage.txt` en custom genérico |

---

## Casa / vitrina (detalle)

| Idea | Estado | Notas |
|------|--------|-------|
| Vender casas en ciudad o refugios campo | `pendiente` | Instancia individual |
| Decorar con dolls | `pendiente` | Sin client: limitado |
| Vitrina cartas para enseñar | `pendiente` | NPC o instancia |
| Storage más grande / cofres múltiples | `pendiente` | Viable con pocos jugadores |
| Contratar NPCs de servicio (pago mantenimiento) | `pendiente` | |
| Carta inobtenible aleatoria por precio absurdo | `reformular` | Muy jackpot; evaluar sink extremo |

---

## Minijuegos y flavor

| Idea | Estado | Notas |
|------|--------|-------|
| NPC minijuegos (RPS, dados, lotería) | `en-repo` | blackjack, lottery, rpsroulette en custom |
| Story Teller (historias junto al fuego) | `pendiente` | Complemento cronista, no reemplazo arcos |
| Vendedor Viajero | `pendiente` | Ver [15-vendedor-viajero.md](./15-vendedor-viajero.md) |
| Rebirth Soul en Soul Linker | `pendiente` | `soul_link.txt` en repo |

---

## Ideas ChatGPT (doc viejo) — reformuladas

| Idea original | Estado | Integración |
|---------------|--------|-------------|
| Minijuegos NPC | `en-repo` | Scripts ya en `npc/custom/etc/` |
| Story Teller | `pendiente` | Zonas del mundo, historias cortas |
| Armas evolutivas | `reformular` | → Hungry Weapons / challenges |
| NPC errante semanal | `pendiente` | Evento rotativo |
| MVP mutados en instancia | `pendiente` | Late game |
| Llaves para mazmorras | `pendiente` | Daily + trade |
| Reputación NPC | `pendiente` | Largo plazo |

---

## Sistemas basados en tiempo / idle

Inspiración en idle games y juegos de gestión de celular: **hago cosas, pero debo entrar a revisar** para obtener beneficios.

| Idea | Estado | Notas |
|------|--------|-------|
| Gachas + sistemas basados en tiempo | `pendiente` | Recompensas que se acumulan y se reclaman al entrar |
| NPC granjero (produce con el tiempo) | `pendiente` | Ejemplo de sistema idle: dejar producir y recolectar luego |

---

## Simplicidad e interfaz

| Idea | Estado | Notas |
|------|--------|-------|
| Quitar barter | `pendiente` | Eliminar `feature.barter` y NPCs/scripts asociados; revisar quests que dependan de trueque |
| Quitar navi | `pendiente` | Evaluar quitar navegación del cliente/servidor (`navigateto`, generación navi); puede requerir parche de cliente |
| Simplificar juego e interfaz | `pendiente` | Menos sistemas, botones y NPCs; ocultar lo que no aporte sin tocar el cliente si es posible |
| RODEX: quitar o limitar a buzones de ciudad | `pendiente` | Opción A: `norodex` en mapas + NPC `openmail` en ciudades. Opción B: deshabilitar RODEX. Revisar complejidad antes |

### RODEX (idea abierta)

- Hoy RODEX se puede usar desde cualquier mapa; la idea es que el correo solo exista en buzones de ciudad.
- rAthena tiene el mapflag `norodex` y el comando `openmail`, así que la opción de “solo buzones” parece viable sin tocar el cliente.
- Hay que revisar: botón/atajo del cliente, paquetes RODEX, `mail.cpp`, `norodex`, DB de correo y scripts que envíen items por mail.
- Alternativa más simple: deshabilitar RODEX por completo y dejar solo el correo clásico/NPC.

### Navi (idea abierta)

- La navegación tiene generación en el server (`navi_create_lists`), comandos `navigateto`/`navihide`/`naviregisterwarp` y UI del cliente.
- Quitarla del todo puede requerir parche de cliente; alternativa: ocultar NPCs/warps de navi y no generar rutas.
- Pendiente: medir cuánto depende el gameplay actual de la navegación antes de decidir.

---

## Descartadas o en pausa

| Idea | Motivo |
|------|--------|
| Servidor "balanceado y listo" antes de jugar | Reemplazado por enfoque incremental |
| Libro con todas las quests extraídas | Preferir guía in-game + arcos curados |
| Competencia principal por MVP/zeny | Injusta para tiempo y roles |
| Regalar equip de wikis | Rompe progresión |
| Portar NPCs de Hercules | Sprites/lore incompatibles; el repo viejo es referencia, no código a migrar |
| Ox Hunter / Ox Merchant | Sprite elegido al azar, historia incompatible, quedaron a medio implementar |

---

## Cómo priorizar

1. ¿Funciona con 3 jugadores y 2 semanas/año?
2. ¿Progreso por cuenta?
3. ¿Sin tocar client?
4. ¿Se puede probar en una tarde?
5. ¿Balancea o reemplaza algo que ya está activo?

Si 3+ son sí → subir prioridad.

**Regla de orden:** primero balancear las monedas existentes; después agregar NPCs/quests nuevas. No hay server de prueba: se valida directo en producción con los 3 jugadores.

## Comentarios

<!-- Borrador libre para ideas nuevas; luego organizar en las tablas de arriba -->
