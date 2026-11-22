import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

PROYECTO_GCP = os.environ.get("GOOGLE_CLOUD_PROJECT")
UBICACION_GCP = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

# el valor de trabajo.name que imprime laboratorio_dataset.py al enviar el trabajo
nombre_trabajo = "NOMBRE_DE_TU_TRABAJO"

if nombre_trabajo == "NOMBRE_DE_TU_TRABAJO" or not PROYECTO_GCP:
    raise SystemExit(
        "No hay trabajo de tuning que inspeccionar: falta el nombre del trabajo "
        "o GOOGLE_CLOUD_PROJECT en tu .env. Este bloque se puede leer como referencia."
    )

client = genai.Client(vertexai=True, project=PROYECTO_GCP, location=UBICACION_GCP)

try:
    trabajo = client.tunings.get(name=nombre_trabajo)
except Exception as error:
    raise SystemExit(f"No se pudo consultar el trabajo de tuning: {error}")

if trabajo.tuning_data_stats is None or trabajo.tuning_data_stats.supervised_tuning_data_stats is None:
    raise SystemExit("El trabajo todavía no tiene estadísticas de datos. Espera a que termine y vuelve a ejecutar.")

stats = trabajo.tuning_data_stats.supervised_tuning_data_stats

print("ejemplos usados:", stats.tuning_dataset_example_count)
print("ejemplos truncados:", stats.total_truncated_example_count)
print("tokens facturables totales:", stats.total_billable_token_count)
print("caracteres facturables totales:", stats.total_billable_character_count)
print("pasos de entrenamiento:", stats.tuning_step_count)

print()
print("razones de truncado:", stats.dropped_example_reasons)
print("caracteres de tuning:", stats.total_tuning_character_count)
print("de esos, facturables:", stats.total_billable_character_count)