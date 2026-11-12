import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit("Falta GEMINI_API_KEY en .env")

# Corpus: documentación del data warehouse (extractos del schema.yml del proyecto)
corpus = [
    "El modelo fct_revenue es la tabla de hechos con los ingresos diarios por ruta. "
    "Contiene una fila por día y por ruta activa.",
    "La columna route_id en fct_revenue es el identificador único de la ruta. "
    "Se usa para relacionar con dim_routes.",
    "La columna ingresos en fct_revenue registra el monto total de ingresos del día "
    "para esa ruta, expresado en la moneda local.",
    "La columna pasajeros en fct_revenue registra la cantidad de pasajeros "
    "transportados en esa ruta en ese día.",
    "El modelo dim_routes es la dimensión con el catálogo de rutas activas del sistema. "
    "Tiene una fila por ruta.",
    "La columna origen en dim_routes indica la ciudad de origen de la ruta. "
    "La columna destino indica la ciudad de destino.",
    "La columna activa en dim_routes existe en el modelo pero no tiene descripción "
    "documentada. Es una columna que requiere re-documentación.",
]

# Chunking recursivo — respeta párrafos, mejor para documentación
splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)
chunks = splitter.create_documents(corpus)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

try:
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="vectorstore/",
    )
except Exception as error:
    mensaje = str(error)
    if "429" in mensaje or "RESOURCE_EXHAUSTED" in mensaje:
        print("Límite de peticiones. Espera un minuto y vuelve a ejecutar.")
    elif "API key" in mensaje or "401" in mensaje or "403" in mensaje:
        print("Clave rechazada. Revisa tu .env.")
    else:
        print("Error al indexar:", type(error).__name__, mensaje)
    raise SystemExit(1)

print(f"Indexados {len(chunks)} chunks en vectorstore/")

# Verificar que quedó persistido sin recalcular embeddings
vectorstore_recargado = Chroma(
    persist_directory="vectorstore/",
    embedding_function=embeddings,
)
print(f"Verificación: {vectorstore_recargado._collection.count()} chunks en disco")