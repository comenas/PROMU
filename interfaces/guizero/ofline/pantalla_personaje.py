import tkinter as tk
from PIL import Image, ImageTk
import os
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, limpiar_frame

BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF  = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)


# ── Criterios de asignación ───────────────────────────────────────────────────
def asignar_personaje(altura_m):
    """Devuelve (nombre, archivo_imagen, color, descripcion) según h1 en metros."""
    cm = altura_m * 100
    if cm <= 15:
        return ("Slime",        "slime.png",        "#55ff55",
                "Pequeño pero pegajoso.\n¡Sigue saltando!")
    elif cm <= 30:
        return ("Lobo",         "lobo.png",         "#aaaaff",
                "Fiel y persistente.\n¡Buen salto!")
    elif cm <= 45:
        return ("Creeper",      "creeper.png",      "#44cc44",
                "Explosivo en la pista.\n¡Muy bien!")
    elif cm <= 59:
        return ("Enderman",     "enderman.png",     "#cc88ff",
                "Largo y veloz.\n¡Impresionante!")
    else:
        return ("Ender Dragon", "ender_dragon.png", "#aa00ff",
                "El jefe definitivo.\n¡Eres una leyenda!")


def pantalla_personaje(root, frame, h1, volver_fn=None):
    """
    Muestra el personaje asignado según h1 (metros).
    volver_fn: callable sin argumentos para el botón Volver.
               Si es None, vuelve a pantalla_gestion_salto (modo offline).
    """
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    nombre, img_archivo, color, descripcion = asignar_personaje(h1)
    altura_cm = h1 * 100

    # ── Título ────────────────────────────────────────────────────────────────
    canvas.create_text(640, 90, text="Tu personaje",
                       font=("Minecraft", 30), fill="white", anchor="center")

    # ── Altura conseguida ─────────────────────────────────────────────────────
    canvas.create_text(640, 150, text=f"Altura de vuelo: {altura_cm:.1f} cm",
                       font=("Minecraft", 16), fill="#ffff55", anchor="center")

    # ── Imagen del personaje ──────────────────────────────────────────────────
    try:
        img_pil = Image.open(ruta(img_archivo)).resize((280, 280), Image.NEAREST)
        img_tk  = ImageTk.PhotoImage(img_pil)
        canvas.create_image(640, 370, image=img_tk, anchor="center")
        canvas._personaje_img = img_tk
    except Exception:
        canvas.create_text(640, 370, text="[imagen no disponible]",
                           font=("Minecraft", 13), fill="#ff5555", anchor="center")

    # ── Nombre ────────────────────────────────────────────────────────────────
    canvas.create_text(640, 535, text=nombre,
                       font=("Minecraft", 28), fill=color, anchor="center")

    # ── Descripción ───────────────────────────────────────────────────────────
    canvas.create_text(640, 595, text=descripcion,
                       font=("Minecraft", 14), fill="#dddddd",
                       anchor="center", justify="center")

    # ── Barra de nivel ────────────────────────────────────────────────────────
    _dibujar_barra_nivel(canvas, altura_cm)

    # ── Botón de info ─────────────────────────────────────────────────────────
    def mostrar_info():
        ventana = tk.Toplevel(root)
        ventana.title("Criterios de asignación")
        ventana.configure(bg="#1a1108")
        ventana.resizable(False, False)
        ventana.geometry("520x400")
        ventana.grab_set()

        tk.Label(ventana, text="¿Qué personaje eres?",
                 font=("Minecraft", 16), bg="#1a1108", fg="white").pack(pady=(20, 14))

        criterios = [
            ("Slime",        " 0 – 15 cm",  "#55ff55"),
            ("Lobo",         "16 – 30 cm",  "#aaaaff"),
            ("Creeper",      "31 – 45 cm",  "#44cc44"),
            ("Enderman",     "46 – 59 cm",  "#cc88ff"),
            ("Ender Dragon", "60+ cm",      "#aa00ff"),
        ]
        for n, r, c in criterios:
            fila = tk.Frame(ventana, bg="#1a1108")
            fila.pack(fill="x", padx=50, pady=5)
            tk.Label(fila, text=f"▸ {n:<15}", font=("Minecraft", 13),
                     bg="#1a1108", fg=c, anchor="w").pack(side="left")
            tk.Label(fila, text=r, font=("Minecraft", 13),
                     bg="#1a1108", fg="white", anchor="w").pack(side="left")

        tk.Button(ventana, text="Cerrar", font=("Minecraft", 13),
                  bg="#2a2118", fg="white", relief="flat", bd=0,
                  activebackground="#3a3128", activeforeground="white",
                  cursor="hand2", padx=20, pady=6,
                  command=ventana.destroy).pack(pady=22)

    crear_boton_imagen(frame, canvas, ruta("info.png"), "",
                       ruta("fuente_minecraft.ttf"), 1,
                       x=50, y=910, ancho=50, alto=50,
                       comando=mostrar_info)

    # ── Botón Volver ──────────────────────────────────────────────────────────
    if volver_fn is None:
        from interfaces.guizero.ofline.gestionar_salto_invitado import pantalla_gestion_salto
        volver_fn = lambda: pantalla_gestion_salto(root, frame)

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=760, ancho=452, alto=50,
                       comando=volver_fn)


def _dibujar_barra_nivel(canvas, altura_cm):
    """Barra de progreso por segmentos de color, uno por nivel."""
    niveles = ["#55ff55", "#aaaaff", "#44cc44", "#cc88ff", "#aa00ff"]
    BAR_X0, BAR_Y = 240, 660
    SEG_W, SEG_H, GAP = 148, 18, 4
    cap      = 80.0
    progreso = min(altura_cm, cap) / cap

    total_px = 5 * SEG_W + 4 * GAP
    fill_px  = progreso * total_px

    x = BAR_X0
    restante = fill_px
    for color in niveles:
        canvas.create_rectangle(x, BAR_Y, x + SEG_W, BAR_Y + SEG_H,
                                 fill="#2a2118", outline="#444444")
        ancho_relleno = max(0, min(restante, SEG_W))
        if ancho_relleno > 0:
            canvas.create_rectangle(x, BAR_Y, x + ancho_relleno, BAR_Y + SEG_H,
                                     fill=color, outline="")
        restante -= SEG_W
        x += SEG_W + GAP

    canvas.create_text(640, BAR_Y + SEG_H + 16,
                       text=f"{progreso * 100:.0f}% del máximo",
                       font=("Minecraft", 11), fill="#888888", anchor="center")