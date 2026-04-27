"""Step 3: Chunk text into smaller segments."""
import argparse
import json
import sys

from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.common import CHUNK_OVERLAP, CHUNK_SIZE


def chunk_text(text: str, document_id: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )

    chunks = splitter.split_text(text)

    return [
        {
            "chunk_index": i,
            "content": chunk,
            "document_id": document_id,
            "char_count": len(chunk),
        }
        for i, chunk in enumerate(chunks)
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to extracted text file")
    parser.add_argument("--document-id", required=True)
    parser.add_argument("--output", default="/tmp/chunks.json")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text, args.document_id)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

    print(f"Created {len(chunks)} chunks")
    sys.exit(0)
