"""Tarea 3.1 · Seleccionar: qué filas (clips) y qué columnas (señales) entran.

Decisiones: docs/decisiones/0002-alcance-filas.md y 0003-fuentes-excluidas.md
Uso: python src/seleccionar.py <crudo> <intermedio> <reporte.json>
"""
import sys
from pathlib import Path

import pandas as pd

from comun import cargar_params, escribir_json, leer_json


def main(ruta_crudo, ruta_intermedio, ruta_reporte):
    params = cargar_params()
    col, sel = params["columnas"], params["seleccion"]
    crudo, salida = Path(ruta_crudo), Path(ruta_intermedio)
    salida.mkdir(parents=True, exist_ok=True)

    etiquetas = leer_json(crudo / "labels.json")
    manifest = leer_json(crudo / "manifest.json")

    clips = pd.DataFrame(
        [
            {col["id_clip"]: k, col["etiqueta"]: v[col["etiqueta"]], col["video"]: v[col["video"]]}
            for k, v in sorted(etiquetas.items())
        ]
    )
    conteo_entrada = clips[col["etiqueta"]].value_counts().to_dict()

    # 1) solo etiquetas candidatas
    es_candidata = clips[col["etiqueta"]].isin(sel["etiquetas_candidatas"])
    # 2) solo clases con clips suficientes para poder partir y evaluar
    conteo = clips.loc[es_candidata, col["etiqueta"]].value_counts()
    clases_ok = conteo[conteo >= sel["min_clips_por_clase"]].index.tolist()
    clases_fuera = sorted(set(conteo.index) - set(clases_ok))
    elegidos = clips[clips[col["etiqueta"]].isin(clases_ok)].reset_index(drop=True)

    frames = []
    for clip_id in elegidos[col["id_clip"]]:
        archivo = crudo / "clips" / f"{clip_id}.csv"
        df = pd.read_csv(archivo)
        faltan = [c for c in [col["frame"], *col["senales"]] if c not in df.columns]
        if faltan:
            raise ValueError(f"{archivo}: faltan columnas {faltan}")
        df = df[[col["frame"], *col["senales"]]].copy()
        df.insert(0, col["id_clip"], clip_id)
        frames.append(df)
    frames = pd.concat(frames, ignore_index=True)

    elegidos.to_parquet(salida / "clips_seleccionados.parquet", index=False)
    frames.to_parquet(salida / "frames_seleccionados.parquet", index=False)

    videos_con_clips = set(elegidos[col["video"]])
    videos_sin_clips = sorted(
        v[col["video"]] for v in manifest["videos"] if v[col["video"]] not in videos_con_clips
    )
    por_video = elegidos[col["video"]].value_counts()
    escribir_json(
        {
            "origen_datos": manifest.get("origen", "desconocido"),
            "clips_entrada": int(len(clips)),
            "clips_por_etiqueta_entrada": {k: int(v) for k, v in conteo_entrada.items()},
            "clases_excluidas_por_pocos_clips": clases_fuera,
            "clips_salida": int(len(elegidos)),
            "clips_por_etiqueta_salida": {
                k: int(v) for k, v in elegidos[col["etiqueta"]].value_counts().items()
            },
            "frames_salida": int(len(frames)),
            "videos_en_manifest": int(len(manifest["videos"])),
            "videos_sin_clips_seleccionados": videos_sin_clips,
            "clips_por_video": {k: int(v) for k, v in por_video.items()},
            "proporcion_video_mayoritario": round(float(por_video.max() / por_video.sum()), 4),
        },
        ruta_reporte,
    )


if __name__ == "__main__":
    main(*sys.argv[1:4])
