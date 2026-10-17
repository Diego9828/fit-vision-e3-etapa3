"""Tarea 3.3 · Construir: variables derivadas (frames -> 1 fila por clip).

Decisión: docs/decisiones/0005-construccion-features.md
Uso: python src/construir.py <intermedio>
"""
import sys
from pathlib import Path

import pandas as pd

from comun import cargar_params


def main(ruta_intermedio):
    params = cargar_params()
    col, con = params["columnas"], params["construccion"]
    carpeta = Path(ruta_intermedio)
    frames = pd.read_parquet(carpeta / "limpio.parquet")

    agrupado = frames.groupby(col["id_clip"], sort=True)
    salida = pd.DataFrame(index=agrupado.size().index)
    for sufijo, funcion in con["estadisticos"].items():
        for senal in col["senales"]:
            serie = agrupado[senal]
            salida[f"{senal}_{sufijo}"] = (
                serie.std(ddof=con["ddof"]) if funcion == "std" else getattr(serie, funcion)()
            )
    salida[col["n_frames"]] = agrupado.size()
    salida = salida.fillna(0.0)  # std de 1 frame con ddof=1 sería NaN: variación nula
    salida.reset_index().to_parquet(carpeta / "construido.parquet", index=False)


if __name__ == "__main__":
    main(sys.argv[1])
