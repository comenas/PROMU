import os 
import pandas as pd
import numpy as np

def validate_file_exists(path):
    """
    función que comprueba que el archivo existe si no existe lanza FileNotFoundError
    si existe devuelve True
    """
    if os.path.exists(path): #comprueba la existencia
        return True
    else:
        raise FileNotFoundError(f"No se encontró el fichero: {path}") #lanzar error

def validate_file_extension(path):
    """
    función que comprueba la extension del archivo si no es .xlsx lanza ValueError
    si es correcta devuelve True
    """
    extension = os.path.splitext(path)[1] #funcion propia de la libreria os que divide el texto
    if extension.lower() == ".xlsx": #el archivo debe ser excel
        return True
    else:
        raise ValueError(f"Extensión del archivo {path} erronea") #lanzar error

def read_excel_file(path):
    """
    función que lee el archivo excel mediante pandas
    """
    return pd.read_excel(path) #el propio pandas lanza el error si algo sale mal

def extract_column_as_float(df, col_idx):
    """
    función que transforma cada columna del dataFrame a float
    """
    columna = df.iloc[:, col_idx] #extrae columna
    return columna.to_numpy(dtype = float) #transforma en float

def validate_no_nan(array):
    """
    función que valida si existe algún valor Nan dentro del array
    """
    validacion = np.isnan(array) #función numpy que devuelve un array de true y false
    if validacion.any(): #mira el array por si hay algún True 
        raise ValueError(f"Algún Valor Nan en el array") #si alguno es True lanza error
    else:
        return True #si no, pasa
    
def validate_min_length(array, min_len):
    """
    función que comprueba que en el array hay al menos el mínimo de valores indicados
    """
    if len(array) < min_len: #cantidad de valores mayor al mínimo
        raise ValueError(f"Hay menos valores de los mínimos en el array") #lanza error si no es así
    else:
        return True
