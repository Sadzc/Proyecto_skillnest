from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# SEGMENTO 1: PromptTemplate básico y cadena simple

plantilla = PromptTemplate.from_template(
    "Explica el concepto de {tema} en un párrafo, "
    "para un analista de negocio que trabaja con {contexto}."
)

# plantilla → modelo → string plano
cadena_simple = plantilla | modelo | StrOutputParser()

respuesta = cadena_simple.invoke({
    "tema": "linaje de datos",
    "contexto": "dbt y un Data Warehouse analítico"
})

print("=== Segmento 1 ===")
print(respuesta)
print(type(respuesta))
print(isinstance(respuesta, str))  # ← respuesta, no puntos
print()

# SEGMENTO 2: tres pasos por separado (verificar antes de encadenar)


fragmento_prueba = (
    "version: 2\n"
    "models:\n"
    "  - name: fact_ventas\n"
    "    description: 'Tabla de hechos de ventas.'\n"
    "    columns:\n"
    "      - name: id_venta\n"
    "        description: 'Identificador único de la venta.'\n"
    "      - name: monto_total\n"
)

# Paso 1: extraer hechos clave del fragmento de schema.yml
plantilla_extraccion = PromptTemplate.from_template(
    "Eres un data engineer senior. Lee este fragmento de schema.yml de dbt "
    "y devuelve solo los 3 hechos más importantes sobre su documentación, "
    "uno por línea, sin desarrollarlos:\n\n{fragmento}"
)
paso_extraccion = plantilla_extraccion | modelo | StrOutputParser()

# Paso 2: traducir a lenguaje simple para un analista de negocio
plantilla_simplificacion = PromptTemplate.from_template(
    "Reescribe estos puntos técnicos de dbt en lenguaje simple, "
    "sin jerga técnica, para un analista de negocio que no sabe programar:\n\n{puntos}"
)
paso_simplificacion = plantilla_simplificacion | modelo | StrOutputParser()

# Paso 3: formatear como lista de viñetas markdown lista para compartir
plantilla_formato = PromptTemplate.from_template(
    "Convierte este texto en una lista de viñetas markdown, "
    "máximo 3 líneas, sin introducción:\n\n{texto_simple}"
)
paso_formato = plantilla_formato | modelo | StrOutputParser()

print("=== Segmento 2: pasos por separado ===")

puntos = paso_extraccion.invoke({"fragmento": fragmento_prueba})
print("Paso 1 - Extracción:")
print(puntos)
print(type(puntos))
print(isinstance(puntos, str))
print()

simple = paso_simplificacion.invoke({"puntos": puntos})
print("Paso 2 - Simplificación:")
print(simple)
print(type(simple))
print(isinstance(puntos, str))
print()

formato = paso_formato.invoke({"texto_simple": simple})
print("Paso 3 - Formato:")
print(formato)
print(type(formato))
print(isinstance(puntos, str))
print()

# SEGMENTO 3: los tres pasos encadenados con |

cadena_tres_pasos = (
    plantilla_extraccion
    | modelo
    | StrOutputParser()
    | (lambda puntos: {"puntos": puntos})
    | plantilla_simplificacion
    | modelo
    | StrOutputParser()
    | (lambda texto_simple: {"texto_simple": texto_simple})
    | plantilla_formato
    | modelo
    | StrOutputParser()
)

print("=== Segmento 3: cadena completa ===")
resultado = cadena_tres_pasos.invoke({"fragmento": fragmento_prueba})
print(resultado)