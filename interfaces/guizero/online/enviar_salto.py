import tkinter as tk
import os
from tkinter import filedialog
from interfaces.ui import crear_boton_imagen, crear_canvas, crear_entrada, limpiar_frame
from servidor.red import enviar_salto

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)


def pantalla_enviar_salto(root, frame):
    """Pantalla para enviar un salto — solo usuarios autenticados."""
    limpiar_frame(frame)
    canvas    = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 200, text="Enviar Salto",
                       font=("Minecraft", 28), fill="white", anchor="center")
    canvas.create_text(640, 320, text="Grupo ProMu (ej: A2-4)",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_grupo = crear_entrada(frame, canvas, x=640, y=360, ancho=400, alto=40,
                                  imagen_caja=ruta("minecraft_caja.png"), fuente=fuente_mc)

    ruta_xlsx = tk.StringVar(value="")

    canvas.create_text(640, 420, text="Archivo de datos (.xlsx)",
                   font=("Minecraft", 14), fill="white", anchor="center")

    lbl_archivo = tk.Label(frame, text="Sin archivo seleccionado",
                       font=("Minecraft", 11), bg="#1a1108", fg="#aaaaaa",
                       wraplength=500, anchor="center")
    canvas.create_window(640, 455, window=lbl_archivo, width=520, height=28)

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
                   x=640, y=495, ancho=400, alto=40,
                   comando=seleccionar_archivo)

    # ── Mensaje de estado en canvas (sin fondo, no tapa nada) ────────────────
    msg_id = canvas.create_text(640, 513, text="",
                                font=("Minecraft", 13), fill="#55ff55", anchor="center")

    _timer    = [None]
    _enviando = [False]

    def mostrar_mensaje(texto, color="#55ff55", duracion_ms=3000):
        canvas.itemconfig(msg_id, text=texto, fill=color)
        if _timer[0]:
            root.after_cancel(_timer[0])
            _timer[0] = None
        if duracion_ms > 0:
            _timer[0] = root.after(duracion_ms,
                                   lambda: canvas.itemconfig(msg_id, text=""))

    def enviar():
  
        if _enviando[0]:
            return
        grupo = entrada_grupo.get().strip()
        path  = ruta_xlsx.get()

        if not grupo:
            mostrar_mensaje("Rellena el grupo.", "#ff5555")
            return
        if not path:
            mostrar_mensaje("Selecciona un archivo .xlsx.", "#ff5555")
            return

        _enviando[0] = True
        mostrar_mensaje("Analizando salto…", "#ffff55", duracion_ms=0)

        try:
            from core.matemáticas import Mat_obj1_AD, Mat_obj8_Altura
            t, ace_y, ace = Mat_obj1_AD(path)
            h1, h2, h3   = Mat_obj8_Altura(ace, ace_y, t)
            altura_m     = int(h1 * 1000)   # h1 es el método más fiable, en metros → mm
        except Exception as e:
            _enviando[0] = False
            mostrar_mensaje(f"Error al analizar: {e}", "#ff5555")
            return

        mostrar_mensaje(f"Enviando… altura: {altura_m} mm", "#ffff55", duracion_ms=0)

        def on_resp(resp):
            _enviando[0] = False
            root.after(0, lambda: mostrar_mensaje(resp, "#55ff55"))

        enviar_salto(grupo, altura_m, on_resp)

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Enviar",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=575, ancho=400, alto=45,
                       comando=enviar)

    from interfaces.principal import pantalla_principal
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=633, ancho=400, alto=45,
                       comando=lambda: pantalla_principal(root, frame))