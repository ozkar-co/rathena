# OzRo Market

Documentación del rediseño de la economía sintética y del mercado de OzRo.

## Objetivo

Construir una economía sintética para un servidor rAthena Renewal de
aproximadamente cuatro jugadores, sin mercado orgánico ni ground truth, que
cumpla dos funciones:

1. **Liquidez para lo que sale:** un objeto raro o valioso obtenido por un
   jugador no debe terminar en la basura por no haber comprador.
2. **Suministro para lo que se necesita:** un objeto raro o difícil no debe
   quedar limitado a la suerte o al grindeo personal por no haber quien lo
   provea.

La economía debe emular el efecto estadístico de una población mayor: con
suficientes jugadores, a alguien le termina tocando; el mercado redistribuye.
Con cuatro jugadores ese componente no existe y hay que diseñarlo.

## Decisiones vigentes

- **Unidad de cuenta:** hora de juego.
- **Dificultad de adquisición:** se obtiene cruzando la distribución de
  capacidad de jugadores simulados con la distribución determinista de
  dificultad de los mobs. Los mobs más difíciles son además más improbables,
  porque requieren jugadores expertos y bien equipados, que son escasos.
- **Arquitectura por capas:** cada capa se construye, evalúa y ajusta por
  separado. Sobre esas capas se ajusta la regresión o política de cada NPC.
  Puede haber más de tres NPCs, con alcance, objetivos y políticas distintas.
- **Demanda/utilidad:** se diseña, no se estima. Puede quedar fuera de la v1
  si se justifica.
- **Nivel absoluto:** se decide e impone, no se calibra con datos externos.
  Modelo directo.
- **Validación:** no hay ground truth. El modelo se construye desde lógica,
  economía, estadística e intuición, y debe incluir detección temprana de
  colapso.
- **Taxonomía:** se define de nuevo. No se reutiliza la anterior.
- **LLM:** aceptable para extraer features de utilidad o interpretar mecánicas;
  no para fijar precios. Una corrida no determinista es aceptable si queda
  registrada y auditable.

## Documentos

- [`brief-01.md`](brief-01.md) — brief original, archivado como contexto.
- [`brief-02.md`](brief-02.md) — brief vigente para la segunda ronda.
- [`historia/brief-01/`](historia/brief-01/) — respuestas al primer brief, archivadas.

## Estado

Segunda ronda preparada. La responde únicamente **ChatGPT**, por ser el que
demostró mayor competencia en la primera ronda. La respuesta se usará para
escribir el **Spec de Economía Sintética v1**: parámetros, ontología, contratos
de capas, modelo de adquisición, política de precios, política NPC y
validación.

La calidad y procedencia de los datos de item, mob y spawn es una precondición
del modelo; se valida por separado y no se asume correcta.
