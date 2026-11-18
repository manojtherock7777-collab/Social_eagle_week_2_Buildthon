from pathlib import Path
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from backend.rag.pipeline import run_rag_pipeline
from backend.rag.ingestion import ingest_pdf


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT / "data" / "uploaded_pdfs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="Tamil Nadu Farmers RAG Assistant",
    description=(
        "API for answering questions about Tamil Nadu "
        "farmer welfare schemes using PDF-based RAG."
    ),
    version="1.3.0"
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class ChatRequest(BaseModel):

    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Question about Tamil Nadu farmer schemes"
    )

    language: str = Field(
        default="English",
        description="Preferred response language: English or தமிழ்"
    )


# --------------------------------------------------
# HOME ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "application": "Tamil Nadu Farmers RAG Assistant",
        "status": "running",
        "message": "Welcome to the Farmers RAG API"
    }


# --------------------------------------------------
# HEALTH CHECK ENDPOINT
# --------------------------------------------------

@app.get("/health")
def health_check():

    index_path = PROJECT_ROOT / "vector_db" / "faiss_index"

    return {
        "api_status": "healthy",
        "vector_database_exists": index_path.exists()
    }


# --------------------------------------------------
# LIST UPLOADED PDF FILES
# --------------------------------------------------

@app.get("/uploaded-pdfs")
def get_uploaded_pdfs():

    try:

        pdf_files = []

        for file_path in UPLOAD_DIR.glob("*.pdf"):

            if not file_path.is_file():
                continue

            file_info = file_path.stat()

            pdf_files.append({

                "filename": file_path.name,

                "size_bytes": file_info.st_size,

                "size_mb": round(
                    file_info.st_size / (1024 * 1024),
                    2
                ),

                "uploaded_at": datetime.fromtimestamp(
                    file_info.st_mtime
                ).strftime("%d-%m-%Y %I:%M %p")

            })

        # Show newest files first
        pdf_files.sort(
            key=lambda item: item["filename"].lower()
        )

        return {

            "success": True,

            "total_files": len(pdf_files),

            "files": pdf_files

        }

    except Exception as error:

        print(f"PDF listing error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve uploaded PDF files."
        )


# --------------------------------------------------
# CHAT ENDPOINT
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        print("\n========== CHAT REQUEST ==========")

        print(f"Question: {request.question}")
        print(f"Selected language: {request.language}")

        result = run_rag_pipeline(
            request.question,
            request.language
        )

        return result

    except Exception as error:

        print(f"Chat API error: {error}")

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred "
                "while processing your question."
            )
        )


# --------------------------------------------------
# PDF UPLOAD ENDPOINT
# --------------------------------------------------

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Please select a PDF file."
        )

    original_name = Path(file.filename).name

    if Path(original_name).suffix.lower() != ".pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = None

    try:

        # Read uploaded PDF
        file_content = await file.read(MAX_FILE_SIZE + 1)

        # Validate file size
        if len(file_content) > MAX_FILE_SIZE:

            raise HTTPException(
                status_code=413,
                detail="PDF size cannot exceed 25 MB."
            )

        # Validate PDF signature
        if not file_content.startswith(b"%PDF-"):

            raise HTTPException(
                status_code=400,
                detail="The uploaded file is not a valid PDF."
            )

        # Save PDF using unique filename
        unique_name = f"{uuid4().hex}_{original_name}"

        file_path = UPLOAD_DIR / unique_name

        file_path.write_bytes(file_content)

        print(f"PDF saved: {unique_name}")

        # Run ingestion without blocking async endpoint
        ingestion_result = await run_in_threadpool(
            ingest_pdf,
            str(file_path)
        )

        # ------------------------------------------
        # DUPLICATE PDF HANDLING
        # ------------------------------------------

        if ingestion_result.get("duplicate", False):

            if file_path.exists():
                file_path.unlink()

            print(
                "Duplicate PDF detected. "
                "Upload copy deleted."
            )

            return {
                "success": True,
                "duplicate": True,
                "message": (
                    "This PDF has already been processed. "
                    "No duplicate chunks were added."
                ),
                "filename": unique_name,
                "size_bytes": len(file_content),
                "ingestion_status": "skipped",
                "pages_processed": 0,
                "chunks_added": 0
            }

        # ------------------------------------------
        # SUCCESSFUL PDF INGESTION
        # ------------------------------------------

        return {
            "success": True,
            "duplicate": False,
            "message": "PDF uploaded and processed successfully.",
            "filename": unique_name,
            "size_bytes": len(file_content),
            "ingestion_status": "completed",
            "pages_processed": ingestion_result["pages_processed"],
            "chunks_added": ingestion_result["chunks_added"]
        }

    except HTTPException:

        raise

    except Exception as error:

        print(f"PDF ingestion error: {error}")

        if file_path and file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                "PDF upload or ingestion failed. "
                "Check the server terminal."
            )
        )

    finally:

        await file.close()