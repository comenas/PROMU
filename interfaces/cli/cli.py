import sys
import os
import socket
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.matemáticas import Mat_obj1_AD, Mat_obj7_Puntos, Mat_obj8_Altura
from core.formatter import format_results

# ── Configuración del servidor ────────────────────────────────────────────────
IP_SERVIDOR = "158.42.188.200"
SERVER_PORT = 64010
TIMEOUT     = 10
MAX_MSG     = 4096

# ── Estado de sesión ──────────────────────────────────────────────────────────
sesion = {
    "socket":      None,
    "autenticado": False,
    "usuario":     None,
}

# ── Utilidades de consola ─────────────────────────────────────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def titulo(texto):
    print("\n" + "=" * 50)
    print(f"  {texto}")
    print("=" * 50)

def pedir(texto):
    return input(f"  {texto}: ").strip()

def mensaje(texto, prefijo=">>"):
    print(f"\n  {prefijo} {texto}")

# ── Primitivas de red (síncronas, sin tkinter) ────────────────────────────────

def recibir_linea(sock):
    data = b""
    while not data.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise RuntimeError("Conexión cerrada por el servidor.")
        data += chunk
        if len(data) > MAX_MSG:
            raise RuntimeError("Respuesta demasiado larga.")
    return data.decode("utf-8", errors="replace")

def recibir_leaderboard(sock):
    MARCADORES_FIN = ("202 NO HAY MÁS REGISTROS", "201 NO HAY REGISTROS TODAVIA")
    lineas = []
    while True:
        linea = recibir_linea(sock).strip()
        lineas.append(linea)
        if any(m in linea for m in MARCADORES_FIN):
            break
    return lineas

def abrir_socket_anonimo():
    hostname = socket.gethostname()
    ip       = socket.gethostbyname(hostname)
    sock     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    sock.connect((IP_SERVIDOR, SERVER_PORT))
    sock.send(f"HELLO {ip}\r\n".encode())
    recibir_linea(sock)
    return sock

# ── Acciones de red ───────────────────────────────────────────────────────────

def accion_iniciar_sesion():
    titulo("INICIAR SESIÓN")
    usuario  = pedir("Usuario")
    password = pedir("Contraseña")

    mensaje("Conectando al servidor…")
    try:
        hostname = socket.gethostname()
        ip       = socket.gethostbyname(hostname)
        sock     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60)
        sock.connect((IP_SERVIDOR, SERVER_PORT))
        sock.settimeout(TIMEOUT)

        sock.send(f"HELLO {ip}\r\n".encode())
        resp = recibir_linea(sock)
        if not resp.startswith("100"):
            mensaje(f"Error HELLO: {resp.strip()}", "!!")
            sock.close()
            return

        sock.send(f"USER {usuario}\r\n".encode())
        resp = recibir_linea(sock)
        if not resp.startswith("101"):
            mensaje(f"Error USER: {resp.strip()}", "!!")
            sock.close()
            return

        sock.send(f"PASS {password}\r\n".encode())
        resp = recibir_linea(sock)
        if not resp.startswith("102"):
            mensaje(f"Credenciales incorrectas: {resp.strip()}", "!!")
            sock.close()
            return

        sesion["socket"]      = sock
        sesion["autenticado"] = True
        sesion["usuario"]     = usuario
        mensaje(f"Sesión iniciada como {usuario}.", "OK")

    except socket.timeout:
        mensaje("Tiempo de conexión agotado.", "!!")
    except Exception as e:
        mensaje(str(e), "!!")

def accion_cerrar_sesion():
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
    mensaje("Sesión cerrada.", "OK")

def accion_ver_ranking(comando, titulo_ranking):
    titulo(titulo_ranking)
    mensaje("Descargando ranking…")
    try:
        sock_sesion = sesion["socket"]
        if sock_sesion:
            sock_sesion.send(f"{comando}\r\n".encode())
            lineas = recibir_leaderboard(sock_sesion)
        else:
            sock = abrir_socket_anonimo()
            sock.send(f"{comando}\r\n".encode())
            lineas = recibir_leaderboard(sock)
            sock.close()
        print()
        for linea in lineas:
            print(f"  {linea}")
    except Exception as e:
        mensaje(str(e), "!!")

def accion_analizar_salto():
    titulo("ANALIZAR SALTO")
    path = pedir("Ruta del fichero .xlsx  (ej: C:/Users/yo/salto.xlsx)")
    if not os.path.exists(path):
        mensaje("Fichero no encontrado.", "!!")
        return None, None

    mensaje("Analizando…")
    try:
        t, ace_y, ace                    = Mat_obj1_AD(path)
        idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace, ace_y, t)
        h1, h2, h3                       = Mat_obj8_Altura(ace, ace_y, t)
    except Exception as e:
        mensaje(f"Error al analizar: {e}", "!!")
        return None, None

    resultados = {
        "altura_vuelo":          h1,
        "altura_velocidad":      h2,
        "altura_desplazamiento": h3,
        "tiempo_vuelo":          t_aire,
        "velocidad_despegue":    velocidad[idx_T0],
    }
    formateados = format_results(resultados)

    print()
    print("  ┌─────────────────────────────────────────┐")
    for clave, valor in formateados.items():
        print(f"  │  {clave:<28} {valor:>6}   │")
    print("  └─────────────────────────────────────────┘")

    return h1, formateados

def accion_enviar_salto():
    titulo("ENVIAR SALTO")
    grupo = pedir("Grupo ProMu (ej: A2-4)")
    if not grupo:
        mensaje("El grupo no puede estar vacío.", "!!")
        return

    h1, _ = accion_analizar_salto()
    if h1 is None:
        return

    altura_mm = int(h1 * 1000)
    mensaje(f"Enviando altura {altura_mm} mm al servidor…")
    try:
        sock = sesion["socket"]
        if not sock:
            mensaje("No hay sesión activa.", "!!")
            return
        data    = {"grupo_ProMu": grupo, "altura": altura_mm}
        mensaje_red = f"SEND_DATA {json.dumps(data)}\r\n"
        sock.send(mensaje_red.encode())
        resp = recibir_linea(sock)
        mensaje(resp.strip(), "OK")
    except Exception as e:
        mensaje(str(e), "!!")

# ── Menús ─────────────────────────────────────────────────────────────────────

def menu_invitado():
    while True:
        limpiar()
        titulo("MENÚ INVITADO")
        print("  1. Analizar salto")
        print("  2. Ver ranking masculino")
        print("  3. Ver ranking femenino")
        print("  0. Volver")
        opcion = pedir("Opción")

        if opcion == "1":
            accion_analizar_salto()
            input("\n  Pulsa Enter para continuar…")
        elif opcion == "2":
            accion_ver_ranking("GET_LEADERBOARD_MEN", "RANKING MASCULINO")
            input("\n  Pulsa Enter para continuar…")
        elif opcion == "3":
            accion_ver_ranking("GET_LEADERBOARD_WOMEN", "RANKING FEMENINO")
            input("\n  Pulsa Enter para continuar…")
        elif opcion == "0":
            break
        else:
            mensaje("Opción no válida.", "!!")
            input("\n  Pulsa Enter para continuar…")

def menu_usuario():
    while True:
        limpiar()
        titulo(f"MENÚ USUARIO — {sesion['usuario']}")
        print("  1. Enviar salto")
        print("  2. Ver ranking masculino")
        print("  3. Ver ranking femenino")
        print("  4. Cerrar sesión")
        print("  0. Salir")
        opcion = pedir("Opción")

        if opcion == "1":
            accion_enviar_salto()
            input("\n  Pulsa Enter para continuar…")
        elif opcion == "2":
            accion_ver_ranking("GET_LEADERBOARD_MEN", "RANKING MASCULINO")
            input("\n  Pulsa Enter para continuar…")
        elif opcion == "3":
            accion_ver_ranking("GET_LEADERBOARD_WOMEN", "RANKING FEMENINO")
            input("\n  Pulsa Enter para continuar…")
        elif opcion == "4":
            accion_cerrar_sesion()
            input("\n  Pulsa Enter para continuar…")
            break
        elif opcion == "0":
            sys.exit(0)
        else:
            mensaje("Opción no válida.", "!!")
            input("\n  Pulsa Enter para continuar…")

def menu_principal():
    while True:
        limpiar()
        titulo("VLC_JUMP — MENÚ PRINCIPAL")
        print("  1. Iniciar sesión")
        print("  2. Continuar como invitado")
        print("  0. Salir")
        opcion = pedir("Opción")

        if opcion == "1":
            accion_iniciar_sesion()
            input("\n  Pulsa Enter para continuar…")
            if sesion["autenticado"]:
                menu_usuario()
        elif opcion == "2":
            menu_invitado()
        elif opcion == "0":
            sys.exit(0)
        else:
            mensaje("Opción no válida.", "!!")
            input("\n  Pulsa Enter para continuar…")

# ── Punto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    menu_principal()