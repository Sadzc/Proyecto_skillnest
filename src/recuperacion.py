import re

from dotenv import load_dotenv

from indexar_corpus import COLLECTION, PERSIST_DIR, cargar_vectorstore

load_dotenv()

MODELO_LLM = "gemini-3.6-flash"

PROMPT_TEMPLATE = """Eres un data engineer senior que trabaja con un Data Warehouse analítico. \
Responde la pregunta usando SOLO el contexto de abajo. Cita la fuente de cada afirmacion \
con su numero entre corchetes, como [1]. Si el contexto no alcanza para responder, dilo \
explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""


def etiqueta_fuente(doc):
    """'schema.yml > fct_revenue.route_id'. Todos los chunks comparten 'schema.yml',
    así que doc_id es lo que permite verificar a qué modelo/columna se refiere la cita."""
    fuente = doc.metadata.get("fuente")
    if not fuente:
        return "desconocida"
    doc_id = doc.metadata.get("doc_id")
    return f"{fuente} > {doc_id}" if doc_id else fuente


def formatear_contexto(chunks_recuperados):
    """Contexto numerado [1], [2]... y mapa numero -> fuente para reconstruir la cita."""
    lineas = []
    citas = {}
    for i, doc in enumerate(chunks_recuperados, start=1):
        lineas.append(f"[{i}] {doc.page_content}")
        citas[i] = etiqueta_fuente(doc)
    return "\n\n".join(lineas), citas


def construir_prompt(pregunta, k=3, vectorstore=None):
    """Recupera los k chunks más relevantes y arma el prompt. Devuelve (prompt, citas).

    `vectorstore` es opcional: si no se pasa, se reconecta al índice persistido.
    """
    if vectorstore is None:
        vectorstore = cargar_vectorstore(PERSIST_DIR, COLLECTION)
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    chunks = retriever.invoke(pregunta)
    contexto, citas = formatear_contexto(chunks)
    return PROMPT_TEMPLATE.format(contexto=contexto, pregunta=pregunta), citas


def resolver_citas(respuesta, citas):
    """Mapea cada [N] o [N, M, ...] de la respuesta a su fuente; marca como inválidas las alucinadas."""
    indices = set()
    for grupo in re.findall(r"\[(\d+(?:\s*,\s*\d+)*)\]", respuesta):
        indices.update(int(n) for n in re.findall(r"\d+", grupo))
    return {i: citas.get(i, "Cita invalida / no encontrada") for i in sorted(indices)}


def responder(pregunta, k=3):
    """Prompt -> Gemini 3.6 Flash. Gasta 1 llamada de embeddings + 1 de generación."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    prompt, citas = construir_prompt(pregunta, k)
    texto = ChatGoogleGenerativeAI(model=MODELO_LLM).invoke(prompt).text
    return texto, resolver_citas(texto, citas)


if __name__ == "__main__":
    preguntas = [
        "¿Qué significa la columna route_id?",
        "¿Cuál es el margen de ganancia por ruta?",  # el corpus no la responde
    ]
    for pregunta in preguntas:
        prompt, citas = construir_prompt(pregunta)
        print(prompt)
        print(citas)
        print("-" * 60)