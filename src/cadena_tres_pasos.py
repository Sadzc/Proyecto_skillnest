from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def construir_cadena(modelo):
    # Paso 1: clasificar el estado de documentación del fragmento
    plantilla_clasificar = PromptTemplate.from_template(
        "Eres un data engineer senior. Lee este fragmento de schema.yml de dbt "
        "y clasifica su estado de documentación en una sola palabra: "
        "'completa', 'incompleta' o 'sin_documentar'. "
        "Luego explica en una línea por qué.\n\n{fragmento}"
    )

    # Paso 2: redactar un diagnóstico legible para el equipo
    plantilla_diagnostico = PromptTemplate.from_template(
        "Basándote en esta clasificación de documentación de dbt:\n\n{clasificacion}\n\n"
        "Redacta un diagnóstico breve (2-3 oraciones) en lenguaje simple, "
        "para un analista de negocio, explicando qué está bien y qué falta."
    )

    # Paso 3: sugerir mejoras concretas y accionables
    plantilla_mejoras = PromptTemplate.from_template(
        "Dado este diagnóstico sobre la documentación de un modelo dbt:\n\n{diagnostico}\n\n"
        "Lista máximo 3 mejoras concretas y accionables en formato de viñetas markdown, "
        "sin introducción."
    )

    cadena = (
        plantilla_clasificar
        | modelo
        | StrOutputParser()
        | (lambda clasificacion: {"clasificacion": clasificacion})
        | plantilla_diagnostico
        | modelo
        | StrOutputParser()
        | (lambda diagnostico: {"diagnostico": diagnostico})
        | plantilla_mejoras
        | modelo
        | StrOutputParser()
    )

    return cadena


if __name__ == "__main__":
    load_dotenv()
    modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    cadena = construir_cadena(modelo)

    fragmento = (
        "version: 2\n"
        "models:\n"
        "  - name: fact_ventas\n"
        "    description: 'Tabla de hechos de ventas.'\n"
        "    columns:\n"
        "      - name: id_venta\n"
        "        description: 'Identificador único de la venta.'\n"
        "      - name: monto_total\n"
    )

    resultado = cadena.invoke({"fragmento": fragmento})
    print(resultado)