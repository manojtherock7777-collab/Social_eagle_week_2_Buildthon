TAMIL NADU FARMERS AI ASSISTANT
================================

PROJECT OVERVIEW
----------------
A bilingual Retrieval-Augmented Generation (RAG) application that helps users
find information about Tamil Nadu farmer welfare schemes, subsidies, benefits
and application guidance from uploaded PDF reference documents.

The application uses:
- Streamlit for the frontend
- FastAPI for the backend
- LangChain for RAG orchestration
- OpenAI GPT-4o-mini for answer generation and Tamil-query translation
- OpenAI text-embedding-3-small for embeddings
- FAISS for persistent vector search
- PyPDF / LangChain PDF loader for PDF text extraction

IMPORTANT
---------
Answers are based on the documents available to the application. Verify scheme
rules, eligibility, subsidy amounts, deadlines and application procedures with
the relevant Tamil Nadu government department.

MAIN FEATURES
-------------
1. Ask questions in English or Tamil.
2. Translate Tamil questions into English for retrieval from English PDF text.
3. Preserve the original question for answer generation in the selected language.
4. Retrieve relevant chunks using semantic and keyword/lexical search.
5. Combine rankings using Reciprocal Rank Fusion (RRF).
6. Remove near-duplicate chunks.
7. Generate answers grounded in retrieved PDF context.
8. Display source filenames and page references.
9. Upload PDFs through the FastAPI API.
10. Validate PDF extension, file size and PDF signature.
11. Detect duplicate uploads using SHA-256 hashes.
12. Display PDF inventory in the Streamlit sidebar when GET /uploaded-pdfs
    has been implemented in the backend.
13. Maintain chat history during the current Streamlit session.

HIGH-LEVEL ARCHITECTURE
-----------------------

                         +------------------+
                         |       USER       |
                         +---------+--------+
                                   |
                                   v
                         +------------------+
                         | Streamlit UI     |
                         | English / Tamil  |
                         +---------+--------+
                                   |
                                   v
                         +------------------+
                         | FastAPI Backend  |
                         | /chat            |
                         +---------+--------+
                                   |
                                   v
                         +------------------+
                         | RAG Pipeline     |
                         | Input Guard      |
                         +---------+--------+
                                   |
                      +------------+------------+
                      |                         |
                      v                         v
              +---------------+        +----------------+
              | Tamil query?  |        | English query  |
              +-------+-------+        +--------+-------+
                      |                         |
                      v                         |
              +---------------+                 |
              | Translate to  |                 |
              | English       |                 |
              +-------+-------+                 |
                      +------------+------------+
                                   |
                                   v
                         +------------------+
                         | Hybrid Retriever |
                         +--------+---------+
                                  |
                      +-----------+-----------+
                      |                       |
                      v                       v
              +---------------+       +----------------+
              | FAISS semantic|       | Keyword search |
              | retrieval     |       |                |
              +-------+-------+       +--------+-------+
                      |                        |
                      +-----------+------------+
                                  |
                                  v
                         +------------------+
                         | RRF ranking and  |
                         | duplicate filter |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | Retrieved PDF    |
                         | context + sources|
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | OpenAI GPT-4o-mini|
                         | Grounded answer  |
                         +--------+---------+
                                  |
                                  v
                         +------------------+
                         | Answer + source  |
                         | pages to Streamlit|
                         +------------------+


PDF INGESTION FLOW
------------------

 PDF upload
     |
     v
 Validate extension, size and PDF signature
     |
     v
 Calculate SHA-256 hash
     |
     v
 Is this file already processed?
     |                         |
    Yes                        No
     |                         |
     v                         v
 Skip duplicate          Save uploaded PDF
     |                         |
     |                         v
     |                   Extract PDF text
     |                         |
     |                         v
     |                   Readable text found?
     |                     |          |
     |                    No         Yes
     |                     |          |
     |                     v          v
     |                Return error  Split into chunks
     |                                |
     |                                v
     |                         Create embeddings
     |                                |
     |                                v
     |                           Add to FAISS
     |                                |
     |                                v
     |                         Save index and
     |                         processed manifest
     |                                |
     +----------------+---------------+
                      |
                      v
                Ingestion result


QUESTION-ANSWERING FLOW
-----------------------

 User asks a question
          |
          v
 Validate input and selected language
          |
          v
 Tamil question?
    |             |
   Yes            No
    |             |
    v             v
 Translate      Use original
 retrieval      English query
 query              |
    |               |
    +-------+-------+
            |
            v
    Hybrid retrieval
            |
       +----+----+
       |         |
       v         v
    FAISS     Keyword /
    semantic  lexical search
       |         |
       +----+----+
            |
            v
      RRF ranking
            |
            v
    Remove near duplicates
            |
            v
    Build context with source metadata
            |
            v
    Generate answer using original
    question and selected language
            |
            v
    Return answer, source pages
    and retrieval count
            |
            v
    Display in Streamlit


PDF INGESTION DETAILS
---------------------
- Maximum upload size configured in the API: 25 MB.
- Duplicate detection uses a SHA-256 file hash.
- Text splitting configuration: 1,000-character chunks and 200-character overlap.
- Embedding model: text-embedding-3-small.
- Vector store: local persistent FAISS index.
- OCR is not enabled. Scanned/image-only PDFs without extractable text are
  rejected rather than indexed as empty content.

PROJECT STRUCTURE
-----------------
TN_FARMERS_RAG_ASSISTANT/
|
+-- backend/
|   +-- main.py
|   +-- rag/
|   |   +-- pdf_loader.py
|   |   +-- text_splitter.py
|   |   +-- embeddings.py
|   |   +-- vector_store.py
|   |   +-- retriever.py
|   |   +-- generator.py
|   |   +-- ingestion.py
|   |   +-- pipeline.py
|   +-- guardrails/
|       +-- input_guard.py
|       +-- output_guard.py
|
+-- frontend/
|   +-- app.py
|
+-- data/
|   +-- uploaded_pdfs/
|   +-- scraped_data/
|
+-- vector_db/
|   +-- faiss_index/
|
+-- tests/
|
+-- .env
+-- .gitignore
+-- requirements.txt
+-- README.md

CONFIGURATION
-------------
Create a .env file in the project root:

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
FAISS_INDEX_PATH=vector_db/faiss_index

Use your own API key locally. Do not commit .env to GitHub or share the key.


RUN THE APPLICATION
-------------------
Terminal 1 - FastAPI backend:

uvicorn backend.main:app --reload

Backend:
http://127.0.0.1:8000/

Health:
http://127.0.0.1:8000/health

Swagger documentation:
http://127.0.0.1:8000/docs

Terminal 2 - Streamlit frontend:

streamlit run frontend/app.py

Open the local URL printed by Streamlit, usually:
http://localhost:8501

API ENDPOINTS
-------------
GET  /             API welcome/status response
GET  /health       API health and FAISS path check
POST /chat         Ask a question and receive answer and sources
POST /upload-pdf   Upload and ingest a PDF

PDF INVENTORY ENDPOINT NOTE
---------------------------
The Streamlit sidebar can call GET /uploaded-pdfs to show filenames, file
sizes and upload times. This endpoint must be implemented in backend/main.py
before the PDF inventory panel can work. Do not assume it is available just
because the frontend calls it.

CHAT REQUEST EXAMPLE
--------------------
{
  "question": "What subsidy is available for gypsum distribution?",
  "language": "English"
}

Tamil example:
{
  "question": "ஜிப்சம் பயன்படுத்துவதற்கு என்ன மானியம் வழங்கப்படுகிறது?",
  "language": "தமிழ்"
}

TESTING
-------
Run the retriever test from the project root:

python -m tests.test_retriever

Check the FAISS vector count:

python -c "from backend.rag.vector_store import load_vector_store; db=load_vector_store(); print('Total indexed vectors:', db.index.ntotal)"

At the last recorded development check, the FAISS index contained 704 vectors:
696 chunks from farmer_scheme.pdf and 8 chunks from tamilnadu.pdf. This is a
historical development snapshot; the count changes after successful ingestion.

KNOWN LIMITATIONS
-----------------
- OCR for scanned PDFs is not enabled.
- Retrieval quality depends on PDF text quality and completeness.
- Tamil retrieval uses English translation as a search aid.
- A retrieved page may contain adjacent table rows or multiple schemes; inspect
  the source page context before relying on a specific benefit.
- Local PDFs and the FAISS index are stored on the backend machine.
- The PDF inventory panel requires GET /uploaded-pdfs to be implemented.
- Guardrails reduce some risks but cannot guarantee perfectly accurate answers.
- Source references identify retrieved pages; they do not independently verify
  every sentence in a generated answer.

SECURITY NOTES
--------------
- Keep API keys in .env and exclude the file from Git.
- Treat uploaded PDF content as untrusted reference data.
- Only load FAISS indexes created and controlled by this application.
- Before production deployment, add authentication, authorization, rate limits,
  stronger file scanning, backups, monitoring and secure secret management.

FUTURE ENHANCEMENTS
-------------------
- Complete and secure the PDF inventory endpoint.
- Add safe PDF removal and re-indexing controls.
- Improve Tamil and table-aware PDF extraction.
- Consider optional OCR for scanned documents.
- Add official government website ingestion and scheduled refresh.
- Evaluate retrieval with a curated set of Tamil and English questions.
- Add authentication and production deployment.
- Consider Neo4j Knowledge Graph integration as a separate project extension.

PROJECT SUMMARY
---------------
The Tamil Nadu Farmers AI Assistant processes uploaded farmer-scheme PDFs,
indexes their text, retrieves relevant passages using semantic and lexical
search, and generates bilingual answers with source filename and page
references. It is designed to make available reference information easier to
discover and does not replace official government guidance.
