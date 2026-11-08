import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

clave = os.getenv("GEMINI_API_KEY")
nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not clave:
    raise ValueError("Falta GEMINI_API_KEY en el archivo .env")

SCHEMA = {
    "fct_revenue": {
        "descripcion": "Tabla de hechos con los ingresos diarios por ruta.",
        "columnas": {
            "route_id": "Identificador único de la ruta.",
            "fecha": "Fecha del registro de ingreso.",
            "ingresos": "Monto total de ingresos del día.",
            "pasajeros": "Cantidad de pasajeros transportados.",
        },
    },
    "dim_routes": {
        "descripcion": "Dimensión con el catálogo de rutas activas.",
        "columnas": {
            "route_id": "Identificador único de la ruta.",
            "origen": "Ciudad de origen de la ruta.",
            "destino": "Ciudad de destino de la ruta.",
            "activa": None,  # columna sin documentar
        },
    },
}


@tool
def buscar_modelo(nombre_modelo: str) -> str:
    """Busca la descripción y las columnas de un modelo del
    data warehouse a partir de su nombre.
    Usar cuando la pregunta es sobre qué hace un modelo,
    qué columnas tiene o qué significa una tabla.
    No calcula métricas ni verifica cobertura de documentación.
    """
    datos = SCHEMA.get(nombre_modelo.strip().lower())
    if not datos:
        return (
            f"No se encontró el modelo '{nombre_modelo}' "
            "en el data warehouse. Pide al usuario que "
            "revise el nombre exacto."
        )
    columnas = "\n".join(
        f"  - {col}: {desc if desc else '⚠️ sin descripción'}"
        for col, desc in datos["columnas"].items()
    )
    return (
        f"Modelo: {nombre_modelo}\n"
        f"Descripción: {datos['descripcion']}\n"
        f"Columnas:\n{columnas}"
    )


@tool
def calcular_cobertura(nombre_modelo: str) -> str:
    """Calcula qué porcentaje de columnas de un modelo del
    data warehouse tienen descripción documentada.
    Usar cuando la pregunta es sobre cobertura, calidad o
    estado de documentación de un modelo.
    No describe columnas ni explica qué hace el modelo.
    """
    datos = SCHEMA.get(nombre_modelo.strip().lower())
    if not datos:
        return (
            f"No se encontró el modelo '{nombre_modelo}' "
            "para calcular su cobertura."
        )
    total = len(datos["columnas"])
    documentadas = sum(
        1 for desc in datos["columnas"].values() if desc
    )
    porcentaje = (documentadas / total) * 100
    return (
        f"Modelo '{nombre_modelo}': "
        f"{documentadas}/{total} columnas documentadas "
        f"({porcentaje:.0f}% de cobertura)."
    )


modelo = ChatGoogleGenerativeAI(
    model=nombre_modelo,
    api_key=clave,
    temperature=0,
    timeout=20,
    max_retries=0,
)

herramientas = [buscar_modelo, calcular_cobertura]

instrucciones = (
    "Eres un asistente que ayuda a equipos de datos a entender "
    "la documentación del data warehouse. Responde en español. "
    "Para consultar qué hace un modelo o qué columnas tiene, "
    "usa buscar_modelo. "
    "Para saber qué tan documentado está un modelo, "
    "usa calcular_cobertura. "
    "No inventes modelos, columnas ni descripciones. "
    "Si el modelo no existe, informa eso sin inventar datos. "
    "Para un saludo, responde directamente sin usar herramientas."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", instrucciones),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agente = create_tool_calling_agent(
    llm=modelo,
    tools=herramientas,
    prompt=prompt,
)

ejecutor = AgentExecutor(
    agent=agente,
    tools=herramientas,
    return_intermediate_steps=True,
    verbose=False,
    max_iterations=4,
)


def probar(entrada: str):
    print("\nPREGUNTA:", entrada)

    resultado = ejecutor.invoke({"entrada": entrada})
    pasos = resultado["intermediate_steps"]

    print("\nTRAZA DE HERRAMIENTAS:")

    if not pasos:
        print("No se utilizaron herramientas.")

    for numero, (accion, observacion) in enumerate(pasos, start=1):
        print(f"\nPaso {numero}")
        print("Herramienta:", accion.tool)
        print("Argumentos:", accion.tool_input)
        print("Observación:", observacion)

    print("\nRESPUESTA FINAL:")

    salida = resultado["output"]

    if isinstance(salida, str):
        print(salida)
    else:
        texto = "\n".join(
            bloque["text"]
            for bloque in salida
            if isinstance(bloque, dict)
            and bloque.get("type") == "text"
            and isinstance(bloque.get("text"), str)
        )
        print(texto)


if __name__ == "__main__":
    print("Asistente de documentación del data warehouse")

    modelos_disponibles = ", ".join(SCHEMA.keys())
    print("Modelos disponibles:", modelos_disponibles)
    print("Escribe 'salir' para terminar.")

    while True:
        entrada = input("\nTu pregunta: ").strip()

        if entrada.lower() == "salir":
            break

        if not entrada:
            continue

        probar(entrada)