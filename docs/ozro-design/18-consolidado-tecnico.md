# Ficha técnica — OzRagnarok (OzRo)

## Identidad y plataforma

| Campo | Valor |
|-------|-------|
| Nombre | OzRagnarok (OzRo) |
| Modalidad | Servidor privado familiar, ~3 jugadores |
| Acceso | VPN ZeroTier + invitación |
| Pincode | Desactivado |
| Motor | rAthena Renewal |
| Base | rAthena master de enero de 2026 |
| Modo | Renewal |
| Contenido principal | Episode 17.1 |
| Contenido deshabilitado | Episode 17.2, Episode 18, Novice Academy, 4th jobs |
| Nivel máximo | 175 base / 60 job para 3rd jobs |
| Protocolo servidor | `PACKETVER 20190605` |
| Cliente | Ragexe 2019-06-05 |
| Web / API | `ro.ozkr.net` |
| Stack web | React + Vite |
| API | Node.js |
| Base de datos | MariaDB compartida entre servidor y web |
| Seguridad | VPN + CORS restringido; cuentas admin no expuestas |
| Idioma del contenido custom | Español |


**Nota:** la base y el cliente se congelaron para evitar desajustes de protocolo y data. El cliente es la restricción; el servidor se alinea a él.

---

## Cliente y distribución

| Campo | Valor |
|-------|-------|
| Cliente base | Ragexe 2019-06-05 |
| Custom | Solo overlay; la base no se edita |
| Distribución | ZIP manual por USB o enlace; sin updater |
| Codificación de textos | ISO-8859-1 / Latin-1 |
| Acentos y eñes | Soportados por el cliente actual |
| Nombres de recursos coreanos | CP949; no se tocan ni se reinterpretan |
| Items custom | 5 (4 monedas + Alma de MVP) |
| Quest IDs | Cada ID debe existir en servidor y en la lista del cliente |
| Navegación | Habilitada; no se logró desactivar sin riesgo |
| Mapas con override visual | Reemplazo solo de la capa visual; colisión original intacta |
| Reconstrucción del cliente | Descartada |

**Nota:** una base limpia con el overlay no abrió; el ejecutable está parcheado de forma particular. Tocar la base o reconstruir el cliente es más riesgoso que alinear el servidor.

---

## Progresión y límites

| Parámetro | Valor |
|-----------|-------|
| Nivel máximo 3rd jobs | 175 / 60 |
| 4th jobs | Bloqueados en código |
| Nivel máximo | Tablas renewal estándar |
| ASPD máxima normal | 190 |
| ASPD máxima 3rd / extended | 193 |
| HP máximo nivel 175 | 1.100.000 |
| Respawn | 50% HP y 50% SP |
| Skill points por nivel | Sin límite |
| Reset de personaje | Disponible (gema + zeny) |
| Party share | 15 niveles |
| Misma cuenta en party | Bloqueada |
| Multi-cuenta | Permitida; las metas importantes son por cuenta |

---

## Experiencia

| Parámetro | Valor |
|-----------|-------|
| Base EXP | 5x |
| Job EXP | 5x |
| MVP EXP | 10x |
| Quest EXP (NPCs) | 3x |
| Multi level-up | Activado |
| Bonus por atacante extra | +25% base EXP |
| Tope de bonus por atacantes | 12 |
| Party even share bonus | 0 |
| Shop EXP (Discount/Overcharge) | 1% del zeny × nivel de skill |
| EXP en mapas PvP | Sí |
| Mostrar EXP y zeny ganados | Sí |
| Muerte | 1% base EXP + 1% job EXP del nivel actual |
| Muerte en max level | Sin pérdida de EXP |
| Penalización de zeny | 1% |

---

## Drops

| Tipo | Normal | Boss (no MVP) | MVP |
|------|--------|---------------|-----|
| Common (etc) | 5x | 5x | 1x |
| Healing | 10x | 10x | 1x |
| Usable | 10x | 10x | 1x |
| Equipment | 15x | 15x | 1x |
| Card | 10x | 100x | 100x |
| Recompensa MVP directa | — | — | 5x |
| Tesoros WoE | 5x | — | — |

| Regla | Valor |
|-------|-------|
| Tope efectivo de drop | 90% |
| Drops logarítmicos | No; lineales |
| Anuncio de drop raro | ≤ 1% |
| Autoloot mercenario | Sí |
| Autoloot homúnculo | Sí |
| Items al inventario | Sí; auto-get activo |
| Duración de item en suelo | 60 s |
| Prioridad de loot por primer ataque | +30% |
| Summons de Alchemist | Dropean recompensa |

---

## Combate y economía

| Parámetro | Valor |
|-----------|-------|
| HP de mobs | ×2 |
| HP de MVP | ×2 |
| Críticos de mobs | Desactivados |
| Penalización de flee a mobs | Sí |
| Penalización de DEF por cantidad de atacantes | No |
| Falcon + Warg simultáneos | Permitido |
| Curación de jefes | Heal/Full Heal sobre mobs cura 1 HP |
| Barra de HP de mobs | Oculta |
| MVP tomb | Activado |
| Zeny por kill | Sí, cantidad pequeña |
| Vending tax | 0% |
| Barter | Activado |
| Barter extendido | Desactivado |
| Banco / buying store / búsqueda de tiendas | Activados |
| Reconexión a instancias | Sí |
| Achievements / attendance / equip switch / roulette / airship privado | Desactivados |
| Mascotas | No requieren equip; atacan y dan EXP; level 50% |
| Skill points limit | No |

---

## Contenido custom

| Sistema | Detalle |
|---------|---------|
| NPCs base | Healer, stylist, Monke, reset, canje puntos↔zeny, Card Collector, Card Remover, cronista, Sabio de los Elementos, Ludovico, Kessinger (soul link) y Garrett |
| Bounty Boards | 57 tableros en 25 ciudades; niveles 1–165, con tramos abiertos |
| Quests repetibles | 18 quests de EXP por monstruo |
| Card Collector | 6 categorías; variables por cuenta; progreso persistente |
| Almas de MVP | Kills y asistencias generan fragmentos; 1 fragmento = 1 Alma; puntos por MVP de 1/3/5/10/20 |
| Ecos Tejidos | Instancia de 1 hora, 300 s de inactividad; 29 MVPs; cuesta 3/5/10 Almas + items; entra la party |
| Garrett el Recolector | 5 ofertas diarias; cap de 500.000 zeny por cuenta/día; contrato diario de 6 horas; moneda de bronce cada 10 tratos únicos |
| Warps por ciudad | 8 ciudades, 23 destinos; 4.000 zeny + 1 Blue Gemstone por viaje |
| Endless Tower | Reingreso cada 20 horas; límite interno de 4 horas |
| Monedas OzRo | 4 tiers (bronce, plata, oro, platino); solo bronce tiene fuente activa; tiers altos reservados |
| Mapas de job quest | Clones para Warlock, Mechanic y Sura |

---

## Datos y sincronización

| Dato | Valor |
|------|-------|
| IDs de quest custom en servidor | 290 |
| Items custom | 5 |
| Mapas en el servidor | 1.217 |
| Mapas con spawn | 410 |
| Puntos de spawn | 3.867 |
| Monstruos distintos con spawn | 1.384 |
| MVPs en radar | 74 |
| Refresh del radar | 30 s |
| Base de datos web | MariaDB compartida con el servidor |
| Tasas de drop en web | Espejo de la configuración del servidor |

**Nota:** cada quest ID debe existir en los dos lados; cada item custom necesita definición en servidor e icono/ilustración en cliente. Si falta un lado, la quest aparece vacía o el item falla al cargar.

---

## Limitaciones conocidas

| Limitación | Estado |
|------------|--------|
| Navegación del cliente | No se pudo ocultar; queda habilitada |
| 4th jobs | Bloqueados: cliente 2019 y bugs de la base |
| Cliente limpio | No abre con el overlay; no usar como reemplazo |
| Mapas de job quest | Dependen de clones; no están en los clientes disponibles |
| Sincronización de quests | Manual; un ID faltante rompe la ventana de quests |
| Items custom | Requieren icono e ilustración; si faltan, error de carga |
| Traducción de quests de job | Pendiente; implica revisión archivo por archivo |
| Economía de tiers altos | Sin usos definidos todavía |
