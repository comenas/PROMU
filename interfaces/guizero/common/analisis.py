import tkinter as tk
from tkinter import filedialog
import os
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, crear_entrada, limpiar_frame

BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)


def pantalla_analisis(root, frame):
    """Pantalla de análisis local: elige xlsx + peso y abre las 6 gráficas."""
    limpiar_frame(frame)
    canvas    = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 195, text="Analizar Salto",
                       font=("Minecraft", 28), fill="white", anchor="center")

    # ── Selector de archivo ───────────────────────────────────────────────────
    ruta_xlsx = tk.StringVar(value="")

    canvas.create_text(640, 300, text="Archivo de datos (.xlsx)",
                       font=("Minecraft", 14), fill="white", anchor="center")

    lbl_archivo = tk.Label(frame, text="Sin archivo seleccionado",
                           font=("Minecraft", 11), bg="#1a1108", fg="#aaaaaa",
                           wraplength=500, anchor="center")
    canvas.create_window(640, 335, window=lbl_archivo, width=520, height=28)

    def seleccionar_archivo():
        path = filedialog.askopenfilename(
            title="Selecciona el archivo de datos",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")]
        )
        if path:
            ruta_xlsx.set(path)
            lbl_archivo.config(text=os.path.basename(path), fg="#55ff55")

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Seleccionar archivo",
                       ruta("fuente_minecraft.ttf"), 16,
                       x=640, y=378, ancho=400, alto=40,
                       comando=seleccionar_archivo)

    # ── Peso ─────────────────────────────────────────────────────────────────
    canvas.create_text(640, 434, text="Peso (kg)",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_peso = crear_entrada(frame, canvas, x=640, y=472, ancho=300, alto=40,
                                 imagen_caja=ruta("minecraft_caja.png"), fuente=fuente_mc)

    # ── Mensaje de estado ────────────────────────────────────────────────────
    _timer = [None]
    msg_id = canvas.create_text(640, 525, text="",
                                font=("Minecraft", 13), fill="#ff5555", anchor="center")

    def mostrar_mensaje(texto, color="#ff5555", duracion_ms=3000):
        canvas.itemconfig(msg_id, text=texto, fill=color)
        if _timer[0]:
            root.after_cancel(_timer[0])
        if duracion_ms > 0:
            _timer[0] = root.after(duracion_ms,
                                   lambda: canvas.itemconfig(msg_id, text=""))

    # ── Botón ver gráficas ───────────────────────────────────────────────────
    def ver_graficas():
        from core.fisica import abrir_graficas_en_hilo

        path     = ruta_xlsx.get()
        peso_str = entrada_peso.get().strip().replace(",", ".")

        if not path:
            mostrar_mensaje("Selecciona un archivo .xlsx primero.")
            return
        if not peso_str:
            mostrar_mensaje("Introduce el peso en kg.")
            return
        try:
            peso = float(peso_str)
            if peso <= 0:
                raise ValueError
        except ValueError:
            mostrar_mensaje("El peso debe ser un número positivo.")
            return

        mostrar_mensaje("Generando gráficas…", "#ffff55", duracion_ms=0)
        try:
            abrir_graficas_en_hilo(path, peso)
            root.after(1500, lambda: canvas.itemconfig(msg_id, text=""))
        except Exception as e:
            mostrar_mensaje(f"Error: {e}")

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver gráficas",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=590, ancho=452, alto=50,
                       comando=ver_graficas)

    from interfaces.guizero.common.principal import pantalla_principal
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=655, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(root, frame))