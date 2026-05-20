# pantallas/configuracion.py

import tkinter as tk
from interfaces.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from servidor.red import sesion, cerrar_sesion


def pantalla_configuracion(root, frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, "minecraft_inicio_sesion.png")

    canvas.create_text(640, 250, text="Configuración",
                       font=("Minecraft", 30), fill="white", anchor="center")

    canvas.create_text(640, 380, text="Volumen",
                       font=("Minecraft", 18), fill="white", anchor="center")

    volumen = tk.IntVar(value=50)
    slider  = tk.Scale(
        frame,
        from_=0, to=100,
        orient="horizontal",
        variable=volumen,
        bg="#1a1108", fg="white",
        highlightthickness=0,
        troughcolor="#3a3a3a",
        length=400,
        font=("Minecraft", 12),
        label=""
    )
    canvas.create_window(640, 430, window=slider, width=400, height=50)

    etiqueta_vol = tk.Label(frame, text="50%",
                            font=("Minecraft", 14), bg="#1a1108", fg="white")
    canvas.create_window(640, 480, window=etiqueta_vol)
    slider.config(command=lambda val: etiqueta_vol.config(text=f"{val}%"))

    from interfaces.principal import pantalla_principal

    if sesion["autenticado"]:
        canvas.create_text(640, 540, text=f"Sesión: {sesion['usuario']}",
                           font=("Minecraft", 14), fill="#aaffaa", anchor="center")

        def logout():
            cerrar_sesion()
            pantalla_principal(root, frame)

        crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Cerrar sesión",
                           "fuente_minecraft.ttf", 18,
                           x=640, y=595, ancho=400, alto=45,
                           comando=logout)

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Volver",
                       "fuente_minecraft.ttf", 20,
                       x=640, y=670, ancho=452, alto=50,
                       comando=lambda: pantalla_principal(root, frame))