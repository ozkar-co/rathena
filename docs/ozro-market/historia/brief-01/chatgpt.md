# Revisión externa del sistema de valoración de OzRo
**Dictamen técnico y propuesta de rediseño**

## 1. Dictamen ejecutivo

Después de revisar el brief, mi conclusión es que el problema de OzRo no consiste principalmente en encontrar mejores multiplicadores para calcular precios. El problema es que el sistema actual intenta representar fenómenos económicos diferentes mediante una única fórmula que mezcla variables de naturaleza distinta.

Actualmente se combinan:
- Referencias de precios de otros servidores.
- Cantidad y frecuencia de aparición de monstruos.
- Probabilidad de obtención de objetos.
- Dificultad de los monstruos.
- Indicadores indirectos de demanda.
- Percentiles generales por categoría.
- Restricciones de comercio y adquisición.

El resultado es un sistema que puede producir cifras matemáticamente válidas, pero económicamente absurdas.

Los casos de Monster Coin, Golden Thief Bug Card, Ifrit Card y Pantie[1] ilustran cuatro fallos distintos: clasificación incorrecta de objetos, pérdida de información de adquisición, ausencia de costos de oportunidad y falta de tratamiento de procesos destructivos.

El problema más serio es que actualmente el modelo no distingue adecuadamente entre:

1. **Cuánto cuesta conseguir un objeto.**
2. **Cuánto está dispuesto a pagar un jugador por él.**
3. **Qué tan fácil es convertirlo en dinero mediante una venta.**
4. **Cuánta confianza tenemos en la estimación.**

Son cuatro preguntas diferentes y necesitan modelos diferentes.

### Mi recomendación principal

Abandonaría el modelo de precio basado en una referencia inicial corregida mediante multiplicadores y lo reemplazaría por un sistema de valoración compuesto por cinco capas independientes:

| Capa | Responsabilidad | Resultado |
|---|---|---|
| 1. Procedencia | Determinar qué sabemos del objeto y de sus fuentes | Datos confiables y rutas identificadas |
| 2. Adquisición | Estimar el costo económico de conseguirlo | Costo de reposición |
| 3. Mercado | Estimar cuánto se paga por él | Distribución de precios |
| 4. Elegibilidad y liquidez | Determinar dónde puede venderse y con qué restricciones | Estado comercial |
| 5. Decisión | Combinar evidencia, incertidumbre y reglas de seguridad | Precio low/mid/high o sin precio |

El punto fundamental es que el costo de adquisición no debe convertirse directamente en precio de mercado. Es un ancla económica, no una verdad comercial.

Un objeto puede costar 20 millones en recursos para producirse y tener un precio de mercado de 12 millones porque nadie lo necesita. También puede costar 100.000 zeny conseguirlo y venderse por 50 millones porque su demanda es extraordinariamente alta.

**El modelo debe permitir ambos resultados.**

---

## 2. Diagnóstico: qué problemas deben resolverse y en qué orden

El brief identifica seis problemas metodológicos y un problema de calidad de datos. Mi evaluación de prioridades es la siguiente:

| Problema | Gravedad | Prioridad |
|---|---|---|
| Corrupción o pérdida de datos de mobs | Crítica | P0 |
| Confusión entre transferencia y restricciones NPC | Crítica | P0 |
| Ausencia de costo de adquisición | Muy alta | P1 |
| Uso de percentiles generales por tipo | Muy alta | P1 |
| Uso de referencias históricas sin ponderar confianza | Muy alta | P1 |
| Tratamiento de oferta cero como neutral | Alta | P1 |
| Modelo de demanda insuficiente | Alta | P2 |
| Ausencia de incertidumbre explícita | Alta | P2 |

No recomiendo invertir tiempo en optimizar la fórmula actual antes de solucionar P0.

Un modelo estadístico sofisticado no puede compensar datos de entrada incorrectos. El caso del GTB es especialmente ilustrativo: si la ingesta reemplaza los atributos reales del monstruo por los de una versión de evento, cualquier cálculo posterior de rareza estará equivocado.

La primera regla de ingeniería debería ser:

> Ningún precio puede tener una confianza superior a la confianza de sus datos de procedencia.

## 3. La primitiva correcta: costo esperado de adquisición

### 3.1. Mi respuesta: sí, pero con una precisión importante

El costo esperado de adquisición es una excelente variable fundamental para el modelo, porque permite comparar rutas de obtención completamente diferentes utilizando una unidad común: zeny.

Sin embargo, hay que distinguir entre:

- Costo directo: cuánto zeny se gasta.
- Costo temporal: cuánto tiempo se invierte.
- Costo de oportunidad: cuánto se deja de ganar realizando otra actividad.
- Costo de riesgo: cuánto se pierde por probabilidades de fracaso.
- Costo de acceso: cuánto cuesta llegar a una actividad o desbloquearla.

La fórmula general que propongo es:

\[
C_{i,r}=\frac{C_{directo,r}+V_h\cdot T_r}{E[Q_{i,r}]}
\]

Donde:

- \(i\): objeto.
- \(r\): ruta de adquisición.
- \(C_{directo,r}\): costo en zeny por intento.
- \(V_h\): valor económico de una hora de juego.
- \(T_r\): tiempo invertido por intento, expresado en horas.
- \(E[Q_{i,r}]\): cantidad esperada del objeto por intento.

El resultado es el costo económico esperado por unidad adquirida.

La fórmula supone intentos repetibles y un costo promedio por intento. En procesos con resultados y consumos diferentes según el éxito o fracaso, debe calcularse el costo esperado de todo el proceso hasta obtener una unidad.

### 3.2. Cómo aplicarlo a cada tipo de adquisición

**A. Farming de monstruos**

Para un objeto obtenido mediante drop:

\[
C_i=\frac{C_{kill}+V_h\cdot T_{kill}}{P_{drop}}
\]

Esta expresión debe incluir el tiempo de desplazamiento y acceso, distribuido entre los intentos correspondientes.

La probabilidad de drop debe ser la probabilidad efectiva después de aplicar las reglas reales del servidor.

Hay una distinción importante: el HP del monstruo no determina directamente el costo del objeto. Determina parte del tiempo necesario para matarlo.

Por eso no utilizaría HP como multiplicador directo del precio. Lo utilizaría para estimar tiempo de combate, usando perfiles representativos de jugadores.

Además, el ritmo de obtención debe respetar la disponibilidad real de monstruos:

\[
K_{efectivo}=\min(K_{jugador},K_{spawn})
\]

Y:

\[
Producción_i=K_{efectivo}\cdot P_{drop}
\]

Para un monstruo con 25 apariciones y un respawn de 60 segundos, existe una capacidad de aparición diferente a la de un MVP que aparece una vez cada once horas.

Esta diferencia debe reflejarse en el costo de adquisición, no mediante un multiplicador arbitrario.

**B. Procesos destructivos**

El caso de Pantie[1] es especialmente importante.

Supongamos que:
- La probabilidad de éxito es 5%.
- Se consume una Pantie por intento.
- Se consume 1 Elunium por intento.
- Se gastan 1 millón de zeny por intento.
- Los materiales se pierden también cuando falla.

El número esperado de intentos hasta conseguir un éxito es:

\[
E[N]=\frac{1}{0.05}=20
\]

Por tanto:

\[
C_{\text{Pantie[1]}}=
20(C_{\text{Pantie}}+C_{\text{Elunium}}+1M)
\]

Esto es conceptualmente correcto y explica por qué un objeto producido mediante una transformación destructiva no puede valorarse únicamente por su dificultad de obtención original.

Hay que tener especial cuidado con los casos donde algunos materiales se conservan al fracasar. En ese escenario, no debe multiplicarse indiscriminadamente todo por \(1/p\). Hay que calcular el consumo esperado de cada componente según las reglas del proceso.

**C. Cajas y grupos**

Si una caja cuesta \(C_b\) y tiene una probabilidad \(p_i\) de entregar el objeto:

\[
C_i=\frac{C_b}{p_i}
\]

Esto es válido cuando cada intento produce como máximo una unidad del objeto y todos los intentos tienen el mismo costo.

Si existen múltiples resultados, probabilidades dependientes o recompensas simultáneas, se utiliza la distribución completa de resultados.

**D. Quests**

El costo de una quest debe incluir:

- Materiales entregados.
- Zeny requerido.
- Tiempo de ejecución.
- Prerrequisitos.
- Cooldowns.
- Número máximo de repeticiones.
- Probabilidad de éxito, cuando exista.

Una quest que entrega un objeto cada tres horas tiene una capacidad de producción completamente diferente de una quest repetible sin límite.

**E. Objetos de NPC y Cash Shop**

También deben constituir rutas de adquisición independientes.

Una ruta de NPC tiene un costo monetario conocido, mientras que una ruta Cash debe incluir el costo de la moneda o mecanismo real que utiliza el servidor.

No se deben inventar equivalencias entre dinero real, puntos Cash y zeny cuando no existe una tasa de conversión observable.

### 3.3. El problema de calcular el valor de una hora

Esta es una de las preguntas más importantes del brief.

¿Cómo estimar el costo de oportunidad si desconocemos la economía del servidor?

Mi respuesta es que no podemos identificarlo con precisión utilizando únicamente item_db y mob_db.

El valor de una hora de juego depende de la capacidad del jugador, el equipo, la clase, el contenido disponible y la economía.

Intentar obtener un único valor exacto desde los atributos de los monstruos sería introducir una falsa precisión.

Propongo tres escenarios configurables:

| Escenario | Interpretación |
|---|---|
| Conservador | Jugador poco optimizado, baja capacidad de generación |
| Medio | Jugador representativo del contenido |
| Optimizado | Jugador eficiente, equipo adecuado y ruta optimizada |

Cada escenario tiene un \(V_h\) distinto.

Inicialmente utilizaría parámetros configurables, no estimaciones pretendidamente exactas.

Cuando OzRo tenga información propia, se podrán calibrar usando actividades de referencia con ganancias netas observadas por hora.

Esto permite que el mismo objeto tenga un costo de adquisición expresado como intervalo.

Por ejemplo:

\[
C_{adq}=[P10,P50,P90]
\]

No es necesario que estos valores sean simétricos.

### 3.4. Una consideración económica fundamental

El costo de adquisición no representa necesariamente un precio mínimo de mercado.

Este punto es crítico.

Supongamos que producir un objeto cuesta 20 millones, pero los jugadores solo están dispuestos a pagar 12 millones.

El precio de mercado puede ser 12 millones.

Los jugadores pueden estar liquidando inventarios, abandonando una actividad o vendiendo por debajo de su costo de reposición.

Por tanto, recomiendo almacenar dos magnitudes independientes:

`replacement_cost`: costo económico esperado de reemplazar el objeto.

`market_price`: estimación del precio al que realmente puede comercializarse.

La primera explica la economía de producción. La segunda representa el comportamiento del mercado.

No impondría:

\[
MarketPrice\geq ReplacementCost
\]

como una restricción obligatoria.

Sí utilizaría las diferencias entre ambas para detectar oportunidades de arbitraje, cambios de oferta, desabastecimiento o anomalías.

---

## 4. Nueva ontología: adquisición, transferencia y mercado

Coincido plenamente con la hipótesis formulada en el brief: el problema principal es haber convertido propiedades independientes en booleanos que luego se utilizan para tomar decisiones económicas.

La propuesta de separar tres ejes es correcta y recomiendo adoptarla.

Hay que desarrollarla un poco más.

### 4.1. Eje de adquisición

En lugar de `obtainable = true/false`, utilizaría un conjunto de rutas:

| Estado | Significado |
|---|---|
| farmed | Drop de monstruo |
| crafted | Fabricación |
| quested | Obtención por quest |
| group | Caja o grupo |
| npc | Compra mediante NPC |
| cash | Tienda Cash |
| event | Evento |
| legacy | Fuente histórica actualmente retirada |
| unknown | No se conoce suficientemente la procedencia |
| none | No existe una ruta disponible identificada y confirmada |

Un objeto puede tener varias rutas simultáneamente.

Por ejemplo, puede obtenerse mediante drop y también mediante una caja.

Cada ruta tendrá su costo, probabilidad y disponibilidad.

Es especialmente importante diferenciar `unknown` de `none`.

Que el parser no haya encontrado una fuente no demuestra que no exista.

Esta distinción responde directamente al problema de los 18.319 objetos identificados actualmente como unobtainable. Texto pegado

### 4.2. Eje de transferencia

Aquí deben representarse los canales independientes:

| Propiedad | Significado |
|---|---|
| player_trade | Intercambio entre jugadores |
| npc_sell | Posibilidad de vender al NPC |
| npc_buy | Posibilidad de comprar al NPC |
| drop_allowed | Puede tirarse al suelo |
| storage_allowed | Puede guardarse |
| cart_allowed | Puede introducirse en carro |
| mail_allowed | Puede enviarse por correo |
| auction_allowed | Puede entrar en subastas |
| bound_scope | Alcance de la vinculación |

No recomendaría reducir este eje a un booleano.

Hay una confirmación importante en la documentación oficial de rAthena: `NoDrop`, `NoTrade`, `NoSell`, `NoStorage`, `NoMail`, `NoCart` y `NoAuction` representan restricciones diferentes. En particular, `NoSell` se refiere a la venta a NPC, no a la transferencia entre jugadores. [GitHub](https://github.com/rathena/rathena/blob/master/doc/item_db.txt?utm_source=chatgpt.com)

También existen niveles de override asociados a las restricciones, por lo que el cálculo de elegibilidad debe considerar el comportamiento efectivo de la configuración del servidor, no solamente el valor booleano almacenado.

### 4.3. Eje de mercado

Utilizaría los siguientes estados:

| Estado | Interpretación |
|---|---|
| active | Existe evidencia reciente de comercialización |
| thin | Existen operaciones, pero son escasas |
| stale | Hay referencias históricas antiguas |
| no_evidence | No tenemos evidencia suficiente |
| not_traded | El objeto no tiene un canal efectivo de intercambio entre jugadores |

El estado de mercado debe derivarse de la evidencia y las restricciones efectivas.

No debe determinarse simplemente porque exista una ruta de obtención.

Un objeto puede obtenerse fácilmente y no tener demanda.

También puede no tener ninguna fuente de adquisición actual, pero existir un mercado de inventarios antiguos.

### 4.4. Una corrección importante a los criterios de éxito

El brief establece que ningún objeto con ventas históricas debe quedar fuera del mercado por un booleano.

Estoy de acuerdo con el objetivo de eliminar las exclusiones incorrectas, pero existe una excepción lógica que hay que reconocer.

Si un objeto tiene realmente `NoTrade = true` en OzRo y esa restricción está activa para todos los jugadores, no existe un mercado de intercambio entre jugadores, aunque haya tenido ventas en Atlantis o LATAM.

Esas ventas históricas siguen siendo evidencia válida sobre otros servidores, pero no demuestran que pueda comercializarse actualmente en OzRo.

Reformularía el criterio así:

> Ningún objeto con ventas históricas puede perder su evidencia comercial por una clasificación incorrecta. La elegibilidad del mercado de OzRo debe determinarse exclusivamente mediante sus canales efectivos de transferencia.

Esto preserva tanto la información histórica como la realidad de las reglas del servidor.

---

## 5. Cómo calcular precios utilizando referencias históricas

Considero que este es el segundo componente más importante después del costo de adquisición.

El modelo actual trata una referencia histórica como una verdad puntual.

Eso debe cambiar.

Una observación de dos ventas a 650 millones no equivale a una estimación confiable de 650 millones.

Tampoco dos servidores que ofrecen precios muy diferentes deben resolverse seleccionando silenciosamente uno de ellos.

### 5.1. Trabajar en escala logarítmica

Los precios de Ragnarok tienen distribuciones muy asimétricas.

En un catálogo pueden convivir objetos de 500 zeny con objetos de cientos de millones.

Trabajar directamente con precios absolutos hace que los objetos más caros dominen numerosos cálculos.

Recomiendo transformar los precios:

\[
y=\ln(P)
\]

Esto permite:

- Comparar diferencias relativas.
- Reducir la influencia de valores extremos.
- Combinar fuentes mediante medias geométricas ponderadas.
- Construir intervalos de incertidumbre más naturales.

### 5.2. Incorporar confianza por fuente

Cada observación histórica debería tener:

- Servidor de origen.
- Precio.
- Número de operaciones.
- Fecha.
- Tipo de evidencia.
- Calidad de la muestra.
- Desacuerdo frente a otras fuentes.

Propongo un modelo de ponderación:

\[
w_s=
f(n_{efectivo},recencia,calidad)
\]

Como implementación inicial:

\[
w_s=
\frac{n}{n+k}
\cdot e^{-\lambda t}
\cdot q_s
\]

Donde:

- \(n\): cantidad de ventas.
- \(k\): parámetro de regularización.
- \(t\): antigüedad de la observación.
- \(\lambda\): velocidad de pérdida de relevancia.
- \(q_s\): calidad de la fuente.

No fijaría los valores definitivos de \(k\) y \(\lambda\) sin analizar la distribución de los datos.

### 5.3. Combinar servidores con desacuerdos grandes

Mi recomendación es utilizar un modelo jerárquico robusto.

Conceptualmente:

\[
\ln(P_{i,s})=
\mu_i+b_s+\epsilon_{i,s}
\]

Donde:

- \(\mu_i\): valor latente del objeto.
- \(b_s\): sesgo o nivel general de precios del servidor.
- \(\epsilon\): variación propia del objeto y error de observación.

Para evitar que dos ventas extremas distorsionen el resultado, utilizaría una distribución Student-t o un estimador robusto equivalente.

Con solamente dos servidores externos no existe información suficiente para estimar todos los efectos con gran precisión. El modelo debe reconocerlo y conservar la incertidumbre.

Consideremos el caso de Menblatt Card:

LATAM: 1,5 millones.

Atlantis: 30,2 millones.

La diferencia es de aproximadamente 20 veces.

Una media geométrica simple produciría:

\[
P=\sqrt{1.5M\cdot30.2M}
\]

\[
P\approx6.73M
\]

Pero no presentaría 6,73 millones como una valoración confiable.

Lo presentaría como un punto central provisional, con un conflicto entre fuentes extremadamente alto y un intervalo amplio.

También investigaría si las observaciones corresponden a periodos, economías o condiciones comerciales comparables.

**La discrepancia entre fuentes es información. No es ruido que deba eliminarse.**

### 5.4. El caso de Ice Pick[1]

Dos ventas a 650 millones no deberían producir automáticamente un precio de confianza media.

Recomiendo estas categorías operativas iniciales:

| Evidencia | Tratamiento |
|---|---|
| 0 ventas | Sin evidencia transaccional |
| 1-2 ventas | Muestra insuficiente |
| 3-10 ventas | Confianza baja |
| 11-50 ventas | Confianza intermedia |
| Más de 50 ventas | Potencialmente sólida |

Los umbrales son orientativos, no reglas estadísticas universales.

La cantidad de observaciones no es el único criterio. También importan la dispersión, la antigüedad, la independencia de las transacciones y la calidad de los registros.

Para muestras pequeñas no usaría un promedio aritmético.

Utilizaría mediana o estimadores robustos, siempre conservando la dispersión observada.

---

---

## 6. Cómo modelar demanda cuando hay pocas ventas o ninguna

Esta es una cuestión estadística que merece un tratamiento separado.

El modelo actual parece utilizar el residual de ventas respecto a la mediana de una categoría para producir un multiplicador de demanda.

No lo considero suficientemente robusto.

El número de ventas no representa por sí solo la demanda.

Por ejemplo:

- Un objeto puede no venderse porque nadie lo quiere.
- Puede no venderse porque nadie lo está ofreciendo.
- Puede tener compradores, pero estar fuera de su rango de precio.
- Puede tener una oferta muy limitada y, por tanto, pocas transacciones.
- Puede tener un mercado pequeño, pero compradores dispuestos a pagar precios extraordinarios.

Son situaciones distintas.

### 6.1. Separar tres variables

Recomiendo almacenar:

**1. Precio transaccional:** cuánto pagaron realmente los compradores.

**2. Velocidad de comercialización:** cuántas unidades se venden por unidad de tiempo.

**3. Liquidez:** qué tan probable es convertir el objeto en zeny durante un periodo determinado.

Esto permite distinguir un objeto caro y líquido de uno caro que prácticamente nunca encuentra comprador.

### 6.2. El problema de los datos censurados

Supongamos que un objeto no registra ventas durante 30 días.

No podemos concluir que su demanda es cero.

Necesitamos saber cuánto tiempo estuvo efectivamente disponible en el mercado.

Una métrica útil es:

\[
H_i=\frac{Ventas_i}{DíasOferta_i}
\]

Donde los días de oferta representan la exposición efectiva del objeto al mercado.

Una aproximación estadística sencilla consiste en modelar las operaciones mediante un proceso de Poisson:

\[
N_i\sim Poisson(\lambda_i T_i)
\]

Donde:

- \(N_i\): operaciones observadas.
- \(T_i\): tiempo de exposición.
- \(\lambda_i\): velocidad esperada de transacciones.

Esto permite modelar incluso los objetos que tuvieron cero ventas.

Con cero operaciones y una exposición conocida, podemos calcular un límite superior para la tasa probable de ventas.

Como aproximación, el límite superior del 95% para cero eventos es:

\[
\lambda_{95}\approx\frac{3}{T}
\]

Esto es mucho más informativo que asignarle demanda cero.

Pero hay una condición: necesitamos conocer la exposición.

Si solamente tenemos el número de ventas, sin conocer cuánto tiempo estuvo el objeto disponible, la demanda no es identificable correctamente.

En ese caso recomiendo utilizar un prior de su categoría económica, acompañado de incertidumbre elevada.

### 6.3. Prior de demanda

Para los objetos sin suficiente evidencia, utilizaría un modelo jerárquico.

En lugar de:

`Card → demanda promedio de todas las cartas`

Utilizaría categorías progresivamente más específicas:

- Tipo de objeto.
- Función económica.
- Rareza de adquisición.
- Utilidad dentro del juego.
- Compatibilidad con builds.
- Necesidad para recetas y progresión.
- Evidencia de comercialización de objetos similares.

Por ejemplo, una carta MVP y una carta común son ambas cartas, pero no pertenecen a la misma clase económica.

La categoría debe representar una semejanza económica, no solamente una semejanza técnica de `item_db`.

### 6.4. Separar demanda de rareza

Esta separación es fundamental.

Una carta puede ser extremadamente rara y tener poca demanda.

Otra puede ser relativamente accesible y tener mucha demanda.

No utilizaría un único multiplicador de rareza-demanda.

La rareza debe salir del costo y la capacidad de adquisición.

La demanda debe salir del comportamiento de compra y de la utilidad.

Posteriormente se combinan mediante la estimación de mercado.

---

## 7. Objetos complementarios, sustitutos y relaciones económicas

El modelo actual trata cada objeto como una entidad independiente.

Esto es insuficiente para un juego como Ragnarok Online.

La utilidad de un objeto no depende exclusivamente de sus atributos individuales.

Depende de cómo encaja en una configuración.

Propongo crear un grafo de relaciones entre objetos.

### 7.1. Sustitutos

Dos armas pueden cumplir una función similar para una clase.

Si una es considerablemente más económica, puede absorber parte de la demanda de la otra.

Esto significa que el valor de una no es independiente del precio de su sustituto.

Ejemplos:
- Armas de características similares.
- Armaduras con estadísticas equivalentes.
- Cartas que ofrecen bonificaciones comparables.
- Equipamiento que cumple una misma función en una build.

No intentaría resolver todo esto mediante reglas individuales.

Crearía grupos de sustitución y atributos compartidos.

### 7.2. Complementarios

Hay objetos cuyo valor aumenta considerablemente cuando se utilizan juntos.

Ejemplos:
- Arma + carta.
- Equipo + carta específica.
- Conjuntos que producen bonificaciones.
- Materiales necesarios para una mejora.
- Equipamiento con slots y refinamientos determinados.

Aquí aparece un problema importante: el valor de un conjunto no siempre equivale a la suma de sus componentes.

\[
V(A+B)\neq V(A)+V(B)
\]

Puede existir un efecto de sinergia.

Mi recomendación es modelar estas relaciones solamente cuando exista una regla verificable o evidencia suficiente.

No construiría todas las combinaciones posibles de cartas, slots y refinamientos. Eso produciría una explosión combinatoria.

En su lugar, utilizaría:

1. Una representación normalizada del objeto base.
2. Modificadores de estado: refine, cartas, enchants y slots.
3. Relaciones conocidas de sinergia.
4. Un conjunto limitado de configuraciones populares.

Esto permite mantener el modelo escalable.

### 7.3. Recetas y demanda indirecta

Un objeto puede tener demanda porque es necesario para fabricar otro objeto.

Por tanto, su valor puede estar relacionado con el valor esperado del producto final.

Este mecanismo también puede generar demanda especulativa.

Recomiendo registrar las dependencias de crafting en un grafo dirigido.

El cálculo de costos de adquisición puede recorrer ese grafo en orden topológico cuando no existen ciclos.

Cuando aparecen ciclos, dependencias recursivas o conversiones repetidas, deben identificarse explícitamente y resolverse mediante optimización o análisis de ciclos, no mediante iteraciones ilimitadas.

---

## 8. La salida correcta: una distribución de precios

Estoy completamente de acuerdo con la propuesta de abandonar la banda simétrica low/mid/high.

No recomendaría:

\[
mid\pm x\%
\]

porque los precios de objetos raros tienen distribuciones naturalmente asimétricas.

Recomiendo representar:

\[
P_i\sim F_i
\]

Y almacenar:

| Campo | Significado |
|---|---|
| p10 | Percentil 10 |
| p50 | Mediana |
| p90 | Percentil 90 |
| confidence | Confianza de la estimación |
| evidence_count | Cantidad de observaciones |
| source_disagreement | Desacuerdo entre fuentes |
| distribution_type | Tipo de distribución |
| estimation_method | Método utilizado |

La correspondencia inicial puede ser:

- Low = P10.
- Mid = P50.
- High = P90.

Estos valores representan incertidumbre, no límites garantizados de compra o venta.

### 8.1. No todas las distribuciones serán iguales

Para objetos comunes con muchas operaciones:

Una distribución relativamente concentrada puede ser apropiada.

Para objetos raros:

La distribución será más amplia y posiblemente asimétrica.

Para objetos con comportamientos comerciales diferentes entre servidores:

Podemos encontrar distribuciones multimodales.

Por ejemplo, si un servidor comercializa un objeto alrededor de 2 millones y otro alrededor de 30 millones, asumir una distribución normal simple alrededor de 16 millones sería incorrecto.

En estos casos utilizaría modelos de mezcla o conservaría las distribuciones por fuente.

### 8.2. El sistema debe admitir «sin precio»

Esta es una decisión que considero indispensable.

No todos los objetos necesitan recibir un precio estimado.

Propongo cuatro estados de valoración:

| Estado | Resultado |
|---|---|
| priced | Precio respaldado por evidencia suficiente |
| estimated | Estimación apoyada en evidencia indirecta |
| indicative_cost | Solo existe una estimación del costo de reposición |
| unpriced | No existe evidencia suficiente para valorar |

Esto resuelve un problema filosófico del modelo actual:

**Es preferible reconocer que desconocemos el precio de un objeto que inventar un número para completar el catálogo.**

Un objeto legacy sin ventas recientes, sin ruta de adquisición y sin referencias comparables debería quedar como `unpriced`.

Eso no es un fallo del simulador.

Es un resultado estadístico válido.

---

## 9. Precios NPC: deben ser un subsistema independiente

Aquí recomiendo un cambio bastante concreto.

El precio NPC no debería calcularse como porcentaje del precio de mercado.

En rAthena existen dos valores independientes en la definición del objeto:

- `Buy`: precio de compra del objeto por parte del NPC, es decir, lo que paga el jugador.
- `Sell`: precio de venta del objeto por parte del NPC, es decir, lo que recibe el jugador al vendérselo.

La documentación oficial establece también los valores por defecto cuando uno de estos campos no está especificado. [GitHub](https://github.com/rathena/rathena/blob/master/doc/item_db.txt?utm_source=chatgpt.com)

Por tanto, el simulador debe respetar el comportamiento efectivo de la configuración de OzRo.

### 9.1. Reglas propuestas

Para comprar al NPC:

\[
NPC_{player\_buy}=Buy_{effective}
\]

Para vender al NPC:

\[
NPC_{player\_sell}=Sell_{effective}
\]

Pero:

\[
NoSell=true\Rightarrow NPC_{player\_sell}=0
\]

Y si el precio efectivo de venta es cero, el NPC no debe pagar al jugador por ese objeto.

También deben considerarse las modificaciones que puedan producir las habilidades de Merchant y las reglas particulares de los NPC.

Si el tasador es un NPC personalizado con intención de ofrecer precios diferentes a los de las tiendas tradicionales, debe definirse como una política independiente.

No mezclaría esa funcionalidad con los precios base de `item_db`.

### 9.2. Una distinción económica importante

El precio NPC representa una regla del sistema.

El precio de mercado representa un comportamiento de los jugadores.

No son equivalentes.

Un objeto puede tener un precio NPC de 100 zeny y venderse entre jugadores por 10 millones.

Otro puede tener un valor de mercado de 10 millones y no poder venderse a NPC.

El simulador debe conservar esa distinción.

---

## 10. Arquitectura de datos que recomiendo implementar

No recomiendo mantener toda la información económica dentro de una única propiedad `price`.

El resultado debería estar dividido en estructuras independientes.

Una representación conceptual:

```json
{
  "item_id": 744,

  "provenance": {
    "item_db": "valid",
    "mob_sources": "partial",
    "recipe_sources": "valid",
    "source_version": "dataset_version"
  },

  "acquisition": {
    "status": "legacy",
    "routes": [],
    "replacement_cost": null
  },

  "transfer": {
    "player_trade": "allowed",
    "npc_sell": "allowed",
    "drop": "blocked",
    "storage": "allowed",
    "mail": "allowed",
    "auction": "allowed"
  },

  "market": {
    "status": "stale",
    "eligible": true,
    "evidence_count": 12,
    "price_p10": null,
    "price_p50": 7500000,
    "price_p90": null
  },

  "npc": {
    "player_buy": 0,
    "player_sell": 0
  },

  "valuation": {
    "method": "historical_evidence",
    "confidence": "low",
    "warnings": [
      "legacy_source",
      "insufficient_recent_evidence"
    ]
  }
}
```

Es un ejemplo ilustrativo, no una valoración real de Bouquet.

Los campos numéricos nulos representan información no estimada. En producción, los datos de mercado, adquisición y NPC deben tener sus propias estructuras de procedencia y validación.

### 10.1. Trazabilidad obligatoria

Cada valoración debería poder explicar:

- Qué fuentes se utilizaron.
- Qué rutas de adquisición se encontraron.
- Qué probabilidades se aplicaron.
- Cuánto costaba cada ruta.
- Qué observaciones históricas se utilizaron.
- Qué parámetros produjeron el resultado.
- Por qué se asignó esa confianza.
- Qué advertencias se generaron.

Recomiendo que el resultado sea reproducible a partir de:

`input_snapshot + source_versions + configuration + model_version + overrides + seed`

No basta con guardar el precio final.

Hay que poder reconstruirlo.

---

## 11. Ingeniería de datos: el problema que debe solucionarse primero

El problema del loader de `mob_db.yml` merece atención inmediata.

El brief documenta un caso en el que 66 registros parciales sobrescriben información de monstruos en vez de complementar los registros existentes. Esto provoca la pérdida de atributos y fuentes de drops. Texto pegado

Mi recomendación es cambiar el comportamiento de la ingesta.

### 11.1. No reemplazar registros: aplicar overlays

Supongamos que existe:

```yaml
Id: 1086
AegisName: GOLDEN_THIEF_BUG
Hp: 222750
Level: 65
```

Y en la importación:

```yaml
Id: 1086
DamageTaken:
  ...
```

El registro final debe conservar HP y nivel y aplicar solamente la modificación de `DamageTaken`.

La implementación debe diferenciar entre:

- Campo ausente: conservar el valor anterior.
- Campo presente: aplicar el nuevo valor.
- Campo explícitamente nulo: aplicar el comportamiento definido para ese campo.

No basta con hacer un merge superficial indiscriminado. Los campos anidados y las listas necesitan reglas de combinación explícitas.

### 11.2. Pruebas obligatorias de ingesta

Antes de producir precios, ejecutaría estas verificaciones:

| Prueba | Resultado esperado |
|---|---|
| GTB ID 1086 | Conserva su HP original |
| GTB spawn | Conserva su frecuencia real |
| Ifrit | Conserva su fuente y respawn |
| Registros parciales | No eliminan campos existentes |
| alb_ship | Se clasifica correctamente |
| Monster Coin | Reconoce el flujo de 75 unidades/hora indicado en el brief |
| Cartas MVP | Conservan sus fuentes reales |
| Drops | Coinciden con los datos de origen |

También generaría un reporte de diferencias entre la base original y la base fusionada.

Ninguna pérdida masiva de HP, drops o spawns debería pasar inadvertida.

### 11.3. Separar incertidumbre de ausencia

Actualmente, 3.628 objetos synthetic tienen `supply.open = 0` y multiplicador de oferta neutral.

Ese comportamiento debe desaparecer.

Propongo estos estados:

- `known_supply`: oferta calculable.
- `unknown_supply`: no hay información suficiente.
- `zero_supply`: se ha confirmado que no existe producción.
- `legacy_supply`: existe inventario potencial, pero no una ruta activa de generación.

En particular:

\[
UnknownSupply\neq ZeroSupply
\]

La ausencia de información no puede convertirse en una conclusión económica.

---

## 12. Validación estadística sin ground truth

Esta es una de las preguntas más difíciles del brief.

No tener precios reales de OzRo no significa que no podamos evaluar el modelo.

Significa que debemos evaluar otras propiedades.

Propongo cinco grupos de pruebas.

### 12.1. Pruebas de monotonía

Para rutas equivalentes:

- Menor probabilidad de drop no debe reducir el costo esperado.
- Menor frecuencia de aparición no debe reducir el costo.
- Mayor costo de materiales no debe reducir el costo de fabricación.
- Mayor probabilidad de fracaso destructivo no debe reducir el costo esperado.
- Mayor tiempo de adquisición no debe reducir el costo de adquisición.

Una precisión: estas propiedades son válidas para el costo de adquisición cuando los demás factores permanecen constantes.

No deben imponerse directamente al precio de mercado, porque la demanda puede justificar diferencias.

### 12.2. Pruebas de consistencia comercial

- `NoTrade` bloquea el intercambio entre jugadores cuando está efectivamente activo.
- `NoSell` impide la venta al NPC.
- `NoDrop` no bloquea automáticamente el intercambio entre jugadores.
- Un objeto sin ruta identificada no recibe una penalización arbitraria de oferta.
- Una referencia histórica no convierte por sí sola un objeto en comerciable en OzRo.

### 12.3. Pruebas de consistencia estadística

- P10 ≤ P50 ≤ P90.
- Una muestra de dos ventas no debe producir artificialmente confianza alta.
- Un desacuerdo de 20x debe generar una advertencia.
- Una observación antigua debe perder peso frente a evidencia reciente comparable.
- Ningún promedio debe ocultar una dispersión extraordinaria.
- Los objetos sin información suficiente pueden quedar sin precio.

### 12.4. Pruebas de estrés

Ejecutaría escenarios modificando:

| Variable | Prueba |
|---|---|
| Drop rate | 1x, 2x, 5x y 10x |
| Respawn | Normal y reducido |
| HP de monstruos | Normal y aumentado |
| Probabilidad de crafting | 100%, 50%, 10%, 5% |
| Referencias históricas | Una fuente disponible y dos fuentes contradictorias |
| Acceso | Disponible, restringido y retirado |

La pregunta es si las consecuencias económicas siguen una lógica coherente.

### 12.5. Backtesting

Reservaría observaciones históricas que no se utilicen en el cálculo.

El sistema estima precios utilizando una parte de los datos y se compara contra las observaciones reservadas.

Evaluaría:

- Error porcentual logarítmico.
- Cobertura de intervalos P10-P90.
- Error de la mediana.
- Comportamiento por categorías económicas.
- Comportamiento en objetos comunes y raros.

La cobertura es particularmente importante.

Si el intervalo P10-P90 pretende contener el 80% de los precios observados comparables, debería aproximarse a esa proporción en un conjunto de validación adecuado.

No esperaría una validación perfecta entre servidores diferentes, pero sí identificaría sistemáticamente dónde falla la generalización.

---

## 13. Qué debe hacer cada componente: fórmula, manual y LLM

Mi recomendación es asignar responsabilidades muy claras.

| Componente | Responsabilidad |
|---|---|
| Código determinista | Cálculos, probabilidades, rutas, restricciones, distribución y trazabilidad |
| Overrides manuales | Excepciones verificadas y decisiones explícitas de diseño |
| LLM | Interpretación de fuentes complejas y extracción de conocimiento no estructurado |

### 13.1. Qué dejaría al código

Prácticamente toda la matemática:

- Costos de adquisición.
- Probabilidades.
- Respawn.
- Flujo de producción.
- Cálculos de crafting.
- Distribuciones de precios.
- Combinación estadística.
- Clasificación de canales comerciales.
- Restricciones NPC.
- Pruebas de consistencia.

No utilizaría un LLM para calcular directamente los precios de 9.600 objetos.

No hay una ventaja real en pedirle que estime miles de precios cuando las variables económicas ya pueden representarse formalmente.

### 13.2. Qué dejaría para intervención manual

La intervención manual debe reservarse para datos que verdaderamente requieren conocimiento del servidor.

Por ejemplo:

- Un evento que retiró permanentemente un objeto.
- Una modificación especial de un MVP.
- Una receta implementada mediante scripts complejos.
- Un NPC personalizado que modifica una ruta.
- Un override de política económica.

Todo override debe registrar:

`item_id + field + value + reason + author + timestamp + version`

No permitiría modificaciones manuales silenciosas.

### 13.3. Qué utilizaría para el LLM

Aquí sí veo una oportunidad interesante.

Un LLM puede ayudar a interpretar información que resulta difícil de extraer mediante reglas tradicionales:

- Scripts de quests.
- Scripts de crafting.
- Recetas especiales.
- NPC personalizados.
- Condiciones de acceso a instancias.
- Sistemas de transformación.
- Dependencias entre objetos.

Por ejemplo, puede analizar una receta descrita mediante un script y proponer:

```json
{
  "output_item": "Pantie[1]",
  "success_probability": 0.05,
  "inputs_consumed_on_failure": true,
  "inputs": [
    {
      "item": "Pantie",
      "quantity": 1
    },
    {
      "item": "Elunium",
      "quantity": 1
    }
  ],
  "zeny_cost": 1000000,
  "source": "socket_enchant2.txt",
  "confidence": "high"
}
```

El código debe verificar que el resultado coincida con las instrucciones reales del script.

El LLM no debe tener autoridad para inventar precios.

Debe extraer conocimiento, no decidir arbitrariamente el valor económico.

### 13.4. Cómo gastaría los 2-5 USD

No destinaría el presupuesto a valorar todos los objetos individualmente.

Lo utilizaría en una pasada de extracción y clasificación de las fuentes complejas.

Priorizaría:

1. Scripts de crafting y upgrades.
2. Quests con costos y restricciones.
3. Eventos y fuentes retiradas.
4. Casos ambiguos de adquisición.
5. Relaciones entre grupos, cajas y objetos.

La salida debe ser estructurada y contener referencias a las fuentes.

Si una afirmación del LLM no puede relacionarse con una fuente verificable, no debe incorporarse automáticamente al modelo.

Este enfoque es considerablemente más útil que generar 9.600 precios mediante una conversación con un modelo de lenguaje.

---

## 14. Plan de implementación recomendado

No intentaría construir todo simultáneamente.

Recomiendo cinco fases, con entregables y criterios de aceptación.

| Fase | Trabajo | Resultado |
|---|---|---|
| P0 — Integridad | Reparar loader, mobs, spawns y clasificación de mapas | Dataset confiable |
| P1 — Ontología | Separar adquisición, transferencia y mercado | Modelo de datos correcto |
| P2 — Economía | Implementar costos esperados por ruta | Costos de reposición |
| P3 — Estadística | Implementar estimación robusta de mercado e incertidumbre | Precios P10/P50/P90 |
| P4 — Enriquecimiento | Interpretación de scripts, relaciones y excepciones con LLM | Cobertura ampliada |

### Fase P0: integridad

No permitiría avanzar mientras persista el problema de ingesta.

Entregable: un `master.jsonl` corregido, con procedencia y validaciones automáticas.

### Fase P1: ontología

Reemplazaría las propiedades actuales por los tres ejes propuestos.

Entregable: nuevo esquema de datos, sin modificar todavía los precios.

### Fase P2: adquisición

Implementaría primero:
- Drops.
- Respawns.
- Grupos y cajas.
- Crafting.
- Quests.
- Costos de acceso.

Entregable: un costo de reposición estimado para cada objeto que tenga una ruta identificable.

### Fase P3: mercado

Implementaría:
- Normalización logarítmica.
- Ponderación de fuentes.
- Medianas robustas.
- Tratamiento de muestras pequeñas.
- Penalización por desacuerdo entre fuentes.
- Distribuciones de incertidumbre.

Entregable: precio de mercado con procedencia y confianza.

### Fase P4: enriquecimiento

Finalmente incorporaría:
- Relaciones de sustitución.
- Complementariedad.
- Clasificación de objetos legacy y event.
- Interpretación de scripts mediante LLM.
- Overrides versionados.

Esto evita gastar dinero y tiempo en interpretar correctamente objetos que todavía tienen información de origen corrupta.

---

## 15. Cómo comprobaría que el nuevo modelo realmente funciona

Utilizaría los seis casos problemáticos del brief como pruebas de regresión, pero no como reglas particulares.

| Objeto | Comportamiento que debe producir el nuevo modelo |
|---|---|
| Menblatt Card | Separar costo de adquisición y demanda; detectar conflicto histórico |
| Frilldora Card | Evitar que su referencia histórica determine por sí sola su rareza |
| Monster Coin | Reconocer su producción real y evitar clasificarlo por un prior genérico de Etc |
| Golden Thief Bug Card | Recuperar el monstruo 1086, su HP y su frecuencia real |
| Ifrit Card | Incorporar el time gate de once horas |
| Pantie[1] | Incorporar el costo esperado del proceso destructivo |
| Ice Pick[1] | Evitar que dos ventas extremas produzcan una estimación artificialmente confiable |

Hay una advertencia adicional: no podemos garantizar que GTB o Ifrit tengan los precios más elevados solamente a partir de su rareza.

Podemos calcular que son difíciles de obtener y estimar su costo de reposición. Para justificar que su precio de mercado esté entre los mayores necesitamos evidencia de utilidad, demanda y disposición de pago.

La rareza por sí sola no demuestra el valor comercial.

Esto es importante porque precisamente queremos evitar sustituir los multiplicadores actuales por nuevos multiplicadores arbitrarios.

---

# 16. Respuestas ejecutivas a las diez preguntas del brief

Para que las decisiones queden explícitas:

| Pregunta | Mi decisión |
|---|---|
| 1. ¿Costo esperado de adquisición? | Sí. Es el principal ancla económica, complementada por demanda y evidencia de mercado. |
| 2. ¿Objetos sin mercado ni ruta? | Deben poder quedar sin precio. No inventar valores. |
| 3. ¿Dos servidores con diferencias de 20x? | Modelo robusto en escala logarítmica, conservando la discrepancia y ampliando la incertidumbre. |
| 4. ¿Demanda con 0-2 ventas? | Modelar exposición y velocidad de transacciones. Con información insuficiente, utilizar priors débiles y bandas amplias. |
| 5. ¿Upgrades destructivos? | Modelar el proceso como una secuencia de intentos hasta el éxito, contabilizando todos los consumos. |
| 6. ¿Complementarios y sustitutos? | Grafo económico de relaciones y modelos de utilidad basados en características. |
| 7. ¿Mid y banda simétrica? | No. Distribución P10/P50/P90, con soporte para asimetría y multimodalidad. |
| 8. ¿Validación sin ground truth? | Invariantes, pruebas de monotonía, backtesting, cobertura de intervalos y pruebas de estrés. |
| 9. ¿Fórmula, manual o LLM? | Fórmula para la economía, manual para excepciones verificadas y LLM para interpretar información compleja. |
| 10. ¿Qué hacer con 2-5 USD? | Corregir primero los datos y utilizar el LLM para extraer recetas, quests, restricciones y fuentes complejas. |

Los criterios de éxito originales son adecuados en términos generales, pero recomiendo incorporar expresamente la separación entre evidencia histórica externa y comerciabilidad efectiva en OzRo. Texto pegado

---

# 17. Dictamen final

Mi evaluación es favorable respecto al enfoque de rediseño planteado en el brief.

De hecho, considero que identificar el problema como uno de ontología económica, en lugar de intentar corregir los multiplicadores existentes, es la decisión más importante de todo el proyecto.

Sin embargo, haría tres cambios fundamentales en la forma de pensar el simulador:

**Primero: dejar de intentar producir un precio para absolutamente todos los objetos.**

Un sistema que devuelve `unpriced` cuando no tiene evidencia es mejor que uno que asigna 500.000 zeny a una carta MVP porque pertenece a una categoría estadística.

**Segundo: dejar de considerar la dificultad de adquisición como sinónimo de valor.**

El costo de reposición explica lo que cuesta conseguir un objeto. La demanda explica cuánto están dispuestos a pagar los jugadores. La liquidez explica qué tan fácil es encontrar un comprador.

Las tres dimensiones importan.

**Tercero: convertir la trazabilidad en una característica central del producto.**

El MarketSimulator no debería ser simplemente un generador de precios.

Debería ser un sistema capaz de explicar la economía de cada objeto.

Por ejemplo, ante una valoración de 20 millones, debería poder responder:

- Se obtiene mediante una receta con 5% de éxito.
- Consume determinados materiales en cada intento.
- Su costo esperado de reposición es de aproximadamente 20 millones.
- Las referencias externas presentan determinada dispersión.
- Existe evidencia de determinadas operaciones comerciales.
- La confianza de la valoración es baja, media o alta por razones identificables.

Esa explicación tiene mucho más valor que el número aislado.

### Mi recomendación de decisión

Aprobaría el rediseño con esta prioridad:

1. Reparar la integridad de los datos.
2. Implementar la nueva ontología.
3. Construir el motor de adquisición.
4. Construir el estimador estadístico de mercado.
5. Incorporar incertidumbre y relaciones económicas.
6. Utilizar LLM solamente para enriquecer información no estructurada.

**No invertiría más esfuerzo en perfeccionar la fórmula actual.**

Tiene problemas conceptuales que no se solucionan ajustando exponentes, topes o factores.

El nuevo diseño debería tener una propiedad esencial: cuando una estimación sea incorrecta, debe ser posible identificar si falló la procedencia, la ruta de adquisición, la demanda, la referencia histórica o la interpretación económica.

Eso convierte un sistema de precios heurístico en un verdadero motor de valoración auditable.

---

**Conclusión del revisor:** recomiendo abandonar el modelo actual de multiplicadores y desarrollar un modelo híbrido, probabilístico y basado en rutas de adquisición. No recomiendo utilizar IA generativa para fijar precios. Recomiendo utilizarla para descubrir y estructurar información que permita al modelo económico calcularlos correctamente.

El siguiente paso de ingeniería debería ser convertir este dictamen en una especificación técnica implementable: esquema definitivo de `master.jsonl`, fórmulas exactas, contratos entre módulos y pruebas automatizadas para los casos de regresión.

# POSDATA — CONTEXTO ECONÓMICO PARTICULAR DE OZRO

## 9. Contexto adicional: un mercado simulado para una economía sin mercado real

Hay una particularidad fundamental de nuestro servidor que debe tenerse en cuenta al evaluar las propuestas anteriores: OzRo no tiene una economía de jugadores convencional.

Es un servidor privado de Ragnarok Online, basado en rAthena Renewal, compartido por aproximadamente cuatro jugadores que intercambian recursos, objetos y progresión entre ellos. No existe una población suficientemente grande para producir un mercado orgánico, una formación de precios representativa ni una evolución económica comparable a la de un servidor público.

En consecuencia, no disponemos de un mercado interno que podamos utilizar como ground truth, ni esperamos que aparezca uno con el tiempo.

El NPC tasador y el MarketSimulator no se están construyendo para complementar un mercado existente, sino para **suplir su ausencia y proporcionar artificialmente las funciones económicas que normalmente cumpliría una comunidad de jugadores**.

El objetivo es poder disfrutar de una experiencia de Ragnarok Online fundamentalmente offline, conservando elementos esenciales de su economía: adquisición, intercambio, progresión, acumulación de riqueza, decisiones de compra, fabricación y administración de recursos.

Esto cambia el propósito del sistema.

No necesitamos necesariamente reproducir los precios que tendría un servidor público, ni clonar la economía de LATAM o Atlantis. Necesitamos construir una economía sintética coherente, estable y suficientemente convincente para que el juego conserve su profundidad económica incluso sin una comunidad activa.

## 10. Consecuencias para el diseño del modelo

### 10.1. El precio no es únicamente una estimación estadística: es una decisión de diseño económico

En un servidor convencional, el precio emerge de la interacción entre compradores y vendedores.

En OzRo, esa interacción no existe en una escala suficiente.

Por tanto, el precio del NPC debe cumplir parcialmente la función de un mecanismo de formación de precios.

No basta con estimar cuánto podría valer un objeto en otro servidor. Necesitamos determinar cuánto debería valer dentro de la economía simulada de OzRo para mantener una experiencia de juego razonable.

Esto introduce una distinción entre:

- Valor externo: referencia observada en otros servidores.
- Costo de reposición: recursos y tiempo necesarios para conseguir el objeto.
- Valor de utilidad: importancia del objeto para la progresión y las actividades del juego.
- Valor económico sintético: precio que el sistema asigna para permitir una economía funcional.

Estos valores pueden coincidir, pero no tienen por qué hacerlo.

### 10.2. Los precios históricos externos son referencias de comportamiento, no objetivos

LATAM y Atlantis siguen siendo fuentes útiles.

Permiten observar relaciones relativas entre objetos, órdenes de magnitud, preferencias de los jugadores y posibles diferencias de utilidad.

Sin embargo, sus precios absolutos responden a economías que OzRo no tiene:

- Poblaciones diferentes.
- Cantidades distintas de moneda circulante.
- Disponibilidad de objetos diferente.
- Actividades de farming con distinta rentabilidad.
- Demanda generada por comunidades grandes.
- Concentración de riqueza y comportamientos especulativos.

Por tanto, recomiendo utilizar los datos externos principalmente para aprender relaciones y patrones, no para imponer precios absolutos.

Una carta MVP debería conservar una posición relativa de rareza y utilidad frente a una carta común, pero no necesariamente costar lo mismo que en Atlantis.

### 10.3. La economía sintética necesita una unidad de referencia propia

Propongo definir una unidad económica interna: el valor de una hora de juego representativa.

Esta unidad permitiría expresar los costos de adquisición en términos comparables.

Por ejemplo:

- Un objeto requiere aproximadamente 30 minutos de farming.
- Otro requiere 5 horas de farming.
- Otro necesita 20 horas de producción esperada debido a un proceso destructivo.
- Otro puede comprarse directamente a un NPC por una cantidad conocida de zeny.

El objetivo no es que todos los objetos respeten estrictamente su costo de reposición como precio de venta, sino disponer de una escala común para evaluar su posición económica.

La economía debe reconocer que los jugadores sacrifican tiempo, recursos y oportunidades para conseguir objetos.

### 10.4. El NPC debe funcionar como estabilizador económico

En ausencia de compradores y vendedores reales, el NPC se convierte en un participante económico artificial.

Por tanto, sus funciones deberían estar claramente diferenciadas:

**NPC tasador:** ofrece una referencia de valoración y proporciona información económica sobre los objetos.

**NPC comprador:** permite convertir objetos en zeny, estableciendo una salida económica para recursos que de otra forma no tendrían mercado.

**NPC vendedor:** permite adquirir recursos y objetos cuando no existe otro jugador que pueda suministrarlos.

No necesariamente deben ser el mismo NPC ni compartir las mismas políticas de precios.

Recomiendo evitar que el NPC compre y venda sistemáticamente al mismo precio, porque permitiría conversiones sin fricción y podría generar ciclos económicos artificiales.

Debe existir una diferencia entre compra y venta, pero no mediante porcentajes arbitrarios: debe responder a la función económica del NPC y a los límites de emisión de moneda que se quieran establecer.

### 10.5. La oferta debe representar disponibilidad para el jugador, no solamente cantidad de drops

En un servidor con cuatro jugadores, el problema no es exclusivamente cuántos objetos pueden producir los monstruos.

También importa cuánto tiempo necesita invertir un jugador para conseguirlos y cuánto contenido debe completar para tener acceso a ellos.

Un MVP que aparece una vez cada once horas representa una restricción real de disponibilidad, incluso si la probabilidad de drop es relativamente generosa.

Por eso, el costo de adquisición debe considerar:

- Frecuencia de aparición.
- Competencia por el recurso, aunque sea limitada.
- Tiempo de desplazamiento.
- Tiempo de combate.
- Probabilidad efectiva de obtención.
- Restricciones de acceso.
- Repetibilidad de la actividad.

La oferta debe expresarse como capacidad de producción por jugador o por unidad de tiempo, no únicamente como flujo agregado de monstruos.

### 10.6. La demanda debe ser parcialmente sintética

Este es posiblemente el cambio metodológico más importante.

No existe una población de compradores de la que podamos inferir demanda.

Tampoco es correcto asumir que las ventas de otros servidores representan las necesidades de cuatro jugadores con una experiencia de juego diferente.

Recomiendo construir un indicador de utilidad económica basado en:

- Importancia para la progresión.
- Utilidad en builds.
- Necesidad en recetas.
- Valor para completar equipamiento.
- Importancia para acceder a contenido.
- Existencia de sustitutos.
- Dependencia de otros objetos.

Este indicador no debe confundirse con demanda observada.

Debe identificarse explícitamente como demanda sintética o utilidad estimada.

Su función es permitir que el sistema valore objetos necesarios para progresar aunque nunca hayan tenido ventas registradas.

### 10.7. La inflación y la emisión de zeny deben formar parte del modelo

En una economía sin mercado orgánico, el principal riesgo no es solamente asignar precios incorrectos.

Es permitir que el sistema genere o destruya cantidades de zeny que desestabilicen la progresión.

Si el NPC compra materiales a precios demasiado generosos, los jugadores pueden generar riqueza ilimitada mediante farming y venta automática.

Si el NPC vende todos los objetos importantes a precios demasiado elevados, puede convertir la progresión en una acumulación artificialmente lenta.

Propongo establecer indicadores de control:

- Zeny generado por hora de farming.
- Zeny generado por hora de actividades repetibles.
- Costo de equipamiento por etapa de progresión.
- Tiempo esperado para adquirir equipamiento relevante.
- Rentabilidad relativa entre actividades.
- Diferencia entre precios de compra y venta NPC.

La economía sintética debe tener una progresión razonable y evitar rutas de generación de dinero claramente dominantes.

## 11. Cambio de objetivo: de estimar precios a diseñar una economía funcional

Considero necesario reformular el objetivo general del proyecto.

No buscamos obtener el precio verdadero de cada objeto, porque en ausencia de un mercado no existe una observación que permita conocerlo.

Buscamos construir un sistema de precios que cumpla simultáneamente estas propiedades:

1. Sea coherente con los costos de adquisición.
2. Respete la rareza y disponibilidad de los objetos.
3. Considere la utilidad para la progresión.
4. Mantenga relaciones económicas razonables entre objetos equivalentes.
5. Permita generar y gastar zeny de manera equilibrada.
6. No produzca arbitrajes o ciclos económicos triviales.
7. Permita disfrutar de una progresión similar a la de un servidor con economía activa.
8. Sea explicable, auditable y modificable sin intervenciones arbitrarias.

En este escenario, la ausencia de ground truth no es un inconveniente temporal que debamos solucionar esperando más datos. Es una condición estructural del proyecto.

Por eso, la validación debe cambiar.

Además de evaluar precisión estadística frente a referencias externas, debemos evaluar coherencia económica mediante simulaciones de escenarios, pruebas de rentabilidad, curvas de progresión y análisis de sensibilidad.

