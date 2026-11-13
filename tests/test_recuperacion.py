import re

import pytest
from langchain_chroma import Chroma
from langchain_core.embeddings import DeterministicFakeEmbedding

from indexar_corpus import CORPUS, preparar_chunks
from recuperacion import construir_prompt, formatear_contexto, resolver_citas

@pytest.fixture
def vectorstore(tmp_path):
    chunks, ids = preparar_chunks(CORPUS)
    return Chroma.from_documents(
        chunks, ids=ids, embedding=DeterministicFakeEmbedding(size=16),
        collection_name="test_recuperacion", persist_directory=str(tmp_path),
    )

def test_citas_tiene_k_entradas_con_claves_consecutivas(vectorstore):
    _, citas = construir_prompt("¿Qué es route_id?", k=3, vectorstore=vectorstore)
    assert list(citas) == [1, 2, 3]

def test_ninguna_cita_es_desconocida(vectorstore):
    _, citas = construir_prompt("cualquier pregunta", k=4, vectorstore=vectorstore)
    assert all("schema.yml" in fuente and fuente != "desconocida" for fuente in citas.values())

def test_prompt_contiene_la_pregunta_exacta_y_la_instruccion_de_citar(vectorstore):
    pregunta = "¿Qué significa la columna route_id?"
    prompt, _ = construir_prompt(pregunta, k=3, vectorstore=vectorstore)
    assert f"Pregunta: {pregunta}" in prompt
    assert "Cita la fuente" in prompt and "dilo explicitamente" in prompt

def test_contexto_numerado_sin_saltos(vectorstore):
    prompt, _ = construir_prompt("x", k=5, vectorstore=vectorstore)
    assert re.findall(r"^\[(\d+)\]", prompt, flags=re.M) == ["1", "2", "3", "4", "5"]

def test_chunk_sin_fuente_se_marca_desconocida():
    from langchain_core.documents import Document
    _, citas = formatear_contexto([Document(page_content="x", metadata={})])
    assert citas == {1: "desconocida"}

def test_resolver_citas_marca_la_alucinada():
    res = resolver_citas("Dato [1] y otro [99].", {1: "schema.yml > fct_revenue"})
    assert res == {1: "schema.yml > fct_revenue", 99: "Cita invalida / no encontrada"}

def test_resolver_citas_acepta_citas_agrupadas():
    res = resolver_citas("Hay datos [1, 2, 3].", {1: "a", 2: "b", 3: "c"})
    assert res == {1: "a", 2: "b", 3: "c"}