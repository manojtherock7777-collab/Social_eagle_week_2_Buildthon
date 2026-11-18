
from backend.rag.pdf_loader import load_pdf
from backend.rag.text_splitter import split_documents

from backend.rag.vector_store import (
    create_vector_store,
    save_vector_store,
    load_vector_store,
    search_vector_store
)

PDF_PATH = "data/uploaded_pdfs/farmer_scheme.pdf"


def test_vector_store():

    # Step 1: Load PDF
    documents = load_pdf(PDF_PATH)

    # Step 2: Split PDF into chunks
    chunks = split_documents(
        documents,
        chunk_size=1000,
        chunk_overlap=200
    )

    # Step 3: Create FAISS database
    vector_store = create_vector_store(chunks)

    # Step 4: Save FAISS database
    save_vector_store(vector_store)

    # Step 5: Load saved database
    loaded_store = load_vector_store()

    # Step 6: Perform similarity search
    question = "What are the agricultural schemes available for farmers in Tamil Nadu?"

    results = loaded_store.similarity_search(
        question,
        k=4
    )

    print("\n========== FAISS SEARCH RESULTS ==========")

    for index, result in enumerate(results, start=1):
        print(f"\nResult {index}")
        print("Content:")
        print(result.page_content[:400])
        print("\nMetadata:")
        print(result.metadata)

    assert len(results) > 0

    print("\nFAISS vector store test completed successfully!")


if __name__ == "__main__":
    test_vector_store()
