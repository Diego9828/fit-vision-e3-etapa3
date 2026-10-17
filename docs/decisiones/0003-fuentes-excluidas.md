# 0003 · Excluir de la tabla de entrenamiento los 28 cortes de los videos de Yessenia

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #3
- **Etapa del pipeline:** `seleccionar` (tarea CRISP-DM 3.1: justificación de exclusión de fuentes)

## Hallazgo que la motiva
El 25/09 la fisioterapeuta Yessenia entregó 7 videos (60 fps) de demostración: sentadilla,
sentadilla con brazos, curl de bíceps, elevaciones laterales, puente, zancada y plancha con
flexiones. Se cortaron el 28/09: **28 repeticiones = 7 base + 21 bien**, todas ejecuciones
correctas y **ninguna `mal`**. Además su esquema es distinto: 8 ángulos por frame + 33
landmarks, frente a las 4 señales del entrenamiento actual (postura_torso, nivel_cabeza,
apertura_mano_izq, angulo_pie_izq).

## Decisión
Esos 28 cortes **no entran** a la tabla de modelado de esta etapa y no forman parte de
`datos/crudo`. Mezclarlos ahora haría que la *fuente* (otro ejercicio, otra cámara, otros
fps, solo `bien`) quedara perfectamente correlacionada con la etiqueta: el modelo aprendería
"a qué video pertenece" en lugar de "cómo se ejecutó".

## Alternativas descartadas
- *Añadirlos como más ejemplos `bien`:* sesgo de fuente + desbalance artificial hacia `bien`.
- *Usarlos como prueba externa:* sin ejemplos `mal` no se puede medir recall de la clase `mal`.

## Dónde vive
- Parámetros: ninguno (la decisión es de alcance de fuentes, no de umbral)
- Código: ninguno; el crudo registrado en DVC (`datos/crudo.dvc`) no los contiene
- Evidencia: `reportes/seleccion.json` (solo clips de los 4 videos etiquetados)
- Los ángulos de Yessenia se conservan aparte (`angulos_yessenia/*_angulos.npz`) para el módulo de
  ángulos del equipo; se incorporarán con una tabla propia cuando existan ejemplos `mal` del
  mismo ejercicio.

## Efecto esperado y cómo verificarlo
`reportes/seleccion.json` → `clips_por_video` solo lista videos de la sesión original.
Pendiente de negocio (E1): grabar ~10 bien + ~10 mal del ejercicio elegido para reabrir esta decisión.
