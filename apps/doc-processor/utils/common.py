import os


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


MINIO_ENDPOINT = get_env("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = get_env("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = get_env("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = get_env("MINIO_BUCKET", "documents")

QDRANT_HOST = get_env("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(get_env("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = get_env("QDRANT_COLLECTION", "document_chunks")

ES_URL = get_env("ELASTICSEARCH_URL", "http://elasticsearch:9200")
ES_INDEX = get_env("ELASTICSEARCH_INDEX", "document_chunks")

DB_URL = get_env("DATABASE_URL", "postgresql://postgres:postgres@postgresql:5432/knowledgebase")

EMBEDDING_MODEL = get_env("EMBEDDING_MODEL", "BAAI/bge-base-zh-v1.5")
CHUNK_SIZE = int(get_env("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(get_env("CHUNK_OVERLAP", "100"))
