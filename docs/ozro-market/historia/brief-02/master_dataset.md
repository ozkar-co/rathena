# OzRo — Master World Dataset
## Especificación técnica para el equipo de agentes de IA

**Proyecto:** OzRo  
**Fase:** World Data Foundation  
**Objetivo:** Construcción de extractores, normalización, generación y validación de la base maestra del servidor.  
**Destino:** Base de datos SQL con prefijo de tablas configurable.

---

# 1. Propósito del proyecto

El objetivo es construir un sistema de extracción y consolidación de información que genere una representación estructurada, completa y verificable del mundo efectivo de OzRo.

Esta información será la fuente única de datos para los sistemas que se desarrollen posteriormente, entre ellos:

- MarketSimulator.
- NPC tasador.
- NPC de compra y venta.
- Sistemas de información y consulta.
- Enciclopedia pública del servidor.
- Mapas interactivos.
- Herramientas de exploración y progresión.
- Sistemas de análisis de monstruos, drops y farmeo.
- Cualquier herramienta administrativa que necesite consultar información del juego.

La extracción debe contemplar las particularidades de OzRo, incluyendo sus configuraciones, personalizaciones, scripts, contenido habilitado y recursos del cliente.

No buscamos replicar simplemente las bases de datos originales de rAthena. Buscamos representar el estado efectivo del servidor, con sus reglas y modificaciones aplicadas.

## 1.1. Principio arquitectónico fundamental

> **Ningún sistema posterior debe volver a interpretar directamente los archivos originales de rAthena. Todos deben consumir el Master World Dataset.** 

(a excepcion del juego base, con sistema nos referimos a lo que construiremos externamente)

Los extractores serán los únicos componentes autorizados para interpretar las fuentes originales.

Los sistemas posteriores no deben implementar sus propios parsers, reconstruir valores, aplicar nuevamente configuraciones ni deducir información que ya debería estar resuelta en la base maestra.

Por ejemplo:

- El MarketSimulator no debe volver a calcular los drops.
- La página web no debe interpretar `item_db`.
- Un NPC no debe consultar los scripts originales para conocer una receta.
- Un sistema de mapas no debe volver a analizar los warps.
- Un sistema de farmeo no debe aplicar nuevamente los rates del servidor.

Todo debe estar disponible mediante consultas al Master World Dataset.

---

# 2. Requisitos fundamentales

La implementación debe cumplir los siguientes principios.

### 2.1. Fuente de verdad

La información generada debe representar el estado efectivo de OzRo.

Para ello, los extractores deben consultar:

1. Archivos y configuraciones activos del servidor.
2. Bases de datos efectivamente utilizadas.
3. Scripts NPC y scripts de contenido.
4. Configuraciones particulares de OzRo.
5. Recursos del cliente.
6. Información obtenida del servidor en ejecución, cuando sea necesaria para verificar comportamientos.

### 2.2. Idempotencia

La generación de la base debe ser completamente idempotente.

Esto significa que:

- Ejecutar el proceso varias veces con las mismas fuentes debe producir exactamente el mismo resultado.
- No deben generarse registros duplicados.
- No deben acumularse transformaciones sobre valores previamente transformados.
- Los identificadores deben ser estables.
- Las relaciones deben reconstruirse de forma determinista.
- Las tablas deben reflejar el resultado completo de la extracción.
- Una modificación en las fuentes debe reflejarse en la siguiente ejecución.
- Una ejecución interrumpida no debe dejar una base parcialmente actualizada.

**La base debe poder regenerarse desde las fuentes sin depender del estado de una ejecución anterior.**

No se deben utilizar los valores existentes en SQL como entrada para calcular los nuevos valores.

### 2.3. Configuración aplicada durante la generación

Las personalizaciones de OzRo deben resolverse durante la extracción.

Por ejemplo:

- Modificadores de HP de monstruos.
- Rates de drops.
- Rates de experiencia.
- Configuraciones de aparición.
- Modificaciones de atributos.
- Valores económicos nativos.
- Cualquier otro ajuste que altere el comportamiento efectivo del juego.

Los extractores deben leer directamente los archivos de configuración correspondientes.

La base generada debe contener los valores efectivos, no solamente los valores originales que aparecen en las bases de datos.

Cuando sea relevante, se conservarán también los valores originales para trazabilidad.

### 2.4. Separación entre extracción y consumo

Los extractores deben ser responsables de:

- Leer.
- Interpretar.
- Normalizar.
- Resolver configuraciones.
- Calcular valores derivados.
- Validar.
- Persistir.

Los consumidores deben limitarse a consultar los datos resultantes.

### 2.5. Trazabilidad

Toda información debe poder rastrearse hasta su origen.

Cuando sea posible, cada registro debe identificar:

- Fuente.
- Archivo.
- Registro o identificador original.
- Script de procedencia.
- Configuración utilizada.
- Tipo de transformación aplicada.
- Estado de verificación.

---

# 3. Arquitectura general

Se propone implementar el sistema mediante cinco componentes principales.

```text
                 FUENTES DE OZRO
                       |
          +------------+------------+
          |            |            |
       DATABASES     SCRIPTS      CONFIG
          |            |            |
          +------------+------------+
                       |
                  CLIENT GRF
                  (ozro-cli)
                       |
                       v
              1. SOURCE DISCOVERY
                       |
                       v
              2. DATA EXTRACTION
                       |
                       v
              3. NORMALIZATION
                       |
                       v
              4. EFFECTIVE DATA
                 RESOLUTION
                       |
                       v
              5. VALIDATION
                       |
                       v
                MASTER WORLD
                   DATASET
                       |
                       v
                  SQL DATABASE
                       |
          +------------+------------+
          |            |            |
       MARKET         NPC          WEB
       SYSTEMS      SYSTEMS       SYSTEMS
```

## 3.1. Componentes

| Componente | Responsabilidad |
|---|---|
| Source Discovery | Identificar fuentes y archivos disponibles |
| Extractors | Extraer información estructurada |
| Normalizers | Unificar estructuras y nomenclaturas |
| Effective Resolver | Aplicar configuraciones y personalizaciones |
| Validator | Comprobar integridad y consistencia |
| SQL Writer | Generar y sincronizar las tablas |

Cada componente debe ser independiente, pero utilizar contratos de datos compartidos.

---

# 4. Organización de los dominios de información

El Master World Dataset estará compuesto por los siguientes dominios.

1. Maps.
2. Map Connections.
3. Mobs.
4. Spawns.
5. Skills *(jugador y monstruo; ver §8bis)*.
6. NPCs.
7. Items.
8. Item Properties.
9. Item Scripts.
10. Item Restrictions.
11. Item Enchantments.
12. Acquisition Sources.
13. Drops.
14. NPC Shops.
15. Quests.
16. Instances.
17. Boxes and Rewards.
18. Recipes and Crafting.
19. Enchanting and Socketing.
20. Item Relationships.
21. Source Provenance.

**Nota de orden (Etapa 3):** el barrido de **Skills** (en especial `mob_skill_db` y summons de `skill_db`) entra **antes** del análisis profundo de NPCs. Muchos `mob_role: pending` y spawns no-mapa (slaves de boss) solo se resuelven con esa evidencia; el análisis de scripts NPC puede refinar relaciones adicionales después.

Cada dominio tendrá sus propias tablas SQL, pero podrá relacionarse con los demás mediante identificadores estables.

---

# 5. MAPS — Catálogo de mapas

## 5.1. Objetivo

Construir un inventario de los mapas utilizables en OzRo y sus propiedades.

La información debe permitir:

- Identificar los mapas disponibles.
- Clasificarlos.
- Consultar sus características.
- Conocer sus conexiones.
- Reconstruir rutas entre ciudades y zonas.
- Identificar los NPC y monstruos presentes en cada mapa.
- Determinar las condiciones de acceso.

## 5.2. Campos del mapa

| Campo | Tipo conceptual | Descripción |
|---|---|---|
| `map_id` | String | Nombre técnico del mapa |
| `display_name` | String | Nombre visible |
| `category` | Enum | Categoría principal |
| `categories` | Array | Categorías complementarias |
| `is_town` | Boolean | Es una ciudad |
| `is_dungeon` | Boolean | Pertenece a un dungeon |
| `is_instance` | Boolean | Pertenece a una instancia |
| `is_quest_map` | Boolean | Está relacionado con quests |
| `is_guild_map` | Boolean | Pertenece a contenido de guild |
| `is_interior` | Boolean | Es un interior |
| `is_accessible` | Boolean | Es utilizable |
| `access_conditions` | JSON | Condiciones de acceso |
| `width` | Integer | Ancho, cuando esté disponible |
| `height` | Integer | Alto, cuando esté disponible |
| `source` | JSON | Procedencia |

Las categorías serán:

- City.
- Field.
- Dungeon.
- Instance.
- Quest.
- Guild.
- Interior.
- Arena.
- Special.

No deben ser necesariamente excluyentes. Todo mapa enabled debe recibir una `category` principal en Etapa 2. Lo que no encaje con reglas claras va a **`Special`** (cajón explícito “sin clasificar fino”), nunca `null`.

### Dos capas: verdad del servidor vs categoría nuestra

| Campo | Origen | Capa | Naturaleza |
|---|---|---|---|
| `is_town` | Mapflag `town` en `npc/mapflag/town.txt` + `npc/re/mapflag/town.txt` | **original / configuración absoluta** | Verdad del sistema rAthena OzRo. No se inventa ni se “completa” con listas nuestras. |
| `category` / `categories` | Extracción + reglas de normalización del dataset | **inferred / normalizado** | Etiqueta nuestra para catálogo. Puede discrepar de flags mecánicos. |
| `classification_layer` | Siempre `inferred` para `category` | metadato | Obliga a no confundir categoría con config. |

Principio: **está permitido** que definamos `category` nosotros en esta etapa, **siempre que** el origen quede explícito y los flags de configuración (`is_town`, etc.) se guarden aparte como verdad absoluta.

Ejemplo válido: `morocc` → `is_town: false` (no está en el mapflag) y `category: City` (nosotros lo etiquetamos ciudad/hub). Eso no es contradicción: son dos preguntas distintas.

### Reglas de clasificación verificadas (Etapa 2)

| Señal | Fuente canónica | Notas |
|---|---|---|
| `is_town` | Solo mapflags `town` (pre-re + re) | Absoluto. No mezclar con `category`. |
| City | Reglas/lista del normalizador (inferred) | Independiente de `is_town`. |
| Instance | `instance_db` + nombres `N@…` | |
| Guild | `gld_` / `gld2_` / castillos / `06guild` / etc. | |
| Dungeon | Heurísticas incl. `gl_*` (Glast Heim), `*_dun*`, etc. | |
| Arena | `force_*`, `ordeal_*`, `guild_vs`, etc. | |
| Field | `_fild` / campos conocidos (`mjolnir_*`, …) | |
| Interior | `_in`, `in_*`, `ba_*`, interiores de ciudad, etc. | |
| Quest | `que_*`, `evt_*`, … | |
| Special | Resto (transporte, utilitarios, dudosos) | Incluye airplane/airport/naves, etc. **No** crear categoría Transport. |
| `display_name` | 1) `mapnametable.txt` 2) fallback `instance_db.Name` 3) null | Ver abajo. |
| `width` / `height` | Cabecera `.gat` | |
| Recurso presente | `client_maps.jsonl` | |
| `access_conditions` | Mapflags + scripts + quests/instances | Etapa 3+. |

### `display_name` ausente ≠ mapa injugable

El exportador de cliente **ya** entrega `display_name` cuando existe en `mapnametable.txt`. Si falta:

- El mapa puede seguir siendo **jugable** si tiene rsw+gat+gnd (`client_resource_present`).
- El cliente suele mostrar el `map_id` técnico o un título de instancia/UI.
- Fallback permitido en el extractor de Maps: nombre de `instance_db` para mapas de instancia.
- No inventar nombres bonitos; si no hay fuente, `display_name` queda null y se reporta.

## 5.3. Fuentes

| Información | Fuente |
|---|---|
| Existencia del mapa | `conf/maps_athena.conf` (líneas `map:` habilitadas) |
| Nombre técnico | Mismo conf / `map_index` |
| Nombre visible | Cliente `mapnametable.txt`; fallback servidor `instance_db` |
| Disponibilidad del recurso | Inventario GRF (`ozro-cli` → `client_maps.jsonl`) |
| Dimensiones | Cliente: cabecera `.gat` |
| `is_town` | Mapflags `town` únicamente (verdad de configuración) |
| `category` | Normalizador del dataset (inferred; no sustituye mapflags) |
| Condiciones de acceso | Scripts, mapflags, quests, instances |

## 5.4. Criterio de extracción

`ozro-cli` debe utilizarse para consultar los recursos del GRF del cliente y verificar la disponibilidad de los archivos correspondientes, incluyendo nombre visible y dimensiones cuando existan.

El extractor debe relacionar esa información con los mapas definidos por el servidor. El cliente valida presencia y metadatos visuales; no es la fuente de taxonomía.

## 5.5. Map Connections

Las conexiones deben almacenarse separadamente de los mapas.

Cada conexión representa un desplazamiento dirigido desde un punto de origen hasta un destino.

### Tipos de conexión

| Tipo | Descripción |
|---|---|
| `warp` | Warp convencional |
| `kafra` | Transporte mediante Kafra |
| `custom_npc_tp` | Transporte mediante NPC personalizado |
| `airship` | Transporte mediante aeronave |
| `boat` | Transporte mediante barco |
| `dungeon_tp` | Transporte especial hacia un dungeon |
| `scripted` | Transporte mediante lógica de script |

Aqui vale la pena detenerse, ver que "otros scripts" existen por ejemplo Eden Group (que esta tras una quest) o otros para definir si crear un tipo nuevo y mapearlo o ignorarlo y dejarlo como "scripted" general.

### Campos

| Campo | Descripción |
|---|---|
| `connection_id` | Identificador estable |
| `connection_type` | Tipo de conexión |
| `source_map_id` | Mapa de origen |
| `source_x` | Coordenada X de origen |
| `source_y` | Coordenada Y de origen |
| `destination_map_id` | Mapa de destino |
| `destination_x` | Coordenada X de destino |
| `destination_y` | Coordenada Y de destino |
| `npc_id` | NPC asociado, si aplica |
| `zeny_cost` | Costo en Zeny |
| `required_items` | Ítems requeridos |
| `conditions` | Condiciones adicionales |
| `is_directional` | Indica que la conexión es dirigida |
| `source` | Procedencia |

### Transporte personalizado

Existe un sistema de teletransporte personalizado que cobra:

- Zeny.
- Blue Gemstone.

Debe representarse como una conexión propia, con ambos costos registrados.

También deben contemplarse las rutas de airship y barco.

**Referencia adicional:** utilizar el documento existente que mapea las fuentes de transporte especiales como referencia para extraer y verificar estas conexiones. Ese documento es la referencia funcional para este conjunto de transportes. (esta en ozro-site)

---

### 5.6. Grafo de conexiones y cálculo de fricción (Dijkstra All-Pairs)

Construir un grafo dirigido donde cada mapa utilizable sea un nodo y cada conexión de transporte una arista. El objetivo es calcular anticipadamente la ruta de menor fricción entre todos los pares de mapas mediante Dijkstra All-Pairs.

**Pesos por tipo de conexión:**

| Conexión | Peso |
|---|---:|
| Warp | 1.0 |
| Kafra | 0.2 |
| Dungeon TP (transporte personalizado OzRo) | 0.5 |
| Airship | 1.5 |
| Barco | 1.2 |

Los pesos representan una medida relativa y constante de fricción o conveniencia del desplazamiento, no tiempo ni costo económico. Los costos en Zeny y materiales se conservan como atributos independientes.

Se ignorarán otras conexiones especiales implementadas mediante scripts, pues se consideran atajos adicionales que los jugadores descubrirán durante el juego.

**Resultados:**

- Fricción mínima entre cada par de mapas.
- Ruta de conexiones que produce ese mínimo.
- Cantidad de conexiones utilizadas.
- Identificación de destinos sin ruta disponible.

Los resultados se almacenarán en SQL, utilizando las tablas `ozro_map_distances` y `ozro_map_routes`, para que cualquier sistema posterior pueda consultarlos directamente.

**Aplicaciones:** calcular la fricción de desplazamiento para llegar a un monstruo, recorrer ubicaciones de farmeo o construir guías de quests que involucren visitas a NPC y cacería de monstruos. Para recorridos con varios destinos, se sumarán las distancias mínimas entre cada ubicación consecutiva, respetando el orden requerido.

El cálculo debe ser determinista e idempotente y regenerarse cuando cambien los mapas, las conexiones o sus pesos. Los sistemas posteriores consumirán los resultados almacenados, sin reconstruir el grafo.

---

# 6. NPCs — Catálogo maestro de NPC

Este dominio debe incorporarse como una entidad de primer nivel.

> **Dependencia Etapa 3:** el análisis profundo de NPCs (§6.3) va **después** del barrido de Skills (§8bis). Los summons/slaves de boss no deben “descubrirse” solo desde diálogos NPC si ya constan en `mob_skill_db`.

No basta con registrar NPCs que ofrecen tiendas o transportes. Necesitamos conocer para qué sirve cada NPC y con qué contenido está relacionado.

## 6.1. Objetivo

Construir un catálogo que permita responder:

- ¿Qué NPC existen?
- ¿Dónde están?
- ¿Qué función cumplen?
- ¿Qué servicios ofrecen?
- ¿Qué scripts ejecutan?
- ¿Con qué quests están relacionados?
- ¿Qué ítems venden, compran o entregan?
- ¿Permiten desplazamientos?
- ¿Tienen condiciones especiales de uso?

## 6.2. Campos del NPC

| Campo | Descripción | Etapa |
|---|---|---|
| `npc_id` | Identificador estable | 2 |
| `name` | Nombre técnico o identificador del script | 2 |
| `display_name` | Nombre visible | 2 |
| `map_id` | Mapa donde aparece | 2 |
| `x` / `y` | Coordenadas (null si floating) | 2 |
| `sprite_id` | Sprite del header (numérico o constante) | 2 |
| `sprite_stem` / presencia cliente | Join a `client_npc_sprites` vía id numérico | 2 |
| `npc_type` | `script` / `shop` / `warp` / `duplicate` / … | 2 |
| `functions` | Funciones identificadas (multi-valor) | 2 (solo seguros) → 3 (refinado) |
| `description` | Descripción funcional | 3 |
| `related_quests` | Quests relacionadas | 3 |
| `related_instances` | Instancias relacionadas | 3 |
| `related_items` | Ítems involucrados | 3 |
| `script_ids` / `script_path` | Scripts asociados | 2 path; 3 análisis |
| `source` | Procedencia | 2 |

### Etapa 2 vs Etapa 3 (NPCs)

| Etapa | Qué se extrae |
|---|---|
| **2** | Catálogo de headers: id, nombre, mapa/x/y, `npc_type`, `sprite_id` + enlace a imagen cliente, `functions` **solo** cuando sean evidentes al 100 % de un vistazo al tipo/header. Si no es claro → `pending`. |
| **3** | Análisis profundo del cuerpo del script (ver nota abajo). Con ese análisis se **refina** `functions` (un NPC puede tener varias) y se llenan relaciones. |

`pending` en `functions` es válido al cerrar Etapa 2: se resuelve en **Etapa 3 — NPCs / relaciones**, cuando exista el inventario de comportamientos del script.

## 6.3. Clasificación funcional

Un NPC puede cumplir **varias** funciones a la vez (lista multi-valor; no forzar una sola).

Clasificaciones iniciales:

- Shop.
- Buyback.
- Kafra.
- Transport.
- Quest.
- Instance.
- Guild.
- Warper.
- Healer.
- Storage.
- Repair.
- Refine.
- Enchant.
- Socket.
- Reward.
- Event.
- Utility.
- Custom.
- **pending** — aún sin evidencia segura (default Etapa 2).

### Etapa 2 — solo marcas 100 % seguras

En Etapa 2 solo se asignan funciones cuando el header/tipo no deja duda, por ejemplo:

- `npc_type` ∈ shop/cashshop/itemshop/pointshop/marketshop → `Shop`.
- `npc_type` ∈ warp/warp2 → `Warper`.

Heurísticas de path/nombre (“parece quest”, “está bajo guild/”) **no** bastan en Etapa 2: dejar `pending` y resolver en Etapa 3.

### Nota — revisar en Etapa 3 (NPCs)

Al llegar a NPCs en Etapa 3, el extractor de relaciones debe inventariar por NPC (y usar eso para fijar `functions` con evidencia):

- Ítems que **vende** / **compra** (shops, barters, `getitem`/`delitem` de menú, etc.).
- **Quests** con las que se relaciona (ids, roles).
- Variables que **lee** o **escribe**: nombre y **scope** (`permanent`, `account`, `player`/`#`, `npc`, `instance`, temporales `.@`, etc.).
- Si **invoca mobs** (`monster` / `areamonster` / …) y **cuáles** (id / AegisName).
- Si **crea o entra a instancias**.
- Si **teleporta** al personaje (destino map/x/y, costos, condiciones).
- Otros servicios evidentes (refine, enchant, storage, heal, …).

Con ese inventario se determina `functions` de forma efectiva: marcar solo lo demostrado; si sigue sin ser claro → permanece `pending`. Un mismo NPC puede acumular varias funciones.

### Hallazgos Etapa 3 — shops + análisis de script (OzRo)

**Shops (headers):** ~342 tiendas (`shop` 300 · `marketshop` 42); ~2911 filas ítem; ~555 ítems únicos. Currency: `zeny`. `cashshop`/`itemshop`/`pointshop` no aparecen en scripts enabled (parser listo).

**callshop → inventario (hecho, parcial):** ~98 usos. Literales → `shop_id` **70**; prefijo (`"market_refine_" + …`) **1** → 7 marketshops. **24** → **barter** (nombres ~66 indexados desde `barters.yml` enabled, sin inventario; incluye prefijos `shop_ext162_*`). **1** dinámico. Residuo: `EnchantGradeExchange` ×2 — barter solo en `trash_bin/…/enchantgrade.yml`, **no** cargado en OzRo.

**Decisión:** resolver de una vez el enlace callshop→tienda ya parseada (cara del NPC + inventario flotante). **No** meter inventario barter aquí: modelo distinto (`RequiredItems`, stock, zeny/ítem) → paso/dominio propio después.

**Script bodies:** ~7479 scripts analizados; `functions` pending **16518 → ~9066**. Duplicates heredan del `duplicate_of` (~4259).

| Función | ~n (tras análisis) | Evidencia típica |
|---|---|---|
| Warper | 3930 | header `warp`/`warp2` |
| Transport | 3428 | `warp` / `savepoint` / `warpparty`… en cuerpo |
| Quest | 1980 | `setquest` / `checkquest` / … |
| Instance | 1329 | `instance_create` / `instance_enter` / … |
| Healer | 1105 | `percentheal` / `fullheal` (también en quests) |
| Shop | 581 | header shop + `callshop` / `npcshop*` |
| Kafra / Storage / Refine / … | menor | `F_Kafra`, `openstorage`, `successrefitem`, … |

**Ruido aceptado (no “bug”):** `Transport`/`Healer` en quests que warpean/curan una vez = multi-función real; no implica NPC de servicio dedicado. Comandos rAthena suelen ir **sin paréntesis**.

## 6.4. Relaciones

Los NPC deben relacionarse con:

- Mapas.
- Conexiones.
- Quests.
- Instancias.
- Ítems.
- Tiendas.
- Recetas.
- Recompensas.
- Scripts.
- Mobs invocados (Etapa 3).
- Variables / scopes (Etapa 3).

Un NPC puede estar relacionado con varias quests y una quest puede involucrar varios NPC.

## 6.5. Fuentes

| Información | Fuente | Etapa |
|---|---|---|
| Definición / ubicación / sprite header | Scripts | 2 |
| Imagen cliente | `npcidentity` + `jobname` + `client_npc_sprites` (id numérico) | 2 |
| Funciones seguras (tipo) | Header `npc_type` | 2 |
| Funciones refinadas | Análisis de cuerpo de script | 3 |
| Tiendas / buy-sell | Scripts | 3 |
| Quests / instancias / warps scripted | Scripts | 3 |
| Variables y scopes | Scripts | 3 |
| Invocación de mobs | Scripts | 3 |

---

# 7. MOBS — Catálogo de monstruos

## 7.1. Objetivo

Construir un catálogo de monstruos con sus estadísticas y propiedades efectivas.

Debe permitir consultar:

- Qué monstruos existen.
- Sus atributos.
- Su clasificación.
- Su rol de aparición (campo, summon, pet, stub, etc.).
- Su comportamiento.
- Sus propiedades de combate.
- Sus drops.
- Sus apariciones.

No todos los registros de `mob_db` son monstruos de campo farmeables. El catálogo debe representar el universo completo y etiquetar el rol, para que sistemas posteriores (economía, enciclopedia, farmeo) puedan filtrar sin reinterpretar rAthena.

## 7.2. Campos

### Identificación

| Campo | Descripción |
|---|---|
| `mob_id` | ID del monstruo |
| `aegis_name` | Nombre Aegis (`AegisName`) |
| `name` | Nombre en inglés del YAML (`Name`) |
| `display_name` | Nombre visible al jugador, cuando exista fuente distinta |
| `mob_class` | Protocolo de clase rAthena (`Class` YAML): Normal, Boss, Event, … |
| `is_mvp` | Flag **distinto**: tiene recompensa/identidad MVP (`MvpExp` hoy; ampliable) |
| `mob_role` | Rol de aparición / uso del registro (ver abajo) |
| `sprite_name` | Nombre del recurso visual |
| `has_sprite` | Existencia del recurso en el cliente activo |

### Boss protocol vs MVP (dos campos, no uno)

| Campo | Significa | No significa |
|---|---|---|
| `mob_class = Boss` | **Boss protocol** de rAthena (reglas de combate/exp/damage distintas) | Que sea MVP anunciable / farmeable como MVP |
| `is_mvp = true` | Es MVP (hoy: `MvpExp` presente; luego MVP drops/spawn flags) | Que `Class` sea Boss |

Puede haber Boss protocol **sin** ser MVP (mayoría). Puede haber MVP que también sea Boss. **Nunca** colapsar ambos en un solo enum.

### `mob_role` — para qué existe el campo

`mob_role` responde: **¿qué clase de entrada es este registro del `mob_db` en el mundo OzRo?**, no “¿en qué mapa aparece?” (eso es Spawns).

| Rol | Cuándo |
|---|---|
| `map_spawn` | Header `monster`/`boss_monster` de mapa (permanente/event) |
| `instance` | Solo evidencia de aparición en instancia |
| `scripted` | Solo `monster`/`areamonster`/`guardian` en scripts NPC (mob_id resuelto) |
| `slave` | Invocado como slave/summon de otro mob vía `mob_skill_db` (`NPC_SUMMONSLAVE` / `NPC_SUMMONMONSTER`) |
| `skill_summon` | Invocación por skill de **jugador** (evidencia `skill_db` / src `MOBID_*`) |
| `quest_prop` | Evidencia de script de quest/prop |
| `pet` | Pet-only (p. ej. en `pet_db` **sin** ficha usable de mapa; la mayoría de pets tameables son `map_spawn`) |
| `stub` | YAML mínimo sin uso hallado |
| `pending` | **Default honesto:** está en `mob_db`, aún sin evidencia de aparición |

`pending` es válido al cerrar Etapa 2. Se resuelve en **Etapa 3** con esta prioridad de evidencia: headers de mapa → instancia → scripted → slave (`mob_skill_db`) → skill de jugador. No usar `field` como sinónimo de “aún no sabemos”.

### Hallazgo Etapa 3 — volumen de `pending` (esperado, no bug)

Tras headers + scripted + slaves (`mob_skill_db`), OzRo quedó en **~1003 `pending`** (antes ~1137 sin slaves). Roles verificados: `map_spawn` 1199 · `instance` 242 · `slave` 134 · `scripted` 81 · `skill_summon` 8 · `pet` 1 · `quest_prop` 3 · `stub` 4.

Desglose típico de lo que **sigue** `pending`:

| Grupo | ~n | Origen / resolución |
|---|---|---|
| Clones `G_*` no listados como `val` de summon | ~195 | Muchos `G_*` tienen filas propias en `mob_skill_db` (como **padres** con skills) pero **no** aparecen en `val1–val5` de `NPC_SUMMON*`. No inventar `slave`; pueden salir por script NPC o quedar sin uso. |
| `E_*` / event | ~78 | Eventos no cargados o por ítem |
| `MD_*` | ~69 | Instancias / contenido por variable |
| Treasure boxes | ~63 | Scripts de castillo con ID por fórmula |
| `M_*` / `META_*` | ~34 | Variantes quest/job |
| Resto | ~564 | Sin mención estática segura |

**Slaves resueltos:** ~316 mobs únicos invocados vía `NPC_SUMMONSLAVE` / `NPC_SUMMONMONSTER` / `NPC_DEATHSUMMON` (`val[0..4]`, amount = `skill_lv`). De ellos, solo los que no tenían ya `map_spawn`/`instance`/`scripted` reciben `mob_role: slave` (~134); el resto conserva el rol de mayor prioridad.

**Pets:** casi todos los de `pet_db` que existen en campo quedan `map_spawn` (tameables). Solo stubs pet-only llevan `pet`.

### Propiedades

- Raza, tamaño, elemento, nivel.
- HP / ATK / DEF / MDEF / EXP base (valores del YAML).
- Si `Hp` (u otros) **faltan en el YAML**, no inventar en la capa original: registrar null/ausencia. rAthena aplica defaults en runtime (p. ej. `Hp` default 1); eso pertenece a capa efectiva/default documentada, no a fingir que el YAML lo decía.
- Stats, AI, motions, `Modes` originales.
- Otras propiedades del YAML.

Hallazgo Etapa 2: un puñado de registros sin `Hp` declarado no son “corrupción”; son pets, props, summons o stubs. Estudiarlos evita falsos positivos de calidad.

### Comportamiento

Registrar los atributos y comportamientos disponibles:

- Agresivo.
- Asistente.
- Inmóvil.
- Looter.
- Detector.
- Cambia de objetivo.
- Inmunidades.
- Resistencias.
- Habilidades.
- Comportamientos especiales.

No asumir que todos estos comportamientos se representan mediante un único campo. Se deben conservar los flags originales (`Modes`, etc.) y generar una interpretación normalizada en capa aparte.

### Cliente / sprite (riesgos)

- `has_sprite` derivado del inventario cliente (gaps) es útil pero aproximado.
- Usar `AegisName` como `sprite_name` por defecto puede no coincidir 1:1 con el stem real (`jobname` / identity). Etapas posteriores deben preferir el enlace identity→jobname→sprite cuando exista.
- Entradas `no_identity` (dummies de skill, etc.) no son mobs de mundo; no deben mezclarse ciegamente en métricas de “contenido jugable”.

## 7.3. Configuraciones efectivas

Los atributos finales deben incorporar las personalizaciones de OzRo.

Ejemplo:

Si un monstruo tiene un multiplicador custom de HP, la base debe registrar el HP efectivo.

Se recomienda conservar:

```text
hp_base
hp_multiplier
hp_effective
```

Esto permite consultar el valor utilizado en el juego y conocer cómo se obtuvo.

El mismo principio aplica a cualquier atributo modificado.

Para **skill summons**, el HP “efectivo” puede depender del nivel de skill / fórmula del src, no solo de `monster_hp_rate`. No aplicar rates genéricos como si fueran mobs de campo sin verificar.

## 7.4. Fuentes

| Información | Fuente |
|---|---|
| Estadísticas originales | `db/re/mob_db.yml` + merge `db/import/mob_db.yml` (por `Id`; el import puede ser parcial) |
| `mob_class` | Campo `Class` del YAML (default `Normal` si ausente) |
| MVP | `MvpExp` / MVP drops / spawns — no el enum `Class` |
| `mob_role` | Inferencia: spawns headers/scripted, `mob_skill_db` (slaves), `pet_db`, `skill_db` + enums src, stubs |
| Comportamiento original | `Modes`, AI, etc. en `mob_db` |
| Sprite / gaps | Inventario cliente (`client_mob_*`) |
| Personalizaciones de rates | Archivos conf → Effective Resolver (Etapa 4) |
| Habilidades de monstruo | `mob_skill_db` y scripts |
| Propiedades finales | Effective Resolver |

### Merge de import (hallazgo)

`db/import/mob_db.yml` no siempre reemplaza la ficha completa: a menudo solo pisa campos (`DamageTaken: 100` en bosses). El extractor debe hacer merge superficial por `Id` y marcar `import_override` sin asumir “mob 100 % custom”.

---

# 8. SPAWNS — Apariciones de monstruos

Este dominio debe estar separado de MOBS.

Un monstruo es una entidad. Un spawn es una configuración concreta de aparición.

Un mismo monstruo puede tener muchos registros de spawn, incluso dentro del mismo mapa.

## 8.1. Objetivo

Construir la representación más completa posible de las apariciones de monstruos en OzRo.

La información debe permitir estimar posteriormente:

- Cantidad de monstruos disponibles.
- Distribución por mapa.
- Frecuencia de aparición.
- Disponibilidad temporal.
- Competencia potencial por recursos.
- Disponibilidad de drops.
- Tiempo de reposición.

## 8.2. Campos

| Campo | Descripción |
|---|---|
| `spawn_id` | Identificador estable |
| `mob_id` | Monstruo asociado |
| `map_id` | Mapa |
| `spawn_type` | Tipo de spawn |
| `amount` | Cantidad |
| `x` | Coordenada X |
| `y` | Coordenada Y |
| `x_area` | Extensión horizontal |
| `y_area` | Extensión vertical |
| `respawn_min` | Tiempo mínimo |
| `respawn_max` | Tiempo máximo |
| `respawn_unit` | Unidad temporal |
| `spawn_condition` | Condiciones |
| `event_id` | Evento relacionado |
| `script_id` | Script relacionado |
| `source` | Procedencia |

## 8.3. Tipos de spawn

| Tipo | Descripción |
|---|---|
| `permanent` | Aparición recurrente (archivos `monster` de mapa) |
| `timed` | Aparición controlada por temporizador |
| `one_time` | Aparición única |
| `event` | Aparición de evento |
| `scripted` | Aparición generada por script (`monster`/`areamonster`/`guardian` en NPC) |
| `slave` | **Slave/summon de boss u otro mob** vía `mob_skill_db` (`NPC_SUMMONSLAVE` / `NPC_SUMMONMONSTER`). Sin `map_id` fijo: aparece donde esté el padre. Guardar `parent_mob_id` + skill. |
| `skill_summon` | Invocación por skill de jugador (no es spawn de mapa) |
| `pet` | Vinculado a `pet_db` / egg; no spawn de campo |
| `instance` | Aparición asociada a instancia |
| `unknown` | No determinada |

También debe identificarse si la aparición es natural o generada mediante un script.

**Hallazgo Etapa 3:** los slaves de MVP/boss **no** aparecen como headers `monster` ni siempre como `monster()` en NPC. Sin barrer `mob_skill_db` quedan como `mob_role: pending`. Es un tipo de spawn de primera clase.

**Extracción verificada (OzRo):** ~1177 filas `spawn_type: slave` (`map_id` null, `spawn_kind: mob_skill_summon`) a partir de `skill_summons`; total spawns ~9375 (permanent 3565 · instance 2840 · scripted 1758 · slave 1177 · event 35).

**Semántica rAthena:** `mob_summonslave()` usa hasta **5** IDs en `val[]` (round-robin) y `skill_lv` como **cantidad**. Skills: `NPC_SUMMONSLAVE`, `NPC_SUMMONMONSTER`, `NPC_DEATHSUMMON`. No basta con `val1`.

Los tipos `slave`, `skill_summon` y `pet` **no** cuentan como densidad de farmeo de un `map_id`. Pueden vivir como filas de spawn con `map_id` null + metadatos, y/o como relaciones mob↔mob / mob↔skill en el dominio Skills.

Campos adicionales cuando aplique:

| Campo | Uso |
|---|---|
| `parent_mob_id` | Mob que invoca (slaves) |
| `skill_id` / `skill_name` | Skill de invocación |
| `amount` | Cantidad (`skill_lv` en summons de mob) |
| `map_id` | **Nullable** para `slave` / `skill_summon` / parciales scripted |

## 8.4. Spawns dinámicos

No todos los spawns estarán declarados en archivos de configuración convencionales.

Se deben inspeccionar los scripts que generen monstruos mediante comandos de aparición, especialmente cuando tengan:

- Condiciones de ejecución.
- Temporizadores.
- Cantidades variables.
- Áreas específicas.
- Relación con quests.
- Relación con instancias.
- Apariciones de MVP.
- Eventos.
- Blancos / props de job quests (p. ej. Rebellion en `job_gun`).
- Summons de clase referenciados solo desde `skill_db` / código (`MOBID_*`), sin línea `monster` en mapa.

Cuando una aparición dependa de condiciones que no puedan resolverse estáticamente, se debe registrar la información conocida y documentar la condición pendiente.

No se debe presentar como permanente una aparición que depende de una ejecución o condición especial.

Cuidado con falsos positivos al buscar IDs numéricos en scripts: el mismo entero puede ser `quest_id`, precio, timer o mob id. Preferir `AegisName` / contexto `monster` / tablas skill-pet.

## 8.5. Cálculos derivados

Se pueden generar datos agregados:

- Total de apariciones por monstruo.
- Total de apariciones por mapa.
- Cantidad total configurada.
- Tiempo de respawn normalizado.
- Distribución por tipo de spawn.

Estos datos deben derivarse de los registros individuales, no reemplazarlos.

---

# 8bis. SKILLS — Catálogo de skills (jugador y monstruo)

**Nuevo dominio (Etapa 3).** No se contempló al inicio; el barrido de skills es obligatorio para cerrar spawns/roles de mobs y para informar el análisis de NPCs.

## 8bis.1. Objetivo

Representar de forma estructurada:

1. Skills de **jugador** relevantes al mundo de datos (summons, consumos de ítem, warps, crafting ligado a skill, etc.).
2. Skills de **monstruo** (`mob_skill_db`), en especial invocaciones.

Debe permitir responder:

- ¿Qué mobs invoca este boss (slaves)?
- ¿Qué skill de jugador invoca qué mob (`skill_summon`)?
- ¿Qué skills usan monstruos (para enciclopedia / dificultad)?
- ¿Qué relaciones mob↔skill existen sin pasar por scripts NPC?

## 8bis.2. Fuentes

| Información | Fuente |
|---|---|
| Skills de monstruo + slaves | `db/re/mob_skill_db.txt` (+ import si existe) |
| Skills de jugador / summons | `db/re/skill_db.yml` (+ import) |
| IDs `MOBID_*` de summons | Código src / enums (cuando el YAML no baste) |
| Condiciones / rates | Mismos archivos (capa original; efectiva en Etapa 4 si aplica) |

## 8bis.3. Modelo mínimo

### Catálogo de skill (opcional al inicio; ampliable)

| Campo | Descripción |
|---|---|
| `skill_id` | ID |
| `aegis_name` / `name` | Nombre |
| `skill_owner` | `player` / `monster` / `both` |
| `source` | Procedencia |

### Relación de invocación (obligatoria en Etapa 3)

| Campo | Descripción |
|---|---|
| `summon_id` | Identificador estable |
| `summon_kind` | `mob_slave` / `player_skill_summon` / … |
| `parent_mob_id` | Mob invocador (si aplica) |
| `skill_id` | Skill usada |
| `summoned_mob_id` | Mob invocado |
| `amount` / condiciones | Cuando consten (p. ej. `slavele`, rate) |
| `source` | Archivo + línea / registro |

Estas relaciones **alimentan** Spawns (`spawn_type: slave` o `skill_summon`) y resuelven `mob_role` pendientes.

## 8bis.4. Orden en Etapa 3

1. Map Connections (+ Dijkstra).
2. Spawns (headers + scripted).
3. **Skills / mob skills** ← aquí.
4. Reconciliar Spawns slaves + `mob_role`.
5. **NPCs** (análisis de script; puede añadir más summons scripted y relaciones).
6. Resto (drops, shops, quests, …).

Sin el paso 3, cientos de `G_*` y slaves de MVP quedan `pending` sin motivo de calidad de datos.

## 8bis.5. Reglas

- No inventar slaves: solo `val[0..4]` de skills de summon en `mob_skill_db` (`NPC_SUMMONSLAVE` / `NPC_SUMMONMONSTER` / `NPC_DEATHSUMMON`).
- `amount` = `skill_lv` (no confundir con el ID del mob).
- No contar slaves/skill_summon en densidad de farmeo por mapa.
- Separar summon de jugador (`skill_summon`) vs slave de mob (`slave`).
- Trazabilidad hasta la fila de `mob_skill_db` / skill YAML.
- Un `G_*` con skills propias **no** implica `slave`; solo si algún padre lo lista en `val[]`.

## 8bis.6. Hallazgos verificados (OzRo)

| Métrica | Valor |
|---|---|
| Filas `mob_skill_db` parseadas | 14449 |
| Relaciones `skill_summons` (`mob_slave`) | 1177 |
| Padres únicos / invocados únicos | 294 / 316 |
| `spawn_type: slave` materializados | 1177 |
| `mob_role: slave` (prioridad tras map/instance/scripted) | 134 |
| `pending` restante tras slaves | ~1003 |
| Diferido | summons de jugador (`skill_db`), catálogo completo de skills de jugador |

---

# 9. ITEMS — Catálogo maestro de ítems

## 9.1. Objetivo

Construir un catálogo completo de los ítems utilizables en OzRo, con sus propiedades, restricciones, scripts y relaciones.

El modelo debe respetar la estructura original de rAthena, pero permitir una clasificación normalizada para los sistemas posteriores.

## 9.2. Identificación

| Campo | Descripción |
|---|---|
| `item_id` | ID del ítem |
| `name` | Nombre técnico |
| `display_name` | Nombre visible |
| `item_type` | Tipo original |
| `item_category` | Categoría normalizada |
| `item_subcategory` | Subcategoría |
| `sprite_name` | Recurso visual |
| `has_sprite` | Existencia del recurso |
| `description` | Descripción, cuando esté disponible |

## 9.3. Categorías

La clasificación debe incluir, como mínimo:

| Categoría | Ejemplos |
|---|---|
| Weapon | Armas |
| Armor | Armaduras / headgear de combate (no costume) |
| Costume | Equipamiento costume (ver abajo) |
| Garment | Capas |
| Shoes | Zapatos |
| Accessory | Accesorios |
| Shadow Gear | Equipamiento Shadow |
| Card | Cartas |
| Enchantment | Encantamientos |
| Consumable | Consumibles |
| Usable | Objetos utilizables |
| Healing | Objetos de curación |
| Taming | Objetos de domesticación |
| Pet Egg | Huevos de mascota |
| Monster | Objetos relacionados con monstruos |
| Miscellaneous | Materiales y objetos varios |
| Quest | Objetos de quest |
| Currency | Monedas y recursos económicos |
| Ammo | Munición |
| Cash | Ítems cash shop (tipo original `Cash`) |

Las categorías deben poder ampliarse sin modificar la estructura principal.

### Costume vs Armor (hallazgo Etapa 2)

En rAthena RE, los costumes **no** son un `Type` distinto: son `Type: Armor` con `Locations` `Costume_*`.

Observado en OzRo (~3104 ítems):

| Location | Rol visual |
|---|---|
| `Costume_Head_Top` | Headgear top costume |
| `Costume_Head_Mid` | Headgear mid costume |
| `Costume_Head_Low` | Headgear low costume |
| `Costume_Garment` | Garment/cape costume |

Implicación de modelo:

1. **Capa original:** `type`, `locations` (dict YAML) — única fuente cruda.
2. **`is_costume`:** true si alguna location es `Costume_*`.
3. **`item_category`:** `Costume` cuando `is_costume`.
4. **Slots normalizados:** ver regla de verdad única abajo (aplica a costume y no costume).

Shadow Gear es ortogonal: locations `Shadow_*` (y/o `Type: ShadowGear`) → categoría `Shadow Gear`, no costume.

No usar el nombre del ítem (“Costume …”) como fuente de verdad; solo `Locations`.

### Verdad única de slots de equipo (Etapa 2 — corregir dualidad)

**Prohibido** mantener un `equip_location` “primario” parcial además de `locations` como si fueran dos verdades.

| Campo | Capa | Regla |
|---|---|---|
| `locations` | original | Dict/list exacto del YAML. |
| `equip_slot_key` | normalized | **Una** clave sintética derivada del conjunto ordenado de locations de equipo (no cards). |
| `equip_slot_families` | normalized | Lista de familias (`head_top`, `garment`, …) cubiertas por ese conjunto. |

Ejemplos de `equip_slot_key` (sintéticos):

| Locations | `equip_slot_key` |
|---|---|
| `Head_Top` | `head_top` |
| `Head_Top`+`Head_Mid` | `headgear_top_mid` |
| `Head_Top`+`Head_Mid`+`Head_Low` | `headgear_entire` |
| `Costume_Head_Top`+`Costume_Head_Mid` | `costume_headgear_top_mid` |
| `Costume_*` (las tres) | `costume_headgear_entire` |
| `Right_Hand` | `right_hand` |

La función de síntesis vive en el normalizador de ítems (Etapa 2). Ampliar la tabla de sintéticos sin cambiar el esquema.

### Cards: campo aparte (no reutilizar equip slots)

Las `Locations` de una **Card** significan *en qué slot de equipo puede insertarse la carta*, no que la carta se “equipe” como armadura.

| Campo | Uso |
|---|---|
| `card_insert_slots` | Lista/clave sintética de slots donde la carta puede ir |
| `equip_slot_key` | **null** para `Type: Card` |

No exponer cards en filtros de “equipamiento por slot” via `equip_slot_key`.

### Separación de Cards y Enchantments

Es importante distinguir las cartas de los encantamientos.

Las cartas son ítems identificables con su propio ID y comportamiento.

Los encantamientos representan modificaciones o propiedades que pueden aplicarse a equipamiento, que usan slots especiales (Hidden Socket Enchant y cosas por el estilo) por ejemplo:

- STR +1.
- AGI +1.
- DEX +1.
- Bonificaciones de atributos.
- Bonificaciones de combate.
- Efectos especiales.

No deben tratarse automáticamente como cartas.

Los encantamientos deben tener su propio dominio y sus propias relaciones con los equipos, NPC, materiales y mecanismos de aplicación.

Cuando una carta contenga efectos que representen bonificaciones, estos deben conservarse como propiedades de la carta, sin convertir la carta completa en un enchant.

## 9.4. Propiedades

Los campos deben depender del tipo de ítem.

### Propiedades generales

- Peso.
- Nivel requerido.
- Nivel mínimo de equipamiento.
- Restricción de clase.
- Restricción de género, cuando aplique.
- Restricciones de uso.
- Tipo de equipamiento.

### Propiedades de equipamiento

- ATK.
- DEF.
- Slots.
- Nivel de arma.
- Posición de equipamiento.
- Refinable.
- Elemento.
- Bonificaciones.
- Restricciones de clase.
- Scripts de equipamiento.

### Propiedades de consumibles

- Efectos.
- Duración.
- Cantidad de usos.
- Condiciones de aplicación.
- Restricciones.

### Propiedades especiales

- Comportamiento de mascota.
- Propiedades de domesticación.
- Efectos de cartas.
- Funciones de materiales.
- Funciones relacionadas con quests.

No se deben crear campos con valores ficticios para propiedades que no correspondan a un tipo de ítem.

Se debe tener en cuenta un origen particular que es el sistema Socket Enchant (Slot Addition)  que es por probabilidad, esta descrito en los npc Seiyablem y Leablem.
asi como identificar (y aqui detenerse y confirmar con el usuario) posibles NPC similares que eliminan un objeto y devuelven otro distinto.
como Armor Enchant (Stat Addition) del NPC Apprentice Craftsman
Bain & Bajin (aunque no es tan relevante y lo podriamos ignorar)
la creacion de tintes Dye Maker JavaDullihan
la creacion de Counteragent y Mixture con el npc Morgenstein
o el Equipment gambling con Kachua (que usa diamantes, pero como se pueden comprar...)
todas estas fuentes adicionales servirán como insumo para crear guias especificas en la pagina web

---

# 10. ITEM SCRIPTS — Scripts de los ítems

Esta parte requiere especial atención.

Los ítems pueden tener más de un script asociado y estos pueden ejecutarse en momentos distintos.

Por ejemplo:

- Script de uso.
- `OnEquip`.
- `OnUnequip`.
- Scripts de efectos pasivos.
- Scripts asociados a condiciones.
- Scripts relacionados con eventos de equipamiento.

El extractor no debe asumir que un ítem tiene un único campo de script.

## 10.1. Modelo recomendado

Separar los scripts en una tabla propia.

Cada registro debe representar un script asociado a un ítem.

| Campo | Descripción |
|---|---|
| `item_script_id` | Identificador estable |
| `item_id` | Ítem asociado |
| `script_type` | Tipo de script |
| `trigger` | Momento de ejecución |
| `script_content` | Contenido original |
| `script_hash` | Hash del contenido |
| `source_file` | Archivo de origen |
| `source_location` | Ubicación dentro del archivo |
| `parsed_effects` | Efectos interpretados |
| `parse_status` | Estado del análisis |

## 10.2. Reglas

1. Conservar el contenido original.
2. Registrar todos los scripts asociados.
3. No sobrescribir un script con otro.
4. Diferenciar el momento de ejecución.
5. Permitir varios scripts del mismo tipo.
6. Identificar efectos interpretables.
7. Mantener trazabilidad hasta el origen.

El análisis semántico de los scripts puede ser asistido por LLM, pero el contenido original debe permanecer intacto.

---

# 11. ITEM RESTRICTIONS — Restricciones

Las restricciones deben almacenarse de forma normalizada.

Entre ellas:

- NoDrop.
- NoTrade.
- NoSell.
- NoStorage.
- NoCart.
- NoMail.
- NoAuction.
- Restricciones de equipamiento.
- Restricciones de uso.
- Restricciones de clase.
- Restricciones especiales.

Se debe conservar el valor original y su interpretación.

No confundir restricciones diferentes.

Por ejemplo, impedir que un objeto se venda a NPC no implica necesariamente impedir el intercambio entre jugadores.

El sistema debe exponer cada restricción por separado.

---

# 12. ITEM ECONOMY — Valores nativos de NPC

Los valores `Buy` y `Sell` de rAthena deben resolverse durante la extracción.

La base debe registrar los valores efectivos.

## 12.1. Reglas

Cuando ambos valores estén definidos, se conservan.

Cuando falte uno, debe aplicarse la regla nativa de rAthena:

- Si falta `Buy`, se calcula como el doble de `Sell`.
- Si falta `Sell`, se calcula como la mitad de `Buy`.

Ejemplo:

| Buy original | Sell original | Buy efectivo | Sell efectivo |
|---:|---:|---:|---:|
| 1000 | 500 | 1000 | 500 |
| Ausente | 500 | 1000 | 500 |
| 1000 | Ausente | 1000 | 500 |

La implementación debe respetar las reglas de valores por defecto y redondeo de la versión de rAthena utilizada por OzRo.

Si ambos valores están ausentes, debe verificarse el comportamiento nativo correspondiente y registrarse el resultado efectivo sin inventar un valor.

## 12.2. Campos recomendados

- `buy_value_original`.
- `sell_value_original`.
- `buy_value_effective`.
- `sell_value_effective`.
- `buy_value_source`.
- `sell_value_source`.
- `value_was_derived`.

Los sistemas posteriores consumirán exclusivamente los valores efectivos, salvo que necesiten consultar la procedencia.

---

# 13. ENCHANTMENTS — Catálogo de encantamientos

Los encantamientos deben ser entidades propias.

No deben quedar escondidos dentro de la categoría de cartas ni representados únicamente como texto en un script.

## 13.1. Información

| Campo | Descripción |
|---|---|
| `enchant_id` | Identificador estable |
| `name` | Nombre técnico |
| `display_name` | Nombre visible |
| `enchant_type` | Categoría |
| `effects` | Efectos |
| `stat_modifiers` | Modificadores de atributos |
| `source` | Procedencia |

## 13.2. Relaciones

Se debe registrar:

- Equipos compatibles.
- NPC que los aplican.
- Materiales requeridos.
- Costos.
- Probabilidades.
- Condiciones.
- Restricciones.
- Recetas o procedimientos asociados.

Un encantamiento puede estar disponible en más de un equipo o mecanismo.

---

# 14. ACQUISITION SOURCES — Fuentes de obtención

Este es uno de los dominios más importantes del sistema.

Cada ítem debe poder relacionarse con todas las formas identificadas de obtención.

No se debe limitar la extracción a los drops de monstruos.

## 14.1. Tipos de fuente

| Tipo | Descripción |
|---|---|
| `mob_drop` | Drop de monstruo |
| `map_drop` | Drop asociado a mapa |
| `npc_shop` | Compra a NPC |
| `npc_reward` | Recompensa entregada por NPC |
| `quest_reward` | Recompensa de quest |
| `instance_reward` | Recompensa de instancia |
| `box_reward` | Contenido de caja |
| `crafting` | Producción mediante receta |
| `guild_reward` | Recompensa de guild |
| `castle_reward` | Recompensa de castillo |
| `enchanting` | Obtención o aplicación de enchant |
| `socketing` | Modificación mediante socket |
| `event_reward` | Recompensa de evento |
| `scripted` | Fuente personalizada |
| `other` | Fuente identificada no clasificada |

## 14.2. Modelo de fuentes

Se recomienda utilizar una entidad central `acquisition_sources` y tablas de detalle para cada mecanismo.

La fuente representa el mecanismo de obtención.

Los resultados representan los ítems producidos.

Esto permite modelar correctamente:

- Una caja que entrega varios posibles ítems.
- Una receta que consume varios materiales.
- Una quest que entrega varias recompensas.
- Una instancia con diferentes recompensas.
- Un NPC que ofrece varios servicios.

## 14.3. Campos generales

| Campo | Descripción |
|---|---|
| `source_id` | Identificador estable |
| `source_type` | Tipo de fuente |
| `source_name` | Nombre descriptivo |
| `source_description` | Descripción |
| `npc_id` | NPC asociado |
| `map_id` | Mapa relacionado |
| `script_id` | Script relacionado |
| `conditions` | Condiciones de acceso |
| `is_repeatable` | Si puede repetirse |
| `source_status` | Estado |
| `source_provenance` | Procedencia |

## 14.4. Resultados

Cada fuente debe poder entregar uno o varios resultados.

| Campo | Descripción |
|---|---|
| `source_output_id` | Identificador |
| `source_id` | Fuente |
| `item_id` | Ítem producido |
| `quantity_min` | Cantidad mínima |
| `quantity_max` | Cantidad máxima |
| `probability` | Probabilidad |
| `probability_unit` | Unidad |
| `conditions` | Condiciones |
| `output_type` | Tipo de resultado |

Las probabilidades deben conservar su unidad original y, cuando sea posible, su valor efectivo.

---

# 15. DROPS — Extracción de drops

Los drops deben tener un modelo específico.

Se debe contemplar:

- Drops normales.
- Drops MVP.
- Drops especiales.
- Drops configurados mediante scripts.
- Drops asociados a eventos.
- Drops sujetos a rates personalizados.

## 15.1. Campos

- `drop_id`.
- `mob_id`.
- `item_id`.
- `quantity_min`.
- `quantity_max`.
- `rate_original`.
- `rate_effective`.
- `rate_unit`.
- `drop_category`.
- `conditions`.
- `source_file`.
- `source_record`.

## 15.2. Aplicación de rates

Los rates personalizados deben resolverse durante la generación del dataset.

El extractor debe leer los archivos de configuración y aplicar las mismas reglas que utiliza el servidor.

No se debe implementar una multiplicación genérica si rAthena utiliza reglas diferentes para categorías de drops.

Debe contemplarse la configuración específica para:

- Drops normales.
- Drops MVP.
- Drops de cartas.
- Drops especiales.
- Otros grupos de drops configurados.

El resultado debe ser el rate efectivo utilizado por OzRo.

Se conservará también el valor original para auditoría.

---

# 16. NPC SHOPS — Tiendas

Las tiendas deben tener su propio modelo.

Un NPC puede tener varias tiendas y cada tienda puede ofrecer diferentes productos.

## 16.1. Campos

### Tienda

- `shop_id`.
- `npc_id`.
- `shop_name`.
- `shop_type` — `shop` / `cashshop` / `itemshop` / `pointshop` / `marketshop`.
- `currency` — `zeny` / `cash` / `item:<id>` / `var:<name>`.
- `cost_item_id` / `cost_variable` — cuando aplique.
- `discount` — yes/no del header, si consta.
- `conditions`.
- `source_script` (+ línea).

### Productos

- `shop_id`.
- `item_id`.
- `price` — `-1` = default `item_db` (`price_is_default`).
- `stock` — solo `marketshop` (`item:price:qty`).
- `conditions`.

Debe contemplarse tanto la compra como la venta de ítems por parte de NPC.

También deben identificarse las tiendas que utilicen monedas o recursos distintos de Zeny.

**Etapa 3 (hecho):** headers + `npc_shop_links` (`callshop` literal/prefijo → `shop_ids` + inventario ya extraído).

**Diferido (documentado a propósito):**

| Qué | Por qué después |
|---|---|
| Inventario **barter** (`barters.yml` + imports) | Modelo distinto (coste en ítems/`RequiredItems`, no `item:price` de shop). ~23 callshops + NPCs barter. |
| `callshop` con variable/array | 1 caso; requiere análisis de asignación de `.@shopname$[]`. |
| Buysell / `npcshopadditem` runtime | Inventario mutado en script; no header estático. |
| Precio efectivo de `-1` | Etapa 4 (`item_db` buy price + rates). |

---

# 17. QUESTS — Catálogo de quests

Las quests deben representarse como entidades propias.

## 17.1. Información

- Identificador.
- Nombre.
- Descripción.
- Tipo.
- NPC involucrados.
- Mapas relacionados.
- Requisitos.
- Objetivos.
- Ítems requeridos.
- Monstruos involucrados.
- Recompensas.
- Condiciones de repetición.
- Scripts asociados.

## 17.2. Relaciones

Una quest puede involucrar varios NPC, mapas, monstruos e ítems.

Un mismo NPC puede participar en varias quests.

Debe existir una relación explícita entre estas entidades.

Cuando una quest sea compleja o condicional, se debe conservar el script original y documentar el grado de interpretación alcanzado.

---

# 18. INSTANCES — Instancias

Las instancias requieren un dominio independiente porque pueden tener condiciones y comportamientos propios.

Extraer:

- Identificador.
- Nombre.
- Scripts.
- Mapas.
- NPC de entrada.
- Requisitos.
- Tiempo de espera.
- Duración.
- Monstruos.
- Spawns.
- Recompensas.
- Ítems requeridos.
- Condiciones de finalización.
- Recompensas por etapa.

Las apariciones de monstruos dentro de instancias deben relacionarse con el sistema general de spawns, conservando la referencia a la instancia.

---

# 19. BOXES & REWARDS — Cajas y recompensas

Las cajas y sistemas de recompensas deben tener una representación explícita.

Debe ser posible conocer:

- Qué ítems pueden obtenerse.
- En qué cantidades.
- Con qué probabilidades.
- Bajo qué condiciones.
- Qué script define el contenido.
- Si existen cajas anidadas.

Una caja que entrega otra caja debe representarse mediante relaciones entre fuentes, sin perder la cadena de obtención.

También deben contemplarse recompensas entregadas mediante NPC, quests, instancias, eventos y scripts personalizados.

---

# 20. RECIPES & CRAFTING — Recetas

Las recetas deben representar tanto los materiales consumidos como los resultados producidos.

## 20.1. Información

- `recipe_id`.
- Nombre.
- NPC asociado.
- Script asociado.
- Ítem resultado.
- Cantidad producida.
- Materiales requeridos.
- Cantidades.
- Costo en Zeny.
- Probabilidad de éxito.
- Condiciones.
- Requisitos de nivel, clase o quest.
- Resultado en caso de fallo.
- Materiales consumidos en caso de fallo.

Es importante distinguir entre:

- Materiales requeridos.
- Materiales consumidos.
- Materiales devueltos.
- Costos no recuperables.
- Resultados posibles.

No todas las recetas son equivalentes.

El modelo debe permitir representar procesos destructivos, probabilísticos o con múltiples resultados.

---

# 21. ENCHANTING & SOCKETING

(ver 14. ACQUISITION SOURCES)

---

# 22. RELATIONSHIPS — Relaciones entre ítems

Además de las fuentes de obtención, es necesario identificar relaciones funcionales.

Por ejemplo:

- Combos de cartas.
- Equipos que funcionan conjuntamente.
- Materiales de una receta.
- Ítems utilizados por habilidades.
- Ítems consumidos por otros ítems.
- Equipos compatibles con encantamientos.
- Equipos que admiten refinamiento.
- Equipos con sockets.
- Ítems requeridos por quests.

Estas relaciones deben almacenarse explícitamente.

No se deben dejar únicamente como información textual dentro de scripts.

## 22.1. Combos

Registrar:

- Identificador del combo.
- Ítems participantes.
- Efectos.
- Condiciones.
- Script de origen.

Un combo puede involucrar dos o más ítems.

## 22.2. Dependencias

Registrar las relaciones de consumo, producción y compatibilidad.

Esto permitirá construir posteriormente grafos de recetas y dependencias.

---

# 23. SOURCE PROVENANCE — Procedencia de los datos

La trazabilidad es obligatoria.

Cada entidad y relación debe poder rastrearse hasta su origen.

## 23.1. Información de procedencia

| Campo | Descripción |
|---|---|
| `source_type` | Tipo de fuente |
| `source_file` | Archivo |
| `source_record` | Registro original |
| `source_script` | Script |
| `source_location` | Ubicación dentro del archivo |
| `extraction_method` | Método utilizado |
| `transformation` | Transformación aplicada |
| `verification_status` | Estado de verificación |
| `extracted_at` | Fecha de extracción |
| `source_hash` | Hash de la fuente |

No es obligatorio duplicar todos estos campos en cada tabla si se implementa un sistema de procedencia centralizado.

Lo importante es que la trazabilidad pueda consultarse sin ambigüedad.

## 23.2. Tipos de información

Todos los datos deben distinguirse entre:

| Tipo | Descripción |
|---|---|
| `source` | Extraído directamente |
| `normalized` | Transformado a una estructura común |
| `effective` | Resultado de aplicar configuraciones |
| `derived` | Calculado a partir de otros datos |
| `inferred` | Interpretado con evidencia incompleta |
| `manual` | Confirmado mediante intervención manual |

No se deben presentar datos inferidos como hechos confirmados.

---

# 24. CONFIGURATION RESOLUTION — Resolución de configuraciones

Este componente es transversal a todos los dominios.

Su responsabilidad es leer las configuraciones de OzRo y resolver los valores efectivos.

## 24.1. Objetivo

Evitar que cada extractor implemente su propia lógica de configuración.

Debe existir un componente central que:

1. Identifique los archivos de configuración.
2. Lea los valores activos.
3. Resuelva prioridades y overrides.
4. Aplique los modificadores correspondientes.
5. Exponga los valores efectivos a los extractores.
6. Documente las transformaciones realizadas.

## 24.2. Ejemplos

| Personalización | Dominio afectado |
|---|---|
| Multiplicador de HP | Mobs |
| Modificadores de ATK/DEF | Mobs |
| Rates de drop | Drops |
| Rates de experiencia | Mobs / configuración |
| Modificadores de aparición | Spawns |
| Buy/Sell por defecto | Items |

La lista anterior es ilustrativa. El equipo debe identificar las configuraciones reales de OzRo y documentar cuáles afectan a cada dominio.

## 24.3. Reglas

- No duplicar lógica de configuración.
- No aplicar una transformación dos veces.
- No asumir valores por defecto sin verificar la versión de rAthena.
- No utilizar valores de una ejecución anterior.
- Conservar los valores originales cuando sea necesario.
- Registrar la configuración utilizada para generar cada versión.

---

# 25. SQL — Persistencia del Master World Dataset

Toda la información consolidada debe almacenarse en SQL.

No se debe utilizar un conjunto de JSON como almacenamiento definitivo del sistema.

Los archivos JSONL pueden utilizarse como formato intermedio de extracción, intercambio o depuración, pero SQL será la fuente de consumo para los sistemas posteriores.

## 25.1. Prefijo de tablas

Todas las tablas deben utilizar un prefijo común.

Prefijo propuesto:

`ozro_`

Ejemplos:

```text
ozro_maps
ozro_map_connections

ozro_npcs
ozro_npc_quests
ozro_npc_functions

ozro_mobs
ozro_spawns

ozro_skills
ozro_mob_skills
ozro_skill_summons

ozro_items
ozro_item_properties
ozro_item_scripts
ozro_item_restrictions
ozro_item_enchantments

ozro_acquisition_sources
ozro_source_outputs

ozro_mob_drops
ozro_npc_shops
ozro_npc_shop_items

ozro_quests
ozro_instances

ozro_boxes
ozro_box_rewards

ozro_recipes
ozro_recipe_materials

ozro_enchantments
ozro_enchantment_materials

ozro_item_combos
ozro_item_relationships

ozro_source_provenance
ozro_dataset_metadata
```

El prefijo debe estar centralizado en la configuración del proyecto, no escrito manualmente en cada extractor.

## 25.2. Diseño relacional

Se deben utilizar:

- Primary Keys.
- Foreign Keys cuando corresponda.
- Índices sobre identificadores de relación.
- Índices sobre campos de consulta frecuente.
- Tipos adecuados para probabilidades y cantidades.
- Restricciones de integridad.

No se deben almacenar listas de IDs como texto separado por comas cuando puedan representarse mediante tablas de relación.

## 25.3. Identificadores estables

Los registros deben tener identificadores reproducibles.

Ejemplos:

- `item_id` para ítems.
- `mob_id` para monstruos.
- `map_id` para mapas.
- Identificadores compuestos o hashes deterministas para relaciones y fuentes.

No utilizar IDs autoincrementales como única forma de identificar una relación que deba reconstruirse de manera idempotente.

## 25.4. Sincronización idempotente

La escritura en SQL debe realizarse mediante un proceso controlado.

Requisitos:

1. Generar el resultado completo en una etapa temporal.
2. Validar los registros.
3. Abrir una transacción.
4. Sincronizar las tablas correspondientes.
5. Mantener consistencia entre entidades y relaciones.
6. Confirmar la transacción únicamente si la operación completa es válida.
7. Registrar la versión generada.

Una extracción fallida no debe dejar una mezcla de información anterior y nueva.

---

# 26. ESTRUCTURA DE PROYECTO RECOMENDADA

La implementación debe organizarse por dominios y responsabilidades.

```text
ozro-data/
│
├── config/
│   ├── extractor.yml
│   ├── database.yml
│   └── source_registry.yml
│
├── discovery/
│   ├── server_sources.py
│   ├── client_resources.py
│   └── source_manifest.py
│
├── extractors/
│   ├── maps/
│   ├── connections/
│   ├── npcs/
│   ├── mobs/
│   ├── spawns/
│   ├── items/
│   ├── item_scripts/
│   ├── drops/
│   ├── shops/
│   ├── quests/
│   ├── instances/
│   ├── boxes/
│   ├── recipes/
│   ├── enchantments/
│   └── relationships/
│
├── resolvers/
│   ├── configuration_resolver.py
│   ├── database_override_resolver.py
│   ├── item_value_resolver.py
│   ├── mob_stats_resolver.py
│   └── drop_rate_resolver.py
│
├── normalizers/
│   ├── map_normalizer.py
│   ├── mob_normalizer.py
│   ├── item_normalizer.py
│   ├── npc_normalizer.py
│   └── source_normalizer.py
│
├── validators/
│   ├── schema_validator.py
│   ├── relationship_validator.py
│   ├── source_validator.py
│   ├── configuration_validator.py
│   └── integrity_validator.py
│
├── database/
│   ├── schema/
│   ├── repositories/
│   ├── migrations/
│   └── synchronizer.py
│
├── reports/
│
├── tests/
│   ├── fixtures/
│   ├── unit/
│   ├── integration/
│   └── regression/
│
├── pipeline.py
└── README.md
```

Esta estructura es orientativa. El equipo puede adaptarla a la tecnología y convenciones existentes, siempre que mantenga la separación de responsabilidades.

---

# 27. ESTRATEGIA DE IMPLEMENTACIÓN PARA LOS AGENTES

No recomiendo que todos los agentes empiecen a desarrollar extractores simultáneamente sin una estructura compartida.

Primero deben definir los contratos de datos.

## Etapa 1 — Arquitectura y descubrimiento

**Objetivo:** conocer las fuentes y definir el esquema.

Tareas:

1. Inspeccionar la estructura del repositorio de OzRo.
2. Identificar las bases de datos utilizadas.
3. Identificar todos los archivos de configuración.
4. Identificar el orden de carga de las bases de datos.
5. Identificar los directorios de scripts.
6. Identificar las herramientas disponibles.
7. Inspeccionar el GRF mediante `ozro-cli`.
8. Identificar el documento existente de transportes.
9. Elaborar un registro de fuentes.
10. Proponer el esquema SQL definitivo.

Entregables:

- Source Registry.
- Configuration Registry.
- Data Dictionary.
- Esquema SQL.
- Mapa de dependencias entre extractores.

**No comenzar la implementación masiva hasta aprobar los contratos de datos.**

## Etapa 2 — Extractores de entidades principales

Desarrollar:

- Maps.
- Mobs.
- Items.
- NPCs.

Estos dominios constituyen la base para los demás.

Cada extractor debe producir registros normalizados, trazables y verificables.

Campos `pending` (p. ej. `mob_role`, `functions` de NPC) **cierran Etapa 2** si está documentado **cuándo** se resuelven (casi siempre Etapa 3 del dominio relacionado). No inventar etiquetas para “completar” el catálogo.

## Etapa 3 — Extractores de relaciones

**Gate antes de cada paso:** revisar por escrito (1) qué ya existe, (2) qué falta, (3) qué se puede romper, (4) qué se define después, (5) qué no se puede cerrar aún. No implementar hasta esa revisión.

Orden de trabajo (Skills **antes** de NPCs):

1. Map Connections *(+ grafo Dijkstra / fricción)*.
2. Spawns — headers + scripted (`monster`/`areamonster`).
3. **Skills / mob skills** *(§8bis; `mob_skill_db` → slaves)*.
4. Spawns — materializar `slave` / `skill_summon` y **resolver `mob_role`** pendiente con esa evidencia.
5. NPC Shops / análisis de script NPC. *(resuelve `functions` pending; ver §6.3; puede añadir más spawns scripted)*.
6. Item Scripts.
7. Item Restrictions.
8. Drops.
9. Quests.
10. Instances.
11. Boxes.
12. Recipes.
13. Enchantments.
14. Item Relationships.

### Hallazgos ya aplicados / a respetar (Connections + Spawns + Skills)

- **Kafra VIP:** con `#define VIP_SCRIPT 0` el ×2 de precio no aplica; ignorar VIP en grafo/economía de teleports.
- **Airship:** aristas ciudad↔ciudad peso 1.5 (proxy de ir al aeropuerto); sin nodos `airport` por ahora.
- **Boat:** peso 1.2; zeny irrelevante para Dijkstra; puertos a field (`gon_fild01`, `lou_fild01`) son intencionales.
- **Dijkstra:** colapsar paralelas; excluir quest-gated, instancias y `scripted` atajos especiales del grafo.
- **Pets:** tameables de campo = `map_spawn`; casi nunca `pet`.
- **Skills antes de NPC:** §8bis; `mob_skill_db` → `skill_summons` → spawns `slave` → `mob_role`.
- **Slaves:** tipo de spawn obligatorio; `val[0..4]` + `skill_lv`=amount; skills `NPC_SUMMONSLAVE`/`NPC_SUMMONMONSTER`/`NPC_DEATHSUMMON`.
- **`G_*` residuales:** ~195 siguen `pending` tras el barrido — tienen skills como padre, no como `val` de summon; no forzar `slave`.
- **NPC Shops:** headers → `npc_shops` / `npc_shop_items`; `callshop` → `npc_shop_links` (literal/prefijo resuelto; barter solo clasificado).
- **Barter inventory / callshop dinámico / buysell runtime:** diferidos (ver §16).
- **NPC script analysis:** evidencia de cuerpo → `functions`; duplicates heredan; pending ~9k; ruido Transport/Healer aceptado.

## Etapa 4 — Resolución de valores efectivos

Integrar:

- Configuraciones.
- Overrides.
- Multiplicadores.
- Rates.
- Defaults nativos.
- Reglas particulares de OzRo.

Los extractores deben consumir un único componente de resolución.

## Etapa 5 — Persistencia SQL

Implementar:

- Esquema.
- Prefijo.
- Repositorios.
- Transacciones.
- Sincronización idempotente.
- Metadatos de versión.
- Reportes.

## Etapa 6 — Validación integral

Ejecutar la extracción completa y comprobar las relaciones entre todos los dominios.

---

# 28. CRITERIOS DE ACEPTACIÓN

La fase se considerará terminada cuando se cumplan los siguientes requisitos.

| Dominio | Criterio |
|---|---|
| Maps | Catálogo de mapas utilizables completo |
| Connections | Grafo de desplazamiento reconstruido |
| NPCs | Catálogo funcional y relaciones identificadas |
| Mobs | Estadísticas efectivas disponibles |
| Spawns | Apariciones extraídas y clasificadas |
| Items | Catálogo y propiedades normalizadas |
| Item Scripts | Todos los scripts asociados registrados |
| Restrictions | Restricciones normalizadas |
| Buy/Sell | Valores efectivos resueltos |
| Enchantments | Catálogo independiente |
| Drops | Fuentes y rates efectivos |
| Shops | Tiendas y productos |
| Quests | Requisitos, NPC y recompensas |
| Instances | Mapas, condiciones y recompensas |
| Boxes | Contenido y probabilidades |
| Recipes | Materiales, costos y resultados |
| Relationships | Relaciones funcionales reconstruidas |
| Provenance | Procedencia consultable |
| SQL | Todas las tablas utilizan el prefijo |


---

# 32. REGLAS DE DESARROLLO PARA LOS AGENTES

Estas reglas son obligatorias para todos los agentes involucrados.

1. No inventar datos.
2. No asumir que dos campos con nombres parecidos tienen la misma semántica.
3. No asumir unidades.
4. No asumir valores por defecto sin verificar el comportamiento de rAthena utilizado.
5. No sobrescribir información original con valores calculados.
6. No aplicar configuraciones más de una vez.
7. No generar identificadores aleatorios para relaciones.
8. No crear estructuras incompatibles con el esquema compartido.
9. No ocultar errores de interpretación.
10. No descartar silenciosamente registros que no puedan interpretarse.
11. Conservar la procedencia de los datos.
12. Separar datos originales, normalizados, efectivos e inferidos.
13. Mantener los scripts originales disponibles para auditoría.
14. No implementar lógica económica dentro de los extractores.
15. No introducir cálculos de precios de mercado en esta fase.
16. No permitir que los consumidores interpreten nuevamente las fuentes originales.
17. Si hay dudas detenerse y preguntar al usuario.
18. Toda escritura SQL debe respetar la idempotencia.

---

# 33. ENTREGABLE FINAL

El resultado debe ser una base SQL que represente el mundo efectivo de OzRo.

No un conjunto de archivos de extracción aislados ni una colección de información parcialmente interpretada.

Para el desarrollo se puede montar un docker con mariadb o incluso con el sistema completo, pero este debe ser temporal, no quedar en el git y ser facilmente borrable luego de terminar el desarrollo, al final se ejecutará en el servidor y este se conectará directamente a la db de produccion.

Debe ser un sistema capaz de regenerar, validar y sincronizar toda la información desde las fuentes.

El entregable incluye:

1. Extractores por dominio.
2. Configuration Resolver.
3. Normalizadores.
4. Sistema de procedencia.
5. Esquema SQL.
6. Sincronizador idempotente.
7. Validadores.

---

# 34. DEFINICIÓN DE ÉXITO

La prueba definitiva de esta fase será que cualquier sistema posterior pueda responder preguntas sobre OzRo consultando exclusivamente el Master World Dataset.

Por ejemplo:

- ¿Dónde puedo encontrar determinado monstruo?
- ¿Qué cantidad aparece y cada cuánto tiempo?
- ¿Qué objetos puede soltar?
- ¿Cuál es la probabilidad efectiva de obtenerlos?
- ¿Qué NPC vende determinado objeto?
- ¿Qué NPC permite llegar a determinado mapa?
- ¿Qué quests involucran un ítem?
- ¿Qué necesito para fabricar un equipo?
- ¿Qué materiales consume una receta?
- ¿Qué encantamientos puedo aplicar?
- ¿Qué cartas forman un combo?
- ¿Qué restricciones tiene un objeto?
- ¿Cuál es su Buy/Sell efectivo?
- ¿Qué fuente proporciona cada dato?

Y, sobre todo, debe poder responderlo sin volver a leer un archivo de rAthena, interpretar un script original o aplicar nuevamente una configuración.

**El Master World Dataset será la representación estructurada y autoritativa del mundo de OzRo.**

Todo lo demás se construirá encima de él.

---

# 35. INSTRUCCIÓN FINAL PARA EL EQUIPO

Antes de desarrollar los extractores, el equipo debe realizar una inspección técnica de las fuentes disponibles y producir una propuesta de implementación basada en la estructura real de OzRo.

No asumir que las rutas, nombres de archivos, formatos o estructuras son idénticos a una instalación estándar de rAthena.

La prioridad es comprender cómo está organizado el servidor y cómo se cargan realmente sus datos.

El orden de trabajo debe ser:

1. Descubrir las fuentes.
2. Documentar las configuraciones.
3. Definir el esquema SQL.
4. Aprobar los contratos de datos.
5. Implementar los extractores.
6. Implementar la resolución de valores efectivos.
7. Integrar la persistencia.
8. Generar la primera versión completa del Master World Dataset.

La calidad de todos los sistemas posteriores dependerá directamente de la calidad de esta base.