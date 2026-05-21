import tkinter as tk
import os
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from servidor.red import pedir_leaderboard

BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)


def pantalla_leaderboard(root, frame, comando, titulo):
    """Descarga y muestra el leaderboard pedido."""
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    canvas.create_text(640, 120, text=titulo,
                       font=("Minecraft", 28), fill="white", anchor="center")

    txt_frame = tk.Frame(frame, bg="#1a1108")
    canvas.create_window(640, 430, window=txt_frame, width=700, height=500)

    scrollbar = tk.Scrollbar(txt_frame)
    scrollbar.pack(side="right", fill="y")

    txt = tk.Text(txt_frame, font=("Minecraft", 13),
                  bg="#1a1108", fg="white",
                  relief="flat", wrap="word",
                  yscrollcommand=scrollbar.set)
    txt.pack(fill="both", expand=True)
    scrollbar.config(command=txt.yview)

    txt.insert("end", "Cargando…\n")
    txt.config(state="disabled")

    # pedir_leaderboard es asíncrono (hilo), actualizamos la UI desde el hilo principal
    def on_leaderboard(lineas):
        def actualizar():
            txt.config(state="normal")
            txt.delete("1.0", "end")
            for linea in lineas:
                txt.insert("end", linea + "\n")
            txt.config(state="disabled")
        root.after(0, actualizar)

    pedir_leaderboard(comando, on_leaderboard)

    from interfaces.guizero.ofline.invitado import pantalla_invitado
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=730, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(root, frame))