import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
ARCHIVO_SALIDA = "respuestas_completas.md"

# 1. Función: Validar y armar la petición
def armar_peticion(pregunta, modelo):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("No se encontró GEMINI_API_KEY en el archivo .env")

    url = f"{URL_BASE}{modelo}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body

# 2. Función: Enviar la petición, con reintentos y errores claros.
#    Devuelve (datos, latencia) midiendo solo el intento exitoso.
def enviar_peticion(url, body, reintentos=4):
    for intento in range(reintentos):
        ultimo = intento == reintentos - 1
        inicio = time.perf_counter()
        try:
            respuesta = requests.post(url, json=body, timeout=60)
        except requests.exceptions.Timeout:
            if ultimo:
                raise RuntimeError("El servicio tardó demasiado en responder.")
            time.sleep(2 ** intento * 5)
            continue
        except requests.exceptions.ConnectionError:
            raise RuntimeError("No se pudo conectar con el servicio.")
        latencia = time.perf_counter() - inicio

        if respuesta.status_code in (429, 500, 503) and not ultimo:
            time.sleep(2 ** intento * 5)  # 5s, 10s, 20s...
            continue

        if not respuesta.ok:
            try:
                detalle = respuesta.json().get("error", {}).get("message", "")
            except ValueError:
                detalle = respuesta.text[:200]
            raise RuntimeError(f"Error {respuesta.status_code}: {detalle}")

        try:
            return respuesta.json(), latencia
        except ValueError:
            raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

# 3. Función: Procesar y extraer el texto
def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")

# 4. Función para calcular el costo
def calcular_costo(datos, precio_entrada, precio_salida):
    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso.get("promptTokenCount", 0)
        tokens_salida = uso.get("candidatesTokenCount", 0)
        tokens_razonamiento = uso.get("thoughtsTokenCount", 0)
        return (tokens_entrada * precio_entrada) + ((tokens_salida + tokens_razonamiento) * precio_salida)
    except KeyError:
        return 0.0

# 5. Función Central de ejecución
def ejecutar_prueba(pregunta, modelo, precio_entrada, precio_salida):
    url, body = armar_peticion(pregunta, modelo)
    datos, latencia = enviar_peticion(url, body)
    costo = calcular_costo(datos, precio_entrada, precio_salida)
    respuesta = extraer_texto(datos)
    return latencia, costo, respuesta

# Ejecución Principal
if __name__ == "__main__":
    preguntas_prueba = [
        "Explica en una sola frase breve por qué el archivo schema.yml de dbt es clave para documentar un Data Warehouse.",
        "Escribe un ejemplo básico de un archivo schema.yml en dbt que documente una tabla llamada 'fact_ventas' con dos columnas: 'id_venta' y 'monto_total'.",
        "Si un analista de negocio pregunta '¿De qué tabla sale la métrica de ingresos netos?', explica en tres pasos cómo buscarías esa respuesta dentro de las descripciones de modelos dbt.",
        "Explica qué es un 'linaje de datos' (data lineage) en dbt, usando un lenguaje muy sencillo y una analogía para un analista de negocio que no sabe programar."
    ]

    modelos_a_comparar = {
        "gemini-3.5-flash": {"in": 0.000000075, "out": 0.00000030},
        "gemini-3.6-flash": {"in": 0.0000000375, "out": 0.00000015},
        "gemini-3.8-flash": {"in": 0.00000125, "out": 0.00000500}
    }

    resultados = {m: [] for m in modelos_a_comparar}

    # Empieza el archivo de cero en cada corrida (así no se acumulan corridas)
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(f"# Respuestas completas ({time.strftime('%Y-%m-%d %H:%M')})\n\n")

    print("=== INICIANDO COMPARATIVA DE MODELOS ===\n")

    for nombre_modelo, precios in modelos_a_comparar.items():
        print("-" * 50)
        print(f"Evaluando Modelo: {nombre_modelo}")
        print("-" * 50)

        for i, pregunta in enumerate(preguntas_prueba, 1):
            try:
                lat, costo, resp = ejecutar_prueba(
                    pregunta, nombre_modelo, precios["in"], precios["out"]
                )
                resultados[nombre_modelo].append((i, lat, costo))

                print(f"  [Pregunta {i}]")
                print(f"    - Latencia:  {lat:.2f} segundos")
                print(f"    - Costo:     ${costo:.6f} USD")
                print(f"    - Respuesta:\n{resp.strip()}\n")

                with open(ARCHIVO_SALIDA, "a", encoding="utf-8") as f:
                    f.write(f"## {nombre_modelo} - Pregunta {i}\n\n")
                    f.write(f"**Pregunta:** {pregunta}\n\n")
                    f.write(f"Latencia: {lat:.2f} s | Costo: ${costo:.6f} USD\n\n")
                    f.write(f"{resp.strip()}\n\n---\n\n")
            except Exception as e:
                print(f"  [Pregunta {i}] Falló: {e}\n")
                with open(ARCHIVO_SALIDA, "a", encoding="utf-8") as f:
                    f.write(f"## {nombre_modelo} - Pregunta {i}\n\nFalló: {e}\n\n---\n\n")

            # Pausa para evitar el Error 429 de Rate Limit
            time.sleep(15)
        print()

    # Resumen final
    print("=" * 50)
    print("RESUMEN")
    print("=" * 50)
    for nombre_modelo, filas in resultados.items():
        if not filas:
            print(f"{nombre_modelo}: sin respuestas exitosas")
            continue
        n = len(filas)
        lat_prom = sum(f[1] for f in filas) / n
        costo_prom = sum(f[2] for f in filas) / n
        preguntas_ok = [f[0] for f in filas]
        print(f"{nombre_modelo}: {n}/{len(preguntas_prueba)} OK (preguntas {preguntas_ok}) | "
              f"latencia prom. {lat_prom:.2f} s | costo prom. ${costo_prom:.6f} USD")