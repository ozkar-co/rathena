# Cliente: organización y pruebas sin romper lo que ya funciona

**Última revisión:** 2026-11-16
**Objetivo:** ordenar el cliente actual, separar base de custom y probar versiones sin tocar el cliente que ya funciona.  
**Decisión de fondo:** **no reconstruir el cliente desde cero ahora**. Primero alinear el server al cliente actual y congelar; recién después evaluar un cliente nuevo.

> Contexto histórico: el server estaba compilado para `20211103` y el cliente parecía ser `20210703` (string `RO Offline 20210703`, aunque el archivo base se llame `2019-06-05fRagexe_patched`). La diferencia era de ~4 meses y se podía resolver recompilando el server, sin tocar el cliente.
>
> **Actualización 2026-11-16:** el repo quedó fijado en `PACKETVER=20190605` (commit `6ea66a121`). La hipótesis `20210703` de este documento queda como referencia histórica.

---

## 1. Situación actual

### Lo que funciona

- Hay un cliente que abre, loguea y se usa en LAN.
- El contenido custom es mínimo:
  - imágenes de loading/logo,
  - 5 items activos en `db/import/item_db.yml` (35001–35005),
  - entradas e iconos en el cliente (`System/itemInfo_EN.lua`, `data/texture/.../item`, `collection`).
- El custom del cliente ya está bastante aislado en `ozro-cli/patch/`:
  - `data.ini`
  - `data/clientinfo.xml`
  - `data/etcinfo.txt`
  - `System/itemInfo_EN.lua`
  - `data/texture/...` (loading, logo, iconos custom)
  - `gefenia.grf`
  - `OzRo.exe`

### Lo que falló antes

Intentar usar una descarga limpia + `OzRo.exe` no abrió. **Ya se descartó** la explicación simple de "faltaba el overlay": se copiaron `data.ini`, `data/clientinfo.xml`, `data/etcinfo.txt`, `System/itemInfo_EN.lua`, texturas, `gefenia.grf` y dgVoodoo.

Hipótesis restantes (ninguna confirmada):

1. **La data/GRF del cliente limpio no es compatible con el exe parcheado** (versión de data, packetver o estructuras internas distintas).
2. **El exe espera una combinación específica de GRF/nombres/orden**; aunque se ajuste `data.ini`, el cliente limpio puede traer GRF con otro nombre, otro formato o cifrado distinto.
3. **El exe está parcheado para una fecha/packetver concreta**; la data del cliente limpio puede ser de otra fecha.
4. **Faltan archivos de sistema, DLLs o dependencias** que no son parte del overlay visible.
5. **El exe depende de la carpeta/registro original** o de un `clientinfo`/`data.ini` con una ruta/estructura distinta.

> Conclusión: no fue un simple archivo faltante. Es una incompatibilidad entre el exe parcheado y la base limpia. Por eso la recomendación es **no tocar el cliente actual** hasta que sea necesario.

---

## 2. Estrategia recomendada

### Opción A (recomendada): no tocar el cliente, alinear el server

1. Mantener el cliente actual congelado tal como está.
2. Compilar el server con el `PACKETVER` actual (`20190605`) y probarlo en producción (no hay entorno separado; ver sección 5).
3. Probar login, personaje, skills, NPCs y mapas con el cliente actual.
4. Si funciona: congelar el binario de producción con ese `PACKETVER`.
5. Si no funciona: ajustar el `PACKETVER` y revisar el paquete exacto. El cliente no se tocó.

Ventajas:

- riesgo bajo y reversible,
- no se repara el cliente,
- se confirma empíricamente el `PACKETVER`,
- el contenido custom queda intacto.

### Opción B (solo si A falla): cliente limpio en paralelo

1. Descargar un cliente limpio **20210406** o **20210703** (no 2022/2023 por ahora).
2. Copiarlo a una carpeta de prueba, nunca encima del cliente actual.
3. Copiar el overlay `ozro-cli/patch/` completo, no solo el exe.
4. Ajustar `data.ini` a los GRF que realmente trae la descarga limpia.
5. Probar en una carpeta separada; si abre y loguea, recién ahí evaluar el reemplazo.

No conviene pagar un cliente 20220721 o 20230404 todavía: son más nuevos que la data actual y obligan a mover más piezas del server.

---

## 3. Estructura propuesta del cliente

Separar base, overlay y pruebas:

```text
/mnt/games/OzRo/                  # cliente actual que funciona (NO tocar)
/home/oz/Code/ozro-cli/patch/     # overlay custom (fuente de verdad del custom)
/home/oz/Code/ozro-cli/dist/      # patch.zip para repartir
/mnt/games/OzRo-test/             # cliente de prueba (copias)
/mnt/games/OzRo-backup/           # backup antes de cambios
```

### Regla de oro

- **Base:** no se edita. Si hay que actualizar, se reemplaza por una copia nueva.
- **Overlay:** todo lo custom va en `ozro-cli/patch/`.
- **Pruebas:** siempre en `OzRo-test/` o similar.
- **Producción:** solo se toca cuando la prueba funciona.

### Manifiesto sugerido

Guardar en `ozro-cli/` un archivo `client-manifest.md` o `client-manifest.txt` con:

- versión/fecha del cliente base,
- hash SHA-256 del exe,
- hash de cada GRF,
- lista de archivos del overlay,
- `PACKETVER` esperado,
- comando de build del server,
- fecha del snapshot.

Ejemplo:

```bash
sha256sum /mnt/games/OzRo/OzRo.exe
sha256sum /mnt/games/OzRo/*.grf
sha256sum /mnt/games/OzRo/data.ini
```

---

## 4. Overlay actual

`ozro-cli/patch/` ya contiene:

| Ruta | Función |
|------|---------|
| `OzRo.exe` | Cliente parcheado que funciona |
| `data.ini` | Orden de GRF |
| `data/clientinfo.xml` | IP/puerto/nombre del server y pantallas de carga |
| `data/etcinfo.txt` | Config del cliente |
| `System/itemInfo_EN.lua` | Nombres/descripciones/iconos de items |
| `data/texture/.../loading*.jpg` | Pantallas de carga custom |
| `data/texture/.../t_*.bmp`, `scr_logo.bmp` | UI/logo custom |
| `data/texture/.../item/ozro_*.bmp` | Iconos de items custom |
| `data/texture/.../collection/ozro_*.bmp` | Ilustraciones de items custom |
| `gefenia.grf` | Mapa custom |

### Cosas a ordenar

1. **Duplicados:** el cliente actual tiene una copia de los assets custom en `data/custom/items/`. Eso es staging, no la fuente real. La fuente real es `ozro-cli/patch/`.
2. **Items 35010:** `System/itemInfo_EN.lua` tiene entrada para `35010` (Ozro Apple), pero `db/import/item_db.yml` **no** define el 35010. Hay que:
   - agregarlo al server, o
   - quitarlo del cliente.
3. **Icono de MVP Soul:** el cliente usa `ozro_mvp_soul`; el staging usa el sprite vanilla. Unificar criterio.
4. **`data/custom/items/itemInfo_custom.lua`** no lo carga el cliente; es solo staging. No confundirlo con `System/itemInfo_EN.lua`.

---

## 5. Plan de prueba (referencia histórica)

> **Actualización 2026-11-16:** no hay server de prueba separado. Se prueba directo en producción con los 3 jugadores, aceptando apagar o desconectar el server si algo falla. Las copias/worktrees de abajo quedan como referencia por si alguna vez se monta un entorno aparte.

### 5.1 Preparar una copia de prueba

Referencia para montar un entorno aparte (no es el flujo actual; hoy se prueba en producción). Opciones:

```bash
# Copia de trabajo del repo
cp -a /home/oz/Code/rathena /home/oz/Code/rathena-20210703
cd /home/oz/Code/rathena-20210703
```

O usar un worktree de git:

```bash
cd /home/oz/Code/rathena
git worktree add ../rathena-20210703 HEAD
```

### 5.2 Compilar

```bash
cd /home/oz/Code/rathena-20210703
./configure --enable-packetver=20210703
make -j$(nproc) server
```

> Si `make server` no es el target correcto en tu versión, usar el target habitual del server (`make -j$(nproc)`).

### 5.3 Ejecutar con DB de prueba

- Usar una base MySQL aparte (`rathena_test`) o un puerto/instancia separada.
- No apuntar el server de prueba a la DB de producción.
- Copiar `conf/` y `db/` del repo, pero cambiar `conf/import/inter_conf.txt` a la DB de prueba.

### 5.4 Smoke test mínimo

1. Login.
2. Crear personaje.
3. Entrar al mapa inicial.
4. Subir una skill (`@skillall`/`@lvup` o el flujo normal).
5. Cambiar de job (`@jobchange`) y revisar el árbol de skills.
6. Usar un NPC custom.
7. Warpear a un mapa custom (`gefenia`).
8. Revisar la consola del map-server por warnings/errores.

Si todo funciona, el cliente es compatible con 20210703. Si falla el login o las skills, probar `20190605` o investigar el paquete exacto.

### 5.5 Rollback

- En el flujo actual se prueba en producción: hacer backup de la DB y del binario antes de cada cambio.
- Si algo falla, restaurar el backup y avisar a los jugadores; el server puede apagarse sin problema.
- El cliente actual no se toca.

---

## 6. Cómo probar un cliente limpio sin romper el actual

1. Copiar el cliente limpio a `/mnt/games/OzRo-test/<version>/`.
2. Copiar `ozro-cli/patch/` encima (incluyendo `data.ini`, `data/`, `System/`, `gefenia.grf`, `OzRo.exe`).
3. Verificar que existan los GRF que pide `data.ini`:
   ```bash
   cd /mnt/games/OzRo-test/<version>
   ls -lh gefenia.grf renewal2021.grf resources2021.grf data.grf rdata.grf
   ```
4. Si falta alguno, ajustar `data.ini` a los GRF reales o copiar el GRF faltante.
5. Ejecutar `OzRo.exe` desde esa carpeta.
6. Si no abre:
   - revisar `data/clientinfo.xml`,
   - revisar `data/etcinfo.txt`,
   - revisar `System/itemInfo_EN.lua`,
   - revisar DLLs,
   - revisar que el exe sea el parcheado, no el limpio.
7. No copiar el cliente de prueba encima del cliente actual hasta que funcione.

---

## 7. Sobre descargar un cliente nuevo

| Cliente | Opinión |
|---------|---------|
| 20210406 | El más cercano a 20210703. Útil solo si el actual falla. |
| 20220721 | Más nuevo; puede requerir cambios de server/data. No ahora. |
| 20230404 | Mucho más nuevo; no conviene para congelar con la base actual. |
| Atlantis RO ep 16.1 | Puede tener `grf.bin` cifrado; no asumir que se puede extraer. |
| data/rdata 20200603 | Sirve para comparar mapas/archivos, no para reemplazar el cliente. |

**Recomendación:** no pagar un cliente nuevo todavía. El cliente actual funciona; el problema es de protocolo server/cliente y se resuelve recompilando.

---

## 8. Checklist de organización

- [ ] Backup completo de `/mnt/games/OzRo`.
- [ ] Manifiesto con hashes del exe y GRF.
- [ ] Confirmar que `ozro-cli/patch/` es la fuente de verdad del custom.
- [ ] Eliminar/aislar duplicados en `data/custom/items/`.
- [ ] Resolver el 35010 (agregar al server o quitar del cliente).
- [ ] Compilar con el `PACKETVER` actual (`20190605`) y validar en producción.
- [ ] Smoke test con el cliente actual.
- [ ] Si funciona, congelar el binario de producción.
- [ ] Si no funciona, revisar el paquete de login y ajustar `PACKETVER`.
- [ ] Documentar el resultado en `09-estado-tecnico-y-estabilidad.md`.

---

## 9. Preguntas abiertas

1. ¿El `PACKETVER` real del cliente es 20210703? Se valida en producción con el cliente actual.
2. ¿El cliente limpio 20210406 trae los GRF `renewal2021.grf`/`resources2021.grf`? Si no, hay que adaptar `data.ini`.
3. ¿El `grf.bin` de Atlantis RO se puede leer? Si está cifrado, descartarlo.
4. ¿El data/rdata 20200603 tiene mapas que el cliente actual no tiene? Comparar antes de usar.
5. ¿El 35010 se va a usar o se elimina?

---

## 10. Decisión

- **2026-11-14:** no reconstruir el cliente desde cero ahora.
- **2026-11-14:** no tocar el cliente ni comprar el 20210406 por ahora. Seguir con el cliente actual hasta que algo se rompa.
- **2026-11-14:** congelar el cliente actual; compilar con `20190605` (config actual) y validar en producción.
- **2026-11-14:** mantener el custom en `ozro-cli/patch/` y no editar la base del cliente.
- **2026-11-14:** resolver el 35010 y los duplicados antes de congelar.
- **2026-11-16:** no hay server de prueba; se valida directamente en producción con los 3 jugadores.
