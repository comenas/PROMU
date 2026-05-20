import tkinter as tk
from interfaces.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from servidor.red import sesion
from interfaces.audio import detener_musica, reproducir_musica
import os

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)

_musica_activa = [True]

def pantalla_principal(root, frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_fondo.png"))

    if sesion["autenticado"]:
        canvas.create_text(
            640, 400, text=f"Conectado como: {sesion['usuario']}",
            font=("Minecraft", 14), fill="#aaffaa", anchor="center"
        )

    from interfaces.inicio_sesion   import pantalla_inicio_sesion
    from interfaces.invitado_rankings import pantalla_invitado
    from interfaces.configuracion   import pantalla_configuracion
    from interfaces.enviar_salto    import pantalla_enviar_salto
    from interfaces.analisis        import pantalla_analisis

    # ── Botones principales (espaciado uniforme de 54 px) ─────────────────────
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=460, ancho=452, alto=50,
                       comando=lambda: pantalla_inicio_sesion(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Continuar como invitado",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=516, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Analizar salto",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=572, ancho=452, alto=50,
                       comando=lambda: pantalla_analisis(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Configuración",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=628, ancho=452, alto=50,
                       comando=lambda: pantalla_configuracion(root, frame))

    if sesion["autenticado"]:
        crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Enviar salto",
                           ruta("fuente_minecraft.ttf"), 25,
                           x=645, y=684, ancho=452, alto=50,
                           comando=lambda: pantalla_enviar_salto(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Salir",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=740, ancho=452, alto=50,
                       comando=root.destroy)

    # ── Botón de música ───────────────────────────────────────────────────────
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
                       x=388, y=740, ancho=50, alto=50,
                       comando=toggle_musica)