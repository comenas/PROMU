from guizero import App
from PIL import Image, ImageTk, ImageFont, ImageDraw
import tkinter as tk

ANCHO, ALTO = 1280, 960

app = App(title="Minecraft: Jump Edition", width=ANCHO, height=ALTO)
app.tk.resizable(False, False)

# Fondo
img = Image.open("minecraft_fondo.png").resize((ANCHO, ALTO), Image.LANCZOS)
tk_img = ImageTk.PhotoImage(img)

canvas = tk.Canvas(app.tk, width=ANCHO, height=ALTO, highlightthickness=0)
canvas.place(x=0, y=0)
canvas.create_image(0, 0, anchor="nw", image=tk_img)

# Fuente Minecraft
fuente_minecraft = ("fuente_minecraft.ttf", 16)  # nombre del .ttf instalado

# Botón "Iniciar sesión"
def iniciar_sesion():
    print("Iniciando sesión...")

boton = tk.Button(
    app.tk,
    text="Iniciar sesión",
    font=fuente_minecraft,
    bg="#8B8B8B",        # gris estilo Minecraft
    fg="white",
    activebackground="#A8A8A8",
    relief="raised",
    borderwidth=3,
    width=20,
    height=2,
    command=iniciar_sesion
)

# Posición encima de la imagen (ajusta x, y a tu gusto)
canvas.create_window(640, 480, window=boton)

app.display()