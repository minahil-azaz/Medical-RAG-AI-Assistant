from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.llm import get_llm_chain
from modules.query_handler import query_chain
from modules.load_vectorStore import get_embed_model, get_pinecone_index  # ✅ reuse singletons
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from typing import List, Optional
from logger import logger

router = APIRouter()


# ✅ FIX: Defined once at module level, not recreated on every request
class SimpleRetriever(BaseRetriever):
    tags: Optional[List[str]] = Field(default_factory=list)
    metadata: Optional[dict] = Field(default_factory=dict)

    def __init__(self, documents: List[Document]):
        super().__init__()
        self._docs = documents

    def _get_relevant_documents(self, query: str) -> List[Document]:
        return self._docs


@router.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        logger.info(f"Processing question: {question}")

        # ✅ Reuses the already-loaded singleton — no re-initialization
        embed_model = get_embed_model()
        index = get_pinecone_index()

        logger.info("Embedding query")
        embedded_query = embed_model.embed_query(question)

        logger.info("Querying Pinecone")
        res = index.query(vector=embedded_query, top_k=2, include_metadata=True)
        matches = res.get("matches", [])

        logger.info(f"Found {len(matches)} matches")

        docs = [
            Document(
                page_content=match["metadata"].get("text", ""),
                metadata=match["metadata"],
            )
            for match in matches
        ]

        if not docs:
            logger.warning("No documents found in vector store")
            return {
                "response": "I'm sorry, but I couldn't find any relevant information in the uploaded documents. Please try uploading some medical documents first.",
                "sources": [],
            }

        retriever = SimpleRetriever(docs)
        chain = get_llm_chain(retriever)
        result = query_chain(chain, question)

        logger.info("Query successful")
        return result

    except Exception as e:
        logger.exception(f"Error processing question: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})