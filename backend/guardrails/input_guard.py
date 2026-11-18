
import re

MAX_QUESTION_LENGTH = 2000

# Basic English and Tamil agriculture-related keywords.
ALLOWED_TOPICS = [
    "farmer",
    "farmers",
    "agriculture",
    "agricultural",
    "farming",
    "scheme",
    "schemes",
    "subsidy",
    "subsidies",
    "crop",
    "crops",
    "irrigation",
    "fertilizer",
    "fertiliser",
    "seeds",
    "insurance",
    "horticulture",
    "loan",
    "loans",
    "eligibility",
    "benefit",
    "benefits",
    "financial assistance",
    "government",
    "tn",
    "tamil nadu",
    "விவசாயி",
    "விவசாயிகள்",
    "விவசாயம்",
    "விவசாய",
    "திட்டம்",
    "திட்டங்கள்",
    "மானியம்",
    "பயிர்",
    "பாசனம்",
    "உதவி",
    "கடன்",
    "காப்பீடு",
    "உரம்",
    "விதை",
]

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?rules",
    r"reveal\s+(your\s+)?system\s+prompt",
    r"show\s+(your\s+)?hidden\s+instructions",
    r"act\s+as\s+an\s+unrestricted",
    r"bypass\s+(all\s+)?restrictions",
    r"disregard\s+(all\s+)?instructions",
]


def validate_input(question: str) -> dict:
    """
    Validate farmer-related questions before retrieval.
    """

    if not isinstance(question, str):
        return {
            "allowed": False,
            "message": "Please enter a valid text question."
        }

    question = question.strip()

    if not question:
        return {
            "allowed": False,
            "message": "Please enter your question."
        }

    if len(question) > MAX_QUESTION_LENGTH:
        return {
            "allowed": False,
            "message": "Your question is too long. Please shorten it."
        }

    # Detect basic English prompt-injection patterns.
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, question, re.IGNORECASE):
            return {
                "allowed": False,
                "message": (
                    "Your request contains instructions that "
                    "cannot be followed. Please ask a question "
                    "about Tamil Nadu farmer welfare schemes."
                )
            }

    # Accept questions containing relevant agriculture topics.
    question_lower = question.lower()

    has_allowed_topic = any(
        keyword in question_lower
        for keyword in ALLOWED_TOPICS
    )

    if not has_allowed_topic:
        return {
            "allowed": False,
            "message": (
                "I can help with Tamil Nadu agriculture, "
                "farmer welfare schemes, eligibility, "
                "subsidies and related benefits. "
                "Please ask a question about these topics."
            )
        }

    return {
        "allowed": True,
        "message": "Input validation successful.",
        "question": question
    }
