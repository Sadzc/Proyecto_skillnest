import json
from pathlib import Path

from cliente import consultar_modelo
from evaluar_pipeline import CASOS, SISTEMA
from pipeline_texto import calcular_metricas, resumir_metricas
from prompts.banco import SCHEMA_YML

RUTA_RESULTADOS = Path(__file__).resolve().parent / "docs" / "resultados" / "resultados_metricas.json"


def guardar(resultados: list[dict]) -> None:
    RUTA_RESULTADOS.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_RESULTADOS, "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    if RUTA_RESULTADOS.exists():
        resultados = json.loads(RUTA_RESULTADOS.read_text(encoding="utf-8"))
    else:
        resultados = []
    ya_hechas = {r["consulta"] for r in resultados}
    fallos_seguidos = 0

    for caso in CASOS:
        if caso["consulta"] in ya_hechas:
            continue

        pregunta = f"Fragmento de schema.yml:\n{SCHEMA_YML}\nPregunta: {caso['consulta']}"
        try:
            respuesta = consultar_modelo(pregunta, SISTEMA)
        except (ValueError, RuntimeError) as error:
            print(f"Falló '{caso['consulta']}': {error}")
            fallos_seguidos += 1
            if fallos_seguidos >= 2:
                print("Dos fallos seguidos: probablemente cuota agotada. Corta y reanuda después.")
                break
            continue

        fallos_seguidos = 0
        metricas = calcular_metricas(caso["referencia"], respuesta)
        resultados.append({
            "consulta": caso["consulta"],
            "referencia": caso["referencia"],
            "respuesta": respuesta.strip(),
            **{clave: round(valor, 3) for clave, valor in metricas.items()},
        })
        guardar(resultados)
        print(caso["consulta"], metricas)

    if resultados:
        print(f"\nTotal guardado: {len(resultados)} de {len(CASOS)}")
        print("\nResumen:", resumir_metricas(resultados))
        print("\nPeores casos primero:")
        for r in sorted(resultados, key=lambda r: r["f1"])[:3]:
            print(f"  {r['f1']:.3f}  {r['consulta']}")
        print(f"\nGuardado en: {RUTA_RESULTADOS}")