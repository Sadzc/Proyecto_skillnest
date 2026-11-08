import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
from langchain_core.callbacks import BaseCallbackHandler
from prompts.banco import ROL, FORMATO, SCHEMA_YML


logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="error.log",
    filemode="a",
    encoding="utf-8",
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# --- Clasificación de intención ---
# Reutiliza el mismo prompt de clasificar_intencion del banco.py

plantilla_clasificacion = PromptTemplate.from_template(
    ROL +
    "Clasifica qué quiere saber el usuario sobre el Data Warehouse. "
    "Responde solo con una palabra: "
    "'definicion' si pregunta qué significa algo, "
    "'origen' si pregunta de qué tabla o modelo sale un dato, "
    "'calidad' si pregunta si algo está documentado o probado, "
    "'otro' en los demás casos.\n\n"
    "Pregunta: {pregunta}"
)

paso_clasificacion = (
    plantilla_clasificacion
    | modelo
    | StrOutputParser()
    | (lambda texto: texto.strip().lower())
)

# --- Tres rutas según la intención ---

cadena_definicion = (
    PromptTemplate.from_template(
        ROL +
        "El usuario quiere saber qué significa algo en el Data Warehouse. "
        "Responde usando solo la información del fragmento de schema.yml. "
        "Si no está en el fragmento, dilo claramente.\n\n"
        "Fragmento:\n{contexto}\n\n"
        "Pregunta: {pregunta}"
    )
    | modelo
    | StrOutputParser()
)

cadena_origen = (
    PromptTemplate.from_template(
        ROL +
        "El usuario quiere saber de qué tabla o modelo sale un dato o métrica. "
        "Traza el origen usando solo la información del fragmento de schema.yml. "
        "Si no está en el fragmento, dilo claramente.\n\n"
        "Fragmento:\n{contexto}\n\n"
        "Pregunta: {pregunta}"
    )
    | modelo
    | StrOutputParser()
)

cadena_calidad = (
    PromptTemplate.from_template(
        ROL +
        "El usuario quiere saber si algo está documentado o tiene tests definidos. "
        "Revisa el fragmento de schema.yml y responde si hay description y/o tests. "
        "Si falta documentación, indícalo explícitamente.\n\n"
        "Fragmento:\n{contexto}\n\n"
        "Pregunta: {pregunta}"
    )
    | modelo
    | StrOutputParser()
)

cadena_otro = (
    PromptTemplate.from_template(
        ROL +
        "Responde esta pregunta general sobre el Data Warehouse "
        "usando solo la información disponible en el fragmento.\n\n"
        "Fragmento:\n{contexto}\n\n"
        "Pregunta: {pregunta}"
    )
    | modelo
    | StrOutputParser()
)

# --- Bifurcación ---

bifurcacion = RunnableBranch(
    (lambda x: x["clasificacion"] == "definicion", cadena_definicion),
    (lambda x: x["clasificacion"] == "origen", cadena_origen),
    (lambda x: x["clasificacion"] == "calidad", cadena_calidad),
    cadena_otro  # ruta por defecto para "otro" o clasificaciones inesperadas
)

cadena_con_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificacion)
    | bifurcacion
)

# --- Fallback y manejo de errores ---

def fallback_con_log(x):
    logger.warning(
        "Cadena principal falló. Activando respuesta genérica. Error: %s",
        x.get("error")
    )
    return (
        "No pude procesar tu pregunta en este momento. "
        "Intenta de nuevo o reformula la consulta."
    )

respuesta_generica = RunnableLambda(fallback_con_log)

cadena_robusta = cadena_con_enrutamiento.with_fallbacks(
    [respuesta_generica], exception_key="error"
)

class CapturadorError(BaseCallbackHandler):
    def on_chain_error(self, error: BaseException, **kwargs):
        logger.warning(
            "Error capturado antes del fallback: [%s] -> %s",
            type(error).__name__,
            error
        )

manejador_error = CapturadorError()

# Reemplaza la actual procesar_pregunta por esta versión
def procesar_pregunta(cadena, pregunta: str, contexto: str) -> str:
    try:
        return cadena.invoke(
            {"pregunta": pregunta, "contexto": contexto},
            config={"callbacks": [manejador_error]}
        )
    except Exception as error:
        logger.error("Error procesando pregunta: %s", error)
        return "No pudimos procesar tu pregunta en este momento. Intenta de nuevo más tarde."
    
def construir_paso_clasificacion(modelo):
    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_definicion=None,
    cadena_origen=None,
    cadena_calidad=None,
    cadena_otro=None,
):
    _cadena_definicion = cadena_definicion or RunnablePassthrough()
    _cadena_origen = cadena_origen or RunnablePassthrough()
    _cadena_calidad = cadena_calidad or RunnablePassthrough()
    _cadena_otro = cadena_otro or RunnablePassthrough()

    bifurcacion = RunnableBranch(
        (lambda x: x["clasificacion"] == "definicion", _cadena_definicion),
        (lambda x: x["clasificacion"] == "origen", _cadena_origen),
        (lambda x: x["clasificacion"] == "calidad", _cadena_calidad),
        _cadena_otro,
    )
    return (
        RunnablePassthrough.assign(clasificacion=paso_clasificacion)
        | bifurcacion
    )

def construir_cadena_robusta(cadena):
    return cadena.with_fallbacks([respuesta_generica])

def construir_cadena_robusta(cadena):
    return cadena.with_fallbacks([respuesta_generica], exception_key="error")

if __name__ == "__main__":
    preguntas_prueba = [
        "¿Qué significa la columna monto_total?",
        "¿De qué tabla sale la métrica de ingresos netos?",
        "¿Está documentada la columna id_venta?",
    ]

    for pregunta in preguntas_prueba:
        print(f"\nPregunta: {pregunta}")
        print(procesar_pregunta(cadena_robusta, pregunta, SCHEMA_YML))