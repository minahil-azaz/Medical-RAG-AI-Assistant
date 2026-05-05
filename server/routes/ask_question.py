from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from modules.llm import get_llm_chain
from modules.query_handler import query_chain
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone
from pydantic import Field
from typing import List, Optional
from logger import logger
import os

router=APIRouter()

@router.post("/ask/")
async def ask_question(question:str=Form(...)):
    # embed model and pinecone setup
    try:
        logger.info(f"Processing question: {question}")
        
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            logger.error("PINECONE_API_KEY environment variable is missing")
            raise ValueError("PINECONE_API_KEY environment variable is required")
            
        logger.info("Initializing Pinecone client")
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index("medical-assistance")  # Use hardcoded index name
        
        logger.info("Creating embedding model")
        # Use CPU-only embeddings to reduce memory
        embed_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        logger.info("Embedding query")
        embedded_query = embed_model.embed_query(question)
        
        logger.info("Querying Pinecone")
        res = index.query(vector=embedded_query, top_k=2, include_metadata=True)  # Reduced from 3 to 2
        matches = res.get("matches", res.get("match", []))
        
        logger.info(f"Found {len(matches)} matches")
        
        docs = [
            Document(
                page_content=match["metadata"].get("text", ""),
                metadata=match["metadata"]
            ) for match in matches
        ]
        
        logger.info(f"Created {len(docs)} documents")
        
        # Handle case where no documents are found
        if not docs:
            logger.warning("No documents found in vector store")
            return {
                "response": "I'm sorry, but I couldn't find any relevant information in the uploaded documents. Please try uploading some medical documents first.",
                "sources": []
            }
        
        class SimpleRetriever(BaseRetriever):
            tags:Optional[List[str]] = Field(default_factory=list)
            metadata:Optional[dict] = Field(default_factory=dict)
            
            def __init__(self,document:List[Document]):
                super().__init__()
                self._docs = document
                
            def _get_relevant_documents(self,query:str) -> List[Document]:
                return self._docs
                
        retriever = SimpleRetriever(docs)
        
        logger.info("Getting LLM chain")
        chain = get_llm_chain(retriever)
        
        logger.info("Running query chain")
        result = query_chain(chain,question)
        
        logger.info("Query successful")
        
        return result
    except Exception as e:
        logger.exception(f"Error processing question: {str(e)}")
        return JSONResponse(status_code=500,content={"error":str(e)})

                