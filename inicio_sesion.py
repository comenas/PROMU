# pantallas/inicio_sesion.py

import tkinter as tk
from UI import crear_boton_imagen, crear_canvas, crear_entrada, limpiar_frame
from RED import conectar_y_autenticar


def pantalla_inicio_sesion(root, frame):
    limpiar_frame(frame)
    canvas    = crear_canvas(frame, "minecraft_inicio_sesion.png")
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 250, text="Inicia sesión en el servidor UPV",
                       font=("Minecraft", 24), fill="white", anchor="center")

    canvas.create_text(640, 360, text="Usuario",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_usuario = crear_entrada(frame, canvas, x=640, y=400, ancho=400, alto=40,
                                    imagen_caja="minecraft_caja.png", fuente=fuente_mc)

    canvas.create_text(640, 460, text="Contraseña",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_password = crear_entrada(frame, canvas, x=640, y=500, ancho=400, alto=40,
                                     imagen_caja="minecraft_caja.png", fuente=fuente_mc,
                                     password=True)

    estado_var = tk.StringVar(value="")
    estado_lbl = tk.Label(frame, textvariable=estado_var,
                          font=("Minecraft", 12), bg="#1a1108", fg="#ffff55")
    canvas.create_window(640, 550, window=estado_lbl)

    def iniciar_sesion():
        from principal import pantalla_principal
        usuario  = entrada_usuario.get().strip()
        password = entrada_password.get().strip()
        if not usuario or not password:
            estado_var.set("Rellena usuario y contraseña.")
            return
        estado_var.set("Conectando…")
        root.update()
        ok, error = conectar_y_autenticar(usuario, password)
        if ok:
            pantalla_principal(root, frame)
        else:
            estado_var.set(error)

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Iniciar sesión",
                       "fuente_minecraft.ttf", 18,
                       x=640, y=600, ancho=400, alto=40,
                       comando=iniciar_sesion)

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Volver",
                       "fuente_minecraft.ttf", 18,
                       x=640, y=655, ancho=400, alto=40,
                       comando=lambda: __import__(
                           "pantallas.principal", fromlist=["pantalla_principal"]
                       ).pantalla_principal(root, frame))