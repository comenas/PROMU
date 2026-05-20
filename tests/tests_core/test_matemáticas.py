import pytest
from core.matemáticas import *
import numpy as np

def test_mat_obj1_AD_sin_aceleraci(tmp_path):
    fichero = tmp_path / "prueba.xlsx"
    df = pd.DataFrame({
        "tiempo": [0.0, 0.01, 0.02],
        "ace_x":  [0.1, 0.2, 0.3],
        "ace_y":  [0.4, 0.5, 0.6],
        "ace_z":  [0.7, 0.8, 0.9]
    })
    df.to_excel(str(fichero), index=False)
    tiempo, ace_y, aceleracion = Mat_obj1_AD(str(fichero))
    assert isinstance(tiempo, np.ndarray)
    assert isinstance(ace_y, np.ndarray)
    assert isinstance(aceleracion, np.ndarray)
    assert len(tiempo) == 3

def test_mat_obj1_AD_con_aceleracion(tmp_path):
    fichero = tmp_path / "prueba.xlsx"
    df = pd.DataFrame({
        "tiempo": [0.0, 0.01, 0.02],
        "ace_x":  [0.1, 0.2, 0.3],
        "ace_y":  [0.4, 0.5, 0.6],
        "ace_z":  [0.7, 0.8, 0.9],
        "ace":    [1.0, 1.1, 1.2]
    })
    df.to_excel(str(fichero), index=False)
    tiempo, ace_y, aceleracion = Mat_obj1_AD(str(fichero))
    assert np.allclose(tiempo, [0.0,0.01,0.02])
    assert np.allclose(ace_y, [0.4,0.5,0.6])
    assert np.allclose(aceleracion, [1.0, 1.1, 1.2])

def test_mat_obj2_FM():
    tiempo = np.array([2,4])
    assert Mat_obj2_FM(tiempo) == 1/2


def test_mat_obj2_FM_error():
    tiempo = np.array([1])
    with pytest.raises(ValueError):
        Mat_obj2_FM(tiempo)

def test_mat_obj3_sua():
    FM = 20.0
    ace = np.array([5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0])
    resultado = Mat_obj3_Sua(ace, FM)
    assert np.allclose(ace, resultado)

def test_mat_obj4_FR():
    FM = 20.0
    ace = np.array([5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                    5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0,
                    50.0, 80.0, 90.0, 70.0, 60.0])
    idx, tam_ventana = Mat_obj4_FR(ace, FM)
    assert idx == 0
    assert tam_ventana == 10

def test_mat_obj5_GR():
    FM = 20.0
    ace = np.array([9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81,
                    9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81, 9.81,
                    50.0, 80.0, 90.0, 70.0, 60.0])
    resultado = Mat_obj5_GR(ace, FM)
    assert abs(resultado - 9.81) < 0.01

def test_mat_obj6_Integra():
    t = np.linspace(0, 1, 100)
    var = np.ones(100)
    resultado = Mat_obj6_Integra(var, t, 0)
    assert np.allclose(resultado, t, atol=0.01)

def test_mat_obj6_Integra_y0():
    t = np.linspace(0, 1, 100)
    var = np.zeros(100)
    resultado = Mat_obj6_Integra(var, t, 5.0)
    assert np.allclose(resultado, 5.0, atol=0.01)

def test_mat_obj7_Puntos():
    FM = 100.0
    t = np.linspace(0, 3, 300)
    ace = np.ones(300) * 9.81
    ace_y = np.ones(300) * 9.81  # positivo → signo 
    ace[50:80] = 15.0
    ace[80:150] = 9.81
    ace[150] = 25.0
    idx_T0, idx_L, t_aire, velocidad = Mat_obj7_Puntos(ace, ace_y, t)
    assert idx_T0 < idx_L
    assert t_aire.any() > 0
    assert velocidad.any() > 0 

def test_mat_obj8_Altura():
    FM = 100.0
    t = np.linspace(0, 3, 300)
    ace = np.ones(300) * 9.81
    ace_y = np.ones(300) * 9.81
    ace[50:80] = 15.0
    ace[80:150] = 9.81
    ace[150] = 25.0
    h1, h2, h3 = Mat_obj8_Altura(ace, ace_y, t)
    assert h1 > 0
    assert h2 > 0
    assert h3 > 0