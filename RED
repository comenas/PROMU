
import socket
import json
import threading
 
# ── Configuración ─────────────────────────────────────────────────────────────
 
IP_SERVIDOR = "158.42.188.200"
IP_CLIENTE  = "10.236.35.228"
SERVER_PORT = 64010
 
# ── Estado global de sesión ───────────────────────────────────────────────────
 
sesion = {
    "socket":      None,
    "autenticado": False,
    "usuario":     None,
}
 
# ── Primitivas de lectura ─────────────────────────────────────────────────────
 
def recibir_linea(sock):
    """Lee del socket byte a byte hasta encontrar \\r\\n."""
    data = b""
    while not data.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode()
 
def recibir_leaderboard(sock):
    """Lee líneas del leaderboard hasta el marcador de fin."""
    lineas = []
    while True:
        linea = recibir_linea(sock)
        lineas.append(linea.strip())
        if "202 NO HAY MÁS REGISTROS" in linea or "201 NO HAY REGISTROS TODAVIA" in linea:
            break
    return lineas
 
# ── Operaciones de alto nivel (asíncronas, usan hilos) ───────────────────────
 
def conectar_y_autenticar(usuario, password, callback_ok, callback_err):
    """
    Conecta al servidor y realiza el handshake HELLO / USER / PASS
    en un hilo secundario para no bloquear la UI.
 
    callback_ok()       → se llama si la autenticación tiene éxito.
    callback_err(msg)   → se llama con el mensaje de error si falla.
    """
    def _tarea():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(60)
            sock.connect((IP_SERVIDOR, SERVER_PORT))
 
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
 
            # Éxito: guardamos el socket en la sesión
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
    Si hay sesión activa la reutiliza; si no, abre una conexión anónima.
 
    callback(lineas: list[str]) → recibe las líneas del ranking.
    """
    def _tarea():
        try:
            if sesion["socket"]:
                sock   = sesion["socket"]
                propio = False
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect((IP_SERVIDOR, SERVER_PORT))
                sock.send(f"HELLO {IP_CLIENTE}\r\n".encode())
                recibir_linea(sock)   # descartamos el "100 OK"
                propio = True
 
            sock.send(f"{comando}\r\n".encode())
            lineas = recibir_leaderboard(sock)
 
            if propio:
                sock.close()
 
            callback(lineas)
        except Exception as e:
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
            if not sesion["socket"]:
                callback("No hay sesión activa.")
                return
            data    = {"grupo_ProMu": grupo, "altura": int(altura)}
            mensaje = f"SEND_DATA {json.dumps(data)}\r\n"
            sesion["socket"].send(mensaje.encode())
            resp = recibir_linea(sesion["socket"])
            callback(resp.strip())
        except Exception as e:
            callback(f"ERROR: {e}")
 
    threading.Thread(target=_tarea, daemon=True).start()
 
 
def cerrar_sesion():
    """Envía QUIT al servidor y limpia el estado de sesión."""
    if sesion["socket"]:
        try:
            sesion["socket"].send("QUIT\r\n".encode())
        except Exception:
            pass
        sesion["socket"].close()
    sesion["socket"]      = None
    sesion["autenticado"] = False
    sesion["usuario"]     = None
