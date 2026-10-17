"""Genera el diccionario de datos de la tabla final y verifica que cubre el 100 % de sus columnas.

Decisión: docs/decisiones/0007-formato-y-diccionario.md
Uso: python src/diccionario.py <tabla.parquet> <descripciones.yaml> <salida.csv>
"""
import sys
from pathlib import Path

import pandas as pd
import yaml


def tipo_de(serie):
    if pd.api.types.is_integer_dtype(serie):
        return "int"
    if pd.api.types.is_float_dtype(serie):
        return "float"
    return "string"


def main(ruta_tabla, ruta_descripciones, ruta_salida):
    df = pd.read_parquet(ruta_tabla)
    with open(ruta_descripciones, encoding="utf-8") as f:
        desc = yaml.safe_load(f)

    sin_describir = [c for c in df.columns if c not in desc]
    sobrantes = [c for c in desc if c not in df.columns]
    if sin_describir or sobrantes:
        raise SystemExit(
            f"diccionario desincronizado. Sin describir: {sin_describir}. Sobrantes: {sobrantes}."
        )

    filas = []
    for c in df.columns:
        real, esperado = tipo_de(df[c]), desc[c]["tipo"]
        if real != esperado:
            raise SystemExit(f"{c}: tipo real {real} != tipo documentado {esperado}")
        numerica = pd.api.types.is_numeric_dtype(df[c])
        filas.append(
            {
                "columna": c,
                "tipo": real,
                "unidad": desc[c]["unidad"],
                "origen": desc[c]["origen"],
                "descripcion": desc[c]["descripcion"],
                "nulos": int(df[c].isna().sum()),
                "minimo": round(float(df[c].min()), 4) if numerica else "",
                "maximo": round(float(df[c].max()), 4) if numerica else "",
            }
        )
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas).to_csv(ruta_salida, index=False)


if __name__ == "__main__":
    main(*sys.argv[1:4])
