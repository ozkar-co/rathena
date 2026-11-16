# Arena MVP: instancia e invocador

**Estado:** `probar` — T1, T2 y T3 accesible implementados en modo solo; party y drops pendientes.

## Mapa e instancia

- Mapa: **`quiz_00`**, la vieja arena de MVPs.
- Entrada: `51,35`.
- Spawn del MVP: `81,8`.
- Regreso: `prontera,171,149`.

Configuración actual en `db/import/instance_db.yml`:

```yml
Body:
  - Id: 10001
    Name: OzRo MVP Arena
    TimeLimit: 3600
    IdleTimeOut: 300
    Enter:
      Map: quiz_00
      X: 51
      Y: 35
```

- **No usar `NoMapFlag: true`:** en esta versión de rAthena deja el vector de flags vacío y `setmapflag` puede crashear el map-server.
- La instancia copia los flags de `quiz_00`; en `OnInstanceInit` se quita `mf_noskill` y se agregan `nobranch`, `nomemo`, `noteleport`, `monster_noteleport` y un `nosave` con destino a Prontera.

## NPC invocador

- Ubicación: `prontera,173,152`.
- Modo actual: **`IM_CHAR`** (solo, sin party). La party queda para una etapa posterior.
- Flujo:
  1. Si ya hay una instancia activa, ofrece reingresar.
  2. Pregunta el costo: 3 Almas (T1) o 5 Almas (T2).
  3. Muestra la lista de MVPs de ese costo.
  4. Verifica Almas y keys, y muestra lo que falta.
  5. Crea la instancia.
  6. Descuenta Almas y keys.
  7. Guarda el MVP en `'mvp_id` con `setinstancevar`.
  8. Dispara `OnSummon` con `donpcevent`.
  9. Entra con `instance_enter`.
- Si algo falla después de crear, no hay devolución automática: el GM lo resuelve a mano.

## Spawner y salida

- NPC invisible sobre `quiz_00`, copiado a la instancia.
- `OnInstanceInit`: flags del mapa.
- `OnSummon`: lee `'mvp_id` y ejecuta `monster` en `81,8` con evento `OnMvpDead`.
- `OnMvpDead`: warpea a todos a `prontera,171,149`, inicia un timer de 1 segundo y destruye la instancia.
- Si la instancia expira por tiempo, el `nosave` la manda a Prontera.

## Costos de invocación

| Tier | Costo | Estado |
|------|------:|--------|
| T1 | 3 Almas + keys | Implementado |
| T2 | 5 Almas + keys | Implementado |
| T3 | 10 Almas + keys | Implementado (solo MVPs accesibles) |
| T4 | — | Fuera de invocación |
| T5 | — | Fuera de invocación |

- Las Almas se consumen siempre; las keys también.
- El costo en Almas es el freno principal; las keys son el segundo candado.
- T4/T5 quedan fuera por estar fuera de escala.

## Keys T1

| MVP | Almas | Keys |
|---|---:|---|
| Golden Thief Bug | 3 | 1 Gold (969) |
| Phreeoni | 3 | 10 Tongue (1015) + 5 Ant Jaw (1014) |
| Moonlight Flower | 3 | 20 Nine Tails (1022) |
| Dracula | 3 | 1 3carat Diamond (732) + 100 Wing of Red Bat (7006) |
| Lady Tanee | 3 | 1 Banana Hat (5116) |
| Orc Hero | 3 | 2 Orc Warlord Token (25508) |
| Mistress | 3 | 30 Royal Jelly (526) |
| Maya | 3 | 30 Round Shell (1096) |
| Doppelganger | 3 | 1 Lance (1411) + 2 Broad Sword (1162) |
| Orc Lord | 3 | 1 Heroic Emblem (968) |

## Keys T2

| MVP | Almas | Keys |
|---|---:|---|
| Stormy Knight | 5 | 5 Old Blue Box (603) |
| Baphomet | 5 | 2 Evil Horn (923) |
| White Lady | 5 | 2 White Snake's Tear (25622) + 2 Black Hair (1020) |
| Drake | 5 | 1 Pirate Bandana (2287) + 10 Skel-Bone (932) |
| Pharaoh | 5 | 2 Broken Pharaoh Emblem (7113) + 1 Masque of Tutankhamen (7114) |
| Eddga | 5 | 5 Tiger Skin (1029) + 2 Tiger's Footskin (1030) |
| RSX-0806 | 5 | 2 Flashlight (7327) + 2 Cogwheel (7093) |
| Amon Ra | 5 | 3 Fragment of Rossata Stone (7211) |
| Evil Snake Lord | 5 | 3 Ba Gua (7169) |
| Osiris | 5 | 10 Rotten Bandage (930) + 1 Memento (934) + 10 Scale Shell (936) |
| Dark Lord | 5 | 10 Skull (7005) + 1 Coif (5093) |
| Tao Gunka | 5 | 1 Gemstone (7300) + 3 Stone Fragment (7067) |
| Hatii | 5 | 2 Fang of Hatii (7036) |
| Boitata | 5 | 1 Treasure Box (7444) + 10 Sharp Scale (963) |
| Turtle General | 5 | 10 Broken Shell (7070) |
| Atroce | 5 | 5 Bloody Rune (7563) |

### T2 excluidos de la invocación

- **Samurai Specter:** Amatsu Dungeon requiere quest y Transit Permit.
- **Leak:** Krakatau/Dewata requiere `dew_legend >= 8`.
- **Gopinich:** el acceso a los campos de Moscovia requiere quest.

## Keys T3

Solo los T3 accesibles sin guild dungeon, nightmare ni quest de acceso:

| MVP | Almas | Keys |
|---|---:|---|
| Scaraba Queen | 10 | 10 Queen Wing Piece (6326) |
| Kiel D-01 | 10 | 5 Pocket Watch (7513) |
| Kraken | 10 | 10 Tentacle (962) + 1 Treasure Box (7444) |

### T3 excluidos de la invocación

- **The Last One** y **King of the Alley**: retirados por diseño.
- **Guild dungeon:** Angry Student Pyuriel, General Daehyun, Dark Guardian Kades y Gioia.
- **Nightmare:** Amon Ra (Nightmare) y Nightmare Baphomet.
- **Quest o instancia de acceso:** Wounded Morocc (quest/evento), Gloom Under Night (Rachel Sanctuary), Vesper (Juperos), Egnigem Cenia (Lab Passport) y Venomous Chimera (Werner Lab).
- Si en el futuro se desbloquean esos accesos, se pueden reevaluar.

## Tracker

- `npc/custom/ozro/mvp_tracker.txt` ignora kills dentro de instancias para `IM_CHAR`, `IM_PARTY`, `IM_GUILD` e `IM_CLAN`.
- Las kills de MVPs invocados no generan Almas ni asistencias.
- Las instancias oficiales también quedan fuera del Tracker por ahora.

## Drops del MVP invocado

- En la prueba actual el MVP puede soltar su loot normal y su drop MVP.
- Queda pendiente decidir si se mantiene, se reduce o se desactiva.
- Si el MVP invocado suelta sus propias keys, el costo en Almas sigue frenando el loop.

## Pendientes

- Pasar de `IM_CHAR` a party (`IM_PARTY`) y definir quién paga.
- Reevaluar T3 si se desbloquean más accesos; T4/T5 siguen fuera.
- Definir drops de MVPs invocados.
- Definir devoluciones, cooldown y límites de invocación.
- Cargar en el vendedor viajero las keys de lujo: Pirate Bandana, Memento, etc. Ver [15-vendedor-viajero.md](./15-vendedor-viajero.md).

## Pruebas

1. Crear una instancia T1, T2 y T3, pagar Almas + keys y verificar que se descuenten.
2. Verificar que el MVP elegido aparezca una sola vez.
3. Matar el MVP: warp a Prontera, timer de 1 segundo y destroy.
4. Dejar que expire el timer de 1 hora: warp y destroy.
5. Reingresar a una instancia activa sin pagar de nuevo.
6. Confirmar que la kill no suma Almas ni Tracker.
7. Reiniciar el server: las Almas y el Tracker quedan; la instancia se pierde.
