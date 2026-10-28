from datetime import datetime
from pathlib import Path

from cliente import consultar_modelo
from pipeline_texto import procesar_texto, proporcion_coincidencia
from prompts.banco import SCHEMA_YML

SISTEMA = "Responde en español, en una o dos frases, usando solo el fragmento de schema.yml."

CASOS = [
    {
        "consulta": "¿Qué significa la columna id_venta?",
        "referencia": "id_venta es el identificador único de la venta.",
    },
    {
        "consulta": "¿Qué descripción tiene el modelo fact_ventas?",
        "referencia": "El modelo fact_ventas es la tabla de hechos de ventas.",
    },
    {
        "consulta": "¿Qué columna no tiene descripción?",
        "referencia": "La columna monto_total no tiene descripción.",
    },
]

RUTA_REGISTRO = Path(__file__).resolve().parent / "docs" / "registro_pipeline_texto.md"


if __name__ == "__main__":
    ahora = datetime.now().astimezone().isoformat(timespec="seconds")
    lineas = [f"# Antes y después del pipeline ({ahora})\n"]

    for i, caso in enumerate(CASOS, 1):
        pregunta = f"Fragmento de schema.yml:\n{SCHEMA_YML}\nPregunta: {caso['consulta']}"
        try:
            respuesta = consultar_modelo(pregunta, SISTEMA)
        except (ValueError, RuntimeError) as error:
            print(f"[Caso {i}] Falló: {error}")
            continue

        referencia = caso["referencia"]
        crudo = proporcion_coincidencia(referencia.split(), respuesta.split())
        procesado = proporcion_coincidencia(procesar_texto(referencia), procesar_texto(respuesta))

        resumen = (
            f"[Caso {i}] Coincidencia texto crudo: {crudo:.1%} | "
            f"texto procesado: {procesado:.1%}"
        )
        print(resumen)
        lineas.append(
            f"## Caso {i}\n\n"
            f"- Consulta: {caso['consulta']}\n"
            f"- Referencia: {referencia}\n"
            f"- Respuesta: {respuesta.strip()}\n"
            f"- {resumen}\n"
        )

    RUTA_REGISTRO.parent.mkdir(exist_ok=True)
    RUTA_REGISTRO.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Registro guardado en: {RUTA_REGISTRO}")