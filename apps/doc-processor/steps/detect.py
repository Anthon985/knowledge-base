"""Step 1: Detect file type from MinIO storage."""
import argparse
import json
import mimetypes
import sys

from minio import Minio

from utils.common import MINIO_ACCESS_KEY, MINIO_BUCKET, MINIO_ENDPOINT, MINIO_SECRET_KEY


def detect_type(storage_path: str) -> dict:
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    stat = client.stat_object(MINIO_BUCKET, storage_path)
    content_type = stat.content_type or "application/octet-stream"

    ext = storage_path.rsplit(".", 1)[-1].lower() if "." in storage_path else ""
    guessed_type = mimetypes.guess_type(storage_path)[0] or content_type

    file_category = _categorize(ext, guessed_type)

    return {
        "storage_path": storage_path,
        "content_type": guessed_type,
        "extension": ext,
        "category": file_category,
        "size": stat.size,
    }


def _categorize(ext: str, content_type: str) -> str:
    pdf_types = {"pdf"}
    doc_types = {"docx", "doc"}
    spreadsheet_types = {"xlsx", "xls", "csv"}
    presentation_types = {"pptx", "ppt"}
    image_types = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"}
    text_types = {"txt", "md", "html", "htm", "rst"}

    if ext in pdf_types:
        return "pdf"
    elif ext in doc_types:
        return "document"
    elif ext in spreadsheet_types:
        return "spreadsheet"
    elif ext in presentation_types:
        return "presentation"
    elif ext in image_types:
        return "image"
    elif ext in text_types:
        return "text"
    else:
        return "unknown"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage-path", required=True)
    parser.add_argument("--output", default="/tmp/detect-result.json")
    args = parser.parse_args()

    result = detect_type(args.storage_path)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)
