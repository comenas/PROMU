from PIL import Image, ImageTk, ImageFont, ImageDraw
import tkinter as tk
import os

# Ruta base: carpeta donde está este archivo
BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)

fuente = ImageFont.truetype(ruta("fuente_minecraft.ttf"), size=24)
# ── Audio ──────────────────────────────────────────────────────────────────────
from audio import inicializar_audio, cargar_musica, reproducir_musica, ajustar_volumen, obtener_volumen

# Inicializa pygame mixer y arranca la música al importar el módulo
inicializar_audio()
try:
    cargar_musica("wet hands.mp3")
    reproducir_musica()
    ajustar_volumen(50)           # volumen inicial 50 %
except FileNotFoundError as e:
    print(f"[Audio] {e} — la aplicación arrancará sin música.")

# ── Configuración visual ───────────────────────────────────────────────────────
fuente = ImageFont.truetype(ruta("fuente_minecraft.ttf"), size=24)
ANCHO, ALTO = 1280, 960

# ── Utilidades ────────────────────────────────────────────────────────────────

def crear_boton_imagen(frame, canvas, imagen_path, texto, fuente_path, fuente_size, x, y, ancho, alto, comando):
    btn_img = Image.open(imagen_path).resize((ancho, alto), Image.LANCZOS)
    draw = ImageDraw.Draw(btn_img)
    fuente = ImageFont.truetype(fuente_path, fuente_size)
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    tx = (ancho - (bbox[2] - bbox[0])) // 2
    ty = (alto  - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), texto, font=fuente, fill="white")
    btn_tk = ImageTk.PhotoImage(btn_img)
    boton = tk.Button(frame, image=btn_tk, borderwidth=0,
                      highlightthickness=0, cursor="hand2", command=comando)
    boton.image = btn_tk
    canvas.create_window(x, y, window=boton)
    return boton

def crear_canvas(frame, imagen_path):
    img = Image.open(imagen_path).resize((ANCHO, ALTO), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(img)
    canvas = tk.Canvas(frame, width=ANCHO, height=ALTO, highlightthickness=0)
    canvas.place(x=0, y=0)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img
    return canvas

def crear_entrada(frame, canvas, x, y, ancho, alto, imagen_caja, fuente, password=False):
    caja_img = Image.open(imagen_caja).resize((ancho, alto), Image.LANCZOS)
    caja_tk = ImageTk.PhotoImage(caja_img)
    canvas.create_image(x, y, image=caja_tk, anchor="center")
    if not hasattr(canvas, "image_refs"):
        canvas.image_refs = []
    canvas.image_refs.append(caja_tk)
    entrada = tk.Entry(
        frame,
        font=fuente,
        bg="#1a1108",
        fg="white",
        insertbackground="white",
        relief="flat",
        borderwidth=0,
        show="*" if password else ""
    )
    canvas.create_window(x, y, window=entrada, width=ancho - 10, height=alto - 10)
    return entrada

def limpiar_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

# ── Pantallas ─────────────────────────────────────────────────────────────────

def pantalla_principal(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_fondo.png"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=490, ancho=452, alto=50,
                       comando=lambda: pantalla_inicio_sesion(frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Continuar como invitado",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=551, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Configuración",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=612, ancho=452, alto=50,
                       comando=lambda: pantalla_configuracion(frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Salir",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=712, ancho=452, alto=50,
                       comando=root.destroy)

def pantalla_inicio_sesion(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 250, text="Inicia sesión en el servidor UPV",
                       font=("Minecraft", 24), fill="white", anchor="center")

    canvas.create_text(640, 360, text="Usuario",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_usuario = crear_entrada(frame, canvas, x=640, y=400, ancho=400, alto=40,
                                    imagen_caja=ruta("minecraft_caja.png"), fuente=fuente_mc)

    canvas.create_text(640, 460, text="Contraseña",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_password = crear_entrada(frame, canvas, x=640, y=500, ancho=400, alto=40,
                                     imagen_caja=ruta("minecraft_caja.png"), fuente=fuente_mc, password=True)

    def iniciar_sesion():
        usuario = entrada_usuario.get()
        password = entrada_password.get()
        print(f"Usuario: {usuario} | Contraseña: {password}")

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       ruta("fuente_minecraft.ttf"), 18,
                       x=640, y=580, ancho=400, alto=40,
                       comando=iniciar_sesion)

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 18,
                       x=640, y=640, ancho=400, alto=40,
                       comando=lambda: pantalla_principal(frame))

def pantalla_invitado(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    canvas.create_text(640, 300, text="Rankings",
                       font=("Minecraft", 30), fill="white", anchor="center")

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking masculino",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=450, ancho=452, alto=50,
                       comando=lambda: print("Ranking masculino"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking femenino",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=520, ancho=452, alto=50,
                       comando=lambda: print("Ranking femenino"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=650, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(frame))

def pantalla_configuracion(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    canvas.create_text(640, 250, text="Configuración",
                       font=("Minecraft", 30), fill="white", anchor="center")

    canvas.create_text(640, 380, text="Volumen de música",
                       font=("Minecraft", 18), fill="white", anchor="center")

    # Slider — valor inicial igual al volumen actual de pygame
    volumen = tk.IntVar(value=obtener_volumen())

    slider = tk.Scale(
        frame,
        from_=0, to=100,
        orient="horizontal",
        variable=volumen,
        bg="#1a1108",
        fg="white",
        highlightthickness=0,
        troughcolor="#3a3a3a",
        length=400,
        font=("Minecraft", 12),
        label=""
    )
    canvas.create_window(640, 430, window=slider, width=400, height=50)

    etiqueta_vol = tk.Label(frame, text=f"{obtener_volumen()}%", font=("Minecraft", 14),
                            bg="#1a1108", fg="white")
    canvas.create_window(640, 480, window=etiqueta_vol)

    def actualizar_volumen(val):
        """Cambia el volumen en pygame y actualiza la etiqueta."""
        ajustar_volumen(int(val))
        etiqueta_vol.config(text=f"{val}%")

    slider.config(command=actualizar_volumen)

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=650, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(frame))

# ── Main ──────────────────────────────────────────────────────────────────────

root = tk.Tk()
root.title("Minecraft: Jump Edition")
root.geometry(f"{ANCHO}x{ALTO}")
root.resizable(False, False)

frame = tk.Frame(root, width=ANCHO, height=ALTO)
frame.place(x=0, y=0)

pantalla_principal(frame)

root.mainloop()