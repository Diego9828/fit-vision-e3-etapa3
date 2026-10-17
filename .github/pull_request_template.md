## Decisión que implementa
Cierra #<número del asunto>

## Qué cambia y por qué
<!-- Decisión, motivo y magnitud. No: "actualización de datos". -->

## Lista de comprobación
- [ ] Hay una entrada en `docs/decisiones/` y la etapa de `dvc.yaml` la cita en `desc`
- [ ] Todo umbral / lista / constante de negocio está en `params.yaml`, no en el código
- [ ] Si cambió `params.yaml`, se reejecutó `dvc repro` y `dvc.lock` va en este mismo cambio
- [ ] `dvc push` hecho **antes** de `git push` (primero el contenido, después el historial)
- [ ] Ninguna tabla ni credencial en el commit
