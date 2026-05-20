# pantallas/principal.py

import tkinter as tk
from interfaces.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from servidor.red import sesion
from interfaces.audio import detener_musica, reproducir_musica
import os

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)

# Estado global del mute — lista para que sea mutable desde el closure
_musica_activa = [True]

def pantalla_principal(root, frame):

    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_fondo.png"))

    if sesion["autenticado"]:
        canvas.create_text(
            640, 420, text=f"Conectado como: {sesion['usuario']}",
            font=("Minecraft", 14), fill="#aaffaa", anchor="center"
        )

    # Importaciones locales para evitar ciclos entre pantallas
    from interfaces.inicio_sesion import pantalla_inicio_sesion
    from interfaces.invitado_rankings import pantalla_invitado
    from interfaces.configuracion import pantalla_configuracion
    from interfaces.enviar_salto import pantalla_enviar_salto

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=490, ancho=452, alto=50,
                       comando=lambda: pantalla_inicio_sesion(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Continuar como invitado",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=551, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Configuración",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=612, ancho=452, alto=50,
                       comando=lambda: pantalla_configuracion(root, frame))

    if sesion["autenticado"]:
        crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Enviar salto",
                           ruta("fuente_minecraft.ttf"), 25,
                           x=645, y=673, ancho=452, alto=50,
                           comando=lambda: pantalla_enviar_salto(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Salir",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=712, ancho=452, alto=50,
                       comando=root.destroy)

    # ── Botón de música (toggle mute/unmute) ──────────────────────────────────
    def toggle_musica():
        _musica_activa[0] = not _musica_activa[0]
        if _musica_activa[0]:
            reproducir_musica()
        else:
            detener_musica()
        pantalla_principal(root, frame)

    icono = "unmuted.png" if _musica_activa[0] else "muted.png"
    crear_boton_imagen(frame, canvas, ruta(icono), "",
                       ruta("fuente_minecraft.ttf"), 1,
                       x=388, y=712, ancho=50, alto=50,
                       comando=toggle_musica)