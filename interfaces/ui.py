import tkinter as tk
from PIL import Image, ImageTk, ImageFont, ImageDraw
 
ANCHO, ALTO = 1280, 960
 
# ── Componentes ───────────────────────────────────────────────────────────────
 
def crear_boton_imagen(frame, canvas, imagen_path, texto, fuente_path, fuente_size,
                       x, y, ancho, alto, comando):
    """
    Crea un botón con imagen de fondo y texto centrado,
    y lo coloca en el canvas en las coordenadas (x, y).
    """
    btn_img = Image.open(imagen_path).resize((ancho, alto), Image.LANCZOS)
    draw    = ImageDraw.Draw(btn_img)
    fuente  = ImageFont.truetype(fuente_path, fuente_size)
    bbox    = draw.textbbox((0, 0), texto, font=fuente)
    tx = (ancho - (bbox[2] - bbox[0])) // 2
    ty = (alto  - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), texto, font=fuente, fill="white")
    btn_tk = ImageTk.PhotoImage(btn_img)
    boton  = tk.Button(frame, image=btn_tk, borderwidth=0,
                       highlightthickness=0, cursor="hand2", command=comando)
    boton.image = btn_tk          # evita que el GC elimine la imagen
    canvas.create_window(x, y, window=boton)
    return boton
 
 
def crear_canvas(frame, imagen_path):
    """
    Crea un Canvas que ocupa toda la ventana y pone
    la imagen dada como fondo.
    """
    img    = Image.open(imagen_path).resize((ANCHO, ALTO), Image.LANCZOS)
    tk_img = ImageTk.PhotoImage(img)
    canvas = tk.Canvas(frame, width=ANCHO, height=ALTO, highlightthickness=0)
    canvas.place(x=0, y=0)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    canvas.image = tk_img         # evita que el GC elimine la imagen
    return canvas
 
 
def crear_entrada(frame, canvas, x, y, ancho, alto, imagen_caja, fuente, password=False):
    """
    Crea un campo de texto con imagen de fondo (caja) y lo coloca
    en el canvas en las coordenadas (x, y).
    """
    caja_img = Image.open(imagen_caja).resize((ancho, alto), Image.LANCZOS)
    caja_tk  = ImageTk.PhotoImage(caja_img)
    canvas.create_image(x, y, image=caja_tk, anchor="center")
    if not hasattr(canvas, "image_refs"):
        canvas.image_refs = []
    canvas.image_refs.append(caja_tk)   # evita que el GC elimine la imagen
    entrada = tk.Entry(
        frame,
        font=fuente,
        bg="#1a1108", fg="white",
        insertbackground="white",
        relief="flat", borderwidth=0,
        show="*" if password else ""
    )
    canvas.create_window(x, y, window=entrada, width=ancho - 10, height=alto - 10)
    return entrada
 
 
def limpiar_frame(frame):
    """Destruye todos los widgets hijos de un frame (cambio de pantalla)."""
    for widget in frame.winfo_children():
        widget.destroy()