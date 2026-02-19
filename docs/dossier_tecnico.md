1)Un LiDAR 2D 360° es un sensor activo que mide distancias mediante tiempo de vuelo (Time of Flight) de pulsos láser.
El sistema emite un haz láser infrarrojo que, al impactar contra un objeto, se refleja y regresa al receptor del sensor. A partir del tiempo transcurrido entre emisión y recepción, el dispositivo calcula la distancia al obstáculo.
2)Campo de visión: 360°
Plano de medición: 2D (horizontal)
Rango típico: ~0.15 m – 6 a 12 m (según modelo)
Resolución angular: dependiente de la velocidad de giro (≈0.5° – 1°)
Frecuencia de muestreo: varios kHz
Velocidad de rotación: ~5–15 Hz
Interfaz: UART / USB
Longitud de onda del láser: infrarrojo (≈785 nm)
Clase láser: Clase 1 
📄 Referencia: Datasheet oficial de Slamtec RPLIDAR.
3) LiDAR ── UART ── USB ── PC
3.2) Normalmente 5 V por USB
3.3) Puesta en marcha,Conectar el LiDAR al PC, nstalar driver / librería
Formato de datos un ejemplo quality = 47
angle_deg = 90.5
dist_mm = 1320
