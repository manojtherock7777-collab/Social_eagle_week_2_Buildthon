
from backend.rag.pdf_loader import load_pdf

PDF_PATH = "data/uploaded_pdfs/farmer_scheme.pdf"


def test_pdf_loader():

    documents = load_pdf(PDF_PATH)

    print("\n========== PDF SUMMARY ==========")
    print("Total pages:", len(documents))

    valid_pages = [
        doc for doc in documents
        if doc.page_content.strip()
    ]

    print("Pages containing text:", len(valid_pages))

    print("\n========== FIRST NON-EMPTY PAGE ==========")

    if valid_pages:
        first_page = valid_pages[0]

        print("Page number:", first_page.metadata.get("page"))
        print("Page label:", first_page.metadata.get("page_label"))
        print("Source:", first_page.metadata.get("source"))

        print("\nExtracted content:")
        print(first_page.page_content[:2000])

    else:
        print("No readable text found.")

    print("\n========== PAGE VERIFICATION ==========")

    for doc in valid_pages[:5]:
        print(
            f"Page {doc.metadata.get('page_label')}: "
            f"{len(doc.page_content)} characters"
        )


if __name__ == "__main__":
    test_pdf_loader()
