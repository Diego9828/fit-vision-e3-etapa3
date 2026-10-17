"""Tarea 3.4 · Integrar: combinar las features por clip con etiqueta y video de origen.

Decisión: docs/decisiones/0006-integracion-y-particion.md
Uso: python src/integrar.py <intermedio>
"""
import sys
from pathlib import Path

import pandas as pd

from comun import cargar_params


def main(ruta_intermedio):
    params = cargar_params()
    col = params["columnas"]
    carpeta = Path(ruta_intermedio)
    feats = pd.read_parquet(carpeta / "construido.parquet")
    clips = pd.read_parquet(carpeta / "clips_seleccionados.parquet")

    # una fila por clip en ambos lados: si no, la unión duplicaría o perdería filas
    unido = feats.merge(
        clips[[col["id_clip"], col["video"], col["etiqueta"]]],
        on=col["id_clip"],
        how="inner",
        validate="one_to_one",
    )
    perdidos = set(feats[col["id_clip"]]) ^ set(unido[col["id_clip"]])
    if perdidos or len(unido) != len(feats):
        raise ValueError(f"la integración cambió el número de clips: {sorted(perdidos)}")
    unido.to_parquet(carpeta / "integrado.parquet", index=False)


if __name__ == "__main__":
    main(sys.argv[1])
