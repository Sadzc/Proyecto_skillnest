import json
from pathlib import Path

resultados = json.loads(
    Path("docs/resultados/resultados_metricas.json").read_text(encoding="utf-8")
)
peores_casos = sorted(resultados, key=lambda r: r["f1"])
muestra = peores_casos[:5] + peores_casos[-5:]

for r in muestra:
    print(f"{r['f1']:.3f} | {r['consulta']}")
    print(f"  REF:  {r['referencia']}")
    print(f"  RESP: {r['respuesta']}\n")