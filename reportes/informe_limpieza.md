# Informe de limpieza (tarea 3.2)

Generado por `src/limpiar.py`; no editar a mano. Responde, problema por problema, al informe
de calidad de la etapa 2.

| Problema (etapa 2) | Qué se hizo | Cantidad | Queda sin resolver |
|---|---|---|---|
| Faltantes en señales (etapa 2: 0 NaN en 656 celdas) | `interpolacion_lineal` dentro de cada clip | 0 originales; 0 a rellenar tras marcar rangos | 0 |
| Frames congelados (captura a ~7 fps efectivos, 69–71 % congelados en 3 videos medidos) | se eliminan las filas idénticas a la anterior | 19 frames (12.2 % de 156) | la causa (frecuencia de captura) no se corrige aquí: se corrige al capturar |
| Valores fuera de rango físico | se marcan como faltantes y se rellenan | postura_torso: 0, nivel_cabeza: 0, apertura_mano_izq: 0, angulo_pie_izq: 0 | rangos plausibles, no clínicos: validar con la fisioterapeuta |
| Clips demasiado cortos (< 3 frames) o irrecuperables | se descartan | 0 (ninguno) | — |

Resultado: 18 → 18 clips y 156 → 137 frames.
Métricas completas en `reportes/limpieza.json`.
