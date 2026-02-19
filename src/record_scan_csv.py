"""
record_scan_csv.py
Procesa el CSV de referencia, filtra puntos y genera un informe.
Propietario: Computación.
Importa lidar_processing.py (contrato de interfaz — NO modificar).

Salidas generadas en --out:
 filtered_points.csv → nube de puntos válidos proyectados a XY
 report_scan.md → informe markdown con métricas

Uso:
 python src/record_scan_csv.py --csv data/scan_720.csv --out docs
"""

from __future__ import annotations
import argparse
from pathlib import Path
from lidar_driver_csv import read_scan_csv
from lidar_processing import is_valid, polar_to_xy  # contrato interfaz


def main(csv_in: str, out_dir_str: str):
    out = Path(out_dir_str)
    out.mkdir(parents=True, exist_ok=True)

    samples = read_scan_csv(csv_in)
    n = len(samples)

    # Separar válidas e inválidas usando el módulo compartido
    valid = [s for s in samples if is_valid(s)]
    invalid = [s for s in samples if not is_valid(s)]

    # ── Guardar puntos filtrados ──────────────────────────────────────
    filtered_csv = out / "filtered_points.csv"
    with filtered_csv.open("w", encoding="utf-8") as f:
        f.write("x_m,y_m,quality,angle_deg,measure_m\n")
        for s in valid:
            x, y = polar_to_xy(s)
            f.write(
                f"{x:.6f},{y:.6f},{s.quality},{s.angle:.3f},{s.measure_m:.4f}\n"
            )

    # ── Generar informe markdown ──────────────────────────────────────
    ok_ratio = sum(1 for s in samples if s.ok == 1) / n if n else 0
    valid_ratio = len(valid) / n if n else 0

    report = out / "report_scan.md"
    report.write_text(
        f"""# Informe de scan CSV

**Archivo de entrada:** `{csv_in}`  
**Total de lecturas:** {n}  
**ok == 1:** {ok_ratio:.2%}  
**Válidas tras filtro (lidar_processing):** {valid_ratio:.2%} ({len(valid)} puntos)  
**Inválidas:** {len(invalid)} puntos  

## Criterio de filtrado (lidar_processing.py)

- ok == 1  
- quality >= 20  
- 0.20 m < measure_m <= 10.0 m  

## Archivos generados

- `{filtered_csv.name}`: nube de puntos válidos (x, y, quality, angle, r)

## TODO [Computación]

- Añadir CLI para ajustar umbrales de filtro sin editar el código.
- Exportar también las inválidas con el motivo de descarte.
- Añadir logging y control de errores (CSV malformado, rutas inexistentes).
""",
        encoding="utf-8",
    )

    print("[OK] Generados:")
    print(f"  {filtered_csv}")
    print(f"  {report}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/scan_720.csv")
    ap.add_argument("--out", default="docs")
    args = ap.parse_args()

    main(args.csv, args.out)
