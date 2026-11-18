
from backend.rag.retriever import retrieve_documents


def test_retrieval():

    question = (
        "What agricultural schemes and benefits "
        "are available for farmers in Tamil Nadu?"
    )

    results = retrieve_documents(
        question,
        k=4,
        fetch_k=16
    )

    print("\n========== RETRIEVAL RESULTS ==========")

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("Source:", result["source"])
        print("Page:", result["page"])
        print("Distance:", result["distance_score"])
        print("Content:")
        print(result["content"][:400])

    assert len(results) > 0
    assert len(results) <= 4

    # Confirm that returned content is distinct
    normalized_contents = [
        " ".join(result["content"].lower().split())
        for result in results
    ]

    assert len(normalized_contents) == len(set(normalized_contents))

    print("\nRetrieval quality test completed successfully!")


if __name__ == "__main__":
    test_retrieval()
