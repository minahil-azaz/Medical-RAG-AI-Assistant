from logger import logger

def query_chain(chain, user_input: str):
    try:
        logger.debug(f"Running chain for input: {user_input}")
        
        # Ensure user_input is a string
        if not isinstance(user_input, str):
            user_input = str(user_input)
            
        results = chain({"query": user_input})
        
        # Handle different response formats
        if isinstance(results, dict):
            answer = results.get("result")
            source_docs = results.get("source_documents", [])
        else:
            answer = results
            source_docs = []
            
        if hasattr(answer, "content"):
            answer = answer.content
            
        # Ensure answer is a string
        if not isinstance(answer, str):
            answer = str(answer)
            
        response = {
            "response": answer,
            "sources": [doc.metadata.get("source", doc.metadata.get("text", "")) for doc in source_docs if hasattr(doc, 'metadata')]
        }
        logger.debug(f"Chain response: {response}")
        return response
    except Exception as e:
        logger.exception(f"Error in query chain: {str(e)}")
        # Return a fallback response instead of raising
        return {
            "response": "I'm sorry, but I encountered an error while processing your question. Please try again.",
            "sources": []
        }