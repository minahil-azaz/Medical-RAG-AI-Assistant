from langchain_core.prompts import PromptTemplate
import os

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_llm_chain(retriever):
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant"
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are **MediBot**, an AI-powered assistant trained to help users understand medical documents and health-related questions.

Your job is to provide clear, accurate, and helpful responses based **only on the provided context**.

---

🔍 Context:
{context}

🙋‍♂️ User Question:
{question}

---

💬 Answer:
- Respond in a calm, factual, and respectful tone.
- Use simple explanations when needed.
- If the context does not contain the answer, say:
  "I'm sorry, but I couldn't find relevant information in the provided documents."
- Do NOT make up facts.
- Do NOT give medical advice or diagnoses.
"""
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    class ChainWrapper:
        def __init__(self, llm, prompt, retriever):
            self.llm = llm
            self.prompt = prompt
            self.retriever = retriever

        def __call__(self, inputs):
            query = inputs.get("query") if isinstance(inputs, dict) else inputs
            docs = self.retriever.invoke(query)
            if docs is None:
                context = ""
            elif isinstance(docs, list):
                context = format_docs(docs)
            else:
                context = format_docs([docs])

            prompt_text = self.prompt.format(context=context, question=query)
            result = self.llm.invoke(prompt_text)
            return {
                "result": result,
                "source_documents": docs
            }

    return ChainWrapper(llm, prompt, retriever)