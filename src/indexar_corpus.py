import os
import time
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# Misma ruta y mismo nombre de colección en indexación y consulta (guía de troubleshooting).
# Ruta anclada al repo, no al directorio desde donde se ejecuta el script.
PERSIST_DIR = str(Path(__file__).resolve().parent.parent / "vectorstore")
COLLECTION = "docs_dwh"
MODELO_EMBEDDINGS = "models/gemini-embedding-001"

# Corpus: extractos de la documentación del data warehouse (schema.yml).
# Cada entrada lleva su metadata para que el Gate 2 pueda CITAR la fuente.
CORPUS = [
    {"texto": "El modelo fct_revenue es la tabla de hechos con los ingresos diarios por ruta. "
              "Contiene una fila por día y por ruta activa.",
     "fuente": "schema.yml", "modelo": "fct_revenue"},
    {"texto": "La columna route_id en fct_revenue es el identificador único de la ruta. "
              "Se usa para relacionar con dim_routes.",
     "fuente": "schema.yml", "modelo": "fct_revenue", "columna": "route_id"},
    {"texto": "La columna ingresos en fct_revenue registra el monto total de ingresos del día "
              "para esa ruta, expresado en la moneda local.",
     "fuente": "schema.yml", "modelo": "fct_revenue", "columna": "ingresos"},
    {"texto": "La columna pasajeros en fct_revenue registra la cantidad de pasajeros "
              "transportados en esa ruta en ese día.",
     "fuente": "schema.yml", "modelo": "fct_revenue", "columna": "pasajeros"},
    {"texto": "El modelo dim_routes es la dimensión con el catálogo de rutas activas del sistema. "
              "Tiene una fila por ruta.",
     "fuente": "schema.yml", "modelo": "dim_routes"},
    {"texto": "La columna origen en dim_routes indica la ciudad de origen de la ruta. "
              "La columna destino indica la ciudad de destino.",
     "fuente": "schema.yml", "modelo": "dim_routes", "columna": "origen"},
    {"texto": "La columna activa en dim_routes existe en el modelo pero no tiene descripción "
              "documentada. Es una columna que requiere re-documentación.",
     "fuente": "schema.yml", "modelo": "dim_routes", "columna": "activa"},
]


def con_reintentos(operacion, max_intentos=4, espera_inicial=5):
    """Repite la operación solo ante 429/RESOURCE_EXHAUSTED, con espera creciente."""
    espera = espera_inicial
    for intento in range(1, max_intentos + 1):
        try:
            return operacion()
        except Exception as error:
            mensaje = str(error)
            es_limite = "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje
            if not es_limite or intento == max_intentos:
                raise
            print(f"Límite de peticiones. Reintento {intento} de {max_intentos - 1} en {espera} s...")
            time.sleep(espera)
            espera *= 2


def _doc_id(entrada):
    """Id estable por documento de origen: 'fct_revenue.route_id' o 'dim_routes'."""
    columna = entrada.get("columna")
    return f"{entrada['modelo']}.{columna}" if columna else entrada["modelo"]


def preparar_chunks(corpus, chunk_size=400, chunk_overlap=20):
    """Pasos 1-2 (local, sin API): parte el corpus y genera ids explícitos y metadata.

    Devuelve (chunks, ids). Los ids son predecibles (<doc_id>_<n>), así se pueden
    reemplazar o borrar chunks puntuales sin reindexar todo.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    textos = [e["texto"] for e in corpus]
    metadatas = [{**{k: v for k, v in e.items() if k != "texto"}, "doc_id": _doc_id(e)} for e in corpus]
    chunks = splitter.create_documents(textos, metadatas=metadatas)

    contador = defaultdict(int)
    ids = []
    for chunk in chunks:
        doc_id = chunk.metadata["doc_id"]
        ids.append(f"{doc_id}_{contador[doc_id]}")
        contador[doc_id] += 1
    return chunks, ids


def _embeddings():
    return GoogleGenerativeAIEmbeddings(model=MODELO_EMBEDDINGS)


def indexar_corpus(corpus=CORPUS, persist_directory=PERSIST_DIR, collection_name=COLLECTION,
                   chunk_size=400, chunk_overlap=20):
    """Pasos 1-4. Si cambias chunk_size, estrategia o modelo: borra la carpeta y reindexa."""
    chunks, ids = preparar_chunks(corpus, chunk_size, chunk_overlap)
    vectorstore = con_reintentos(lambda: Chroma.from_documents(
        documents=chunks,
        ids=ids,
        embedding=_embeddings(),
        collection_name=collection_name,
        persist_directory=persist_directory,
    ))
    print(f"Indexados {len(chunks)} chunks en {persist_directory}")
    return vectorstore


def cargar_vectorstore(persist_directory=PERSIST_DIR, collection_name=COLLECTION):
    """Paso 5: reconecta al índice existente. No recalcula nada ni gasta tokens."""
    return Chroma(collection_name=collection_name, embedding_function=_embeddings(),
                  persist_directory=persist_directory)


def agregar_documentos(vectorstore, corpus_nuevo, chunk_size=400, chunk_overlap=20):
    """Agrega documentos nuevos (solo embebe los nuevos). Mismo id -> reemplaza ese chunk."""
    chunks, ids = preparar_chunks(corpus_nuevo, chunk_size, chunk_overlap)
    con_reintentos(lambda: vectorstore.add_documents(chunks, ids=ids))
    print(f"Agregados {len(chunks)} chunks: {ids}")


def eliminar_por_ids(vectorstore, ids):
    vectorstore.delete(ids=ids)


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit('Falta GEMINI_API_KEY. Defínela en tu ".env" y vuelve a ejecutar.')
    try:
        indexar_corpus()
    except Exception as error:
        mensaje = str(error)
        if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
            print("Límite de peticiones agotado tras los reintentos. Espera un minuto y vuelve a ejecutar.")
        elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
            print('La API rechazó tu clave. Revisa GEMINI_API_KEY en tu ".env".')
        else:
            print("Error al indexar:", type(error).__name__)
        print("Detalle técnico:", mensaje)
        raise SystemExit(1)

    recargado = cargar_vectorstore()  # verificación de persistencia, sin recalcular embeddings
    print(f"Verificación: {recargado._collection.count()} chunks en disco")