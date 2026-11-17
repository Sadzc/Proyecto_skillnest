"""Evaluación de la recuperación sobre el corpus real del proyecto (Bloque 27, Segmento 3).

Corre un conjunto de preguntas contra el retriever de Chroma, calcula precisión@k y
recall@k por pregunta y en promedio, y deja un registro en docs/resultados/.

Uso (desde la raíz del proyecto, con el venv activo y GEMINI_API_KEY en .env):
    python src/evaluacion_recuperacion.py             # evalúa y guarda el registro
    python src/evaluacion_recuperacion.py --detalle   # además muestra los ids recuperados
    python src/evaluacion_recuperacion.py --verificar # chequeos del bloque (2 corridas + k=5)

Gasta 1 llamada de embeddings por pregunta; --verificar hace 3 corridas.
"""

import os
import sys
from datetime import date
from pathlib import Path

from indexar_corpus import cargar_vectorstore, con_reintentos

K = 3  # cuántos chunks recupera el retriever y cuántos evalúa la función
# Deben coincidir con los de indexar_corpus.py: este script no los lee del índice.
CHUNK_SIZE = 400
CHUNK_OVERLAP = 20
RUTA_RESULTADOS = (Path(__file__).resolve().parent.parent
                   / "docs" / "resultados" / "resultados_evaluacion.txt")

# Conjunto de evaluación. Los ids se etiquetaron leyendo el CORPUS de indexar_corpus.py,
# ANTES de correr nada contra el retriever. Cada id es <doc_id>_<n> (ver preparar_chunks).
# Las preguntas usan palabras distintas a las del corpus a propósito: miden búsqueda
# semántica, no coincidencia literal.
casos_evaluacion = [
    {"pregunta": "cada cuanto se genera una fila en la tabla de ingresos",
     "ids_relevantes": {"fct_revenue_0"}},
    {"pregunta": "que campo identifica de forma unica a cada ruta",
     "ids_relevantes": {"fct_revenue.route_id_0"}},
    {"pregunta": "con que tabla se relaciona el identificador de ruta",
     "ids_relevantes": {"fct_revenue.route_id_0"}},
    {"pregunta": "en que moneda se registran los ingresos del dia",
     "ids_relevantes": {"fct_revenue.ingresos_0"}},
    {"pregunta": "cuanta gente viajo en una ruta en un dia determinado",
     "ids_relevantes": {"fct_revenue.pasajeros_0"}},
    {"pregunta": "que contiene el catalogo de rutas del sistema",
     "ids_relevantes": {"dim_routes_0"}},
    {"pregunta": "que ciudad es el punto de partida de una ruta",
     "ids_relevantes": {"dim_routes.origen_0"}},
    {"pregunta": "como se llama el campo con la ciudad de llegada",
     "ids_relevantes": {"dim_routes.origen_0"}},
    {"pregunta": "que columna del catalogo de rutas no esta documentada",
     "ids_relevantes": {"dim_routes.activa_0"}},
    # Varios chunks relevantes: las tres columnas documentadas de la tabla de hechos.
    {"pregunta": "que columnas tiene la tabla de hechos de ingresos",
     "ids_relevantes": {"fct_revenue.route_id_0", "fct_revenue.ingresos_0",
                        "fct_revenue.pasajeros_0"}},
    # Sin respuesta en el corpus: ids_relevantes vacío -> recall n/a, fuera del promedio.
    {"pregunta": "cual es el margen de ganancia por ruta",
     "ids_relevantes": set()},
]


def precision_at_k(ids_recuperados, ids_relevantes):
    """Fracción de los ids recuperados que son relevantes (0.0 si no hay ninguno)."""
    if not ids_recuperados:
        return 0.0
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_recuperados)


def recall_at_k(ids_recuperados, ids_relevantes):
    """Fracción de los ids relevantes que se recuperaron (None si el caso no tiene ninguno)."""
    if not ids_relevantes:
        return None
    acertados = [i for i in ids_recuperados if i in ids_relevantes]
    return len(acertados) / len(ids_relevantes)


def promediar(valores):
    """Promedio que ignora los None y evita dividir por cero."""
    validos = [v for v in valores if v is not None]
    return sum(validos) / len(validos) if validos else 0.0


def evaluar_recuperacion(retriever, casos, k=3):
    """Corre cada caso contra el retriever real y promedia precisión y recall."""
    resultados = []
    for caso in casos:
        # Reintenta solo ante 429/RESOURCE_EXHAUSTED (cuota gratuita de embeddings).
        chunks = con_reintentos(lambda: retriever.invoke(caso["pregunta"]))
        ids_recuperados = [c.id for c in chunks][:k]
        p = precision_at_k(ids_recuperados, caso["ids_relevantes"])
        r = recall_at_k(ids_recuperados, caso["ids_relevantes"])
        resultados.append({"pregunta": caso["pregunta"], "ids_recuperados": ids_recuperados,
                           "precision": p, "recall": r})

    precision_promedio = promediar(x["precision"] for x in resultados)
    recall_promedio = promediar(x["recall"] for x in resultados)
    return resultados, precision_promedio, recall_promedio


def formatear_linea(r):
    recall_txt = "n/a" if r["recall"] is None else f"{r['recall']:.2f}"
    return f"{r['precision']:.2f}  {recall_txt}  {r['pregunta']}"


def formatear_promedio(precision_promedio, recall_promedio):
    return f"promedio -> precision: {precision_promedio:.3f}  recall: {recall_promedio:.3f}"


def guardar_resultados(resultados, precision_promedio, recall_promedio, k=K,
                       ruta=RUTA_RESULTADOS):
    """Escribe el registro de la corrida: fecha, configuración, una línea por pregunta, promedios."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(f"Fecha: {date.today()}\n")
        archivo.write(f"Configuracion: k={k}, chunk_size={CHUNK_SIZE}, "
                      f"chunk_overlap={CHUNK_OVERLAP}\n\n")
        for r in resultados:
            archivo.write(formatear_linea(r) + "\n")
        archivo.write("\n" + formatear_promedio(precision_promedio, recall_promedio) + "\n")
    return ruta


def _correr(vectorstore, k):
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    return evaluar_recuperacion(retriever, casos_evaluacion, k=k)


def verificar(vectorstore):
    """Los dos chequeos del bloque: determinismo (2 corridas iguales) y trade-off k=3 -> k=5."""
    res1, p1, r1 = _correr(vectorstore, K)
    res2, p2, r2 = _correr(vectorstore, K)
    print(f"Corrida 1 (k={K}) -> {formatear_promedio(p1, r1)}")
    print(f"Corrida 2 (k={K}) -> {formatear_promedio(p2, r2)}")
    print("Identico a la primera corrida:", res1 == res2)

    _, p5, r5 = _correr(vectorstore, 5)
    print(f"Corrida 3 (k=5) -> {formatear_promedio(p5, r5)}")
    print(f"recall subio o se mantuvo (k={K} -> k=5):", r5 >= r1 - 1e-9)
    print(f"precision bajo o se mantuvo (k={K} -> k=5):", p5 <= p1 + 1e-9)


def main(argv):
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit('Falta GEMINI_API_KEY. Defínela en tu ".env" y vuelve a ejecutar.')

    vectorstore = cargar_vectorstore()
    if vectorstore._collection.count() == 0:
        raise SystemExit("El índice está vacío. Corre primero: python src/indexar_corpus.py")

    if "--verificar" in argv:
        verificar(vectorstore)
        return

    resultados, precision_promedio, recall_promedio = _correr(vectorstore, K)
    for r in resultados:
        print(formatear_linea(r))
        if "--detalle" in argv:
            print(f"        recuperados: {r['ids_recuperados']}")
    print("\n" + formatear_promedio(precision_promedio, recall_promedio))

    ruta = guardar_resultados(resultados, precision_promedio, recall_promedio)
    print(f"Resultados guardados en {ruta}")


if __name__ == "__main__":
    main(sys.argv[1:])