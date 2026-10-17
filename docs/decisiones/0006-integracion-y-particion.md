# 0006 · Integración 1:1 y partición agrupada por video (sin mezclar un video en train y test)

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #6
- **Etapa del pipeline:** `integrar` (tarea 3.4) y `formatear` (columna `fold`)

## Hallazgo que la motiva
- Los 19 clips salen de **4 videos etiquetados** y el video 211856 aporta **11 de 19 clips (58 %)**.
- El entrenamiento `run_1` usó `StratifiedKFold(k=5, random_state=42)` **por clip**: clips del
  mismo video (misma persona, cámara y sesión) caen a la vez en entrenamiento y validación. Eso es una
  forma de fuga de información (Kapoor y Narayanan, 2023: filas no independientes en ambas
  mitades). Es un **riesgo** para el 61.1 % reportado, no una medición de cuánto lo infla.

## Decisión
1. La integración une features, etiqueta y video con `validate="one_to_one"` y falla si cambia el
   número de clips (no se pierden ni se duplican filas).
2. La tabla final trae una columna `fold` calculada con `GroupKFold` agrupando por `video`
   (`particion.columna_grupo`, `particion.n_splits`). La partición **no ajusta nada**: solo asigna
   filas; imputación y escalado se ajustarán dentro de cada fold en modelado.

## Alternativas descartadas
- *Mantener `StratifiedKFold` por clip:* comparable con `run_1` pero con el riesgo de fuga señalado.
- *Dejar la partición solo para modelado:* se pierde el registro de una decisión que condiciona la
  validez de la métrica; se registra aquí para que sea auditable.

## Dónde vive
- Parámetros: `params.yaml` → `particion.columna_grupo`, `particion.n_splits`
- Código: `src/integrar.py` y `src/formatear.py`
- Salidas declaradas: `datos/intermedio/integrado.parquet`, `datos/final/tabla_modelado.*`

## Efecto esperado y cómo verificarlo
`reportes/tabla_final.json` → `filas_por_fold`, `clases_por_fold`. Advertencia conocida: con 4
videos y uno que concentra el 58 % de las filas, los folds quedan muy desbalanceados en tamaño;
las métricas por fold serán ruidosas y deben leerse así. Ampliar el número de videos reduce el problema.
