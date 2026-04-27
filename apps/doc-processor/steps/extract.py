"""Step 2: Extract text from document."""
import argparse
import json
import sys
import tempfile

from minio import Minio

from utils.common import MINIO_ACCESS_KEY, MINIO_BUCKET, MINIO_ENDPOINT, MINIO_SECRET_KEY


def extract_text(storage_path: str, detect_result: dict) -> str:
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    with tempfile.NamedTemporaryFile(
        suffix=f".{detect_result['extension']}", delete=False
    ) as tmp:
        client.fget_object(MINIO_BUCKET, storage_path, tmp.name)
        tmp_path = tmp.name

    category = detect_result["category"]

    if category == "image":
        return _extract_from_image(tmp_path)
    else:
        return _extract_with_unstructured(tmp_path)


def _extract_with_unstructured(file_path: str) -> str:
    from unstructured.partition.auto import partition

    elements = partition(filename=file_path)
    return "\n\n".join(str(el) for el in elements)


def _extract_from_image(file_path: str) -> str:
    import pytesseract
    from PIL import Image

    image = Image.open(file_path)
    text = pytesseract.image_to_string(image, lang="chi_sim+eng")
    return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--storage-path", required=True)
    parser.add_argument("--detect-result", required=True)
    parser.add_argument("--output", default="/tmp/extracted-text.txt")
    args = parser.parse_args()

    with open(args.detect_result, "r", encoding="utf-8") as f:
        detect_result = json.load(f)

    text = extract_text(args.storage_path, detect_result)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Extracted {len(text)} characters")
    sys.exit(0)
