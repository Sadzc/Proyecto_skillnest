"""Registro de latencia y costo del flujo RAG 
Corre consultas RAG REALES (embeddings + generación con Gemini), mide el tiempo de cada
etapa por separado y toma los tokens reales de la respuesta del modelo. Cada consulta
agrega una línea (JSON Lines) a registros_latencia_costo.jsonl, en la raíz del proyecto.
"""

import argparse
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from consumir_gemini import PRECIO_ENTRADA, PRECIO_SALIDA  # USD por token
from indexar_corpus import cargar_vectorstore
from preflight import preflight_check
from recuperacion import MODELO_LLM, PROMPT_TEMPLATE, formatear_contexto

RAIZ = Path(__file__).resolve().parent.parent
RUTA_REGISTRO = RAIZ / "registros_latencia_costo.jsonl"

# Del conjunto de evaluación del Bloque 27: una respuesta corta, una con varios chunks
# relevantes y una que el corpus no responde (largo de respuesta distinto en cada una).
PREGUNTAS = [
    "cada cuanto se genera una fila en la tabla de ingresos",
    "que columnas tiene la tabla de hechos de ingresos",
    "cual es el margen de ganancia por ruta",
]


@contextmanager
def medir(tiempos, etapa):
    """Guarda en `tiempos[etapa]` los segundos que tarda el bloque `with`."""
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def calcular_costo(tokens):
    """Costo real en USD de una llamada, a partir de usage_metadata (None si no hay datos).

    La salida se toma como total - entrada, para incluir los tokens de razonamiento del
    modelo, que se cobran como salida.
    """
    if not tokens:
        return None
    entrada = tokens["input_tokens"]
    salida = tokens["total_tokens"] - entrada
    return round(entrada * PRECIO_ENTRADA + salida * PRECIO_SALIDA, 8)


def registrar_consulta(pregunta, k=3, vectorstore=None, chat_model=None):
    """Corre una consulta RAG midiendo cada etapa y devuelve el registro (dict).

    `vectorstore` y `chat_model` son opcionales: si no se pasan, se usan el índice
    persistido y Gemini. Se inyectan solo para poder probar el flujo sin API.
    """
    if vectorstore is None:
        vectorstore = cargar_vectorstore()
    if chat_model is None:
        from langchain_google_genai import ChatGoogleGenerativeAI
        chat_model = ChatGoogleGenerativeAI(model=MODELO_LLM)

    tiempos = {}

    with medir(tiempos, "embed_query"):  # red
        vector = vectorstore.embeddings.embed_query(pregunta)

    with medir(tiempos, "busqueda_vectorial"):  # local; reusa el vector, no embebe de nuevo
        chunks = vectorstore.similarity_search_by_vector(vector, k=k)

    contexto, _ = formatear_contexto(chunks)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    with medir(tiempos, "generacion"):  # red
        respuesta = chat_model.invoke(prompt)

    tokens = dict(respuesta.usage_metadata) if respuesta.usage_metadata else None
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "tiempos_ms": {etapa: round(s * 1000, 2) for etapa, s in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "tokens": tokens,
        "costo_usd": calcular_costo(tokens),
    }


def guardar_registro(registro, ruta=RUTA_REGISTRO):
    """Agrega el registro como una línea JSON (JSON Lines) al archivo."""
    with open(ruta, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Registra latencia y costo del flujo RAG.")
    parser.add_argument("pregunta", nargs="?", help="una sola pregunta (si se omite, corre la tanda)")
    parser.add_argument("--k", type=int, default=3, help="chunks a recuperar (por defecto 3)")
    args = parser.parse_args(argv)

    if not os.environ.get("GEMINI_API_KEY"):
        from dotenv import load_dotenv
        load_dotenv()
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit('Falta GEMINI_API_KEY. Defínela en tu ".env" y vuelve a ejecutar.')

    problemas = preflight_check()
    if problemas:
        raise SystemExit("Preflight con problemas:\n" + "\n".join(f" - {p}" for p in problemas))

    if args.pregunta:
        corridas = [(args.pregunta, args.k)]
    else:
        corridas = [(p, 3) for p in PREGUNTAS] + [(PREGUNTAS[0], 6)]  # misma pregunta, k=3 vs k=6

    vectorstore = cargar_vectorstore()
    for pregunta, k in corridas:
        try:
            registro = registrar_consulta(pregunta, k, vectorstore=vectorstore)
        except Exception as error:
            if "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error):
                raise SystemExit("Límite de peticiones agotado (429). Lo ya registrado quedó "
                                 "guardado; espera y vuelve a correr solo lo que falta.")
            raise
        guardar_registro(registro)
        print(json.dumps(registro, indent=2, ensure_ascii=False))

    print(f"\nRegistros agregados a {RUTA_REGISTRO.name}")


if __name__ == "__main__":
    main()