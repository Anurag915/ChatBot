from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.core.config import get_settings
from app.db.mongodb import get_database
from app.services.embedding_service import _get_embeddings


class ChatProcessingError(RuntimeError):
    """Raised when chat generation fails."""


def generate_answer(query: str, file_id: str) -> dict:
    """Retrieve chunks from FAISS and generate an answer using Groq."""
    
    settings = get_settings()
    
    if not settings.groq_api_key:
        raise ChatProcessingError("Groq API key is not configured.")
        
    index_dir = Path(settings.vector_store_dir) / file_id
    if not index_dir.exists():
        raise ChatProcessingError(f"No indexed data found for file_id: {file_id}")
        
    try:
        # Load the FAISS index
        vector_store = FAISS.load_local(
            str(index_dir), 
            _get_embeddings(), 
            allow_dangerous_deserialization=True
        )
        
        # Retrieve relevant chunks
        docs = vector_store.similarity_search(query, k=5)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        sources = [doc.page_content for doc in docs]
        
        timestamps = []
        for doc in docs:
            ts = doc.metadata.get("timestamps")
            if ts:
                timestamps.append({"start": ts["start"], "end": ts["end"]})
        
        # Setup Groq LLM
        llm = ChatGroq(
            model_name=settings.groq_model,
            groq_api_key=settings.groq_api_key,
            temperature=0.0
        )
        
        # Create prompt
        prompt = ChatPromptTemplate.from_template(
            "You are a helpful AI assistant. Answer the user's question based strictly on the provided context.\n\n"
            "Context:\n{context}\n\n"
            "Question: {query}\n\n"
            "Answer:"
        )
        
        chain = prompt | llm
        
        # Generate answer
        response = chain.invoke({"context": context_text, "query": query})
        
        return {
            "answer": response.content,
            "sources": sources,
            "timestamps": timestamps
        }
        
    except Exception as exc:
        raise ChatProcessingError(f"Failed to generate answer: {str(exc)}") from exc


async def generate_summary(file_id: str) -> str:
    """Generate a summary of the extracted text using Groq."""
    
    settings = get_settings()
    
    if not settings.groq_api_key:
        raise ChatProcessingError("Groq API key is not configured.")
        
    database = get_database()
    document = await database.documents.find_one({"file_id": file_id})
    if document is None or not document.get("text"):
        raise ChatProcessingError(f"No extracted text found for file_id: {file_id}")
        
    text = document["text"]
    
    # Setup Groq LLM
    llm = ChatGroq(
        model_name=settings.groq_model,
        groq_api_key=settings.groq_api_key,
        temperature=0.0
    )
    
    # Create prompt
    prompt = ChatPromptTemplate.from_template(
        "You are an expert summarizer. Please provide a concise but comprehensive summary of the following text:\n\n"
        "Text:\n{text}\n\n"
        "Summary:"
    )
    
    chain = prompt | llm
    
    try:
        response = await chain.ainvoke({"text": text})
        return response.content
    except Exception as exc:
        raise ChatProcessingError(f"Failed to generate summary: {str(exc)}") from exc

