#!/usr/bin/env python3
"""
Convierte los reportes de aprovechamiento (.xlsx) de UPMH en un unico data.json
que consume el dashboard (index.html).

Uso:
    python3 scripts/generar_datos.py

Lee todos los .xlsx dentro de data/reportes/ y escribe data.json en la raiz
del repositorio. Cada archivo .xlsx debe tener el formato estandar exportado
por el sistema administrativo: encabezado con la carrera, y bloques de grupo
(Tutor, Corte 1-3, Final, Bajas) seguidos de una tabla de materias.
"""
import json
import re
from pathlib import Path

import openpyxl

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTES_DIR = REPO_ROOT / "data" / "reportes"
OUTPUT_PATH = REPO_ROOT / "data.json"


def parse_bajas(texto):
    if texto is None:
        return {"cantidad": 0, "porcentaje": 0.0}
    m = re.match(r"Bajas:\s*(\d+)\s*(?:\(([\d.]+)\s*%\))?", str(texto))
    if not m:
        return {"cantidad": 0, "porcentaje": 0.0}
    cantidad = int(m.group(1))
    porcentaje = float(m.group(2)) if m.group(2) else 0.0
    return {"cantidad": cantidad, "porcentaje": porcentaje}


def parse_grupal(texto):
    if texto is None:
        return None
    m = re.match(r"Grupal:\s*([\d.]+)", str(texto))
    return float(m.group(1)) if m else None


def parse_alumnos(texto):
    if texto is None:
        return {"total": 0, "reprobados": 0}
    m = re.match(r"\s*(\d+)\s*/\s*(\d+)", str(texto))
    if not m:
        return {"total": 0, "reprobados": 0}
    return {"total": int(m.group(1)), "reprobados": int(m.group(2))}


def parse_porcentaje_reprobados(texto):
    if texto is None:
        return 0.0
    texto = str(texto)
    if "Sin Reprobados" in texto:
        return 0.0
    m = re.match(r"([\d.]+)\s*%", texto)
    return float(m.group(1)) if m else 0.0


def parse_periodo(texto):
    m = re.search(r"Reporte de Aprovechamiento:\s*(.+)", str(texto or ""))
    return m.group(1).strip() if m else "Periodo desconocido"


def parse_workbook(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    periodo = None
    carrera = None
    grupos = []
    i = 0
    while i < len(rows):
        row = rows[i]
        first = row[0]
        if first is None and row[1] and "Reporte de Aprovechamiento" in str(row[1]):
            periodo = parse_periodo(row[1])
        elif first is None and row[1] and periodo and carrera is None:
            carrera = str(row[1]).strip()
        elif first and isinstance(first, str) and str(row[1] or "").startswith("Tutor:"):
            grupo_nombre = str(first).strip()
            tutor = str(row[1]).replace("Tutor:", "").strip()
            bajas = parse_bajas(row[6])
            header_row = rows[i + 1]
            grupales = [parse_grupal(header_row[c]) for c in (2, 3, 4, 5)]

            materias = []
            j = i + 2
            while j < len(rows) and rows[j][0]:
                mrow = rows[j]
                materias.append({
                    "materia": str(mrow[0]).strip(),
                    "docente": str(mrow[1]).strip() if mrow[1] else "No disponible",
                    "corte1": mrow[2],
                    "corte2": mrow[3],
                    "corte3": mrow[4],
                    "final": mrow[5],
                    "alumnos": parse_alumnos(mrow[6]),
                    "porcentajeReprobados": parse_porcentaje_reprobados(mrow[7]),
                })
                j += 1

            grupos.append({
                "grupo": grupo_nombre,
                "tutor": tutor,
                "bajas": bajas,
                "grupal": {
                    "corte1": grupales[0],
                    "corte2": grupales[1],
                    "corte3": grupales[2],
                    "final": grupales[3],
                },
                "materias": materias,
            })
            i = j
            continue
        i += 1

    return {
        "periodo": periodo or "Periodo desconocido",
        "carrera": carrera or path.stem,
        "grupos": grupos,
    }


def main():
    archivos = sorted(REPORTES_DIR.glob("*.xlsx"))
    if not archivos:
        raise SystemExit(f"No se encontraron archivos .xlsx en {REPORTES_DIR}")

    carreras = [parse_workbook(f) for f in archivos]

    OUTPUT_PATH.write_text(
        json.dumps({"carreras": carreras}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    total_grupos = sum(len(c["grupos"]) for c in carreras)
    print(f"OK: {len(carreras)} carreras, {total_grupos} grupos -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
