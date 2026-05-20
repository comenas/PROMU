import socket
import json

# ── Configuración ──────────────────────────────────────────────────────────────

IP_SERVIDOR  = "158.42.188.200"
hostname     = socket.gethostname()
IP_CLIENTE   = socket.gethostbyname(hostname)

SERVER_PORT  = 64010
TIMEOUT_CONN = 60   # segundos para la conexión inicial
TIMEOUT_OP   = 10   # segundos para operaciones sobre el socket de sesión
MAX_MSG      = 4096 # bytes máximos por línea antes de abortar

# ── Estado global ──────────────────────────────────────────────────────────────

sesion = {
    "socket":      None,
    "autenticado": False,
    "usuario":     None,
}

# root de tkinter — se inyecta desde main.py llamando a inicializar(root)
_root = None

def inicializar(root):
    """Debe llamarse desde main.py antes de usar cualquier función de red."""
    global _root
    _root = root


# ── Primitivas de lectura ──────────────────────────────────────────────────────

def recibir_linea(sock):
    """Lee del socket byte a byte hasta encontrar \\r\\n (bloqueante con timeout)."""
    data = b""
    while not data.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise RuntimeError("Conexión cerrada por el servidor.")
        data += chunk
        if len(data) > MAX_MSG:
            raise RuntimeError("Respuesta del servidor demasiado larga.")
    return data.decode("utf-8", errors="replace")


def recibir_leaderboard(sock):
    """Lee líneas del leaderboard hasta el marcador de fin."""
    MARCADORES_FIN = ("202 NO HAY MÁS REGISTROS", "201 NO HAY REGISTROS TODAVIA")
    lineas = []
    while True:
        linea = recibir_linea(sock).strip()
        lineas.append(linea)
        if any(m in linea for m in MARCADORES_FIN):
            break
    return lineas


def _abrir_socket_anonimo():
    """Abre una conexión TCP sin autenticación y devuelve el socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT_OP)
    sock.connect((IP_SERVIDOR, SERVER_PORT))
    sock.send(f"HELLO {IP_CLIENTE}\r\n".encode())
    recibir_linea(sock)   # descartamos el "100 OK"
    return sock


# ── Operaciones de alto nivel (sin hilos, usan root.after para no bloquear UI) ─

def conectar_y_autenticar(usuario, password, callback_ok, callback_err):
    """
    Conecta y autentica al servidor.
    Usa root.after(1, ...) para ejecutarse fuera del evento actual de tkinter
    y evitar congelar la UI durante la operación de red.

    callback_ok()      → llamado si la autenticación tiene éxito.
    callback_err(msg)  → llamado con el mensaje de error si falla.
    """
    def _ejecutar():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT_CONN)
            sock.connect((IP_SERVIDOR, SERVER_PORT))
            sock.settimeout(TIMEOUT_OP)

            # HELLO
            sock.send(f"HELLO {IP_CLIENTE}\r\n".encode())
            resp = recibir_linea(sock)
            if not resp.startswith("100"):
                sock.close()
                callback_err(f"Error HELLO: {resp.strip()}")
                return

            # USER
            sock.send(f"USER {usuario}\r\n".encode())
            resp = recibir_linea(sock)
            if not resp.startswith("101"):
                sock.close()
                callback_err(f"Error USER: {resp.strip()}")
                return

            # PASS
            sock.send(f"PASS {password}\r\n".encode())
            resp = recibir_linea(sock)
            if not resp.startswith("102"):
                sock.close()
                callback_err(f"Credenciales incorrectas: {resp.strip()}")
                return

            # Éxito
            sesion["socket"]      = sock
            sesion["autenticado"] = True
            sesion["usuario"]     = usuario

            callback_ok()

        except socket.timeout:
            callback_err("Tiempo de conexión agotado.")
        except Exception as e:
            callback_err(str(e))

    # Diferimos 1 ms para que tkinter pueda actualizar la UI (p.ej. "Conectando...")
    # antes de que el socket bloquee el hilo principal.
    _root.after(1, _ejecutar)


def pedir_leaderboard(comando, callback):
    """
    Solicita un leaderboard al servidor.
    Si hay sesión activa la reutiliza; si no, abre conexión anónima.

    callback(lineas: list[str]) → recibe las líneas del ranking.
    """
    def _ejecutar():
        sock_propio = False
        try:
            sock_sesion = sesion["socket"]

            if sock_sesion:
                sock_sesion.send(f"{comando}\r\n".encode())
                lineas = recibir_leaderboard(sock_sesion)
            else:
                sock = _abrir_socket_anonimo()
                sock_propio = True
                sock.send(f"{comando}\r\n".encode())
                lineas = recibir_leaderboard(sock)
                sock.close()

            callback(lineas)

        except Exception as e:
            if sock_propio:
                try:
                    sock.close()
                except Exception:
                    pass
            callback([f"ERROR: {e}"])

    _root.after(1, _ejecutar)


def enviar_salto(grupo, altura, callback):
    """
    Envía SEND_DATA con el grupo y la altura al servidor.
    Requiere sesión autenticada.

    callback(respuesta: str) → recibe la respuesta del servidor.
    """
    def _ejecutar():
        try:
            sock = sesion["socket"]

            if not sock:
                callback("No hay sesión activa.")
                return

            data    = {"grupo_ProMu": grupo, "altura": int(altura)}
            mensaje = f"SEND_DATA {json.dumps(data)}\r\n"

            sock.send(mensaje.encode())
            resp = recibir_linea(sock)

            callback(resp.strip())

        except Exception as e:
            callback(f"ERROR: {e}")

    _root.after(1, _ejecutar)


def cerrar_sesion():
    """Envía QUIT al servidor y limpia el estado de sesión."""
    sock = sesion["socket"]
    if sock:
        try:
            sock.send("QUIT\r\n".encode())
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass
    sesion["socket"]      = None
    sesion["autenticado"] = False
    sesion["usuario"]     = None
