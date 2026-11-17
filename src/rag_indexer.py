"""Utilidades de clase para auditar e inspeccionar el índice RAG.

Reutiliza indexar_corpus.py (indexar, cargar, agregar, eliminar) y recuperacion.py
(formatear_contexto) en vez de duplicarlos; acá solo viven las piezas que el repo no tenía:

- verificar_integridad: auditoría local de chunks (Bloque 25), no gasta tokens.
- buscar_similares: búsqueda con distancia, para ver qué tan cerca queda cada chunk (Bloque 26).
- inspeccionar_chunks: inventario de ids + metadata + contenido en Chroma. Sirve para
  etiquetar ids_relevantes en el Bloque 27 sin adivinar qué ids existen.
"""

from indexar_corpus import (  # noqa: F401  (re-exportadas para usarlas desde aquí)
    CORPUS,
    agregar_documentos,
    cargar_vectorstore,
    eliminar_por_ids,
    indexar_corpus,
    preparar_chunks,
)
from recuperacion import formatear_contexto  # noqa: F401


def verificar_integridad(chunks, corpus_original):
    """Audita localmente que no haya chunks vacíos ni duplicados antes de gastar embeddings.

    `corpus_original` es la lista de textos de origen (list[str]).
    Lanza ValueError si hay chunks vacíos; avisa si hay duplicados.
    """
    vacios = [i for i, c in enumerate(chunks) if not c.page_content.strip()]
    textos = [c.page_content for c in chunks]
    hay_duplicados = len(textos) != len(set(textos))  # set = valores únicos

    if vacios:
        raise ValueError(f"Se detectaron chunks vacíos en los índices: {vacios}")
    if hay_duplicados:
        print("Advertencia: Se detectaron chunks duplicados en el corpus.")

    total_chars_chunks = sum(len(c.page_content) for c in chunks)
    total_chars_corpus = sum(len(d) for d in corpus_original)
    print(f"Integridad OK | Chunks: {len(chunks)} | Caracteres (corpus/chunks): "
          f"{total_chars_corpus}/{total_chars_chunks}")


def buscar_similares(vectorstore, pregunta, k=3):
    """Búsqueda semántica mostrando la distancia de cada chunk.

    Chroma devuelve distancia (L2 al cuadrado), no similitud: menor = más parecido.
    Gasta 1 llamada de embeddings (la pregunta). Devuelve [(Document, distancia), ...].
    """
    resultados = vectorstore.similarity_search_with_score(query=pregunta, k=k)
    for i, (doc, score) in enumerate(resultados, start=1):
        print(f"[Resultado {i}] id: {doc.id} | distancia: {score:.4f}")
        print(f"Contenido: {doc.page_content}")
        if doc.metadata:
            print(f"Metadata: {doc.metadata}")
    return resultados


def inspeccionar_chunks(vectorstore):
    """Inventario de lo que hay en Chroma: id, metadata y los primeros 100 caracteres.

    No gasta tokens. Úsalo antes de etiquetar ids_relevantes (Bloque 27) y para
    diagnosticar precisión/recall en 0 (ids que no coinciden, metadata faltante).
    """
    datos = vectorstore.get()  # datos["ids"], datos["documents"], datos["metadatas"]
    total = len(datos["ids"])
    print(f"--- INVENTARIO DE CHUNKS EN CHROMA (Total: {total}) ---")

    for i, (chunk_id, texto, meta) in enumerate(
        zip(datos["ids"], datos["documents"], datos["metadatas"]), start=1
    ):
        print(f"[{i}] ID: {chunk_id}")
        print(f"Fuente/Meta: {meta}")
        resumen = texto.replace("\n", " ")[:100]  # sin saltos de línea, solo 100 caracteres
        print(f"Contenido: {resumen}...")
    return datos


if __name__ == "__main__":
    # 1. Auditoría local del corpus del proyecto (sin API)
    chunks, ids = preparar_chunks(CORPUS)
    verificar_integridad(chunks, [e["texto"] for e in CORPUS])

    # 2. Inventario del índice persistido (solo lectura, no gasta tokens)
    vs = cargar_vectorstore()
    inspeccionar_chunks(vs)

    # 3. Búsqueda con distancias (gasta 1 embedding de la pregunta)
    # buscar_similares(vs, "¿Qué significa la columna route_id?", k=3)