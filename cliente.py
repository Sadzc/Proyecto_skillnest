import random
import time
from typing import Any, Callable

from src.consumir_gemini import (
    PRECIO_ENTRADA,
    PRECIO_SALIDA,
    armar_peticion,
    calcular_costo,
    enviar_peticion,
    extraer_texto,
)

costo_total_sesion = 0.0


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 4,
    espera_base: float = 5,
    espera_maxima: float = 30,
) -> Any:
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera += random.uniform(0, espera * 0.1)  # jitter
            print(f"Intento {intento} de {intentos} falló. Reintentando en {espera:.1f}s...")
            time.sleep(espera)


def consultar_modelo(pregunta: str, system_instruction=None, response_schema=None) -> str:
    global costo_total_sesion
    url, cuerpo = armar_peticion(pregunta, system_instruction, response_schema)
    try:
        datos = con_reintento(lambda: enviar_peticion(url, cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")

    costo = calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    costo_total_sesion += costo
    print(f"Costo: ${costo:.6f} USD (acumulado: ${costo_total_sesion:.6f})")
    return extraer_texto(datos)


if __name__ == "__main__":
    try:
        print(consultar_modelo("¿Cuál es la capital de Chile?"))
    except (ValueError, RuntimeError) as error:
        print(f"Falló: {error}")

    for i in range(5):
        try:
            respuesta = consultar_modelo(f"Pregunta de prueba número {i}")
            print(f"Respuesta {i}: {respuesta[:40]}...")
        except (ValueError, RuntimeError) as error:
            print(f"Respuesta {i} falló definitivamente: {error}")