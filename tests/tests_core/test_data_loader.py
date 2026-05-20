import pytest
from core.data_loader import *
import pandas as pd


def test_validate_file_exist(tmp_path):
    fichero = tmp_path / "prueba.xlsx"
    fichero.write_text("contenido")
    assert validate_file_exists(str(fichero)) == True

def test_validate_file_exists_error():
    with pytest.raises(FileNotFoundError):
        validate_file_exists("fichero_que_no_existe.xlsx")

def test_validate_file_extension(tmp_path):
    fichero = tmp_path / "prueba.xlsx"
    fichero.write_text("contenido")
    assert validate_file_extension(str(fichero)) == True

def test_validate_file_extension_error():
    with pytest.raises(ValueError):
        validate_file_extension("fichero_sin_extension_correcta.txt")




def test_read_excel_file(tmp_path):
    fichero = tmp_path / "prueba.xlsx"
    fichero.write_text("contenido")
    df_original = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    df_original.to_excel(str(fichero), index=False)
    resultado = read_excel_file(str(fichero))
    assert isinstance(resultado, pd.DataFrame)

def test_read_excel_file_error(tmp_path):
    fichero = tmp_path / "prueba.xlsx"
    fichero.write_text("esto no es un excel")
    with pytest.raises(Exception):
        read_excel_file(str(fichero))

def test_extract_column_as_float(tmp_path):
    fichero = tmp_path / "prueba.xlsx"
    df_original = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    df_original.to_excel(str(fichero), index=False)
    df = read_excel_file(str(fichero))
    resultado = extract_column_as_float(df, 0)
    assert isinstance(resultado, np.ndarray)
    for number in resultado:
        assert isinstance(number,float)




def test_validate_min_lenght():
    array = np.array([1.0,2.0])
    assert validate_min_length(array, 2) ==  True
    assert validate_min_length(array, 1) == True
    assert validate_min_length(array, 0) == True

def test_validate_min_lenght_error():
    array = np.array([1.0])
    with pytest.raises(ValueError):
        validate_min_length(array,2)
