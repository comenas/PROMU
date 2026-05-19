from PIL import Image, ImageTk, ImageFont, ImageDraw
import tkinter as tk
import os
from guizero import App

# ── Rutas ──────────────────────────────────────────────────────────────────────
BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)

# ── Audio ──────────────────────────────────────────────────────────────────────
from audio import inicializar_audio, cargar_musica, reproducir_musica, ajustar_volumen, obtener_volumen

inicializar_audio()
try:
    cargar_musica(BASE)
    reproducir_musica(BASE)
    ajustar_volumen(50)
except FileNotFoundError as e:
    print(f"[Audio] {e} — la aplicación arrancará sin música.")

# ── Configuración visual ───────────────────────────────────────────────────────
ANCHO, ALTO = 1280, 960

# ── Utilidades PIL + tkinter ──────────────────────────────────────────────────

def crear_boton_imagen(frame, canvas, imagen_path, texto, fuente_size, x, y, ancho, alto, comando):
    btn_img = Image.open(imagen_path).resize((ancho, alto), Image.LANCZOS)
    draw = ImageDraw.Draw(btn_img)
    fuente = ImageFont.truetype(ruta("fuente_minecraft.ttf"), fuente_size)
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

def crear_canvas(frame, imagen_path, textos=None):
    img = Image.open(imagen_path).resize((ANCHO, ALTO), Image.LANCZOS)
    if textos:
        draw = ImageDraw.Draw(img)
        for t in textos:
            fuente = ImageFont.truetype(ruta("fuente_minecraft.ttf"), t["size"])
            bbox = draw.textbbox((0, 0), t["texto"], font=fuente)
            tx = t["x"] - (bbox[2] - bbox[0]) // 2
            ty = t["y"] - (bbox[3] - bbox[1]) // 2
            draw.text((tx, ty), t["texto"], font=fuente, fill=t.get("color", "white"))
    tk_img = ImageTk.PhotoImage(img)
    canvas = tk.Canvas(frame, width=ANCHO, height=ALTO, highlightthickness=0)
    canvas.place(x=0, y=0)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img
    return canvas

def crear_entrada(frame, canvas, x, y, ancho, alto, imagen_caja, password=False):
    caja_img = Image.open(imagen_caja).resize((ancho, alto), Image.LANCZOS)
    caja_tk = ImageTk.PhotoImage(caja_img)
    canvas.create_image(x, y, image=caja_tk, anchor="center")
    if not hasattr(canvas, "image_refs"):
        canvas.image_refs = []
    canvas.image_refs.append(caja_tk)
    entrada = tk.Entry(
        frame,
        font=("Courier", 14),
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

# ── Pantallas (todas usan el mismo frame) ─────────────────────────────────────

def pantalla_principal(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_fondo.png"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       25, x=645, y=490, ancho=452, alto=50,
                       comando=lambda: pantalla_inicio_sesion(frame))
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Continuar como invitado",
                       25, x=645, y=551, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(frame))
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Configuración",
                       25, x=645, y=612, ancho=452, alto=50,
                       comando=lambda: pantalla_configuracion(frame))
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Salir",
                       25, x=645, y=712, ancho=452, alto=50,
                       comando=app.destroy)

def pantalla_inicio_sesion(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"), textos=[
        {"texto": "Inicia sesión en el servidor UPV", "x": 640, "y": 250, "size": 24},
        {"texto": "Usuario",                          "x": 640, "y": 360, "size": 14},
        {"texto": "Contraseña",                       "x": 640, "y": 460, "size": 14},
    ])
    entrada_usuario = crear_entrada(frame, canvas, x=640, y=400, ancho=400, alto=40,
                                    imagen_caja=ruta("minecraft_caja.png"))
    entrada_password = crear_entrada(frame, canvas, x=640, y=500, ancho=400, alto=40,
                                     imagen_caja=ruta("minecraft_caja.png"), password=True)

    def iniciar_sesion():
        usuario = entrada_usuario.get()
        password = entrada_password.get()
        print(f"Usuario: {usuario} | Contraseña: {password}")

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       18, x=640, y=580, ancho=400, alto=40, comando=iniciar_sesion)
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       18, x=640, y=640, ancho=400, alto=40,
                       comando=lambda: pantalla_principal(frame))

def pantalla_invitado(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"), textos=[
        {"texto": "Rankings", "x": 640, "y": 300, "size": 30},
    ])
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking masculino",
                       20, x=640, y=450, ancho=452, alto=50,
                       comando=lambda: print("Ranking masculino"))
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking femenino",
                       20, x=640, y=520, ancho=452, alto=50,
                       comando=lambda: print("Ranking femenino"))
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       20, x=640, y=650, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(frame))

def pantalla_configuracion(frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"), textos=[
        {"texto": "Configuración",     "x": 640, "y": 250, "size": 30},
        {"texto": "Volumen de música", "x": 640, "y": 350, "size": 18},
    ])

    volumen = tk.IntVar(value=obtener_volumen())
    slider = tk.Scale(frame, from_=0, to=100, orient="horizontal", variable=volumen,
                      bg="#1a1108", fg="white", highlightthickness=0,
                      troughcolor="#3a3a3a", length=400, font=("Courier", 12), label="")
    canvas.create_window(640, 410, window=slider, width=400, height=50)

    etiqueta_vol = tk.Label(frame, text=f"{obtener_volumen()}%", font=("Courier", 14),
                            bg="#1a1108", fg="white")
    canvas.create_window(640, 460, window=etiqueta_vol)

    def actualizar_volumen(val):
        ajustar_volumen(int(val))
        etiqueta_vol.config(text=f"{val}%")

    slider.config(command=actualizar_volumen)
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       20, x=640, y=650, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(frame))

# ── Main con guizero ──────────────────────────────────────────────────────────

app = App(title="Minecraft: Jump Edition", width=ANCHO, height=ALTO)

# Frame tkinter sobre la ventana de guizero — aquí viven todas las pantallas
frame_principal = tk.Frame(app.tk, width=ANCHO, height=ALTO)
frame_principal.place(x=0, y=0)

pantalla_principal(frame_principal)

app.display()