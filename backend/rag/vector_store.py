
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS

from backend.rag.embeddings import create_embedding_model

load_dotenv()


def create_vector_store(chunks):
    """
    Convert document chunks into embeddings
    and create a FAISS vector database.
    """

    if not chunks:
        raise ValueError("No document chunks provided.")

    embeddings = create_embedding_model()

    print("\nCreating FAISS vector database...")
    print(f"Total chunks to process: {len(chunks)}")

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    print("FAISS vector database created successfully!")

    return vector_store


def save_vector_store(vector_store):
    """
    Save the FAISS index to local storage.
    """

    index_path = Path(
        os.getenv(
            "FAISS_INDEX_PATH",
            "vector_db/faiss_index"
        )
    )

    index_path.mkdir(parents=True, exist_ok=True)

    vector_store.save_local(str(index_path))

    print("\nFAISS index saved successfully!")
    print(f"Storage location: {index_path.resolve()}")

    return index_path


def load_vector_store():
    """
    Load an existing FAISS index from local storage.
    """

    index_path = Path(
        os.getenv(
            "FAISS_INDEX_PATH",
            "vector_db/faiss_index"
        )
    )

    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {index_path}"
        )

    embeddings = create_embedding_model()

    vector_store = FAISS.load_local(
        str(index_path),
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("FAISS index loaded successfully!")

    return vector_store


def search_vector_store(question, k=4):
    """
    Search FAISS for the most relevant document chunks.
    """

    if not question or not question.strip():
        raise ValueError("Search question cannot be empty.")

    vector_store = load_vector_store()

    results = vector_store.similarity_search(
        question,
        k=k
    )

    print(f"\nSearch completed. Results found: {len(results)}")

    return results
