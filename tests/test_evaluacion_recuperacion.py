from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding

import evaluacion_recuperacion as ev
from indexar_corpus import CORPUS, preparar_chunks


def test_conjunto_tiene_entre_8_y_15_preguntas_unicas():
    preguntas = [c["pregunta"] for c in ev.casos_evaluacion]
    assert 8 <= len(preguntas) <= 15
    assert len(preguntas) == len(set(preguntas))


def test_ids_etiquetados_existen_en_el_indice():
    _, ids = preparar_chunks(CORPUS, ev.CHUNK_SIZE, ev.CHUNK_OVERLAP)
    for caso in ev.casos_evaluacion:
        assert isinstance(caso["ids_relevantes"], set)
        assert caso["ids_relevantes"] <= set(ids), caso["pregunta"]


def test_hay_un_caso_sin_respuesta_y_uno_con_varios_relevantes():
    tamanos = [len(c["ids_relevantes"]) for c in ev.casos_evaluacion]
    assert 0 in tamanos and max(tamanos) > 1


def test_evaluacion_de_punta_a_punta_con_embeddings_de_prueba(tmp_path):
    chunks, ids = preparar_chunks(CORPUS, ev.CHUNK_SIZE, ev.CHUNK_OVERLAP)
    vs = Chroma.from_documents(
        chunks, ids=ids, embedding=DeterministicFakeEmbedding(size=16),
        collection_name="test_evaluacion", persist_directory=str(tmp_path / "db"),
    )
    resultados, p, r = ev._correr(vs, 3)
    assert len(resultados) == len(ev.casos_evaluacion)
    assert all(len(x["ids_recuperados"]) == 3 for x in resultados)
    assert 0.0 <= p <= 1.0 and 0.0 <= r <= 1.0
    # recuperación determinista: misma entrada, mismo resultado
    assert ev._correr(vs, 3)[0] == resultados


def test_guardar_resultados_deja_el_formato_del_bloque(tmp_path):
    resultados = [
        {"pregunta": "p1", "ids_recuperados": ["a"], "precision": 1 / 3, "recall": 1.0},
        {"pregunta": "p2", "ids_recuperados": ["b"], "precision": 0.0, "recall": None},
    ]
    ruta = ev.guardar_resultados(resultados, 1 / 6, 1.0, k=3, ruta=tmp_path / "x" / "res.txt")
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    assert lineas[0].startswith("Fecha: ")
    assert lineas[1] == "Configuracion: k=3, chunk_size=400, chunk_overlap=20"
    assert lineas[3] == "0.33  1.00  p1"
    assert lineas[4] == "0.00  n/a  p2"
    assert lineas[-1] == "promedio -> precision: 0.167  recall: 1.000"