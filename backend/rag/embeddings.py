
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env
load_dotenv()


def create_embedding_model():
    """
    Create and return the OpenAI embedding model.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv(
        "EMBEDDING_MODEL",
        "text-embedding-3-small"
    )

    if not api_key or api_key == "your_actual_api_key":
        raise ValueError(
            "OPENAI_API_KEY is missing. "
            "Please configure it in your .env file."
        )

    embeddings = OpenAIEmbeddings(
        model=model_name,
        api_key=api_key
    )

    print(f"Embedding model initialized: {model_name}")

    return embeddings
