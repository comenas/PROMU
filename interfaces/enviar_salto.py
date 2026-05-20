import tkinter as tk
import os
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

    canvas.create_text(640, 420, text="Altura (mm)",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_altura = crear_entrada(frame, canvas, x=640, y=460, ancho=400, alto=40,
                                   imagen_caja=ruta("minecraft_caja.png"), fuente=fuente_mc)

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
        grupo  = entrada_grupo.get().strip()
        altura = entrada_altura.get().strip()

        if not grupo or not altura:
            mostrar_mensaje("Rellena todos los campos.", "#ff5555")
            return
        if not altura.isdigit():
            mostrar_mensaje("La altura debe ser un número entero.", "#ff5555")
            return

        _enviando[0] = True
        mostrar_mensaje("Enviando…", "#ffff55", duracion_ms=0)

        def on_resp(resp):
            _enviando[0] = False
            root.after(0, lambda: mostrar_mensaje(resp, "#55ff55"))

        enviar_salto(grupo, altura, on_resp)

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Enviar",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=575, ancho=400, alto=45,
                       comando=enviar)

    from interfaces.principal import pantalla_principal
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=633, ancho=400, alto=45,
                       comando=lambda: pantalla_principal(root, frame))