# 0005 · Construcción: vector de 8 features por clip (media y desviación de cada señal)

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #5
- **Etapa del pipeline:** `construir` (tarea CRISP-DM 3.3)

## Hallazgo que la motiva
La unidad de análisis es 1 clip (decisión 0002) pero los datos están a nivel de frame
(164 frames en 19 clips, ~8–9 por clip). El entrenamiento `run_1` ya usaba el vector de **8
features = media + desviación de 4 señales**, con un mejor resultado de 61.1 % de accuracy frente a
un baseline mayoritario de 55.6 % (clase `mal`, 10/18). Mantener el mismo vector permite comparar
la tabla nueva con `run_1` sin cambiar dos cosas a la vez.

## Decisión
Agregar por clip la **media** y la **desviación estándar** (`ddof = 0`, población) de cada una de
las 4 señales, más `n_frames` como metadato de control (no es predictor). Resultado: 8 features +
`n_frames`.

## Alternativas descartadas
- *Añadir min/max/rango o derivadas temporales:* con 18 clips más columnas aumentan el riesgo de
  sobreajuste; se reabre en la etapa de modelado si hace falta.
- *`ddof = 1`:* con clips de ~8 frames y un posible clip de 1 frame generaría NaN; `ddof = 0`
  es siempre definido.

## Dónde vive
- Parámetros: `params.yaml` → `construccion.estadisticos`, `construccion.ddof`
- Código: `src/construir.py`
- Salida declarada: `datos/intermedio/construido.parquet`

## Efecto esperado y cómo verificarlo
`construido.parquet` tiene 1 fila por clip y 8 columnas `*_media` / `*_desv` + `n_frames`.
El diccionario de datos (decisión 0007) debe cubrir las 9 columnas.
