import streamlit as st
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logs.analytics import get_analytics_data

st.set_page_config(
    page_title="DriveWise — Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DriveWise Telemetry & Analytics")
st.write("Real-time monitoring of RAG assistant queries, response latency, and grounding metrics.")
st.write("---")


analytics = get_analytics_data()

if analytics["total_queries"] == 0:
    st.info("ℹ️ No queries have been logged yet. Start chatting with the assistant to populate telemetry data.")
else:
    # 1. Metric Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric(label="Total Queries", value=analytics["total_queries"])
    col2.metric(label="System Success Rate", value=f"{analytics['success_rate']*100:.1f}%")
    col3.metric(label="Grounded Rate", value=f"{analytics['grounded_rate']*100:.1f}%")
    col4.metric(label="Avg Response Time", value=f"{analytics['avg_response_time']:.2f}s")
    col5.metric(label="P95 Response Time", value=f"{analytics['p95_response_time']:.2f}s")
    
    st.write("---")
    
    # 2. Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Response Time Latency (Seconds)")
        ts_df = analytics["response_time_series"]
        if not ts_df.empty:
            ts_df = ts_df.set_index("timestamp")
            st.line_chart(ts_df["response_time_seconds"])
        else:
            st.write("No timeseries data available.")
            
    with col_right:
        st.subheader("🚗 Query Distribution by Car Model")
        car_df = analytics["queries_per_car"]
        if not car_df.empty:
            car_df = car_df.set_index("car")
            st.bar_chart(car_df["count"])
        else:
            st.write("No query distribution data available.")
            
    st.write("---")
    
    # 3. Failed Queries Table (with error logs)
    st.subheader("❌ System Failures & Refusals Log")
    failed_df = analytics["failed_queries"]
    if not failed_df.empty:
        st.dataframe(
            failed_df,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Timestamp"),
                "brand": "Brand",
                "model": "Model",
                "question": "User Question",
                "error_message": "Error Message / Refusal Reason"
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("🎉 No failed queries logged! All system calls are running successfully.")
        
    # 4. Recent Queries Log (raw view)
    with st.expander("📝 View Recent Raw Logs"):
        st.write(analytics["recent_queries"][:20])
