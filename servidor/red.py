import socket
import json
import threading

# ── Configuración ──────────────────────────────────────────────────────────────

IP_SERVIDOR  = "158.42.188.200"
hostname = socket.gethostname()
IP_CLIENTE = socket.gethostbyname(hostname)

SERVER_PORT  = 64010
TIMEOUT_CONN = 60   # segundos para la conexión inicial
TIMEOUT_OP   = 10   # segundos para operaciones sobre el socket de sesión
MAX_MSG      = 4096 # bytes máximos por línea antes de abortar

# ── Estado global de sesión ────────────────────────────────────────────────────

_lock = threading.Lock()   # protege sesion y el socket frente a accesos concurrentes

sesion = {
    "socket":      None,
    "autenticado": False,
    "usuario":     None,
}

# ── Primitivas de lectura ──────────────────────────────────────────────────────

def recibir_linea(sock):
    """Lee del socket byte a byte hasta encontrar \\r\\n.
    Lanza RuntimeError si la conexión se cierra o el mensaje supera MAX_MSG bytes."""
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
    """Lee líneas del leaderboard hasta el marcador de fin.
    Devuelve lista de strings. El socket debe tener timeout configurado."""
    MARCADORES_FIN = ("202 NO HAY MÁS REGISTROS", "201 NO HAY REGISTROS TODAVIA")
    lineas = []
    while True:
        linea = recibir_linea(sock).strip()
        lineas.append(linea)
        if any(m in linea for m in MARCADORES_FIN):
            break
    return lineas


# ── Helpers internos ───────────────────────────────────────────────────────────

def _abrir_socket_anonimo():
    """Abre una conexión TCP sin autenticación y devuelve el socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT_OP)
    sock.connect((IP_SERVIDOR, SERVER_PORT))
    sock.send(f"HELLO {IP_CLIENTE}\r\n".encode())
    recibir_linea(sock)   # descartamos el "100 OK"
    return sock


# ── Operaciones de alto nivel (asíncronas, usan hilos) ────────────────────────

def conectar_y_autenticar(usuario, password, callback_ok, callback_err):
    """
    Conecta al servidor y realiza el handshake HELLO / USER / PASS
    en un hilo secundario para no bloquear la UI.

    callback_ok()       → llamado si la autenticación tiene éxito.
    callback_err(msg)   → llamado con el mensaje de error si falla.
    """
    def _tarea():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT_CONN)
            sock.connect((IP_SERVIDOR, SERVER_PORT))
            sock.settimeout(TIMEOUT_OP)  # tras conectar, timeout de operación normal

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

            # Éxito: guardamos el socket bajo lock
            with _lock:
                sesion["socket"]      = sock
                sesion["autenticado"] = True
                sesion["usuario"]     = usuario

            callback_ok()

        except socket.timeout:
            callback_err("Tiempo de conexión agotado.")
        except Exception as e:
            callback_err(str(e))

    threading.Thread(target=_tarea, daemon=True).start()


def pedir_leaderboard(comando, callback):
    """
    Solicita un leaderboard al servidor en un hilo secundario.
    Si hay sesión activa la reutiliza (con lock); si no, abre conexión anónima.

    callback(lineas: list[str]) → recibe las líneas del ranking.
    """
    def _tarea():
        sock_propio = False
        try:
            with _lock:
                sock_sesion = sesion["socket"]

            if sock_sesion:
                # Reutilizamos el socket de sesión; el lock evita solapamiento
                with _lock:
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

    threading.Thread(target=_tarea, daemon=True).start()


def enviar_salto(grupo, altura, callback):
    """
    Envía SEND_DATA con el grupo y la altura al servidor en un hilo secundario.
    Requiere sesión autenticada.

    callback(respuesta: str) → recibe la respuesta del servidor.
    """
    def _tarea():
        try:
            with _lock:
                sock = sesion["socket"]

            if not sock:
                callback("No hay sesión activa.")
                return

            data    = {"grupo_ProMu": grupo, "altura": int(altura)}
            mensaje = f"SEND_DATA {json.dumps(data)}\r\n"

            with _lock:
                sock.send(mensaje.encode())
                resp = recibir_linea(sock)

            callback(resp.strip())

        except Exception as e:
            callback(f"ERROR: {e}")

    threading.Thread(target=_tarea, daemon=True).start()


def cerrar_sesion():
    """Envía QUIT al servidor y limpia el estado de sesión de forma thread-safe."""
    with _lock:
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