from indexar_corpus import CORPUS, preparar_chunks


def test_un_chunk_por_documento_con_chunk_size_400():
    chunks, ids = preparar_chunks(CORPUS)
    assert len(chunks) == len(CORPUS) == len(ids)


def test_ids_unicos_y_predecibles():
    _, ids = preparar_chunks(CORPUS)
    assert len(ids) == len(set(ids))
    assert "fct_revenue.route_id_0" in ids
    assert "dim_routes.activa_0" in ids


def test_metadata_permite_citar_la_fuente():
    chunks, _ = preparar_chunks(CORPUS)
    for chunk in chunks:
        assert chunk.metadata["fuente"] == "schema.yml"
        assert chunk.metadata["modelo"]


def test_documento_largo_se_divide_con_ids_consecutivos():
    largo = [{"texto": "palabra " * 100, "fuente": "schema.yml", "modelo": "m_largo"}]
    chunks, ids = preparar_chunks(largo, chunk_size=100, chunk_overlap=10)
    assert len(chunks) > 1
    assert ids == [f"m_largo_{i}" for i in range(len(chunks))]


def test_no_hay_chunks_vacios():
    chunks, _ = preparar_chunks(CORPUS)
    assert all(c.page_content.strip() for c in chunks)