"""
lidar_driver_csv.py
Versión del driver que lee desde un CSV de referencia en lugar del sensor.
Propietario: Sensores.
Formato del CSV (header obligatorio):
 quality, angle, measure_m, ok
Uso:
 samples = read_scan_csv('data/scan_720.csv')
 print(dataset_health(samples))
"""
from __future__ import annotations
import csv
from dataclasses import dataclass
from typing import List
# Header exacto que debe tener el CSV (no modificar)
CSV_HEADER = ['quality', 'angle', 'measure_m', 'ok']
@dataclass
class LidarSample:
"""Una muestra individual del CSV (equivale a un ScanPoint + flag ok)."""

 quality: int # calidad de la medida [0-255]
 angle: float # ángulo en grados [0, 360)
 measure_m: float # distancia en metros
 ok: int # 1 = válida según el sensor, 0 = sospechosa
def read_scan_csv(path: str) -> List[LidarSample]:
 """
 Lee el CSV y devuelve una lista de LidarSample.
 Lanza ValueError si el header no coincide exactamente con CSV_HEADER.
 """
 samples: List[LidarSample] = []
 with open(path, 'r', newline='', encoding='utf-8') as f:
 reader = csv.DictReader(f)
 if list(reader.fieldnames) != CSV_HEADER:
 raise ValueError(
 f'Header inválido.\n'
 f'Esperado: {CSV_HEADER}\n'
 f'Recibido: {reader.fieldnames}'
 )
 for row in reader:
 samples.append(LidarSample(
 quality = int(row['quality']),
 angle = float(row['angle']),
 measure_m = float(row['measure_m']),
 ok = int(row['ok']),
 ))
 return samples
def dataset_health(samples: List[LidarSample]) -> dict:
 """
 Resumen estadístico del dataset, análogo a get_health() del sensor real.
 """
 n = len(samples)
 if n == 0:
 return {'count': 0}
 measures = [s.measure_m for s in samples]
 qualities = [s.quality for s in samples]
 angles = [s.angle for s in samples]
 return {
 'count': n,
 'ok_ratio': sum(1 for s in samples if s.ok == 1) / n,
 'quality_min': min(qualities),
 'quality_max': max(qualities),
 'quality_mean': sum(qualities) / n,
 'measure_min_m': min(measures),
 'measure_max_m': max(measures),
 'angle_min_deg': min(angles),
 'angle_max_deg': max(angles),
 }

# Dentro de lidar_driver_csv.py

def detect_outliers(samples: List[LidarSample]):
    """
    Identifica puntos que no cumplen con los estándares de calidad.
    """
    outliers = []
    for i, s in enumerate(samples):
        # Criterios de fallo (basados en especificaciones técnicas)
        motivo = []
        if s.measure_m <= 0.15: # [cite: 16, 261]
            motivo.append("Demasiado cerca/Zero")
        if s.measure_m > 12.0: # [cite: 16, 262]
            motivo.append("Fuera de rango max")
        if s.quality < 20: # [cite: 178, 198]
            motivo.append("Baja calidad")
        
        if motivo:
            outliers.append({
                'index': i,
                'angle': s.angle,
                'dist': s.measure_m,
                'reasons': motivo
            })
    return outliers

if __name__ == '__main__':
 

 import argparse
 ap = argparse.ArgumentParser()
 ap.add_argument('--csv', default='data/scan_720.csv')
 args = ap.parse_args()
 scan = read_scan_csv(args.csv)
 print('Dataset health:', dataset_health(scan))
 # TODO [Sensores]: añadir detección de outliers:
 # measure_m == 0, measure_m > 10, quality < umbral, etc.
 # Generar un informe en docs/ con las métricas y los casos problemáticos.
