# pantallas/invitado.py

from UI import crear_boton_imagen, crear_canvas, limpiar_frame


def pantalla_invitado(root, frame):
    """Pantalla de Rankings — accesible sin login."""
    limpiar_frame(frame)
    canvas = crear_canvas(frame, "minecraft_inicio_sesion.png")

    canvas.create_text(640, 280, text="Rankings",
                       font=("Minecraft", 30), fill="white", anchor="center")

    from leaderboard import pantalla_leaderboard
    from principal import pantalla_principal

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Ver ranking masculino",
                       "fuente_minecraft.ttf", 20,
                       x=640, y=420, ancho=452, alto=50,
                       comando=lambda: pantalla_leaderboard(
                           root, frame, "GET_LEADERBOARD_MEN", "Ranking Masculino"))

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Ver ranking femenino",
                       "fuente_minecraft.ttf", 20,
                       x=640, y=490, ancho=452, alto=50,
                       comando=lambda: pantalla_leaderboard(
                           root, frame, "GET_LEADERBOARD_WOMEN", "Ranking Femenino"))

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Volver",
                       "fuente_minecraft.ttf", 20,
                       x=640, y=650, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(root, frame))