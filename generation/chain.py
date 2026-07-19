import os
import time
import sys
from typing import Optional, Dict, Any

from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BASE_DIR
from generation.schema import RAGResponse
from generation.context_builder import build_context
from retrieval.hybrid_retriever import get_reranked_retriever
from logs.logger import log_query


_llm_instance = None

def get_llm():
    """
    Lazy-loads and returns the LLM client configured in the environment.
    """
    global _llm_instance
    if _llm_instance is not None:
        return _llm_instance

    provider = os.getenv("LLM_PROVIDER", "google").lower()
    
    if provider == "google":
        from langchain_google_genai import ChatGoogleGenAI
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:

            raise ValueError("Google API key (GOOGLE_API_KEY or GEMINI_API_KEY) not found in env.")    
        model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-flash")
        print(f"[LLM] Instantiating Google ChatGoogleGenAI ({model_name})...")
        
        _llm_instance = ChatGoogleGenAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.0
        )
        
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key (ANTHROPIC_API_KEY) not found in env.")
            
        model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        print(f"[LLM] Instantiating Anthropic ChatAnthropic ({model_name})...")
        _llm_instance = ChatAnthropic(
            model=model_name,
            anthropic_api_key=api_key,
            temperature=0.0
        )
        
    elif provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Groq API key (GROQ_API_KEY) not found in env.")
            
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        print(f"[LLM] Instantiating Groq ChatGroq ({model_name})...")
        _llm_instance = ChatGroq(
            model=model_name,
            groq_api_key=api_key,
            temperature=0.0
        )
        
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Supported: google, anthropic, groq")
        
    return _llm_instance

def answer_query(
    brand: str,
    model: str,
    question: str,
    k: int = 8,
    section: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes retrieval, builds prompt context, invokes the structured LLM,
    and returns a normalized response dict. Logs the query before returning.
    """
    start_time = time.time()
    raw_docs = []
    used_docs = []
    context_str = ""
    
    
    fallback_response = {
        "brand": brand,
        "model": model,
        "question": question,
        "status": "failed",
        "error_message": "",
        "response_time_seconds": 0.0,
        "answer": "Sorry, I encountered an internal error while trying to process your request.",
        "grounded": False,
        "sources": [],
        "contexts": [],
        "retrieved_sections": []
    }
    
    try:
        
        retriever = get_reranked_retriever(brand, model, k=k, section=section)
        raw_docs = retriever.invoke(question)
        
        context_str, used_docs = build_context(raw_docs, token_budget=1500)
        
        if not used_docs:
            elapsed = time.time() - start_time
            res = {
                "brand": brand,
                "model": model,
                "question": question,
                "status": "success",
                "error_message": "",
                "response_time_seconds": elapsed,
                "answer": f"I could not find any information about the {brand} {model} in the brochure related to your request.",
                "grounded": False,
                "sources": [],
                "contexts": [],
                "retrieved_sections": []
            }
            
            log_query(res)
            return res
            
        llm = get_llm()
        structured_llm = llm.with_structured_output(RAGResponse)
        
        system_prompt = (
            "You are a helpful, brochure-grounded RAG assistant named DriveWise.\n"
            "Your task is to answer the user's question about the vehicle using ONLY the provided brochure context.\n\n"
            "Strict rules:\n"
            "1. Answer the question using ONLY the provided context blocks. Do not use outside knowledge.\n"
            "2. For every fact in your answer, you MUST cite the source using the exact Section and Page number from the context tags (e.g., Section=safety, Page=5). Include these in the 'sources' list.\n"
            "3. If the context does not contain enough information, or if you are unsure, set 'grounded' to False and state that the information was not found in the brochure. Do not guess.\n"
            "4. Keep the answer clear, professional, and in plain language.\n"
            "5. If the user's input is a greeting or not a query about the vehicle, set 'grounded' to False and request them to ask a question about the vehicle's brochure.\n"
        )
        
        user_prompt = (
            f"Vehicle: {brand} {model}\n"
            f"Question: {question}\n\n"
            f"Context:\n{context_str}\n"
        )
        
        messages = [
            ("system", system_prompt),
            ("user", user_prompt)
        ]
        
        llm_response = structured_llm.invoke(messages)
        
        # Handle case where llm_response is a dict or RAGResponse object
        if isinstance(llm_response, dict):
            ans_text = llm_response.get("answer")
            is_grounded = llm_response.get("grounded", False)
            src_list = llm_response.get("sources", [])
        else:
            ans_text = llm_response.answer
            is_grounded = llm_response.grounded
            src_list = [
                {"section": citation.section, "page_number": citation.page_number}
                for citation in llm_response.sources
            ]
            
        
        if is_grounded and not src_list:
            is_grounded = False
            
        elapsed = time.time() - start_time
        res = {
            "brand": brand,
            "model": model,
            "question": question,
            "status": "success",
            "error_message": "",
            "response_time_seconds": elapsed,
            "answer": ans_text,
            "grounded": is_grounded,
            "sources": src_list,
            "contexts": [doc.page_content for doc in used_docs],
            "retrieved_sections": list(set([doc.metadata.get("section") for doc in used_docs]))
        }
        log_query(res)
        return res
        
    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)
        
        if "tool" in error_msg.lower() or "structure" in error_msg.lower() or len(question.strip().split()) <= 2:
            fallback_ans = "Hello! I am DriveWise, your car brochure assistant. Please ask me a specific question about the features, safety, specifications, or trims of the vehicle."
        else:
            fallback_ans = f"Sorry, I encountered an issue processing your request: {error_msg}"
            
        res = {
            "brand": brand,
            "model": model,
            "question": question,
            "status": "failed",
            "error_message": error_msg,
            "response_time_seconds": elapsed,
            "answer": fallback_ans,
            "grounded": False,
            "sources": [],
            "contexts": [doc.page_content for doc in raw_docs] if raw_docs else [],
            "retrieved_sections": list(set([doc.metadata.get("section") for doc in raw_docs])) if raw_docs else []
        }
        log_query(res)
        return res
