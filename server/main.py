from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middlewares.expectional_handler import catch_exception_middleware
from routes.upload_pdfs import router as upload_router
from routes.ask_question import router as ask_router

app = FastAPI(title="Medical Assistance API", description="API for ai Medical Assistance chatbot")

# CORS Setup

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)


# middleWARE expectional handdle
app.middleware("http")(catch_exception_middleware)


# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "Medical RAG AI Assistant API is running"}

@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to check if basic functionality works"""
    try:
        import os
        import psutil
        import gc
        
        # Get memory info
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        env_status = {
            "PINECONE_API_KEY": bool(os.getenv("PINECONE_API_KEY")),
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY"))
        }
        
        # Force garbage collection
        gc.collect()
        
        return {
            "status": "test successful",
            "environment_variables": env_status,
            "memory_usage_mb": round(memory_mb, 2),
            "message": "Basic functionality check passed"
        }
    except Exception as e:
        return {"status": "test failed", "error": str(e)}


# routers


# 1. upload_pdfd document
app.include_router(upload_router)

# 2. asking quuery

app.include_router(ask_router)

