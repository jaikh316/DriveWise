import fitz
import os
from typing import List, Dict, Any

def extract_pdf_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text from a PDF brochure page-by-page.
    Skips blank pages. Returns a list of dictionaries with 1-indexed page numbers and text.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
    extracted_pages = []
    
    # Open document
    doc = fitz.open(pdf_path)
    try:
        for page_idx, page in enumerate(doc):
            text = page.get_text()
            
            cleaned_text = text.strip()
            if not cleaned_text:
                continue
                
            page_num = page_idx + 1  # 1-indexed
            extracted_pages.append({
                "page_number": page_num,
                "text": cleaned_text
            })
    finally:
        doc.close()
        
    return extracted_pages
