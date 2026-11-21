# OzRo — Inventario de assets activos del cliente

Generado: 2026-11-20 22:52 UTC

Complementario a `master_dataset.md` (no lo reemplaza ni se integra). Inventario de lo que **existe** en el cliente activo para validación previa server↔client.

**Machine-readable:** `python3 ozro-cli/tools/export_client_inventory.py` → `ozro-data/reports/client_*.jsonl` + `client_grf_index_meta.json`.

Reglas: `data.ini` (clave menor gana). Conteos = archivo ganador tras override. Rangos cuando el stem es numérico o `prefijo+N`. Iconos/collection/cardbmp usan `ResourceName` (no item ID).

## Fuentes

| Pri | GRF | Path | Entradas |
|---:|---|---|---:|
| 1 | `ozro_fix` | `patch/ozro_fix.grf` | 10 |
| 2 | `ozro` | `patch/ozro.grf` | 92 |
| 3 | `gefenia` | `patch/gefenia.grf` | 12 |
| 4 | `renewal2021` | `tmp/renewal2021.grf` | 1464 |
| 5 | `resources2021` | `tmp/resources2021.grf` | 29607 |
| 6 | `rdata` | `tmp/rdata.grf` | 24740 |
| 7 | `data` | `tmp/data.grf` | 150686 |

- Paths únicos (unión): **160791**
- Paths en ≥2 GRFs: **45581**
- `tmp/gefenia.grf` = copia de patch; no se cuenta aparte.

## Overrides globales

- resources2021 ≻ data: **23554**
- rdata ≻ data: **21254**
- renewal2021 ≻ data: **707**
- resources2021 ≻ rdata: **180**
- renewal2021 ≻ rdata: **46**
- ozro ≻ data: **38**
- ozro ≻ rdata: **20**
- gefenia ≻ data: **12**
- ozro ≻ renewal2021: **6**
- ozro_fix ≻ data: **3**

## Items — iconos (`…/item/*`)

- **Archivos:** 8600
- **Por GRF ganador:** resources2021=6216, data=2134, rdata=239, ozro=11
- **Duplicados entre GRFs:** 5419
  - resources2021≻data=5181; rdata≻data=238; resources2021≻rdata=25
- **Rutas:** 2

- `data/texture/유저인터페이스/item/` — **8591** (.bmp×8588, .tga×1, .db×1, .scc×1)
  - Series: `wolf_orb_skill_*`×51[1–51]; `로또*`×45[1–45]; `펫알스크롤상자*`×11[1–11]; `힘요리*`×10[1–10]; `어질요리*`×10[1–10]; `costama_egg*`×10[53, 61, 63, 65, 68–70, 80, 85–86]; `덱요리*`×10[1–10]; `럭요리*`×10[1–10]; `바탈요리*`×10[1–10]; `인트요리*`×10[1–10]; `퀴즈참가권*`×5[1–5]; `번호상자*`×5[1–5]; `선물상자_*`×5[1–5]; `슬러그탄_*`×5[1–5]; `md_airboat_boots*`×5[2–6]; +64 series
  - Nombres no-ID: **8174** (`10식안경` … `힙색`)
- `data/texture/item/` — **9** (.bmp×9)
  - Nombres: `bearballoon`, `c_drops_muffler`, `c_fairy_long_cb`, `c_long_ribbon`, `c_school_bag_bu`, `기계깃털헤어밴드`, `다람쥐귀모자`, `이사벨라브라운귀모자`, `황금날개`

## Items/Cards — collection (`…/collection/*`)

- **Archivos:** 7219
- **Por GRF ganador:** resources2021=5164, data=1975, rdata=70, ozro=10
- **Duplicados entre GRFs:** 4240
  - resources2021≻data=4170; rdata≻data=70; resources2021≻rdata=25
- **Rutas:** 2

- `data/texture/유저인터페이스/collection/` — **7211** (.bmp×7208, .db×1, .egg×1, .zip×1)
  - Series: `wolf_orb_skill_*`×51[1–51]; `로또*`×45[1–45]; `펫알스크롤상자*`×11[1–11]; `costama_egg*`×10[53, 61, 63, 65, 68–70, 80, 85–86]; `덱요리*`×10[1–10]; `럭요리*`×10[1–10]; `바탈요리*`×10[1–10]; `어질요리*`×10[1–10]; `인트요리*`×10[1–10]; `힘요리*`×10[1–10]; `퀴즈참가권*`×5[1–5]; `번호상자*`×5[1–5]; `선물상자_*`×5[1–5]; `슬러그탄_*`×5[1–5]; `생쥐모자*`×5[1–5]; +62 series
  - Nombres no-ID: **6800** (`100레벨이상낙원단아이템일러스트` … `힙색`)
- `data/texture/collection/` — **8** (.bmp×8)
  - Nombres: `c_drops_muffler`, `c_fairy_long_cb`, `c_long_ribbon`, `c_school_bag_bu`, `기계깃털헤어밴드`, `다람쥐귀모자`, `이사벨라브라운귀모자`, `황금날개`

## Cards — cardbmp

- **Archivos:** 984
- **Por GRF ganador:** data=984
- **Duplicados entre GRFs:** 0
- **Rutas:** 1

- `data/texture/유저인터페이스/cardbmp/` — **984** (.bmp×984)
  - Series: `밝히리카드*`×5[1–5]
  - Nombres no-ID: **979** (`agnes_card` … `힐윈드카드`)

## Illustrations (`…/illust*`)

- **Archivos:** 1356
- **Por GRF ganador:** data=1342, renewal2021=13, rdata=1
- **Duplicados entre GRFs:** 12
  - renewal2021≻data=11; rdata≻data=1
- **Rutas:** 3

- `data/texture/유저인터페이스/illust/` — **1236** (.bmp×1125, .png×111)
  - IDs: 5 ids · span 1–5 · 1 rangos → 1–5
  - Series: `hair_m_*`×29[1–29]; `hair_f_*`×29[1–29]; `ep16_spica_nerius*`×8[1–8]; `bu_oliver*`×14[0–7, 81–86]; `lhz_ryo*`×14[1–14]; `ep16_evil*`×6[101–103, 201–203]; `ep172_nillem*`×6[1–6]; `lhz_kaz*`×11[1–11]; `ep162_rds*`×5[1–5]; `ep14_etran*`×9[0–8]; `v_seryu*`×10[1–10]; `ep16_skia_shadow*`×5[1–5]; `ep172_barmund_b*`×5[1–5]; `wish_maiden*`×9[11–13, 21–23, 31–33]; `kafra_*`×9[1–9]; +146 series
  - Nombres no-ID: **371** (`09_moon_evt` … `펫_헌터플라이`)
- `data/texture/userinterface/illust/` — **106** (.bmp×106)
  - Series: `pet_goblin_*`×3[1–2, 4]
  - Nombres no-ID: **103** (`alicel` … `펫_leaf_cat`)
- `data/유저인터페이스/illust/` — **14** (.bmp×14)
  - Series: `soul_van*`×4[1–4]; `se_sun*`×3[1–3]; `se_moon*`×3[1–3]
  - Nombres: `se_star02_1`, `se_star02_2`, `se_star1`, `se_star3`

## Items — sprites (`data/sprite/아이템`)

- **Archivos:** 17056
- **Por GRF ganador:** resources2021=12165, data=4401, rdata=480, ozro=10
- **Duplicados entre GRFs:** 10637
  - resources2021≻data=10159; rdata≻data=478; resources2021≻rdata=50
- **Assets sprite (stems):** 8531 · spr+act=8518 · solo.spr=5 · solo.act=8 · otros=7
- **Rutas:** 2

- `data/sprite/아이템/` — **17054** (.act×8525, .spr×8522, .bmp×5, .log×1, .db×1)
  - Series: `wolf_orb_skill_*`×51[1–51]; `로또*`×45[1–45]; `펫알스크롤상자*`×11[1–11]; `costama_egg*`×10[53, 61, 63, 65, 68–70, 80, 85–86]; `덱요리*`×10[1–10]; `럭요리*`×10[1–10]; `힘요리*`×10[1–10]; `바탈요리*`×10[1–10]; `인트요리*`×10[1–10]; `어질요리*`×10[1–10]; `번호상자*`×5[1–5]; `퀴즈참가권*`×5[1–5]; `선물상자_*`×5[1–5]; `슬러그탄_*`×5[1–5]; `md_airboat_boots*`×5[2–6]; +64 series
  - Nombres no-ID: **16220** (`10식안경` … `힙색`)
- `data/sprite/아이템/몸통/여/` — **2** (.act×1, .spr×1)
  - Nombres: `길로틴크로스_여`, `길로틴크로스_여`

## Accessories — sprites (`data/sprite/악세사리`)

- **Archivos:** 7548 · GRF: resources2021=6062, data=1462, rdata=24
- **Duplicados:** 4068 · resources2021≻data=4044; resources2021≻rdata=80; rdata≻data=24
- **Stems:** 3716 · spr+act=3714
- `data/sprite/악세사리/여/` — 3727 files · 1864 stems
- `data/sprite/악세사리/남/` — 3707 files · 1853 stems
- `data/sprite/악세사리/남_doram/` — 58 files · 29 stems
- `data/sprite/악세사리/여_doram/` — 56 files · 28 stems

## Shields — sprites (`data/sprite/방패`)

- **Archivos:** 2140 · GRF: data=1772, rdata=366, ozro_fix=2
- **Duplicados:** 366 · rdata≻data=366
- **Por job (79):** `abyss_chaser`=18, `arch_mage`=16, `biolo`=18, `cardinal`=18, `dragon_knight`=22, `elemetal_master`=16, `hyper_novice`=16, `imperial_guard`=26, `inquisitor`=18, `kagerou`=6, `meister`=18, `night_watch`=16, `oboro`=6, `rebellion`=12, `shadow_cross`=18, `shinkiro`=8, `shiranui`=8, `sky_emperor`=18, `sky_emperor2`=14, `soul_ascetic`=18, `spirit_handler`=22, `summoner`=22, `troubadour`=9, `trouvere`=9, `windhawk`=16, `건너`=12, `검사`=21, `궁수`=16, `권성`=12, `권성융합`=12, `기사`=21, `길로틴크로스`=12, `닌자`=12, `도둑`=17, `레인져`=12, `로그`=16, `로드나이트`=13, `룬나이트`=13, `마법사`=14, `몽크`=16, `무희`=7, `미케닉`=12, `민스트럴`=6, `바드`=7, `상인`=16, `성직자`=16, `세이지`=14, `소서러`=12, `소울링커`=12, `수라`=12, `쉐도우체이서`=12, `슈퍼노비스`=14, `스나이퍼`=12, `스토커`=12, `아크비숍`=12, `어세신`=16, `어쌔신크로스`=12, `연금술사`=17, `오보로`=5, `워록`=12, `원더러`=6, `위저드`=14, `제네릭`=12, `제철공`=16, `집시`=6, `챔피온`=12, `초보자`=14, `카게로`=5, `크루세이더`=20, `크리에이터`=12, `클라운`=6, `태권소년`=12, `팔라딘`=12, `프로페서`=12, `프리스트`=16, `하이위저드`=12, `하이프리스트`=12, `헌터`=14, `화이트스미스`=12

## Robes — sprites (`data/sprite/로브`)

- **Archivos:** 42276 · GRF: data=34055, rdata=8221
- **Duplicados:** 5579
- **Stems únicos (capa):** 471 · spr+act=396 (cada capa se replica por job/sexo → muchos archivos)
- **Capas distintas:** 82
- Top: `c_giant_shark`=718, `c_put_on_coat`=718, `c_school_bag_pu`=709, `c_bloody_wing`=701, `c_samba_carnival`=698, `c_kings_twin_sword`=682, `c_triple_ice_cream`=682, `c_school_bag_bl`=679, `아미스트르가방`=671, `halloween_poring_bag`=669, `c_sakura_wing`=669, `c_t_bear_bag`=669, `c_big_ribbon_cloak`=664, `아버지사랑날개2012`=661, `기린의날개`=661, … +67

## Mobs — sprites (`data/sprite/몬스터`)

- **Archivos:** 2869
- **Por GRF ganador:** data=2739, rdata=130
- **Duplicados entre GRFs:** 130
  - rdata≻data=130
- **Assets sprite (stems):** 1448 · spr+act=1420 · solo.spr=0 · solo.act=28 · otros=1
- **Rutas:** 1

- `data/sprite/몬스터/` — **2869** (.act×1448, .spr×1420, .flc×1)
  - Series: `geffen_mage_*`×11[1–2, 4–12]; `ep14_mors_mob*`×6[1–6]; `elemetal_master_s*`×5[1–5]; `goblin_*`×5[1–5]; `kobold_*`×5[1–5]; `meister_abr*`×4[1–4]; `venatu_*`×4[1–4]; `pere*`×4[1–4]; `dimik_*`×4[1–4]; `crystal_*`×4[1–4]; `morocc_*`×4[1–4]; `ep18_armed_villager*`×3[1–3]; `poton_canon_*`×3[1–3]; `e_cowraiders*`×3[1–3]; `g_cowraiders*`×3[1–3]; `dr_basilisk*`×3[1–3]; `ep14_3_death_a_mob*`×3[1–3]; `ep14_3_death_b_mob*`×3[1–3]; `cowraiders*`×3[1–3]; `geffen_mage_3_*`×3[1–3]; +3 series
  - Nombres no-ID: **2685** (`14_3_mercenary_a` … `워그`)

## NPCs — sprites (`data/sprite/npc`)

- **Archivos:** 2473
- **Por GRF ganador:** data=2463, rdata=10
- **Duplicados entre GRFs:** 10
  - rdata≻data=10
- **Assets sprite (stems):** 1235 · spr+act=1235 · solo.spr=0 · solo.act=0 · otros=3
- **Rutas:** 1

- `data/sprite/npc/` — **2473** (.act×1235, .spr×1235, .sfk×3)
  - Series: `4_tower_*`×17[1–17]; `4_ragfes_*`×15[2–16]; `4_geffen_*`×14[1–14]; `4_f_kafra*`×9[1–9]; `4_f_*`×8[1–8]; `4_xmas_cat*`×6[1–6]; `4_m_*`×6[1–6]; `4_f_fairykid*`×5[2–6]; `4_cat_sailor*`×5[1–5]; `4_man_piom*`×5[2–6]; `kobold_*`×5[1–5]; `goblin_*`×5[1–5]; `4_m_fairykid*`×5[2–6]; `1_f_*`×4[1–4]; `1_f_orient_*`×4[1–4]; `1_m_*`×4[1–4]; `4_f_ruswoman*`×3[1–3]; `4_m_cactusman*`×3[1–3]; `4_m_kid*`×3[1–3]; `4_f_charleston*`×3[1–3]; +4 series
  - Nombres no-ID: **2191** (`1_etc_1` … `zombie`)

## Humanoid / jobs (`data/sprite/인간족`)

- **Archivos:** 11733 · GRF: data=8592, rdata=3137, ozro_fix=4
- **Duplicados:** 3139 · rdata≻data=3137; ozro_fix≻data=2
- **Subcarpetas (jobs/partes):** 77
  - `몸통/` — 1028
  - `imperial_guard/` — 370
  - `로얄가드/` — 370
  - `크루세이더/` — 354
  - `페코페코_기사/` — 350
  - `dragon_knight_chicken/` — 340
  - `페코페코_룬나이트/` — 338
  - `신페코로얄가드/` — 334
  - `imperial_guard_chicken/` — 332
  - `dragon_knight/` — 328
  - `룬나이트/` — 328
  - `신페코크루세이더/` — 326
  - `기사/` — 324
  - `검사/` — 324
  - `biolo/` — 282
  - `제네릭/` — 282
  - `연금술사/` — 230
  - `meister/` — 228
  - `구페코크루세이더/` — 228
  - `상인/` — 220
  - `미케닉/` — 220
  - `제철공/` — 216
  - `inquisitor/` — 168
  - `머리통/` — 168
  - `몽크/` — 168
  - … +52

## Homunculus (`data/sprite/homun`)

- **Archivos:** 42
- **Por GRF ganador:** data=42
- **Duplicados entre GRFs:** 0
- **Assets sprite (stems):** 21 · spr+act=21 · solo.spr=0 · solo.act=0 · otros=0
- **Rutas:** 1

- `data/sprite/homun/` — **42** (.act×21, .spr×21)
  - Nombres no-ID: **42** (`amistr` … `vanilmirth_h2`)

## Mapas

- **Nombres distintos:** 917
- **Completos (rsw+gat+gnd):** 917
- **Incompletos:** 0
- **`.rsw` por GRF:** data=879, rdata=23, ozro=11, gefenia=4
- **`.gat` por GRF:** data=885, rdata=23, ozro=5, gefenia=4
- **`.gnd` por GRF:** data=879, rdata=23, ozro=11, gefenia=4
- **Archivos duplicados entre GRFs:** 93
  - rdata≻data=69; ozro≻data=12; gefenia≻data=12

### Series `prefijo+N` (539 mapas · 183 series)

- `abbey*` ×3 [1–3]
- `abyss_*` ×4 [1–4]
- `alde_dun*` ×4 [1–4]
- `alde_tt*` ×2 [2–3]
- `aldeg_cas*` ×5 [1–5]
- `ama_dun*` ×3 [1–3]
- `ama_fild*` ×1 [1]
- `ama_in*` ×2 [1–2]
- `amicit*` ×2 [1–2]
- `amicitia*` ×2 [1–2]
- `anthell*` ×2 [1–2]
- `arug_cas*` ×3 [1–3]
- `arug_dun*` ×1 [1]
- `arug_que*` ×1 [1]
- `auction_*` ×2 [1–2]
- `ayo_dun*` ×2 [1–2]
- `ayo_fild*` ×2 [1–2]
- `ayo_in*` ×2 [1–2]
- `ba_2whs*` ×2 [1–2]
- `ba_in*` ×1 [1]
- `ba_pw*` ×3 [1–3]
- `bat_a*` ×1 [1]
- `bat_b*` ×1 [1]
- `bat_c*` ×1 [1]
- `beach_dun*` ×2 [2–3]
- `bif_fild*` ×2 [1–2]
- `bra_dun*` ×2 [1–2]
- `bra_fild*` ×1 [1]
- `bra_in*` ×1 [1]
- `c_tower*` ×4 [1–4]
- `clock_*` ×1 [1]
- `cmd_fild*` ×9 [1–9]
- `cmd_in*` ×2 [1–2]
- `dali*` ×1 [2]
- `dew_dun*` ×2 [1–2]
- `dew_fild*` ×1 [1]
- `dew_in*` ×1 [1]
- `dic_dun*` ×2 [1–2]
- `dic_fild*` ×2 [1–2]
- `dic_in*` ×1 [1]
- `dicastes*` ×2 [1–2]
- `ecl_fild*` ×1 [1]
- `ecl_hub*` ×1 [1]
- `ecl_in*` ×4 [1–4]
- `ecl_tdun*` ×4 [1–4]
- `ein_dun*` ×3 [1–3]
- `ein_fild*` ×10 [1–10]
- `ein_in*` ×1 [1]
- `force_map*` ×3 [1–3]
- `gef_dun*` ×4 [0–3]
- `gef_fild*` ×15 [0–14]
- `gefenia*` ×4 [1–4]
- `gefg_cas*` ×5 [1–5]
- `gl_cas*` ×2 [1–2]
- `gl_dun*` ×2 [1–2]
- `gl_in*` ×1 [1]
- `gl_knt*` ×2 [1–2]
- `gl_prison*` ×1 [1]
- `gl_sew*` ×4 [1–4]
- `glast_*` ×1 [1]
- `gld_dun*` ×4 [1–4]
- `gon_dun*` ×3 [1–3]
- `gon_fild*` ×1 [1]
- `guild_vs*` ×5 [1–5]
- `gw_fild*` ×2 [1–2]
- `har_in*` ×1 [1]
- `harboro*` ×2 [1–2]
- `hu_fild*` ×7 [1–7]
- `hu_in*` ×1 [1]
- `ice_dun*` ×4 [1–4]
- `in_moc_*` ×1 [16]
- `in_orcs*` ×1 [1]
- `in_sphinx*` ×5 [1–5]
- `int_land*` ×4 [1–4]
- `iz_ac*` ×2 [1–2]
- `iz_dun*` ×6 [0–5]
- `iz_int*` ×4 [1–4]
- `iz_ng*` ×1 [1]
- `job3_arch*` ×2 [1–2]
- `job3_gen*` ×1 [1]
- `job3_guil*` ×3 [1–3]
- `job3_rang*` ×2 [1–2]
- `job3_rune*` ×2 [1–2]
- `job3_sha*` ×1 [1]
- `job3_war*` ×2 [1–2]
- `job_sword*` ×1 [1]
- `job_thief*` ×1 [1]
- `jupe_area*` ×2 [1–2]
- `jupe_core*` ×1 [2]
- `juperos_*` ×2 [1–2]
- `kh_dun*` ×2 [1–2]
- `kh_kiehl*` ×2 [1–2]
- `lasa_dun*` ×3 [1–3]
- `lasa_fild*` ×2 [1–2]
- `lasa_in*` ×1 [1]
- `lhz_d_n*` ×1 [2]
- `lhz_dun*` ×4 [1–4]
- `lhz_fild*` ×3 [1–3]
- `lhz_in*` ×3 [1–3]
- `lhz_que*` ×1 [1]
- `lou_dun*` ×3 [1–3]
- `lou_fild*` ×1 [1]
- `lou_in*` ×2 [1–2]
- `ma_dun*` ×1 [1]
- `ma_fild*` ×2 [1–2]
- `ma_in*` ×1 [1]
- `ma_scene*` ×1 [1]
- `ma_zif*` ×9 [1–9]
- `mag_dun*` ×3 [1–3]
- `mal_dun*` ×1 [1]
- `mal_in*` ×2 [1–2]
- `man_fild*` ×3 [1–3]
- `man_in*` ×1 [1]
- `mjo_dun*` ×3 [1–3]
- `mjolnir_*` ×12 [1–12]
- `mjolnir_04_*` ×1 [1]
- `moc_fild*` ×22 [1–22]
- `moc_para*` ×1 [1]
- `moc_pryd*` ×6 [1–6]
- `moc_prydb*` ×1 [1]
- `moc_prydn*` ×2 [1–2]
- `mosk_dun*` ×3 [1–3]
- `mosk_fild*` ×2 [1–2]
- `new_zone*` ×4 [1–4]
- `nif_dun*` ×2 [1–2]
- `nif_fild*` ×2 [1–2]
- `nyd_dun*` ×2 [1–2]
- `odin_tem*` ×3 [1–3]
- `orcsdun*` ×2 [1–2]
- `ordeal_a*` ×2 [0, 2]
- `oz_dun*` ×2 [1–2]
- `p_track*` ×1 [1]
- `pay_dun*` ×5 [0–4]
- `pay_fild*` ×11 [1–11]
- `payg_cas*` ×5 [1–5]
- `payon_in*` ×3 [1–3]
- `poring_w*` ×2 [1–2]
- `prt_are*` ×1 [1]
- `prt_fild*` ×12 [0–11]
- `prt_maze*` ×3 [1–3]
- `prt_pri*` ×1 [0]
- `prt_sewb*` ×4 [1–4]
- `prtg_cas*` ×5 [1–5]
- `pvp_2vs*` ×1 [2]
- `que_avan*` ×1 [1]
- `que_dan*` ×2 [1–2]
- `que_god*` ×2 [1–2]
- `que_job*` ×2 [1–2]
- `que_qsch*` ×1 [1]
- `que_sign*` ×1 [1]
- `quiz_*` ×3 [0–2]
- `ra_fild*` ×13 [1–13]
- `ra_in*` ×1 [1]
- `ra_san*` ×5 [1–5]
- `rockmi*` ×2 [1–2]
- `rockrdg*` ×2 [1–2]
- `schg_cas*` ×3 [1–3]
- `schg_dun*` ×1 [1]
- `sec_in*` ×2 [1–2]
- `slabw*` ×1 [1]
- `sp_rudus*` ×3 [2–4]
- `spl_fild*` ×3 [1–3]
- `spl_in*` ×2 [1–2]
- `te_aldecas*` ×5 [1–5]
- `te_prtcas*` ×5 [1–5]
- `teg_dun*` ×2 [1–2]
- `tha_scene*` ×1 [1]
- `tha_t*` ×12 [1–12]
- `thor_v*` ×3 [1–3]
- `treasure*` ×2 [1–2]
- `treasure_n*` ×2 [1–2]
- `tur_dun*` ×6 [1–6]
- `um_dun*` ×2 [1–2]
- `um_fild*` ×4 [1–4]
- `ve_fild*` ×7 [1–7]
- `ve_in*` ×1 [2]
- `verus*` ×4 [1–4]
- `vis_h*` ×4 [1–4]
- `xmas_dun*` ×2 [1–2]
- `xmas_fild*` ×1 [1]
- `yggdrasil*` ×1 [1]
- `yuno_fild*` ×12 [1–12]
- `yuno_in*` ×5 [1–5]

### Sin sufijo numérico puro (378)

- **Instancias** (`N@…`): 126
  - `1@*` ×102: `1@4cdn` … `1@xm_d2`
  - `2@*` ×13: `2@cata` … `2@tower`
  - `3@*` ×3: `3@ch_t`, `3@thts`, `3@tower`
  - `4@*` ×2: `4@thts`, `4@tower`
  - `5@*` ×2: `5@thts`, `5@tower`
  - `6@*` ×2: `6@thts`, `6@tower`
  - `7@*` ×1: `7@thts`
  - `8@*` ×1: `8@thts`
- **Resto:** 252
  - `06guild_*` ×1: `06guild_r`
  - `airpl*` ×1: `airplane`
  - `airpo*` ×1: `airport`
  - `alb2t*` ×1: `alb2trea`
  - `alb_*` ×1: `alb_ship`
  - `alber*` ×1: `alberta`
  - `alberta_*` ×1: `alberta_in`
  - `alde_*` ×2: `alde_alche`, `alde_gld`
  - `aldeb*` ×1: `aldebaran`
  - `aldeba_*` ×1: `aldeba_in`
  - `ama_*` ×1: `ama_test`
  - `amats*` ×1: `amatsu`
  - `ant_*` ×1: `ant_d02_i`
  - `arena_*` ×1: `arena_room`
  - `aru_*` ×1: `aru_gld`
  - `ayoth*` ×1: `ayothaya`
  - `ba_*` ×6: `ba_bath`, `ba_chess`, `ba_go`, `ba_lib`, `ba_lost`, `ba_maison`
  - `bat_*` ×1: `bat_room`
  - `beach_*` ×1: `beach_dun`
  - `bl_*` ×4: `bl_death`, `bl_grass`, `bl_ice`, `bl_lava`
  - `brasi*` ×1: `brasilis`
  - `c_*` ×2: `c_tower2_`, `c_tower3_`
  - `cave*` ×1: `cave`
  - `com_*` ×1: `com_d02_i`
  - `comod*` ×1: `comodo`
  - `conch_*` ×1: `conch_in`
  - `dali*` ×1: `dali`
  - `dewat*` ×1: `dewata`
  - `e_*` ×2: `e_hugel`, `e_tower`
  - `eclag*` ×1: `eclage`
  - `ein_*` ×1: `ein_d02_i`
  - `einbe*` ×1: `einbech`
  - `einbr*` ×1: `einbroch`
  - `evt_*` ×2: `evt_bomb`, `evt_mobroom`
  - `gef_*` ×2: `gef_d01_i`, `gef_tower`
  - `geffe*` ×1: `geffen`
  - `geffen_*` ×1: `geffen_in`
  - `gl_*` ×7: `gl_cas01_`, `gl_cas02_`, `gl_church`, `gl_chyard`, `gl_chyard_`, `gl_prison`, `gl_step`
  - `gld2_*` ×4: `gld2_ald`, `gld2_gef`, `gld2_pay`, `gld2_prt`
  - `gon_*` ×2: `gon_in`, `gon_test`
  - `gonry*` ×1: `gonryun`
  - `grade*` ×1: `grademk`
  - `hugel*` ×1: `hugel`
  - `ice_*` ×1: `ice_d03_i`
  - `in_*` ×2: `in_hunter`, `in_rogue`
  - `int_*` ×1: `int_land`
  - `iz_*` ×11: `iz_ac01_a` … `iz_int`
  - `izlu2*` ×1: `izlu2dun`
  - `izlud*` ×1: `izlude`
  - `izlude_*` ×5: `izlude_a`, `izlude_b`, `izlude_c`, `izlude_d`, `izlude_in`
  - `jawai*` ×1: `jawaii`
  - `jawaii_*` ×1: `jawaii_in`
  - `job4_*` ×3: `job4_bio`, `job4_mag`, `job4_tro`
  - `job_*` ×16: `job_cru` … `job_wizard`
  - `jupe_*` ×5: `jupe_cave`, `jupe_core`, `jupe_ele`, `jupe_ele_r`, `jupe_gate`
  - `kh_*` ×4: `kh_mansion`, `kh_rossi`, `kh_school`, `kh_vila`
  - `lasa_*` ×2: `lasa_dun_q`, `lasa_sea`
  - `lasag*` ×1: `lasagna`
  - `lhz_*` ×2: `lhz_cube`, `lhz_dun_n`
  - `light*` ×1: `lighthalzen`
  - `louya*` ×1: `louyang`
  - `malan*` ×1: `malangdo`
  - `malay*` ×1: `malaya`
  - `manuk*` ×1: `manuk`
  - `mid_*` ×2: `mid_camp`, `mid_campin`
  - `moc_*` ×3: `moc_castle`, `moc_fild22b`, `moc_ruins`
  - `monk_*` ×2: `monk_in`, `monk_test`
  - `mora*` ×1: `mora`
  - `moro_*` ×2: `moro_cav`, `moro_vol`
  - `moroc*` ×1: `morocc`
  - `morocc_*` ×1: `morocc_in`
  - `mosco*` ×1: `moscovia`
  - `mosk_*` ×3: `mosk_in`, `mosk_que`, `mosk_ship`
  - `n_*` ×1: `n_castle`
  - `nakhy*` ×1: `nakhyang`
  - `nameless_*` ×3: `nameless_i`, `nameless_in`, `nameless_n`
  - `new_*` ×1: `new_event`
  - `nif_*` ×1: `nif_in`
  - `niflh*` ×1: `niflheim`
  - `niflx*` ×1: `niflxmas`
  - `odin_*` ×1: `odin_past`
  - `param*` ×1: `paramk`
  - `pay_*` ×3: `pay_arche`, `pay_d03_i`, `pay_gld`
  - `payon*` ×1: `payon`
  - `ppron*` ×1: `pprontera`
  - `pront*` ×1: `prontera`
  - `prt_*` ×18: `prt_are_in` … `prt_q`
  - `pub_*` ×1: `pub_cat`
  - `pvp_*` ×9: `pvp_room`, `pvp_y_1-2`, `pvp_y_2-2`, `pvp_y_3-2`, `pvp_y_4-2`, `pvp_y_5-2`, `pvp_y_6-2`, `pvp_y_7-2`, `pvp_y_8-2`
  - `que_*` ×10: `que_ba`, `que_bingo`, `que_house_s`, `que_hugel`, `que_lhz`, `que_ng`, `que_rachel`, `que_swat`, `que_thor`, `que_thr`
  - `ra_*` ×3: `ra_temin`, `ra_temple`, `ra_temsky`
  - `rache*` ×1: `rachel`
  - `rag_*` ×2: `rag_fes`, `rag_fes_a`
  - `rebel_*` ×1: `rebel_in`
  - `rgsr_*` ×1: `rgsr_in`
  - `s_*` ×1: `s_atelier`
  - `sch_*` ×1: `sch_gld`
  - `sec_*` ×1: `sec_pri`
  - `siege_*` ×1: `siege_test`
  - `silk_*` ×1: `silk_lair`
  - `sp_*` ×3: `sp_cor`, `sp_os`, `sp_rudus`
  - `splen*` ×1: `splendide`
  - `star_*` ×2: `star_frst`, `star_in`
  - `sword_*` ×3: `sword_1-1`, `sword_2-1`, `sword_3-1`
  - `te_*` ×2: `te_alde_gld`, `te_prt_gld`
  - `thana_*` ×2: `thana_boss`, `thana_step`
  - `thor_*` ×1: `thor_camp`
  - `tra_*` ×1: `tra_fild`
  - `tur_*` ×4: `tur_d03_i`, `tur_d04_i`, `tur_d04ia`, `tur_d04ib`
  - `turbo_*` ×1: `turbo_room`
  - `um_*` ×1: `um_in`
  - `umbal*` ×1: `umbala`
  - `un_*` ×3: `un_bk_q`, `un_bunker`, `un_myst`
  - `valky*` ×1: `valkyrie`
  - `ve_*` ×1: `ve_in`
  - `veins*` ×1: `veins`
  - `ver_*` ×2: `ver_eju`, `ver_tunn`
  - `verus02_*` ×2: `verus02_a`, `verus02_b`
  - `wolfv*` ×1: `wolfvill`
  - `x_*` ×3: `x_lhz`, `x_prt`, `x_ra`
  - `xmas*` ×1: `xmas`
  - `xmas_*` ×1: `xmas_in`
  - `yuno*` ×1: `yuno`
  - `yuno_*` ×1: `yuno_pre`

## Minimaps / map UI

- **Archivos:** 923 · GRF: data=890, rdata=27, renewal2021=6
- `data/texture/유저인터페이스/map/` — 857
- `data/texture/유저인터페이스/minimap/` — 66

## Skills

- **Carpeta `skillicon/`:** no existe en este cliente (ni en data ni en patch/renewal/resources).
- **UI buttons `btn_skill*`:** 6 · renewal2021=3, data=3
  - `data/texture/유저인터페이스/btn_skill.bmp` ← `renewal2021`
  - `data/texture/유저인터페이스/btn_skill_a.bmp` ← `renewal2021`
  - `data/texture/유저인터페이스/btn_skill_b.bmp` ← `renewal2021`
  - `data/texture/유저인터페이스/basic_interface/btn_skill_dis.bmp` ← `data`
  - `data/texture/유저인터페이스/basic_interface/btn_skill_on.bmp` ← `data`
  - `data/texture/유저인터페이스/basic_interface/btn_skill_off.bmp` ← `data`
- **Lua/Lub skill* activos:** 23
- **`skillinfolist` ganador:** `data/luafiles514/lua files/skillinfoz/skillinfolist.lub` ← `renewal2021`
  - Entradas SKID: **1446** (únicos 1446)
  - `SkillName` definidos: **1446**
  - Por prefijo job/skill: `NPC`=80, `EL`=42, `DE`=40, `SA`=35, `SU`=35, `DA`=33, `EM`=32, `SL`=31, `NC`=30, `AM`=27, `MB`=27, `SO`=27, `MH`=26, `BS`=24, `AB`=24, `WL`=24, `NJ`=23, `RA`=23, `SR`=23, `RK`=22, `SC`=22, `WM`=22, `KO`=22, `GS`=22, `SJ`=22, … +68
- **`skillid` ganador:** `data/luafiles514/lua files/skillinfoz/skillid.lub` ← `renewal2021` · 1667 IDs · 1658 ids · span 1–12999 · 28 rangos → 1–776, 1001–1019, 2000–2057, 2200–2304, 2306–2352, 2379–2383, 2410–2434, 2441–2468, 2472–2498, 2513–2520, 2531–2612, 3001–3044, 5000–5058, 5063–5065, 5068, 5072–5078, 5201–5305, 5311–5381, 5383–5384, 8000–8045, 8200–8242, 8400–8457, 8601–8605, 9999–10020, 10100–10101, 11000–11006, 11999–12000, 12999
- **Archivos skill lua/lub:**
  - `data/lua files/skilleffectinfo/actorstate.lub` ← `renewal2021`
  - `data/lua files/skilleffectinfo/effectid.lub` ← `renewal2021`
  - `data/lua files/skilleffectinfo/skilleffectinfo_f.lub` ← `renewal2021`
  - `data/lua files/skilleffectinfo/skilleffectinfolist.lub` ← `renewal2021`
  - `data/lua files/skillinfoz/jobinheritlist.lub` ← `renewal2021`
  - `data/lua files/skillinfoz/skilldescript.lub` ← `renewal2021`
  - `data/lua files/skillinfoz/skillid.lub` ← `renewal2021`
  - `data/lua files/skillinfoz/skillinfo_f.lub` ← `renewal2021`
  - `data/lua files/skillinfoz/skillinfolist.lub` ← `renewal2021`
  - `data/lua files/skillinfoz/skilltreeview.lub` ← `renewal2021`
  - `data/luafiles514/lua files/newskillinfo/jobinheritlist.lub` ← `data`
  - `data/luafiles514/lua files/skilleffectinfo/actorstate.lub` ← `renewal2021` · también ['renewal2021', 'data']
  - `data/luafiles514/lua files/skilleffectinfo/effectid.lub` ← `renewal2021` · también ['renewal2021', 'data']
  - `data/luafiles514/lua files/skilleffectinfo/skilleffectinfo_f.lub` ← `renewal2021` · también ['renewal2021', 'data']
  - `data/luafiles514/lua files/skilleffectinfo/skilleffectinfolist.lub` ← `renewal2021` · también ['renewal2021', 'data']
  - `data/luafiles514/lua files/skillinfoz/jobinheritlist.lub` ← `renewal2021` · también ['renewal2021', 'rdata', 'data']
  - `data/luafiles514/lua files/skillinfoz/skilldescript.lub` ← `renewal2021` · también ['renewal2021', 'rdata', 'data']
  - `data/luafiles514/lua files/skillinfoz/skillid.lub` ← `renewal2021` · también ['renewal2021', 'rdata', 'data']
  - `data/luafiles514/lua files/skillinfoz/skillinfo_f.lub` ← `renewal2021` · también ['renewal2021', 'rdata', 'data']
  - `data/luafiles514/lua files/skillinfoz/skillinfolist.lub` ← `renewal2021` · también ['renewal2021', 'rdata', 'data']
  - `data/luafiles514/lua files/skillinfoz/skilltreeview.lub` ← `renewal2021` · también ['renewal2021', 'rdata', 'data']
  - `data/luafiles514/lua files/skillinfoz/skilltreeview_web.lub` ← `renewal2021`
  - `data/luafiles514/lua files/skillinfoz/test.lub` ← `renewal2021`

## Anexo — tops `data/sprite/*`

- `data/sprite/로브/` — 42276
- `data/sprite/아이템/` — 17056
- `data/sprite/인간족/` — 11733
- `data/sprite/악세사리/` — 7548
- `data/sprite/몬스터/` — 2869
- `data/sprite/npc/` — 2473
- `data/sprite/방패/` — 2140
- `data/sprite/이팩트/` — 427
- `data/sprite/도람족/` — 100
- `data/sprite/homun/` — 42
- `data/sprite/book/` — 10
- `data/sprite/roullette/` — 6
- `data/sprite/shadow.act/` — 1
- `data/sprite/shadow.spr/` — 1
- `data/sprite/collection_slotmachine.act/` — 1
- `data/sprite/collection_slotmachine.spr/` — 1
- `data/sprite/count.spr/` — 1
- `data/sprite/ork_warrior.act/` — 1
- `data/sprite/ork_warrior.spr/` — 1
- `data/sprite/slotmachine.act/` — 1
- `data/sprite/slotmachine.spr/` — 1
- `data/sprite/cursors.act/` — 1
- `data/sprite/cursors.spr/` — 1

## Anexo — carpetas UI (top 40)

- `…/item/` — 8591
- `…/collection/` — 7211
- `…/illust/` — 1357
- `…/cardbmp/` — 984
- `…/map/` — 857
- `…/basic_interface/` — 805
- `…/renewalparty/` — 599
- `…/renewalparty 2017/` — 532
- `…/cashshop/` — 295
- `…/tipbox/` — 259
- `…/navigation_interface3/` — 158
- `…/styleshop/` — 133
- `…/make_character_ver2/` — 129
- `…/refining_renewal/` — 91
- `…/refining/` — 79
- `…/login_interface/` — 78
- `…/menu_icon/` — 78
- `…/achievement_re/` — 73
- `…/renew_questui/` — 69
- `…/minimap/` — 66
- `…/ro_menu_icon/` — 64
- `…/dancing_knife/` — 54
- `…/select_character_ver3/` — 49
- `…/replay_interface/` — 45
- `…/navigation_interface/` — 42
- `…/battle_field/` — 40
- `…/uiadventureragency/` — 40
- `…/select_character/` — 35
- `…/information/` — 33
- `…/inventory/` — 31
- `…/grade_enchant/` — 31
- `…/lapine/` — 29
- `…/bank/` — 25
- `…/group/` — 25
- `…/worldview_interface/` — 25
- `…/enchantui/` — 25
- `…/achievement/` — 24
- `…/make_character/` — 24
- `…/display_mapname/` — 18
- `…/clan_system/` — 18
- … +460 carpetas más

