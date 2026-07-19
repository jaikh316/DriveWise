import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import BROCHURE_CATALOG
from generation.chain import answer_query
from logs.analytics import get_analytics_data

st.set_page_config(
    page_title="DriveWise — Brochure RAG Assistant",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e1e30 0%, #0d0d15 100%) !important;
        color: #F3F4F6 !important;
    }
    
    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(13, 13, 21, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Title Banner Glassmorphism */
    .title-container {
        padding: 2.5rem;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(24px);
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    
    .title-text {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #60A5FA, #A78BFA, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        font-size: 1.1rem;
        color: #9CA3AF;
        font-weight: 400;
    }
    
    /* Metric Cards Glassmorphism */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 14px !important;
        padding: 1rem !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.3);
    }
    
    /* Car Profile Card Glassmorphism */
    .profile-card {
        padding: 1.4rem;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        margin-bottom: 1.5rem;
    }
    
    .profile-header {
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
        color: #FFFFFF;
    }
    
    /* Chat Message Bubbles Glassmorphism */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 16px !important;
        padding: 1.2rem !important;
        backdrop-filter: blur(16px) !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
        transition: border-color 0.3s ease;
    }
    [data-testid="stChatMessage"]:hover {
        border-color: rgba(255, 255, 255, 0.09) !important;
    }
    
    /* Suggested Questions Buttons with micro-animations */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.02) !important;
        color: #D1D5DB !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.4rem !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        font-weight: 500 !important;
        text-align: left !important;
        backdrop-filter: blur(12px);
        width: 100%;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, rgba(96, 165, 250, 0.15) 0%, rgba(167, 139, 250, 0.15) 100%) !important;
        border-color: rgba(167, 139, 250, 0.4) !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(167, 139, 250, 0.25) !important;
    }
    
    /* Chat Input Container Glassmorphism */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        color: #FFFFFF !important;
        backdrop-filter: blur(12px);
    }
    
    /* Badge styling */
    .section-badge {
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 6px;
        display: inline-block;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    }
    .badge-safety { background-color: rgba(239, 68, 68, 0.2); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-engine_performance { background-color: rgba(245, 158, 11, 0.2); color: #FDE047; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-dimensions { background-color: rgba(59, 130, 246, 0.2); color: #93C5FD; border: 1px solid rgba(59, 130, 246, 0.4); }
    .badge-interior_comfort { background-color: rgba(16, 185, 129, 0.2); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-infotainment_connectivity { background-color: rgba(139, 92, 246, 0.2); color: #C4B5FD; border: 1px solid rgba(139, 92, 246, 0.4); }
    .badge-exterior_styling { background-color: rgba(236, 72, 153, 0.2); color: #FBCFE8; border: 1px solid rgba(236, 72, 153, 0.4); }
    .badge-mileage_fuel_efficiency { background-color: rgba(6, 182, 212, 0.2); color: #A5F3FC; border: 1px solid rgba(6, 182, 212, 0.4); }
    .badge-variants_pricing { background-color: rgba(107, 114, 128, 0.2); color: #D1D5DB; border: 1px solid rgba(107, 114, 128, 0.4); }
    .badge-general_overview { background-color: rgba(75, 85, 99, 0.2); color: #E5E7EB; border: 1px solid rgba(75, 85, 99, 0.4); }
    
    /* Expanders styling */
    div.stExpander {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<h1 style='text-align: center;'>🚗 DriveWise</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #9CA3AF;'>Brochure-Grounded RAG Assistant</p>", unsafe_allow_html=True)
st.sidebar.write("---")

brands = sorted(list(set(car["brand"] for car in BROCHURE_CATALOG)))

if "selected_brand" not in st.session_state:
    st.session_state["selected_brand"] = brands[0]

try:
    brand_idx = brands.index(st.session_state["selected_brand"])
except ValueError:
    brand_idx = 0

selected_brand = st.sidebar.selectbox("Select Car Brand", brands, index=brand_idx)

# If brand changed, update session state and reset model to first option
if selected_brand != st.session_state["selected_brand"]:
    st.session_state["selected_brand"] = selected_brand
    temp_models = sorted(list(set(car["model"] for car in BROCHURE_CATALOG if car["brand"] == selected_brand)))
    st.session_state["selected_model"] = temp_models[0]

models_for_brand = sorted(list(set(car["model"] for car in BROCHURE_CATALOG if car["brand"] == selected_brand)))

if "selected_model" not in st.session_state:
    st.session_state["selected_model"] = models_for_brand[0]

try:
    model_idx = models_for_brand.index(st.session_state["selected_model"])
except ValueError:
    model_idx = 0

selected_model = st.sidebar.selectbox("Select Model", models_for_brand, index=model_idx)

# Update session state on model selection
if selected_model != st.session_state["selected_model"]:
    st.session_state["selected_model"] = selected_model

car_profile = next(
    car for car in BROCHURE_CATALOG 
    if car["brand"] == selected_brand and car["model"] == selected_model
)

# Reset Chat History if Car selection changes
car_key = f"{selected_brand} {selected_model}"
if "current_car" not in st.session_state:
    st.session_state["current_car"] = car_key
    st.session_state["messages"] = []

if st.session_state["current_car"] != car_key:
    st.session_state["current_car"] = car_key
    st.session_state["messages"] = []

brand_colors = {"Hyundai": "#002C5F", "Kia": "#05141F", "Tata": "#005F9E"}
card_color = brand_colors.get(selected_brand, "#1F2937")

st.sidebar.markdown(
    f"""
    <div class="profile-card" style="border-left: 5px solid {card_color};">
        <div class="profile-header">{selected_brand} {selected_model}</div>
        <div style="font-size: 0.9rem; color: #9CA3AF;">
            <b>Body Type:</b> {car_profile['body_type']}<br>
            <b>Model Year:</b> {car_profile['year']}<br>
            <b>Doc Version:</b> {car_profile['doc_version']}<br>
            <b>Source File:</b> <span style="font-family: monospace;">{car_profile['file']}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.write("### Recent Activity (Live)")
analytics = get_analytics_data()
recent_queries = analytics["recent_queries"]

if recent_queries:
    last_n = recent_queries[:5]
    success_rate_n = sum(1 for q in last_n if q["status"] == "success") / len(last_n)
    avg_latency_n = sum(q["response_time_seconds"] for q in last_n) / len(last_n)
    
    st.sidebar.metric(label="Success Rate (Last 5)", value=f"{success_rate_n*100:.0f}%")
    st.sidebar.metric(label="Avg Latency (Last 5)", value=f"{avg_latency_n:.2f}s")
else:
    st.sidebar.write("No queries logged yet.")

st.markdown(
    """
    <div class='title-container'>
        <div class='title-text'>DriveWise AI Assistant</div>
        <div class='subtitle-text'>A brochure-grounded, metadata-filtered RAG co-pilot for your car</div>
    </div>
    """, 
    unsafe_allow_html=True
)
st.write(f"Ask details about **{selected_brand} {selected_model} ({car_profile['year']})** grounded strictly in its official brochure.")

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📚 Show Brochure Sources"):
                for src in msg["sources"]:
                    sec = src["section"]
                    page = src["page_number"]
                    badge_class = f"badge-{sec}" if sec in [
                        "engine_performance", "mileage_fuel_efficiency", "safety", "dimensions",
                        "interior_comfort", "infotainment_connectivity", "exterior_styling", "variants_pricing"
                    ] else "badge-general_overview"
                    
                    st.markdown(
                        f"<span class='section-badge {badge_class}'>{sec}</span> Page {page}",
                        unsafe_allow_html=True
                    )
        
        if msg["role"] == "assistant" and not msg.get("grounded", True):
            st.warning("⚠️ This answer could not be verified by the brochure contents and is flagged as ungrounded.")


if not st.session_state["messages"]:
    st.write("### Suggested Questions:")
    
    
    suggestions = {
        "Alcazar": [
            "What engine options are available for the Hyundai Alcazar?",
            "What safety features are standard across all variants?",
            "Does it have a sunroof?"
        ],
        "Seltos": [
            "What safety features are included in the Kia Seltos ADAS Level 2?",
            "What is the screen size of the infotainment system?",
            "What is the fuel tank capacity of the Kia Seltos?"
        ],
        "Harrier": [
            "What is the safety rating and platform of the Tata Harrier?",
            "What is the boot space of the Tata Harrier?",
            "Does the Tata Harrier have ventilated seats?"
        ]
    }
    
    model_suggs = suggestions.get(selected_model, [
        f"What are the specifications of the {selected_model}?",
        f"What safety features does the {selected_model} have?"
    ])
    
    cols = st.columns(len(model_suggs))
    for idx, sugg in enumerate(model_suggs):
        if cols[idx].button(sugg, key=f"sugg_{idx}"):
            # Inject question into chat
            st.session_state["messages"].append({"role": "user", "content": sugg})
            
            with st.spinner("Analyzing brochure documents..."):
                response = answer_query(selected_brand, selected_model, sugg)
                
            st.session_state["messages"].append({
                "role": "assistant",
                "content": response["answer"],
                "grounded": response["grounded"],
                "sources": response["sources"]
            })
            

            st.rerun()


if prompt := st.chat_input(placeholder=f"Ask about {selected_brand} {selected_model}..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    

    with st.chat_message("user"):
        st.write(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Analyzing brochure documents..."):
            response = answer_query(selected_brand, selected_model, prompt)
        
        st.write(response["answer"])
        
        
        if response["sources"]:
            with st.expander("📚 Show Brochure Sources"):
                for src in response["sources"]:
                    sec = src["section"]
                    page = src["page_number"]
                    badge_class = f"badge-{sec}" if sec in [
                        "engine_performance", "mileage_fuel_efficiency", "safety", "dimensions",
                        "interior_comfort", "infotainment_connectivity", "exterior_styling", "variants_pricing"
                    ] else "badge-general_overview"
                    
                    st.markdown(
                        f"<span class='section-badge {badge_class}'>{sec}</span> Page {page}",
                        unsafe_allow_html=True
                    )
                    
        if not response["grounded"]:
            st.warning("⚠️ This answer could not be verified by the brochure contents and is flagged as ungrounded.")
            
    st.session_state["messages"].append({
        "role": "assistant",
        "content": response["answer"],
        "grounded": response["grounded"],
        "sources": response["sources"]
      })
    
    st.rerun()