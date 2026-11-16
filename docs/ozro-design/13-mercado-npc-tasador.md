# Mercado NPC: tasador y casa de empeño

**Estado:** `pendiente`  
**Contexto:** `ragnabots` quedó deprecado. No se van a usar bots para emular el mercado; la idea es resolverlo con NPCs.

## Objetivo

Dar salida a objetos que no encajan en el vending ni en la compra de chatarra, sin depender de una población grande de jugadores.

- **Vending:** ya existe una solución definida aparte.
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

La idea es cruzar **dificultad de obtención** con **datos de mercado limpios**.

- La rareza interna del servidor sigue siendo la base: drop rate, spawn, acceso, quest/craft, instancia y utilidad.
- La taxonomía de items (`ozro-site/assets/items/taxonomy.json`) puede servir de base.
- Los precios de mercado se pueden usar como **señal secundaria**, no como ancla.
- El tasador puede dar un rango y dejar que el jugador negocie dentro de ese rango.

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

## Viabilidad

Es un NPC complejo y queda para mucho más adelante. Antes de implementarlo hacen falta:

- Datos de mercado limpios y con criterio de outliers.
- Modelo de rareza y valuación de objetos compuestos.
- Persistencia segura de item + cartas + refine + opciones + dueño.
- Simulación con objetos reales y plausibles.
- Decidir si la venta es simulada, real o mixta.

Si la valuación de objetos compuestos resulta demasiado costosa, se puede empezar solo por items base y dejar cartas/refine/encantamientos para una segunda etapa.

## Preguntas abiertas

- ¿El NPC compra el objeto al instante o solo lo deja en consignación?
- ¿La venta es simulada por demanda del NPC o hay compradores reales?
- ¿La negociación es un menú de ofertas o un precio libre con límites?
- ¿El precio baja automáticamente si nadie compra?
- ¿Se puede cancelar la consignación antes del plazo?
- ¿Qué interfaz usa: tienda NPC, menú de diálogo o catálogo web?

## Relación con otras ideas

- No reemplaza la compra de chatarra existente; el tasador maneja objetos de mayor valor.
- No reemplaza el vending: el vending sigue siendo para venta directa entre jugadores.
- Puede conectarse con el mercado de la web para mostrar objetos en consignación.
