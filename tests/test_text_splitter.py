
from backend.rag.pdf_loader import load_pdf
from backend.rag.text_splitter import split_documents


PDF_PATH = "data/uploaded_pdfs/farmer_scheme.pdf"


def test_text_splitting():

    # Step 1: Load PDF
    documents = load_pdf(PDF_PATH)

    # Step 2: Split extracted text
    chunks = split_documents(
        documents,
        chunk_size=1000,
        chunk_overlap=200
    )

    # Step 3: Display summary
    print("\n========== CHUNK DETAILS ==========")

    for index, chunk in enumerate(chunks[:5]):

        print(f"\nChunk {index + 1}")

        print("Content:")
        print(chunk.page_content[:300])

        print("\nMetadata:")
        print(chunk.metadata)

        print("-" * 50)

    # Step 4: Validate
    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk.page_content.strip()
        assert "source" in chunk.metadata
        assert "page" in chunk.metadata

    print("\nText splitting test completed successfully!")


if __name__ == "__main__":
    test_text_splitting()
