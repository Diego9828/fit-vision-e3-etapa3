# 0004 · Limpieza de señales: frames congelados, rango físico y faltantes dentro del clip

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #4
- **Etapa del pipeline:** `limpiar` (tarea CRISP-DM 3.2)

## Hallazgo que la motiva
- Etapa 2: 0 NaN (0 % de faltantes) en 656 celdas; rangos observados postura_torso 14–120°,
  nivel_cabeza 30–53°, apertura_mano_izq 0.17–0.44, angulo_pie_izq 37–77°.
- `GymFitx_mejoras.md`: el pipeline de captura procesa a ~**7 fps efectivos** (no 30) y el
  **69–71 %** de los frames aparecen "congelados" en los 3 videos medidos. Un frame congelado repite la
  fila anterior y sesga las medias y desviaciones por clip (la desviación se subestima).

## Decisión
1. Eliminar, dentro de cada clip, las filas idénticas a la anterior
   (`limpieza.eliminar_frames_congelados`).
2. Marcar como faltante cualquier valor fuera del rango físico plausible de su señal
   (`limpieza.limites`). Los límites son deliberadamente holgados: detectan errores de captura,
   no ejecuciones "raras".
3. Rellenar faltantes **solo con datos del mismo clip** (`limpieza.estrategia_faltantes`:
   interpolación lineal). Hoy no hay faltantes; la regla queda lista y documentada.
4. Descartar clips con menos de `limpieza.min_frames_por_clip` frames o con señal irrecuperable.

## Alternativas descartadas
- *Imputar con la mediana global:* usa información de otros clips (y de la futura partición) →
  fuga de información; además no hay faltantes que justifiquen un criterio global.
- *Dejar los frames congelados:* repite observaciones idénticas y falsea la desviación estándar,
  que es parte del vector de 8 features.
- *Eliminar valores "atípicos" por z-score:* con 18 clips un umbral estadístico borraría ejecuciones
  legítimamente malas, que son precisamente la clase a detectar.

## Dónde vive
- Parámetros: `params.yaml` → `limpieza.*`
- Código: `src/limpiar.py`
- Salidas declaradas: `datos/intermedio/limpio.parquet`, `reportes/informe_limpieza.md`,
  métrica `reportes/limpieza.json`

## Efecto esperado y cómo verificarlo
`reportes/limpieza.json` → `frames_congelados_eliminados` (> 0 si hay captura repetida),
`faltantes_restantes: 0`. Cambiar `eliminar_frames_congelados` modifica `limpio.parquet` y
`dvc.lock` en el mismo commit. Pendiente: confirmar con la clínica rangos clínicos de cada señal.
