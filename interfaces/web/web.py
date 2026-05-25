#!/usr/bin/env python3
"""
Web interface for PROMU - Minecraft: Jump Edition
Flask web application with file analysis, graphs, login and leaderboard.
"""

import sys, os, io, json, uuid, threading, base64, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from flask import (
    Flask, request, render_template_string, session,
    redirect, url_for, jsonify, send_file
)

from core.matemáticas import (
    Mat_obj1_AD, Mat_obj2_FM, Mat_obj3_Sua, Mat_obj4_FR,
    Mat_obj5_GR, Mat_obj6_Integra, Mat_obj7_Puntos, Mat_obj8_Altura
)
from core.formatter import format_height, format_results
from servidor import red
import socket

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = os.path.join(tempfile.mkdtemp(prefix='promu_web_'), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BBASEI = os.path.join(os.path.dirname(__file__), '..', '..', 'archivos_interfaz', 'imagenes')

def asignar_personaje(altura_m):
    cm = altura_m * 100
    if cm <= 15:
        return ('Slime', 'slime.png', '#55ff55',
                'Pequeño pero pegajoso. ¡Sigue saltando!', 0)
    elif cm <= 30:
        return ('Lobo', 'lobo.png', '#aaaaff',
                'Fiel y persistente. ¡Buen salto!', 1)
    elif cm <= 45:
        return ('Creeper', 'creeper.png', '#44cc44',
                'Explosivo en la pista. ¡Muy bien!', 2)
    elif cm <= 59:
        return ('Enderman', 'enderman.png', '#cc88ff',
                'Largo y veloz. ¡Impresionante!', 3)
    else:
        return ('Ender Dragon', 'ender_dragon.png', '#aa00ff',
                'El jefe definitivo. ¡Eres una leyenda!', 4)

def generar_graficas(path, peso_kg):
    t, ace_y, ace = Mat_obj1_AD(path)
    FM = Mat_obj2_FM(t)
    ace_real = ace * np.sign(ace_y)
    sua_ace = Mat_obj3_Sua(ace_real, FM)
    g_media = Mat_obj5_GR(ace_real, FM)
    ace_neta = sua_ace - g_media
    velocidad = Mat_obj6_Integra(ace_neta, t, 0)
    desplazamiento = Mat_obj6_Integra(velocidad, t, 0)
    fuerza = peso_kg * ace_real
    potencia = fuerza * velocidad
    masa_aparente = fuerza / 9.81

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.patch.set_facecolor('#1a1108')
    fig.suptitle("Análisis del Salto", fontsize=18, fontweight='bold', color='white')

    graficas = [
        (ace_real, "Aceleración", "m/s²"),
        (velocidad, "Velocidad", "m/s"),
        (desplazamiento, "Desplazamiento", "m"),
        (fuerza, "Fuerza", "N"),
        (potencia, "Potencia", "W"),
        (masa_aparente, "Masa", "kg"),
    ]
    colores = ['#00ff99', '#ff6666', '#6699ff', '#ffcc00', '#ff99cc', '#99ffff']

    for ax, (y, titulo, unidad), color in zip(axes.flatten(), graficas, colores):
        ax.set_facecolor('#2a2118')
        ax.plot(t, y, color=color, linewidth=1.5)
        ax.set_title(titulo, color='white', fontsize=13, fontweight='bold')
        ax.set_xlabel("Tiempo (s)", color='#aaaaaa', fontsize=10)
        ax.set_ylabel(f"{titulo} ({unidad})", color='#aaaaaa', fontsize=10)
        ax.tick_params(colors='#aaaaaa')
        for spine in ax.spines.values():
            spine.set_color('#555555')
        ax.grid(True, color='#333333', linestyle='--', alpha=0.7)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

def abrir_socket_anonimo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((red.IP_SERVIDOR, red.SERVER_PORT))
    sock.send(f"HELLO {socket.gethostbyname(socket.gethostname())}\r\n".encode())
    _recibir_linea(sock)
    return sock

def _recibir_linea(sock):
    data = b""
    while not data.endswith(b"\r\n"):
        chunk = sock.recv(1)
        if not chunk:
            raise RuntimeError("Conexión cerrada por el servidor.")
        data += chunk
        if len(data) > 4096:
            raise RuntimeError("Respuesta del servidor demasiado larga.")
    return data.decode("utf-8", errors="replace")

def autenticar_sync(usuario, password):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60)
        sock.connect((red.IP_SERVIDOR, red.SERVER_PORT))
        sock.settimeout(10)
        host = socket.gethostbyname(socket.gethostname())
        sock.send(f"HELLO {host}\r\n".encode())
        resp = _recibir_linea(sock)
        if not resp.startswith("200"):
            sock.close()
            return False, f"Error HELLO: {resp.strip()}"
        sock.send(f"USER {usuario}\r\n".encode())
        resp = _recibir_linea(sock)
        if not resp.startswith("200"):
            sock.close()
            return False, f"Error USER: {resp.strip()}"
        sock.send(f"PASS {password}\r\n".encode())
        resp = _recibir_linea(sock)
        if not resp.startswith("200"):
            sock.close()
            return False, f"Credenciales incorrectas: {resp.strip()}"
        return True, sock
    except socket.timeout:
        return False, "Tiempo de conexión agotado."
    except Exception as e:
        return False, str(e)

def leaderboard_sync(comando):
    try:
        sock_sesion = red.sesion["socket"]
        if sock_sesion:
            sock_sesion.send(f"{comando}\r\n".encode())
            return _recibir_leaderboard(sock_sesion)
        else:
            sock = abrir_socket_anonimo()
            sock.send(f"{comando}\r\n".encode())
            lineas = _recibir_leaderboard(sock)
            sock.close()
            return lineas
    except Exception as e:
        return [f"ERROR: {e}"]

def _recibir_leaderboard(sock):
    marcadores = ("202 NO HAY MAS REGISTROS", "202 NO HAY MÁS REGISTROS",
                  "201 NO HAY REGISTROS TODAVIA")
    lineas = []
    while True:
        linea = _recibir_linea(sock).strip()
        lineas.append(linea)
        if any(m in linea for m in marcadores):
            break
    return lineas

def _render(template, **context):
    content = render_template_string(template, **context)
    return render_template_string(
        BASE_HTML, content=content, usuario=session.get('usuario'))

BASE_HTML = '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>PROMU - Minecraft: Jump Edition</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f0f0f; color: #e0e0e0; min-height: 100vh;
    padding-bottom: env(safe-area-inset-bottom);
}
.container { max-width: 1000px; margin: 0 auto; padding: 16px; }
header {
    background: linear-gradient(135deg, #1a1108, #2a1f0f);
    padding: 16px 0; border-bottom: 2px solid #44cc44; margin-bottom: 20px;
}
header .container { display: flex; justify-content: space-between; align-items: center; padding: 0 16px; }
header h1 { color: #44cc44; font-size: 1.3em; }
header nav a {
    color: #aaaaaa; text-decoration: none; margin-left: 15px; font-size: 0.85em;
}
header nav a:hover { color: #44cc44; }
.card {
    background: #1a1a1a; border: 1px solid #333; border-radius: 12px;
    padding: 20px; margin-bottom: 20px;
}
.card h2 { color: #44cc44; margin-bottom: 16px; font-size: 1.2em; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 6px; color: #aaaaaa; font-size: 0.85em; }
.form-group input[type="file"],
.form-group input[type="number"],
.form-group input[type="text"],
.form-group input[type="password"] {
    width: 100%; padding: 12px 14px; background: #0f0f0f; border: 1px solid #444;
    border-radius: 8px; color: #e0e0e0; font-size: 1em;
}
.form-group input:focus { outline: none; border-color: #44cc44; }
.btn {
    display: inline-block; padding: 14px 28px; border: none; border-radius: 8px;
    font-size: 1em; font-weight: 600; cursor: pointer; text-decoration: none;
    text-align: center; width: 100%; margin-bottom: 8px;
}
.btn-primary { background: #44cc44; color: #0f0f0f; }
.btn-secondary { background: #333; color: #e0e0e0; }
.btn-danger { background: #cc4444; color: white; }
.alert {
    padding: 12px 14px; border-radius: 8px; margin-bottom: 16px; font-size: 0.9em;
}
.alert-error { background: #442222; border: 1px solid #cc4444; color: #ff6666; }
.alert-success { background: #224422; border: 1px solid #44cc44; color: #66ff66; }
.results-grid {
    display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;
    margin-bottom: 20px;
}
.result-item {
    background: #0f0f0f; border: 1px solid #333; border-radius: 8px;
    padding: 12px; text-align: center;
}
.result-item .label { color: #888; font-size: 0.75em; text-transform: uppercase; }
.result-item .value { color: #44cc44; font-size: 1.3em; font-weight: bold; margin-top: 4px; }
.character-display { text-align: center; padding: 16px; }
.character-display img { width: 150px; height: 150px; image-rendering: pixelated; margin: 12px 0; }
.character-display h3 { font-size: 1.6em; margin: 8px 0; }
.character-display p { color: #aaaaaa; font-size: 1em; }
.actions { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }
.leaderboard-table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
.leaderboard-table th,
.leaderboard-table td { padding: 8px 10px; text-align: left; border-bottom: 1px solid #333; }
.leaderboard-table th { color: #888; font-size: 0.75em; text-transform: uppercase; }
.leaderboard-table tr:hover { background: #1f1f1f; }
.rank-1 { color: #ffd700; } .rank-2 { color: #c0c0c0; } .rank-3 { color: #cd7f32; }
.level-bar { width: 100%; height: 16px; background: #0f0f0f; border-radius: 8px;
    overflow: hidden; margin: 12px 0; display: flex; gap: 3px; padding: 2px; }
.level-bar .segment { height: 100%; flex: 1; border-radius: 6px;
    background: #2a2118; }
.level-bar .segment.filled { background: var(--seg-color); }
</style>
</head>
<body>
<header>
<div class="container">
<h1>PROMU</h1>
<nav>
{% if usuario %}
<a href="{{ url_for('usuario') }}">{{ usuario }}</a>
<a href="{{ url_for('logout') }}">Salir</a>
{% else %}
<a href="{{ url_for('login') }}">Login</a>
{% endif %}
</nav>
</div>
</header>
<div class="container">
{{ content|safe }}
</div>
</body>
</html>'''

INDEX_HTML = '''
<div class="card">
<h2>Analizar salto</h2>
{% if error %}
<div class="alert alert-error">{{ error }}</div>
{% endif %}
{% if success %}
<div class="alert alert-success">{{ success }}</div>
{% endif %}
<form method="post" enctype="multipart/form-data">
<div class="form-group">
<label for="file">Archivo Excel (.xlsx)</label>
<input type="file" name="file" accept=".xlsx" required>
</div>
<div class="form-group">
<label for="peso">Peso (kg)</label>
<input type="number" name="peso" step="0.1" min="1" max="500" placeholder="Ej: 70" required>
</div>
<button type="submit" class="btn btn-primary">Analizar salto</button>
</form>
</div>

{% if resultados %}
<div class="card">
<h2>Resultados</h2>
<div class="results-grid">
<div class="result-item">
<div class="label">h1 (vuelo)</div>
<div class="value">{{ resultados.h1 }}</div>
</div>
<div class="result-item">
<div class="label">h2 (despegue)</div>
<div class="value">{{ resultados.h2 }}</div>
</div>
<div class="result-item">
<div class="label">h3 (desplaz.)</div>
<div class="value">{{ resultados.h3 }}</div>
</div>
<div class="result-item">
<div class="label">Velocidad</div>
<div class="value">{{ resultados.v_despegue }}</div>
</div>
<div class="result-item">
<div class="label">Tiempo vuelo</div>
<div class="value">{{ resultados.t_vuelo }}</div>
</div>
</div>

<div class="character-display">
<h3 style="color: {{ personaje.2 }}">{{ personaje.0 }}</h3>
<img src="{{ url_for('static_image', filename=personaje.1) }}" alt="{{ personaje.0 }}">
<p>{{ personaje.3 }}</p>
<div class="level-bar">
{% for i in range(5) %}
<div class="segment{% if i <= personaje.4 %} filled{% endif %}"
     style="--seg-color: {{ personaje.2 }}"></div>
{% endfor %}
</div>
<p style="color: #888; font-size: 0.8em;">{{ "%.1f"|format(resultados.h1_val * 100) }} cm &mdash; {{ ((resultados.h1_val * 100) / 80 * 100)|int }}% del máximo</p>
</div>

<div class="actions">
<a href="{{ url_for('graficas') }}" class="btn btn-primary" target="_blank">Ver gráficas</a>
{% if usuario %}
<a href="{{ url_for('enviar') }}" class="btn btn-secondary">Enviar salto</a>
{% endif %}
<a href="{{ url_for('index') }}" class="btn btn-secondary">Nuevo análisis</a>
</div>
</div>
{% endif %}
'''

LOGIN_HTML = '''
<div class="card" style="max-width: 400px; margin: 0 auto;">
<h2>Iniciar sesión</h2>
{% if error %}
<div class="alert alert-error">{{ error }}</div>
{% endif %}
<form method="post">
<div class="form-group">
<label for="usuario">Usuario</label>
<input type="text" name="usuario" required>
</div>
<div class="form-group">
<label for="password">Contraseña</label>
<input type="password" name="password" required>
</div>
<button type="submit" class="btn btn-primary">Conectar</button>
</form>
<div class="actions" style="margin-top: 16px;">
<a href="{{ url_for('index') }}" class="btn btn-secondary">Volver</a>
</div>
</div>
'''

USUARIO_HTML = '''
<div class="card">
<h2>Bienvenido, {{ usuario }}</h2>
<p style="color: #888; margin-bottom: 16px;">Sesión iniciada en el servidor PROMU.</p>
<div class="actions">
<a href="{{ url_for('index') }}" class="btn btn-primary">Analizar salto</a>
<a href="{{ url_for('leaderboard') }}" class="btn btn-secondary">Ranking masculino</a>
<a href="{{ url_for('leaderboard_femenino') }}" class="btn btn-secondary">Ranking femenino</a>
<a href="{{ url_for('logout') }}" class="btn btn-danger">Cerrar sesión</a>
</div>
</div>
'''

LEADERBOARD_HTML = '''
<div class="card">
<h2>{{ titulo }}</h2>
{% if lineas %}
<table class="leaderboard-table">
<thead>
<tr><th>#</th><th>Jugador</th><th>Grupo</th><th>Altura</th><th>Fecha</th></tr>
</thead>
<tbody>
{% for entry in lineas %}
<tr>
<td class="rank-{{ entry.rank if entry.rank <= 3 else '' }}">{{ entry.rank }}</td>
<td>{{ entry.nombre }}</td>
<td>{{ entry.grupo }}</td>
<td>{{ entry.altura_cm }}</td>
<td>{{ entry.fecha }}</td>
</tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p style="color: #888; text-align: center; padding: 20px;">No hay registros disponibles.</p>
{% endif %}
<div class="actions">
<a href="{{ url_for('usuario') }}" class="btn btn-secondary">Volver</a>
</div>
</div>
'''

ENVIAR_HTML = '''
<div class="card">
<h2>Enviar salto</h2>
{% if error %}
<div class="alert alert-error">{{ error }}</div>
{% endif %}
{% if success %}
<div class="alert alert-success">{{ success }}</div>
{% endif %}
<form method="post" enctype="multipart/form-data">
<div class="form-group">
<label for="grupo">Grupo (ej: A2-4)</label>
<input type="text" name="grupo" placeholder="Ej: A2-4" required>
</div>
<div class="form-group">
<label for="file">Archivo Excel (.xlsx)</label>
<input type="file" name="file" accept=".xlsx" required>
</div>
<div class="form-group">
<label for="peso">Peso (kg)</label>
<input type="number" name="peso" step="0.1" min="1" max="500" required>
</div>
<button type="submit" class="btn btn-primary">Analizar y enviar</button>
</form>
<div class="actions">
<a href="{{ url_for('usuario') }}" class="btn btn-secondary">Volver</a>
</div>
</div>
'''

@app.route('/')
def index():
    return _render(
        INDEX_HTML,
        resultados=session.pop('resultados', None),
        personaje=session.pop('personaje', None),
        error=session.pop('error', None),
        success=session.pop('success', None),
    )

@app.route('/', methods=['POST'])
def analizar():
    if 'file' not in request.files:
        session['error'] = 'No se ha seleccionado ningún archivo.'
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        session['error'] = 'No se ha seleccionado ningún archivo.'
        return redirect(url_for('index'))
    peso = request.form.get('peso', type=float)
    if not peso:
        session['error'] = 'Debes introducir un peso válido.'
        return redirect(url_for('index'))

    tmp_path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4().hex}.xlsx')
    file.save(tmp_path)

    try:
        t, ace_y, ace = Mat_obj1_AD(tmp_path)
        h1, h2, h3 = Mat_obj8_Altura(ace, ace_y, t)
        FM = Mat_obj2_FM(t)
        ace_real = ace * np.sign(ace_y)
        ace_suav = Mat_obj3_Sua(ace_real, FM)
        g_media = Mat_obj5_GR(ace_real, FM)
        ace_neta = ace_suav - g_media
        velocidad = Mat_obj6_Integra(ace_neta, t, 0)
        idx_T0, idx_L, t_aire, _ = Mat_obj7_Puntos(ace, ace_y, t)
        v_despegue = velocidad[idx_T0]

        session['resultados'] = {
            'h1': format_height(h1),
            'h2': format_height(h2),
            'h3': format_height(h3),
            'v_despegue': f'{v_despegue:.2f} m/s',
            't_vuelo': f'{t_aire:.3f} s',
            'h1_val': h1,
            'peso': peso,
        }
        session['personaje'] = asignar_personaje(h1)
        session['graficas_path'] = tmp_path
        session['graficas_peso'] = peso
        session['success'] = 'Análisis completado con éxito.'
    except Exception as e:
        session['error'] = f'Error: {str(e)}'
        try: os.remove(tmp_path)
        except: pass

    return redirect(url_for('index'))

@app.route('/graficas')
def graficas():
    path = session.get('graficas_path')
    peso = session.get('graficas_peso')
    if not path or not os.path.exists(path) or not peso:
        session['error'] = 'No hay gráficas. Analiza un salto primero.'
        return redirect(url_for('index'))
    try:
        buf = generar_graficas(path, peso)
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        session['error'] = f'Error: {str(e)}'
        return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    ruta = os.path.join(BBASEI, 'slime.png')
    if os.path.exists(ruta):
        return send_file(ruta, mimetype='image/png')
    return ('', 204)

@app.route('/static_imagenes/<filename>')
def static_image(filename):
    return send_file(os.path.join(BBASEI, filename), mimetype='image/png')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return _render(LOGIN_HTML, error=session.pop('error', None))
    usuario = request.form.get('usuario', '').strip()
    password = request.form.get('password', '').strip()
    if not usuario or not password:
        return _render(LOGIN_HTML, error='Completa todos los campos.')
    ok, resultado = autenticar_sync(usuario, password)
    if ok:
        session['usuario'] = usuario
        red.sesion["socket"] = resultado
        red.sesion["autenticado"] = True
        red.sesion["usuario"] = usuario
        return redirect(url_for('usuario'))
    return _render(LOGIN_HTML, error=resultado)

@app.route('/usuario')
def usuario():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return _render(USUARIO_HTML, usuario=session['usuario'])

@app.route('/logout')
def logout():
    try: red.cerrar_sesion()
    except: pass
    session.clear()
    return redirect(url_for('index'))

@app.route('/leaderboard')
def leaderboard():
    return _mostrar_leaderboard('GET_LEADERBOARD_MEN', 'Ranking Masculino')

@app.route('/leaderboard/femenino')
def leaderboard_femenino():
    return _mostrar_leaderboard('GET_LEADERBOARD_WOMEN', 'Ranking Femenino')

def _mostrar_leaderboard(comando, titulo):
    lineas_raw = leaderboard_sync(comando)
    entradas = []
    for linea in lineas_raw:
        if linea.startswith('2') or linea.startswith('1'):
            continue
        try:
            datos = json.loads(linea)
            altura_cm = datos.get('altura', 0) / 10
            entradas.append({
                'rank': len(entradas) + 1,
                'nombre': datos.get('nombre', '—'),
                'grupo': datos.get('grupo_ProMu', '—'),
                'altura_cm': f'{altura_cm:.1f} cm',
                'fecha': datos.get('fecha', '—'),
            })
        except: continue
    return _render(LEADERBOARD_HTML, titulo=titulo, lineas=entradas)

@app.route('/enviar', methods=['GET', 'POST'])
def enviar():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    if request.method == 'GET':
        return _render(ENVIAR_HTML, error=session.pop('error', None), success=session.pop('success', None))
    grupo = request.form.get('grupo', '').strip()
    if not grupo:
        return _render(ENVIAR_HTML, error='El grupo es obligatorio.', success=None)
    if 'file' not in request.files:
        return _render(ENVIAR_HTML, error='Selecciona un archivo.', success=None)
    file = request.files['file']
    peso = request.form.get('peso', type=float)
    if not peso:
        return _render(ENVIAR_HTML, error='Peso válido requerido.', success=None)
    tmp_path = os.path.join(UPLOAD_FOLDER, f'{uuid.uuid4().hex}.xlsx')
    file.save(tmp_path)
    try:
        t, ace_y, ace = Mat_obj1_AD(tmp_path)
        h1, h2, h3 = Mat_obj8_Altura(ace, ace_y, t)
        altura_mm = int(h1 * 1000)
        ok, respuesta = _enviar_salto_sync(grupo, altura_mm)
        if ok:
            session['success'] = f'Salto enviado. Altura: {h1*100:.1f} cm'
        else:
            session['error'] = f'Error: {respuesta}'
    except Exception as e:
        session['error'] = f'Error: {str(e)}'
    finally:
        try: os.remove(tmp_path)
        except: pass
    return redirect(url_for('enviar'))

def _enviar_salto_sync(grupo, altura_mm):
    try:
        sock = red.sesion["socket"]
        if not sock:
            return False, "No hay sesión activa."
        data = {"grupo_ProMu": grupo, "altura": altura_mm}
        sock.send(f"SEND_DATA {json.dumps(data)}\r\n".encode())
        resp = _recibir_linea(sock)
        return resp.startswith("200"), resp.strip()
    except Exception as e:
        return False, str(e)

def main():
    print(f"Servidor PROMU corriendo en http://0.0.0.0:5000")
    print(f"Accede desde el móvil con http://TU_IP:5000")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    main()
