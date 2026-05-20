# pantallas/enviar_salto.py

import tkinter as tk
from interfaces.ui import crear_boton_imagen, crear_canvas, crear_entrada, limpiar_frame
from servidor.red import enviar_salto


def pantalla_enviar_salto(root, frame):
    """Pantalla para enviar un salto — solo usuarios autenticados."""
    limpiar_frame(frame)
    canvas    = crear_canvas(frame, "minecraft_inicio_sesion.png")
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 200, text="Enviar Salto",
                       font=("Minecraft", 28), fill="white", anchor="center")

    canvas.create_text(640, 320, text="Grupo ProMu (ej: A2-4)",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_grupo = crear_entrada(frame, canvas, x=640, y=360, ancho=400, alto=40,
                                  imagen_caja="minecraft_caja.png", fuente=fuente_mc)

    canvas.create_text(640, 420, text="Altura (mm)",
                       font=("Minecraft", 14), fill="white", anchor="center")
    entrada_altura = crear_entrada(frame, canvas, x=640, y=460, ancho=400, alto=40,
                                   imagen_caja="minecraft_caja.png", fuente=fuente_mc)

    estado_var = tk.StringVar(value="")
    estado_lbl = tk.Label(frame, textvariable=estado_var,
                          font=("Minecraft", 13), bg="#1a1108", fg="#55ff55")
    canvas.create_window(640, 530, window=estado_lbl)

    def enviar():
        grupo  = entrada_grupo.get().strip()
        altura = entrada_altura.get().strip()
        if not grupo or not altura:
            estado_var.set("Rellena todos los campos.")
            return
        if not altura.isdigit():
            estado_var.set("La altura debe ser un número entero.")
            return
        estado_var.set("Enviando…")
        root.update()
        resp = enviar_salto(grupo, altura)
        estado_var.set(resp)

    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Enviar",
                       "fuente_minecraft.ttf", 20,
                       x=640, y=590, ancho=400, alto=45,
                       comando=enviar)

    from interfaces.principal import pantalla_principal
    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Volver",
                       "fuente_minecraft.ttf", 20,
                       x=640, y=650, ancho=400, alto=45,
                       comando=lambda: pantalla_principal(root, frame))