# Estado técnico y estabilidad

**Última revisión:** 2026-11-14  
**Objetivo:** dejar registrada la investigación técnica previa al congelamiento de una base estable.  
**Alcance:** revisión del repo rAthena, del cliente actual y del contenido que el cliente puede o no soportar.  
**Estado:** investigación terminada; no se modificó el servidor en esta revisión.

> **Meta:** congelar el server en rAthena de enero 2026 + el cliente actual, quitar/ajustar lo que el cliente no tenga, y recién después balancear skills, mobs, mapas, traducir y agregar contenido custom.

---

## Resumen ejecutivo

1. **El server no es Episode 14.3.** El `02-configuracion-servidor.md` dice 14.3, pero la base real es rAthena master de enero 2026. `conf/maps_athena.conf` incluye mapas hasta Episode 21 y la DB tiene jobs/skills 4th de 2024/2025.
2. **El repo estaba limpio y sincronizado al momento de la revisión.** `HEAD = 8e436db5e`, base upstream `934896a00` (Atemo, 2026-01-15) + 100 commits custom. `git status` limpio, `master == origin/master`, sin stash ni untracked. Después de esta revisión solo se agregó este documento y su entrada en el índice.
3. **La versión del cliente es la duda principal.** El ejecutable activo está basado en `2019-06-05fRagexe_patched`, pero el binario contiene el string `RO Offline 20210703`. Lo más probable es que el cliente efectivo sea **20210703**, no 2019-06-05. Hay que confirmarlo antes de compilar el server.
4. **El `PACKETVER` configurado en el repo es 20211103.** Si el cliente es 20210703, hay ~4 meses de diferencia de protocolo. No es lo mismo que el caso 2019, pero conviene alinear el server exactamente al cliente.
5. **La data de skills está alineada.** El árbol de skills del cliente y `db/re/skill_tree.yml` no tienen diferencias de MaxLevel para skills de jugador. Solo aparece el nombre `BA_FROSTJOKE` en el cliente vs `BA_FROSTJOKER` en el server, pero es el mismo ID (318).
6. **El riesgo grande está en mapas/contenido nuevo.** Según los GRF del cliente actual, **372 mapas** de `conf/maps_athena.conf` no están en el cliente y **106** de esos mapas están referenciados por scripts habilitados. Si el cliente no los tiene, entrar o warpear ahí puede romper.
7. **No se pudo compilar ni ejecutar el server en este entorno.** No hay gcc/make ni binarios en el repo. La validación final hay que hacerla en el server de producción.

---

## 1. Repositorio y revisión

### Datos duros

| Dato | Valor |
|------|-------|
| Rama | `master` |
| HEAD | `8e436db5e` — `feat(tools): añadir scripts de inventario y sprites de NPC` |
| Base upstream | `934896a00` — Atemo, 2026-01-15 — `Split up Assassin skills (#9741)` |
| Commits custom sobre la base | 100 |
| Archivos cambiados por lo custom | 137 archivos, ~152k inserciones |
| Estado del working tree al inicio | limpio |
| Sincronización | `master == origin/master` |
| Stash / untracked / ignorados | ninguno |

### Cómo verificar en el server de producción

```bash
cd /ruta/al/rathena
git rev-parse HEAD
git status -sb
git log --oneline -5
git stash list
git rev-list --left-right --count origin/master...master
```

Si el server de producción muestra cambios locales que no están en este clon, esos cambios no están cubiertos por esta investigación.

---

## 2. Cliente

### Ejecutables encontrados

En `/mnt/games/OzRo`:

| Archivo | Tamaño | Evidencia de versión |
|---------|--------|----------------------|
| `OzRo.exe` | ~9.2 MB | Copia parcheada del cliente activo. Contiene `RO Offline 20210703`. |
| `2019-06-05fRagexe_patched.exe` | ~8.8 MB | Nombre base del cliente. Contiene `RO Offline 20210703`. |
| `RagexeRE.exe` | ~12 MB | PDB con fecha 2020-12-29. |
| `Ragexe.exe` | ~7.4 MB | PDB `2021-12-16`. |
| `Ragnarok.exe`, `Ragnarok_RE.exe`, etc. | varios | Lanzadores/parcheadores, no son el cliente activo. |

### Interpretación

- El **nombre del archivo base** es `2019-06-05fRagexe_patched.exe`, pero el string interno del ejecutable dice **`RO Offline 20210703`**.
- El nombre del archivo no es prueba suficiente del `PACKETVER`; puede ser el nombre del binario base que se parcheó/reempaquetó.
- La data del cliente es de 2021: existen `renewal2021.grf` y `resources2021.grf`, y el `SkillTreeView` incluye jobs 4th (`JT_DRAGON_KNIGHT`, `JT_IMPERIAL_GUARD`, `JT_CARDINAL`, etc.).
- Conclusión provisional: **el cliente efectivo parece ser 20210703**. Confirmarlo antes de recompilar.

### GRF del cliente

`data.ini` carga:

```ini
[Data]
1=gefenia.grf
2=renewal2021.grf
3=resources2021.grf
4=data.grf
5=rdata.grf
```

Tamaños aproximados:

| GRF | Tamaño |
|-----|--------|
| `data.grf` | ~3.1 GB |
| `rdata.grf` | ~293 MB |
| `resources2021.grf` | ~66 MB |
| `renewal2021.grf` | ~7.1 MB |
| `gefenia.grf` | ~4.4 MB |

### Cómo confirmar el PACKETVER del cliente

No hay un atcommand in-game que muestre el `PACKETVER`. Opciones:

1. **Empírica:** compilar el server con `--enable-packetver=20210703` y probar login, creación de personaje, skills y NPCs. Si todo funciona estable, esa es la versión.
2. **Captura de paquetes:** usar un login server mínimo o un sniffer para ver el primer paquete `CA_LOGIN` y comparar su header con las tablas de rAthena.
3. **Comparar con clientes conocidos:** `Ragexe.exe` tiene PDB `2021-12-16` y `RagexeRE.exe` PDB `2020-12-29`; sirven como referencia, pero no son el cliente activo.
4. **Título/ventana del cliente:** si el cliente muestra `RO Offline 20210703` en el título o pantalla de parche, es una pista fuerte, no una prueba definitiva.

> **Importante:** el `@version` del juego muestra el hash/rev del **server**, no el `PACKETVER` del cliente.

---

## 3. Servidor

### Configuración actual del repo

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| `PACKETVER` por defecto | `20211103` | `src/config/packets.hpp:16` |
| Build Docker | `--enable-packetver=20211103` | `tools/docker/docker-compose.yml:34` |
| Renewal | activo | `src/config/renewal.hpp` |
| `MAX_LEVEL` del código | 275 | `src/map/map.hpp:78` |
| `max_lv` de client.conf | 99 | `conf/battle/client.conf:49` |
| `display_version` | `no` | `conf/import/battle_conf.txt:14` |

`max_lv: 99` en `client.conf` es el máximo de nivel que se manda en paquetes de unidad/aura, **no** el nivel máximo real del servidor. El máximo real del código es `MAX_LEVEL = 275`; los `job_stats` no parecen limitarlo a 175. El doc viejo dice 175/60, pero eso no está aplicado como override.

### Contenido real

- `conf/maps_athena.conf` incluye secciones de **Episode 18, 19, 20 y 21**.
- `npc/re/scripts_athena.conf` incluye contenido renewal moderno (`quests_18.txt`, instancias, etc.).
- `db/re/skill_db.yml` tiene copyright 2025 y contiene jobs/skills 4th de 2024/2025:
  - `Soul_Ascetic`, `Night_Watch`, `Hyper_Novice`, `Spirit_Handler`, `Sky_Emperor`, `Shinkiro`, `Shiranui`, entre otros.
- `db/re/skill_tree.yml`: 175 jobs, ~1142 nombres de skills en árboles.
- `db/re/skill_db.yml`: ~1635 skills con nombre.

Por lo tanto, el server es **mucho más nuevo** que un Episode 14.3 y también más nuevo que la data del cliente (2021).

### Cómo ver el `PACKETVER` del server

Al arrancar el map-server:

```text
Using packet version: 20211103
```

Código: `src/map/clif.cpp:25817`.

También:

```bash
./map-server --version
```

Eso muestra el hash/rev, no el `PACKETVER`.

---

## 4. Skills

### Método

Se extrajeron del cliente:

- `data/luafiles514/lua files/skillinfoz/skilltreeview.lub`
- `data/luafiles514/lua files/skillinfoz/skillid.lub`
- `data/luafiles514/lua files/skillinfoz/skillinfolist.lub`

Se parsearon los bytecodes Lua 5.1 y se compararon contra:

- `db/re/skill_db.yml`
- `db/re/skill_tree.yml`
- `db/import/skill_db.yml`
- `db/import/skill_tree.yml`

### Resultados

| Comparación | Resultado |
|-------------|-----------|
| Skills del árbol del cliente sin equivalente en DB del server | Solo `BA_FROSTJOKE` (mismo ID 318 que `BA_FROSTJOKER`) |
| Skills del árbol del cliente sin equivalente en el árbol del server | Solo `BA_FROSTJOKE` |
| Diferencias de MaxLevel en skills de jugador por job | 0 |
| Diferencias de MaxLevel en `skill_db.yml` | 41, casi todas de NPC/guild/mobs, no del árbol de jugador |
| `db/import/skill_tree.yml` | vacío (solo header) |
| `db/import/skill_db.yml` | solo agrega `AM_CALLHOMUN` |

### Interpretación

- **La data de skills no parece ser la causa de los problemas viejos.** El árbol del cliente y el del server están alineados para jobs de jugador.
- La diferencia `BA_FROSTJOKE` / `BA_FROSTJOKER` es solo de nombre; el ID es el mismo, y el cliente manda el ID.
- Las 41 diferencias de MaxLevel son en skills NPC, de guild o de mobs; no afectan el leveling normal de un jugador.
- El problema viejo de "skills que no subían" era más probablemente de **Hercules/cliente** o de un desajuste de protocolo, no de `skill_tree.yml` en este repo.

### Nota sobre el formato de skill list

El formato de `ZC_SKILLINFO_LIST` cambia en:

```c
#if PACKETVER_RE_NUM >= 20190807 || PACKETVER_ZERO_NUM >= 20190918
```

Código: `src/map/clif.cpp:5729`.

Si el cliente fuera **2019-06-05**, el server 20211103 mandaría el formato nuevo y el cliente esperaría el viejo. Pero si el cliente es **20210703**, ambos usan el formato nuevo y ese problema concreto no aplica. Por eso es clave confirmar el `PACKETVER` real antes de sacar conclusiones.

---

## 5. Mapas y contenido

### Comparación de mapas

Se listaron los `.gat` de todos los GRF del cliente y se compararon contra los `map:` de `conf/maps_athena.conf`.

| Dato | Valor |
|------|-------|
| Mapas en el server | 1265 |
| Mapas en los GRF del cliente | 912 |
| Mapas del server que no aparecen en el cliente | 372 |
| Mapas server-only referenciados por scripts habilitados | 106 |

### Mapas server-only referenciados por scripts

Entre los 106 hay mapas viejos de PvP/eventos y mapas de contenido nuevo. Ejemplos:

- `new_1-1` … `new_5-4` (novice academy)
- `force_*` (arenas)
- `pvp_n_*`, `pvp_y_*`
- `job3_arch03`, `job3_rune03`, `job3_war02`
- `airplane_01`
- `1@ep21a`, `1@ep21b`, `1@ep21c`
- `ch1_*`, `jor_*`
- `que_qaru*`, `que_qsch*`
- `turbo_*`

> **Cuidado:** esta comparación es una señal de riesgo, no una prueba absoluta. Puede haber falsos positivos si el cliente carga mapas desde otra fuente, si el GRF usa nombres no estándar o si el cliente los descarga en runtime. Verificar en juego antes de borrar nada.

### Contenido posterior al cliente

El server incluye Episode 18-21 y contenido de 2024/2025. El cliente es de 2021. Si el cliente no tiene esos mapas/NPCs/instancias, hay que:

- quitarlos de `conf/maps_athena.conf`, o
- deshabilitar los scripts que los usan, o
- actualizar el cliente (lo que se quiere evitar).

---

## 6. Configuración y DB

### `conf/import/battle_conf.txt`

Es la fuente de verdad de rates y ajustes. Puntos relevantes:

- `display_version: no` → el server no manda el mensaje de versión al loguear.
- `item_auto_get: yes` → el doc viejo dice `no`; el import manda.
- rates custom: base/job 5x, MVP 10x, quest 3x, drops custom.
- `feature.achievement: off`, `feature.attendance: off`, `feature.equipswitch: off`.
- `pincode_enabled: no` en `conf/import/char_conf.txt`.

### `db/import`

- `skill_tree.yml`: vacío.
- `skill_db.yml`: solo `AM_CALLHOMUN`.
- Hay muchos otros imports custom (`item_db.yml`, `mob_db.yml`, `quest_db.yml`, `stylist.yml`, etc.). No se auditó cada uno en esta revisión.

### Documentación desactualizada

`docs/ozro-design/02-configuracion-servidor.md` dice:

- Episodio 14.3 → **incorrecto** para el server actual.
- Nivel máximo 175/60 → el código tiene `MAX_LEVEL 275`; no hay override visible a 175.
- `item_auto_get: no` → el import dice `yes`.
- "Ocultar versión servidor: yes" → consistente con `display_version: no`, pero el doc no aclara que el `@version` sí existe.

No se modificó ese doc en esta revisión; queda anotado para actualizarlo cuando se congele la base.

---

## 7. Riesgos para el congelamiento

| Riesgo | Impacto | Evidencia |
|--------|---------|-----------|
| `PACKETVER` del server no coincide con el cliente | Paquetes mal parseados: skills, UI, login, items | Repo compila 20211103; cliente probable 20210703 |
| Mapas del server ausentes en el cliente | Crash/desconexión al entrar o warpear | 372 server-only, 106 referenciados |
| Contenido Episode 18-21 en un cliente 2021 | NPCs/instancias/mapas rotos | `maps_athena.conf`, `npc/re/scripts_athena.conf` |
| Jobs/skills 4th de 2024/2025 en cliente 2021 | Skills no visibles o con comportamiento raro | `db/re/skill_db.yml`, `skill_tree.yml` |
| Cliente base 2019-06-05 vs data 2021 | Funciones que el exe no soporta | Nombre del exe vs `renewal2021.grf` |
| No se pudo compilar/probar acá | No hay validación real del binario | Sin gcc/make ni binarios en el repo |

---

## 8. Plan de congelamiento propuesto

### Fase 0 — Confirmar la versión

1. Confirmar el `PACKETVER` real del cliente (20210703 es la hipótesis principal).
2. Anotar:
   - hash del exe,
   - nombre y hash de los GRF,
   - fecha/versión del cliente,
   - `PACKETVER` elegido.

### Fase 1 — Fijar la base

1. Crear una rama/tag de congelamiento, por ejemplo:
   ```bash
   git tag ozro-freeze-2026-11
   git push origin ozro-freeze-2026-11
   ```
2. Registrar en este doc:
   - commit exacto,
   - comando de build,
   - `PACKETVER`,
   - salida de `./map-server --version`,
   - salida del startup `Using packet version`.
3. Guardar una copia del binario compilado y de la config del server.

### Fase 2 — Alinear el protocolo

1. Recompilar con el `PACKETVER` del cliente:
   ```bash
   ./configure --enable-packetver=20210703
   make -j$(nproc) server
   ```
   (Ajustar el número si la confirmación da otro.)
2. Probar login, creación de personaje, entrada al mapa, skills y NPCs.
3. Revisar el startup del map-server por warnings de features deshabilitadas por `PACKETVER`.

### Fase 3 — Recortar contenido no soportado

1. Listar los mapas que el cliente no tiene y que los scripts usan.
2. Decidir por mapa:
   - quitar de `conf/maps_athena.conf`, y
   - deshabilitar el NPC/instancia/warp que lo usa, o
   - mantenerlo solo si el cliente lo tiene.
3. Deshabilitar contenido Episode 18-21 y cualquier instancia/NPC que use mapas ausentes.
4. Revisar jobs 4th:
   - si el cliente los soporta, limitar skills a las que el cliente conoce;
   - si no, bloquear el cambio de job y quitar el contenido relacionado.
5. Revisar `db/import` y `npc/custom` por scripts que referencien mapas ausentes.

### Fase 4 — Smoke test

Probar en orden:

1. Login y creación de personaje.
2. Todos los jobs disponibles.
3. Skills: subir niveles, resetear, cambiar de job.
4. Todos los NPCs custom activos.
5. Todos los warps y mapas habilitados.
6. Instancias habilitadas.
7. Rates/EXP/drops.
8. Guardar/cargar personaje, party, storage, mail, etc.

### Fase 5 — Snapshot

1. Dump SQL completo.
2. Backup de `conf/`, `db/import/`, `npc/custom/`.
3. Backup del binario y de los GRF del cliente.
4. Anotar en este doc la fecha y el commit del snapshot.

---

## 9. Checklist de verificación

### En el server

```bash
./map-server --version
./map-server --run-once
```

- Revisar `Using packet version:`.
- Revisar warnings/errores de carga de scripts, mapas, DB y features.
- Revisar que no haya `Unknown map` ni `NPC not found`.

### In-game (GM)

- `@version` → hash/rev del server (no packetver).
- Activar `display_version: yes` en `conf/import/battle_conf.txt` si se quiere ver el hash al loguear.
- Probar skills con los atcommands de test disponibles (`@jobchange`, `@skillall`, `@lvup`, etc.).
- Warpear a los mapas dudosos y ver si el cliente carga.
- Probar NPCs y warps que usen mapas server-only.
- Revisar el chat/consola por errores del cliente.

### GRF

Listar mapas del cliente:

```bash
cd /home/oz/Code/ozro-cli
python3 tools/grf.py list /mnt/games/OzRo/data.grf --filter .gat --limit 1000000
python3 tools/grf.py list /mnt/games/OzRo/rdata.grf --filter .gat --limit 1000000
```

Extraer un archivo puntual:

```bash
python3 tools/grf.py extract /mnt/games/OzRo/rdata.grf \
  "data/luafiles514/lua files/skillinfoz/skilltreeview.lub" \
  --out /tmp/skilltreeview.lub
```

### Comparación de mapas (repetible)

```bash
# Mapas del server
python3 -c "import re; [print(m.group(1)) for l in open('conf/maps_athena.conf',errors='replace') for m in [re.match(r'^map:\s*(\S+)', l)] if m]" | sort -u > /tmp/server_maps.txt

# Mapas del cliente (repetir por cada GRF y unir)
python3 tools/grf.py list /mnt/games/OzRo/data.grf --filter .gat --limit 1000000 2>/dev/null \
  | python3 -c "import sys,re; [print(m.group(1)) for l in sys.stdin for m in [re.search(r'data[/\\\\](.+)\.gat\s*$', l)] if m]" \
  | sort -u > /tmp/client_maps.txt

comm -23 /tmp/server_maps.txt /tmp/client_maps.txt
```

---

## 10. Datos de la investigación

### Diferencias de MaxLevel cliente vs `db/re/skill_db.yml`

Son 41; la mayoría son skills de NPC/guild/mobs. Se listan para referencia:

| Skill | Cliente | Server |
|-------|---------|--------|
| `NPC_IMMUNE_PROPERTY` | 5 | 10 |
| `NPC_DEFENDER` | 5 | 1 |
| `NPC_ICEMINE` | 5 | 10 |
| `WS_CREATECOIN` | 3 | 1 |
| `WS_CREATENUGGET` | 3 | 1 |
| `WS_SYSTEMCREATE` | 1 | 5 |
| `CR_ALCHEMY` | 0 | 1 |
| `CR_SYNTHESISPOTION` | 0 | 1 |
| `PF_FOGWALL` | 1 | 5 |
| `NPC_STONESKIN` | 10 | 5 |
| `NPC_ANTIMAGIC` | 10 | 5 |
| `NPC_HELLPOWER` | 1 | 5 |
| `GM_SANDMAN` | 1 | 10 |
| `ALL_PARTYFLEE` | 10 | 1 |
| `ALL_ANGEL_PROTECT` | 1 | 9 |
| `ALL_DREAM_SUMMERNIGHT` | 1 | 9 |
| `ALL_BUYING_STORE` | 2 | 1 |
| `GD_GLORYGUILD` | 0 | 1 |
| `GD_LEADERSHIP` | 5 | 1 |
| `GD_SOULCOLD` | 5 | 1 |
| `GD_HAWKEYES` | 5 | 1 |
| `GD_GLORYWOUNDS` | 5 | 1 |
| `GD_GUARDUP` | 3 | 1 |
| `EL_COOLER` | 0 | 1 |
| `SA_MONOCELL` | 10 | 1 |
| `SA_CLASSCHANGE` | 10 | 1 |
| `SA_SUMMONMONSTER` | 10 | 1 |
| `SA_REVERSEORCISH` | 10 | 1 |
| `SA_DEATH` | 10 | 1 |
| `SA_FORTUNE` | 10 | 1 |
| `SA_TAMINGMONSTER` | 10 | 1 |
| `SA_QUESTION` | 10 | 1 |
| `SA_GRAVITY` | 10 | 1 |
| `SA_LEVELUP` | 10 | 1 |
| `SA_INSTANTDEATH` | 10 | 1 |
| `SA_FULLRECOVERY` | 10 | 1 |
| `SA_COMA` | 10 | 1 |
| `NPC_MAGICMIRROR` | 10 | 5 |
| `RL_FALLEN_ANGEL` | 1 | 5 |
| `SJ_FALLINGSTAR_ATK2` | 1 | 10 |
| `SJ_FALLINGSTAR_ATK` | 1 | 10 |

> Estas diferencias están en `skill_db.yml`; el `skill_tree.yml` del job correspondiente puede sobrescribir el MaxLevel. En la comparación por job, las skills de jugador coincidieron.

### Nombres de skills del cliente sin match exacto

- `BA_FROSTJOKE` (cliente) vs `BA_FROSTJOKER` (server) — mismo ID 318.

---

## 11. Preguntas abiertas

1. ¿El `PACKETVER` real del cliente es 20210703? Confirmarlo con prueba empírica o captura de paquetes.
2. ¿El exe activo soporta jobs 4th? La data los incluye, pero el exe base es dudoso.
3. ¿Los 372 mapas server-only son realmente faltantes, o el cliente los carga desde otra fuente? Verificar en juego.
4. ¿El `grf.bin` de Atlantis RO (ep 16.1) se puede leer? Si está cifrado, no sirve como fuente de archivos.
5. ¿El data/rdata 20200603 tiene mapas que el cliente actual no tiene? Comparar antes de usarlo.
6. ¿Qué atcommands de test están habilitados en el server actual?

---

## 12. Decisiones

- **2026-11-14:** congelar la base en rAthena de enero 2026 + cliente actual; no cambiar el cliente por ahora.
- **2026-11-14:** antes de balancear/traducir/crear contenido, alinear `PACKETVER` y recortar contenido que el cliente no soporte.
- **2026-11-14:** la investigación se guarda en este documento; no se modificó el server.
