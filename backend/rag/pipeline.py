
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.guardrails.input_guard import validate_input
from backend.rag.retriever import retrieve_documents
from backend.rag.generator import generate_answer


# --------------------------------------------------
# ENVIRONMENT CONFIGURATION
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# TRANSLATE TAMIL QUESTION FOR RETRIEVAL
# --------------------------------------------------

def translate_query_to_english(question: str) -> str:
    """
    Translate a Tamil question into English for
    searching English PDF documents.

    This function translates only the retrieval query.
    The original question is preserved for answer generation.
    """

    model_name = os.getenv(
        "OPENAI_MODEL",
        "gpt-4o-mini"
    )

    llm = ChatOpenAI(
        model=model_name,
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([

        (
            "system",
            """
You are a translation assistant.

Translate the user's question into English.

Rules:
- Translate the meaning accurately.
- Preserve scheme names, agricultural terms and numbers.
- Do not answer the question.
- Do not add explanations.
- Return only the English translation.
"""
        ),

        (
            "human",
            """
Translate this question into English:

{question}
"""
        )

    ])

    response = (prompt | llm).invoke({
        "question": question
    })

    translated_question = response.content.strip()

    if not translated_question:
        raise ValueError(
            "Question translation returned an empty result."
        )

    return translated_question


# --------------------------------------------------
# RAG PIPELINE
# --------------------------------------------------

def run_rag_pipeline(
    question: str,
    language: str = "English"
) -> dict:
    """
    Execute the complete bilingual farmer schemes RAG pipeline.

    Tamil question:
        Translate for retrieval.
        Generate final answer in Tamil.

    English question:
        Retrieve using original question.
        Generate final answer in English.
    """

    # STEP 1: VALIDATE LANGUAGE

    if language not in ["English", "தமிழ்"]:
        language = "English"

    # STEP 2: VALIDATE USER INPUT

    input_result = validate_input(question)

    if not input_result["allowed"]:

        return {
            "success": False,
            "answer": input_result["message"],
            "sources": [],
            "retrieved_count": 0
        }

    validated_question = input_result["question"]

    try:

        # STEP 3: PREPARE RETRIEVAL QUERY

        if language == "தமிழ்":

            print(
                "\nTamil question detected. "
                "Translating retrieval query..."
            )

            retrieval_question = translate_query_to_english(
                validated_question
            )

            print(
                f"English retrieval query: {retrieval_question}"
            )

        else:

            retrieval_question = validated_question

        # STEP 4: RETRIEVE DOCUMENTS

        retrieved_documents = retrieve_documents(
            retrieval_question,
            k=4,
            fetch_k=32
        )

        print(
            f"Retrieved documents: {len(retrieved_documents)}"
        )

        # STEP 5: HANDLE NO RESULTS

        if not retrieved_documents:

            if language == "தமிழ்":

                fallback_answer = (
                    "உங்கள் கேள்விக்குப் பதிலளிக்கத் தேவையான "
                    "போதுமான தகவல்கள் ஆவணங்களில் கிடைக்கவில்லை."
                )

            else:

                fallback_answer = (
                    "I could not find sufficient information "
                    "in the available documents to answer "
                    "your question reliably."
                )

            return {
                "success": True,
                "answer": fallback_answer,
                "sources": [],
                "retrieved_count": 0
            }

        # STEP 6: GENERATE ANSWER

        # IMPORTANT:
        # Pass the original question, not the translated query.
        # This ensures the answer follows the selected language.

        answer = generate_answer(
            validated_question,
            retrieved_documents,
            language
        )

        # STEP 7: COLLECT SOURCE REFERENCES

        sources = []

        for document in retrieved_documents:

            reference = {
                "source": document["source"],
                "page": document["page"]
            }

            if reference not in sources:
                sources.append(reference)

        # STEP 8: RETURN RESULT

        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "retrieved_count": len(retrieved_documents)
        }

    except Exception as error:

        print(f"RAG pipeline error: {error}")

        if language == "தமிழ்":

            error_message = (
                "உங்கள் கேள்வியைச் செயல்படுத்தும்போது "
                "பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்."
            )

        else:

            error_message = (
                "Sorry, an error occurred while processing "
                "your question. Please try again."
            )

        return {
            "success": False,
            "answer": error_message,
            "sources": [],
            "retrieved_count": 0
        }
