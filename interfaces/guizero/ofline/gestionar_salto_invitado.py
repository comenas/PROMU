import tkinter as tk
import os
from tkinter import filedialog
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, crear_entrada, limpiar_frame
from core.formatter import format_results
from core.matemáticas import Mat_obj1_AD, Mat_obj8_Altura, Mat_obj7_Puntos
from core.formatter import format_results
from interfaces.guizero.common.principal import pantalla_principal

BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)



def pantalla_gestion_salto(root, frame):
    """Pantalla para analizar un salto como invitado."""
    limpiar_frame(frame)
    canvas    = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 80, text="Analizar Salto",
                       font=("Minecraft", 28), fill="white", anchor="center")
    
    ruta_xlsx = tk.StringVar(value="")

    canvas.create_text(640, 200, text="Archivo de datos (.xlsx)",
                   font=("Minecraft", 14), fill="white", anchor="center")

    lbl_archivo = tk.Label(frame, text="Sin archivo seleccionado",
                       font=("Minecraft", 11), bg="#1a1108", fg="#aaaaaa",
                       wraplength=500, anchor="center")
    canvas.create_window(640, 235, window=lbl_archivo, width=520, height=28)

    def seleccionar_archivo():
        path = filedialog.askopenfilename(
            title="Selecciona el archivo de datos",
           filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")]
        )
        if path:
            ruta_xlsx.set(path)
            lbl_archivo.config(text=os.path.basename(path), fg="#55ff55")

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Seleccionar archivo",
                   ruta("fuente_minecraft.ttf"), 16,
                   x=640, y=275, ancho=400, alto=40,
                   comando=seleccionar_archivo)

    # ── Mensaje de estado en canvas ──────────────────────────────────────────
    msg_id = canvas.create_text(640, 325, text="",
                                font=("Minecraft", 13), fill="#55ff55", anchor="center")

    _timer = [None]

    def mostrar_mensaje(texto, color="#55ff55", duracion_ms=3000):
        canvas.itemconfig(msg_id, text=texto, fill=color)
        if _timer[0]:
            root.after_cancel(_timer[0])
            _timer[0] = None
        if duracion_ms > 0:
            _timer[0] = root.after(duracion_ms,
                                   lambda: canvas.itemconfig(msg_id, text=""))
    
    # ── Cuadro de resultados ─────────────────────────────────────────────────
    resultado_frame = tk.Frame(frame, bg="#1a1108")
    canvas.create_window(640, 490, window=resultado_frame, width=600, height=160)

    txt_resultados = tk.Text(resultado_frame, font=("Minecraft", 12),
                          bg="#2a2118", fg="#00ff99",
                          relief="flat", wrap="word", state="disabled")
    txt_resultados.pack(fill="both", expand=True)

    # ── Almacena h1 para pasarlo a la pantalla de personaje ──────────────────
    _h1 = [None]

    def gestionar():
        path = ruta_xlsx.get()
        if not path:
            mostrar_mensaje("Selecciona un archivo .xlsx primero.", "#ff5555")
            return
        mostrar_mensaje("Analizando salto...", "#ffff55", duracion_ms=0)

        try:
            t, ace_y, ace                    = Mat_obj1_AD(path)
            idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace, ace_y, t)
            h1, h2, h3                       = Mat_obj8_Altura(ace, ace_y, t)
        except Exception as e:
            mostrar_mensaje(f"Error al analizar: {e}", "#ff5555")
            return

        _h1[0] = h1

        resultados = {
            "altura_vuelo":          h1,
            "altura_velocidad":      h2,
            "altura_desplazamiento": h3,
            "tiempo_vuelo":          t_aire,
            "velocidad_despegue":    velocidad[idx_T0],
        }

        formateados = format_results(resultados)

        txt_resultados.config(state="normal")
        txt_resultados.delete("1.0", "end")
        for clave, valor in formateados.items():
            txt_resultados.insert("end", f"{clave}: {valor}\n")
        txt_resultados.config(state="disabled")

        mostrar_mensaje("Análisis completado.", "#55ff55")

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Analizar",
                ruta("fuente_minecraft.ttf"), 20,
                x=640, y=640, ancho=400, alto=45,
                comando=gestionar)

    # ── Botón Continuar → pantalla de personaje ──────────────────────────────
    def ir_a_personaje():
        if _h1[0] is None:
            mostrar_mensaje("Analiza un salto primero.", "#ff5555")
            return
        from interfaces.guizero.ofline.pantalla_personaje import pantalla_personaje
        pantalla_personaje(root, frame, _h1[0])

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Continuar",
                ruta("fuente_minecraft.ttf"), 20,
                x=640, y=695, ancho=400, alto=45,
                comando=ir_a_personaje)

    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                ruta("fuente_minecraft.ttf"), 20,
                x=640, y=750, ancho=400, alto=45,
                comando=lambda: pantalla_principal(root, frame))

    # ── Botón de info (esquina inferior izquierda) ───────────────────────────
    def mostrar_info():
        ventana = tk.Toplevel(root)
        ventana.title("Criterios de asignación")
        ventana.configure(bg="#1a1108")
        ventana.resizable(False, False)
        ventana.geometry("520x400")
        ventana.grab_set()  # modal

        tk.Label(ventana, text="¿Qué personaje eres?",
                 font=("Minecraft", 16), bg="#1a1108", fg="white").pack(pady=(20, 14))

        criterios = [
            ("Slime",        " 0 – 15 cm",  "#55ff55"),
            ("Lobo",         "16 – 30 cm",  "#aaaaff"),
            ("Creeper",      "31 – 45 cm",  "#44cc44"),
            ("Enderman",     "46 – 59 cm",  "#cc88ff"),
            ("Ender Dragon", "60+ cm",      "#aa00ff"),
        ]

        for nombre, rango, color in criterios:
            fila = tk.Frame(ventana, bg="#1a1108")
            fila.pack(fill="x", padx=50, pady=5)
            tk.Label(fila, text=f"▸ {nombre:<15}", font=("Minecraft", 13),
                     bg="#1a1108", fg=color, anchor="w").pack(side="left")
            tk.Label(fila, text=rango, font=("Minecraft", 13),
                     bg="#1a1108", fg="white", anchor="w").pack(side="left")

        tk.Button(ventana, text="Cerrar", font=("Minecraft", 13),
                  bg="#2a2118", fg="white", relief="flat", bd=0,
                  activebackground="#3a3128", activeforeground="white",
                  cursor="hand2", padx=20, pady=6,
                  command=ventana.destroy).pack(pady=22)

    crear_boton_imagen(frame, canvas, ruta("info.png"), "",
                ruta("fuente_minecraft.ttf"), 1,
                x=50, y=910, ancho=50, alto=50,
                comando=mostrar_info)