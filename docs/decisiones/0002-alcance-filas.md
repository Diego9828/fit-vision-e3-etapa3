# 0002 · Alcance de filas: solo clips etiquetados `bien`/`mal` con clase suficiente

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #2
- **Etapa del pipeline:** `seleccionar` (tarea CRISP-DM 3.1)

## Hallazgo que la motiva
Etapa 2 (export de `cortador.py`): 19 clips = **base 1, bien 8, mal 10**, provenientes de
4 videos etiquetados (205448, 205453, 211230, 211856) y 2 sin etiquetar (214947, 215049).
En el entrenamiento `run_1` ya se había excluido la clase `base` por tener menos de 2 clips
(quedaron 18 muestras). El objetivo de negocio (etapa 1) es decidir si una repetición está
*bien* o *mal* ejecutada, es decir, un problema binario.

## Decisión
La unidad de análisis es **1 clip = 1 repetición**. Entran solo los clips cuya etiqueta está en
`seleccion.etiquetas_candidatas` y cuya clase tiene al menos `seleccion.min_clips_por_clase`
clips. Con los datos actuales sale `base` (1 clip) y quedan 18 clips (8 bien, 10 mal).
Los videos sin etiquetar no aportan filas (no tienen clips etiquetados).

## Alternativas descartadas
- *Mantener `base` como tercera clase:* con 1 clip no se puede partir ni evaluar; solo añadiría ruido.
- *Fijar la regla "excluir `base`" a mano en el código:* esconde la decisión; con un umbral
  parametrizado la regla se aplica sola si cambian los datos (p. ej. al grabar más ejemplos).

## Dónde vive
- Parámetros: `params.yaml` → `seleccion.etiquetas_candidatas`, `seleccion.min_clips_por_clase`
- Código: `src/seleccionar.py`
- Salidas declaradas: `datos/intermedio/clips_seleccionados.parquet`,
  `datos/intermedio/frames_seleccionados.parquet`, métrica `reportes/seleccion.json`

## Efecto esperado y cómo verificarlo
`reportes/seleccion.json` debe mostrar `clases_excluidas_por_pocos_clips: ["base"]`,
`clips_salida: 18` y `clips_por_etiqueta_salida` con bien 8 / mal 10. Si cambia el umbral y la tabla
cambia, el cambio aparece en `dvc.lock` dentro del mismo commit.
