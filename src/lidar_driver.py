"""
lidar_driver.py
Driver principal del RPLIDAR A1M8.
Propietarios: Sensores (diag/checklist) + LiDAR líder (frames/shutdown).
Uso:
 driver = LidarDriver('/dev/ttyUSB0')
 print(driver.diag())
 for frame in driver.frames():
 procesar(frame) # cada frame es un barrido completo 360°
 driver.shutdown_safe()
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Iterable, List, Tuple
from rplidar import RPLidar
# Tipo para cada punto: (quality, angle_deg, dist_mm)
ScanPoint = Tuple[int, float, float]
@dataclass
class ScanFrame:
 """Un barrido completo del sensor (aprox. 360°)."""
 t: float # timestamp Unix (time.time())
 pts: List[ScanPoint] # lista de (quality, angle_deg, dist_mm)
# ── Umbrales de filtrado (Sensores ajusta estos valores) ─────────────
QUALITY_MIN = 10 # descartar puntos con calidad menor
DIST_MIN_MM = 150.0 # 15 cm → mínimo físico del sensor
DIST_MAX_MM = 12000.0 # 12 m → máximo especificado
class LidarDriver:
 """Interfaz de alto nivel para el RPLIDAR A1M8."""
 def __init__(self, port: str) -> None:
 """ 
Inicializa la conexión con el sensor.
 Args:
 port: puerto serie (ej. '/dev/ttyUSB0' o 'COM5')
 """
 self.port = port
 self.lidar = RPLidar(port) # abre la conexión serie
 def diag(self) -> dict:
 """
 Lee info y health del sensor y devuelve un dict normalizado.
 Returns:
 dict con claves: model, firmware, hardware, status, error_code
 """
 info = self.lidar.get_info()
 health = self.lidar.get_health()
 # TODO [Sensores]: extraer y normalizar los campos del dict 'info'
 # y de la tupla 'health'. Ejemplo de estructura esperada:
 # info → {'model': X, 'firmware': (M,m), 'hardware': X, ...}
 # health → (status_str, error_code_int)
return {
        'model': info.get('model', 'Unknown'),         # Extrae el modelo (ej: 24)
        'firmware': info.get('firmware', (0, 0)),      # Extrae la versión (mayor, menor)
        'hardware': info.get('hardware', 0),           # Extrae la versión del hardware
        'status': health[0] if health else 'Unknown',  # 'Good', 'Warning' o 'Error'
        'error_code': health[1] if health else -1,     # Código numérico del error
        '_raw_info': info,                             # Mantenemos esto para depuración
        '_raw_health': health,
    }
 def frames(self, max_buf_meas: int = 500) -> Iterable[ScanFrame]:
 """ Generador que produce ScanFrames en tiempo real.
 Args:
 max_buf_meas: máximo de medidas en buffer interno (evita lag)
 Yields:
 ScanFrame con timestamp y lista de puntos filtrados.
 """
 for scan in self.lidar.iter_scans(max_buf_meas=max_buf_meas):
 pts: List[ScanPoint] = []
 for q, a, d in scan:
 # TODO [LiDAR líder]: añadir todos los filtros necesarios
 # Filtro básico de distancia y calidad:
 if d <= 0 or q < QUALITY_MIN:
 continue
 if not (DIST_MIN_MM <= d <= DIST_MAX_MM):
 continue
 pts.append((int(q), float(a), float(d)))
 if pts: # no emitir frames vacíos
 yield ScanFrame(t=time.time(), pts=pts)
 def shutdown_safe(self) -> None:
 """
 Parada segura del sensor.
 SIEMPRE llamar antes de cerrar el programa.
 Orden obligatorio: stop() → stop_motor() → disconnect()
 """
 try:
 self.lidar.stop() # detiene el escaneo
 self.lidar.stop_motor() # detiene el motor de rotación
 except Exception as e:
 print(f'[WARN] shutdown_safe: {e}')
 finally:
 self.lidar.disconnect() # cierra el puerto serie
# ── Ejecución directa: diagnóstico rápido ────────────────────────────
if __name__ == '__main__':
 import argparse
 ap = argparse.ArgumentParser()
 ap.add_argument('--port', required=True, help='Puerto serie del sensor')
 args = ap.parse_args()
 d = LidarDriver(args.port)
 print('Diagnóstico:', d.diag())
 print('Leyendo 3 frames...')
 count = 0
 for fr in d.frames():
 print(f' Frame {count}: {len(fr.pts)} puntos, t={fr.t:.2f}')
 count += 1
 if count >= 3:
 break
 d.shutdown_safe()
