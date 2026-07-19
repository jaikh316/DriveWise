import os
import json
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import QUERY_LOG_FILE

def log_query(response_dict: dict) -> None:
    """
    Appends a query execution record to logs/query_log.jsonl in JSON Lines format.
    Guaranteed not to raise an exception, preventing logging issues from breaking the app.
    """
    try:
        log_dir = os.path.dirname(QUERY_LOG_FILE)

        os.makedirs(log_dir, exist_ok=True)
        

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "brand": response_dict.get("brand"),
            "model": response_dict.get("model"),
            "question": response_dict.get("question"),
            "status": response_dict.get("status"),
            "grounded": response_dict.get("grounded", False),
            "response_time_seconds": response_dict.get("response_time_seconds", 0.0),
            "error_message": response_dict.get("error_message", ""),
            "num_sources": len(response_dict.get("sources", []))
        }
        
        
        with open(QUERY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception:
        pass
