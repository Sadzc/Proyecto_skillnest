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
    {
        "consulta": "¿Qué descripción tiene la columna id_venta?",
        "referencia": "La columna id_venta tiene la descripción identificador único de la venta.",
    },
    {
        "consulta": "¿Tiene la columna monto_total una descripción?",
        "referencia": "No, la columna monto_total no tiene descripción.",
    },
    {
        "consulta": "¿Qué columnas tiene el modelo fact_ventas?",
        "referencia": "El modelo fact_ventas tiene las columnas id_venta y monto_total.",
    },
    {
        "consulta": "¿Cuántas columnas tiene fact_ventas?",
        "referencia": "El modelo fact_ventas tiene dos columnas.",
    },
    {
        "consulta": "¿Qué versión de esquema usa el archivo?",
        "referencia": "El archivo usa la versión 2.",
    },
    {
        "consulta": "¿Cómo se llama el modelo documentado?",
        "referencia": "El modelo documentado se llama fact_ventas.",
    },
    {
        "consulta": "¿Para qué sirve id_venta?",
        "referencia": "id_venta identifica de forma única cada venta.",
    },
    {
        "consulta": "¿Qué columnas sí tienen descripción?",
        "referencia": "Solo la columna id_venta tiene descripción.",
    },
    {
        "consulta": "¿Está documentada la columna monto_total?",
        "referencia": "No, la columna monto_total no está documentada.",
    },
    {
        "consulta": "¿Qué tests tiene el modelo fact_ventas?",
        "referencia": "El fragmento no define tests para fact_ventas.",
    },
    {
        "consulta": "¿De qué tabla sale la métrica de ingresos netos?",
        "referencia": "El fragmento no indica de qué tabla sale la métrica de ingresos netos.",
    },
    {
        "consulta": "¿Qué significa la columna monto_total?",
        "referencia": "El fragmento no incluye una descripción de la columna monto_total.",
    },
    {
        "consulta": "¿El modelo fact_ventas tiene descripción?",
        "referencia": "Sí, el modelo fact_ventas tiene la descripción Tabla de hechos de ventas.",
    },
    {
        "consulta": "¿Qué tipo de dato tiene id_venta?",
        "referencia": "El fragmento no indica el tipo de dato de id_venta.",
    },
    {
        "consulta": "¿Está completa la documentación del fragmento?",
        "referencia": "No, está incompleta porque a la columna monto_total le falta la descripción.",
    },
    {
        "consulta": "¿Cuál es la columna que identifica cada venta?",
        "referencia": "La columna id_venta identifica cada venta.",
    },
    {
        "consulta": "¿Cuántas columnas tienen descripción?",
        "referencia": "Una sola columna, id_venta, tiene descripción.",
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