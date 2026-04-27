"""Step 6: Update document metadata in PostgreSQL."""
import argparse
import json
import sys

from sqlalchemy import create_engine, text

from utils.common import DB_URL


def update_metadata(document_id: str, chunk_count: int, status: str = "completed"):
    engine = create_engine(DB_URL)

    with engine.connect() as conn:
        conn.execute(
            text(
                "UPDATE documents SET status = :status, chunk_count = :chunk_count, "
                "updated_at = NOW() WHERE id = :doc_id"
            ),
            {"status": status, "chunk_count": chunk_count, "doc_id": document_id},
        )
        conn.commit()

    engine.dispose()
    return True


def mark_failed(document_id: str, error_message: str):
    engine = create_engine(DB_URL)

    with engine.connect() as conn:
        conn.execute(
            text(
                "UPDATE documents SET status = 'failed', error_message = :error, "
                "updated_at = NOW() WHERE id = :doc_id"
            ),
            {"error": error_message, "doc_id": document_id},
        )
        conn.commit()

    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--chunks-file", required=True)
    parser.add_argument("--status", default="completed")
    args = parser.parse_args()

    with open(args.chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    update_metadata(args.document_id, len(chunks), args.status)
    print(f"Updated document {args.document_id}: status={args.status}, chunks={len(chunks)}")
    sys.exit(0)
