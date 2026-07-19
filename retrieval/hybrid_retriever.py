import os
import json
import sys
from typing import List, Dict, Any, Optional

# Silence Chroma telemetry before importing it
os.environ["ANONYMIZED_TELEMETRY"] = "False"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CHROMA_DB_DIR, CHUNKS_FILE
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

# Singleton caches
_embeddings = None
_vectorstore = None
_all_documents = None
_reranker_compressor = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("[Retrieval] Loading Embeddings Model (BAAI/bge-small-en-v1.5)...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            encode_kwargs={"normalize_embeddings": True}
        )
    return _embeddings

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        print("[Retrieval] Loading Chroma Vector Store...")
        _vectorstore = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=get_embeddings(),
            collection_name="drivewise_collection"
        )
    return _vectorstore

def get_all_documents() -> List[Document]:
    """
    Lazy-loads all chunked documents into memory to support fast BM25 scoping.
    """
    global _all_documents
    if _all_documents is None:
        print("[Retrieval] Loading chunks into memory for BM25...")
        if not os.path.exists(CHUNKS_FILE):
            raise FileNotFoundError(f"Chunks file not found at {CHUNKS_FILE}. Run ingestion first.")
            
        docs = []
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    docs.append(Document(page_content=data["text"], metadata=data["metadata"]))
        _all_documents = docs
        print(f"[Retrieval] Loaded {len(docs)} documents.")
    return _all_documents

def get_reranker_compressor():
    global _reranker_compressor
    if _reranker_compressor is None:
        print("[Retrieval] Loading Reranker (ms-marco-MiniLM-L-6-v2)...")
        model = HuggingFaceCrossEncoder(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
        _reranker_compressor = CrossEncoderReranker(model=model, top_n=4)
    return _reranker_compressor

def get_reranked_retriever(brand: str, model: str, k: int = 8, section: Optional[str] = None):
    """
    Returns a scoped hybrid BM25 + Chroma ensemble retriever wrapped with a CrossEncoder re-ranker.
    Pre-filters the documents for BM25 and Chroma so they search over the same candidate pool.
    """
    all_docs = get_all_documents()
    scoped_docs = [
        doc for doc in all_docs
        if doc.metadata.get("brand") == brand and doc.metadata.get("model") == model
    ]
    
    if section:
        scoped_docs = [doc for doc in scoped_docs if doc.metadata.get("section") == section]
        
    if not scoped_docs:
        
        scoped_docs = [Document(page_content=f"No details found for {brand} {model}.", metadata={"brand": brand, "model": model, "page_number": 1, "section": "general_overview"})]
        
    bm25_retriever = BM25Retriever.from_documents(scoped_docs)
    bm25_retriever.k = k
    
    db = get_vectorstore()
    
    
    filter_conditions = [
        {"brand": brand},
        {"model": model}
    ]
    if section:
        filter_conditions.append({"section": section})
        
    chroma_filter = {"$and": filter_conditions}
    
    chroma_retriever = db.as_retriever(
        search_kwargs={
            "k": k,
            "filter": chroma_filter
        }
    )
    
    
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.5, 0.5]
    )
    
    
    reranked_retriever = ContextualCompressionRetriever(
        base_compressor=get_reranker_compressor(),
        base_retriever=ensemble_retriever
    )
    
    return reranked_retriever

if __name__ == "__main__":
    
    import dotenv
    dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    
    try:
        retriever = get_reranked_retriever(brand="Kia", model="Seltos", k=8)
        docs = retriever.invoke("Tell me about the airbags and ADAS safety features.")
        print(f"\nRetrieved and re-ranked {len(docs)} documents:")
        for idx, doc in enumerate(docs):
            print(f"\n[{idx+1}] Score: {doc.metadata.get('relevance_score', 'N/A')}")
            print(f"Page: {doc.metadata.get('page_number')} | Section: {doc.metadata.get('section')}")
            print(f"Content: {doc.page_content[:200]}...")
    except Exception as e:
        print(f"Error during retrieval test: {e}")
        print("Note: This is expected if ingestion and vector store setup have not been run or completed.")
