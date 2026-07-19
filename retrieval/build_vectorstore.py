import os
import json
import sys

os.environ["ANONYMIZED_TELEMETRY"] = "False"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CHUNKS_FILE, CHROMA_DB_DIR
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def build_vectorstore():
    print("=== Building Chroma Vector Store ===")
    
    if not os.path.exists(CHUNKS_FILE):
        print(f"Error: {CHUNKS_FILE} does not exist. Run ingestion first.")
        sys.exit(1)
        

    print(f"Loading chunks from {CHUNKS_FILE}...")
    documents = []
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                documents.append(
                    Document(
                        page_content=data["text"],
                        metadata=data["metadata"]
                    )
                )            
    print(f"Loaded {len(documents)} chunks.")
    
    print("Initializing embedding model (BAAI/bge-small-en-v1.5)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )
    
    print(f"Creating and persisting Chroma DB in {CHROMA_DB_DIR}...")
    

    import shutil
    if os.path.exists(CHROMA_DB_DIR):
        print(f"  Clearing existing database directory at {CHROMA_DB_DIR}...")
        try:
            shutil.rmtree(CHROMA_DB_DIR)
            print("  Clear complete.")
        except Exception as e:
            print(f"  Warning: Could not clear existing directory: {e}")
            
    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR,
        collection_name="drivewise_collection"
    )
    
    print("Vector store successfully built and persisted!")
    return db

if __name__ == "__main__":
    db = build_vectorstore()
    
    
    print("\nRunning similarity search smoke test...")
    query = "What safety features does the Seltos have?"
    print(f"Query: '{query}' for Brand: Kia, Model: Seltos")
    
    filter_metadata = {
        "$and": [
            {"brand": "Kia"},
            {"model": "Seltos"}
        ]
    }
    
    results = db.similarity_search(query, k=3, filter=filter_metadata)
    print(f"Retrieved {len(results)} results:")
    for i, res in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"  Page: {res.metadata.get('page_number')}")
        print(f"  Section: {res.metadata.get('section')}")
        print(f"  Content: {res.page_content[:150]}...")
