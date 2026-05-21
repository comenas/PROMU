import tkinter as tk
import os
from tkinter import filedialog
from interfaces.ui import crear_boton_imagen, crear_canvas, crear_entrada, limpiar_frame
from core.formatter import format_results
from core.matemáticas import Mat_obj1_AD, Mat_obj8_Altura, Mat_obj7_Puntos

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "archivos_interfaz")

def ruta(nombre):
    return os.path.join(BASE, nombre)


def pantalla_gestion_salto(root, frame):
    """Pantalla para enviar un salto — solo usuarios autenticados."""
    limpiar_frame(frame)
    canvas    = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 80, text="Enviar Salto",
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

    # ── Mensaje de estado en canvas (sin fondo, no tapa nada) ────────────────
    msg_id = canvas.create_text(640, 325, text="",
                                font=("Minecraft", 13), fill="#55ff55", anchor="center")

    _timer    = [None]
    

    def mostrar_mensaje(texto, color="#55ff55", duracion_ms=3000):
        canvas.itemconfig(msg_id, text=texto, fill=color)
        if _timer[0]:
            root.after_cancel(_timer[0])
            _timer[0] = None
        if duracion_ms > 0:
            _timer[0] = root.after(duracion_ms,
                                   lambda: canvas.itemconfig(msg_id, text=""))
    
    # ── Cuadro de resultados ─────────────────────────────────────────────────────
    resultado_frame = tk.Frame(frame, bg="#1a1108")
    canvas.create_window(640, 490, window=resultado_frame, width=600, height=160)

    txt_resultados = tk.Text(resultado_frame, font=("Minecraft", 12),
                          bg="#2a2118", fg="#00ff99",
                          relief="flat", wrap="word", state="disabled")
    txt_resultados.pack(fill="both", expand=True)

    def gestionar():
        path = ruta_xlsx.get()
        if not path:
            mostrar_mensaje("Selecciona un archivo .xlsx primero.", "#ff5555")
            return
        mostrar_mensaje("Analizando salto...", "#ffff55", duracion_ms=0)

        try:
            t, ace_y, ace        = Mat_obj1_AD(path)
            idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace, ace_y, t)
            h1, h2, h3           = Mat_obj8_Altura(ace, ace_y, t)
        except Exception as e:
            mostrar_mensaje(f"Error al analizar: {e}", "#ff5555")
            return

        resultados = {
            "altura_vuelo":          h1,
            "altura_velocidad":      h2,
            "altura_desplazamiento": h3,
            "tiempo_vuelo":          t_aire,
            "velocidad_despegue":    velocidad[idx_T0],
        }
        from core.formatter import format_results
        formateados = format_results(resultados)

        txt_resultados.config(state="normal")
        txt_resultados.delete("1.0", "end")
        for clave, valor in formateados.items():
            txt_resultados.insert("end", f"{clave}: {valor}\n")
        txt_resultados.config(state="disabled")

    mostrar_mensaje("Análisis completado.", "#55ff55")
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Analizar",
                ruta("fuente_minecraft.ttf"), 20,
                x=640, y=680, ancho=400, alto=45,
                comando=gestionar)

    from interfaces.principal import pantalla_principal
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                ruta("fuente_minecraft.ttf"), 20,
                x=640, y=745, ancho=400, alto=45,
                comando=lambda: pantalla_principal(root, frame))
