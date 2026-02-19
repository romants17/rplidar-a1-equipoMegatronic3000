# Proyecto RPLidar A1 - Equipo Megatronic 3000

Bienvenido al repositorio oficial del **Equipo Megatronic 3000**. Este proyecto está enfocado en la implementación y el uso del sensor **RPLidar A1**.


## Descripción del Proyecto
Este repositorio contiene todo el código fuente, esquemas electrónicos y documentación necesaria para hacer funcionar el sensor LIDAR. El sistema permite escanear el entorno en 360 grados y obtener nubes de puntos en tiempo real.

## Requisitos del Sistema
Para que este proyecto funcione en tu computadora, asegúrate de tener:
* **Hardware:** * Sensor RPLidar A1 (Slamtec).
    * Cable USB conversor serial.
* **Software:**
    * Python 3.10 o superior (o Arduino IDE según tu caso).
    * Drivers de Silicon Labs (CP210x) instalados.

## Estructura del Repositorio
* `/src`: Código fuente principal (.py o .ino).
* `/docs`: Manuales del sensor y diagramas de conexión.
* `/examples`: Scripts de prueba para verificar el funcionamiento.
* `/data`: Capturas de escaneos realizados.

## Instalación y Uso Rápido
1. **Clonar o descargar** este repositorio.
2. **Conectar** el sensor al puerto USB de tu PC.
3. **Instalar dependencias** (si usas Python): pip install rplidar-roboticia matplotlib
4. Ejecutar el script de prueba: python main.py

## Integrantes del Equipo
Juan Cano Vicens - LIDAR
Roman Torres Santander - COMPUTACIÓN
Alejandro García Chirivella - ACTUADORES
Joan Corbera Vidal - VISIÓN
Sergio Fabian Felix - SENSORES
