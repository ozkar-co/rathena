# OzRo Server

Emulador de Ragnarok Online para el servidor privado **OzRo**: Renewal, pocos jugadores, acceso por invitación. Este repositorio es un fork operativo de [rAthena](https://github.com/rathena/rathena), no un emulador genérico para terceros.

## Qué es esto

- **Base:** rAthena Renewal (snapshot enero 2026), `PACKETVER` congelado alineado al cliente OzRo (~2021).
- **Contenido propio:** `npc/custom/ozro/`, `db/import/`, `conf/import/`.
- **Archivo:** scripts y capas que no cargamos en `trash_bin/` (ver `trash_bin/README.md`).
- **Documentación de diseño:** [`docs/ozro-design/`](docs/ozro-design/README.md).

Repos relacionados: web (`ozro-site/`), API (`ozro-backup/`), parches de cliente (`ozro-cli/`).

## Requisitos

- Linux, GCC, `make`, autotools (`./configure`)
- MariaDB/MySQL para login/char (YAML para datos de juego; `use_sql_db: no`)
- Cliente Ragnarok OzRo en LAN/VPN

## Compilar y arrancar

```bash
./configure --enable-packetver=20210703   # ajustar al PACKETVER del cliente si cambia la doc
make -j"$(nproc)" server
./athena-start start
```

Ajustes de rates, features y protocolo: `conf/import/`. NPCs custom: `npc/scripts_custom.conf`.

## Estructura útil

| Ruta | Uso |
|------|-----|
| `npc/custom/ozro/` | NPCs, warps, sistemas jugables |
| `db/import/` | Items, mobs, skills, quests custom |
| `conf/import/` | Battle, char, inter, packet |
| `docs/ozro-design/` | Decisiones y freeze |
| `tools/` | Scripts locales (inventario NPC, spawns, etc.) |
| `trash_bin/` | Contenido archivado, no cargado |

## Licencia y atribución

El código del emulador está bajo **GNU GPLv3** (`LICENSE`), heredado de rAthena y del proyecto eAthena.

- Proyecto upstream: **[rathena/rathena](https://github.com/rathena/rathena)**
- Lista de autores histórica del upstream: ver [AUTHORS](https://github.com/rathena/rathena/blob/master/AUTHORS) en GitHub

Las modificaciones y el contenido OzRo en este repo son mantenidos por el equipo OzRo; no implican afiliación con Gravity ni con la comunidad rAthena más allá del uso del emulador bajo GPLv3.