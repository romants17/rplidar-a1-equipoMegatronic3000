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
import argparse
from dataclasses import dataclass
from typing import List

# Header exacto que debe tener el CSV (no modificar)
CSV_HEADER = ['quality', 'angle', 'measure_m', 'ok']

@dataclass
class LidarSample:
    """Una muestra individual del CSV (equivale a un ScanPoint + flag ok)."""
    quality: int      # calidad de la medida [0-255]
    angle: float      # ángulo en grados [0, 360)
    measure_m: float  # distancia en metros
    ok: int           # 1 = válida según el sensor, 0 = sospechosa

def read_scan_csv(path: str) -> List[LidarSample]:
    """
    Lee el CSV y devuelve una lista de LidarSample.
    Lanza ValueError si el header no coincide exactamente con CSV_HEADER.
    """
    samples: List[LidarSample] = []
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validación de cabecera
        if list(reader.fieldnames) != CSV_HEADER:
            raise ValueError(
                f'Header inválido.\n'
                f'Esperado: {CSV_HEADER}\n'
                f'Recibido: {reader.fieldnames}'
            )
            
        for row in reader:
            samples.append(LidarSample(
                quality=int(row['quality']),
                angle=float(row['angle']),
                measure_m=float(row['measure_m']),
                ok=int(row['ok']),
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

def detect_outliers(samples: List[LidarSample]) -> List[dict]:
    """
    Identifica puntos que no cumplen con los estándares de calidad.
    """
    outliers = []
    for i, s in enumerate(samples):
        # Criterios de fallo (basados en especificaciones técnicas del A1M8)
        motivo = []
        
        # Rango mínimo físico (aprox 15cm)
        if s.measure_m <= 0.15: 
            motivo.append("Demasiado cerca/Zero")
            
        # Rango máximo teórico (12m para A1M8)
        if s.measure_m > 12.0: 
            motivo.append("Fuera de rango max")
            
        # Calidad mínima para navegación confiable
        if s.quality < 20: 
            motivo.append("Baja calidad")
        
        if motivo:
            outliers.append({
                'index': i,
                'angle': s.angle,
                'dist': s.measure_m,
                'reasons': motivo
            })
    return outliers

# ── Ejecución del script ─────────────────────────────────────────────

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='data/scan_720.csv', help='Ruta al archivo CSV')
    args = ap.parse_args()

    try:
        # 1. Cargar datos
        scan_data = read_scan_csv(args.csv)
        
        # 2. Análisis de salud general
        health = dataset_health(scan_data)
        print(f"--- Dataset Health ({args.csv}) ---")
        for k, v in health.items():
            print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
        
        # 3. Detección de problemas
        problematic_points = detect_outliers(scan_data)
        print(f"\nSe encontraron {len(problematic_points)} puntos problemáticos.")
        
        if problematic_points:
            print("\nEjemplos de outliers (primeros 5):")
            for p in problematic_points[:5]:
                print(f"  - Índice {p['index']} (Ang: {p['angle']}°): {', '.join(p['reasons'])}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {args.csv}")
    except ValueError as e:
        print(f"Error de validación: {e}")