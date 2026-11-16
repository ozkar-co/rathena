# Mercado NPC: tasador y casa de empeño

**Estado:** `pendiente`  
**Contexto:** `ragnabots` quedó deprecado. No se van a usar bots para emular el mercado; la idea es resolverlo con NPCs.

## Objetivo

Dar salida a objetos que no encajan en el vending ni en Garrett, sin depender de una población grande de jugadores.

- **Vending:** ya existe una solución definida aparte.
- **Garrett:** compra chatarra barata al instante.
- **Tasador / casa de empeño:** para objetos de más valor o de venta lenta.

## Flujo propuesto

1. El jugador lleva un objeto al tasador.
2. El NPC le dice un **valor estimado** o un rango.
3. El jugador puede **negociar el precio de venta**.
4. Si acepta, el objeto queda **en consignación** durante varios días.
5. El jugador puede volver a preguntar cómo va la venta.
6. Si se vendió, cobra el dinero menos una comisión.
7. Si no se vendió, puede **retirar el objeto** o dejarlo más tiempo.

## Reglas a definir

- Solo aceptar objetos **comerciables**; excluir bound, quest, almas y objetos no transferibles.
- Precio mínimo y máximo; el tasador no debe comprar cualquier cosa a cualquier precio.
- Comisión del NPC y posible costo de publicación.
- Tiempo de consignación (por ejemplo, 3–7 días).
- Qué pasa al vencer: devolución automática, prórroga o retiro obligatorio.
- Límite de objetos en consignación por cuenta.
- Persistencia completa: item, cartas, refine, opciones aleatorias y dueño.
- Anti-dupe: el objeto sale del inventario y queda registrado una sola vez.

## Valuación

- No usar `ragnabots` como fuente principal: queda como dato histórico.
- Usar la rareza interna del servidor: drop rate, spawn, acceso, utilidad y demanda.
- La taxonomía de items (`ozro-site/assets/items/taxonomy.json`) puede servir de base.
- El tasador puede dar un rango y dejar que el jugador negocie dentro de ese rango.

## Preguntas abiertas

- ¿El NPC compra el objeto al instante o solo lo deja en consignación?
- ¿La venta es simulada por demanda del NPC o hay compradores reales?
- ¿La negociación es un menú de ofertas o un precio libre con límites?
- ¿El precio baja automáticamente si nadie compra?
- ¿Se puede cancelar la consignación antes del plazo?
- ¿Qué interfaz usa: tienda NPC, menú de diálogo o catálogo web?

## Relación con otras ideas

- No reemplaza a Garrett: Garrett compra basura común; el tasador maneja objetos de mayor valor.
- No reemplaza el vending: el vending sigue siendo para venta directa entre jugadores.
- Puede conectarse con el mercado de la web para mostrar objetos en consignación.
