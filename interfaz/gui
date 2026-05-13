from guizero import App
from PIL import Image, ImageTk, ImageFont, ImageDraw
import tkinter as tk
import ctypes
import os

# Registrar la fuente
ruta_fuente = os.path.abspath("fuente_minecraft.ttf")
ctypes.windll.gdi32.AddFontResourceW(ruta_fuente)

ANCHO, ALTO = 1280, 960

app = App(title="Minecraft: Jump Edition", width=ANCHO, height=ALTO)
app.tk.resizable(False, False)

# Fondo
img = Image.open("minecraft_fondo.png").resize((ANCHO, ALTO), Image.LANCZOS)
tk_img = ImageTk.PhotoImage(img)

canvas = tk.Canvas(app.tk, width=ANCHO, height=ALTO, highlightthickness=0)
canvas.place(x=0, y=0)
canvas.create_image(0, 0, anchor="nw", image=tk_img)

# Crear imagen del botón con texto encima
btn_img = Image.open("minecraft_boton.png").resize((440, 40), Image.LANCZOS)
draw = ImageDraw.Draw(btn_img)

# Escribir texto con la fuente Minecraft
fuente = ImageFont.truetype("fuente_minecraft.ttf", 18)
texto = "Iniciar sesión"

# Centrar el texto en el botón
bbox = draw.textbbox((0, 0), texto, font=fuente)
texto_ancho = bbox[2] - bbox[0]
texto_alto = bbox[3] - bbox[1]
x = (400 - texto_ancho) // 2
y = (40 - texto_alto) // 2

draw.text((x, y), texto, font=fuente, fill="white")

btn_tk = ImageTk.PhotoImage(btn_img)

# Botón transparente con la imagen
def iniciar_sesion():
    print("Iniciando sesión...")

boton = tk.Button(
    app.tk,
    image=btn_tk,
    borderwidth=0,
    highlightthickness=0,
    bg="#1a1a2e",        # color que no se note
    activebackground="#1a1a2e",
    cursor="hand2",
    command=iniciar_sesion
)

canvas.create_window(640, 480, window=boton)

app.display()