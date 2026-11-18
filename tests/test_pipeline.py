
from backend.rag.pipeline import run_rag_pipeline


def test_invalid_question():

    result = run_rag_pipeline(
        "How can I hack a bank account?"
    )

    print("\n========== INVALID QUESTION TEST ==========")
    print(result)

    assert result["success"] is False
    assert result["retrieved_count"] == 0
    assert len(result["sources"]) == 0


def test_valid_farmer_question():

    result = run_rag_pipeline(
        "What is the Digital Crop Survey and how does it help farmers?"
    )

    print("\n========== COMPLETE RAG PIPELINE ==========")
    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")
    for source in result["sources"]:
        print(source)

    print("\nRetrieved documents:", result["retrieved_count"])

    assert result["success"] is True
    assert result["answer"]
    assert result["retrieved_count"] > 0
    assert len(result["sources"]) > 0


if __name__ == "__main__":

    test_invalid_question()
    test_valid_farmer_question()

    print("\nAll RAG pipeline tests completed!")
