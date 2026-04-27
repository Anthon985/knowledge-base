import io
import uuid

from minio import Minio

from app.config import settings


class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(settings.minio_bucket):
            self.client.make_bucket(settings.minio_bucket)

    def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        object_name = f"{uuid.uuid4()}/{filename}"
        self.client.put_object(
            settings.minio_bucket,
            object_name,
            io.BytesIO(file_data),
            length=len(file_data),
            content_type=content_type,
        )
        return object_name

    def download_file(self, object_name: str) -> bytes:
        response = self.client.get_object(settings.minio_bucket, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete_file(self, object_name: str):
        self.client.remove_object(settings.minio_bucket, object_name)

    def get_presigned_url(self, object_name: str, expires_hours: int = 1) -> str:
        from datetime import timedelta

        return self.client.presigned_get_object(
            settings.minio_bucket,
            object_name,
            expires=timedelta(hours=expires_hours),
        )


storage_service = StorageService()
