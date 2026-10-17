"""Utilidades compartidas del pipeline.

Regla del proyecto: aquí no hay umbrales, listas de categorías ni constantes de
negocio. Todo valor que sea una decisión vive en params.yaml.
"""
import json
from pathlib import Path

import yaml


def cargar_params(ruta="params.yaml"):
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def escribir_json(obj, ruta):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
