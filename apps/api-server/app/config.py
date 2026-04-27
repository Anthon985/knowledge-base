from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Knowledge Base API"
    debug: bool = False

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgresql:5432/knowledgebase"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "documents"
    minio_secure: bool = False

    # Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "document_chunks"

    # Elasticsearch
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_index: str = "document_chunks"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Ollama
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "qwen2.5:7b"

    # Argo Workflows
    argo_server_url: str = "https://argo-workflows-server.argo:2746"
    argo_namespace: str = "argo"

    # Embedding
    embedding_model: str = "BAAI/bge-base-zh-v1.5"
    chunk_size: int = 512
    chunk_overlap: int = 100

    model_config = {"env_prefix": "KB_"}


settings = Settings()
