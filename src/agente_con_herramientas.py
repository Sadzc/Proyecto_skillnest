import os
import queue
import threading
import json
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

load_dotenv()

clave = os.getenv("GEMINI_API_KEY")
nombre_modelo = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

if not clave:
    raise ValueError("Falta GEMINI_API_KEY en el archivo .env")

modelo = ChatGoogleGenerativeAI(
    model=nombre_modelo,
    api_key=clave,
    temperature=0,
    timeout=60,
    max_retries=3,
)

# Base de Datos (simulación del schema.yml del DWH)
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

# Persistencia y Análisis de Trazabilidad
def registrar_traza(session_id: str, entrada: str, resultado: dict) -> None:
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado.get("output", "")
    }
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trazas_agente.jsonl"), "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def marcar_repeticiones_sospechosas(
    archivo: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "trazas_agente.jsonl"),
) -> None:
    """Recorre un archivo de trazas y marca las sesiones donde la misma
    herramienta se invocó varias veces seguidas: candidato a revisar a mano,
    no una conclusión definitiva."""
    try:
        with open(archivo, encoding="utf-8") as f:
            registros = [json.loads(linea) for linea in f]
    except FileNotFoundError:
        print(
            f"No se encontró '{archivo}'. Corre "
            "registrar_traza al menos una vez antes "
            "de revisar repeticiones."
        )
        return

    for registro in registros:
        herramientas_usadas = [
            a["herramienta"]
            for a in registro.get("acciones", [])
        ]
        for i in range(1, len(herramientas_usadas)):
            if herramientas_usadas[i] == herramientas_usadas[i - 1]:
                print(
                    f"Revisar: {registro['session_id']} usó "
                    f"'{herramientas_usadas[i]}' dos veces seguidas"
                )
                break

# Auditoría / Human in the Loop
registro_aprobaciones = []

def esperar_aprobacion(mensaje: str, tiempo_limite_segundos: int = 15) -> bool:
    cola_respuesta = queue.Queue()

    def pedir_entrada():
        try:
            texto = input(mensaje)
            cola_respuesta.put(texto.strip().lower())
        except (EOFError, KeyboardInterrupt):
            cola_respuesta.put("")

    hilo = threading.Thread(target=pedir_entrada, daemon=True)
    hilo.start()

    try:
        respuesta = cola_respuesta.get(timeout=tiempo_limite_segundos)
        return respuesta == "s"
    except queue.Empty:
        print("Tiempo de espera agotado. Solicitud denegada por timeout.")
        return False

def registrar_aprobacion(herramienta: str, argumentos: dict, aprobado: bool) -> None:
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "fecha_hora": datetime.now().isoformat()
    })

# Esquemas de Validación (args_schema)
class ArgumentosBusquedaColumna(BaseModel):
    """
    Esquema para buscar una columna específica dentro de un modelo del DWH.
    Documenta y valida cada argumento campo por campo ante el LLM.
    """
    nombre_modelo: str = Field(
        description=(
            "Nombre del modelo del data warehouse donde buscar la columna, "
            "por ejemplo 'fct_revenue' o 'dim_routes'."
        )
    )
    nombre_columna: str = Field(
        description=(
            "Nombre exacto de la columna a buscar dentro del modelo, "
            "por ejemplo 'ingresos' o 'route_id'."
        )
    )

# Herramientas
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


@tool(args_schema=ArgumentosBusquedaColumna)
def buscar_columna_en_modelo(nombre_modelo: str, nombre_columna: str) -> str:
    """Busca la descripción de una columna específica dentro de un modelo
    del data warehouse. Usar cuando la pregunta es sobre qué significa
    o qué contiene una columna en particular dentro de una tabla.
    Requiere conocer tanto el modelo como el nombre exacto de la columna.
    """
    datos = SCHEMA.get(nombre_modelo.strip().lower())
    if not datos:
        return (
            f"No se encontró el modelo '{nombre_modelo}' "
            "en el data warehouse."
        )
    columna_key = nombre_columna.strip().lower()
    columnas = datos["columnas"]

    # Buscar sin importar mayúsculas/minúsculas
    match = next(
        (col for col in columnas if col.lower() == columna_key), None
    )
    if match is None:
        disponibles = ", ".join(columnas.keys())
        return (
            f"No se encontró la columna '{nombre_columna}' "
            f"en el modelo '{nombre_modelo}'. "
            f"Columnas disponibles: {disponibles}."
        )
    desc = columnas[match]
    if desc is None:
        return (
            f"La columna '{match}' en '{nombre_modelo}' "
            "existe pero no tiene descripción documentada. ⚠️"
        )
    return (
        f"Columna '{match}' en modelo '{nombre_modelo}':\n"
        f"  {desc}"
    )


@tool
def solicitar_redocumentacion(nombre_modelo: str, motivo: str) -> str:
    """Solicita que el equipo de Data Engineering re-documente un modelo
    del data warehouse. Acción irreversible: abre un ticket en el sistema
    de seguimiento. Requiere aprobación humana antes de ejecutarse.
    Usar solo cuando hay columnas sin descripción o documentación desactualizada.
    """
    mensaje = (
        f"\n[SUPERVISIÓN REQUERIDA] Se va a abrir un ticket para re-documentar "
        f"el modelo '{nombre_modelo}'.\nMotivo: {motivo}\n"
        f"¿Desea aprobar? (s/n): "
    )

    aprobado = esperar_aprobacion(mensaje, tiempo_limite_segundos=15)

    registrar_aprobacion(
        herramienta="solicitar_redocumentacion",
        argumentos={"nombre_modelo": nombre_modelo, "motivo": motivo},
        aprobado=aprobado
    )

    if not aprobado:
        return (
            "Solicitud de re-documentación no aprobada por el supervisor "
            "o cancelada por timeout."
        )

    return (
        f"Ticket de re-documentación abierto con éxito para el modelo "
        f"'{nombre_modelo}'. Motivo registrado: {motivo}"
    )


# Listado de herramientas
herramientas = [buscar_modelo, calcular_cobertura, buscar_columna_en_modelo, solicitar_redocumentacion]

# Gestión de historial en memoria
historiales = {}

def obtener_historial(session_id: str):
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]

# Construcción del agente
instrucciones = (
    "Eres un asistente que ayuda a equipos de datos a entender "
    "la documentación del data warehouse. Responde en español. "
    "Para consultar qué hace un modelo o qué columnas tiene, usa buscar_modelo. "
    "Para saber qué tan documentado está un modelo, usa calcular_cobertura. "
    "Para buscar qué significa una columna específica dentro de un modelo, "
    "usa buscar_columna_en_modelo. "
    "Para solicitar que se re-documente un modelo con problemas, "
    "usa solicitar_redocumentacion. "
    "No inventes modelos, columnas ni descripciones. "
    "Si el modelo no existe, informa eso sin inventar datos. "
    "Para un saludo, responde directamente sin usar herramientas."
)

prompt_agente = ChatPromptTemplate.from_messages([
    ("system", instrucciones),
    MessagesPlaceholder("chat_history"),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True,
    return_intermediate_steps=True,
    max_iterations=4,
)

# Limpiar output cuando el modelo devuelve lista en vez de string
limpiar_salida = RunnableLambda(
    lambda d: {
        **d,
        "output": (
            d["output"][0]["text"]
            if isinstance(d.get("output"), list)
            else d.get("output")
        )
    }
)

cadena_agente = ejecutor_agente | limpiar_salida

# Agente con memoria
agente_con_memoria = RunnableWithMessageHistory(
    cadena_agente,
    obtener_historial,
    input_messages_key="entrada",
    history_messages_key="chat_history",
    output_messages_key="output",
)


# Ejecución
if __name__ == "__main__":
    # Pausa entre preguntas: el free tier de Gemini permite 5 llamadas por
    # minuto y cada pregunta al agente usa 2 (elegir herramienta + responder).
    PAUSA_SEGUNDOS = 30

    modelos_disponibles = ", ".join(SCHEMA.keys())
    print("Asistente de documentación del data warehouse")
    print("Modelos disponibles:", modelos_disponibles)

    # Prueba 1: memoria entre turnos (mismo session_id)
    print("\n=== Prueba 1: memoria entre turnos ===")
    config1 = {"configurable": {"session_id": "analista_001"}}

    entrada1 = "¿Qué columnas tiene el modelo fct_revenue?"
    resultado1 = agente_con_memoria.invoke({"entrada": entrada1}, config1)
    print("Turno 1:", resultado1["output"])
    registrar_traza("analista_001", entrada1, resultado1)
    time.sleep(PAUSA_SEGUNDOS)

    entrada2 = "¿Y ese mismo modelo, qué cobertura de documentación tiene?"
    resultado2 = agente_con_memoria.invoke({"entrada": entrada2}, config1)
    print("Turno 2:", resultado2["output"])
    registrar_traza("analista_001", entrada2, resultado2)
    time.sleep(PAUSA_SEGUNDOS)

    # Prueba 2: args_schema (buscar columna específica)
    print("\n=== Prueba 2: buscar columna con args_schema ===")
    config2 = {"configurable": {"session_id": "analista_002"}}

    entrada3 = "¿Qué significa la columna 'activa' en el modelo dim_routes?"
    resultado3 = agente_con_memoria.invoke({"entrada": entrada3}, config2)
    print("Turno 3:", resultado3["output"])
    registrar_traza("analista_002", entrada3, resultado3)
    time.sleep(PAUSA_SEGUNDOS)

    # Prueba 3: aislamiento de sesiones
    print("\n=== Prueba 3: aislamiento de sesiones ===")
    config3 = {"configurable": {"session_id": "analista_003"}}
    entrada4 = "¿De qué modelo te pregunté antes?"
    resultado4 = agente_con_memoria.invoke({"entrada": entrada4}, config3)
    print("Turno 4 (sesión nueva, no debería saber):", resultado4["output"])
    time.sleep(PAUSA_SEGUNDOS)

    # Prueba 4: human-in-the-loop
    print("\n=== Prueba 4: solicitar re-documentación ===")
    config4 = {"configurable": {"session_id": "analista_004"}}
    entrada5 = (
        "El modelo dim_routes tiene columnas sin documentar. "
        "Por favor solicita que lo re-documenten."
    )
    resultado5 = agente_con_memoria.invoke({"entrada": entrada5}, config4)
    print("Turno 5:", resultado5["output"])
    registrar_traza("analista_004", entrada5, resultado5)
    print("\nRegistros de aprobaciones:")
    for r in registro_aprobaciones:
        print(r)

    # Revisión de trazas: marcar repeticiones sospechosas
    print("\n=== Revisión de trazas ===")
    marcar_repeticiones_sospechosas()