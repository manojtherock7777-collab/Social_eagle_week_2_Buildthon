
from backend.rag.embeddings import create_embedding_model


def test_embedding_model():
    embeddings = create_embedding_model()

    sample_text = "Tamil Nadu farmer welfare schemes"

    vector = embeddings.embed_query(sample_text)

    print("\n========== EMBEDDING TEST ==========")
    print("Input text:", sample_text)
    print("Vector dimensions:", len(vector))
    print("First 5 vector values:", vector[:5])

    assert len(vector) == 1536

    print("\nEmbedding test completed successfully!")


if __name__ == "__main__":
    test_embedding_model()
