import pytest

from pipeline_texto import limpiar_texto, procesar_texto, proporcion_coincidencia, vectorizar


def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    assert procesar_texto("El Cielo, es AZUL!") == ["el", "cielo", "es", "azul"]


def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    assert procesar_texto("¡¡¡...!!!") == []


def test_limpiar_texto_rechaza_algo_que_no_es_texto():
    with pytest.raises(TypeError):
        limpiar_texto(None)


def test_vectorizar_cuenta_repeticiones():
    assert vectorizar(["el", "gato", "el"]) == {"el": 2, "gato": 1}


def test_proporcion_coincidencia_ignora_diferencias_de_formato():
    referencia = procesar_texto("El cielo es azul.")
    respuesta = procesar_texto("el cielo es azul")
    assert proporcion_coincidencia(referencia, respuesta) == 1.0


def test_proporcion_coincidencia_referencia_vacia_devuelve_cero():
    assert proporcion_coincidencia([], ["hola"]) == 0.0


def test_proporcion_coincidencia_no_distingue_orden():
    """Limitación conocida: la métrica compara conjuntos de palabras, no su orden."""
    referencia = procesar_texto("El perro persiguió al gato.")
    respuesta = procesar_texto("El gato persiguió al perro.")
    assert proporcion_coincidencia(referencia, respuesta) == 1.0