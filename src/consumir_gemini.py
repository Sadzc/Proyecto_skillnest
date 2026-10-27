import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

# Variables
MODELO = "gemini-3.6-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
PRECIO_ENTRADA = 0.00000075
PRECIO_SALIDA = 0.00000375


# 1. Función: Validar y armar la petición
def armar_peticion(pregunta, system_instruction=None, response_schema=None):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env")

    url = f"{URL_BASE}{MODELO}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}

    if system_instruction is not None:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return url, body


# 2. Función: Enviar la petición y manejar errores de red y/o formato
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body, timeout=60)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise TimeoutError("No se pudo contactar al servicio. Puede ser momentáneo.")

    if not respuesta.ok:
        try:
            detalle = respuesta.json().get("error", {}).get("message", "")
        except (ValueError, AttributeError):
            detalle = ""
        mensaje = f"Error {respuesta.status_code}: {detalle}"

        if respuesta.status_code in (401, 403) or (
            respuesta.status_code == 400 and "API key" in detalle
        ):
            raise ValueError(mensaje)
        if respuesta.status_code == 429 or respuesta.status_code >= 500:
            raise TimeoutError(mensaje)
        raise RuntimeError(mensaje)

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

# 3. Función: Procesar y extraer el texto generado
def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


# 4. Función: Limpiar e interpretar la respuesta como JSON y validar su estructura
#    Contrato de todos los prompts del banco: {"categoria": str, "confianza": 0 a 1}
def parsear_respuesta_json(texto, categorias_permitidas=None):
    limpio = texto.strip()
    limpio = re.sub(r"^```(?:json)?\s*", "", limpio)
    limpio = re.sub(r"\s*```$", "", limpio)

    try:
        datos = json.loads(limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")

    if not isinstance(datos, dict):
        raise ValueError("Se esperaba un objeto JSON.")

    if set(datos) != {"categoria", "confianza"}:
        raise ValueError("El JSON debe tener solo las claves 'categoria' y 'confianza'.")

    if not isinstance(datos["categoria"], str):
        raise ValueError("'categoria' debe ser texto.")

    if categorias_permitidas is not None and datos["categoria"] not in categorias_permitidas:
        raise ValueError(f"Categoría no permitida: {datos['categoria']!r}.")

    confianza = datos["confianza"]
    if type(confianza) not in (int, float) or not 0 <= confianza <= 1:
        raise ValueError("'confianza' debe ser un número entre 0 y 1.")

    return datos


# 5. Función: Calcular el costo de la petición
def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    tokens_salida = uso["candidatesTokenCount"]
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)  # puede no venir
    return (tokens_entrada * precio_entrada) + ((tokens_salida + tokens_razonamiento) * precio_salida)


# 6. Función: Central
def obtener_dato_de_prueba(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    costo = calcular_costo(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    print(f"Costo de la petición: ${costo:.6f} USD")
    return extraer_texto(datos)


# Ejecución
if __name__ == "__main__":
    pregunta_prueba = "Confirma en una frase corta que esta conexión funciona"
    try:
        resultado = obtener_dato_de_prueba(pregunta_prueba)
        print(resultado)
    except (ValueError, RuntimeError, KeyError, TimeoutError) as error:
        print("No se pudo completar la operación:", error)