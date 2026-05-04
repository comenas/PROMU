import os 
import pandas 

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
    return pandas.read_excel(path)
