
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_path: str):
    """
    Load a PDF document and extract its text page by page.

    Args:
        file_path: Path to the uploaded PDF.

    Returns:
        List of LangChain Document objects.
    """

    pdf_path = Path(file_path)

    # Step 1: Validate file existence
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    # Step 2: Validate file extension
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are supported."
        )

    # Step 3: Load PDF
    try:
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()

        if not documents:
            raise ValueError("The PDF contains no pages.")

        # Step 4: Validate extracted text
        extracted_text = [
            doc.page_content.strip()
            for doc in documents
            if doc.page_content.strip()
        ]

        if not extracted_text:
            raise ValueError(
                "No readable text found in the PDF. "
                "It may be a scanned document requiring OCR."
            )

        print(f"PDF loaded successfully: {pdf_path.name}")
        print(f"Total pages: {len(documents)}")
        print(f"Pages containing text: {len(extracted_text)}")

        return documents

    except Exception as error:
        raise RuntimeError(
            f"Error while loading PDF: {error}"
        ) from error
