# 0008 · Verificación automática de reproducibilidad y de los criterios de aceptación

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #8
- **Etapa del pipeline:** transversal

## Hallazgo que la motiva
Reproducir y trazar no son la misma pregunta. Un pipeline puede reconstruir la tabla desde un
clon nuevo y aun así no dejar rastro de las decisiones. La comprobación no debe depender de la
memoria de nadie.

## Decisión
- Flujo de integración continua (`.github/workflows/reproducibilidad.yml`): clon limpio →
  `dvc pull` → `dvc repro --force` → `git diff --exit-code dvc.lock`.
  Se usa `--force` y no `dvc status`, porque `dvc status` termina en éxito aunque haya cambios
  pendientes.
- Regla de colaboración comprobable: si cambia `params.yaml`, `dvc.lock` debe cambiar en el mismo
  cambio.
- `tools/verificar_criterios.py` ejecuta localmente los 7 criterios de aceptación de la etapa.
- Rama `main` protegida con revisión obligatoria: es un **ajuste de GitHub**, no del repositorio
  (ver README, "Pendientes de publicación").

## Alternativas descartadas
- *Verificar a mano antes de entregar:* no escala y se olvida.

## Dónde vive
- Parámetros: ninguno
- Código: `tools/verificar_criterios.py`, `.github/workflows/reproducibilidad.yml`

## Efecto esperado y cómo verificarlo
`python tools/verificar_criterios.py` termina con código 0 y una tabla de 7 criterios.
