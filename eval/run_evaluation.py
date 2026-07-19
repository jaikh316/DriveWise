import os
import json
import sys
import pandas as pd
from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import EVAL_RESULTS_FILE
from eval.test_set import TEST_SET
from generation.chain import answer_query, get_llm
from retrieval.hybrid_retriever import get_embeddings

def run_pipeline_eval() -> List[Dict[str, Any]]:
    print("=== Step 1: Running Queries through RAG Pipeline ===")
    results = []
    
    for idx, item in enumerate(TEST_SET):
        brand = item["brand"]
        model = item["model"]
        question = item["question"]
        expected_sec = item["expected_section"]
        
        print(f"[{idx+1}/{len(TEST_SET)}] Querying {brand} {model}: '{question}'...")
        
        
        res = answer_query(brand, model, question)
        
        retrieved_secs = res.get("retrieved_sections", [])
        section_match = expected_sec in retrieved_secs
        
        # Append eval items
        eval_item = {
            "brand": brand,
            "model": model,
            "question": question,
            "ground_truth": item["ground_truth"],
            "expected_section": expected_sec,
            "answer": res.get("answer"),
            "grounded": res.get("grounded"),
            "sources": res.get("sources"),
            "contexts": res.get("contexts", []),
            "retrieved_sections": retrieved_secs,
            "section_match": section_match,
            "response_time_seconds": res.get("response_time_seconds", 0.0),
            "status": res.get("status"),
            "error_message": res.get("error_message", "")
        }
        results.append(eval_item)
        
    return results

def main():
    print("=== DriveWise RAG Pipeline Evaluation ===")
    
    
    results = run_pipeline_eval()
    

    total_queries = len(results)
    section_matches = sum(1 for r in results if r["section_match"])
    section_match_rate = section_matches / total_queries if total_queries > 0 else 0.0
    
    avg_response_time = sum(r["response_time_seconds"] for r in results) / total_queries if total_queries > 0 else 0.0
    grounded_count = sum(1 for r in results if r["grounded"])
    grounded_rate = grounded_count / total_queries if total_queries > 0 else 0.0
    
    print("\n=== Step 2: Retrieval Analytics ===")
    print(f"Total Test Queries: {total_queries}")
    print(f"Retrieval Section-Match Rate: {section_match_rate * 100:.2f}% (Found expected section in context)")
    print(f"Grounded Rate: {grounded_rate * 100:.2f}% (LLM claimed grounded)")
    print(f"Average Pipeline Response Time: {avg_response_time:.2f} seconds")
    
    ragas_scores = {}
    try:
        print("\n=== Step 3: Running RAGAS Evaluation ===")
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_correctness, context_precision
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from ragas.run_config import RunConfig
        
        
        # Ragas expects: question, contexts (list of strings), answer, ground_truth
        data_dict = {
            "question": [r["question"] for r in results],
            "contexts": [r["contexts"] for r in results],
            "answer": [r["answer"] for r in results],
            "ground_truth": [r["ground_truth"] for r in results]
        }
        dataset = Dataset.from_dict(data_dict)
        
        
        llm_wrapper = LangchainLLMWrapper(get_llm())
        embeddings_wrapper = LangchainEmbeddingsWrapper(get_embeddings())
        
        run_config = RunConfig(max_workers=2, timeout=180)
        
        print("Executing Ragas evaluation with max_workers=2...")
        ragas_eval = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_correctness, context_precision],
            llm=llm_wrapper,
            embeddings=embeddings_wrapper,
            run_config=run_config
        )
        
        ragas_scores = dict(ragas_eval)
        print("Ragas evaluation completed successfully!")
        for metric, score in ragas_scores.items():
            print(f"  - {metric}: {score:.4f}")
            
    except Exception as e:
        print(f"\nWarning: RAGAS evaluation failed or was skipped: {e}")
        print("This is normal if LLM API rate limits were hit or RAGAS was misconfigured. Continuing with basic metrics.")
        ragas_scores = {"error": str(e)}

    
    os.makedirs(os.path.dirname(EVAL_RESULTS_FILE), exist_ok=True)
    summary_report = {
        "metadata": {
            "timestamp": pd.Timestamp.now().isoformat(),
            "total_queries": total_queries,
            "section_match_rate": section_match_rate,
            "grounded_rate": grounded_rate,
            "avg_response_time": avg_response_time,
            "llm_provider": os.getenv("LLM_PROVIDER", "google")
        },
        "ragas_scores": ragas_scores,
        "detail_results": [
            {
                "brand": r["brand"],
                "model": r["model"],
                "question": r["question"],
                "ground_truth": r["ground_truth"],
                "expected_section": r["expected_section"],
                "answer": r["answer"],
                "grounded": r["grounded"],
                "section_match": r["section_match"],
                "response_time_seconds": r["response_time_seconds"],
                "status": r["status"]
            }
            for r in results
        ]
    }
    
    with open(EVAL_RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2)
        
    print(f"\nSaved evaluation report to {EVAL_RESULTS_FILE}")

if __name__ == "__main__":
    main()
