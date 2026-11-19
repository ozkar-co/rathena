# Respuesta al brief: Mercado de OzRo

## Diagnóstico en una frase

El modelo no falla por los coeficientes sino por la arquitectura. Hay dos regímenes que no se hablan (historial puntual vs. prior de tipo) y un montón de multiplicadores en unidades distintas. La corrección es **un solo modelo jerárquico en log-precio**, con una prior estructural (costo de adquisición) y la evidencia histórica entrando como verosimilitud con su incertidumbre. Los booleanos se reemplazan por ejes y probabilidades.

---

## 1. Arquitectura propuesta

```
[Ingesta + tests] → [Ontología 3 ejes] → [Rutas y costos (horas)] → [Prior estructural en log-precio]
                                                                          ↓
                         [Evidencia LATAM/Atlantis: verosimilitud robusta] → [Posterior (μ, σ) por item]
                                                                          ↓
                                  [Proyección de restricciones: monotonía, cajas, sustitutos] → p10/p50/p90 + procedencia
                                                                          ↓
                                                        [Precio NPC (regla de sumidero, aparte)]
```

**Unidad común: horas-jugador equivalentes**, convertidas a zeny con un único parámetro global `w` (zeny/hora). Cada ruta se expresa en horas:

- **Drop**: `H = t_kill_efectivo / p_drop_efectivo` (más viaje y riesgo del mapa), con `t_kill` derivado de HP efectivo, DEF/MDEF y un DPS de referencia por nivel.
- **Time gate**: si el flujo global (`spawns/h × p_drop`) es bajo, el precio lo fija la demanda, no el esfuerzo individual. Por eso `H_eff = max(H_esfuerzo, H_flujo)`, con `H_flujo ≈ N_ref / flujo_global`. Aquí GTB (1/h) e Ifrit (1/11h) se separan solos.
- **Quest / instancia**: horas fijas + zeny de entrada, valorando los insumos a su precio de mercado (grafo).
- **Craft**: `(Σ insumos + tasa + horas·w) / p_éxito`, con el item base consumido si el upgrade es destructivo.
- **Caja / grupo**: `precio_caja = Σ pₖ·vₖ`. Es un sistema subdeterminado, así que se usa como restricción más un reparto con vₖ creciente en 1/pₖ, no como fuente de precio puntual.
- **Tienda NPC**: precio conocido y **techo duro** (nadie paga en mercado más que el NPC, salvo conveniencia).

Costo del item: `C_i = softmin_r C_r`. Se usa softmin y no min porque no todos los jugadores acceden a todas las rutas.

**Prior en log-precio:**

```
log p_i ~ N( log w + log C_i + β·x_i + u_{tipo/subtipo},  σ_prior² )
```

`x_i` son features: nivel, slots, tier de utilidad, número de consumidores del item en recetas/quests (esto separa Jellopy de materiales valiosos), precio NPC, etc. **β y w se estiman con regresión robusta sobre los ~5.8k items con evidencia sólida**, no se fijan a mano. Eso elimina el acantilado: todos los items tienen prior, y la evidencia solo la desplaza.

**Sesgo de supervivencia (importante):** los items con historial son los que se comercian, que tienden a ser más caros y populares. Si entrenas la prior solo con ellos y la aplicas a los 23k sin historial, la sesgas al alza. Hay que modelar P(tener ventas | features) y ensanchar σ_prior para los items sin evidencia.

---

## 2. Respuestas a las 10 preguntas

**1. ¿Es el costo esperado la primitiva correcta?** Sí, pero como **ancla y techo de arbitraje**, no como precio exacto. Si el precio de mercado supera el costo de la ruta más barata, la oferta se expande. Pero en regímenes flow-limited o de utilidad muy alta, el precio puede superar el costo. De ahí `max(esfuerzo, flujo)` y la verosimilitud histórica. El costo de oportunidad `w` no se conoce a priori y se **estima por calibración**: la pendiente de log(precio histórico) contra log(horas de ruta). Con la economía desconocida, la evidencia de los otros servidores sirve sobre todo para la **estructura relativa** (qué cuesta más que qué). El nivel absoluto es una decisión de diseño de tu servidor (inflación objetivo), con rates custom que modifican los drop efectivos.

**2. Items sin mercado ni ruta: "sin precio" es una salida válida, y debe ser de primera clase.** Tres estados:
- `priced`: con (p10, p50, p90).
- `wide_band`: poca información, banda ancha y marcada.
- `unpriced(reason)`: `legacy_no_evidence`, `event_no_evidence`, `no_transfer`, `source_unparsed`. El simulador simplemente no lo lista.

Inventar un precio para un item que nadie puede obtener es peor que no tenerlo.

**3. Combinar dos servidores con desacuerdos de 20x.** Modelo en log-espacio:

`log p_{i,s} = μ_i + b_s(tipo) + ε`, con `Var(ε) = σ_s²/n_{i,s} + τ²`.

- `b_s` es el offset del servidor (se estima con items que están en ambos).
- Verosimilitud **Student-t** o mezcla de dos componentes, no gaussiana, por los 898 desacuerdos >2x.
- Cada fuente se pondera por n de **ventas** (no por mediana de ofertas: las ofertas son asks, sesgadas al alza).
- **La prior estructural arbitra**: en Menblatt (1.5M vs 30M), la mezcla le da más peso a la componente más consistente con la dificultad real del mob. Si ninguna es consistente, se etiqueta `disputed` y la banda se ensancha.
- Regla de rechazo: n < 3 en una fuente la deja casi sin peso.

**4. Demanda con datos censurados.** No se estima demanda por item con 0–2 ventas. Se usa un modelo Poisson/Binomial Negativa jerárquico con pooling parcial por (tipo, subtipo, banda de precio). El posterior Gamma(α+n, β+T) da la tasa de venta, y `n=0` significa "tasa baja, incierta", no "demanda cero". La señal útil no es el residual de ventas sino el **sell-through** (ventas / flujo de oferta). Su efecto sobre el precio se estima dentro de la regresión, sin topes ±25% manuales.

**5. Upgrade destructivo y circularidad.** Para Pantie[1] (5%, consume la base, 1M + Elunium):

`P_up = (P_base + tasa + P_Elunium) / 0.05`

Es un **DAG** (el base no depende del upgrade), así que se resuelve en orden topológico, no es punto fijo. Si hay ciclos (A→B→A), se detectan como componentes fuertemente conexas y se resuelven con iteración amortiguada en log-espacio. La incertidumbre del base se propaga por Monte Carlo lognormal, lo que da p10/p90 del upgrade gratis. Ojo: con esta fórmula Pantie[1] ronda 20M solo si el base es barato. Es la fórmula la que debe producir ese número, no un parche.

**6. Complementos y sustitutos.** No modeles un sistema de equilibrio general. Usa restricciones en una pasada final de proyección:
- Gear con slots: `p(n slots) = p(0) + prima_slot`, con la prima acotada por precios típicos de cartas de esa clase.
- Refine: cadena de Markov absorbente con tasas conocidas (computable exacto).
- Sustitutos: `p ≤ p(sustituto más barato) + fricción`.
- Cajas: consistencia con el valor esperado.

**7. Salida: distribución, no banda simétrica.** Lognormal (μ, σ) por item, publicando **p10/p50/p90**. En zeny queda asimétrica a la derecha, como los datos reales. Para `disputed`, guarda ambos modos. El simulador usa p50 como mid y la banda para su ruido.

**8. Validación sin ground truth.**
- *Out-of-sample*: oculta items con n>50 y mide el error de la prior sola (mediana |log error|, cobertura p10–p90 ≈ 80%). Haz también leave-one-server-out.
- *Invariantes* (property tests): ruta más rara/cara ⇒ precio ≥ (salvo demanda); upgrade ≥ base; `NoSell ⇒ npc_buy = null`; mercado ≤ precio NPC de tienda; EV(caja) ≈ precio caja.
- *Estrés*: perturba `w` ±50% y las rates ±; el ranking (Spearman) debe ser estable.
- *Tests ordinales amplios*, no de precio: 50–100 pares (GTB > Frilldora > Jellopy…) etiquetados por alguien que conozca el juego, **separados** de los 6 casos del brief para no hacer overfitting.
- *Ingesta*: assertions (el loader debe fusionar, no sobrescribir; conteo de mobs; items canarios).

**9. División fórmula / manual / LLM.**
- **Determinista**: ingesta, ontología, costos, grafo, Bayes, proyección, precio NPC, invariantes.
- **Manual (pocos parámetros, versionados)**: `w`, el nivel objetivo de la economía y un archivo de overrides con motivo, autor y vencimiento.
- **LLM (solo extractor/clasificador, nunca precios)**: (a) extraer rutas de adquisición desde scripts y textos de quests de los ~18k items sin fuente parseada, con salida JSON y cita de la línea fuente, verificada con reglas; (b) tier de utilidad 1–5 de cartas y equipo, con justificación; (c) legacy/event/removed cuando el texto lo permita. Temperatura 0, prompt y versión registrados, resultados en un `.jsonl` versionado.

**10. Con 2–5 USD y una corrida.** Orden:
1. Arreglar la ingesta (merge de mob_db, `alb_ship`, spawns de GTB/Ifrit) con tests. Sin esto nada es fiable.
2. Ontología de 3 ejes y definiciones corregidas.
3. Grafo de rutas y costos, y la regresión para `w` y β.
4. Combinación bayesiana de fuentes y salida en distribución.
5. Con el LLM, solo el extractor de rutas (a) y el tier (b), priorizando los items con mayor incertidumbre.

**Dejaría sin resolver explícitamente:** el nivel absoluto de la economía (se descubre con telemetría real), la demanda real de items de baja rotación, la sustituibilidad fina entre cartas y los items legacy sin evidencia (quedan `unpriced`).

---

## 3. Sobre el punto P6 (ontología)

Tu hipótesis es correcta. Las definiciones concretas:

- **Transferencia**: solo `NoTrade` bloquea el comercio entre jugadores. `NoDrop`, `NoSell`, `NoStorage`, `NoMail`, `NoCart` y `NoAuction` son canales con efecto en **liquidez** (un factor de descuento por canal, estimable de los datos).
- **Los 68 items con historial y solo NoDrop/NoSell deben entrar al mercado.** Bouquet es el caso.
- **Adquisición**: un conjunto de rutas con costo, más un estado de cobertura (`parsed`, `unparsed`, `legacy`, `event`, `none`). `unobtainable` pasa a ser `source_unparsed` o `none_verified`, que son cosas distintas.
- **Mercado**: derivado (`active`, `legacy`, `not_traded`) de evidencia de ventas + transferencia, no al revés.

**Precio NPC.** En rAthena, el NPC compra al `Sell` del item. Que 4,434 items NoSell reciban un precio mayor es un bug. Si tu "NPC tasador" es un sumidero **custom** que paga un porcentaje del mercado, déjalo explícito y blíndalo: paga sobre **p10** (no p50), con spread, límite diario por item y cuenta, y nunca para items con banda ancha o `disputed`. Si no, un mid ruidoso crea un generador de zeny arbitrable.

---

## 4. Cómo se comportarían tus casos

| Caso | Mecanismo en el nuevo diseño |
|---|---|
| Menblatt vs Frilldora | La prior de dificultad arbitra los 20x entre fuentes. Probablemente Menblatt > Frilldora, con banda ancha y `disputed` si no cuadra |
| Monster Coin | `is_ingredient=0` y consumidores=0, junto con tier bajo y flujo alto, lo mandan a la cola baja; NPC ≈ Sell |
| GTB / Ifrit | Time gate y `H_flujo` altos, tras corregir la ingesta; Ifrit > GTB solo si su gate es peor y la demanda lo permite |
| Pantie[1] | Costo destructivo por DAG, ≈ 20M |
| Ice Pick[1] | 2 ventas ⇒ peso casi nulo; banda ancha centrada por la prior, no por 650M |
| 80 cartas a 500k | Desaparece el valor por defecto; cada una recibe su propia prior o `wide_band` |

