from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

from cadena_tres_pasos import construir_cadena


def test_cadena_conecta_los_tres_pasos():
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="incompleta: falta descripción en monto_total"),
        AIMessage(content="El modelo tiene documentación parcial."),
        AIMessage(content="- Agregar descripción a monto_total\n- Incluir tests"),
    ]

    cadena = construir_cadena(modelo_falso)
    resultado = cadena.invoke({"fragmento": "fragmento de prueba"})

    assert modelo_falso.call_count == 3
    assert "monto_total" in resultado