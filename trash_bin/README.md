# trash_bin (Ozro freeze)

Archivo de contenido **no usado** en OzRo Renewal estable. Misma estructura de rutas que en el repo activo (`npc/`, `db/`, etc.) bajo este directorio.

## Contenido

| Carpeta | Qué es |
|---------|--------|
| `npc/` | Scripts NPC no cargados por `npc/re/scripts_main.conf` + barters activos (ver `MANIFEST.txt`). Incluye `npc/pre-re/` completo. |
| `db/pre-re/` | YAML pre-renewal; no se lee con `RENEWAL`. |
| `db/import-tmpl/` | Plantillas de `db/import/` para nuevos servers. |
| `doc/` | Documentación upstream rAthena. |
| `sql-files/` | Schema SQL legacy (`use_sql_db: no` en OzRo). |

## Reactivar algo

- **NPC:** buscar en `MANIFEST.txt`, mover a `npc/...` y volver a declarar `npc:` en el conf activo.
- **DB/doc/SQL:** copiar solo el archivo o subárbol necesario; no restaurar carpetas enteras sin revisión.

Documentación del proceso: [`docs/ozro-design/18-repo-freeze-y-limpieza.md`](../docs/ozro-design/18-repo-freeze-y-limpieza.md).