"""
utils_csv.py
FSM para el pipeline CSV completo (sin sensor físico).
Propietario: Actuadores.

Diagrama de Estados FSM (pipeline CSV):
      INIT 
       │ (csv existe y cabecera ok)
       ▼
      LOAD 
       │ (filtrado y proyección XY)
       ▼
     PROCESS 
       │ (guardado en disco)
       ▼
      SAVE 
       │ (cierre limpio)
       ▼
    SHUTDOWN

* Nota: Un fallo (exception) en cualquier paso deriva inmediatamente al estado ERROR.

La parada segura aquí es simbólica (no hay motor real).
En la integración con hardware real se llama a shutdown_safe() del driver.
"""
from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class State(Enum):
    """Estados del pipeline de procesamiento de datos por CSV."""
    INIT       = auto()  # Estado de reposo, esperando validación del checklist inicial
    LOAD       = auto()  # Cargando archivo CSV en memoria y validando estructura
    PROCESS    = auto()  # Aplicando is_valid() y polar_to_xy() sobre las muestras
    SAVE       = auto()  # Guardando filtered_points.csv y report_scan.md
    SHUTDOWN   = auto()  # Liberando recursos (parada segura completada)
    ERROR      = auto()  # Fallo en algún paso (archivo no encontrado, disco lleno, etc.)


@dataclass
class Checklist:
    """Checklist de validación lógica previa al pipeline CSV."""
    csv_exists:       bool = False  # El archivo CSV existe en la ruta especificada
    header_ok:        bool = False  # El header coincide con ['quality', 'angle', 'measure_m', 'ok']
    scan_length_ok:   bool = False  # El CSV tiene el nº esperado de filas (≥720)
    processed_ok:     bool = False  # El filtrado/proyección se completó sin lanzar excepciones
    files_saved_ok:   bool = False  # Los archivos generados se escribieron con éxito en docs/

# REGLAS DE SEGURIDAD FÍSICA (Hardware Real) documentadas por Actuadores:
# 1. El LiDAR debe montarse sobre una base estable; un vuelco con el motor a 10 Hz dañará la correa.
# 2. No interrumpir la alimentación USB repentinamente; usar siempre stop_motor() primero.
# 3. Mantener los ojos alejados del plano de barrido del láser (aunque sea clase 1).
# 4. Asegurar que los cables del adaptador USB UART no toquen la parte giratoria del cabezal.


def shutdown_safe() -> bool:
    """
    Parada segura.
    En la versión CSV es simbólica. En la versión con hardware real (record_scan.py / view_live.py), 
    este estado garantiza que se invoque driver.shutdown_safe() (LidarDriver).
    
    Returns:
        True si la parada fue limpia.
    """
    # En un script de integración unificada, haríamos algo como:
    # if hasattr(driver, 'shutdown_safe'): driver.shutdown_safe()
    print('[FSM] Parada segura ejecutada (modo CSV: recursos liberados).')
    return True


def run_fsm(check: Checklist) -> State:
    """
    Ejecuta la FSM del pipeline CSV.
    Avanza linealmente por los estados comprobando el checklist de validaciones en cada transición.
    Si alguna comprobación falla, aborta a ERROR y ejecuta shutdown_safe().
    """
    st = State.INIT
    try:
        # Transición INIT → LOAD
        st = State.LOAD
        if not (check.csv_exists and check.header_ok and check.scan_length_ok):
            raise ValueError('Fallo en LOAD: CSV no válido, estructura corrupta o incompleto.')

        # Transición LOAD → PROCESS
        st = State.PROCESS
        if not check.processed_ok:
            raise ValueError('Fallo en PROCESS: error matemático en filtrado o proyección.')

        # Transición PROCESS → SAVE
        st = State.SAVE
        if not check.files_saved_ok:
            raise ValueError('Fallo en SAVE: permisos denegados o disco lleno al guardar los archivos.')

        # Transición SAVE → SHUTDOWN
        st = State.SHUTDOWN
        shutdown_safe()
        return State.SHUTDOWN

    except Exception as e:
        # Cualquier excepción levantada nos lleva a un estado de fallo controlado
        print(f'[FSM] ERROR crítico en estado {st.name}: {e}')
        shutdown_safe()  # Aseguramos que siempre haya cierre limpio, incluso en fallo
        return State.ERROR


if __name__ == '__main__':
    # Demo: simular un pipeline de procesamiento CSV exitoso
    print("--- Simulando FSM Exitosa ---")
    check_ok = Checklist(
        csv_exists=True, header_ok=True, scan_length_ok=True,
        processed_ok=True, files_saved_ok=True
    )
    final_ok = run_fsm(check_ok)
    print(f'Estado final: {final_ok.name}\n')

    # Demo: simular un fallo en el proceso
    print("--- Simulando FSM con Fallo ---")
    check_fail = Checklist(
        csv_exists=True, header_ok=True, scan_length_ok=True,
        processed_ok=False, files_saved_ok=False # Fallará en PROCESS
    )
    final_fail = run_fsm(check_fail)
    print(f'Estado final: {final_fail.name}')