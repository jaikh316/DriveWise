import os
import sys
import json
import pandas as pd
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import QUERY_LOG_FILE

def get_analytics_data() -> Dict[str, Any]:
    """
    Reads query_log.jsonl and calculates key telemetry metrics.
    Returns a dictionary of metrics, tables, and charts data.
    """
    empty_result = {
        "total_queries": 0,
        "success_rate": 0.0,
        "grounded_rate": 0.0,
        "avg_response_time": 0.0,
        "p95_response_time": 0.0,
        "queries_per_car": pd.DataFrame(columns=["car", "count"]),
        "response_time_series": pd.DataFrame(columns=["timestamp", "response_time_seconds"]),
        "failed_queries": pd.DataFrame(columns=["timestamp", "brand", "model", "question", "error_message"]),
        "recent_queries": []
    }
    
    if not os.path.exists(QUERY_LOG_FILE):
        return empty_result
        
    try:
        # Load JSONL file into a list of dicts
        entries = []
        with open(QUERY_LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
                    
        if not entries:
            return empty_result
            
        df = pd.DataFrame(entries)
        
        # Ensure timestamp is datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        total_queries = len(df)
        
        # Success Rate
        success_count = (df["status"] == "success").sum()
        success_rate = float(success_count / total_queries) if total_queries > 0 else 0.0
        
        # Grounded Rate
        grounded_count = df["grounded"].sum()
        grounded_rate = float(grounded_count / total_queries) if total_queries > 0 else 0.0
        
        # Response Time (Avg + P95)
        avg_response_time = float(df["response_time_seconds"].mean())
        p95_response_time = float(df["response_time_seconds"].quantile(0.95))
        
        # Queries per car
        df["car"] = df["brand"] + " " + df["model"]
        car_counts = df["car"].value_counts().reset_index()
        car_counts.columns = ["car", "count"]
        
        # Time Series for chart
        time_series = df[["timestamp", "response_time_seconds"]].sort_values("timestamp")
        
        # Failed Queries
        failed_df = df[df["status"] == "failed"][["timestamp", "brand", "model", "question", "error_message"]]
        failed_df = failed_df.sort_values("timestamp", ascending=False)
        
        # Recent queries ( last 10)
        recent = entries[-10:]
        recent.reverse()  # To Show newest first
        
        return {
            "total_queries": total_queries,
            "success_rate": success_rate,
            "grounded_rate": grounded_rate,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "queries_per_car": car_counts,
            "response_time_series": time_series,
            "failed_queries": failed_df,
            "recent_queries": recent
        }
    except Exception as e:
        print(f"Error parsing analytics logs: {e}")
        return empty_result
