"""Step 5: Index chunks in Elasticsearch for full-text search."""
import argparse
import json
import sys

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from utils.common import ES_INDEX, ES_URL

INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "document_id": {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            "content": {"type": "text", "analyzer": "standard"},
            "filename": {"type": "keyword"},
        }
    },
}


def index_chunks(chunks: list[dict], document_id: str, filename: str):
    client = Elasticsearch(ES_URL)

    if not client.indices.exists(index=ES_INDEX):
        client.indices.create(index=ES_INDEX, body=INDEX_MAPPING)

    actions = []
    for chunk in chunks:
        actions.append(
            {
                "_index": ES_INDEX,
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
        success, errors = bulk(client, actions)
        return success

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks-file", required=True)
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--filename", required=True)
    args = parser.parse_args()

    with open(args.chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    count = index_chunks(chunks, args.document_id, args.filename)
    print(f"Indexed {count} chunks in Elasticsearch")
    sys.exit(0)
