import tkinter as tk
import os
from interfaces.guizero.common.ui import crear_boton_imagen, crear_canvas, crear_entrada, limpiar_frame
from servidor.red import conectar_y_autenticar

BBASEI = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "imagenes")
BASEF = os.path.join(os.path.dirname(__file__), "..", "..", "..", "archivos_interfaz", "fuentes")

def ruta(nombre):
    if "png" in nombre:
        return os.path.join(BBASEI, nombre)
    elif "ttf" in nombre:
        return os.path.join(BASEF, nombre)
    else:
        raise ValueError("Archivo no reconocido: " + nombre)



def pantalla_inicio_sesion(root, frame):
    limpiar_frame(frame)
    canvas = crear_canvas(frame, ruta("minecraft_inicio_sesion.png"))
    fuente_mc = ("Minecraft", 16)

    canvas.create_text(640, 250, text="Inicia sesión en el servidor UPV",
                       font=("Minecraft", 24), fill="white", anchor="center")
    canvas.create_text(640, 360, text="Usuario",
                       font=("Minecraft", 14), fill="white", anchor="center")
    canvas.create_text(640, 460, text="Contraseña",
                       font=("Minecraft", 14), fill="white", anchor="center")

    entrada_usuario = crear_entrada(frame, canvas, x=640, y=400, ancho=400, alto=40,
                                    imagen_caja=ruta("minecraft_caja.png"), fuente=fuente_mc)
    entrada_password = crear_entrada(frame, canvas, x=640, y=500, ancho=400, alto=40,
                                     imagen_caja=ruta("minecraft_caja.png"), fuente=fuente_mc,
                                     password=True)

    # ── Mensaje de estado en canvas ──────────────────────────────────────────
    # Usamos canvas.create_text: no tiene fondo, nunca tapa otros widgets.
    msg_id = canvas.create_text(640, 558, text="",
                                font=("Minecraft", 13), fill="#ffff55", anchor="center")

    _timer      = [None]   # contenedor mutable para poder cancelar el after()
    _procesando = [False]  # bloquea el botón mientras hay una operación en curso

    def mostrar_mensaje(texto, color="#ffff55", duracion_ms=3000):
        """Muestra texto en el canvas y lo borra automáticamente tras duracion_ms.
        Si duracion_ms == 0, el mensaje permanece hasta que se llame de nuevo."""
        canvas.itemconfig(msg_id, text=texto, fill=color)
        if _timer[0]:
            root.after_cancel(_timer[0])
            _timer[0] = None
        if duracion_ms > 0:
            _timer[0] = root.after(duracion_ms,
                                   lambda: canvas.itemconfig(msg_id, text=""))

    def limpiar_mensaje():
        canvas.itemconfig(msg_id, text="")
        if _timer[0]:
            root.after_cancel(_timer[0])
            _timer[0] = None

    # ── Lógica de inicio de sesión ────────────────────────────────────────────
    def iniciar_sesion():
        if _procesando[0]:   # impide doble clic mientras conecta
            return

        usuario  = entrada_usuario.get().strip()
        password = entrada_password.get().strip()

        if not usuario or not password:
            mostrar_mensaje("Introduce usuario y contraseña", "#ff5555")
            return

        _procesando[0] = True
        mostrar_mensaje("Conectando...", "#ffff55", duracion_ms=0)  # sin auto-borrado

        def on_ok():
            _procesando[0] = False
            limpiar_mensaje()
            from interfaces.principal import pantalla_principal
            root.after(0, lambda: pantalla_principal(root, frame))

        def on_err(msg):
            _procesando[0] = False
            root.after(0, lambda: mostrar_mensaje(msg, "#ff5555"))

        conectar_y_autenticar(usuario, password, on_ok, on_err)

    # ── Botones ───────────────────────────────────────────────────────────────
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Iniciar sesión",
                       ruta("fuente_minecraft.ttf"), 18,
                       x=640, y=615, ancho=400, alto=40,
                       comando=iniciar_sesion)

    from interfaces.guizero.common.principal import pantalla_principal
    crear_boton_imagen(frame, canvas, ruta("minecraft_boton.png"), "Volver",
                       ruta("fuente_minecraft.ttf"), 18,
                       x=640, y=668, ancho=400, alto=40,
                       comando=lambda: pantalla_principal(root, frame))