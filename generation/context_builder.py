import re
from typing import List, Tuple
from langchain_core.documents import Document

def get_word_set(text: str) -> set:
    """Helper to tokenize text into a set of lowercased words."""
    return set(re.findall(r'\w+', text.lower()))

def jaccard_similarity(text1: str, text2: str) -> float:
    """Calculates Jaccard similarity coefficient between two texts."""
    words1 = get_word_set(text1)
    words2 = get_word_set(text2)
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

def deduplicate_chunks(docs: List[Document], threshold: float = 0.6) -> List[Document]:
    """
    Deduplicates a list of documents by filtering out those that share a high Jaccard
    similarity with already accepted documents.
    """
    unique_docs = []
    for doc in docs:
        is_duplicate = False
        for u_doc in unique_docs:
            sim = jaccard_similarity(doc.page_content, u_doc.page_content)
            if sim > threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_docs.append(doc)
    return unique_docs

def build_context(docs: List[Document], token_budget: int = 1500) -> Tuple[str, List[Document]]:
    """
    Greedily builds a context string from documents within a token budget.
    Estimates token count via len(text) // 4 (approximate).
    Tags each chunk with its section and page number so the LLM can cite it.
    Returns:
        context_str: The formatted context string.
        used_docs: The list of Document objects actually included in the budget.
    """
    # 1. Deduplicate
    unique_docs = deduplicate_chunks(docs, threshold=0.6)
    
    context_parts = []
    used_docs = []
    current_tokens = 0
    
    for doc in unique_docs:
        section = doc.metadata.get("section", "general_overview")
        page_num = doc.metadata.get("page_number", "unknown")
        
        # Tagged representation for the LLM
        chunk_header = f"--- [Source: Section={section}, Page={page_num}] ---\n"
        chunk_body = f"{doc.page_content.strip()}\n\n"
        chunk_text = chunk_header + chunk_body
        
        # Approximate tokens in this chunk
        chunk_tokens = len(chunk_text) // 4
        
        # Stop before exceeding budget (never truncate a chunk in half)
        if current_tokens + chunk_tokens > token_budget:
            break
            
        context_parts.append(chunk_text)
        used_docs.append(doc)
        current_tokens += chunk_tokens
        
    context_str = "".join(context_parts).strip()
    return context_str, used_docs
