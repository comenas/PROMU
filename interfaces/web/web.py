"""
interfaces/web/web.py  —  Interfaz web Minecraft-themed para VLC_Jump
Ejecutar:  python interfaces/web/web.py
Abrir:     http://localhost:5000
"""

import os, sys, tempfile, socket, json
from flask import (Flask, request, render_template_string,
                   redirect, url_for, session, send_file)

# ── Paths ─────────────────────────────────────────────────────────────────────
# Sube 3 niveles: web/ → interfaces/ → promu/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)
IMAGENES = os.path.join(BASE_DIR, "archivos_interfaz", "imagenes")
FUENTES  = os.path.join(BASE_DIR, "archivos_interfaz", "fuentes")

from core.matemáticas import Mat_obj1_AD, Mat_obj7_Puntos, Mat_obj8_Altura
from core.formatter   import format_results

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "vlcjump_2526"

# ── Servidor ──────────────────────────────────────────────────────────────────
IP_SERVIDOR = "158.42.188.200"
SERVER_PORT = 64010
TIMEOUT     = 10
MAX_MSG     = 4096

# ══════════════════════════════════════════════════════════════════════════════
# RED — funciones síncronas (igual que cli.py pero sin menús)
# ══════════════════════════════════════════════════════════════════════════════

def _recibir_linea(sock):
    data = b""
    while not data.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise RuntimeError("Conexión cerrada por el servidor.")
        data += chunk
        if len(data) > MAX_MSG:
            raise RuntimeError("Respuesta demasiado larga.")
    return data.decode("utf-8", errors="replace")

def _recibir_leaderboard(sock):
    MARCADORES = ("202 NO HAY MAS REGISTROS", "201 NO HAY REGISTROS TODAVIA")
    lineas = []
    while True:
        linea = _recibir_linea(sock).strip()
        lineas.append(linea)
        if any(m in linea for m in MARCADORES):
            break
    return lineas

def red_login(usuario, password):
    """Devuelve (True, None) si OK, o (False, mensaje_error)."""
    try:
        ip   = socket.gethostbyname(socket.gethostname())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60)
        sock.connect((IP_SERVIDOR, SERVER_PORT))
        sock.settimeout(TIMEOUT)

        sock.send(f"HELLO {ip}\r\n".encode())
        if not _recibir_linea(sock).startswith("200"):
            sock.close(); return False, "Error en HELLO"

        sock.send(f"USER {usuario}\r\n".encode())
        if not _recibir_linea(sock).startswith("200"):
            sock.close(); return False, "Usuario no encontrado"

        sock.send(f"PASS {password}\r\n".encode())
        if not _recibir_linea(sock).startswith("200"):
            sock.close(); return False, "Contraseña incorrecta"

        sock.close()
        return True, None
    except socket.timeout:
        return False, "Tiempo de conexión agotado"
    except Exception as e:
        return False, str(e)

def red_leaderboard(comando):
    """Devuelve lista de líneas del leaderboard."""
    try:
        ip   = socket.gethostbyname(socket.gethostname())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((IP_SERVIDOR, SERVER_PORT))
        sock.send(f"HELLO {ip}\r\n".encode())
        _recibir_linea(sock)
        sock.send(f"{comando}\r\n".encode())
        lineas = _recibir_leaderboard(sock)
        sock.close()
        return lineas
    except Exception as e:
        return [f"ERROR: {e}"]

def red_enviar_salto(usuario, password, grupo, altura_mm):
    """Conecta, autentica, envía salto y devuelve respuesta del servidor."""
    try:
        ip   = socket.gethostbyname(socket.gethostname())
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60)
        sock.connect((IP_SERVIDOR, SERVER_PORT))
        sock.settimeout(TIMEOUT)

        sock.send(f"HELLO {ip}\r\n".encode());   _recibir_linea(sock)
        sock.send(f"USER {usuario}\r\n".encode()); _recibir_linea(sock)
        sock.send(f"PASS {password}\r\n".encode()); _recibir_linea(sock)

        data = json.dumps({"grupo_ProMu": grupo, "altura": int(altura_mm)})
        sock.send(f"SEND_DATA {data}\r\n".encode())
        resp = _recibir_linea(sock).strip()
        sock.close()
        return resp
    except Exception as e:
        return f"ERROR: {e}"

# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISIS — mismas funciones del core que cli.py y gui.py
# ══════════════════════════════════════════════════════════════════════════════

def analizar_fichero(ruta):
    """Llama al core y devuelve (resultados_formateados, h1_metros, error)."""
    try:
        t, ace_y, ace                    = Mat_obj1_AD(ruta)
        idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace, ace_y, t)
        h1, h2, h3                       = Mat_obj8_Altura(ace, ace_y, t)
    except Exception as e:
        return None, None, str(e)

    raw = {
        "altura_vuelo":          h1,
        "altura_velocidad":      h2,
        "altura_desplazamiento": h3,
        "tiempo_vuelo":          t_aire,
        "velocidad_despegue":    velocidad[idx_T0],
    }
    return format_results(raw), h1, None

def asignar_personaje(altura_m):
    cm = altura_m * 100
    if   cm <= 15: return ("Slime",        "slime.png",        "#55ff55", "Pequeño pero pegajoso. ¡Sigue saltando!")
    elif cm <= 30: return ("Lobo",         "lobo.png",         "#aaaaff", "Fiel y persistente. ¡Buen salto!")
    elif cm <= 45: return ("Creeper",      "creeper.png",      "#44cc44", "¡Explosivo en la pista!")
    elif cm <= 59: return ("Enderman",     "enderman.png",     "#cc88ff", "Largo y veloz. ¡Impresionante!")
    else:          return ("Ender Dragon", "ender_dragon.png", "#aa00ff", "El jefe definitivo. ¡Eres una leyenda!")

# ══════════════════════════════════════════════════════════════════════════════
# STATIC — sirve la fuente e imágenes
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/fuente")
def fuente():
    return send_file(os.path.join(FUENTES, "fuente_minecraft.ttf"))

@app.route("/imagen/<nombre>")
def imagen(nombre):
    return send_file(os.path.join(IMAGENES, nombre))

# ══════════════════════════════════════════════════════════════════════════════
# BASE HTML
# ══════════════════════════════════════════════════════════════════════════════

BASE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Minecraft: Jump Edition</title>
  <style>
    @font-face { font-family:'Minecraft'; src:url('/fuente') format('truetype'); }
    * { box-sizing:border-box; margin:0; padding:0; }
    body {
      font-family:'Minecraft',monospace; background:#1a1108; color:white;
      min-height:100vh; display:flex; flex-direction:column;
      align-items:center; justify-content:flex-start; padding:2rem 1rem;
    }
    h1 { font-size:2.2rem; color:#00ff99; text-shadow:3px 3px #005533;
         margin-bottom:0.4rem; letter-spacing:2px; }
    h2 { font-size:1.4rem; color:#ffff55; margin-bottom:1.5rem; }
    p  { color:#aaaaaa; margin-bottom:1.5rem; font-size:0.9rem; }
    .panel {
      background:#2a2118; border:2px solid #3a3128; padding:2rem;
      border-radius:4px; width:100%; max-width:480px;
      display:flex; flex-direction:column; gap:1rem; margin-top:1rem;
    }
    .btn {
      display:block; width:100%; padding:0.75rem 1rem;
      font-family:'Minecraft',monospace; font-size:1rem; color:white;
      background:#3a6e3a; border:none; border-bottom:3px solid #1e3e1e;
      cursor:pointer; text-align:center; text-decoration:none;
    }
    .btn:hover  { background:#55aa55; }
    .btn.gris   { background:#555; border-bottom-color:#333; }
    .btn.gris:hover { background:#777; }
    .btn.rojo   { background:#8b1a1a; border-bottom-color:#4a0a0a; }
    .btn.rojo:hover { background:#cc3333; }
    .btn.morado { background:#6a2a8a; border-bottom-color:#3a1a4a; }
    .btn.morado:hover { background:#9955cc; }
    input[type=text],input[type=password],input[type=file] {
      width:100%; padding:0.6rem 0.8rem; font-family:'Minecraft',monospace;
      font-size:0.95rem; background:#1a1108; color:white;
      border:2px solid #555; outline:none;
    }
    input:focus { border-color:#00ff99; }
    label { color:#ffff55; font-size:0.9rem; }
    .error { color:#ff5555; background:#2a1010; border:1px solid #ff5555; padding:0.7rem; font-size:0.9rem; }
    .ok    { color:#55ff55; background:#102a10; border:1px solid #55ff55; padding:0.7rem; font-size:0.9rem; }
    table  { width:100%; border-collapse:collapse; }
    th { background:#3a3128; padding:0.6rem; text-align:left; color:#aaaaaa; font-size:0.85rem; font-weight:normal; }
    td { padding:0.6rem; border-bottom:1px solid #3a3128; color:#00ff99; font-size:0.95rem; }
    .personaje-img { width:180px; height:180px; image-rendering:pixelated; display:block; margin:1rem auto; }
    .lb-linea { padding:0.4rem 0.2rem; border-bottom:1px solid #3a3128; font-size:0.85rem; color:#cccccc; word-break:break-all; }
    .sesion-tag { color:#aaffaa; font-size:0.85rem; margin-top:0.5rem; }
    .sep { border:none; border-top:1px solid #3a3128; margin:0.3rem 0; }
  </style>
</head>
<body>
  <h1>⚔ Minecraft: Jump Edition</h1>
  BLOQUE_CONTENIDO
</body>
</html>"""

def render(contenido, **kwargs):
    from jinja2 import Environment
    html = BASE.replace("BLOQUE_CONTENIDO", contenido)
    return render_template_string(html, **kwargs)

# ══════════════════════════════════════════════════════════════════════════════
# RUTAS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def inicio():
    return render("""
  {% if autenticado %}<p class="sesion-tag">Conectado como: {{ usuario }}</p>{% endif %}
  <div class="panel">
    <h2>Menú principal</h2>
    {% if autenticado %}
      <a class="btn" href="/usuario">Menú usuario</a>
      <a class="btn rojo" href="/logout">Cerrar sesión</a>
    {% else %}
      <a class="btn" href="/login">Iniciar sesión</a>
      <a class="btn gris" href="/invitado">Continuar como invitado</a>
    {% endif %}
    <hr class="sep">
    <a class="btn gris" href="/analizar">Analizar salto (local)</a>
  </div>
""", autenticado=session.get("autenticado", False), usuario=session.get("usuario", ""))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("autenticado"):
        return redirect(url_for("usuario"))
    error = None
    if request.method == "POST":
        u = request.form.get("usuario", "").strip()
        p = request.form.get("password", "").strip()
        if not u or not p:
            error = "Introduce usuario y contraseña."
        else:
            ok, msg = red_login(u, p)
            if ok:
                session["autenticado"] = True
                session["usuario"]     = u
                session["password"]    = p
                return redirect(url_for("usuario"))
            else:
                error = msg
    return render("""
  <div class="panel">
    <h2>Iniciar sesión</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <label>Usuario</label>
      <input type="text" name="usuario" required>
      <label>Contraseña</label>
      <input type="password" name="password" required>
      <button class="btn" type="submit">Entrar</button>
    </form>
    <a class="btn gris" href="/">Volver</a>
  </div>
""", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


@app.route("/usuario")
def usuario():
    if not session.get("autenticado"):
        return redirect(url_for("login"))
    return render("""
  <div class="panel">
    <h2>Bienvenido, {{ usuario }}</h2>
    <a class="btn" href="/enviar">Subir salto al servidor</a>
    <a class="btn gris" href="/leaderboard/hombres">Ranking masculino</a>
    <a class="btn gris" href="/leaderboard/mujeres">Ranking femenino</a>
    <hr class="sep">
    <a class="btn gris" href="/analizar">Analizar salto (local)</a>
    <a class="btn rojo" href="/logout">Cerrar sesión</a>
  </div>
""", usuario=session["usuario"])


@app.route("/invitado")
def invitado():
    return render("""
  <div class="panel">
    <h2>Modo invitado</h2>
    <p>Sin conexión. Los resultados no se guardarán.</p>
    <a class="btn" href="/analizar">Analizar salto</a>
    <a class="btn gris" href="/leaderboard/hombres">Ranking masculino</a>
    <a class="btn gris" href="/leaderboard/mujeres">Ranking femenino</a>
    <hr class="sep">
    <a class="btn gris" href="/">Volver</a>
  </div>
""")


@app.route("/analizar", methods=["GET", "POST"])
def analizar():
    if request.method == "POST":
        fichero = request.files.get("fichero")
        if not fichero or fichero.filename == "":
            return render("""
  <div class="panel">
    <h2>Analizar salto</h2>
    <div class="error">No seleccionaste ningún fichero.</div>
    <form method="POST" enctype="multipart/form-data">
      <label>Fichero de datos (.xlsx)</label>
      <input type="file" name="fichero" accept=".xlsx" required>
      <button class="btn" type="submit">Analizar</button>
    </form>
    <a class="btn gris" href="/">Volver</a>
  </div>
""")
        if not fichero.filename.endswith(".xlsx"):
            return render("""
  <div class="panel">
    <h2>Analizar salto</h2>
    <div class="error">El fichero debe ser .xlsx</div>
    <form method="POST" enctype="multipart/form-data">
      <label>Fichero de datos (.xlsx)</label>
      <input type="file" name="fichero" accept=".xlsx" required>
      <button class="btn" type="submit">Analizar</button>
    </form>
    <a class="btn gris" href="/">Volver</a>
  </div>
""")
        ruta_tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                fichero.save(tmp.name)
                ruta_tmp = tmp.name
            resultados, h1, error = analizar_fichero(ruta_tmp)
        finally:
            if ruta_tmp and os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)

        if error:
            return render("""
  <div class="panel">
    <h2>Analizar salto</h2>
    <div class="error">Error al analizar: {{ error }}</div>
    <a class="btn gris" href="/analizar">Volver</a>
  </div>
""", error=error)

        session["h1"] = h1
        return render("""
  <div class="panel">
    <h2>Resultados del análisis</h2>
    <table>
      <tr><th>Magnitud</th><th>Valor</th></tr>
      {% for clave, valor in resultados.items() %}
      <tr>
        <td>{{ clave.replace("_"," ").capitalize() }}</td>
        <td>{{ valor }}</td>
      </tr>
      {% endfor %}
    </table>
    <hr class="sep">
    <a class="btn morado" href="/personaje">Ver mi personaje</a>
    <a class="btn gris"   href="/analizar">Analizar otro salto</a>
    <a class="btn gris"   href="/">Volver al menú</a>
  </div>
""", resultados=resultados)

    return render("""
  <div class="panel">
    <h2>Analizar salto</h2>
    <form method="POST" enctype="multipart/form-data">
      <label>Fichero de datos (.xlsx)</label>
      <input type="file" name="fichero" accept=".xlsx" required>
      <button class="btn" type="submit">Analizar</button>
    </form>
    <a class="btn gris" href="/">Volver</a>
  </div>
""")


@app.route("/personaje")
def personaje():
    h1 = session.get("h1")
    if h1 is None:
        return redirect(url_for("analizar"))
    nombre, img, color, desc = asignar_personaje(h1)
    return render("""
  <div class="panel" style="text-align:center;">
    <h2>Tu personaje</h2>
    <p style="color:#ffff55;">Altura de vuelo: {{ cm }} cm</p>
    <img class="personaje-img" src="/imagen/{{ img }}" alt="{{ nombre }}">
    <h2 style="color:{{ color }};font-size:1.8rem;">{{ nombre }}</h2>
    <p style="color:#dddddd;">{{ descripcion }}</p>
    <hr class="sep">
    <div style="font-size:0.8rem;color:#888;margin:0.3rem 0;">
      Slime ≤15 · Lobo ≤30 · Creeper ≤45 · Enderman ≤59 · Dragon 60+
    </div>
    <a class="btn gris" href="/analizar">Analizar otro salto</a>
    <a class="btn gris" href="/">Volver al menú</a>
  </div>
""", cm=round(h1 * 100, 1), nombre=nombre, img=img, color=color, descripcion=desc)


@app.route("/enviar", methods=["GET", "POST"])
def enviar():
    if not session.get("autenticado"):
        return redirect(url_for("login"))

    FORM = """
  <div class="panel">
    <h2>Enviar salto al servidor</h2>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    {% if ok    %}<div class="ok">{{ ok }}</div>{% endif %}
    <form method="POST" enctype="multipart/form-data">
      <label>Grupo ProMu (ej: A2-4)</label>
      <input type="text" name="grupo" required>
      <label>Fichero de datos (.xlsx)</label>
      <input type="file" name="fichero" accept=".xlsx" required>
      <button class="btn" type="submit">Analizar y enviar</button>
    </form>
    <a class="btn gris" href="/usuario">Volver</a>
  </div>
"""
    if request.method == "POST":
        grupo   = request.form.get("grupo", "").strip()
        fichero = request.files.get("fichero")
        if not grupo:
            return render(FORM, error="Introduce el grupo.", ok=None)
        if not fichero or not fichero.filename.endswith(".xlsx"):
            return render(FORM, error="Selecciona un fichero .xlsx.", ok=None)

        ruta_tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
                fichero.save(tmp.name)
                ruta_tmp = tmp.name
            _, h1, error = analizar_fichero(ruta_tmp)
        finally:
            if ruta_tmp and os.path.exists(ruta_tmp):
                os.remove(ruta_tmp)

        if error:
            return render(FORM, error=f"Error al analizar: {error}", ok=None)

        altura_mm = int(h1 * 1000)
        resp = red_enviar_salto(session["usuario"], session["password"], grupo, altura_mm)
        return render(FORM, ok=f"Servidor: {resp}", error=None)

    return render(FORM, error=None, ok=None)


@app.route("/leaderboard/<tipo>")
def leaderboard(tipo):
    if tipo == "hombres":
        comando = "GET_LEADERBOARD_MEN"
        titulo  = "Ranking Masculino"
    else:
        comando = "GET_LEADERBOARD_WOMEN"
        titulo  = "Ranking Femenino"
    lineas = red_leaderboard(comando)
    return render("""
  <div class="panel">
    <h2>🏆 {{ titulo }}</h2>
    <div style="max-height:400px;overflow-y:auto;">
      {% for linea in lineas %}
      <div class="lb-linea">{{ linea }}</div>
      {% endfor %}
    </div>
    <hr class="sep">
    <a class="btn gris" href="/">Volver al menú</a>
  </div>
""", titulo=titulo, lineas=lineas)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)