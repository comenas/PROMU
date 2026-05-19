# pantallas/leaderboard.py

import tkinter as tk
from UI import crear_boton_imagen, crear_canvas, limpiar_frame
from RED import pedir_leaderboard


def pantalla_leaderboard(root, frame, comando, titulo):
    """Descarga y muestra el leaderboard pedido."""
    limpiar_frame(frame)
    canvas = crear_canvas(frame, "minecraft_inicio_sesion.png")

    canvas.create_text(640, 120, text=titulo,
                       font=("Minecraft", 28), fill="white", anchor="center")

    txt_frame = tk.Frame(frame, bg="#1a1108")
    canvas.create_window(640, 430, window=txt_frame, width=700, height=500)

    scrollbar = tk.Scrollbar(txt_frame)
    scrollbar.pack(side="right", fill="y")

    txt = tk.Text(txt_frame, font=("Minecraft", 13),
                  bg="#1a1108", fg="white",
                  relief="flat", wrap="word",
                  yscrollcommand=scrollbar.set)
    txt.pack(fill="both", expand=True)
    scrollbar.config(command=txt.yview)

    txt.insert("end", "Cargando…\n")
    txt.config(state="disabled")
    root.update()

    lineas = pedir_leaderboard(comando)
    txt.config(state="normal")
    txt.delete("1.0", "end")
    for linea in lineas:
        txt.insert("end", linea + "\n")
    txt.config(state="disabled")

    from invitado_rankings import pantalla_invitado
    crear_boton_imagen(frame, canvas, "minecraft_boton.png", "Volver",
                       "fuente_minecraft.ttf", 20,
                       x=640, y=730, ancho=452, alto=50,
                       comando=lambda: pantalla_invitado(root, frame))