
from backend.rag.retriever import retrieve_documents
from backend.rag.generator import generate_answer


def test_answer_generation():

    question = (
        "What is the Digital Crop Survey "
        "and how does it help farmers?"
    )

    # Retrieve relevant documents
    documents = retrieve_documents(
        question,
        k=4
    )

    # Generate answer using GPT-4o-mini
    answer = generate_answer(
        question,
        documents
    )

    print("\n========== AI GENERATED ANSWER ==========")
    print(answer)

    assert answer
    assert len(answer.strip()) > 0

    print("\nAnswer generation test completed successfully!")


if __name__ == "__main__":
    test_answer_generation()
