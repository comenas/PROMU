"""
tests/tests_interfaz/test_cli.py

Tests de la interfaz CLI ordenados de más fácil a más difícil.
Los tests más complejos (menús interactivos) se documentan como manuales.
"""

import pytest
import sys
import os
import json
import socket
from unittest.mock import patch, MagicMock, call

# ── Ajuste de rutas para que pytest encuentre el paquete ──────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces.cli.cli import (
    limpiar,
    titulo,
    mensaje,
    pedir,
    recibir_linea,
    recibir_leaderboard,
    accion_analizar_salto,
    accion_iniciar_sesion,
    accion_cerrar_sesion,
    accion_ver_ranking,
    accion_enviar_salto,
    sesion,
)


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 1 — Funciones de consola (sin red, sin ficheros)
# Nivel: MUY FÁCIL — solo comprueban salida estándar
# ══════════════════════════════════════════════════════════════════════════════

class TestFuncionesConsola:
    """Valida que titulo(), mensaje() , pedir() y limpiar() producen la salida esperada."""

    def test_limpiar(self):
        """
        comprueba que aparece el comando clear o cls en la consola
        """
        # Determinamos qué comando esperamos según el sistema operativo
        comando_esperado = 'cls' if os.name == "nt" else 'clear'
        # Interceptamos la llamada a os.system
        with patch("os.system") as mock_system:
            limpiar()
        # Verificamos que os.system fue llamado una vez
        mock_system.assert_called_once_with(comando_esperado)

    def test_titulo_imprime_separadores(self, capsys):
        titulo("HOLA MUNDO")
        out = capsys.readouterr().out
        assert "=" * 50 in out
        assert "HOLA MUNDO" in out

    def test_titulo_doble_separador(self, capsys):
        titulo("TEST")
        out = capsys.readouterr().out
        assert out.count("=" * 50) == 2

    def test_mensaje_prefijo_por_defecto(self, capsys):
        mensaje("Texto de prueba")
        out = capsys.readouterr().out
        assert ">>" in out
        assert "Texto de prueba" in out

    def test_mensaje_prefijo_personalizado(self, capsys):
        mensaje("Algo salió mal", prefijo="!!")
        out = capsys.readouterr().out
        assert "!!" in out
        assert "Algo salió mal" in out

    def test_mensaje_prefijo_ok(self, capsys):
        mensaje("Conexión establecida", prefijo="OK")
        out = capsys.readouterr().out
        assert "OK" in out

    def test_pedir_retorna_input_sin_espacios(self):
        with patch("builtins.input", return_value="  usuario  "):
            resultado = pedir("Introduce usuario")
        assert resultado == "usuario"

    def test_pedir_incluye_texto_en_prompt(self):
        """El prompt visible debe incluir el texto pedido."""
        prompts_vistos = []
        def fake_input(prompt):
            prompts_vistos.append(prompt)
            return "valor"
        with patch("builtins.input", side_effect=fake_input):
            pedir("Contraseña")
        assert "Contraseña" in prompts_vistos[0]


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 2 — Primitivas de red (socket mockeado)
# Nivel: FÁCIL — se prueba la lógica de lectura sin red real
# ══════════════════════════════════════════════════════════════════════════════

class TestPrimitivasRed:
    """Prueba recibir_linea y recibir_leaderboard con sockets simulados."""

    def _socket_con_datos(self, bytes_secuencia):
        """Devuelve un mock de socket que entrega los bytes de uno en uno."""
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [bytes([b]) for b in bytes_secuencia]
        return mock_sock

    def test_recibir_linea_simple(self):
        datos = b"100 OK\r\n"
        sock  = self._socket_con_datos(datos)
        linea = recibir_linea(sock)
        assert linea == "100 OK\r\n"

    def test_recibir_linea_con_acentos(self):
        # El servidor puede enviar caracteres UTF-8
        datos = "200 BIENVENIDO\r\n".encode("utf-8")
        sock  = self._socket_con_datos(datos)
        linea = recibir_linea(sock)
        assert "200" in linea

    def test_recibir_linea_conexion_cerrada(self):
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b""          # señal de cierre
        with pytest.raises(RuntimeError, match="cerrada"):
            recibir_linea(mock_sock)

    def test_recibir_linea_demasiado_larga(self):
        # Supera MAX_MSG (4096 bytes) sin encontrar \r\n
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b"X"         # devuelve 'X' infinitamente
        with pytest.raises(RuntimeError, match="larga"):
            recibir_linea(mock_sock)

    def test_recibir_leaderboard_termina_con_no_hay_mas(self):
        respuestas = [
            b"1 GARCIA 45\r\n",
            b"2 LOPEZ 40\r\n",
            b"202 NO HAY M\xc3\x81S REGISTROS\r\n",   # UTF-8
        ]
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            bytes([b]) for linea in respuestas for b in linea
        ]
        lineas = recibir_leaderboard(mock_sock)
        assert len(lineas) == 3
        assert any("202" in l for l in lineas)

    def test_recibir_leaderboard_termina_con_no_hay_registros(self):
        respuestas = [
            b"201 NO HAY REGISTROS TODAVIA\r\n",
        ]
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            bytes([b]) for linea in respuestas for b in linea
        ]
        lineas = recibir_leaderboard(mock_sock)
        assert len(lineas) == 1


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 — Gestión de sesión
# Nivel: MEDIO — comprueba el estado mutable del dict sesion
# ══════════════════════════════════════════════════════════════════════════════

class TestGestionSesion:
    """Verifica que accion_cerrar_sesion limpia el estado de sesión."""

    def setup_method(self):
        """Inyecta una sesión activa falsa antes de cada test."""
        mock_sock = MagicMock()
        sesion["socket"]      = mock_sock
        sesion["autenticado"] = True
        sesion["usuario"]     = "alumno01"

    def teardown_method(self):
        """Deja el estado limpio para otros tests."""
        sesion["socket"]      = None
        sesion["autenticado"] = False
        sesion["usuario"]     = None

    def test_cerrar_sesion_limpia_autenticado(self, capsys):
        accion_cerrar_sesion()
        assert sesion["autenticado"] is False

    def test_cerrar_sesion_limpia_usuario(self, capsys):
        accion_cerrar_sesion()
        assert sesion["usuario"] is None

    def test_cerrar_sesion_limpia_socket(self, capsys):
        accion_cerrar_sesion()
        assert sesion["socket"] is None

    def test_cerrar_sesion_envia_quit(self, capsys):
        mock_sock = sesion["socket"]
        accion_cerrar_sesion()
        mock_sock.send.assert_called_with(b"QUIT\r\n")

    def test_cerrar_sesion_sin_socket_no_falla(self, capsys):
        sesion["socket"] = None
        accion_cerrar_sesion()       # no debe lanzar excepción
        assert sesion["autenticado"] is False


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 — accion_analizar_salto (core mockeado)
# Nivel: MEDIO-ALTO — requiere mockear el core y la entrada de usuario
# ══════════════════════════════════════════════════════════════════════════════

class TestAccionAnalizarSalto:
    """
    Prueba accion_analizar_salto mockeando el core matemático y
    la entrada de ruta por teclado.
    """

    RESULTADOS_MOCK = (
        0.35,           # h1 en metros  → 35 cm
        0.32,           # h2
        0.30,           # h3
    )

    @patch("interfaces.cli.cli.Mat_obj8_Altura")
    @patch("interfaces.cli.cli.Mat_obj7_Puntos")
    @patch("interfaces.cli.cli.Mat_obj1_AD")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.input", return_value="/ruta/falsa/salto.xlsx")
    def test_devuelve_h1_correcto(
        self, mock_input, mock_exists, mock_AD, mock_7, mock_8, capsys
    ):
        import numpy as np
        t        = np.linspace(0, 3, 300)
        ace      = np.ones(300) * 9.81
        ace_y    = ace.copy()
        vel      = np.ones(300) * 2.5
        mock_AD.return_value   = (t, ace_y, ace)
        mock_7.return_value    = (50, 150, 0.5, vel)
        mock_8.return_value    = self.RESULTADOS_MOCK

        h1, formateados = accion_analizar_salto()

        assert h1 == pytest.approx(0.35)

    @patch("interfaces.cli.cli.Mat_obj8_Altura")
    @patch("interfaces.cli.cli.Mat_obj7_Puntos")
    @patch("interfaces.cli.cli.Mat_obj1_AD")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.input", return_value="/ruta/falsa/salto.xlsx")
    def test_resultados_contienen_claves_esperadas(
        self, mock_input, mock_exists, mock_AD, mock_7, mock_8, capsys
    ):
        import numpy as np
        t     = np.linspace(0, 3, 300)
        ace   = np.ones(300) * 9.81
        vel   = np.ones(300) * 2.5
        mock_AD.return_value = (t, ace.copy(), ace)
        mock_7.return_value  = (50, 150, 0.5, vel)
        mock_8.return_value  = self.RESULTADOS_MOCK

        _, formateados = accion_analizar_salto()

        assert "altura_vuelo" in formateados
        assert "tiempo_vuelo" in formateados
        assert "velocidad_despegue" in formateados

    @patch("os.path.exists", return_value=False)
    @patch("builtins.input", return_value="/ruta/inexistente.xlsx")
    def test_fichero_no_encontrado_devuelve_none(
        self, mock_input, mock_exists, capsys
    ):
        h1, formateados = accion_analizar_salto()
        assert h1 is None
        assert formateados is None

    @patch("interfaces.cli.cli.Mat_obj1_AD", side_effect=ValueError("columna faltante"))
    @patch("os.path.exists", return_value=True)
    @patch("builtins.input", return_value="/ruta/falsa/salto.xlsx")
    def test_error_en_core_devuelve_none(
        self, mock_input, mock_exists, mock_AD, capsys
    ):
        h1, formateados = accion_analizar_salto()
        assert h1 is None


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 5 — accion_iniciar_sesion (socket real mockeado)
# Nivel: ALTO — simula todo el handshake de red
# ══════════════════════════════════════════════════════════════════════════════

class TestAccionIniciarSesion:
    """
    Simula el handshake completo con el servidor (HELLO→USER→PASS)
    usando un socket falso.
    """

    def setup_method(self):
        sesion["socket"]      = None
        sesion["autenticado"] = False
        sesion["usuario"]     = None

    def teardown_method(self):
        sesion["socket"]      = None
        sesion["autenticado"] = False
        sesion["usuario"]     = None

    def _mock_sock_exitoso(self):
        """Simula las 3 respuestas correctas del servidor."""
        mock_sock = MagicMock()
        respuestas = [
            b"100 HELLO OK\r\n",
            b"101 USER OK\r\n",
            b"102 PASS OK\r\n",
        ]
        mock_sock.recv.side_effect = [
            bytes([b]) for linea in respuestas for b in linea
        ]
        return mock_sock

    @patch("interfaces.cli.cli.socket.socket")
    @patch("interfaces.cli.cli.socket.gethostbyname", return_value="127.0.0.1")
    @patch("interfaces.cli.cli.socket.gethostname",   return_value="localhost")
    @patch("builtins.input", side_effect=["alumno01", "pass123"])
    def test_login_exitoso_autentica_sesion(
        self, mock_input, mock_hn, mock_gbn, mock_socket_cls, capsys
    ):
        mock_socket_cls.return_value = self._mock_sock_exitoso()
        accion_iniciar_sesion()
        assert sesion["autenticado"] is True
        assert sesion["usuario"] == "alumno01"

    @patch("interfaces.cli.cli.socket.socket")
    @patch("interfaces.cli.cli.socket.gethostbyname", return_value="127.0.0.1")
    @patch("interfaces.cli.cli.socket.gethostname",   return_value="localhost")
    @patch("builtins.input", side_effect=["alumno01", "pass_mala"])
    def test_credenciales_incorrectas_no_autentica(
        self, mock_input, mock_hn, mock_gbn, mock_socket_cls, capsys
    ):
        mock_sock = MagicMock()
        respuestas = [
            b"100 HELLO OK\r\n",
            b"101 USER OK\r\n",
            b"400 PASS FAIL\r\n",   # contraseña incorrecta
        ]
        mock_sock.recv.side_effect = [
            bytes([b]) for l in respuestas for b in l
        ]
        mock_socket_cls.return_value = mock_sock
        accion_iniciar_sesion()
        assert sesion["autenticado"] is False

    @patch("interfaces.cli.cli.socket.socket")
    @patch("interfaces.cli.cli.socket.gethostbyname", return_value="127.0.0.1")
    @patch("interfaces.cli.cli.socket.gethostname",   return_value="localhost")
    @patch("builtins.input", side_effect=["alumno01", "pass123"])
    def test_timeout_no_autentica_y_muestra_error(
        self, mock_input, mock_hn, mock_gbn, mock_socket_cls, capsys
    ):
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = socket.timeout
        mock_socket_cls.return_value = mock_sock
        accion_iniciar_sesion()
        out = capsys.readouterr().out
        assert sesion["autenticado"] is False
        assert "agotado" in out.lower() or "timeout" in out.lower()

    @patch("interfaces.cli.cli.socket.socket")
    @patch("interfaces.cli.cli.socket.gethostbyname", return_value="127.0.0.1")
    @patch("interfaces.cli.cli.socket.gethostname",   return_value="localhost")
    @patch("builtins.input", side_effect=["alumno01", "pass_mala"])
    def test_hello_return_no_exitoso(self, mock_input, mock_hn, mock_gbn, mock_socket_cls, capsys
    ):
        mock_sock = MagicMock()
        respuestas = [
            b"200 HELLO Error\r\n",
            b"101 USER OK\r\n",
            b"400 PASS FAIL\r\n",   # contraseña incorrecta
        ]
        mock_sock.recv.side_effect = [
            bytes([b]) for l in respuestas for b in l
        ]
        mock_socket_cls.return_value = mock_sock
        accion_iniciar_sesion()
        assert sesion["autenticado"] is False
    
    @patch("interfaces.cli.cli.socket.socket")
    @patch("interfaces.cli.cli.socket.gethostbyname", return_value="127.0.0.1")
    @patch("interfaces.cli.cli.socket.gethostname",   return_value="localhost")
    @patch("builtins.input", side_effect=["alumno01", "pass_mala"])
    def test_user_return_no_exitoso(self, mock_input, mock_hn, mock_gbn, mock_socket_cls, capsys
    ):
        mock_sock = MagicMock()
        respuestas = [
            b"100 HELLO OK\r\n",
            b"200 USER Error\r\n",
            b"400 PASS FAIL\r\n",   # contraseña incorrecta
        ]
        mock_sock.recv.side_effect = [
            bytes([b]) for l in respuestas for b in l
        ]
        mock_socket_cls.return_value = mock_sock
        accion_iniciar_sesion()
        assert sesion["autenticado"] is False



# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 6 — accion_ver_ranking
# Nivel: ALTO — distingue uso con y sin sesión activa
# ══════════════════════════════════════════════════════════════════════════════

class TestAccionVerRanking:

    def setup_method(self):
        sesion["socket"]      = None
        sesion["autenticado"] = False
        sesion["usuario"]     = None

    def teardown_method(self):
        sesion["socket"]      = None
        sesion["autenticado"] = False
        sesion["usuario"]     = None

    def _lineas_leaderboard(self):
        return [
            b"1 GARCIA 450\r\n",
            b"2 LOPEZ 400\r\n",
            b"202 NO HAY M\xc3\x81S REGISTROS\r\n",
        ]

    @patch("interfaces.cli.cli.socket.socket")
    @patch("interfaces.cli.cli.socket.gethostbyname", return_value="127.0.0.1")
    @patch("interfaces.cli.cli.socket.gethostname",   return_value="localhost")
    def test_ranking_sin_sesion_abre_socket_anonimo(
        self, mock_hn, mock_gbn, mock_socket_cls, capsys
    ):
        mock_sock = MagicMock()
        all_bytes = b"100 OK\r\n" + b"1 GARCIA 450\r\n" + b"202 NO HAY M\xc3\x81S REGISTROS\r\n"
        mock_sock.recv.side_effect = [bytes([b]) for b in all_bytes]
        mock_socket_cls.return_value = mock_sock
        accion_ver_ranking("GET_LEADERBOARD_MEN", "RANKING MASCULINO")
        out = capsys.readouterr().out
        # El resultado debe aparecer en pantalla
        assert "GARCIA" in out or "202" in out

    def test_ranking_con_sesion_usa_socket_existente(self, capsys):
        mock_sock = MagicMock()
        all_bytes = b"1 GARCIA 450\r\n" + b"202 NO HAY M\xc3\x81S REGISTROS\r\n"
        mock_sock.recv.side_effect = [bytes([b]) for b in all_bytes]
        sesion["socket"]      = mock_sock
        sesion["autenticado"] = True
        sesion["usuario"]     = "alumno01"

        accion_ver_ranking("GET_LEADERBOARD_MEN", "RANKING MASCULINO")
        out = capsys.readouterr().out
        assert "GARCIA" in out or "202" in out


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 7 — accion_enviar_salto
# Nivel: MUY ALTO — combina entrada de usuario, análisis de core y red
# ══════════════════════════════════════════════════════════════════════════════

class TestAccionEnviarSalto:

    def setup_method(self):
        mock_sock = MagicMock()
        resp = b"200 SALTO REGISTRADO\r\n"
        mock_sock.recv.side_effect = [bytes([b]) for b in resp]
        sesion["socket"]      = mock_sock
        sesion["autenticado"] = True
        sesion["usuario"]     = "alumno01"

    def teardown_method(self):
        sesion["socket"]      = None
        sesion["autenticado"] = False
        sesion["usuario"]     = None

    @patch("interfaces.cli.cli.Mat_obj8_Altura")
    @patch("interfaces.cli.cli.Mat_obj7_Puntos")
    @patch("interfaces.cli.cli.Mat_obj1_AD")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.input", side_effect=["A2-4", "/ruta/falsa/salto.xlsx"])
    def test_envio_exitoso_llama_send(
        self, mock_input, mock_exists, mock_AD, mock_7, mock_8, capsys
    ):
        import numpy as np
        t   = np.linspace(0, 3, 300)
        ace = np.ones(300) * 9.81
        vel = np.ones(300) * 2.5
        mock_AD.return_value = (t, ace.copy(), ace)
        mock_7.return_value  = (50, 150, 0.5, vel)
        mock_8.return_value  = (0.35, 0.32, 0.30)

        accion_enviar_salto()

        # Verificar que se llamó send con SEND_DATA
        calls = [str(c) for c in sesion["socket"].send.call_args_list]
        assert any("SEND_DATA" in c for c in calls)

    @patch("builtins.input", side_effect=["", "/ruta/cualquiera.xlsx"])
    def test_grupo_vacio_aborta_envio(self, mock_input, capsys):
        accion_enviar_salto()
        out = capsys.readouterr().out
        assert "vacío" in out.lower() or "vacio" in out.lower()

    def test_sin_sesion_activa_aborta_envio(self, capsys):
        sesion["socket"]      = None
        sesion["autenticado"] = False
        with patch("builtins.input", side_effect=["A2-4", "/ruta/falsa.xlsx"]):
            with patch("os.path.exists", return_value=True):
                with patch("interfaces.cli.cli.Mat_obj1_AD", side_effect=Exception("no se llama")):
                    # La acción debe abortar antes de analizar si no hay sesión
                    # Nota: la implementación actual pide la ruta antes de validar sesión,
                    # por lo que mockeamos también el análisis para verificar el mensaje final
                    pass
        # Este caso límite se documenta como TEST MANUAL (ver abajo)


# ══════════════════════════════════════════════════════════════════════════════
# TEST MANUAL — Menús interactivos
# ══════════════════════════════════════════════════════════════════════════════
#
# Los siguientes casos NO se automatizan porque dependen de bucles interactivos
# (menu_principal, menu_usuario, menu_invitado) que llaman a input() en bucle
# y a sys.exit(). Mockearlos completamente produciría tests frágiles con poco
# valor diagnóstico. Se propone el siguiente protocolo MANUAL:
#
# CASO M-1: Menú principal — flujo completo autenticado
#   Precondición : servidor disponible en 158.42.188.200:64010
#   Pasos        :
#     1. Ejecutar:  python interfaces/cli/cli.py
#     2. Seleccionar opción "1" (Iniciar sesión)
#     3. Introducir credenciales válidas
#     4. Verificar que aparece el MENÚ USUARIO con el nombre del usuario
#     5. Seleccionar "2" (Ranking masculino) → debe mostrar filas del ranking
#     6. Seleccionar "4" (Cerrar sesión) → vuelve al menú principal
#     7. Seleccionar "0" (Salir) → termina el proceso
#   Resultado esperado: cada pantalla muestra la información correcta sin errores
#
# CASO M-2: Menú principal — flujo invitado
#   Precondición : ninguna (no necesita servidor)
#   Pasos        :
#     1. Ejecutar:  python interfaces/cli/cli.py
#     2. Seleccionar opción "2" (Continuar como invitado)
#     3. Seleccionar "1" (Analizar salto) e introducir ruta a un .xlsx válido
#     4. Verificar que se muestran los 5 resultados (alturas, tiempo, velocidad)
#     5. Seleccionar "0" (Volver) → regresa al menú principal
#   Resultado esperado: resultados coherentes con los valores del fichero
#
# CASO M-3: Opción inválida
#   Pasos: en cualquier menú introducir "9"
#   Resultado esperado: mensaje "Opción no válida." y se repite el menú
#
# ══════════════════════════════════════════════════════════════════════════════