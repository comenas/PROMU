import pyglet

_musica = None  # referencia global al reproductor

def inicializar_audio():
    """
    Con pyglet no hace falta inicialización explícita.
    Se mantiene la función para no cambiar el resto del código.
    """
    pass

def cargar_musica(ruta):
    """
    Carga un archivo de música. Acepta .mp3, .ogg o .wav.
    Lanza FileNotFoundError si el fichero no existe.
    """
    import os
    global _musica
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el fichero de música: {ruta}")
    origen = pyglet.media.load(ruta)
    _musica = pyglet.media.Player()
    _musica.queue(origen)

def reproducir_musica(repeticiones=-1):
    """
    Reproduce la música cargada en bucle infinito.
    """
    global _musica
    if _musica is None:
        raise RuntimeError("No hay música cargada. Llama primero a cargar_musica().")
    _musica.loop = True
    _musica.play()

def detener_musica():
    """
    Detiene la música.
    """
    global _musica
    if _musica is not None:
        _musica.pause()

def ajustar_volumen(porcentaje_volumen):
    """
    Ajusta el volumen. Recibe un valor entre 0 y 100 y lo convierte a escala 0.0-1.0.
    """
    global _musica
    if not (0 <= porcentaje_volumen <= 100):
        raise ValueError(f"El volumen debe estar entre 0 y 100, recibido: {porcentaje_volumen}")
    if _musica is not None:
        _musica.volume = porcentaje_volumen / 100

def obtener_volumen():
    """
    Devuelve el volumen actual como porcentaje (0-100).
    """
    global _musica
    if _musica is not None:
        return int(_musica.volume * 100)
    return 50  # valor por defecto si no hay música cargada