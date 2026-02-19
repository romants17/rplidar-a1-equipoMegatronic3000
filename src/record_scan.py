"""
record_scan.py
Graba escaneos en tiempo real a un CSV con timestamp.
Propietario: Computación.

Formato CSV de salida:
 t, quality, angle_deg, dist_mm

Uso:
 python src/record_scan.py --port /dev/ttyUSB0 --seconds 10 --out data
 python src/record_scan.py --port /dev/ttyUSB0 --decimation 5
"""

from __future__ import annotations
import argparse, csv, time
from pathlib import Path
from lidar_driver import LidarDriver


def main():
    ap = argparse.ArgumentParser(description='Grabación de escaneo RPLIDAR a CSV')
    ap.add_argument('--port', required=True, help='Puerto serie')
    ap.add_argument('--seconds', type=int, default=10, help='Duración de la grabación')
    ap.add_argument('--out', default='data', help='Carpeta de salida')

    # ── Decimación ────────────────────────────
    # Guarda solo 1 de cada N puntos.
    # 1 = sin decimación (por defecto)
    ap.add_argument('--decimation', type=int, default=1,
                    help='Guardar 1 de cada N puntos (default=1)')

    args = ap.parse_args()

    if args.decimation < 1:
        raise ValueError("El factor de decimación debe ser >= 1")

    # Crear carpeta de salida si no existe
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Nombre de archivo con timestamp para no sobrescribir
    filename = out_dir / f"scan_{time.strftime('%Y%m%d_%H%M%S')}.csv"

    driver = LidarDriver(args.port)
    t0 = time.time()
    total_pts = 0
    raw_pts = 0  # contador total real (sin decimar)

    print(f'[INFO] Grabando {args.seconds}s → {filename}')
    print(f'[INFO] Decimación: 1 de cada {args.decimation} puntos')

    try:
        with filename.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['t', 'quality', 'angle_deg', 'dist_mm'])  # header

            for fr in driver.frames():
                for q, a, d in fr.pts:

                    raw_pts += 1

                    # ── DECIMACIÓN ──────────────────────────────
                    # Solo escribimos el punto si cumple:
                    # raw_pts % N == 0
                    #
                    # Ejemplo:
                    # N = 5
                    # Se escriben los puntos 5, 10, 15, 20...
                    if raw_pts % args.decimation != 0:
                        continue

                    writer.writerow([f'{fr.t:.4f}', q, f'{a:.3f}', f'{d:.1f}'])
                    total_pts += 1

                # Finaliza cuando se cumple el tiempo solicitado
                if time.time() - t0 >= args.seconds:
                    break

    finally:
        driver.shutdown_safe()

    print(f'[OK] Guardado: {filename}')
    print(f'     Puntos capturados: {raw_pts}')
    print(f'     Puntos guardados:  {total_pts}')
    

if __name__ == '__main__':
    main()
