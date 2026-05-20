import os
from interfaces.ui import crear_boton_imagen, crear_canvas, limpiar_frame

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)


def pantalla_invitado(root, frame):
    """Pantalla de Rankings — accesible sin login."""
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    canvas.create_text(640, 280, text="Rankings",
                       font=("Minecraft", 30), fill="white", anchor="center")

    from interfaces.leaderboard import pantalla_leaderboard
    from interfaces.principal import pantalla_principal

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking masculino",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=420, ancho=452, alto=50,
                       comando=lambda: pantalla_leaderboard(
                           root, frame, "GET_LEADERBOARD_MEN", "Ranking Masculino"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking femenino",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=490, ancho=452, alto=50,
                       comando=lambda: pantalla_leaderboard(
                           root, frame, "GET_LEADERBOARD_WOMEN", "Ranking Femenino"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=650, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(root, frame))