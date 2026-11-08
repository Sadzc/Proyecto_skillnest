import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
import pytest

from src.enrutamiento import (
    construir_paso_clasificacion,
    construir_cadena_con_enrutamiento,
)


# --- Pruebas de enrutamiento ---

def test_enrutamiento_va_a_cadena_definicion():
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "definicion"
    cadena_definicion_falsa = MagicMock()
    cadena_definicion_falsa.return_value = "respuesta de definicion"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_definicion=cadena_definicion_falsa,
    )
    resultado = cadena.invoke({
        "pregunta": "¿Qué significa la columna monto_total?",
        "contexto": "fragmento de prueba"
    })

    assert cadena_definicion_falsa.called
    assert resultado == "respuesta de definicion"


def test_enrutamiento_va_a_cadena_origen():
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "origen"
    cadena_origen_falsa = MagicMock()
    cadena_origen_falsa.return_value = "respuesta de origen"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_origen=cadena_origen_falsa,
    )
    resultado = cadena.invoke({
        "pregunta": "¿De qué tabla sale la métrica de ingresos netos?",
        "contexto": "fragmento de prueba"
    })

    assert cadena_origen_falsa.called
    assert resultado == "respuesta de origen"


def test_enrutamiento_va_a_cadena_calidad():
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "calidad"
    cadena_calidad_falsa = MagicMock()
    cadena_calidad_falsa.return_value = "respuesta de calidad"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_calidad=cadena_calidad_falsa,
    )
    resultado = cadena.invoke({
        "pregunta": "¿Está documentada la columna id_venta?",
        "contexto": "fragmento de prueba"
    })

    assert cadena_calidad_falsa.called
    assert resultado == "respuesta de calidad"


def test_enrutamiento_usa_default_ante_categoria_desconocida():
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "categoria_inventada"
    cadena_otro_falsa = MagicMock()
    cadena_otro_falsa.return_value = "respuesta por defecto"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_otro=cadena_otro_falsa,
    )
    resultado = cadena.invoke({
        "pregunta": "pregunta ambigua",
        "contexto": "fragmento de prueba"
    })

    assert cadena_otro_falsa.called
    assert resultado == "respuesta por defecto"


def test_clasificacion_normaliza_mayusculas_y_espacios():
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Definicion \n")

    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"pregunta": "¿Qué significa algo?"}
    )

    assert resultado == "definicion"