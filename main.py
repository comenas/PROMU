# main.py – Punto de entrada. Solo arranca la ventana.

import tkinter as tk
from UI import ANCHO, ALTO
from principal import pantalla_principal

root = tk.Tk()
root.title("Minecraft: Jump Edition")
root.geometry(f"{ANCHO}x{ALTO}")
root.resizable(False, False)

frame = tk.Frame(root, width=ANCHO, height=ALTO)
frame.place(x=0, y=0)

pantalla_principal(root, frame)
root.mainloop()