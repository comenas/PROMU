from core.formatter import *
import pytest

def test_format_height():
    assert format_height(0.456) == "45.6 cm"

def test_format_velocity():
    assert format_velocity(24.23) == "24.23 m/s"

def test_format_time():
    assert format_time(30.222) == "30.222 s"

def test_format_results():
    entrada = {
        "altura_vuelo": 0.45,
        "velocidad_despegue": 2.98,
        "tiempo_vuelo": 0.342
    }
    resultado = format_results(entrada)
    assert resultado["altura_vuelo"] == "45.0 cm"
    assert resultado["velocidad_despegue"] == "2.98 m/s"
    assert resultado["tiempo_vuelo"] == "0.342 s"

def test_format_results_error():
    entrada = {"cosa_rara": 1.0}
    with pytest.raises(ValueError):
        format_results(entrada)
