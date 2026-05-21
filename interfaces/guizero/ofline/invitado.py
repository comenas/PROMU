import os
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from interfaces.guizero.common.leaderboard import pantalla_leaderboard


BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)


def pantalla_invitado(root, frame):
    """Pantalla de Rankings — accesible sin login."""
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    canvas.create_text(640, 280, text="Rankings",
                       font=("Minecraft", 30), fill="white", anchor="center")

    from interfaces.guizero.common.principal import pantalla_principal
    from interfaces.guizero.ofline.gestionar_salto_invitado import pantalla_gestion_salto

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Analizar salto",
                   ruta("fuente_minecraft.ttf"), 20,
                   x=640, y=350, ancho=452, alto=50,
                   comando=lambda: pantalla_gestion_salto(root, frame))

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