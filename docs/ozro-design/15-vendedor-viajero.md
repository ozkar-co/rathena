# Vendedor Viajero

**Estado:** `pendiente`  
**Contexto:** reemplazo del mercado de bots y de la idea de autotrade. El servidor es cooperativo y con pocos jugadores, así que el mercado se resuelve con NPCs viajeros, stock limitado y precios anclados a la taxonomía.

**Relacionado:** [04-npcs.md](./04-npcs.md), [13-mercado-npc-tasador.md](./13-mercado-npc-tasador.md), [14-arena-mvp-invocador.md](./14-arena-mvp-invocador.md)

## Objetivo

- Dar salida a items de invocación fija que no se consiguen fácilmente en el mercado entre jugadores.
- Crear un sink de zeny y de items sin depender de una población grande.
- Aparecer de forma aleatoria en ciudades, con pistas del Cronista y stock diario/semanal.
- Vender, no comprar. La compra de basura sigue siendo de Garrett y el tasador.

## Relación con el invocador

- Las **Almas** son el freno principal: sin Almas no hay invocación, aunque se tengan todos los items.
- El viajero vende las **keys** que faltan; no vende Almas ni crea Almas.
- La invocación fija cuesta Almas + items. El viajero ayuda a completar el paquete, no lo regala.
- Los precios del viajero deben ser un complemento del farmeo, no la vía más barata para todo.

## Reglas propuestas

- **Stock global y limitado** por item. No infinito.
- **Reposición diaria o semanal** según rareza.
- **Cap de compra por cuenta** para evitar que un solo jugador se lleve todo el stock.
- **Solo venta** por zeny; sin ledger de compra en la primera versión.
- Excluir items `untradeable`, `quest_only`, `instance_only`, `unobtainable` y objetos con script especial.
- Si un item ya está en una tienda NPC normal, no venderlo más caro: o se omite, o se vende al mismo precio como conveniencia.
- El viajero no debe vender items que se puedan comprar más barato en el item mall.

## Lista inicial (T1)

| Item | ID | Para | Stock | Reposición | Precio base | Notas |
|---|---:|---|---:|---|---:|---|
| Banana Hat | 5116 | Lady Tanee | 1 | semanal | ~400.000z | Key de lujo; mercado ~399k. |
| Orc Warlord Token | 25508 | Orc Hero | 2 | diario | manual | Key exclusiva; 48.5% de Orc Hero. Alternativa: 100 Orcish Voucher. |
| Tongue | 1015 | Phreeoni | 20 | diario | ~10.000z | Compartido con otros mobs; mercado ~10k. |
| Ant Jaw | 1014 | Phreeoni | 20 | diario | manual | Junk de Garrett; quitar de la lista de Garrett si se usa como key. |
| Heroic Emblem | 968 | Orc Lord | 1 | semanal | ~690.000z | Recuperable matando Orc Lord/Orc Hero; mercado ~690k. |
| 3carat Diamond | 732 | Dracula | 2 | diario | ~63.000z | Mercado ~63k; también cae de otros MVPs. |
| Red Bat Wing | 7006 | Dracula | 100 | diario | manual | Volumen; 27.5% de Drainliar, 100% de ringleaders. |
| Round Shell | 1096 | Maya | 30 | diario | ~1.000z | Key temática de insectos; no es drop de Maya. |
| Royal Jelly | 526 | Mistress | 30 | diario | ~10.000z | Ya está en NPC shop; si se vende, al mismo precio o no vender. |

- **Golden Thief Bug:** la key es **1 Gold (969)**. No se lista como item del viajero porque ya está en el marketshop NPC (1M) y cae de 31 mobs; el jugador lo consigue por drop o compra.
- No se incluye Big Eggring: no es invocable.

## Precios

- Si `marketPrice > 0`, usar el precio de mercado con un margen de cordura (por ejemplo, 0.9–1.2×).
- Si `marketPrice = 0`, usar un precio manual documentado por item.
- Si el item está en NPC shop, el precio del viajero nunca debe superar el precio de la tienda.
- Los items de volumen (Tongue, Ant Jaw, Red Bat Wing, Round Shell, Royal Jelly) pueden venderse en paquetes de 20–100; los de lujo (Banana Hat, Heroic Emblem) en unidades de 1–2.
- Revisar precios después de la primera semana; el stock y el precio son parte del balance.

## Stock y reposición

- Lujo: 1–2 unidades por reposición semanal.
- Volumen: 20–100 unidades por reposición diaria.
- Las reposiciones pueden ser globales o por cuenta; decidir antes de implementar.
- Si el stock está en 0, el item desaparece del menú hasta la próxima reposición.

## Preguntas abiertas

- ¿Stock global o por cuenta?
- ¿Qué días/horarios repone y con qué frecuencia aparece el viajero?
- ¿Vende paquetes completos de invocación o items sueltos?
- ¿Cómo se avisa de su ubicación? ¿Pistas del Cronista, anuncio global o ambos?
- ¿Qué pasa si un jugador compra todo el stock? ¿Cap por cuenta o stock global?
- ¿Qué items de T2/T3 se agregan después?
- ¿Se conecta con el tasador o son NPCs separados?

## Comentarios

- La idea es que el viajero sea una alternativa para completar keys, no la fuente principal.
- Para jugadores cooperativos, el líder puede pagar las Almas y la party aportar items.
- El viajero no debe vender Almas ni items que rompan la economía de invocación.
