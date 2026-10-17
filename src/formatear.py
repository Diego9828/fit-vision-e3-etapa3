"""Tarea 3.5 · Dar formato: tipos, codificación de la etiqueta, partición y tabla final.

Decisión: docs/decisiones/0007-formato-y-diccionario.md
Uso: python src/formatear.py <intermedio> <final> <reporte.json>
"""
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupKFold

from comun import cargar_params, escribir_json


def main(ruta_intermedio, ruta_final, ruta_reporte):
    params = cargar_params()
    col, par, fmt = params["columnas"], params["particion"], params["formato"]
    objetivo, pliegue = fmt["columna_objetivo"], fmt["columna_fold"]
    df = pd.read_parquet(Path(ruta_intermedio) / "integrado.parquet")

    # etiqueta -> entero (codificación declarada, no implícita)
    df[objetivo] = df[col["etiqueta"]].map(fmt["codificacion_etiqueta"])
    if df[objetivo].isna().any():
        raise ValueError("hay etiquetas sin codificación en formato.codificacion_etiqueta")
    df[objetivo] = df[objetivo].astype("int64")

    # partición agrupada: solo asigna filas, no ajusta nada con los datos
    df[pliegue] = -1
    divisor = GroupKFold(n_splits=par["n_splits"])
    for numero, (_, prueba) in enumerate(divisor.split(df, df[objetivo], df[par["columna_grupo"]])):
        df.loc[df.index[prueba], pliegue] = numero
    df[pliegue] = df[pliegue].astype("int64")
    df[col["n_frames"]] = df[col["n_frames"]].astype("int64")

    sufijos = tuple(f"_{s}" for s in params["construccion"]["estadisticos"])
    features = [c for c in df.columns if c.endswith(sufijos)]
    orden = [col["id_clip"], col["video"], pliegue, col["n_frames"], *features, col["etiqueta"], objetivo]
    df = df[orden].sort_values(col["id_clip"]).reset_index(drop=True)

    destino = Path(ruta_final)
    destino.mkdir(parents=True, exist_ok=True)
    df.to_parquet(destino / "tabla_modelado.parquet", index=False)
    df.to_csv(destino / "tabla_modelado.csv", index=False)

    escribir_json(
        {
            "filas": int(len(df)),
            "columnas": int(df.shape[1]),
            "features": int(len(features)),
            "filas_por_clase": {k: int(v) for k, v in df[col["etiqueta"]].value_counts().items()},
            "filas_por_fold": {str(k): int(v) for k, v in df[pliegue].value_counts().sort_index().items()},
            "clases_por_fold": {
                str(k): {c: int(n) for c, n in g[col["etiqueta"]].value_counts().items()}
                for k, g in df.groupby(pliegue)
            },
            "videos_por_fold": {
                str(k): sorted(g[col["video"]].unique().tolist()) for k, g in df.groupby(pliegue)
            },
            "baseline_mayoritario": round(float(df[objetivo].value_counts(normalize=True).max()), 4),
        },
        ruta_reporte,
    )


if __name__ == "__main__":
    main(*sys.argv[1:4])
