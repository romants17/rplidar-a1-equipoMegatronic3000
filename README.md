Se ha tenido que ejecutar el driver que se encuentra dentro de: CP210x_Universal_Windows_Driver.zip, la version de x64
# Instalar entorno
python -m venv .venv
source .venv\Scripts\activate # Windows
pip install -r requirements.txt
# Con sensor conectado
python src/view_live.py --port COM5 # Windows
python src/record_scan.py --port /dev/ttyUSB0 --seconds 10
# Sin sensor (modo CSV)
python src/view_live_csv.py --csv data/scan_720.csv --animate
python src/record_scan_csv.py --csv data/scan_720.csv --out docs

Puerto para el funcionamiento del LIDAR: COM3
Parada segura:
