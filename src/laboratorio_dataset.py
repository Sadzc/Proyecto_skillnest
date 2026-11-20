import os
import json
import time
from collections import Counter

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Configuración de Vertex AI (se lee del .env; nunca se escribe en el código)
PROYECTO_GCP = os.environ.get("GOOGLE_CLOUD_PROJECT")
UBICACION_GCP = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
URI_DATASET_GCS = os.environ.get("TUNING_DATASET_GCS_URI")  # ej: gs://mi-bucket/ejemplos_tuning.jsonl
MODELO_BASE = "gemini-2.5-flash"  # modelo base con tuning supervisado en Vertex AI
RUTA_JSONL = os.path.join("docs", "ejemplos_tuning.jsonl")
ENVIAR_TRABAJO = False  # cambia a True solo cuando quieras entrenar de verdad (genera costo)


# Paso 1: construcción del dataset
ejemplos_raw = [
    ("TimeoutError: la conexion tardo mas de 10 segundos en responder.",
     {"categoria": "red", "accion_sugerida": "reintentar con backoff exponencial"}),
    ("ValueError: la clave de API no tiene el formato esperado.",
     {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"}),
    ("429 RESOURCE_EXHAUSTED: se supero el limite de peticiones por minuto.",
     {"categoria": "cuota", "accion_sugerida": "esperar y reintentar, con backoff"}),
    ("API key not valid. Please pass a valid API key.",
     {"categoria": "autenticacion", "accion_sugerida": "revisar GEMINI_API_KEY, no reintentar"}),
    ("RuntimeError: Your system has an unsupported version of sqlite3.",
     {"categoria": "entorno", "accion_sugerida": "instalar pysqlite3-binary"}),
    ("ModuleNotFoundError: No module named langchain_chroma.",
     {"categoria": "entorno", "accion_sugerida": "instalar dependencia faltante"}),
    ("PermissionError al crear la carpeta del vector store.",
     {"categoria": "entorno", "accion_sugerida": "revisar permisos de escritura"}),
    ("InvalidArgumentError: Collection expecting embedding with dimension of 768, got 1536.",
     {"categoria": "consistencia_indice", "accion_sugerida": "reindexar con el mismo modelo de embeddings"}),
]

# Lista de TuningExample: el texto es la entrada y el JSON es la salida exacta a aprender
examples = [
    types.TuningExample(text_input=texto, output=json.dumps(salida, ensure_ascii=False))
    for texto, salida in ejemplos_raw
]


# Paso 2: validación local, antes de gastar tiempo de entrenamiento
def validar_dataset(
    examples: list[types.TuningExample],
    claves_esperadas: tuple[str, ...] = ("categoria", "accion_sugerida"),
) -> list[str]:
    problemas = []
    vistos = set()
    for i, ej in enumerate(examples):
        if not ej.text_input or not ej.text_input.strip():
            problemas.append(f"ejemplo {i}: text_input vacio")
        if not ej.output or not ej.output.strip():
            problemas.append(f"ejemplo {i}: output vacio")
            continue
        if ej.text_input in vistos:
            problemas.append(f"ejemplo {i}: text_input duplicado")
        vistos.add(ej.text_input)
        try:
            salida = json.loads(ej.output)
        except json.JSONDecodeError:
            problemas.append(f"ejemplo {i}: output no es JSON valido")
            continue
        for clave in claves_esperadas:
            if clave not in salida:
                problemas.append(f'ejemplo {i}: output no tiene la clave "{clave}"')
    return problemas


# Paso 3: balance entre categorías (cero problemas de formato no es lo mismo que un buen dataset)
def chequear_balance(ejemplos_raw: list[tuple[str, dict]], clave: str = "categoria") -> Counter:
    return Counter(salida[clave] for _, salida in ejemplos_raw)


# Exporta el dataset validado al formato JSONL que Vertex AI lee desde Cloud Storage
def exportar_jsonl(examples: list[types.TuningExample], ruta: str) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        for ej in examples:
            linea = {
                "contents": [
                    {"role": "user", "parts": [{"text": ej.text_input}]},
                    {"role": "model", "parts": [{"text": ej.output}]},
                ]
            }
            f.write(json.dumps(linea, ensure_ascii=False) + "\n")


# Paso 4: el tuning es asíncrono, se consulta con tunings.get (no con tune otra vez)
def esperar_a_que_termine(
    client: genai.Client, nombre_trabajo: str, intervalo_segundos: int = 30
) -> types.TuningJob:
    estados_finales = {
        types.JobState.JOB_STATE_SUCCEEDED,
        types.JobState.JOB_STATE_FAILED,
        types.JobState.JOB_STATE_CANCELLED,
        types.JobState.JOB_STATE_PARTIALLY_SUCCEEDED,
    }
    while True:
        trabajo = client.tunings.get(name=nombre_trabajo)
        print(f"Estado actual: {trabajo.state}")
        if trabajo.state in estados_finales:
            return trabajo
        time.sleep(intervalo_segundos)


if __name__ == "__main__":
    print(len(examples), "ejemplos construidos")
    print(examples[0])

    # Validación del dataset
    print()
    problemas = validar_dataset(examples)
    print(f"{len(examples)} ejemplos, {len(problemas)} problemas encontrados")
    for p in problemas:
        print(" -", p)

    # Chequeo de balance
    print()
    balance = chequear_balance(ejemplos_raw)
    for categoria, cuenta in balance.most_common():
        print(f"{categoria}: {cuenta}")
    maximo = max(balance.values())
    minimo = min(balance.values())
    print()
    print(f"categoria mas representada: {maximo} ejemplos")
    print(f"categoria menos representada: {minimo} ejemplos")
    print(f"razon max/min: {maximo / minimo:.1f}x")

    # Estados posibles de un trabajo de tuning
    print()
    print("Estados posibles de un trabajo de tuning:")
    for estado in types.JobState:
        print(" ", estado)

    # Comprobar que el validador detecta errores (dataset roto a propósito)
    print()
    examples_rotos = examples + [
        types.TuningExample(text_input="", output='{"categoria": "red"}'),
        types.TuningExample(text_input=ejemplos_raw[0][0], output="no es json"),
    ]
    problemas2 = validar_dataset(examples_rotos)
    print(f"{len(examples_rotos)} ejemplos, {len(problemas2)} problemas encontrados")
    for p in problemas2:
        print(" -", p)

    if problemas:
        raise SystemExit("\nEl dataset tiene problemas: corrígelos antes de exportar o entrenar.")

    # Exportar el dataset validado (es el archivo que se sube al bucket)
    exportar_jsonl(examples, RUTA_JSONL)
    print(f"\nDataset exportado a {RUTA_JSONL}")

    if not ENVIAR_TRABAJO:
        print("ENVIAR_TRABAJO = False: no se envía el trabajo de tuning (sin costo).")
        raise SystemExit(0)

    # Envío del trabajo de tuning en Vertex AI (demostrativo, genera costo)
    if not PROYECTO_GCP or not URI_DATASET_GCS:
        raise SystemExit("Faltan GOOGLE_CLOUD_PROJECT o TUNING_DATASET_GCS_URI en tu .env.")

    client = genai.Client(vertexai=True, project=PROYECTO_GCP, location=UBICACION_GCP)

    dataset = types.TuningDataset(gcs_uri=URI_DATASET_GCS)

    config = types.CreateTuningJobConfig(
        tuning_mode=types.TuningMode.TUNING_MODE_PEFT_ADAPTER,
        adapter_size=types.AdapterSize.ADAPTER_SIZE_FOUR,
        epoch_count=5,
        tuned_model_display_name="categorizacion-errores",
    )

    try:
        print("Enviando el trabajo de tuning a Vertex AI...")
        trabajo = client.tunings.tune(
            base_model=MODELO_BASE,
            training_dataset=dataset,
            config=config,
        )
        print(f"Trabajo creado con éxito. ID {trabajo.name}")

        resultado_final = esperar_a_que_termine(client, trabajo.name)
        print("\nProceso finalizado con estado:", resultado_final.state)

        if resultado_final.state == types.JobState.JOB_STATE_SUCCEEDED:
            print("Modelo listo para usar:", resultado_final.tuned_model.model)
    except Exception as error:
        print("No se pudo completar el trabajo de tuning:", error)