import numpy as np
import pandas as pd
from core.data_loader import *
from scipy.signal import savgol_filter
from scipy.integrate import cumulative_trapezoid

def Mat_obj1_AD(path):
    """
    Carga el Excel y devuelve tiempo, ace_x, ace_y, ace_z y aceleracion absoluta.
    Si el Excel tiene columna de aceleración absoluta la usa; si no, la calcula.
    """
    validate_file_exists(path)
    validate_file_extension(path)
    archivo = read_excel_file(path)
    tiempo      = extract_column_as_float(archivo, 0)
    ace_x       = extract_column_as_float(archivo, 1)
    ace_y       = extract_column_as_float(archivo, 2)
    ace_z       = extract_column_as_float(archivo, 3)
    if len(archivo.columns) > 4:
        aceleracion = extract_column_as_float(archivo, 4)
    else:
        aceleracion = np.linalg.norm([ace_x, ace_y, ace_z], axis=0)
    return tiempo, ace_y, aceleracion

def Mat_obj2_FM(tiempo):
    """
    Calcula la frecuencia muestral FM = 1 / mean(diff(tiempo)).
    Necesita al menos 2 valores; si no, lanza ValueError.
    """
    if len(tiempo) < 2:
        raise ValueError("se necesitan al menos 2 valores en el array de tiempo")
    FM = 1 / np.mean(np.diff(tiempo))
    return FM

def Mat_obj3_Sua(valor, FM):
    """
    Suaviza la señal con Savitzky-Golay: ventana = 15% de FM (impar), grado 2.
    """
    ventana = int(0.15 * FM)
    if ventana % 2 == 0:
        ventana += 1
    return savgol_filter(valor, ventana, 2)

def Mat_obj4_FR(ace, FM):
    """
    Busca el fragmento de reposo en el primer segundo.
    Devuelve (idx_inicio, tam_ventana) de la ventana con menor desviación típica.
    """
    tam_ventana            = int(0.5 * FM)
    muestras_primer_segundo = int(FM)
    mejor_idx = 0
    mejor_std = np.inf
    for i in range(0, muestras_primer_segundo - tam_ventana):
        ventana = ace[i : i + tam_ventana]
        std = np.std(ventana)
        if std < mejor_std:
            mejor_std = std
            mejor_idx = i
    return mejor_idx, tam_ventana

def Mat_obj5_GR(ace, FM):
    """
    Calcula la gravedad media en el fragmento de reposo detectado por Mat_obj4_FR.
    """
    idx, tam_ventana = Mat_obj4_FR(ace, FM)
    valores = ace[idx : idx + tam_ventana]
    return np.mean(valores)

def Mat_obj6_Integra(var, t, y0):
    """
    Integración numérica acumulada por trapecios. Devuelve array de misma longitud que t.
    """
    int_array = cumulative_trapezoid(var, t, initial=0)
    int_array = int_array + y0
    return int_array

def Mat_obj7_Puntos(ace, ace_y, t):
    """
    Detecta los instantes clave del salto:
      idx_s  → inicio del impulso (primer cambio brusco en la derivada)
      idx_T0 → despegue (máximo de velocidad tras idx_s)
      idx_L  → aterrizaje (máximo de ace_neta tras idx_T0)
      t_aire → tiempo en el aire
    Devuelve también la velocidad para reutilizarla en Mat_obj8.
    """
    FM       = Mat_obj2_FM(t)
    ace_v    = ace * np.sign(ace_y)          # aceleración vertical con signo
    sua_ace  = Mat_obj3_Sua(ace_v, FM)
    g_media  = Mat_obj5_GR(ace_v, FM)
    ace_neta = sua_ace - g_media
    velocidad = Mat_obj6_Integra(ace_neta, t, 0)

    # ── idx_s: primer cambio brusco en la derivada, empezando en 0.2 s ──
    start_index = int(0.2 * FM)
    derivada    = np.gradient(ace_v)
    idx_s = 0
    for i in range(start_index, len(derivada)):
        if np.abs(derivada[i]) > 0.25:
            idx_s = i
            break

    # ── idx_T0: despegue = máximo de velocidad después de idx_s ──
    idx_T0 = np.argmax(velocidad[idx_s:]) + idx_s

    # ── idx_L: aterrizaje = máximo de ace_neta después de idx_T0 ──
    idx_L  = np.argmax(ace_neta[idx_T0:]) + idx_T0

    # ── t_aire: tiempo de vuelo ──
    t_aire = t[idx_L] - t[idx_T0]

    return idx_T0, idx_L, t_aire, velocidad

def Mat_obj8_Altura(ace, ace_y, t):
    """
    Calcula la altura del salto por los 3 métodos físicos.
    h1 → tiempo de vuelo:      h = g·TIA²/8
    h2 → velocidad de despegue: h = v²/(2g)
    h3 → desplazamiento:        max(disp[TO:L])
    """
    idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace, ace_y, t)
    desplazamiento = Mat_obj6_Integra(velocidad, t, 0)
    h1 = 9.81 * t_aire**2 / 8
    h2 = velocidad[idx_T0]**2 / (2 * 9.81)
    h3 = max(desplazamiento[idx_T0 : idx_L])
    return h1, h2, h3