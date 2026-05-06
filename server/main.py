import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------
# 🔧 Logging Configuration
# -------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

logger.info("🚀 Starting Medical RAG API server...")

# -------------------------------
# 🚀 Initialize FastAPI App
# -------------------------------
app = FastAPI(
    title="Medical Assistance API",
    description="API for AI Medical Assistance Chatbot"
)

# -------------------------------
# 🌐 CORS Configuration
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🛡️ Exception Middleware
# -------------------------------
try:
    from middlewares.expectional_handler import catch_exception_middleware
    app.middleware("http")(catch_exception_middleware)
    logger.info("✅ Exception middleware loaded")
except Exception as e:
    logger.error(f"❌ Failed to load middleware: {str(e)}")

# -------------------------------
# 🔌 Safe Router Imports
# -------------------------------
try:
    from routes.upload_pdfs import router as upload_router
    app.include_router(upload_router)
    logger.info("✅ upload_pdfs router loaded")
except Exception as e:
    logger.error(f"❌ upload_pdfs router failed: {str(e)}")

try:
    from routes.ask_question import router as ask_router
    app.include_router(ask_router)
    logger.info("✅ ask_question router loaded")
except Exception as e:
    logger.error(f"❌ ask_question router failed: {str(e)}")

# -------------------------------
# ❤️ Health Check Endpoint
# -------------------------------
@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "message": "Medical RAG AI Assistant API is running"
    }

# -------------------------------
# 🧪 Debug/Test Endpoint
# -------------------------------
@app.get("/test")
async def test_endpoint():
    try:
        import psutil
        import gc

        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        env_status = {
            "PINECONE_API_KEY": bool(os.getenv("PINECONE_API_KEY")),
            "GROQ_API_KEY": bool(os.getenv("GROQ_API_KEY")),
            "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY"))
        }

        gc.collect()

        return {
            "status": "test successful",
            "environment_variables": env_status,
            "memory_usage_mb": round(memory_mb, 2),
            "message": "Basic functionality check passed"
        }

    except Exception as e:
        logger.error(f"❌ Test endpoint failed: {str(e)}")
        return {
            "status": "test failed",
            "error": str(e)
        }

# -------------------------------
# 🔄 Startup Event (Optional)
# -------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("🔥 Server startup complete")

    # OPTIONAL: check env variables early
    required_env_vars = [
        "PINECONE_API_KEY",
        "GROQ_API_KEY",
        "GOOGLE_API_KEY"
    ]

    for var in required_env_vars:
        if not os.getenv(var):
            logger.warning(f"⚠️ Missing environment variable: {var}")

# -------------------------------
# 🧹 Shutdown Event
# -------------------------------
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Server shutting down")