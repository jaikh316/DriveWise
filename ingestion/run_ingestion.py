import os
import json
import sys
from collections import Counter

# Add parent directory to sys.path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BROCHURE_CATALOG, RAW_DATA_DIR, CHUNKS_FILE
from ingestion.extract import extract_pdf_pages
from ingestion.chunker import chunk_extracted_pages

def main():
    print("=== DriveWise Ingestion Pipeline ===")
    
    os.makedirs(os.path.dirname(CHUNKS_FILE), exist_ok=True)
    
    all_chunks = []
    
    # Process each brochure in the catalog
    for car in BROCHURE_CATALOG:
        pdf_name = car["file"]
        pdf_path = os.path.join(RAW_DATA_DIR, pdf_name)
        
        print(f"\nProcessing brochure: {pdf_name} ({car['brand']} {car['model']})...")
        
        if not os.path.exists(pdf_path):
            print(f"Error: PDF not found at {pdf_path}. Skipping.")
            continue
            

        try:
            pages = extract_pdf_pages(pdf_path)
            print(f"  Extracted {len(pages)} non-blank pages.")
        except Exception as e:
            print(f"  Failed to extract pages: {e}")
            continue
            
        
        try:
            chunks = chunk_extracted_pages(pages, car)
            print(f"  Generated {len(chunks)} text chunks.")
            all_chunks.extend(chunks)
            
            # Print section distribution for this car model
            sections = [doc.metadata["section"] for doc in chunks]
            dist = Counter(sections)
            print("  Section classification distribution:")
            for sec, count in dist.items():
                print(f"    - {sec}: {count} chunk(s)")
        except Exception as e:
            print(f"  Failed to chunk pages: {e}")
            continue

    
    print(f"\nWriting a total of {len(all_chunks)} chunks to {CHUNKS_FILE}...")
    try:
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            for doc in all_chunks:
                record = {
                    "text": doc.page_content,
                    "metadata": doc.metadata
                }
                f.write(json.dumps(record) + "\n")
        print("Ingestion completed successfully!")
    except Exception as e:
        print(f"Error writing chunks file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
