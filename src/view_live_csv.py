"""
view_live_csv.py
Visualización del CSV de referencia (scan_720.csv).
Propietario: Visión Artificial.

Importa lidar_processing.py (contrato de interfaz — NO modificar).

Modos:
  Sin --animate : dibuja todos los puntos válidos de golpe.
  Con --animate : simula llegada progresiva de puntos (--step y --delay).

Uso:
    python src/view_live_csv.py --csv data/scan_720.csv --animate
"""
from __future__ import annotations
import os
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from lidar_driver_csv import read_scan_csv
from lidar_processing import filter_and_project  # contrato interfaz

def main(csv_path: str, animate: bool, step: int, delay: float):
    samples = read_scan_csv(csv_path)
    n_total = len(samples)
    
    # Proyectar puntos válidos usando el módulo compartido
    # Se asume que pts tiene el formato: [(x, y, quality, angle, r), ...]
    pts = filter_and_project(samples)  
    n_valid = len(pts)
    pct_valid = n_valid / n_total * 100 if n_total > 0 else 0

    # Extraer puntos inválidos para resaltarlos [Visión]
    # Replicamos la lógica estándar: calidad baja o distancia fuera de rango
    invalid_samples = [s for s in samples if s[0] < 10 or (s[2]/1000.0) < 0.15 or (s[2]/1000.0) > 6.0]
    inv_angles = np.deg2rad([s[1] for s in invalid_samples])
    inv_dists = [s[2]/1000.0 for s in invalid_samples]
    inv_xs = inv_dists * np.cos(inv_angles)
    inv_ys = inv_dists * np.sin(inv_angles)

    # Configuración de 2 Subplots: Cartesiano y Polar [Visión]
    fig = plt.figure(figsize=(14, 7))
    fig.suptitle(f'RPLIDAR scan desde CSV | {n_valid}/{n_total} válidos ({pct_valid:.1f}%)', fontsize=14)
    
    # Subplot 1: Vista Cartesiana (XY)
    ax1 = fig.add_subplot(121)
    ax1.set_title('Vista Cartesiana (XY)')
    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('y (m)')
    ax1.set_aspect('equal', adjustable='box')
    ax1.grid(True, alpha=0.3)
    ax1.plot(0, 0, 'r^', markersize=10, label='Sensor (origen)')
    
    # Subplot 2: Vista Polar (r vs theta)
    ax2 = fig.add_subplot(122, projection='polar')
    ax2.set_title('Vista Polar ($r$ vs $\\theta$)')
    ax2.grid(True, alpha=0.3)
    ax2.set_rmax(6.0) # Ajustado al rango máximo típico de 6 metros

    if not animate:
        # Modo estático: dibujar todo de una vez
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        
        # Gráfico Cartesiano
        ax1.scatter(xs, ys, s=6, c='cyan', alpha=0.8, label='Válidos')
        if len(inv_xs) > 0:
            ax1.scatter(inv_xs, inv_ys, s=4, c='red', marker='x', alpha=0.5, label='Inválidos')
        ax1.legend()
        
        # Gráfico Polar (Ángulos en radianes, Distancia en metros)
        angles = np.deg2rad([p[3] for p in pts])
        dists = [p[4] for p in pts]
        ax2.scatter(angles, dists, s=6, c='magenta', alpha=0.8)

        # GUARDAR CAPTURA AUTOMÁTICA [Visión]
        os.makedirs('docs/capturas', exist_ok=True)
        save_path = 'docs/capturas/live_view_csv.png'
        plt.savefig(save_path)
        print(f"\n[INFO] Captura CSV guardada automáticamente en {save_path}")

        plt.show()
        return

    # Modo animado: acumular puntos progresivamente
    xs, ys = [], []
    angles_anim, dists_anim = [], []
    
    scat_xy = ax1.scatter(xs, ys, s=6, c='cyan', alpha=0.8)
    scat_polar = ax2.scatter(angles_anim, dists_anim, s=6, c='magenta', alpha=0.8)
    
    plt.ion()
    for i in range(0, len(pts), step):
        chunk = pts[i:i + step]
        
        # Actualizar datos Cartesianos
        xs.extend(p[0] for p in chunk)
        ys.extend(p[1] for p in chunk)
        scat_xy.set_offsets(list(zip(xs, ys)))
        
        # Actualizar datos Polares
        angles_anim.extend(np.deg2rad([p[3] for p in chunk]))
        dists_anim.extend(p[4] for p in chunk)
        # En proyecciones polares, set_offsets espera (theta, r)
        scat_polar.set_offsets(list(zip(angles_anim, dists_anim)))
        
        ax1.set_title(f'CSV animado | {len(xs)}/{n_valid} puntos trazados')
        plt.pause(0.001)
        time.sleep(delay)
        
    plt.ioff()
    plt.show()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv',     default='data/scan_720.csv')
    ap.add_argument('--animate', action='store_true', help='Animar llegada de puntos')
    ap.add_argument('--step',    type=int,   default=20,   help='Puntos por actualización')
    ap.add_argument('--delay',   type=float, default=0.02, help='Segundos entre updates')
    args = ap.parse_args()
    
    main(args.csv, args.animate, args.step, args.delay)
