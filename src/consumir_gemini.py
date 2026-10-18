import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Variables
MODELO = "gemini-3.6-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"


# 1. Función: Validar y armar la petición
def armar_peticion(pregunta):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")

    api_key = os.getenv("GEMINI_API_KEY")
    url = f"{URL_BASE}{MODELO}:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": pregunta}]}]
    }
    return url, body


# 2. Función: Enviar la petición y manejar errores de red y/o formato
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body, timeout=30)
    except requests.exceptions.Timeout:
        raise RuntimeError("El servicio tardó demasiado en responder. Intenta de nuevo.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")

    if not respuesta.ok:
        raise RuntimeError(
            f"El servicio respondió con error {respuesta.status_code}. "
            "Revisa tu credencial en el archivo .env y el nombre del modelo."
        )

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")


# 3. Función: Procesar y extraer el texto generado
def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")


# 4. Función: Central
def obtener_dato_de_prueba(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)

# Ejecución
if __name__ == "__main__":
    pregunta_prueba = "Confirma en una frase corta que esta conexión funciona"
    try:
        resultado = obtener_dato_de_prueba(pregunta_prueba)
        print(resultado)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)