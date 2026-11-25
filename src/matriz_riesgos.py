"""Bloque 32 · Paso 3: matriz de riesgos del asistente RAG sobre la documentación del DWH.

Imprime la matriz ordenada por puntaje, marca las filas al límite de su categoría,
verifica que todo riesgo ALTO o CRITICO tenga un punto de supervisión humana y
genera la imagen matriz_riesgos.png en la raíz del repo.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo escribe el PNG
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

RUTA_IMAGEN = Path(__file__).resolve().parent.parent / "matriz_riesgos.png"

COLORES = {"CRITICO": "#e03131", "ALTO": "#f76707", "MEDIO": "#fcc419", "BAJO": "#8ce99a"}

mis_riesgos = [
    {"riesgo": "Respuesta inventada sobre un modelo o columna sin documentar",
     "probabilidad": 3,  # el corpus tiene huecos: justo lo que el sistema debe alertar
     "impacto": 5,       # un analista toma una metrica equivocada como oficial
     "mitigacion": "Prompt exige citar [N] y declarar si no alcanza + resolver_citas marca citas invalidas (Bloque 26)",
     "supervision": "Revision semanal de trazas con afirmaciones sin cita (Bloque 23)"},
    {"riesgo": "Inyeccion de prompt via descripcion maliciosa en schema.yml indexado",
     "probabilidad": 3,  # el schema.yml lo edita el equipo, no usuarios anonimos
     "impacto": 4,       # expone instrucciones y desvia respuestas sobre el DWH
     "mitigacion": "Roles system/human + <contexto> + filtro de patrones (Bloque 31)",
     "supervision": "Chunk descartado (doc_hash en rag_logs.jsonl) se revisa antes de reindexar"},
    {"riesgo": "Version nueva del prompt activada sin revision cambia las respuestas",
     "probabilidad": 3,
     "impacto": 4,
     "mitigacion": "RegistroDePrompts con huella + diff entre versiones (Bloque 32)",
     "supervision": "interrupt() en grafo_supervision.py antes de activar (Bloque 32)"},
    {"riesgo": "Respuesta con definicion vieja por chunk no reindexado tras cambiar schema.yml",
     "probabilidad": 3,
     "impacto": 3,
     "mitigacion": "Ids explicitos + agregar_documentos / eliminar_por_ids (Bloque 25)",
     "supervision": "Revisar el diff del schema.yml en el PR antes de reindexar"},
    {"riesgo": "Ticket de redocumentacion abierto por error por el agente",
     "probabilidad": 2,
     "impacto": 4,       # irreversible: consume tiempo real del equipo de Data Engineering
     "mitigacion": "Aprobacion humana con tiempo limite en solicitar_redocumentacion (Bloque 23)",
     "supervision": "esperar_aprobacion() + registro_aprobaciones (Bloque 23)"},
    {"riesgo": "Cuota diaria del free tier de Gemini agotada deja el servicio sin respuesta",
     "probabilidad": 4,  # 20 requests/dia por modelo, ya ocurrio
     "impacto": 2,       # molesta, pero no entrega informacion incorrecta
     "mitigacion": "con_reintento en cliente.py (Bloque 12) + ensayo de rate limit (Bloque 13)",
     "supervision": None},
]


def puntaje_riesgo(probabilidad, impacto):
    return probabilidad * impacto


def categoria_riesgo(puntaje):
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad, impacto):
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto), (probabilidad - 1, impacto),
        (probabilidad, impacto + 1), (probabilidad, impacto - 1),
    ]
    for p2, i2 in vecinos:
        if not (1 <= p2 <= 5 and 1 <= i2 <= 5):
            continue
        if categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False


def evaluar(riesgos):
    """Agrega puntaje, categoría y al_limite a cada fila; devuelve la lista ordenada."""
    for r in riesgos:
        r["puntaje"] = puntaje_riesgo(r["probabilidad"], r["impacto"])
        r["categoria"] = categoria_riesgo(r["puntaje"])
        r["al_limite"] = esta_en_el_limite(r["probabilidad"], r["impacto"])
    return sorted(riesgos, key=lambda x: -x["puntaje"])


def sin_supervision(riesgos):
    """Riesgos ALTO o CRITICO que no tienen punto de supervisión: deberían ser cero."""
    return [r for r in riesgos if r["categoria"] in ("CRITICO", "ALTO") and not r["supervision"]]


def dibujar_matriz(riesgos, ruta=RUTA_IMAGEN):
    """Heatmap probabilidad x impacto con cada riesgo numerado, y la lista a la derecha."""
    fig = plt.figure(figsize=(16, 8.2))
    fig.suptitle("Matriz de riesgos: asistente RAG de documentacion del DWH",
                 fontsize=20, fontweight="bold", color="#1c3d8c")

    ax = fig.add_axes([0.05, 0.12, 0.36, 0.72])
    for p in range(1, 6):
        for i in range(1, 6):
            puntaje = puntaje_riesgo(p, i)
            ax.add_patch(plt.Rectangle((i - 0.5, p - 0.5), 1, 1, edgecolor="white", linewidth=2,
                                       facecolor=COLORES[categoria_riesgo(puntaje)]))
            ax.text(i, p - 0.3, str(puntaje), ha="center", va="center", fontsize=11,
                    color="#343a40")

    # Riesgos en la misma celda se reparten en horizontal para no taparse
    por_celda = {}
    for n, r in enumerate(riesgos, start=1):
        por_celda.setdefault((r["impacto"], r["probabilidad"]), []).append(n)
    for (i, p), numeros in por_celda.items():
        for k, n in enumerate(numeros):
            x = i + (k - (len(numeros) - 1) / 2) * 0.32
            ax.scatter(x, p + 0.12, s=520, color="#1c3d8c", edgecolor="white", linewidth=2, zorder=3)
            ax.text(x, p + 0.12, str(n), ha="center", va="center", color="white",
                    fontsize=12, fontweight="bold", zorder=4)

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Impacto (1 a 5)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Probabilidad (1 a 5)", fontsize=13, fontweight="bold")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)

    leyenda = [plt.Rectangle((0, 0), 1, 1, color=COLORES[c]) for c in COLORES]
    ax.legend(leyenda, ["CRITICO (15 o mas)", "ALTO (9 a 14)", "MEDIO (4 a 8)", "BAJO (menos de 4)"],
              loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=False, fontsize=10)

    lista = fig.add_axes([0.45, 0.06, 0.53, 0.8])
    lista.axis("off")
    alto_fila = 1 / len(riesgos)
    for n, r in enumerate(riesgos, start=1):
        y = 1 - n * alto_fila + alto_fila / 2
        lista.add_patch(FancyBboxPatch((0.0, y - alto_fila * 0.42), 1.0, alto_fila * 0.84,
                                       boxstyle="round,pad=0.005,rounding_size=0.015",
                                       facecolor="#f8f9fa", edgecolor="#dee2e6"))
        lista.scatter(0.04, y, s=700, color="#1c3d8c", zorder=3)
        lista.text(0.04, y, str(n), ha="center", va="center", color="white",
                   fontsize=13, fontweight="bold", zorder=4)
        lista.text(0.08, y + alto_fila * 0.15, r["riesgo"], va="center", fontsize=10.5,
                   fontweight="bold", color="#212529")
        detalle = "Supervision: " + r["supervision"] if r["supervision"] else "Mitigacion: " + r["mitigacion"]
        lista.text(0.08, y - alto_fila * 0.17, detalle, va="center", fontsize=8.8, color="#495057")
        etiqueta = f"{r['categoria']} ({r['puntaje']})" + (" *" if r["al_limite"] else "")
        lista.text(0.975, y + alto_fila * 0.15, etiqueta, ha="right", va="center", fontsize=10.5,
                   fontweight="bold", color="#212529",
                   bbox={"boxstyle": "round,pad=0.35", "facecolor": COLORES[r["categoria"]],
                         "edgecolor": "none"})
    fig.text(0.715, 0.02, "* al limite: un punto de diferencia le cambia la categoria. "
             "Todo ALTO o CRITICO lleva punto de supervision humana.",
             ha="center", fontsize=9.5, color="#1c3d8c")

    fig.savefig(ruta, dpi=150, facecolor="white")
    plt.close(fig)
    return ruta


if __name__ == "__main__":
    ordenados = evaluar(mis_riesgos)

    print("=" * 62)
    print("PASO 3: mi matriz de riesgos (ordenada por puntaje)")
    print("=" * 62)
    for r in ordenados:
        marca = "[AL LIMITE]" if r["al_limite"] else ""
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']} {marca}")

    print()
    for r in ordenados:
        if r["al_limite"]:
            print("revisar con otra persona:", r["riesgo"])

    faltantes = sin_supervision(ordenados)
    assert not faltantes, f"ALTO/CRITICO sin punto de supervision: {[r['riesgo'] for r in faltantes]}"
    print("\ntodos los ALTO/CRITICO tienen punto de supervision: ok")
    print("imagen generada:", dibujar_matriz(ordenados).name)