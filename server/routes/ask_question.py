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
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("medical-assistance")  # Use hardcoded index name
        embed_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        embedded_query = embed_model.embed_query(question)
        res = index.query(vector=embedded_query, top_k=3, include_metadata=True)
        matches = res.get("matches", res.get("match", []))
        
        docs = [
            Document(
                page_content=match["metadata"].get("text", ""),
                metadata=match["metadata"]
            ) for match in matches
        ]
        class SimpleRetriever(BaseRetriever):
            tags:Optional[List[str]] = Field(default_factory=list)
            metadata:Optional[dict] = Field(default_factory=dict)
            
            def __init__(self,document:List[Document]):
                super().__init__()
                self._docs = document
                
            def _get_relevant_documents(self,query:str) -> List[Document]:
                return self._docs
        retriever = SimpleRetriever(docs)
        chain = get_llm_chain(retriever)
        result = query_chain(chain,question)
        
        logger.info("Query is successfull")
        
        return result
    except Exception as e:
        logger.exception("error processing question")
        return JSONResponse(status_code=500,content={"error":str(e)})

                