"""Step 4: Generate embeddings and store in Qdrant."""
import argparse
import json
import sys

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from utils.common import EMBEDDING_MODEL, QDRANT_COLLECTION, QDRANT_HOST, QDRANT_PORT


def embed_and_store(chunks: list[dict], document_id: str):
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    collections = client.get_collections().collections
    exists = any(c.name == QDRANT_COLLECTION for c in collections)
    if not exists:
        test_vec = model.encode("test")
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=len(test_vec), distance=Distance.COSINE),
        )

    texts = [c["content"] for c in chunks]
    vectors = model.encode(texts, show_progress_bar=True, batch_size=32)

    points = []
    for chunk, vector in zip(chunks, vectors):
        point_id = hash(f"{document_id}_{chunk['chunk_index']}") & 0xFFFFFFFFFFFFFFFF
        points.append(
            PointStruct(
                id=point_id,
                vector=vector.tolist(),
                payload={
                    "document_id": document_id,
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                },
            )
        )

    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(collection_name=QDRANT_COLLECTION, points=batch)

    return len(points)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks-file", required=True)
    parser.add_argument("--document-id", required=True)
    args = parser.parse_args()

    with open(args.chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    count = embed_and_store(chunks, args.document_id)
    print(f"Stored {count} vectors in Qdrant")
    sys.exit(0)
