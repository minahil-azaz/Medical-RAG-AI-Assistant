from logger import logger

def query_chain(chain,user_input:str):
    try:
        logger.debug(f"Running chain for input: {user_input}")
        results = chain({"query": user_input})
        answer = results["result"]
        if hasattr(answer, "content"):
            answer = answer.content
        response = {
            "response": answer,
            "sources": [doc.metadata.get("source", doc.metadata.get("text", "")) for doc in results["source_documents"]]
        }
        logger.debug(f"chian response {response}")
        return response
    except Exception as e:
        logger.exception("error on query chain")
        raise