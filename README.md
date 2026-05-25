# PROMU — Minecraft: Jump Edition

Analizador de saltos verticales a partir de archivos Excel (`.xlsx`) con aceleraciones en los ejes X, Y, Z. Calcula altura del salto por tres métodos físicos (tiempo de vuelo, velocidad de despegue, desplazamiento) y genera gráficas de aceleración, velocidad, fuerza, potencia y masa aparente.

---

## Requisitos

- Python 3.10 o superior
- pip

## Instalación en Thonny

### 1. Instalar dependencias

Abre la consola de Thonny (*Ver → Consola* o `Ctrl+J`) y ejecuta:

```
pip install numpy pandas scipy openpyxl Pillow pyglet matplotlib
```

O, si prefieres desde la terminal del sistema:

```bash
cd ruta/a/PROMU
pip install -r requirements.txt
```

### 2. Ejecutar

Dentro de Thonny, abre el archivo `main.py` y pulsa **Ejecutar** (F5).

También puedes ejecutar la interfaz de línea de comandos:

```
python interfaces/cli/cli.py
```

### 3. Archivo de prueba

En la carpeta `excel_salto/` hay un archivo de ejemplo (`archivo_salto.xlsx`) para probar el análisis.

---

## Estructura del proyecto

```
PROMU/
├── main.py                    # Punto de entrada (interfaz gráfica)
├── core/                      # Lógica de negocio
│   ├── data_loader.py         # Carga y validación de Excel
│   ├── matemáticas.py         # Procesamiento de señales
│   ├── fisica.py              # Cálculos físicos y gráficas
│   └── formatter.py           # Formateo de resultados
├── interfaces/
│   ├── cli/cli.py             # Interfaz de línea de comandos
│   └── guizero/               # Interfaz gráfica (Tkinter)
├── servidor/
│   └── red.py                 # Conexión TCP con el servidor
├── archivos_interfaz/         # Imágenes, audio, fuentes
├── excel_salto/               # Archivos Excel de ejemplo
└── tests/                     # Tests automatizados
```

---

## Servidor

La aplicación se conecta a un servidor remoto (`158.42.188.200:64010`) para autenticación, envío de saltos y consulta de rankings. Si el servidor no está disponible, la aplicación sigue funcionando en modo local.
