# 0001 · El crudo entra una sola vez, inmutable, y vive en un remoto DVC

- **Estado:** aceptada
- **Fecha:** 2026-10-17
- **Issue:** #1
- **Etapa del pipeline:** (previa al pipeline) registro de `datos/crudo`

## Hallazgo que la motiva
Etapa 2: el export de `cortador.py` se regenera cada vez que se pulsa *Entrenar* y vive solo en
la máquina de un integrante (`C:\Users\...\FGML`); no hay repositorio ni versionado de datos.
Eso es el síntoma "en mi máquina funciona" (no reproducible) y no deja rastro de qué datos
produjeron `run_1` (no trazable).

## Decisión
- `datos/crudo/` (clips `*.csv`, `labels.json`, `manifest.json`) se registra con `dvc add` y solo su
  puntero (`datos/crudo.dvc`) entra a Git. Ninguna etapa lo declara como salida: es de solo lectura.
- Una etiqueta anotada `datos-v1` marca el crudo original.
- Remoto de datos: `almacen` (ver `.dvc/config`). Las credenciales van en `.dvc/config.local`
  (ignorado por Git), nunca al repositorio.
- Entorno reproducible: `environment.yml` (conda-forge, Python 3.12, DVC 3.67.1).

## Alternativas descartadas
- *Datos dentro de Git:* binarios/tablas inflan el historial y no se pueden quitar después.
- *Carpeta compartida sin historia:* sin vínculo entre la versión del código y la de los datos.

## Dónde vive
- Parámetros: ninguno
- Código: `tools/generar_crudo_sintetico.py` solo para la demostración (ver README)
- Registro: `datos/crudo.dvc`, `.dvc/config`

## Efecto esperado y cómo verificarlo
`git ls-files` no lista ninguna tabla; lista `datos/crudo.dvc`. Un clon nuevo recupera los datos
con `dvc pull` y reconstruye con `dvc repro` obteniendo el mismo `dvc.lock`.

> **Aviso de procedencia:** el crudo versionado en este repositorio es **sintético**
> (`manifest.json → origen: sintetico_demo`) y reproduce solo la forma verificada del dataset real
> (19 clips, 164 frames, 4 señales). Para el dataset real, sustituir `datos/crudo/` y ejecutar
> `dvc add datos/crudo && dvc repro` (ver README).
