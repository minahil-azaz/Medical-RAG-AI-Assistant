from fastapi import APIRouter, UploadFile, File
from modules.load_vectorStore import load_vectorstore
from fastapi.responses import JSONResponse
from logger import logger

router = APIRouter()

@router.post("/upload_pdfs/")
async def upload_pdfs(file: UploadFile = File(...)):
    try:
        logger.info("Received uploaded file")
        load_vectorstore([file])  # Wrap single file in list
        logger.info("document added to vectorstore")
        return {"message": "file processed and vectorstore updated"}
    except Exception as e:
        logger.exception("error during uploading file")
        return JSONResponse(status_code=500, content={"error": str(e)})
        
  