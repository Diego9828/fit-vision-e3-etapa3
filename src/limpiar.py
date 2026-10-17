"""Tarea 3.2 · Limpiar: elevar la calidad de las señales a lo que exige el análisis.

Decisión: docs/decisiones/0004-limpieza-senales.md
Uso: python src/limpiar.py <intermedio> <reporte.json> <informe.md>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from comun import cargar_params, escribir_json


def rellenar(grupo, senales, estrategia):
    if estrategia == "interpolacion_lineal":
        grupo[senales] = grupo[senales].interpolate(method="linear", limit_direction="both")
    elif estrategia == "mediana_clip":
        grupo[senales] = grupo[senales].fillna(grupo[senales].median())
    else:
        raise ValueError(f"estrategia_faltantes desconocida: {estrategia}")
    return grupo


def main(ruta_intermedio, ruta_reporte, ruta_informe):
    params = cargar_params()
    col, lim = params["columnas"], params["limpieza"]
    senales = col["senales"]
    carpeta = Path(ruta_intermedio)

    frames = pd.read_parquet(carpeta / "frames_seleccionados.parquet")
    frames = frames.sort_values([col["id_clip"], col["frame"]]).reset_index(drop=True)
    n_entrada, clips_entrada = len(frames), frames[col["id_clip"]].nunique()
    nan_originales = int(frames[senales].isna().sum().sum())

    # 1) frames congelados: fila idéntica a la anterior dentro del mismo clip
    n_congelados = 0
    if lim["eliminar_frames_congelados"]:
        previo = frames.groupby(col["id_clip"])[senales].shift()
        congelado = (frames[senales] == previo).all(axis=1)
        n_congelados = int(congelado.sum())
        frames = frames[~congelado].reset_index(drop=True)

    # 2) valores fuera del rango físico plausible -> faltante
    fuera_de_rango = {}
    for senal in senales:
        bajo, alto = lim["limites"][senal]
        malo = (frames[senal] < bajo) | (frames[senal] > alto)
        fuera_de_rango[senal] = int(malo.sum())
        frames.loc[malo, senal] = np.nan
    nan_a_rellenar = int(frames[senales].isna().sum().sum())

    # 3) faltantes: se rellenan SOLO con datos del mismo clip (no mezcla clips -> sin fuga)
    partes = [
        rellenar(g.copy(), senales, lim["estrategia_faltantes"])
        for _, g in frames.groupby(col["id_clip"], sort=True)
    ]
    frames = pd.concat(partes, ignore_index=True)
    nan_restantes = int(frames[senales].isna().sum().sum())

    # 4) clips que quedaron demasiado cortos o con señal sin recuperar
    tam = frames.groupby(col["id_clip"]).size()
    sin_dato = frames.groupby(col["id_clip"])[senales].apply(lambda g: g.isna().any().any())
    cortos = tam[tam < lim["min_frames_por_clip"]].index
    invalidos = sorted(set(cortos) | set(sin_dato[sin_dato].index))
    frames = frames[~frames[col["id_clip"]].isin(invalidos)].reset_index(drop=True)

    frames.to_parquet(carpeta / "limpio.parquet", index=False)

    reporte = {
        "frames_entrada": int(n_entrada),
        "clips_entrada": int(clips_entrada),
        "faltantes_originales": nan_originales,
        "frames_congelados_eliminados": n_congelados,
        "valores_fuera_de_rango": fuera_de_rango,
        "faltantes_tras_rangos": nan_a_rellenar,
        "faltantes_restantes": nan_restantes,
        "estrategia_faltantes": lim["estrategia_faltantes"],
        "clips_descartados": invalidos,
        "frames_salida": int(len(frames)),
        "clips_salida": int(frames[col["id_clip"]].nunique()),
        "frames_por_clip_min": int(frames.groupby(col["id_clip"]).size().min()),
        "frames_por_clip_max": int(frames.groupby(col["id_clip"]).size().max()),
    }
    escribir_json(reporte, ruta_reporte)

    pct = 100 * n_congelados / n_entrada if n_entrada else 0.0
    md = [
        "# Informe de limpieza (tarea 3.2)",
        "",
        "Generado por `src/limpiar.py`; no editar a mano. Responde, problema por problema, al informe",
        "de calidad de la etapa 2.",
        "",
        "| Problema (etapa 2) | Qué se hizo | Cantidad | Queda sin resolver |",
        "|---|---|---|---|",
        f"| Faltantes en señales (etapa 2: 0 NaN en 656 celdas) | `{lim['estrategia_faltantes']}` dentro de cada clip | {nan_originales} originales; {nan_a_rellenar} a rellenar tras marcar rangos | {nan_restantes} |",
        f"| Frames congelados (captura a ~7 fps efectivos, 69–71 % congelados en 3 videos medidos) | "
        f"{'se eliminan' if lim['eliminar_frames_congelados'] else 'se conservan'} las filas idénticas a la anterior | "
        f"{n_congelados} frames ({pct:.1f} % de {n_entrada}) | "
        "la causa (frecuencia de captura) no se corrige aquí: se corrige al capturar |",
        "| Valores fuera de rango físico | se marcan como faltantes y se rellenan | "
        + ", ".join(f"{k}: {v}" for k, v in fuera_de_rango.items())
        + " | rangos plausibles, no clínicos: validar con la fisioterapeuta |",
        f"| Clips demasiado cortos (< {lim['min_frames_por_clip']} frames) o irrecuperables | se descartan | "
        f"{len(invalidos)} ({', '.join(invalidos) if invalidos else 'ninguno'}) | — |",
        "",
        f"Resultado: {clips_entrada} → {reporte['clips_salida']} clips y {n_entrada} → {len(frames)} frames.",
        "Métricas completas en `reportes/limpieza.json`.",
        "",
    ]
    Path(ruta_informe).parent.mkdir(parents=True, exist_ok=True)
    Path(ruta_informe).write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:4])
