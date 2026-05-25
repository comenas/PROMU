import tkinter as tk
import os
import json
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, limpiar_frame
from servidor.red import pedir_leaderboard

BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF  = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)


MEDALLAS     = {1: "🥇", 2: "🥈", 3: "🥉"}
COLOR_ORO    = "#FFD700"
COLOR_PLATA  = "#C0C0C0"
COLOR_BRONCE = "#CD7F32"
COLOR_NORMAL = "#dddddd"


def _parsear_linea(linea):
    """
    Parsea una línea JSON del servidor.
    Formato: {"ranking":"1","nombre":"aramfor","grupo_ProMu":"Elipse","altura":600,"fecha":"20-05-2026"}
    Devuelve (pos, nombre, grupo, altura_mm, fecha) o None.
    """
    linea = linea.strip()
    if not linea.startswith("{"):
        return None
    try:
        d = json.loads(linea)
        pos    = int(d["ranking"])
        nombre = d["nombre"]
        grupo  = d.get("grupo_ProMu", "")
        altura = int(d["altura"])   # viene en mm
        fecha  = d.get("fecha", "")
        return (pos, nombre, grupo, altura, fecha)
    except Exception:
        return None


def pantalla_leaderboard(root, frame, comando, titulo):
    """Descarga y muestra el leaderboard con formato de tabla limpia."""
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))

    # ── Título ────────────────────────────────────────────────────────────────
    canvas.create_text(640, 100, text=titulo,
                       font=("Minecraft", 28), fill="white", anchor="center")

    # ── Cabecera ──────────────────────────────────────────────────────────────
    canvas.create_text(180, 175, text="POS",     font=("Minecraft", 12), fill="#aaaaaa", anchor="center")
    canvas.create_text(390, 175, text="JUGADOR", font=("Minecraft", 12), fill="#aaaaaa", anchor="center")
    canvas.create_text(590, 175, text="GRUPO",   font=("Minecraft", 12), fill="#aaaaaa", anchor="center")
    canvas.create_text(770, 175, text="ALTURA",  font=("Minecraft", 12), fill="#aaaaaa", anchor="center")
    canvas.create_text(920, 175, text="FECHA",   font=("Minecraft", 12), fill="#aaaaaa", anchor="center")
    canvas.create_line(140, 190, 980, 190, fill="#444444", width=2)

    # ── Área scrollable ───────────────────────────────────────────────────────
    contenedor = tk.Frame(frame, bg="#1a1108")
    canvas.create_window(560, 490, window=contenedor, width=860, height=580)

    scrollbar = tk.Scrollbar(contenedor, orient="vertical", bg="#2a2118",
                              troughcolor="#1a1108", activebackground="#444444")
    scrollbar.pack(side="right", fill="y")

    lienzo_filas = tk.Canvas(contenedor, bg="#1a1108", highlightthickness=0,
                              yscrollcommand=scrollbar.set)
    lienzo_filas.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=lienzo_filas.yview)

    frame_filas = tk.Frame(lienzo_filas, bg="#1a1108")
    ventana_filas = lienzo_filas.create_window((0, 0), window=frame_filas, anchor="nw")

    def _ajustar_scroll(event):
        lienzo_filas.configure(scrollregion=lienzo_filas.bbox("all"))
        lienzo_filas.itemconfig(ventana_filas, width=lienzo_filas.winfo_width())

    frame_filas.bind("<Configure>", _ajustar_scroll)

    lbl_cargando = tk.Label(frame_filas, text="Cargando ranking…",
                             font=("Minecraft", 14), bg="#1a1108", fg="#ffff55")
    lbl_cargando.pack(pady=40)

    # ── Callback ──────────────────────────────────────────────────────────────
    def on_leaderboard(lineas):
        def actualizar():
            lbl_cargando.destroy()

            entradas = [_parsear_linea(l) for l in lineas]
            entradas = [e for e in entradas if e is not None]

            if not entradas:
                tk.Label(frame_filas, text="Aún no hay registros.",
                         font=("Minecraft", 13), bg="#1a1108", fg="#888888").pack(pady=20)
                return

            for pos, nombre, grupo, altura_mm, fecha in entradas:
                if pos == 1:
                    color = COLOR_ORO
                elif pos == 2:
                    color = COLOR_PLATA
                elif pos == 3:
                    color = COLOR_BRONCE
                else:
                    color = COLOR_NORMAL

                bg_fila = "#222210" if pos % 2 == 0 else "#1a1108"
                fila = tk.Frame(frame_filas, bg=bg_fila, pady=5)
                fila.pack(fill="x", padx=2, pady=1)

                medalla   = MEDALLAS.get(pos, "")
                texto_pos = f"{medalla}{pos}º" if medalla else f"{pos}º"

                tk.Label(fila, text=texto_pos, font=("Minecraft", 12),
                         bg=bg_fila, fg=color, width=6,
                         anchor="center").pack(side="left", padx=(6, 0))

                tk.Label(fila, text=nombre, font=("Minecraft", 12),
                         bg=bg_fila, fg=color, width=14,
                         anchor="w").pack(side="left", padx=8)

                tk.Label(fila, text=grupo, font=("Minecraft", 11),
                         bg=bg_fila, fg="#aaaaaa", width=12,
                         anchor="center").pack(side="left", padx=4)

                altura_cm = altura_mm / 10
                tk.Label(fila, text=f"{altura_cm:.1f} cm", font=("Minecraft", 12),
                         bg=bg_fila, fg=color, width=9,
                         anchor="center").pack(side="left", padx=4)

                tk.Label(fila, text=fecha, font=("Minecraft", 10),
                         bg=bg_fila, fg="#777777", width=12,
                         anchor="center").pack(side="left", padx=4)

            tk.Label(frame_filas, text="─" * 50, font=("Minecraft", 9),
                     bg="#1a1108", fg="#333333").pack(pady=(10, 2))
            tk.Label(frame_filas, text=f"{len(entradas)} participantes",
                     font=("Minecraft", 11), bg="#1a1108", fg="#555555").pack()

        root.after(0, actualizar)

    pedir_leaderboard(comando, on_leaderboard)

    # ── Botón Volver ──────────────────────────────────────────────────────────
    from interfaces.guizero.online.usuario import pantalla_usuario
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 20,
                       x=640, y=840, ancho=452, alto=50,
                       comando=lambda: pantalla_usuario(root, frame))