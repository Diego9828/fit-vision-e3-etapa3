"""Genera un crudo SINTÉTICO de demostración con el esquema del export de Fit Vision.

NO es el dataset real. Reproduce solo lo verificado en la etapa 2:
  - 19 clips (base 1, bien 8, mal 10), 164 frames en total, 0 faltantes.
  - 4 videos etiquetados (205448, 205453, 211230, 211856; este último aporta 11 clips)
    y 2 sin etiquetar (214947, 215049).
  - 4 señales por frame con los rangos observados.
Los valores se muestrean con semilla fija; sirven para ejecutar y auditar el pipeline.
Para el dataset real: reemplazar datos/crudo/ con el export de cortador.py (ver README).

Uso: python tools/generar_crudo_sintetico.py datos/crudo
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 42
SENALES = {
    "postura_torso": (14.0, 120.0),
    "nivel_cabeza": (30.0, 53.0),
    "apertura_mano_izq": (0.17, 0.44),
    "angulo_pie_izq": (37.0, 77.0),
}
# (video, etiqueta, n clips)
PLAN = [
    ("211856", "bien", 5), ("211856", "mal", 6),
    ("205448", "bien", 1), ("205448", "mal", 2),
    ("205453", "bien", 1), ("205453", "mal", 1), ("205453", "base", 1),
    ("211230", "bien", 1), ("211230", "mal", 1),
]
FRAMES_TOTALES = 164
PROB_FRAME_CONGELADO = 0.12
DESPLAZAMIENTO_MAL = 0.12  # fracción del rango


def main(destino):
    rng = np.random.default_rng(SEMILLA)
    destino = Path(destino)
    (destino / "clips").mkdir(parents=True, exist_ok=True)

    clips = [(v, e) for v, e, n in PLAN for _ in range(n)]
    n_clips = len(clips)
    base, extra = divmod(FRAMES_TOTALES, n_clips)
    frames_por_clip = [base + (1 if i < extra else 0) for i in range(n_clips)]

    etiquetas = {}
    for i, ((video, etiqueta), n) in enumerate(zip(clips, frames_por_clip), start=1):
        clip_id = f"clip_{i:02d}"
        datos = {"frame": np.arange(n)}
        for nombre, (lo, hi) in SENALES.items():
            rango = hi - lo
            centro = lo + rango * rng.uniform(0.3, 0.7)
            if etiqueta == "mal":
                centro += rango * DESPLAZAMIENTO_MAL
            serie = centro + np.cumsum(rng.normal(0, 0.04 * rango, n))
            datos[nombre] = np.clip(serie, lo, hi).round(3)
        df = pd.DataFrame(datos)
        for k in range(1, n):  # frames "congelados": fila idéntica a la anterior
            if rng.random() < PROB_FRAME_CONGELADO:
                df.loc[k, list(SENALES)] = df.loc[k - 1, list(SENALES)].to_numpy()
        df.to_csv(destino / "clips" / f"{clip_id}.csv", index=False)
        etiquetas[clip_id] = {"etiqueta": etiqueta, "video": video}

    manifest = {
        "origen": "sintetico_demo",
        "videos": [
            {"video": v, "etiquetado": True, "fps_efectivo": 7}
            for v in ("205448", "205453", "211230", "211856")
        ] + [
            {"video": v, "etiquetado": False, "fps_efectivo": 7}
            for v in ("214947", "215049")
        ],
    }
    for nombre, obj in (("labels.json", etiquetas), ("manifest.json", manifest)):
        with open(destino / nombre, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1])
