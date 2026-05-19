# pantallas/principal.py

import tkinter as tk
from UI import crear_boton_imagen, crear_canvas, limpiar_frame
from RED import sesion


def pantalla_principal(root, frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, "minecraft_fondo.png")

    if sesion["autenticado"]:
        canvas.create_text(
            640, 420, text=f"Conectado como: {sesion['usuario']}",
            font=("Minecraft", 14), fill="#aaffaa", anchor="center"
        )

    # Importaciones locales para evitar ciclos entre pantallas
    from inicio_sesion import pantalla_inicio_sesion
    from invitado_rankings import pantalla_invitado
    from configuracion import pantalla_configuracion
    from enviar_salto  import pantalla_enviar_salto

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Iniciar sesión",
                       "fuente_minecraft.ttf", 25,
                       x=645, y=490, ancho=452, alto=50,
                       comando=lambda: pantalla_inicio_sesion(root, frame))

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Continuar como invitado",
                       "fuente_minecraft.ttf", 25,
                       x=645, y=551, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(root, frame))

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Configuración",
                       "fuente_minecraft.ttf", 25,
                       x=645, y=612, ancho=452, alto=50,
                       comando=lambda: pantalla_configuracion(root, frame))

    if sesion["autenticado"]:
        crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Enviar salto",
                           "fuente_minecraft.ttf", 25,
                           x=645, y=673, ancho=452, alto=50,
                           comando=lambda: pantalla_enviar_salto(root, frame))

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Salir",
                       "fuente_minecraft.ttf", 25,
                       x=645, y=712, ancho=452, alto=50,
                       comando=root.destroy)