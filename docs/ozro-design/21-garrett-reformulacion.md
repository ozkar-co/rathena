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
offerPrice = npcBuyPrice * 2.00
if item is npc_shop:
    offerPrice = min(offerPrice, npcSellToPlayer * 0.90)
offerPrice = max(500, offerPrice)
```

El multiplicador 2,00 es el “Garrett paga el doble” del lore. El único cap es la tienda NPC, para evitar arbitraje.

Opcional futuro: multiplicador histórico por NPC, como dice el diseño:

```
offerPrice *= npcHistoryMultiplier
```

La base sigue siendo la fórmula canónica v2.

### 4.3 Blacklist

Además de los filtros de acceso, se excluyen:

- `type == "Card"`: todas las cartas.
- `abundanceTier in {scarce, rare}`: demasiado raras.
- Items usados por NPCs custom repetibles de `npc/custom/ozro/repeteables/`: 15 IDs detectados por `delitem`/`countitem`/`getitem`.

El blacklist se aplica a ofertas y misiones.

### 4.4 Pool de misiones

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

### 4.5 Cantidad y pago

La cantidad sale de un **pago objetivo**, no de un mínimo fijo.

```
unit = offerPrice
targetPayout = tierTarget[tier] * (1 + demandPercentile / 200)
targetPayout = clamp(targetPayout, 300_000, 1_500_000)

qty = round(targetPayout / max(1, unit))
qty = clamp(qty, minQty[tier], maxQty[tier])
qty = min(qty, floor(MAX_MISSION_WEIGHT / max(1, weight)))

payout = max(1_000, round(unit * qty * 1.00))
payout = min(payout, 1_500_000)
```

Valores de la propuesta:

| Tier | `tierTarget` | `minQty` | `maxQty` |
|---|---:|---:|---:|
| Común | 800.000 | 20 | 300 |
| Poco común | 1.050.000 | 10 | 200 |
| Raro | 1.300.000 | 5 | 100 |

`missionMultiplier`: 1,00.
`MAX_MISSION_WEIGHT`: 5.000.
No hay piso de 500k.

Resultado de la propuesta generada:

| Métrica | Valor |
|---|---:|
| Misiones | 40 |
| Payout promedio | 947.425 |
| Payout mínimo | 780.000 |
| Payout máximo | 1.150.000 |
| Cantidad mínima | 11 |
| Cantidad máxima | 300 |
| Ratio promedio `payout / (npcBuy × qty)` | 1,986 |
| Misiones limitadas por peso | 7 |

Efecto:

- Item fácil y barato: `qty` sube hasta el cap y el pago queda bajo.
- Item caro: `qty` baja y el pago se acerca al objetivo.
- Item de instancia/boss/high-HP: no entra.
- Nunca se paga el piso de 500k por un item trivial.

### 4.6 Entregas parciales y fracaso

Las misiones pueden requerir cantidades grandes, así que se permite entregar por partes:

```
#GARRETT_MISSION_DELIVERED += cantidad_entregada
delitem item, cantidad_entregada
```

Reglas:

- El pago se entrega solo al completar `quantity`.
- Si el jugador entrega parcialmente y no completa antes de `#GARRETT_MISSION_END`, los items entregados se pierden.
- No hay devolución ni pago parcial.
- La misión se cancela/resetea y no hay otra hasta el día siguiente.
- El contador `DELIVERED` se incrementa solo después de un `delitem` exitoso.
- Al completar, se verifica `DELIVERED >= quantity` y se resetea.

Esto es el “precio de hacer tratos con Garrett”.

### 4.7 Tabla fija, sin generación dinámica

La tabla se genera una vez y se deja fija en el NPC:

- `propose_garrett.py` genera `garrett_proposal.json`, `.md` y `ozro-site/assets/items/garrett.json`.
- El NPC usa arrays fijos generados desde esa tabla.
- No hay selección aleatoria diaria de items.
- El cronograma puede ser fijo: 40 misiones y 200 ofertas siempre disponibles según diseño.

### 4.8 Anti-arbitraje

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

### 4.9 Frecuencia y stock

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
        target = tier_target[tier] * (1 + (item.demand.percentile or 50) / 200)
        target = clamp(target, 300_000, 1_500_000)
        qty = round(target / unit)
        qty = clamp(qty, min_qty[tier], max_qty[tier])
        qty = min(qty, MAX_WEIGHT // max(1, item.weight))
        payout = min(1_500_000, max(1_000, round(unit * qty * 1.00)))
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

## 7. Tabla de revisión

Generada por `tools/market/propose_garrett.py`:

- `data/market/samples/garrett_proposal.json`: datos completos.
- `data/market/samples/garrett_proposal.md`: tabla legible.

El JSON de la web es `ozro-site/assets/items/garrett.json`.

Columnas de misión:

```
tier, item, quantity, canonicalBuy, garrettUnit, payout, canonicalBuyValue,
abundance, difficulty, mob, mobHp, mobLevel, map, spawnAmount, dropRate,
partialDelivery, forfeitOnFail
```

Columnas de oferta:

```
item, canonicalBuy, garrettBuy, mid, abundance, demand, mob, mobHp,
mobLevel, map, spawnAmount, dropRate
```

## 8. Validación propuesta

- [ ] 0 misiones con ratio `payout / (npcBuyPrice * qty) > 1,5`.
- [ ] 0 ofertas con ratio `price / npcBuyPrice > 1,2`.
- [ ] 0 items `instance_only`, `guild_only`, `boss_only`, `high_hp` en ofertas/misiones.
- [ ] 0 items `group_only` en misiones.
- [ ] Payout promedio entre 0,9M y 1,1M.
- [ ] 100% de los pagos dentro de `[1k, 1.5M]`.
- [ ] 40 misiones / 200 ofertas fijas.
- [ ] Cap diario de 500k respetado.
- [ ] Cantidad dentro de `minQty/maxQty` y cap de peso.
- [ ] Anti-arbitraje contra NPC shop activo.
- [ ] Comparación legacy vs v2 documentada en `garrett_comparison.md`.
- [ ] Tabla de revisión generada en `garrett_proposal.md`.
- [ ] Entregas parciales y pérdida por fracaso documentadas.

---

## 9. Decisiones pendientes

1. `tierTarget` definitivo (800k/1.05M/1.3M).
2. `minQty`/`maxQty` por tier (20/10/5 y 1000/500/200).
3. `missionMultiplier` 1,00.
4. Tabla fija: 40 misiones y 200 ofertas.
5. Entregas parciales y pérdida total por fracaso.
6. Pago de misiones por item o por paquete.
7. Uso de `marketPressure` para ajustar cantidad o solo para stock.
8. Multiplicador histórico por NPC (futuro).

---

## 10. Conclusión

El problema de Garrett no es solo el precio: es que el pago no está atado al esfuerzo ni al valor canónico. La v2 permite reemplazar tiers viejos por:

```
precio = npcBuyPrice
cantidad = targetPayout / npcBuyPrice
payout = cantidad * npcBuyPrice * 1,00
```

Eso corrige el caso de items fáciles pagados a 600k: o sube mucho la cantidad, o baja el pago. Y deja el sistema listo para un multiplicador histórico por NPC sin cambiar la base.
