"""Comprueba localmente los 7 criterios de aceptación de la etapa 3 (y un par de seguridad).

Cada criterio se resuelve ejecutando algo y mirando el resultado, sin preguntar al equipo.
Uso:  python tools/verificar_criterios.py            # incluye `dvc repro --force`
      python tools/verificar_criterios.py --sin-repro  # el CI ya lo ejecutó antes
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parent.parent
ENTEROS_PERMITIDOS = {0, 1, 2, 3, 4, 100}  # índices/sangrías/porcentaje; ningún umbral de negocio
EXT_TABLA = (".csv", ".parquet", ".feather", ".xlsx", ".npz", ".pkl", ".h5")
CARPETAS_DOC = ("docs/", "reportes/")


def sh(*args, check=False):
    r = subprocess.run(args, cwd=RAIZ, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(args)}\n{r.stdout}\n{r.stderr}")
    return r


def cargar(ruta):
    with open(RAIZ / ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def c1_reproducibilidad(con_repro):
    if not con_repro:
        return "OMITIDO", "lo ejecuta el CI (dvc repro --force + git diff dvc.lock)"
    antes = (RAIZ / "dvc.lock").read_bytes()
    r = sh("dvc", "repro", "--force")
    if r.returncode:
        return "FALLA", "dvc repro --force terminó con error:\n" + r.stderr[-400:]
    if (RAIZ / "dvc.lock").read_bytes() != antes:
        return "FALLA", "dvc.lock cambió tras reejecutar: no es reproducible"
    return "OK", "repro --force sin error y dvc.lock idéntico"


def c2_separacion():
    tracked = sh("git", "ls-files").stdout.split()
    historia = sh("git", "log", "--all", "--name-only", "--pretty=format:").stdout.split()
    tablas = sorted(
        {p for p in tracked + historia if p.lower().endswith(EXT_TABLA) and not p.startswith(CARPETAS_DOC)}
    )
    if tablas:
        return "FALLA", f"tablas en el historial: {tablas[:5]}"
    punteros = [p for p in tracked if p.endswith(".dvc")]
    if punteros != ["datos/crudo.dvc"]:
        return "FALLA", f"punteros .dvc inesperados (salidas registradas a mano): {punteros}"
    return "OK", "ninguna tabla en el historial; el crudo solo como puntero (datos/crudo.dvc)"


def c3_cobertura():
    stages = cargar("dvc.yaml")["stages"]
    decisiones = {p.name[:4]: p for p in (RAIZ / "docs/decisiones").glob("[0-9]*.md") if p.name[:4] != "0000"}
    mensajes = sh("git", "log", "--all", "--pretty=%B").stdout
    problemas = []
    for nombre, st in stages.items():
        citas = re.findall(r"docs/decisiones/([0-9]{4})-[\w-]+\.md", st.get("desc", ""))
        if not citas:
            problemas.append(f"etapa {nombre} sin entrada de bitácora en desc")
        for n in citas:
            if n not in decisiones:
                problemas.append(f"etapa {nombre} cita decisión inexistente {n}")
    for n in decisiones:
        if not re.search(rf"decisi[oó]n(?:es)?[^\n]*\b{n}\b|decisiones/{n}-", mensajes, re.I):
            problemas.append(f"decisión {n} no citada por ningún commit")
    return ("FALLA", "; ".join(problemas)) if problemas else ("OK", f"{len(stages)} etapas citan su entrada; {len(decisiones)} decisiones citadas por commits")


def _constantes_sospechosas(ruta):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (int, float)) and not isinstance(nodo.value, bool):
            if nodo.value not in ENTEROS_PERMITIDOS:
                yield nodo.lineno, f"constante numérica {nodo.value}"
        if isinstance(nodo, (ast.List, ast.Tuple, ast.Set)):
            textos = [e for e in nodo.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            # lista hecha solo de textos literales = categorías en el código;
            # las plantillas de informe (mezclan f-strings) no cuentan
            if len(textos) >= 2 and len(textos) == len(nodo.elts):
                yield nodo.lineno, "lista de categorías escrita en el código"


def c4_parametrizacion():
    problemas = [
        f"{p.name}:{linea} {que}"
        for p in sorted((RAIZ / "src").glob("*.py"))
        for linea, que in _constantes_sospechosas(p)
    ]
    declarados = set()
    for st in cargar("dvc.yaml")["stages"].values():
        declarados.update(str(x).split(".")[0] for x in st.get("params", []))
    sin_declarar = sorted(set(cargar("params.yaml")) - declarados)
    problemas += [f"clave de params.yaml no declarada por ninguna etapa: {k}" for k in sin_declarar]
    lock = cargar("dvc.lock")["stages"]
    problemas += [
        f"dvc.lock sin bloque params en la etapa {n}"
        for n, st in lock.items()
        if n != "diccionario" and "params" not in st
    ]
    return ("FALLA", "; ".join(problemas)) if problemas else ("OK", "sin umbrales/listas en src/; todo params.yaml declarado y anotado en dvc.lock")


def c5_diccionario():
    tabla = pd.read_parquet(RAIZ / "datos/final/tabla_modelado.parquet")
    dic = pd.read_csv(RAIZ / "docs/diccionario/diccionario.csv")
    if list(tabla.columns) != dic["columna"].tolist():
        return "FALLA", "el diccionario no coincide con las columnas de la tabla final"
    outs = [o if isinstance(o, str) else next(iter(o)) for o in cargar("dvc.yaml")["stages"]["diccionario"]["outs"]]
    if "docs/diccionario/diccionario.csv" not in outs:
        return "FALLA", "el diccionario no es salida declarada de una etapa"
    return "OK", f"{len(dic)}/{tabla.shape[1]} columnas cubiertas (100 %) y salida declarada"


def c6_informe_limpieza():
    st = cargar("dvc.yaml")["stages"]["limpiar"]
    metricas = [m if isinstance(m, str) else next(iter(m)) for m in st.get("metrics", [])]
    outs = [o if isinstance(o, str) else next(iter(o)) for o in st.get("outs", [])]
    if "reportes/limpieza.json" not in metricas or "reportes/informe_limpieza.md" not in outs:
        return "FALLA", "el informe de limpieza no es salida/métrica declarada de `limpiar`"
    return "OK", "reportes/limpieza.json (métrica) y reportes/informe_limpieza.md (salida) declarados"


def c7_colaboracion():
    hay_ci = (RAIZ / ".github/workflows/reproducibilidad.yml").exists()
    hay_pr = (RAIZ / ".github/pull_request_template.md").exists()
    merges = len(sh("git", "log", "--merges", "--oneline").stdout.splitlines())
    if not (hay_ci and hay_pr and merges):
        return "FALLA", f"CI={hay_ci}, plantilla PR={hay_pr}, merges={merges}"
    return "MANUAL", f"CI, plantilla de PR y {merges} cambios integrados por rama OK; falta proteger `main` en GitHub (Settings → Branches)"


def seguridad():
    ignorado = sh("git", "check-ignore", ".dvc/config.local").returncode == 0
    historia = sh("git", "log", "--all", "-p").stdout
    fuga = re.search(r"AKIA[0-9A-Z]{16}|secret_access_key\s*[:=]\s*\S+|-----BEGIN [A-Z ]*PRIVATE KEY", historia)
    if not ignorado:
        return "FALLA", ".dvc/config.local NO está ignorado por Git: el secreto se filtraría"
    if fuga:
        return "FALLA", "posible credencial en el historial: revocarla"
    return "OK", ".dvc/config.local ignorado y sin credenciales en el historial"


def main():
    con_repro = "--sin-repro" not in sys.argv
    resultados = [
        ("1 Reproducibilidad", c1_reproducibilidad(con_repro)),
        ("2 Separación datos/código", c2_separacion()),
        ("3 Cobertura de decisiones", c3_cobertura()),
        ("4 Parametrización", c4_parametrizacion()),
        ("5 Diccionario de datos", c5_diccionario()),
        ("6 Informe de limpieza", c6_informe_limpieza()),
        ("7 Traza de colaboración", c7_colaboracion()),
        ("+ Seguridad de credenciales", seguridad()),
    ]
    for nombre, (estado, detalle) in resultados:
        print(f"[{estado:<7}] {nombre}: {detalle}")
    if any(e == "FALLA" for _, (e, _) in resultados):
        sys.exit(1)


if __name__ == "__main__":
    main()
