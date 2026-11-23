# Recipes con éxito variable — fórmulas para calculadora web

**Estado:** Pre-E5 cerrado. El dataset marca `success_status=variable` y `success_chance=null`. Este doc es la referencia para una calculadora **manual en la web** (no se hornea % en SQL).

**Unidad:** en src, `make_per` se compara con `rnd() % 10000`.  
Éxito si `rnd()%10000 < make_per` (o si `qty > 1`).  
`make_per = 10000` ≈ 100%. Valores > 10000 siguen siendo “siempre” tras el floor `make_per < 1 → 1`.

**Fuente única de runtime:** `src/map/skill.cpp` → `skill_produce_mix` (~L21644–22024).  
Catálogo de recetas (mats / skill / familia): `db/re/produce_db.txt` (+ `db/import/produce_db.txt`).

**Rates de conf (multiplican al final del branch):**

| Conf key | Campo | Default | Uso |
|---|---|---|---|
| `weapon_produce_rate` | `battle_config.wp_rate` | 100 | Weapon forge |
| `potion_produce_rate` | `battle_config.pp_rate` | 100 | `AM_PHARMACY` / Twilight |

Declarados en `src/map/battle.cpp` (`weapon_produce_rate`, `potion_produce_rate`).

**Baby class (global, después de todos los branches):**  
si `JOBL_BABY` → `make_per = make_per * 50 / 100`.

---

## 1. Weapon forging (Blacksmith)

**Cuándo:** el resultado es equipable arma (`itemdb_isequip` + `IT_WEAPON`) y skill ≠ `GN_CHANGEMATERIAL` / `GN_MAKEBOMB`.  
Rama `else` de `equip` en `skill_produce_mix` (~L21992–22017).

**Skills típicas:** `BS_DAGGER`, `BS_SWORD`, `BS_TWOHANDSWORD`, `BS_AXE`, `BS_MACE`, `BS_KNUCKLE`, `BS_SPEAR` (familia `weapon`, `ItemLV` 1–3 en `produce_db`).

```
make_per =
    5000
  + (JOBL_THIRD ? 1400 : job_level * 20)
  + dex * 10
  + luk * 10
  + pc_checkskill(skill_id) * 500          // skill de forja usada
  + pc_checkskill(BS_WEAPONRESEARCH) * 100
  + (wlv >= 3 ? pc_checkskill(BS_ORIDEOCON) * 100 : 0)
  - (ele ? 2000 : 0)                       // piedra elemental en slot
  - star_crumbs * 1500                     // cada Star Crumb en slot
  - (wlv > 1 ? wlv * 1000 : 0)             // malus nivel de arma
  + anvil_bonus

if wp_rate != 100:
    make_per = make_per * wp_rate / 100
```

**Anvil (inventario; el primero que matchee gana):**

| Ítem | Bonus `make_per` |
|---|---|
| Emperium Anvil | +1000 |
| Golden Anvil | +500 |
| Oridecon Anvil | +300 |
| Anvil | +0 |

`wlv` = weapon level del **resultado** (`itemdb_wlv`).  
`ele` / `sc` = piedra elemental / Star Crumbs consumidos en los 3 slots de forge (antes del roll).

No hay RNG dentro de `make_per`; solo el roll final.

---

## 2. Pharmacy (Alchemist — `AM_PHARMACY`)

**Cuándo:** `skill_id` ∈ `AM_PHARMACY`, `AM_TWILIGHT1`, `AM_TWILIGHT2`, `AM_TWILIGHT3` (~L21758–21801).  
Familia `potions` (`ItemLV` 22) en `produce_db`.

```
make_per =
    pc_checkskill(AM_LEARNINGPOTION) * 50
  + pc_checkskill(AM_PHARMACY) * 300
  + job_level * 20
  + (int_ / 2) * 10
  + dex * 10
  + luk * 10
  + (homun activo && HVAN_INSTRUCT > 0 ? Instruct_lv * 100 : 0)
  + item_modifier(nameid)                  // ver tabla; incluye rnd

if pp_rate != 100:
    make_per = make_per * pp_rate / 100
```

**Modificador por producto (`nameid`) — contiene RNG:**

| Productos | Modificador |
|---|---|
| Red / Yellow / White Potion | `+(1 + rnd()%100)*10 + 2000` |
| Alcohol | `+(1 + rnd()%100)*10 + 1000` |
| Fire / Acid / Man Eater / Mini Bottle | `+(1 + rnd()%100)*10` |
| Yellow Slim Potion | `-(1 + rnd()%50)*10` |
| White Slim Potion, Coating Bottle | `-(1 + rnd()%100)*10` |
| Blue Potion, Red Slim, Anodyne, Aloevera, default | `+0` |

Para la calculadora: mostrar **rango** (min/max del término RNG) o valor esperado; no un % fijo por receta.

---

## 3. Cooking (platos — menú pharmacy/cooking)

**Cuándo:** branch `default` del `switch (skill_id)` no-equip, con  
`sd->menuskill_id == AM_PHARMACY` y `10 < menuskill_val <= 20` (~L21972–21987).  
Familia `cooking` (`ItemLV` 11–20) y parte de `cooking_extended` en `produce_db`.  
UI: `clif_cooking_list` / script `cooking` (`src/map/clif.cpp`, `src/map/script.cpp`).

```
if menuskill_val >= 15:          // Legendary Cooking Set
    make_per = 10000             // 100%
else:
    make_per =
        1200 * (menuskill_val - 10)
      + 20  * (base_level + 1)
      + 20  * (dex + 1)
      + 100 * (rnd() % R + L)     // ver cook_mastery abajo
      - 400 * (itemlv - 11 + 1)   // itemlv de produce_db
      - 10  * (100 - luk + 1)
      - 500 * (num - 1)           // num = # materiales distintos en la receta
      - 100 * (rnd()%4 + 1)       // 100..400
```

**Término `cook_mastery` (`sd->cook_mastery`):**

```
L = 6 + cook_mastery / 80
span = 30 + 5*(cook_mastery/400) - L
// rnd()%span + L   (si span inválido en runtime, edge case del src)
```

`cook_mastery` sube/baja al éxito/fallo de cocina (~L22139–22141 / ~L22294–22297); es estado del personaje, no del dataset.

---

## 4. Relacionados (misma flag `variable`, no calculadora prioritaria)

Misma política `success_status=variable` si aplica; fórmulas en el mismo `skill_produce_mix`:

| Caso | Skill / familia | Notas (~líneas) |
|---|---|---|
| Temper Iron / Steel / stones | `BS_IRON`, `BS_STEEL`, `BS_ENCHANTEDSTONE` | Base `job*20+dex*10+luk*10` + bonus por producto (~L21730–21749). Star Crumb → 100% fijo (`fixed_src`). |
| Deadly Poison | `ASC_CDP` | `2000 + 40*dex + 20*luk` (~L21751–21752) |
| Runes | `RK_RUNEMASTERY` | A+B+C+D por rank (~L21807–21845) |
| GX new poison | `GC_CREATENEWPOISON` | `3000 + 500*ResearchNewPoison`; qty RNG |

**Ya fijos en dataset (`fixed_src` / `fixed_db`):** Holy Water, Ancilla, Create Converter, Change Material (DB rate), Special Pharmacy / Mix Cooking / Bomb (éxito forzado 100%; qty variable), Machine / Bionic Pharmacy.

---

## Checklist calculadora web

1. Leer receta desde dataset (`produce_id`, mats, `require_skill_*`, `item_lv`, `recipe_family`).
2. Si `success_status != variable` → usar `success_chance` (per_10000).
3. Si `variable` → pedir inputs del jugador según familia (`weapon` / `potions` / `cooking`) y aplicar la fórmula de este doc.
4. Aplicar `wp_rate` / `pp_rate` del conf del server OzRo y baby ×0.5 si aplica.
5. Mostrar resultado como % = `min(100, make_per / 100)` (o rango si hay RNG interno).
