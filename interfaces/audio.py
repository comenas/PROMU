import pyglet
import os
import random

# ── Lista de canciones ─────────────────────────────────────────────────────────
_canciones = [
    "aria math.mp3",
    "wet hands.mp3",
    "minecraft.mp3",
    "haggstrom.mp3",
    "blind spots.mp3",
]

_reproductor = None
_volumen_actual = 50
_cola = []
_base = None  # carpeta donde están los mp3

def inicializar_audio():
    pass

def _construir_cola():
    """Genera una cola aleatoria con todas las canciones."""
    global _cola
    mezcladas = _canciones[:]
    random.shuffle(mezcladas)
    _cola = [os.path.join(_base, nombre) for nombre in mezcladas]

def _siguiente_cancion():
    """Carga y reproduce la siguiente canción de la cola."""
    global _reproductor, _cola
    if not _cola:
        _construir_cola()
    ruta_cancion = _cola.pop(0)
    origen = pyglet.media.load(ruta_cancion, streaming=False)
    _reproductor = pyglet.media.Player()
    _reproductor.volume = _volumen_actual / 100
    _reproductor.queue(origen)
    _reproductor.push_handlers(on_player_eos=_siguiente_cancion)
    _reproductor.play()

def cargar_musica(base):
    """
    Valida que existan todos los archivos en la carpeta indicada.
    """
    global _base
    _base = base
    for nombre in _canciones:
        ruta_cancion = os.path.join(base, nombre)
        if not os.path.exists(ruta_cancion):
            raise FileNotFoundError(f"No se encontró: {ruta_cancion}")

def reproducir_musica(base=None):
    """Construye la cola y empieza la reproducción."""
    global _base
    if base is not None:
        _base = base
    _construir_cola()
    _siguiente_cancion()

def detener_musica():
    global _reproductor
    if _reproductor is not None:
        _reproductor.pause()

def ajustar_volumen(porcentaje_volumen):
    global _volumen_actual, _reproductor
    if not (0 <= porcentaje_volumen <= 100):
        raise ValueError(f"El volumen debe estar entre 0 y 100, recibido: {porcentaje_volumen}")
    _volumen_actual = porcentaje_volumen
    if _reproductor is not None:
        _reproductor.volume = porcentaje_volumen / 100

def obtener_volumen():
    if _reproductor is not None:
        return int(_reproductor.volume * 100)
    return _volumen_actual