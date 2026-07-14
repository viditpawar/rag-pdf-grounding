from ragcore import vectorstore
from ragcore.chunking import Chunk


def test_add_and_query(tmp_path):
    collection = vectorstore.get_collection(
        persist_dir=str(tmp_path), collection_name="test_collection"
    )

    chunks = [
        Chunk(text="alpha content", page=1, chunk_index=0),
        Chunk(text="beta content", page=1, chunk_index=1),
    ]
    embeddings = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]

    added = vectorstore.add_chunks(collection, "test.pdf", chunks, embeddings)
    assert added == 2

    results = vectorstore.query(collection, [0.9, 0.1, 0.0], top_k=1)
    assert results["documents"][0][0] == "alpha content"


def test_upsert_does_not_duplicate(tmp_path):
    collection = vectorstore.get_collection(
        persist_dir=str(tmp_path), collection_name="test_collection"
    )
    chunks = [Chunk(text="same content", page=1, chunk_index=0)]
    embeddings = [[1.0, 0.0, 0.0]]

    vectorstore.add_chunks(collection, "test.pdf", chunks, embeddings)
    vectorstore.add_chunks(collection, "test.pdf", chunks, embeddings)  # re-ingest

    assert collection.count() == 1
