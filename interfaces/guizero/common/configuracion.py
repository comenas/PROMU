import tkinter as tk
import os
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from interfaces.guizero.common.audio import ajustar_volumen, obtener_volumen
from servidor.red import sesion, cerrar_sesion

BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)



def pantalla_configuracion(root, frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    canvas.create_text(640, 250, text="Configuración",
                       font=("Minecraft", 30), fill="white", anchor="center")
    canvas.create_text(640, 380, text="Volumen",
                       font=("Minecraft", 18), fill="white", anchor="center")

    volumen = tk.IntVar(value=obtener_volumen())
    slider  = tk.Scale(frame, from_=0, to=100, orient="horizontal", variable=volumen,
                       bg="#1a1108", fg="white", highlightthickness=0,
                       troughcolor="#3a3a3a", length=400, font=("Minecraft", 12), label="")
    canvas.create_window(640, 430, window=slider, width=400, height=50)

    etiqueta_vol = tk.Label(frame, text=f"{obtener_volumen()}%", font=("Minecraft", 14),
                            bg="#1a1108", fg="white")
    canvas.create_window(640, 480, window=etiqueta_vol)

    def actualizar_volumen(val):
        ajustar_volumen(int(val))                        # ← conecta con el audio real
        etiqueta_vol.config(text=f"{val}%")

    slider.config(command=actualizar_volumen)

    from interfaces.guizero.common.principal import pantalla_principal

    if sesion["autenticado"]:
        canvas.create_text(640, 540, text=f"Sesión: {sesion['usuario']}",
                           font=("Minecraft", 14), fill="#aaffaa", anchor="center")

        def logout():
            cerrar_sesion()
            pantalla_principal(root, frame)

        crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Cerrar sesión",
                           ruta("fuente_minecraft.ttf"), 18,
                           x=640, y=595, ancho=400, alto=45,
                           comando=logout)

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=670, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(root, frame))