import numpy as np
import pandas as pd
from data_loader import *
from scipy.signal import savgol_filter
from scipy.integrate import cumulative_trapezoid

def Mat_obj1_AD(path):
    """
    función que saca los datos del excel mediante las funciones del data_loader.py recive un fichero
    devuelve los valores de cada columna como los datos para hacer calculos
    """
    validate_file_exists(path) # primero valida que exista el fichero
    validate_file_extension(path) # luego valida que el fichero sea excel
    archivo = read_excel_file(path) # lee el archivo con pandas
    tiempo = extract_column_as_float(archivo, 0) # transforma cada columna a float con la funcion
    ace_x = extract_column_as_float(archivo, 1) # extract_column_as_float del data_loader
    ace_y = extract_column_as_float(archivo, 2) # cada columna es un dato 
    ace_z = extract_column_as_float(archivo, 3)
    if len(archivo.columns) > 4: # puede haber aceleración en el excel o necesitar calcularla
        aceleracion = extract_column_as_float(archivo, 4) # si está en el excel se coge de ahí
    else:
        aceleracion = np.linalg.norm([ace_x, ace_y, ace_z], axis=0) # si no está en el excel se calcula
    return tiempo,ace_x,ace_y,ace_z,aceleracion

def Mat_obj2_FM(tiempo):
    """
    función que saca la Frecuencia Muestral FM necesita al menos 2 valores de tiempo si no lanza error
    lo calcula mediante f = 1/T haciendo la media de T en los valores dados
    """
    if len(tiempo) < 2: #comprueba tener suficientes valores
        raise ValueError(f"se necesitan al menos 2 valores en el array de tiempo")
    else:
        FM = 1/np.mean(np.diff(tiempo)) # calcula la diferencia entre valores y hace la media 
        return FM #para sacar la frecuencia muestral

def Mat_obj3_Sua(ace, FM):
    """
    función que suaviza la señal mediante la aceleración y la frecuencia muestral 
    utiliza una función de scipy para suavizado
    """
    ventana = int(0.15 * FM) #calcula ventana 
    if ventana % 2 == 0: # debe ser impar por lo que si es par se suma 1
        ventana += 1
    return savgol_filter(ace, ventana, 2) # se suaviza la señal

def Mat_obj4_FR(ace, FM):
    """
    función que calcula el fragmento de reposo (el momento en el que está en reposo) 
    se utilizará más tarde para calcular la gravedad y otras cosas
    """
    tam_ventana = int(0.5 * FM) #definimos el tamaño de la ventana donde miramos
    muestras_primer_segundo = int(FM)#las muestras del primer segundo
    mejor_idx = 0 # definimos mejor indice
    mejor_std = np.inf # definimos mejor valor

    for i in range(0, muestras_primer_segundo - tam_ventana): 
        ventana = ace[i : i + tam_ventana] # definimos la ventana donde miramos
        std = np.std(ventana)
        if std < mejor_std:
            mejor_std = std # comprobamos en un bucle donde está el mejor valor
            mejor_idx = i # y que indice corresponde con ese valor
    return mejor_idx, tam_ventana

def Mat_obj5_GR(ace,FM):
    """
    función que calcula la gravedad en el momento de reposo mediante la función anterior para saber 
    cuando está en reposo
    """
    idx, tam_ventana = Mat_obj4_FR(ace,FM)
    valores = ace[idx : idx + tam_ventana] # la aceleración en la ventana de reposo es la gravedad
    return np.mean(valores)

def Mat_obj6_Integra(var,t,y0):
    """
    función que integra un array segun el tiempo y un valor inicial con una función de scipy
    """
    int_array = cumulative_trapezoid(var,t,initial = y0) # función de scipy para integrar arrays
    return int_array

def Mat_obj7_Puntos(ace,t):
    """
    función que con ace y t saca los datos necesarios de las funciones anteriores para calcular
    las fases del salto indice de salto, tiempo en el aire, indice de aterrizaje, además devuelve
    velocidad para poder ahorrar calcularlo en la siguiente función 
    """
    FM = Mat_obj2_FM(t)
    sua_ace = Mat_obj3_Sua(ace, FM) # datos necesario ace suavizada
    g_media = Mat_obj5_GR(ace, FM) # gravedad media
    ace_neta = sua_ace - g_media  # aceleración neta
    velocidad = Mat_obj6_Integra(ace_neta,t,0) # velocidad 
    idx, tam_ventana = Mat_obj4_FR(ace,FM) # indice y el tamaño de la ventana
    vent_reposo = velocidad[idx : idx + tam_ventana] # ventana de reposo
    std_reposo = np.std(vent_reposo) # valor de reposo  
    for i in range(len(velocidad)): # bucle para averiguar donde está el indice de impulso (cuando se impulsa)
        if  abs(velocidad[i]) > 3 * std_reposo: # para localizarlo se mide cuando la velocidad es el triple que en reposo
            idx_s = i # al encontralo se define y rompe el bucle
            break
    idx_T0 = np.argmax(velocidad[idx_s:]) + idx_s # indice de despegue (cuando salta ya impulsado) cuando la velocidad es máxima después del impulso
    idx_L = np.argmax(ace_neta[idx_T0:]) + idx_T0 # indice de aterrizaje (cuando vuelve al suelo) el cuando la aceleración es máxima depués del despegue
    t_aire = t[idx_L] - t[idx_T0] # tiempo en el aire diferencia entre salto y aterrizaje
    return  idx_T0, idx_L, t_aire, velocidad

def Mat_obj8_Altura(ace,t):
    """
    función que calcula mediante las 3 formulas dadas en física la altura del salto utilizando todo lo anterior
    """
    idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace,t) # los valores calculados en la anterior
    desplazamiento = Mat_obj6_Integra(velocidad,t,0) # el desplazamiento integrando la velocidad
    h1 = 9.81 * t_aire**2 / 8 # la altura según tiempo de vuelo
    h2 = velocidad[idx_T0]**2 / (2 * 9.81) # la altura según velocidad de despegue
    h3 = max(desplazamiento[idx_T0:idx_L]) # la altura según desplazamiento 
    return h1,h2,h3 # devuelve las 3 estimaciones 