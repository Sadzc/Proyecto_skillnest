import time
from contextlib import contextmanager

from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding

from consumir_gemini import PRECIO_ENTRADA, PRECIO_SALIDA  # USD por token, centralizados
from indexar_corpus import CORPUS, preparar_chunks
from recuperacion import PROMPT_TEMPLATE, formatear_contexto

PREGUNTA = "¿Qué significa la columna route_id?"
TOKENS_SALIDA_ESTIMADOS = 60  # el largo de la respuesta no cambia por usar RAG o no


@contextmanager
def medir(tiempos, etapa):
    """Guarda en `tiempos[etapa]` los segundos que tarda el bloque `with`."""
    inicio = time.perf_counter()
    yield
    tiempos[etapa] = time.perf_counter() - inicio


def aprox_tokens(texto):
    """Heurística habitual para español/inglés: ~4 caracteres por token.
    Para el costo real usa el conteo que devuelve la API (usage_metadata)."""
    return len(texto) // 4


def calcular_costo(tokens_entrada, tokens_salida,
                   precio_entrada=PRECIO_ENTRADA, precio_salida=PRECIO_SALIDA):
    """Costo = entrada * tarifa_entrada + salida * tarifa_salida (tarifas por token)."""
    return tokens_entrada * precio_entrada + tokens_salida * precio_salida


def medir_etapas_locales(pregunta=PREGUNTA, k=3):
    """Mide embed_query y busqueda_vectorial con embeddings de prueba.

    Devuelve (tiempos_en_segundos, chunks_recuperados).
    """
    embeddings_fake = DeterministicFakeEmbedding(size=16)
    chunks, ids = preparar_chunks(CORPUS)
    vectorstore = Chroma.from_documents(
        chunks, ids=ids, embedding=embeddings_fake, collection_name="demo_costos"
    )

    tiempos = {}
    with medir(tiempos, "embed_query"):
        embeddings_fake.embed_query(pregunta)
    with medir(tiempos, "busqueda_vectorial"):
        recuperados = vectorstore.similarity_search(pregunta, k=k)
    return tiempos, recuperados


def comparar_prompt_y_costo(pregunta, chunks_recuperados,
                            tokens_salida=TOKENS_SALIDA_ESTIMADOS):
    """Compara pregunta sola vs prompt RAG completo: caracteres, tokens aprox y costo."""
    contexto, _ = formatear_contexto(chunks_recuperados)
    prompt_con_rag = PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)

    tokens_sin_rag = aprox_tokens(pregunta)
    tokens_con_rag = aprox_tokens(prompt_con_rag)
    costo_sin_rag = calcular_costo(tokens_sin_rag, tokens_salida)
    costo_con_rag = calcular_costo(tokens_con_rag, tokens_salida)
    return {
        "caracteres_pregunta": len(pregunta),
        "caracteres_prompt_rag": len(prompt_con_rag),
        "tokens_sin_rag": tokens_sin_rag,
        "tokens_con_rag": tokens_con_rag,
        "factor_texto": len(prompt_con_rag) / len(pregunta),
        "costo_sin_rag": costo_sin_rag,
        "costo_con_rag": costo_con_rag,
        "factor_costo": costo_con_rag / costo_sin_rag,
    }


def main():
    tiempos, recuperados = medir_etapas_locales()
    for etapa, segundos in tiempos.items():
        print(f"{etapa}: {segundos * 1000:.2f} ms")
    print(f"total medido: {sum(tiempos.values()) * 1000:.2f} ms")

    r = comparar_prompt_y_costo(PREGUNTA, recuperados)
    print(f"\npregunta sola: {r['caracteres_pregunta']} caracteres, "
          f"~{r['tokens_sin_rag']} tokens")
    print(f"prompt RAG completo (k={len(recuperados)}): {r['caracteres_prompt_rag']} caracteres, "
          f"~{r['tokens_con_rag']} tokens")
    print(f"factor de crecimiento del texto: {r['factor_texto']:.1f}x")

    print(f"\ncosto sin RAG: ${r['costo_sin_rag']:.6f}")
    print(f"costo con RAG: ${r['costo_con_rag']:.6f}")
    print(f"aumento del costo: {r['factor_costo']:.2f}x")


if __name__ == "__main__":
    main()