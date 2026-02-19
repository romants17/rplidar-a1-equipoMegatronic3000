"""
view_live.py
Visualización en tiempo real del RPLIDAR A1M8.
Propietario: Visión Artificial.

Cómo funciona la visualización en tiempo real con matplotlib:
  - plt.ion()  activa el modo interactivo (no bloquea el hilo)
  - fig.canvas.draw() + fig.canvas.flush_events() refresca la ventana
  - Esto funciona bien hasta ~8 Hz (frecuencia de rotación del sensor)
  - Si se necesita mayor fluidez: explorar pyqtgraph o pygame

Uso:
    python src/view_live.py --port /dev/ttyUSB0 --range 6.0
"""
from __future__ import annotations
import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from lidar_driver import LidarDriver

def polar_to_xy(pts):
    """
    Convierte una lista de ScanPoints a arrays numpy X, Y.
    
    Args:
        pts: lista de tuplas (quality, angle_deg, dist_mm)
    Returns:
        x, y: arrays numpy en metros (solo válidos)
        q_valid: array numpy de calidades de puntos válidos
        total_pts: cantidad original de puntos recibidos
        valid_pts: cantidad de puntos tras el filtrado
    """
    q   = np.array([p[0] for p in pts], dtype=float)
    ang = np.deg2rad([p[1] for p in pts])
    r   = np.array([p[2] for p in pts], dtype=float) / 1000.0  # mm → m
    
    total_pts = len(pts)

    # IMPLEMENTACIÓN DEL FILTRO [Visión]:
    # Rango de distancia (0.15m a 6.0m) y calidad mínima (>= 10)
    mask = (r > 0.15) & (r < 6.0) & (q >= 10)
    
    ang_valid = ang[mask]
    r_valid = r[mask]
    q_valid = q[mask]

    x = r_valid * np.cos(ang_valid)
    y = r_valid * np.sin(ang_valid)
    
    valid_pts = len(x)
    
    return x, y, q_valid, total_pts, valid_pts

def main():
    """
    Punto de entrada principal. Gestiona el ciclo de vida del sensor 
    y la orquestación de la visualización dinámica.
    """
    ap = argparse.ArgumentParser(description='Visualización en tiempo real RPLIDAR')
    ap.add_argument('--port',  required=True,       help='Puerto serie (/dev/ttyUSB0 o COM5)')
    ap.add_argument('--range', type=float, default=6.0, help='Rango máximo a mostrar (metros)')
    args = ap.parse_args()

    # Inicializar driver y ventana matplotlib
    driver = LidarDriver(args.port)
    plt.ion()  # modo interactivo: no bloquea
    fig, ax = plt.subplots(figsize=(7, 7))
    # El origen (0,0) marcado con '^' (triángulo) representa el centro óptico del LIDAR. 
    # El grid con transparencia alpha=0.3 ayuda a estimar distancias a ojo 
    # sin saturar visualmente la nube de puntos (scatter).
    ax.set_aspect('equal', 'box')
    ax.set_xlim(-args.range, args.range)
    ax.set_ylim(-args.range, args.range)   
    ax.set_title('RPLIDAR A1M8 — Vista en tiempo real')
    ax.set_xlabel('X (m)  →  frente del sensor')
    ax.set_ylabel('Y (m)  →  izquierda del sensor')
    ax.grid(True, alpha=0.3)
    
    ax.plot(0, 0, 'r^', markersize=10, label='Sensor')  # posición del sensor
    ax.legend(loc='upper right')

    # Scatter vacío que actualizaremos en cada frame
    scat = ax.scatter([], [], s=4, c='cyan', alpha=0.8)
    
    # Texto de info en pantalla
    info_text = ax.text(-args.range + 0.1, args.range - 0.3, '',
                        fontsize=9, color='white',
                        bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))
    
    frame_count = 0
    capture_saved = False # Flag para guardar solo una vez y no saturar el disco

    try:
        for fr in driver.frames():
            x, y, q_valid, total_pts, valid_pts = polar_to_xy(fr.pts)
            
            # Actualizar puntos en el scatter
            scat.set_offsets(np.c_[x, y])
            
            # Actualizar información en pantalla (estadísticas)
            frame_count += 1
            pct_valid = (valid_pts / total_pts * 100) if total_pts > 0 else 0
            
            info_text.set_text(
                f'Frame: {frame_count}\n'
                f'Puntos: {valid_pts}/{total_pts}\n'
                f'Válidos: {pct_valid:.1f}%'
            )
            
            # Refrescar la ventana (clave para tiempo real)
            fig.canvas.draw()
            fig.canvas.flush_events()
            
            # IMPLEMENTACIÓN CAPTURA [Visión]:
            # Guardar captura automáticamente al llegar al frame 20 (para asegurar que hay datos en pantalla)
            if frame_count == 20 and not capture_saved:
                os.makedirs('docs/capturas', exist_ok=True)
                fig.savefig('docs/capturas/live_view.png')
                print('\n[INFO] Captura automática guardada en docs/capturas/live_view.png')
                capture_saved = True

    except KeyboardInterrupt:
        print('\n[INFO] Detenido por el usuario (Ctrl+C)')
    finally:
        driver.shutdown_safe()  # SIEMPRE parar el sensor al salir

if __name__ == '__main__':
    main()
    