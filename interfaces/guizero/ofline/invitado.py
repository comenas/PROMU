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

    canvas.create_text(640, 325, text="SIN CONEXION",
                       font=("Minecraft", 30), fill="white", anchor="center")

    from interfaces.guizero.common.principal import pantalla_principal
    from interfaces.guizero.ofline.gestionar_salto_invitado import pantalla_gestion_salto

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Analizar salto (no se guardará)",
                   ruta("fuente_minecraft.ttf"), 20,
                   x=640, y=400, ancho=452, alto=50,
                   comando=lambda: pantalla_gestion_salto(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                   ruta("fuente_minecraft.ttf"), 20,
                   x=640, y=500, ancho=452, alto=50,
                   comando=lambda: pantalla_principal(root, frame))