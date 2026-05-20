# red.py – Toda la lógica de red y estado de sesión
# La interfaz gráfica importa desde aquí; este módulo no sabe nada de tkinter.
 
import socket
import json
 
# ── Configuración ─────────────────────────────────────────────────────────────
 
IP_SERVIDOR = "158.42.188.200"
IP_CLIENTE  = "192.168.1.142"
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
 
# ── Operaciones de alto nivel (síncronas) ────────────────────────────────────
# AVISO: estas funciones bloquean la UI mientras esperan respuesta del servidor.
 
def conectar_y_autenticar(usuario, password):
    """
    Conecta al servidor y realiza el handshake HELLO / USER / PASS.
    Devuelve (True, None) si tiene éxito o (False, mensaje_error) si falla.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((IP_SERVIDOR, SERVER_PORT))
 
        # HELLO
        sock.send(f"HELLO {IP_CLIENTE}\r\n".encode())
        resp = recibir_linea(sock)
        if not resp.startswith("100"):
            sock.close()
            return False, f"Error HELLO: {resp.strip()}"
 
        # USER
        sock.send(f"USER {usuario}\r\n".encode())
        resp = recibir_linea(sock)
        if not resp.startswith("101"):
            sock.close()
            return False, f"Error USER: {resp.strip()}"
 
        # PASS
        sock.send(f"PASS {password}\r\n".encode())
        resp = recibir_linea(sock)
        if not resp.startswith("102"):
            sock.close()
            return False, f"Credenciales incorrectas: {resp.strip()}"
 
        # Éxito
        sesion["socket"]      = sock
        sesion["autenticado"] = True
        sesion["usuario"]     = usuario
        return True, None
 
    except socket.timeout:
        return False, "Tiempo de conexión agotado."
    except Exception as e:
        return False, str(e)
 
 
def pedir_leaderboard(comando):
    """
    Solicita un leaderboard al servidor.
    Si hay sesión activa la reutiliza; si no, abre una conexión anónima.
    Devuelve list[str] con las líneas del ranking, o una lista con el error.
    """
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
 
        return lineas
    except Exception as e:
        return [f"ERROR: {e}"]
 
 
def enviar_salto(grupo, altura):
    """
    Envía SEND_DATA con el grupo y la altura al servidor.
    Requiere sesión autenticada.
    Devuelve la respuesta del servidor como str, o un mensaje de error.
    """
    try:
        if not sesion["socket"]:
            return "No hay sesión activa."
        data    = {"grupo_ProMu": grupo, "altura": int(altura)}
        mensaje = f"SEND_DATA {json.dumps(data)}\r\n"
        sesion["socket"].send(mensaje.encode())
        return recibir_linea(sesion["socket"]).strip()
    except Exception as e:
        return f"ERROR: {e}"
 
 
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
 