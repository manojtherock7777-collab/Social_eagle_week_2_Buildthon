
from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(
    documents,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """
    Split loaded PDF documents into smaller chunks.

    Args:
        documents: List of LangChain Document objects.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Shared characters between chunks.

    Returns:
        List of split Document objects with metadata.
    """

    if not documents:
        raise ValueError("No documents provided for splitting.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "Chunk overlap must be non-negative "
            "and smaller than chunk size."
        )

    # Create the text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    # Split documents while retaining metadata
    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError("Text splitting produced no chunks.")

    print("\n========== TEXT SPLITTING SUMMARY ==========")
    print(f"Original pages: {len(documents)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Chunk size: {chunk_size}")
    print(f"Chunk overlap: {chunk_overlap}")

    return chunks
