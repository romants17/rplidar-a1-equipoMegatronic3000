"""
utils.py
Máquina de estados (FSM) y checklist de arranque/parada para el sistema LiDAR.
Propietario: Actuadores.

Estados FSM (sensor conectado):
      INIT
       │ (diag_ok)
       ▼
      DIAG
       │ (start)
       ▼
      SCAN
       │ (stop)
       ▼
      STOP
       │ (cualquier evento)
       ▼
      DONE

* Nota: Cualquier estado puede transicionar a ERROR mediante el evento 'error' o 'diag_fail'.

Eventos posibles: 'diag_ok', 'diag_fail', 'start', 'stop', 'error'
"""
from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass


class State(Enum):
    """Estados posibles del sistema de control del LiDAR."""
    INIT  = auto()  # Estado inicial, esperando que el checklist se valide al 100%
    DIAG  = auto()  # Ejecutando diagnóstico del sensor (extrayendo health/info)
    SCAN  = auto()  # Escaneo activo, el motor gira y el láser emite
    STOP  = auto()  # Parada solicitada, ejecutando la secuencia shutdown_safe()
    DONE  = auto()  # Finalización limpia y desconexión exitosa del puerto
    ERROR = auto()  # Error irrecuperable (ej. desconexión abrupta, fallo de hardware)


@dataclass
class Checklist:
    """
    Checklist de arranque. Todos los campos obligatoriamente deben ser True
    antes de permitir que el sistema intente conectarse (transición INIT → DIAG).
    """
    lidar_fijo:       bool = False  # El sensor está atornillado o fijado a la mesa/robot
    cable_ok:         bool = False  # El cable USB tiene holgura y no se enredará al girar
    parada_probada:   bool = False  # Se comprende y ha verificado el uso de shutdown_safe()
    puerto_correcto:  bool = False  # Se ha comprobado en el SO el puerto (COMx o /dev/ttyUSBx)


def transition(state: State, event: str) -> State:
    """
    Función pura de transición de estado que define el comportamiento del sistema.

    Args:
        state: Estado actual de la FSM.
        event: Evento en formato string que dispara la transición.
    Returns:
        El nuevo estado resultante tras evaluar la regla de transición.
    """
    # Regla de seguridad global: el evento 'error' siempre aborta al estado ERROR
    # sin importar en qué punto del ciclo de vida estemos.
    if event == 'error':
        return State.ERROR

    # Diccionario con las transiciones legales de la máquina de estados.
    # Formato: (Estado_Actual, Evento): Estado_Siguiente
    transitions = {
        (State.INIT,  'diag_ok'):   State.DIAG,   # Checklist superado y conexión inicial exitosa
        (State.INIT,  'diag_fail'): State.ERROR,  # Fallo al intentar conectar con el sensor
        (State.DIAG,  'start'):     State.SCAN,   # Diagnóstico de salud OK, arranca el motor
        (State.SCAN,  'stop'):      State.STOP,   # Solicitud de parada (ej. usuario presiona Ctrl+C)
        (State.STOP,  'diag_ok'):   State.DONE,   # Apagado finalizado con éxito (usamos diag_ok genérico o cualquier otro)
        (State.STOP,  'start'):     State.DONE,   # Una vez en STOP, cualquier evento finaliza el ciclo
        (State.STOP,  'stop'):      State.DONE,
    }
    
    # Si la combinación (estado_actual, evento) existe, devuelve el nuevo estado.
    # Si no es una transición válida, ignora el evento y mantiene el estado actual.
    return transitions.get((state, event), state)


if __name__ == '__main__':
    # Demo de la FSM para verificar en consola que el flujo funciona correctamente
    check = Checklist(lidar_fijo=True, cable_ok=True,
                      parada_probada=True, puerto_correcto=True)
                      
    print('Checklist OK:', all([check.lidar_fijo, check.cable_ok,
                                check.parada_probada, check.puerto_correcto]))
                                
    st = State.INIT
    # Simulamos el flujo de vida normal de una ejecución
    for evento in ['diag_ok', 'start', 'stop']:
        st = transition(st, evento)
        print(f'  Evento: {evento!r:12}  → Estado: {st.name}')