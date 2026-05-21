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
estados = {
    "_reproductor": None,
    "_volumen_actual":  50,
    "_cola": [],
    "_base":  None  # carpeta donde están los mp3
}
def inicializar_audio():
    pass

def check_estado(dt):
    if estados["_reproductor"].playing:
        _siguiente_cancion()




def _construir_cola():
    """Genera una cola aleatoria con todas las canciones."""
    mezcladas = _canciones[:]
    random.shuffle(mezcladas)
    estados["_cola"] = [os.path.join(estados["_base"], nombre) for nombre in mezcladas]

def _siguiente_cancion():
    """Carga y reproduce la siguiente canción de la cola."""
    if not estados["_cola"]:
        _construir_cola()
    ruta_cancion = estados["_cola"].pop(0)
    origen = pyglet.media.load(ruta_cancion, streaming=False)
    estados["_reproductor"] = pyglet.media.Player()
    estados["_reproductor"].volume = estados["_volumen_actual"] / 100
    estados["_reproductor"].queue(origen)
    estados["_reproductor"].push_handlers(on_player_eos=_siguiente_cancion)
    estados["_reproductor"].play()

def cargar_musica(base):
    """
    Valida que existan todos los archivos en la carpeta indicada.
    """
    estados["_base"] = base
    for nombre in _canciones:
        ruta_cancion = os.path.join(base, nombre)
        if not os.path.exists(ruta_cancion):
            raise FileNotFoundError(f"No se encontró: {ruta_cancion}")

def reproducir_musica(base=None):
    """Construye la cola y empieza la reproducción."""
    if base is not None:
        estados["_base"] = base
    _construir_cola()
    _siguiente_cancion()

def detener_musica():
    
    if estados["_reproductor"] is not None:
        estados["_reproductor"].pause()

def ajustar_volumen(porcentaje_volumen):
    if not (0 <= porcentaje_volumen <= 100):
        raise ValueError(f"El volumen debe estar entre 0 y 100, recibido: {porcentaje_volumen}")
    estados["_volumen_actual"] = porcentaje_volumen
    if estados["_reproductor"] is not None:
        estados["_reproductor"].volume = porcentaje_volumen / 100

def obtener_volumen():
    if estados["_reproductor"] is not None:
        return int(estados["_reproductor"].volume * 100)
    return estados["_volumen_actual"]

pyglet.clock.schedule_interval(check_estado, 1)