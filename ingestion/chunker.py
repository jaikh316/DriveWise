import re
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import SECTION_KEYWORDS

def classify_page_section(text: str) -> str:
    """
    Classifies a full page of text into a brochure section using keyword scoring.
    Returns the section name with the highest score. If no keywords match, returns "general_overview".

    """
    text_lower = text.lower()
    scores = {}
    
    for section, keywords in SECTION_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            
            score += text_lower.count(keyword.lower())
        scores[section] = score
        
    
    max_section = None
    max_score = 0
    for section, score in scores.items():
        if score > max_score:
            max_score = score
            max_section = section
            
    
    if max_section is None or max_score == 0:
        return "general_overview"
        
    return max_section

def chunk_extracted_pages(
    pages: List[Dict[str, Any]], 
    metadata: Dict[str, Any]
) -> List[Document]:
    """
    Classifies page sections first, then splits them into LangChain Document objects.
    Each chunk inherits page metadata, section, and brochure catalog info.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    documents = []
    
    for page in pages:
        page_num = page["page_number"]
        page_text = page["text"]
        
        
        section = classify_page_section(page_text)
        splits = splitter.split_text(page_text)
        
        # Build Document objects with complete metadata
        for split_text in splits:
            doc_metadata = {
                "source": metadata["file"],
                "brand": metadata["brand"],
                "model": metadata["model"],
                "year": metadata["year"],
                "doc_version": metadata["doc_version"],
                "body_type": metadata["body_type"],
                "page_number": page_num,
                "section": section
            }
            documents.append(Document(page_content=split_text, metadata=doc_metadata))
            
    return documents
