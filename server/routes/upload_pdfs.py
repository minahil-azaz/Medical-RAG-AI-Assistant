from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from modules.load_vectorStore import load_vectorstore
from logger import logger
import io

router = APIRouter()


def process_upload(filename: str, file_bytes: bytes):
    """Runs in background so the HTTP response is returned immediately."""
    try:
        # Reconstruct a file-like object the vectorstore function expects
        class FakeUploadFile:
            def __init__(self, name, data):
                self.filename = name
                self.file = io.BytesIO(data)

        fake_file = FakeUploadFile(filename, file_bytes)
        load_vectorstore([fake_file])
        logger.info(f"Background processing complete for: {filename}")
    except Exception as e:
        logger.exception(f"Background vectorstore processing failed: {str(e)}")


@router.post("/upload_pdfs/")
async def upload_pdfs(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        logger.info(f"Received file: {file.filename}")

        # ✅ FIX: Read file bytes immediately (before background task),
        # then offload heavy processing so we respond within timeout window
        file_bytes = await file.read()

        background_tasks.add_task(process_upload, file.filename, file_bytes)

        return {
            "message": f"File '{file.filename}' received. Processing in background — it will be available for queries in ~30-60 seconds."
        }
    except Exception as e:
        logger.exception("Error during file upload")
        return JSONResponse(status_code=500, content={"error": str(e)})