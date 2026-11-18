# Reformulación de Garrett

**Estado:** análisis preliminar  
**Fuente de datos:** `data/market/` v2  
**Comparación reproducible:** `tools/market/analyze_garrett.py` → `data/market/samples/garrett_comparison.{json,md}`

---

## 1. Estado actual

Garrett sigue usando `npc/custom/ozro/trasher.txt` con arrays hardcodeados:

- 5 ofertas diarias (`abundant`, `common`, `uncommon`, `rare`).
- Cap de compra: 500.000z por cuenta/día.
- 3 contratos de misión (`mcommon`, `muncommon`, `mrare`).
- Ventana de misión: 6 horas.
- Pago: `unitPrice * quantity * 1.5`, con mínimo 500.000 y cap 1.500.000.
- Cantidad: derivada de la posición dentro del tier y del peso, no del valor real del item.
- Precios: listas viejas, no el mercado v2.

Los generadores específicos de Garrett fueron eliminados. La tabla actual es legacy.

---

## 2. Evidencia contra el mercado v2

`analyze_garrett.py` compara los arrays actuales contra `npcBuyPrice`, `mid`, `supplyOpen` y `abundanceTier` de v2.

### 2.1 Misiones

| Item | Qty | Pago viejo | `npcBuy × qty` | Ratio |
|---|---:|---:|---:|---:|
| Glossy Hair | 123 | 553.500 | 21.894 | **25,3x** |
| White Powder | 19 | 609.900 | 26.600 | **22,9x** |
| Coconut Fruit | 23 | 935.000 | 89.700 | **10,4x** |
| Battered Kettle | 25 | 1.125.000 | 110.000 | **10,2x** |
| Old Manteau | 21 | 765.400 | 84.000 | **9,1x** |
| Black Powder | 61 | 786.900 | 103.700 | **7,6x** |
| Dragon's Mane | 67 | 954.800 | 254.600 | 3,8x |
| Broken Shell | 70 | 1.050.000 | 294.000 | 3,6x |
| Dry Sand | 150 | 900.000 | 600.000 | 1,5x |
| Giant Butterfly Wing | 145 | 826.500 | 594.500 | 1,4x |
| Leopard Skin | 128 | 614.400 | 460.800 | 1,3x |
| Striped Sock | 139 | 750.600 | 639.400 | 1,2x |

**17 de 17 misiones** pagan por encima del valor canónico de compra NPC. **7** pagan más de 3x. **5** pagan más de 9x.

### 2.2 Ofertas

También hay errores en ambos sentidos:

| Item | Precio viejo | `npcBuyPrice` v2 | Ratio |
|---|---:|---:|---:|
| Vane | 4.000 | 84 | **47,6x** |
| Glossy Hair | 3.000 | 178 | **16,9x** |
| White Powder | 21.400 | 1.400 | **15,3x** |
| Coconut Fruit | 27.100 | 3.900 | 6,9x |
| Black Powder | 8.600 | 1.700 | 5,1x |
| Dry Sand | 4.000 | 4.000 | 1,0x |
| Tattered Clothes | 800 | 4.200 | 0,19x |
| Dust Pollutant | 700 | 4.100 | 0,17x |
| Sand Clump | 600 | 3.900 | 0,15x |
| Harpy Talon | 600 | 3.900 | 0,15x |

No es solo sobrepago: también hay items abundantes pagados muy por debajo del valor canónico.

---

## 3. Causas

1. **Piso fijo de 500.000z.** Cualquier misión, incluso con items triviales, arranca en 500k.
2. **Cantidad por peso/tier, no por esfuerzo.** No usa `supplyOpen`, `difficulty` ni el valor unitario.
3. **Precio viejo por tier.** Los tiers se asignaron con la lista anterior, no con v2.
4. **Multiplicador fijo 1,5.** No distingue item fácil, raro, boss, instancia o high-HP.
5. **Sin anti-arbitraje.** No compara contra NPC shop ni contra `npcBuyPrice`.
6. **Sin exclusión de acceso.** No filtra instancia, guild, quest, boss-only, high-HP o group-only.

El caso “Suspicious Rat” cae en el mismo patrón: item fácil, tier alto o cantidad baja, pago mínimo 500k. El sistema paga por “tier viejo”, no por esfuerzo real.

---

## 4. Propuesta

### 4.1 Fuente única

Garrett deja de tener tablas propias. Las ofertas y misiones se generan desde el master v2:

- `price.npcBuyPrice` para lo que Garrett paga.
- `price.mid` para presupuesto y referencia.
- `supply.abundanceTier` y `supply.difficultyTier` para elegir el pool.
- `demand.marketPressure` para ajustar pago/stock.
- `access` y `tags` para excluir fuentes no farmeables.
- `weight` para el cap de peso.

### 4.2 Pool de ofertas

Incluir solo si:

```
marketEligible == true
commonFarmEligible == true
supplyOpen > 0
not tags: instance_only, guild_only, boss_only, high_hp, high_hp_source, no_spawn
not group_only
not untradeable
not cash_shop
not party/instance-only
```

Excluir o capar si el item está en NPC shop y `npcSellToPlayer <= npcBuyPrice`.

Precio de oferta:

```
offerPrice = npcBuyPrice
```

Sin factors extra. `npcBuyPrice` ya aplica supply, demanda, dificultad y caps.

Opcional futuro: multiplicador histórico por NPC, como dice el diseño:

```
offerPrice *= npcHistoryMultiplier
```

La base sigue siendo `npcBuyPrice`.

### 4.3 Pool de misiones

Incluir solo si:

```
marketEligible == true
commonFarmEligible == true
supplyOpen > 0
not tags: instance_only, guild_only, boss_only, high_hp, no_spawn
not group_only
not untradeable
```

Tiers:

| Tier | Criterio |
|---|---|
| Común | `abundanceTier in {abundant, common}` y `difficultyTier in {easy, medium}` |
| Poco común | `abundanceTier in {common, uncommon}` y `difficultyTier in {easy, medium, hard}` |
| Raro | `abundanceTier in {uncommon, scarce, rare}` o `difficultyTier in {hard, extreme}` |

### 4.4 Cantidad y pago

La cantidad debe salir de un **pago objetivo**, no de un pago fijo por tier.

```
unit = max(1, npcBuyPrice)
targetPayout = tierTarget[tier] * (1 + marketPressure / 200)
targetPayout = clamp(targetPayout, 100_000, 600_000)

qty = round(targetPayout / unit)
qty = clamp(qty, minQty[tier], maxQty[tier])
qty = min(qty, floor(MAX_MISSION_WEIGHT / max(1, weight)))

payout = round(unit * qty * missionMultiplier)
payout = clamp(payout, 50_000, 1_500_000)
```

Valores iniciales:

| Tier | `tierTarget` | `minQty` | `maxQty` |
|---|---:|---:|---:|
| Común | 200.000 | 20 | 300 |
| Poco común | 350.000 | 10 | 150 |
| Raro | 500.000 | 5 | 60 |

`missionMultiplier`: 1,20.

Efecto:

- Item fácil y barato: `qty` sube hasta el cap y el pago queda bajo.
- Item caro: `qty` baja y el pago se acerca al objetivo.
- Item de instancia/boss/high-HP: no entra.
- Nunca se paga el piso de 500k por un item trivial.

### 4.5 Anti-arbitraje

```
if item is npc_shop and npcSellToPlayer < offerPrice:
    offerPrice = npcSellToPlayer * 0.90
```

Para misiones:

```
maxPayoutByShop = npcSellToPlayer * qty * 0.90
payout = min(payout, maxPayoutByShop)
```

Si el item se puede comprar más barato en NPC shop, Garrett no debe pagar más que eso.

### 4.6 Frecuencia y stock

No hace falta stock para Garrett; las ofertas ya son diarias. Pero se puede usar:

```
marketPressure > 25  -> oferta más baja o menos cantidad
marketPressure < -25 -> oferta normal o más cantidad
```

La base de precio no cambia por esto; solo el pool/cantidad.

---

## 5. Pseudocódigo

```python
def build_offers(master, day_seed, count=5):
    pool = [i for i in master if offer_eligible(i)]
    rng = random.Random(day_seed)
    chosen = rng.sample(pool, count)
    return [
        {
            "itemId": i.itemId,
            "price": i.price.npcBuyPrice,
        }
        for i in chosen
    ]


def build_missions(master, day_seed):
    result = []
    for tier in ("common", "uncommon", "rare"):
        pool = [i for i in master if mission_eligible(i) and mission_tier(i) == tier]
        item = choose_daily(pool, day_seed + tier)
        unit = max(1, item.price.npcBuyPrice)
        target = tier_target[tier] * (1 + (item.demand.marketPressure or 0) / 200)
        target = clamp(target, 100_000, 600_000)
        qty = round(target / unit)
        qty = clamp(qty, min_qty[tier], max_qty[tier])
        qty = min(qty, MAX_WEIGHT // max(1, item.weight))
        payout = round(unit * qty * 1.20)
        payout = clamp(payout, 50_000, 1_500_000)
        result.append({"tier": tier, "item": item, "qty": qty, "payout": payout})
    return result
```

La selección diaria debe ser determinista por cuenta/día o global/día; decidir antes de implementar.

---

## 6. Migración

1. Mantener `trasher.txt` actual hasta que el exportador v2 esté listo.
2. Generar `market_master` completo.
3. Generar arrays de Garrett desde el master:
   - ofertas: item + `npcBuyPrice`;
   - misiones: item + qty + payout;
   - pools ya filtrados.
4. Mantener variables `#GARRETT_*` para no perder:
   - día,
   - ofertas vendidas,
   - presupuesto gastado,
   - misión activa,
   - historial.
5. Validar con `analyze_garrett.py`:
   - oferta nueva ≤ oferta vieja en items fáciles;
   - misión nueva ≤ 1,5x `npcBuyPrice * qty`;
   - ninguna misión con piso 500k para item trivial;
   - ningún item de instancia/boss/high-HP en el pool.

---

## 7. Validación propuesta

- [ ] 0 misiones con ratio `payout / (npcBuyPrice * qty) > 1,5`.
- [ ] 0 ofertas con ratio `price / npcBuyPrice > 1,2`.
- [ ] 0 items `instance_only`, `guild_only`, `boss_only`, `high_hp` en ofertas/misiones.
- [ ] 0 items `group_only` en misiones.
- [ ] 100% de los pagos dentro de `[50k, 1.5M]`.
- [ ] Cap diario de 500k respetado.
- [ ] Cantidad dentro de `minQty/maxQty` y cap de peso.
- [ ] Anti-arbitraje contra NPC shop activo.
- [ ] Comparación legacy vs v2 documentada en `garrett_comparison.md`.

---

## 8. Decisiones pendientes

1. `tierTarget` definitivo (200k/350k/500k).
2. `minQty`/`maxQty` por tier.
3. `missionMultiplier` 1,20 vs 1,25/1,30.
4. Selección diaria global o por cuenta.
5. Mantener 5 ofertas o reducir a 3.
6. Pago de misiones por item o por paquete.
7. Uso de `marketPressure` para ajustar cantidad o solo para stock.
8. Multiplicador histórico por NPC (futuro).

---

## 9. Conclusión

El problema de Garrett no es solo el precio: es que el pago no está atado al esfuerzo ni al valor canónico. La v2 permite reemplazar tiers viejos por:

```
precio = npcBuyPrice
cantidad = targetPayout / npcBuyPrice
payout = cantidad * npcBuyPrice * 1,2
```

Eso corrige el caso de items fáciles pagados a 600k: o sube mucho la cantidad, o baja el pago. Y deja el sistema listo para un multiplicador histórico por NPC sin cambiar la base.
