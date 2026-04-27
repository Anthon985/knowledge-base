from elasticsearch import AsyncElasticsearch

from app.config import settings

INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "default": {"type": "standard"},
            }
        },
    },
    "mappings": {
        "properties": {
            "document_id": {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            "content": {"type": "text", "analyzer": "standard"},
            "filename": {"type": "keyword"},
            "content_type": {"type": "keyword"},
            "created_at": {"type": "date"},
        }
    },
}


class SearchService:
    def __init__(self):
        self.client = AsyncElasticsearch(settings.elasticsearch_url)
        self.index = settings.elasticsearch_index

    async def ensure_index(self):
        exists = await self.client.indices.exists(index=self.index)
        if not exists:
            await self.client.indices.create(index=self.index, body=INDEX_MAPPING)

    async def index_chunks(self, document_id: str, filename: str, chunks: list[dict]):
        actions = []
        for chunk in chunks:
            actions.append(
                {
                    "_index": self.index,
                    "_id": f"{document_id}_{chunk['chunk_index']}",
                    "_source": {
                        "document_id": document_id,
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "filename": filename,
                    },
                }
            )
        if actions:
            from elasticsearch.helpers import async_bulk

            await async_bulk(self.client, actions)

    async def search(self, query: str, top_k: int = 10) -> list[dict]:
        result = await self.client.search(
            index=self.index,
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["content", "filename"],
                    }
                },
                "size": top_k,
                "_source": ["document_id", "chunk_index", "content", "filename"],
            },
        )
        hits = result["hits"]["hits"]
        return [
            {
                "document_id": hit["_source"]["document_id"],
                "chunk_index": hit["_source"]["chunk_index"],
                "content": hit["_source"]["content"],
                "filename": hit["_source"]["filename"],
                "score": hit["_score"],
            }
            for hit in hits
        ]

    async def delete_by_document(self, document_id: str):
        await self.client.delete_by_query(
            index=self.index,
            body={"query": {"term": {"document_id": document_id}}},
        )

    async def close(self):
        await self.client.close()


search_service = SearchService()
