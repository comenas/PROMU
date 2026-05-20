# main.py – Punto de entrada. Arranca la ventana y la música.

import tkinter as tk
from interfaces.ui import ANCHO, ALTO
from interfaces.principal import pantalla_principal
from interfaces.audio import cargar_musica, reproducir_musica, ajustar_volumen
import os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "archivos_interfaz")

root = tk.Tk()
root.title("Minecraft: Jump Edition")
root.geometry(f"{ANCHO}x{ALTO}")
root.resizable(False, False)

# ── Audio ──────────────────────────────────────────────────────────────────────
try:
    cargar_musica(BASE)
    reproducir_musica(BASE)
    ajustar_volumen(50)
except FileNotFoundError as e:
    print(f"[Audio] {e} — la aplicación arrancará sin música.")

# ── Pantalla inicial ───────────────────────────────────────────────────────────
frame = tk.Frame(root, width=ANCHO, height=ALTO)
frame.place(x=0, y=0)

pantalla_principal(root, frame)
root.mainloop()
