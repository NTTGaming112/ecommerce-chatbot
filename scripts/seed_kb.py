"""
Seed the ChromaDB knowledge base with documents from kb/.

Usage:
    uv run python scripts/seed_kb.py           # incremental seed (skip existing docs)
    uv run python scripts/seed_kb.py --reset   # drop the collection and re-ingest everything

Idempotent: each .md file becomes one document (id = relative path), split into
chunks with document_id metadata so they can be re-ingested safely.
"""
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

KB_DIR = Path(__file__).resolve().parent.parent / "kb"
COLLECTION_NAME = "support_docs"


def load_documents() -> list[tuple[str, str]]:
    """Return (document_id, text) for every .md file under kb/."""
    if not KB_DIR.exists():
        print(f"Knowledge base directory not found: {KB_DIR}")
        sys.exit(1)

    docs = []
    for path in sorted(KB_DIR.rglob("*.md")):
        document_id = path.relative_to(KB_DIR).as_posix()
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            print(f"  ! skipped empty file: {document_id}")
            continue
        docs.append((document_id, text))
    return docs


def existing_document_ids(vector_store) -> set[str]:
    """Read metadata of everything currently in the collection."""
    stored = vector_store.get(include=["metadatas"])
    return {
        m.get("document_id")
        for m in stored.get("metadatas", [])
        if m and m.get("document_id")
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed ChromaDB with kb/ documents")
    parser.add_argument("--reset", action="store_true",
                        help="Delete the collection and re-ingest everything")
    args = parser.parse_args()

    # Imports here so --help does not load heavy ML dependencies.
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from app.services.retrieval_service import retrieval_service

    if retrieval_service.vector_store is None:
        print("Vector store failed to initialize (check chromadb install).")
        sys.exit(1)

    if args.reset:
        retrieval_service.vector_store.delete_collection()
        print("Collection deleted.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    already = existing_document_ids(retrieval_service.vector_store)

    added = 0
    for document_id, text in load_documents():
        if document_id in already:
            print(f"  = already ingested: {document_id}")
            continue

        chunks = splitter.split_text(text)
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        retrieval_service.add_documents(chunks, metadatas)
        added += 1
        print(f"  + ingested {document_id} ({len(chunks)} chunks)")

    print(f"Done. {added} new document(s), {len(already)} skipped.")


if __name__ == "__main__":
    main()
