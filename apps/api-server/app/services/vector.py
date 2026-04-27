from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings


class VectorService:
    def __init__(self):
        self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        self.collection = settings.qdrant_collection

    def ensure_collection(self, vector_size: int = 768):
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection for c in collections)
        if not exists:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert_vectors(
        self,
        document_id: str,
        chunks: list[dict],
        vectors: list[list[float]],
    ):
        points = []
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point_id = f"{document_id}_{chunk['chunk_index']}"
            points.append(
                PointStruct(
                    id=hash(point_id) & 0xFFFFFFFFFFFFFFFF,
                    vector=vector,
                    payload={
                        "document_id": document_id,
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "filename": chunk.get("filename", ""),
                    },
                )
            )
        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            {
                "document_id": r.payload["document_id"],
                "chunk_index": r.payload["chunk_index"],
                "content": r.payload["content"],
                "filename": r.payload.get("filename", ""),
                "score": r.score,
            }
            for r in results
        ]

    def delete_by_document(self, document_id: str):
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[
                    FieldCondition(key="document_id", match=MatchValue(value=document_id))
                ]
            ),
        )


vector_service = VectorService()
