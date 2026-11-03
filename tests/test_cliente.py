from unittest.mock import Mock, patch

import pytest
import requests

import cliente
from cliente import con_reintento, consultar_modelo, registrar_costo
from src.consumir_gemini import PRECIO_ENTRADA, PRECIO_SALIDA, enviar_peticion

RUTA_POST = "src.consumir_gemini.requests.post"


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0.0
    yield


@pytest.fixture
def sin_armar_peticion():
    """Evita depender de GEMINI_API_KEY al probar consultar_modelo."""
    with patch("cliente.armar_peticion", return_value=("url", {})):
        yield


def respuesta_falsa(status_code, json_data=None):
    falsa = Mock(status_code=status_code, ok=status_code < 400)
    falsa.json.return_value = json_data if json_data is not None else {}
    return falsa


# ---------- enviar_peticion ----------

@pytest.mark.parametrize("status", [401, 403])
def test_enviar_peticion_credencial_invalida(status):
    falsa = respuesta_falsa(status, {"error": {"message": "sin permiso"}})
    with patch(RUTA_POST, return_value=falsa):
        with pytest.raises(ValueError):
            enviar_peticion("url", {})


def test_enviar_peticion_llave_api_invalida_400():
    falsa = respuesta_falsa(400, {"error": {"message": "API key not valid. Please pass a valid API key."}})
    with patch(RUTA_POST, return_value=falsa):
        with pytest.raises(ValueError):
            enviar_peticion("url", {})


@pytest.mark.parametrize("status", [429, 500, 503])
def test_enviar_peticion_limite_de_uso_o_servidor(status):
    falsa = respuesta_falsa(status, {"error": {"message": "saturado"}})
    with patch(RUTA_POST, return_value=falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("url", {})


def test_enviar_peticion_timeout_de_red():
    with patch(RUTA_POST, side_effect=requests.exceptions.Timeout):
        with pytest.raises(TimeoutError):
            enviar_peticion("url", {})


def test_enviar_peticion_error_400_no_es_temporal():
    falsa = respuesta_falsa(400, {"error": {"message": "petición mal formada"}})
    with patch(RUTA_POST, return_value=falsa):
        with pytest.raises(RuntimeError):
            enviar_peticion("url", {})


def test_enviar_peticion_exito():
    falsa = respuesta_falsa(200, {"texto": "respuesta simulada"})
    with patch(RUTA_POST, return_value=falsa):
        assert enviar_peticion("url", {}) == {"texto": "respuesta simulada"}


# ---------- con_reintento ----------

def test_con_reintento_agota_intentos():
    llamadas = {"n": 0}

    def siempre_falla():
        llamadas["n"] += 1
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)

    assert llamadas["n"] == 3


def test_con_reintento_no_reintenta_value_error():
    llamadas = {"n": 0}

    def credencial_invalida():
        llamadas["n"] += 1
        raise ValueError("credencial inválida")

    with patch("cliente.time.sleep"):
        with pytest.raises(ValueError):
            con_reintento(credencial_invalida, intentos=3)

    assert llamadas["n"] == 1


def test_con_reintento_espera_entre_intentos():
    llamadas = {"n": 0}

    def falla_una_vez():
        llamadas["n"] += 1
        if llamadas["n"] == 1:
            raise TimeoutError("simulado")
        return "ok"

    with patch("cliente.time.sleep") as mock_sleep:
        resultado = con_reintento(falla_una_vez)

    assert resultado == "ok"
    mock_sleep.assert_called_once()


# ---------- registrar_costo ----------

def test_registrar_costo_incluye_tokens_de_razonamiento():
    datos = {"usageMetadata": {
        "promptTokenCount": 1000,
        "candidatesTokenCount": 500,
        "thoughtsTokenCount": 500,
    }}
    esperado = 1000 * PRECIO_ENTRADA + 1000 * PRECIO_SALIDA
    assert registrar_costo(datos) == pytest.approx(esperado)


def test_registrar_costo_acumula():
    datos = {"usageMetadata": {"promptTokenCount": 1000, "candidatesTokenCount": 1000}}
    primero = registrar_costo(datos)
    segundo = registrar_costo(datos)
    assert cliente.costo_total_sesion == pytest.approx(primero + segundo)


# ---------- consultar_modelo ----------

def test_consultar_modelo_convierte_error(sin_armar_peticion):
    with patch("cliente.con_reintento", side_effect=TimeoutError("simulado")):
        with pytest.raises(RuntimeError, match="varios intentos"):
            consultar_modelo("pregunta")


def test_consultar_modelo_propaga_value_error(sin_armar_peticion):
    with patch("cliente.con_reintento", side_effect=ValueError("credencial inválida")):
        with pytest.raises(ValueError, match="credencial"):
            consultar_modelo("pregunta")


def test_consultar_modelo_devuelve_texto_y_registra_costo(sin_armar_peticion):
    datos = {
        "candidates": [{"content": {"parts": [{"text": "Santiago"}]}}],
        "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
    }
    with patch("cliente.con_reintento", return_value=datos):
        assert consultar_modelo("¿Capital de Chile?") == "Santiago"
    assert cliente.costo_total_sesion > 0