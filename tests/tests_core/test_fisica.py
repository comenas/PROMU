import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch
from core.fisica import Graficas_salto, abrir_graficas_en_hilo
import threading


def salto_excel(tmp_path):
    """Fixture auxiliar: crea un Excel mínimo de salto válido."""
    fichero = tmp_path / "salto.xlsx"
    t = np.linspace(0, 3, 300)
    pd.DataFrame({
        "tiempo": t,
        "ace_x":  np.ones(300) * 0.1,
        "ace_y":  np.ones(300) * 9.81,
        "ace_z":  np.ones(300) * 0.1,
    }).to_excel(str(fichero), index=False)
    return str(fichero)


@patch("matplotlib.pyplot.show")
def test_graficas_salto_no_crash(mock_show, tmp_path):
    """Graficas_salto no lanza excepciones con datos válidos."""
    path = salto_excel(tmp_path)
    Graficas_salto(path, 70)
    assert mock_show.called


@patch("matplotlib.pyplot.show")
def test_graficas_salto_fichero_inexistente(mock_show, tmp_path):
    """Graficas_salto lanza FileNotFoundError si el fichero no existe."""
    with pytest.raises(FileNotFoundError):
        Graficas_salto("no_existe.xlsx", 70)


@patch("matplotlib.pyplot.show")
def test_abrir_graficas_en_hilo_lanza_hilo(mock_show, tmp_path):
    """abrir_graficas_en_hilo arranca un hilo daemon sin bloquearse."""
    path = salto_excel(tmp_path)
    hilos_antes = threading.active_count()
    abrir_graficas_en_hilo(path, 70)
    assert threading.active_count() >= hilos_antes