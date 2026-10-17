# 0007 · Formato de la tabla final, etiqueta codificada y diccionario generado por el pipeline

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #7
- **Etapa del pipeline:** `formatear` y `diccionario` (tarea CRISP-DM 3.5)

## Hallazgo que la motiva
Sin descripción, la tabla final es "una tabla anónima" (CRISP-DM, salidas de la etapa 3). Un
diccionario escrito a mano se desincroniza en la primera iteración. Además la etiqueta del
`labels.json` está en texto (`bien`/`mal`) y el baseline mayoritario (clase `mal`) es 55.6 %: la
codificación y el balance deben quedar visibles.

## Decisión
- Tipos explícitos (`int64`, `float64`, texto), orden fijo de columnas, tabla en Parquet y en CSV.
- Etiqueta codificada **por mapa declarado** (`formato.codificacion_etiqueta`: mal = 0, bien = 1);
  si aparece una etiqueta sin código, el stage falla.
- **Imputación y escalado NO se hacen aquí**: se ajustarán dentro de cada fold en modelado
  (evita fuga: la prueba no influye en la preparación).
- El diccionario sale del pipeline: las descripciones humanas viven en
  `docs/diccionario/descripciones.yaml`; el stage `diccionario` comprueba que cubren el **100 %**
  de las columnas y que el tipo documentado coincide con el real. Si no, falla.

## Alternativas descartadas
- *Escalar (z-score) en esta etapa:* ajustaría media y desviación con todas las filas, incluida la
  futura prueba.
- *Diccionario en un documento aparte:* se desincroniza sin que nada falle.

## Dónde vive
- Parámetros: `params.yaml` → `formato.codificacion_etiqueta`, `particion.*`
- Código: `src/formatear.py`, `src/diccionario.py`
- Salidas declaradas: `datos/final/tabla_modelado.parquet|csv`, `docs/diccionario/diccionario.csv`,
  métrica `reportes/tabla_final.json`

## Efecto esperado y cómo verificarlo
`docs/diccionario/diccionario.csv` tiene una fila por cada columna de la tabla final.
`reportes/tabla_final.json` → `baseline_mayoritario` (referencia contra la que debe compararse
cualquier modelo) y distribución de clases por fold.
