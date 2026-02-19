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
from lidar_processing import filter_and_project  # Contrato de interfaz: realiza el filtrado y proyección XY

def main(csv_path: str, animate: bool, step: int, delay: float):
    # 1. CARGA DE DATOS: Lee el archivo CSV generado por el driver
    samples = read_scan_csv(csv_path)
    n_total = len(samples)
    
    # 2. PROCESAMIENTO: Proyectar puntos válidos usando el módulo compartido de Visión
    # El formato esperado de pts es: [(x, y, quality, angle, distance), ...]
    pts = filter_and_project(samples)  
    n_valid = len(pts)
    pct_valid = n_valid / n_total * 100 if n_total > 0 else 0

    # 3. IDENTIFICACIÓN DE RUIDO/ERRORES: Extraer puntos inválidos para diagnóstico visual
    # Se replica la lógica del sensor: calidad baja (<10) o distancias fuera del rango operativo (15cm - 6m)
    invalid_samples = [s for s in samples if s[0] < 10 or (s[2]/1000.0) < 0.15 or (s[2]/1000.0) > 6.0]
    inv_angles = np.deg2rad([s[1] for s in invalid_samples]) # Conversión a radianes para trigonometría
    inv_dists = [s[2]/1000.0 for s in invalid_samples]       # Conversión mm -> metros
    
    # Transformación manual a Cartesiano para los puntos inválidos (solo visualización)
    inv_xs = inv_dists * np.cos(inv_angles)
    inv_ys = inv_dists * np.sin(inv_angles)

    # 4. CONFIGURACIÓN DE LA FIGURA: 2 Subplots (Cartesiano y Polar)
    fig = plt.figure(figsize=(14, 7))
    fig.suptitle(f'RPLIDAR scan desde CSV | {n_valid}/{n_total} válidos ({pct_valid:.1f}%)', fontsize=14)
    
    # Subplot 1: Vista Cartesiana (XY) - Útil para navegación y SLAM
    ax1 = fig.add_subplot(121)
    ax1.set_title('Vista Cartesiana (XY)')
    ax1.set_xlabel('x (m)')
    ax1.set_ylabel('y (m)')
    ax1.set_aspect('equal', adjustable='box') # Mantiene la proporción 1:1 para no deformar el entorno
    ax1.grid(True, alpha=0.3)
    ax1.plot(0, 0, 'r^', markersize=10, label='Sensor (origen)') # Marcador del sensor
    
    # Subplot 2: Vista Polar (r vs theta) - Representación nativa del LiDAR
    ax2 = fig.add_subplot(122, projection='polar')
    ax2.set_title('Vista Polar ($r$ vs $\\theta$)')
    ax2.grid(True, alpha=0.3)
    ax2.set_rmax(6.0) # Límite radial fijado en 6 metros

    # --- MODO ESTÁTICO (Renderizado Único) ---
    if not animate:
        # Extraer coordenadas de la lista de tuplas 'pts'
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        
        # Dibujar en Cartesiano: puntos válidos (cian) e inválidos (rojos/x)
        ax1.scatter(xs, ys, s=6, c='cyan', alpha=0.8, label='Válidos')
        if len(inv_xs) > 0:
            ax1.scatter(inv_xs, inv_ys, s=4, c='red', marker='x', alpha=0.5, label='Inválidos')
        ax1.legend()
        
        # Dibujar en Polar: requiere ángulos en radianes y distancias en metros
        angles = np.deg2rad([p[3] for p in pts])
        dists = [p[4] for p in pts]
        ax2.scatter(angles, dists, s=6, c='magenta', alpha=0.8)

        # GUARDAR CAPTURA AUTOMÁTICA: Para documentación y reportes
        os.makedirs('docs/capturas', exist_ok=True)
        save_path = 'docs/capturas/live_view_csv.png'
        plt.savefig(save_path)
        print(f"\n[INFO] Captura CSV guardada automáticamente en {save_path}")

        plt.show()
        return

    # --- MODO ANIMADO (Simulación de Barrido Real-Time) ---
    xs, ys = [], []
    angles_anim, dists_anim = [], []
    
    # Inicializar objetos scatter vacíos para actualizar sus datos en el bucle
    scat_xy = ax1.scatter(xs, ys, s=6, c='cyan', alpha=0.8)
    scat_polar = ax2.scatter(angles_anim, dists_anim, s=6, c='magenta', alpha=0.8)
    
    plt.ion() # Activar modo interactivo de Matplotlib
    for i in range(0, len(pts), step):
        chunk = pts[i:i + step] # Procesar puntos en bloques para mayor fluidez
        
        # Actualización de datos Cartesianos (XY)
        xs.extend(p[0] for p in chunk)
        ys.extend(p[1] for p in chunk)
        scat_xy.set_offsets(list(zip(xs, ys))) # Actualizar posiciones en el gráfico
        
        # Actualización de datos Polares (Theta, R)
        angles_anim.extend(np.deg2rad([p[3] for p in chunk]))
        dists_anim.extend(p[4] for p in chunk)
        # Nota: set_offsets en proyecciones polares espera la tupla (theta, r)
        scat_polar.set_offsets(list(zip(angles_anim, dists_anim)))
        
        # Actualizar título dinámicamente con el progreso
        ax1.set_title(f'CSV animado | {len(xs)}/{n_valid} puntos trazados')
        plt.pause(0.001) # Forzar refresco de la interfaz gráfica
        time.sleep(delay) # Controlar la velocidad de la animación
        
    plt.ioff() # Desactivar modo interactivo al finalizar
    plt.show()

if __name__ == '__main__':
    # Configuración de argumentos por línea de comandos
    ap = argparse.ArgumentParser(description="Visualizador de Scans LiDAR")
    ap.add_argument('--csv',     default='data/scan_720.csv', help='Ruta al archivo CSV')
    ap.add_argument('--animate', action='store_true',          help='Animar llegada de puntos progresivamente')
    ap.add_argument('--step',    type=int,   default=20,       help='Puntos por cada actualización de frame')
    ap.add_argument('--delay',   type=float, default=0.02,     help='Segundos de espera entre frames')
    args = ap.parse_args()
    
    main(args.csv, args.animate, args.step, args.delay)