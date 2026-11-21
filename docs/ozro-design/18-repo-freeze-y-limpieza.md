# Repo freeze — limpieza y trash_bin

> **Estado:** `implementado` (2026-11-20)  
> **Contexto:** Versión Renewal estable, `PACKETVER` congelado, contenido nuevo solo vía `custom` (`db/import/`, `conf/import/`, `npc/custom/ozro/`).

## Objetivo

Reducir ruido en el árbol del servidor sin perder referencia: lo que no carga en runtime se archiva en `trash_bin/`; lo experimental descartado por pivote se elimina del repo.

## Qué se hizo

### 1. NPC inactivos → `trash_bin/npc/`

- **Criterio:** scripts `.txt` / `.yml` bajo `npc/` que no aparecen en la cadena activa de `npc/re/scripts_main.conf` (imports + líneas `npc:` sin comentar) ni en imports activos de `npc/barters.yml`.
- **Cantidad:** 335 archivos movidos (manifiesto en `trash_bin/MANIFEST.txt`).
- **Config:** en 17 `.conf` / barters, rutas comentadas actualizadas a `trash_bin/npc/...` para recuperación rápida.
- **Verificación:** 884 entradas `npc:` activas, 0 rutas faltantes en disco.

### 2. Fase “muy seguro” → `trash_bin/`

| Origen | Destino | Notas |
|--------|---------|--------|
| `db/pre-re/` | `trash_bin/db/pre-re/` | Con `RENEWAL`, el loader ignora imports `Mode: Prerenewal` en los `db/*.yml` raíz; no hace falta tocar `Footer`. |
| `npc/pre-re/` | `trash_bin/npc/pre-re/` | Fusionado con scripts pre-re ya archivados; el server usa solo `npc/re/scripts_main.conf`. |
| `db/import-tmpl/` | `trash_bin/db/import-tmpl/` | Plantillas de ejemplo; no se cargan. |
| `doc/` (upstream rAthena) | `trash_bin/doc/` | Documentación del emulador, no runtime. |
| `sql-files/` | `trash_bin/sql-files/` | `use_sql_db: no`; el map-server usa YAML. Útil si algún día se monta SQL desde cero (`main.sql` está en trash). |

### 3. Mercado — datos eliminados

- **`data/market/` eliminado** (pivote: el diseño del master/pricing se rehará desde cero).
- **Sigue en el juego:** Garrett (`npc/custom/ozro/trasher.txt`) y datos web en `ozro-site/`.
- **`tools/market/`** queda en el repo pero apunta a paths ya inexistentes; no usar hasta el rediseño. Ver [13-mercado-npc-tasador.md](./13-mercado-npc-tasador.md) cuando se retome.

## Cómo usar `trash_bin/`

```text
trash_bin/
├── README.md
├── MANIFEST.txt          # listado NPC archivados
├── npc/                  # misma estructura que npc/
├── db/
├── doc/
└── sql-files/
```

- **Consultar:** buscar en `MANIFEST.txt` o `rg` bajo `trash_bin/`.
- **Recuperar un NPC:** mover a `npc/...` o descomentar `npc:` con ruta `trash_bin/npc/...`.
- **Recuperar pre-re / SQL / doc:** copiar de vuelta solo lo necesario; no reimportar carpetas enteras sin revisar.

## Política Ozro (custom only)

| Tipo | Dónde vive |
|------|------------|
| Items, mobs, skills, quests | `db/import/` |
| Rates, features | `conf/import/` |
| NPCs, warps, sistemas jugables | `npc/custom/ozro/` + `npc/scripts_custom.conf` |
| Mapas propios | `db/import/map_index.txt`, `map_cache.dat` en import |
| Contenido oficial no usado | `trash_bin/` (archivar, no borrar) |

**No tocar en limpiezas rutinarias:** `src/`, `3rdparty/`, `db/re/` masivo sin auditoría, `PACKETVER`.

## Trabajo futuro (no hecho aún)

Orden sugerido; cada fase con smoke test (`./map-server --run-once` + checklist en [09-estado-tecnico-y-estabilidad.md](./09-estado-tecnico-y-estabilidad.md) §8–9).

1. **Mapas vs cliente** — diff `conf/maps_athena.conf` contra `.gat` del cliente 2021; comentar mapas ausentes.
2. **Cascada** — por cada mapa quitado: warps, instancias (`db/re/instance_db.yml` + `db/import/instance_db.yml`) y NPC activos que lo referencien.
3. **Episodios / instancias** — desactivar contenido Episode 18–21 si el cliente no lo soporta (NPC + mapas, no borrar DB entera).
4. **Jobs / skills** — límites en `db/import/` (`skill_tree.yml`, `skill_db.yml`, jobs) según lo que el cliente muestre, no recortar `db/re/` a ciegas.
5. **Features apagadas** — con `achievement`, `attendance`, `equipswitch` off en `conf/import/battle_conf.txt`, archivar NPC/DB asociados si siguen cargándose.
6. **Mercado v3** — nuevo diseño en `docs/ozro-market/` y custom; no revivir `data/market/` del repo.

### Herramientas de auditoría

- `tools/npc_inventory.py` — NPC activos e items/shops.
- `tools/mob_spawns.py` — spawns según conf activo.
- Comparación de mapas: §9 de [09-estado-tecnico-y-estabilidad.md](./09-estado-tecnico-y-estabilidad.md).

## Raíz del repositorio (2026-11-20)

Eliminado por no usarse en OzRo:

- `.github/` (CI upstream), `tools/docker/`, `tools/ci/`
- Metadatos upstream: `AUTHORS`, `.mailmap`, `CODE_OF_CONDUCT.md`, `.git-blame-ignore-revs`
- IDE local: `.claude/`, `.cursor/`, `.kilo/`
- `install.sh`, `uninstall.sh` (targets `install`/`uninstall` quitados del `Makefile`)

Nuevo `README.md` orientado a OzRo; atribución y autores históricos apuntan a [rathena/rathena](https://github.com/rathena/rathena).

## Comentarios

<!-- Ideas sueltas de mantenimiento del repo -->