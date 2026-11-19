BRIEF PARA REVISIÓN EXTERNA — Mercado de OzRo
0. Contexto
Servidor privado de Ragnarok Online (rAthena, Renewal) con rates custom. Se está construyendo un MarketSimulator y un NPC tasador. El simulador necesita, para ~9,600 items comerciables, un precio de mercado (low/mid/high) y precios NPC de compra/venta. El dataset actual (master.jsonl, 29,061 items) se genera desde:

item_db (tipo, slots, ATK/DEF, nivel, Buy/Sell, flags Trade),
mob_db (HP, DEF/MDEF, nivel, drops),
spawns canónicos (mapa, cantidad, respawn),
rates custom (item_rate_*, monster_hp_rate, mvp_hp_rate),
grupos/cajas, quests, recetas de craft,
un histórico de precios de dos servidores externos (LATAM y Atlantis), tratado como referencia, no como verdad.
El objetivo no es “clonar” otro servidor. Es producir precios plausibles, explicables, monótonos con rareza/utilidad y seguros para la economía, sabiendo que la economía del servidor es en gran parte desconocida.

1. Lo que hace hoy el modelo
Si el item tiene referencia histórica → base = referencia (status = market). 5,847 items.
Si no → base = percentil 40 del tipo × factor de fuente × factor de equipo (status = synthetic). 23,209 items.
Solo 5 items tienen precio manual.
Luego aplica tres multiplicadores:
oferta: clamp((mediana_oferta/oferta)^0.25, 0.5, 2.0)
demanda: 1 + 0.25·z, entre 0.7 y 1.5
dificultad: 1 + 0.15·z, entre 0.8 y 1.5
oferta = flujo de spawn = cantidad × drop efectivo × factor de acceso × 60/respawn, contando solo field + dungeon.
dificultad = log1p(HP efectivo) × (1+DEF/100+MDEF/200) × (1+0.5·boss) × (1+0.2·(nivel-100)/50), ponderada por flujo.
demanda = residual de ventas contra la mediana de (tipo, rareza), combinando LATAM y Atlantis.
Precio NPC: un porcentaje del mid, con piso/techo según Buy/Sell del item.
2. Síntomas medidos
Caso	Resultado actual	Lo que debería ser
Menblatt Card vs Frilldora Card	Menblatt 3.22M, Frilldora 13.58M	Menblatt es de un mob nivel 143 (164k HP efectivo); Frilldora de nivel 57 (3.1k HP). Mismo drop base (0.1% efectivo). Menblatt vendió 1,426 unidades vs 642. La inversión viene de la referencia histórica (1.5M vs 6.39M), no de la fórmula.
Monster Coin	17,900z, NPC paga 8,100	Mob nivel 1, 4,720 HP, drop 100% efectivo, 25 spawns. Es basura. Cae en el percentil 40 de “Etc” (18,000) porque ese tipo mezcla basura con materiales valiosos.
Golden Thief Bug Card	500,000z	Debe ser de los items más caros del juego. Además, el dataset perdió su spawn real (1/hora) y su HP real (222,750) por un bug de ingesta; solo ve la versión de evento.
Ifrit Card	500,000z	Igual que GTB, y encima más raro (1 spawn/11h). Ambas empatan porque la fórmula no ve ninguna de las dos.
Pantie[1]	1.56M	La receta real es 5% de éxito, consume la Pantie, 1M zeny + 1 Elunium. Costo esperado ≈ 20.2M. El modelo no lee socket_enchant2.txt.
Ice Pick[1]	539M	“Funcionó”, pero la referencia son 2 ventas a 650M, mientras el promedio de mercado es 258M. Es una referencia ruidosa que salió alta, no una validación del modelo.
Datos de soporte:

80 cartas synthetic valen exactamente 500,000.
202 cartas boss_only son synthetic; 76 valen exactamente 500,000.
3,628 items synthetic tienen supply.open = 0 y supplyMultiplier = 1.0.
Percentiles por tipo usados como base: Card p40 = 1M, Etc p40 = 18k, Armor p40 = 1.8M. Pero Etc p10 = 800 y p90 = 22M: el “tipo” no es una clase homogénea.
898 items tienen desacuerdo >2x entre las dos fuentes históricas con más de 50 ventas.
3. El problema de fondo
P1. No hay una unidad común
Se combinan cosas no conmensurables: flujo de spawn, HP, residual de ventas, share de caja, percentil de tipo. Los multiplicadores son topes arbitrarios (±15%, ±25%, 0.5–2.0) que no pueden corregir errores de base de 10x–100x. El modelo tiene un “acantilado”: 5,847 items usan un punto histórico; 23,209 usan un prior de tipo. La rareza no puede cruzar ese acantilado.

P2. No se modela el costo de adquisición
La pregunta correcta no es “¿cuánto flujo de spawn hay?”, sino “¿cuánto cuesta, en tiempo y zeny, poner una unidad en el mercado?”. No se modelan:

time gates (1 spawn/hora, 1 spawn/11 horas),
probabilidades destructivas (5% y se pierde el item),
costo en zeny/materiales de quests,
entrada de instancia,
odds de cajas/grupos,
tiempo de kill y riesgo del mapa.
Por eso Pantie[1], GTB e Ifrit no pueden salir bien: su costo real no está en ninguna parte.

P3. El prior de tipo es demasiado grueso
type_p40 trata “Etc” como una sola clase, pero ahí conviven Jellopy y Etel Dust con materiales de 20M. Trata “Card” como una sola clase, pero ahí conviven cartas de 1k y cartas MVP de 100M. El prior no distingue basura de ultra-raro; el resultado es que la basura sube y los ultra-raros se hunden.

P4. La evidencia histórica se usa como punto, no como evidencia
No exige mínimo de ventas: 2 ventas pueden ser “medium confidence”.
No usa el desacuerdo entre fuentes: Menblatt tiene LATAM 1.5M vs Atlantis 30.2M (~20x); el modelo elige LATAM en silencio.
La fuente se fija a latam_offers_median, que puede ser la más alta o la más baja según el item.
Un item “unobtainable” con referencia histórica se vuelve marketEligible: la etiqueta y la elegibilidad se contradicen.
P5. Oferta cero se trata como neutral
Si supply.open = 0, el multiplicador de oferta es 1.0. Es decir: “no hay fuente” no es escasez, es neutro. Peor: access.best = unknown aplica un factor 0.5, así que el item sin spawn recibe un castigo. El resultado es matemáticamente inverso al sentido común.

P6. Se colapsan propiedades ortogonales en un solo booleano
Esto es el punto que más nos interesa que revisen.

4. El caso unobtainable / untradeable
Definiciones actuales:

untradeable  = NoSell OR NoTrade OR NoDrop
unobtainable = no hay fuente directa (drop/shop/cash/quest/craft/script)
               y no está en grupo/paquete
marketEligible = not untradeable
                 AND (not unobtainable OR tiene_referencia)
                 AND (tiene_fuente OR tiene_referencia)
npcEligible = true para todos
Problemas concretos:

NoSell no significa “no comerciable”. En rAthena, NoSell es “el NPC no lo compra”. NoDrop es “no se puede tirar al suelo”. Solo NoTrade impide el comercio entre jugadores. El union los mezcla.
NoTrade: 6,851 items.
NoDrop: 7,132.
NoSell: 4,445.
Unión marcada como untradeable: 7,161.
310 items quedan untradeable sin tener NoTrade: 287 solo NoDrop + 23 solo NoSell.
68 de esos 310 tienen precio histórico y, aun así, quedan fuera del mercado. Ejemplo: Bouquet (744), solo NoDrop, referencia 7.5M, marketEligible = false.
unobtainable no significa “no se puede obtener”. Significa “no encontramos fuente en nuestro parseo”. Prueba: de 18,319 items marcados unobtainable, 800 tienen referencia histórica y 751 son marketEligible. Ejemplos: Thanos Spear, Aqua Staff, Crimson Staff. La etiqueta describe la cobertura de nuestros datos, no una propiedad del item.
npcEligible = true para todos contradice NoSell. 4,434 de 4,445 items NoSell reciben un npcBuyPrice mayor que su Sell configurado; 1,978 con Sell = 0 reciben un precio NPC ≥ 1,000. El modelo le paga al jugador por items que el NPC no debería comprar.
Se ignoran los canales que afectan liquidez, no comercio: NoStorage, NoMail, NoCart, NoAuction. No impiden tradear, pero cambian la velocidad y el precio (un item que no se puede guardar ni mandar por correo es menos líquido).
No existe la categoría “legacy/event/removed”. “Sin fuente” puede significar “ya no dropea”, “solo salió en un evento”, “es de una quest antigua” o “no lo parseamos”. Son cuatro cosas distintas y hoy colapsan en unobtainable.
Nuestra hipótesis: el error no es el valor de esos booleanos, es haber formulado el problema con booleanos. Una ontología mejor separaría tres ejes independientes:

Adquisición: farmed (con costo esperado), crafted, quested, group/box, npc, cash, event, legacy, unknown, none.
Transferencia: player_trade, npc_only, account_bound, char_bound, no_transfer; y por separado drop_allowed, storage_allowed, mail_allowed, auction_allowed.
Mercado: active, legacy, not_traded, derivado de la evidencia de ventas + transferencia.
obtainable debería ser una probabilidad/ruta con costo, no un sí/no. tradeable debería ser un conjunto de canales, no un sí/no.

5. El bug de datos que demuestra el problema de fiabilidad
No es solo metodología; la ingesta también está rota:

db/import/mob_db.yml tiene 67 filas; 66 son solo Id + DamageTaken.
El loader hace mobs[id] = row en vez de fusionar, así que borra HP, nivel y drops de 66 mobs.
Consecuencia: 100 items pierden todas sus fuentes de drop; 43 son cartas MVP; 72 quedan synthetic a ~700k. Incluye Doppelganger, Drake, Eddga, Maya, Moonlight, Pharaoh, Phreeoni, Orc Lord, Hatii, Turtle General, Lord of the Dead, Samurai Specter, Amon Ra, Tao Gunka, RSX-0806, White Lady, Lady Tanee, Thanatos, Detardeurus, Kiel-D-01, Gloom Under Night, Atroce y Beelzebub.
El GTB real (1086) tiene 222,750 HP y spawn de 1 hora; el dataset solo conserva la versión de evento (2306, 100M HP, sin spawn). De ahí no_spawn y minMobHp = 200M.
alb_ship se clasifica como other, así que Monster Coin tiene supply.open = 0 aunque su flujo sea 75.
Esto no es el problema principal, pero explica por qué “arreglar la fórmula” sin arreglar la procedencia de datos no va a dar confianza.

6. Restricciones y criterios de éxito
No exigimos determinismo. Una sola corrida es aceptable si el resultado es fiable y auditable.
Sí exigimos trazabilidad: para cada precio, poder responder “¿de dónde salió?” (ruta, costo, evidencia de demanda, confianza).
Presupuesto LLM: 2–5 USD es aceptable. No se descarta una pasada única de LLM, pero no como caja negra sin auditoría.
Criterios de éxito:
Ningún item con ventas históricas queda fuera del mercado por un booleano.
Dentro de una misma clase, una ruta más rara/cara nunca produce un precio menor, salvo que la demanda lo explique.
Los items con muestra chica (0, 1, 2 ventas) reciben banda ancha o “sin precio”, no un punto de confianza media.
Todo override manual es explícito y versionado.
El resultado se puede reproducir desde un registro de entradas + transcripción/seed.
7. Preguntas para los expertos
¿Es el costo esperado de adquisición la primitiva correcta? ¿Cómo estimar el costo de oportunidad (zeny/hora) de cada ruta si la economía del servidor es desconocida?
¿Cómo modelar items sin mercado y sin ruta (legacy/event) sin inventar un precio? ¿“Sin precio” es una salida válida?
¿Cómo combinar dos servidores históricos con desacuerdos de 20x? ¿Mediana robusta, geométrica, Bayes con priors, rechazo por inconsistencia?
¿Cómo modelar demanda con datos censurados y muestras de 0–2 ventas?
¿Cómo preciar un upgrade destructivo del 5% (costo esperado 20x) cuando el item base tiene su propio precio de mercado? ¿Es un problema de punto fijo? ¿Cómo evitar circularidad?
¿Cómo tratar bienes complementarios y sustitutos (cartas, gear con slots, refine, cajas, combos)?
¿La salida correcta es un mid con banda simétrica, o una distribución (p10/p50/p90) que refleje incertidumbre asimétrica y multimodal?
¿Cómo validar sin ground truth? ¿Qué invariantes, tests de monotonía y pruebas de estrés propondrían?
¿Qué división entre fórmula / manual / LLM minimiza error y mantenimiento? ¿Qué parte debe ser determinista y qué parte puede ser generativa?
Con 2–5 USD de presupuesto LLM y una sola corrida, ¿qué harían primero y qué dejarían explícitamente sin resolver?
8. Lo que no queremos
Parches item por item sin una regla general.
Overfitting a los seis casos de arriba.
Una lista de precios de LLM sin procedencia ni auditoría.
Pureza determinista a costa de correctness.
Seguir refinando una fórmula que mezcla unidades incompatibles.
