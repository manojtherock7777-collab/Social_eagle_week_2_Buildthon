
import re
import math
from collections import Counter

from backend.rag.vector_store import load_vector_store


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DUPLICATE_THRESHOLD = 0.92

RRF_CONSTANT = 60

BM25_K1 = 1.5
BM25_B = 0.75

STOPWORDS = {
    "what", "is", "the", "a", "an", "for", "to",
    "of", "in", "on", "and", "or", "are", "was",
    "were", "how", "does", "do", "can", "will",
    "with", "by", "from", "available", "farmers",
    "farmer", "provided", "provide", "use",
    "using", "about", "which", "that", "this",
    "their", "they", "it", "be", "has", "have"
}


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_text(text: str) -> str:

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    text = re.sub(r"[^\w\s]", " ", text)

    return text.strip()


def tokenize(text: str) -> list:

    words = normalize_text(text).split()

    return [
        word for word in words
        if len(word) > 1 and word not in STOPWORDS
    ]


# --------------------------------------------------
# DUPLICATE DETECTION
# --------------------------------------------------

def calculate_similarity(text1: str, text2: str) -> float:

    words1 = set(tokenize(text1))
    words2 = set(tokenize(text2))

    if not words1 or not words2:
        return 0.0

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    return intersection / union


# --------------------------------------------------
# DOCUMENT IDENTIFICATION
# --------------------------------------------------

def get_document_key(document):

    return (
        document.page_content,
        document.metadata.get("source", "Unknown"),
        str(
            document.metadata.get(
                "page_label",
                document.metadata.get("page", "Unknown")
            )
        )
    )


# --------------------------------------------------
# LOAD DOCUMENTS FROM FAISS
# --------------------------------------------------

def load_all_documents(vector_store):

    documents = []

    for document_id in vector_store.index_to_docstore_id.values():

        document = vector_store.docstore.search(document_id)

        if not hasattr(document, "page_content"):
            continue

        if not document.page_content.strip():
            continue

        documents.append(document)

    return documents


# --------------------------------------------------
# BM25 KEYWORD SEARCH
# --------------------------------------------------

def keyword_search(vector_store, question: str, limit: int):

    query_words = set(tokenize(question))

    if not query_words:
        return []

    documents = load_all_documents(vector_store)

    if not documents:
        return []

    # Tokenize all document chunks
    tokenized_documents = [
        tokenize(document.page_content)
        for document in documents
    ]

    total_documents = len(documents)

    document_lengths = [
        len(tokens)
        for tokens in tokenized_documents
    ]

    average_length = (
        sum(document_lengths) / total_documents
        if total_documents else 0
    )

    if average_length == 0:
        return []

    # Calculate document frequency
    document_frequency = Counter()

    for tokens in tokenized_documents:

        for word in set(tokens):

            document_frequency[word] += 1

    scored_documents = []

    # Calculate BM25 score
    for document, tokens, doc_length in zip(
        documents,
        tokenized_documents,
        document_lengths
    ):

        word_frequency = Counter(tokens)

        bm25_score = 0.0

        for word in query_words:

            frequency = word_frequency.get(word, 0)

            if frequency == 0:
                continue

            df = document_frequency[word]

            # Inverse document frequency
            idf = math.log(
                1 + (
                    total_documents - df + 0.5
                ) / (
                    df + 0.5
                )
            )

            # BM25 term frequency component
            denominator = frequency + BM25_K1 * (
                1 - BM25_B
                + BM25_B * doc_length / average_length
            )

            term_score = (
                frequency * (BM25_K1 + 1)
            ) / denominator

            bm25_score += idf * term_score

        if bm25_score > 0:

            scored_documents.append({
                "document": document,
                "keyword_score": bm25_score
            })

    # Deterministic ranking
    scored_documents.sort(
        key=lambda item: (
            -item["keyword_score"],
            get_document_key(item["document"])
        )
    )

    return scored_documents[:limit]


# --------------------------------------------------
# KEYWORD COVERAGE
# --------------------------------------------------

def calculate_keyword_coverage(document, question):

    question_words = set(tokenize(question))

    document_words = set(
        tokenize(document.page_content)
    )

    if not question_words:
        return 0.0

    matched_words = question_words.intersection(
        document_words
    )

    return len(matched_words) / len(question_words)


# --------------------------------------------------
# HYBRID RETRIEVAL
# --------------------------------------------------

def retrieve_documents(
    question: str,
    k: int = 4,
    fetch_k: int = 32
):

    # Validate input
    if not isinstance(question, str) or not question.strip():

        raise ValueError(
            "Question cannot be empty."
        )

    if len(question) > 2000:

        raise ValueError(
            "Question is too long."
        )

    if k <= 0:

        raise ValueError(
            "k must be greater than zero."
        )

    if fetch_k < k:

        raise ValueError(
            "fetch_k must be greater than or equal to k."
        )

    vector_store = load_vector_store()

    # ----------------------------------------------
    # 1. SEMANTIC SEARCH USING FAISS
    # ----------------------------------------------

    semantic_results = (
        vector_store.similarity_search_with_score(
            question,
            k=fetch_k
        )
    )

    semantic_rank = {}
    document_lookup = {}
    distance_lookup = {}

    for rank, (document, distance) in enumerate(
        semantic_results,
        start=1
    ):

        key = get_document_key(document)

        semantic_rank[key] = rank
        document_lookup[key] = document
        distance_lookup[key] = float(distance)

    # ----------------------------------------------
    # 2. KEYWORD SEARCH USING BM25
    # ----------------------------------------------

    lexical_results = keyword_search(
        vector_store,
        question,
        fetch_k
    )

    lexical_rank = {}
    keyword_score_lookup = {}

    for rank, item in enumerate(
        lexical_results,
        start=1
    ):

        document = item["document"]

        key = get_document_key(document)

        lexical_rank[key] = rank

        document_lookup[key] = document

        keyword_score_lookup[key] = (
            item["keyword_score"]
        )

    # ----------------------------------------------
    # 3. COMBINE RESULTS USING RRF
    # ----------------------------------------------

    all_keys = list(semantic_rank.keys())

    for key in lexical_rank:

        if key not in semantic_rank:

            all_keys.append(key)

    combined_results = []

    for key in all_keys:

        semantic_position = semantic_rank.get(key)

        lexical_position = lexical_rank.get(key)

        hybrid_score = 0.0

        if semantic_position is not None:

            hybrid_score += (
                1 / (RRF_CONSTANT + semantic_position)
            )

        if lexical_position is not None:

            hybrid_score += (
                1 / (RRF_CONSTANT + lexical_position)
            )

        document = document_lookup[key]

        keyword_coverage = calculate_keyword_coverage(
            document,
            question
        )

        combined_results.append({

            "key": key,

            "document": document,

            "hybrid_score": hybrid_score,

            "keyword_coverage": keyword_coverage,

            "keyword_score": keyword_score_lookup.get(
                key,
                0.0
            )

        })

    # ----------------------------------------------
    # 4. IMPROVED RANKING
    # ----------------------------------------------

    combined_results.sort(
        key=lambda item: (
            -item["hybrid_score"],
            -item["keyword_coverage"],
            -item["keyword_score"],
            distance_lookup.get(
                item["key"],
                float("inf")
            ),
            item["key"]
        )
    )

    # ----------------------------------------------
    # 5. REMOVE NEAR-DUPLICATE CHUNKS
    # ----------------------------------------------

    unique_results = []

    duplicate_count = 0

    for item in combined_results:

        document = item["document"]

        content = document.page_content.strip()

        if not content:
            continue

        is_duplicate = any(

            calculate_similarity(
                content,
                previous["content"]
            ) >= DUPLICATE_THRESHOLD

            for previous in unique_results

        )

        if is_duplicate:

            duplicate_count += 1

            continue

        page = (
            document.metadata.get("page_label")
            or document.metadata.get("page", "Unknown")
        )

        key = item["key"]

        result = {

            "content": content,

            "source": document.metadata.get(
                "source",
                "Unknown"
            ),

            "page": str(page),

            "distance_score": distance_lookup.get(key),

            "hybrid_score": item["hybrid_score"],

            "keyword_coverage": item["keyword_coverage"],

            "keyword_score": item["keyword_score"]

        }

        unique_results.append(result)

        if len(unique_results) >= k:
            break

    # ----------------------------------------------
    # 6. RETRIEVAL SUMMARY
    # ----------------------------------------------

    print(
        "\n========== HYBRID RETRIEVAL SUMMARY =========="
    )

    print(
        f"Semantic candidates: {len(semantic_results)}"
    )

    print(
        f"BM25 keyword candidates: {len(lexical_results)}"
    )

    print(
        f"Combined candidates: {len(combined_results)}"
    )

    print(
        f"Duplicate chunks removed: {duplicate_count}"
    )

    print(
        f"Final results returned: {len(unique_results)}"
    )

    return unique_results
