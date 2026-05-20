import os
from interfaces.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from servidor.red import sesion

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)


def pantalla_usuario(root, frame):
    """Pantalla principal para usuarios autenticados: subir salto + rankings."""
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    canvas.create_text(640, 220, text="Bienvenido",
                       font=("Minecraft", 30), fill="white", anchor="center")

    if sesion["usuario"]:
        canvas.create_text(640, 275, text=sesion["usuario"],
                           font=("Minecraft", 18), fill="#aaffaa", anchor="center")

    from interfaces.enviar_salto import pantalla_enviar_salto
    from interfaces.leaderboard  import pantalla_leaderboard
    from interfaces.principal    import pantalla_principal

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Subir archivo de salto",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=380, ancho=452, alto=50,
                       comando=lambda: pantalla_enviar_salto(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking masculino",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=450, ancho=452, alto=50,
                       comando=lambda: pantalla_leaderboard(
                           root, frame, "GET_LEADERBOARD_MEN", "Ranking Masculino"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Ver ranking femenino",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=520, ancho=452, alto=50,
                       comando=lambda: pantalla_leaderboard(
                           root, frame, "GET_LEADERBOARD_WOMEN", "Ranking Femenino"))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=660, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(root, frame))