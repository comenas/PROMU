import tkinter as tk
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from servidor.red import sesion
from interfaces.guizero.common.audio import detener_musica, reproducir_musica
from interfaces.guizero.online.inicio_sesion   import pantalla_inicio_sesion
from interfaces.guizero.ofline.invitado import pantalla_invitado
from interfaces.guizero.common.configuracion   import pantalla_configuracion
from interfaces.guizero.online.enviar_salto    import pantalla_enviar_salto
from interfaces.guizero.common.analisis        import pantalla_analisis
import os

BASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)

_musica_activa = [True]

def pantalla_principal(root, frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_fondo.png"))

    if sesion["autenticado"]:
        canvas.create_text(
            640, 400, text=f"Conectado como: {sesion['usuario']}",
            font=("Minecraft", 14), fill="#aaffaa", anchor="center"
        )

    

    # ── Botones principales (espaciado uniforme de 54 px) ─────────────────────
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=490, ancho=452, alto=50,
                       comando=lambda: pantalla_inicio_sesion(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Continuar como invitado",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=552, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(root, frame))
    
    crear_boton_imagen(frame, canvas, ruta("fisica_bueno.png"), "",
                       ruta("fuente_minecraft.ttf"), 1,
                       x=904, y=712, ancho=50, alto=50,
                       comando=lambda: pantalla_analisis(root, frame))
    

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Configuración",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=613, ancho=452, alto=50,
                       comando=lambda: pantalla_configuracion(root, frame))

    if sesion["autenticado"]:
        crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Enviar salto",
                           ruta("fuente_minecraft.ttf"), 25,
                           x=645, y=684, ancho=452, alto=50,
                           comando=lambda: pantalla_enviar_salto(root, frame))

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Salir",
                       ruta("fuente_minecraft.ttf"), 25,
                       x=645, y=712, ancho=452, alto=50,
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
                       x=386, y=712, ancho=50, alto=50,
                       comando=toggle_musica)