import pytest

from pipeline_texto import (
    calcular_metricas,
    calcular_precision_cobertura_f1,
    contar_coincidencias,
    limpiar_texto,
    procesar_texto,
    proporcion_coincidencia,
    resumir_metricas,
    vectorizar,
)

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

def test_contar_coincidencias_respeta_repeticiones():
    assert contar_coincidencias(["el", "gato"], ["el", "gato", "el", "gato"]) == 2


def test_metricas_ejemplo_calculado_a_mano():
    referencia = procesar_texto("El gato duerme en el sofá.")
    respuesta = procesar_texto("El gato duerme en el sillón todo el día.")
    resultado = calcular_precision_cobertura_f1(referencia, respuesta)
    assert resultado["precision"] == pytest.approx(5 / 9)
    assert resultado["cobertura"] == pytest.approx(5 / 6)
    assert resultado["f1"] == pytest.approx(2 / 3)


def test_metricas_texto_vacio_devuelve_ceros():
    esperado = {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}
    assert calcular_precision_cobertura_f1([], ["hola"]) == esperado
    assert calcular_precision_cobertura_f1(["hola"], []) == esperado


def test_metricas_limite_sinonimo_perfecto():
    """Limitación conocida: sinónimos se penalizan."""
    referencia = procesar_texto("El auto es veloz.")
    respuesta = procesar_texto("El vehículo es rápido.")
    assert calcular_precision_cobertura_f1(referencia, respuesta)["f1"] == pytest.approx(0.5)


def test_metricas_limite_negacion_casi_no_se_nota():
    """Limitación conocida: quitar 'no' invierte el sentido y F1 sigue alto."""
    referencia = procesar_texto("Python no es un lenguaje compilado.")
    respuesta = procesar_texto("Python es un lenguaje compilado.")
    assert calcular_precision_cobertura_f1(referencia, respuesta)["f1"] == pytest.approx(0.909, abs=0.001)

# --- Bloque 16, segmento 2 ---

def test_metricas_limite_dato_equivocado_puntua_alto():
    """Limitación conocida: cambiar 1991 por 1989 solo cuenta como una palabra distinta."""
    referencia = procesar_texto("Python fue creado en 1991.")
    respuesta = procesar_texto("Python fue creado en 1989.")
    resultado = calcular_precision_cobertura_f1(referencia, respuesta)
    assert resultado["precision"] == pytest.approx(0.8)
    assert resultado["cobertura"] == pytest.approx(0.8)
    assert resultado["f1"] == pytest.approx(0.8)

def test_calcular_metricas_aplica_pipeline_a_ambos_lados():
    resultado = calcular_metricas("El cielo es azul.", "el cielo es azul")
    assert resultado == {"precision": 1.0, "cobertura": 1.0, "f1": 1.0}


def test_resumir_metricas_promedia():
    resultados = [
        {"precision": 0.83, "cobertura": 0.71, "f1": 0.77},
        {"precision": 0.40, "cobertura": 0.50, "f1": 0.44},
        {"precision": 0.62, "cobertura": 0.62, "f1": 0.62},
    ]
    assert resumir_metricas(resultados)["f1_promedio"] == pytest.approx(0.61)


def test_resumir_metricas_lista_vacia_devuelve_ceros():
    assert resumir_metricas([]) == {
        "precision_promedio": 0.0,
        "cobertura_promedio": 0.0,
        "f1_promedio": 0.0,
    }