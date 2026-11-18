
import os
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv

from backend.rag.pdf_loader import load_pdf
from backend.rag.text_splitter import split_documents
from backend.rag.vector_store import (
    create_vector_store,
    load_vector_store,
    save_vector_store
)

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

HASH_FILE = PROJECT_ROOT / "data" / "uploaded_pdfs" / "processed_files.json"


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a PDF."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for block in iter(lambda: file.read(4096), b""):
            sha256.update(block)

    return sha256.hexdigest()


def load_processed_files() -> dict:
    """Load previously processed PDF hashes."""

    if not HASH_FILE.exists():
        return {}

    try:
        with open(HASH_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        raise RuntimeError(
            "Processed PDF history is unreadable. "
            "Please check processed_files.json."
        )


def save_processed_files(processed_files: dict):
    """Save processed PDF history."""

    HASH_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(HASH_FILE, "w", encoding="utf-8") as file:
        json.dump(processed_files, file, indent=4)


def ingest_pdf(file_path: str) -> dict:

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    file_hash = calculate_file_hash(str(pdf_path))

    processed_files = load_processed_files()

    if file_hash in processed_files:
        return {
            "success": True,
            "duplicate": True,
            "filename": pdf_path.name,
            "pages_processed": 0,
            "chunks_added": 0,
            "message": "This PDF has already been processed."
        }

    # Load PDF and extract text
    documents = load_pdf(str(pdf_path))

    # Split extracted text into chunks
    chunks = split_documents(documents)

    if not chunks:
        raise ValueError("No text chunks were generated.")

    # Add chunks to FAISS
    index_path = Path(
        os.getenv(
            "FAISS_INDEX_PATH",
            "vector_db/faiss_index"
        )
    )

    if not index_path.is_absolute():
        index_path = PROJECT_ROOT / index_path

    faiss_file = index_path / "index.faiss"
    pickle_file = index_path / "index.pkl"

    if faiss_file.exists() and pickle_file.exists():

        vector_store = load_vector_store()
        vector_store.add_documents(chunks)

        print("New document chunks added to existing FAISS.")

    else:

        vector_store = create_vector_store(chunks)

        print("New FAISS database created.")

    # Save updated FAISS index
    save_vector_store(vector_store)

    # Record hash only after successful indexing
    processed_files[file_hash] = {
        "filename": pdf_path.name,
        "chunks_added": len(chunks)
    }

    save_processed_files(processed_files)

    return {
        "success": True,
        "duplicate": False,
        "filename": pdf_path.name,
        "pages_processed": len(documents),
        "chunks_added": len(chunks),
        "message": "PDF successfully added to FAISS."
    }
