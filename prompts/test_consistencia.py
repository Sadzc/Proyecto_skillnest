import json
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from prompts.banco import BANCO_DE_PROMPTS
from src.consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    parsear_respuesta_json,
)

INTENTOS = 3


def main():
    registro = {
        "fecha_hora_local": datetime.now().astimezone().isoformat(),
        "resultados": {},
    }

    for prompt in BANCO_DE_PROMPTS:
        resumen = {
            "intentos": INTENTOS,
            "exitos": 0,
            "fallos_formato": 0,
            "errores_api": 0,
            "detalle": [],
        }
        registro["resultados"][prompt["nombre"]] = resumen

        for intento in range(1, INTENTOS + 1):
            detalle = {"intento": intento}

            try:
                url, body = armar_peticion(
                    prompt["ejemplo_usuario"],
                    prompt["system_instruction"],
                    prompt.get("response_schema"),
                )
                respuesta = enviar_peticion(url, body)
                texto = extraer_texto(respuesta)

            except (RuntimeError, TimeoutError) as error:
                # Cuota diaria agotada: se corta sin tocar el registro anterior
                if str(error).startswith("Error 429"):
                    raise SystemExit(f"Cuota agotada, no se guarda el registro: {error}")
                resumen["errores_api"] += 1
                detalle.update(estado="error_api", error=str(error))
                resumen["detalle"].append(detalle)
                print(f"{prompt['nombre']} - intento {intento}: {detalle['estado']}")

            else:
                detalle["modelo_reportado"] = respuesta.get("modelVersion")
                detalle["respuesta_original"] = texto

                try:
                    datos = parsear_respuesta_json(texto, prompt["categorias_permitidas"])
                    faltan = [c for c in prompt["claves_esperadas"] if c not in datos]
                    if faltan:
                        raise ValueError(f"Faltan claves {faltan}.")
                except ValueError as error:
                    resumen["fallos_formato"] += 1
                    detalle.update(estado="fallo_formato", error=str(error))
                else:
                    resumen["exitos"] += 1
                    detalle.update(estado="valida", datos=datos)

                resumen["detalle"].append(detalle)
                print(f"{prompt['nombre']} - intento {intento}: {detalle['estado']}")

        time.sleep(10)

        print(
            f"{prompt['nombre']}: {resumen['exitos']}/{INTENTOS} válidas; "
            f"{resumen['fallos_formato']} fallos de formato; "
            f"{resumen['errores_api']} errores de API.\n"
        )

    ruta = RAIZ / "prompts" / "registro_resultados.json"
    ruta.write_text(json.dumps(registro, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Registro guardado en:", ruta)


if __name__ == "__main__":
    main()