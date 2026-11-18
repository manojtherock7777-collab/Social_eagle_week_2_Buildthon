
# --------------------------------------------------
# OUTPUT GUARDRAIL
# --------------------------------------------------

def validate_output(
    answer: str,
    retrieved_documents: list,
    language: str = "English"
) -> str:
    """
    Validate the AI-generated answer.

    Responsibilities:
    1. Check whether the answer is valid.
    2. Check whether retrieved documents are available.
    3. Return a language-specific fallback if required.
    4. Return only the answer without appending source references.

    Source references are returned separately by pipeline.py.
    """

    # --------------------------------------------------
    # STEP 1: LANGUAGE-SPECIFIC FALLBACK
    # --------------------------------------------------

    if language == "தமிழ்":

        fallback_message = (
            "கிடைக்கப்பெற்ற ஆவணங்களில் உங்கள் கேள்விக்குப் "
            "பதிலளிக்கப் போதுமான தகவல்கள் இல்லை. "
            "தயவுசெய்து உங்கள் கேள்வியை மாற்றி முயற்சிக்கவும்."
        )

    else:

        fallback_message = (
            "I could not find sufficient information in the "
            "available documents to answer your question reliably. "
            "Please try rephrasing your question."
        )

    # --------------------------------------------------
    # STEP 2: VALIDATE GENERATED ANSWER
    # --------------------------------------------------

    if not isinstance(answer, str):

        return fallback_message

    if not answer.strip():

        return fallback_message

    # --------------------------------------------------
    # STEP 3: VALIDATE RETRIEVED DOCUMENTS
    # --------------------------------------------------

    if not retrieved_documents:

        return fallback_message

    # --------------------------------------------------
    # STEP 4: RETURN CLEAN ANSWER
    # --------------------------------------------------

    # Do not append source references here.
    # pipeline.py already collects source filenames and pages.
    # Streamlit displays them separately under View Sources.

    validated_answer = answer.strip()

    return validated_answer
