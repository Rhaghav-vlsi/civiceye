import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import time
import hashlib

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="CivicEye - AI Urban Issue Tracker",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - FIXED VERSION
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* SIDEBAR FIX - This is the key change */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1e1b4b 100%);
        position: relative !important;
        z-index: 999 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* Ensure sidebar doesn't block main content */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 280px !important;
        max-width: 280px !important;
    }
    
    /* Fix main content positioning */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .hero-container {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2rem 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 50%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        position: relative;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        color: #a5b4fc;
        font-size: 1.1rem;
        font-weight: 300;
        position: relative;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 1px solid rgba(99,102,241,0.3);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(99,102,241,0.3);
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: #818cf8;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .status-critical {
        background: linear-gradient(135deg, #dc2626, #b91c1c);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-high {
        background: linear-gradient(135deg, #ea580c, #c2410c);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-medium {
        background: linear-gradient(135deg, #d97706, #b45309);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-low {
        background: linear-gradient(135deg, #16a34a, #15803d);
        color: white;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .issue-card {
        background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .issue-card:hover {
        border-color: rgba(99,102,241,0.5);
        box-shadow: 0 8px 30px rgba(99,102,241,0.2);
    }
    
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(99,102,241,0.3);
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #7c3aed, #a855f7);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 8px;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 5px rgba(124,58,237,0.5); }
        to { box-shadow: 0 0 20px rgba(124,58,237,0.8); }
    }
    
    .progress-container {
        background: rgba(30,27,75,0.5);
        border-radius: 10px;
        padding: 3px;
        margin: 5px 0;
    }
    
    .progress-bar {
        height: 8px;
        border-radius: 8px;
        transition: width 1s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30,27,75,0.5);
        border-radius: 10px;
        padding: 10px 20px;
        color: #a5b4fc;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
        color: white !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79,70,229,0.4);
    }
    
    [data-testid="stFileUploader"] {
        border: 2px dashed rgba(99,102,241,0.3);
        border-radius: 16px;
        padding: 1rem;
    }
    
    .stSelectbox > div > div {
        background: rgba(30,27,75,0.8);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 12px;
    }
    
    .stTextInput > div > div > input {
        background: rgba(30,27,75,0.8);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 12px;
        color: white;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(30,27,75,0.8);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 12px;
        color: white;
    }
    
    .success-toast {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .timeline-item {
        border-left: 3px solid #4f46e5;
        padding: 0.5rem 0 0.5rem 1.5rem;
        margin-left: 1rem;
        position: relative;
    }
    
    .timeline-item::before {
        content: '';
        position: absolute;
        left: -7px;
        top: 0.8rem;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #4f46e5;
        border: 2px solid #818cf8;
    }
    
    .timeline-date {
        color: #818cf8;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .timeline-text {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# AI ENGINE
# ============================================
class CivicEyeAI:
    @staticmethod
    def classify_issue(description):
        keywords = {
            "Pothole": ["pothole", "hole", "road damage", "bump", "crater"],
            "Streetlight": ["light", "dark", "lamp", "streetlight", "bulb", "illumination"],
            "Garbage": ["garbage", "trash", "waste", "dump", "litter", "rubbish"],
            "Water Leak": ["water", "leak", "pipe", "flooding", "drain", "sewage"],
            "Road Damage": ["road", "crack", "broken road", "asphalt", "pavement"],
            "Illegal Dumping": ["illegal", "dumping", "construction waste", "debris"],
            "Broken Sidewalk": ["sidewalk", "footpath", "walking", "pedestrian"],
            "Traffic Signal": ["traffic", "signal", "red light", "intersection"],
            "Noise Complaint": ["noise", "loud", "sound", "disturbance", "honking"],
            "Graffiti": ["graffiti", "paint", "vandalism", "wall", "spray"],
        }
        
        description_lower = description.lower()
        scores = {}
        
        for category, words in keywords.items():
            score = sum(1 for word in words if word in description_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(0.65 + (max(scores.values()) * 0.12), 0.98)
            return best_category, round(confidence, 2)
        
        return "General Issue", 0.60
    
    @staticmethod
    def calculate_priority(category, description, upvotes=0):
        base_scores = {
            "Water Leak": 90, "Traffic Signal": 85, "Road Damage": 80,
            "Pothole": 70, "Streetlight": 65, "Broken Sidewalk": 60,
            "Garbage": 55, "Illegal Dumping": 50, "Noise Complaint": 40,
            "Graffiti": 35, "General Issue": 30
        }
        
        score = base_scores.get(category, 50)
        
        urgent_words = ["dangerous", "emergency", "urgent", "accident", "injury", "child", "elderly", "flood"]
        for word in urgent_words:
            if word in description.lower():
                score += 10
        
        score += min(upvotes * 0.5, 15)
        score = min(score, 100)
        
        if score >= 80:
            return "Critical", score
        elif score >= 60:
            return "High", score
        elif score >= 40:
            return "Medium", score
        else:
            return "Low", score
    
    @staticmethod
    def predict_resolution_time(category, priority):
        base_times = {
            "Critical": 2, "High": 5, "Medium": 8, "Low": 14
        }
        
        category_modifier = {
            "Water Leak": 0.7, "Traffic Signal": 0.8, "Pothole": 1.0,
            "Streetlight": 0.9, "Garbage": 0.6, "Road Damage": 1.5,
        }
        
        base = base_times.get(priority, 7)
        modifier = category_modifier.get(category, 1.0)
        
        return max(1, int(base * modifier))
    
    @staticmethod
    def generate_ai_insights(df):
        insights = []
        
        location_counts = df['location'].value_counts()
        hotspot = location_counts.index[0]
        insights.append(f"🔥 **Hotspot Alert**: {hotspot} has the highest concentration of issues ({location_counts.iloc[0]} reports)")
        
        critical_count = len(df[df['priority'] == 'Critical'])
        if critical_count > 0:
            insights.append(f"🚨 **{critical_count} Critical Issues** require immediate attention")
        
        category_counts = df['category'].value_counts()
        top_category = category_counts.index[0]
        insights.append(f"📊 **Trending Issue**: {top_category} is the most reported category ({category_counts.iloc[0]} reports)")
        
        resolved = len(df[df['status'] == 'Resolved'])
        total = len(df)
        rate = (resolved/total)*100 if total > 0 else 0
        insights.append(f"✅ **Resolution Rate**: {rate:.1f}% of reported issues have been resolved")
        
        pending = len(df[df['status'].isin(['Reported', 'Under Review'])])
        insights.append(f"🔮 **AI Prediction**: {pending} issues pending review - estimated clearance in {max(3, pending//5)} days")
        
        return insights
    
    @staticmethod
    def analyze_image(uploaded_file):
        detections = [
            {"issue": "Pothole", "confidence": 0.94, "severity": "High"},
            {"issue": "Road Damage", "confidence": 0.87, "severity": "Medium"},
            {"issue": "Garbage", "confidence": 0.91, "severity": "High"},
            {"issue": "Streetlight Damage", "confidence": 0.88, "severity": "Medium"},
            {"issue": "Water Leak", "confidence": 0.92, "severity": "Critical"},
        ]
        return random.choice(detections)

ai_engine = CivicEyeAI()

# ============================================
# SAMPLE DATA GENERATOR
# ============================================
def generate_sample_issues():
    categories = ["Pothole", "Streetlight", "Garbage", "Water Leak", "Road Damage", 
                   "Illegal Dumping", "Broken Sidewalk", "Traffic Signal", "Noise Complaint", "Graffiti"]
    
    statuses = ["Reported", "Under Review", "In Progress", "Resolved"]
    priorities = ["Critical", "High", "Medium", "Low"]
    
    areas = [
        {"name": "Downtown", "lat": 12.9716, "lon": 77.5946},
        {"name": "Whitefield", "lat": 12.9698, "lon": 77.7500},
        {"name": "Koramangala", "lat": 12.9352, "lon": 77.6245},
        {"name": "Indiranagar", "lat": 12.9784, "lon": 77.6408},
        {"name": "Jayanagar", "lat": 12.9308, "lon": 77.5838},
        {"name": "HSR Layout", "lat": 12.9116, "lon": 77.6389},
        {"name": "Electronic City", "lat": 12.8440, "lon": 77.6568},
        {"name": "Marathahalli", "lat": 12.9591, "lon": 77.6974},
        {"name": "BTM Layout", "lat": 12.9166, "lon": 77.6101},
        {"name": "Hebbal", "lat": 13.0358, "lon": 77.5970},
    ]
    
    issues = []
    for i in range(50):
        area = random.choice(areas)
        cat = random.choice(categories)
        status = random.choice(statuses)
        
        if cat in ["Water Leak", "Road Damage", "Traffic Signal"]:
            priority = random.choice(["Critical", "High"])
        elif cat in ["Pothole", "Streetlight", "Broken Sidewalk"]:
            priority = random.choice(["High", "Medium"])
        else:
            priority = random.choice(["Medium", "Low"])
        
        days_ago = random.randint(0, 30)
        
        issues.append({
            "id": f"CIV-{1000+i}",
            "category": cat,
            "description": f"{cat} reported near {area['name']} area. Needs immediate attention." if priority in ["Critical", "High"] else f"{cat} observed in {area['name']} area.",
            "location": area["name"],
            "lat": area["lat"] + random.uniform(-0.01, 0.01),
            "lon": area["lon"] + random.uniform(-0.01, 0.01),
            "status": status,
            "priority": priority,
            "ai_confidence": round(random.uniform(0.75, 0.99), 2),
            "date_reported": (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "upvotes": random.randint(1, 150),
            "assigned_to": random.choice(["Public Works", "Water Dept", "Traffic Dept", "Sanitation", "Electrical Dept"]),
            "reporter": f"Citizen_{random.randint(100,999)}",
            "estimated_resolution": random.randint(1, 14),
        })
    
    return pd.DataFrame(issues)

# ============================================
# INITIALIZE SESSION STATE
# ============================================
if 'issues' not in st.session_state:
    st.session_state.issues = generate_sample_issues()
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True
if 'user_role' not in st.session_state:
    st.session_state.user_role = "citizen"
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# ============================================
# SIDEBAR NAVIGATION
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <span style="font-size: 3rem;">🏙️</span>
        <h2 style="color: #818cf8; font-family: 'Inter', sans-serif; margin: 0.5rem 0;">CivicEye</h2>
        <p style="color: #64748b; font-size: 0.85rem;">AI-Powered Urban Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Report Issue", "AI Detection", "Issue Tracker", "Analytics", "Heatmap"],
        icons=["speedometer2", "plus-circle", "robot", "list-task", "graph-up", "map"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#818cf8", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px 0",
                "padding": "10px 15px",
                "border-radius": "10px",
                "color": "#94a3b8",
                "background-color": "transparent",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #4f46e5, #7c3aed)",
                "color": "white",
                "font-weight": "600",
            },
        }
    )
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background: rgba(30,27,75,0.5); border-radius: 12px; padding: 1rem; border: 1px solid rgba(99,102,241,0.2);">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #4f46e5, #7c3aed); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">U</div>
            <div>
                <div style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">User Demo</div>
                <div style="color: #64748b; font-size: 0.75rem;">🟢 Active Citizen</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("##### ⚡ Quick Stats")
    total = len(st.session_state.issues)
    resolved = len(st.session_state.issues[st.session_state.issues['status'] == 'Resolved'])
    st.progress(resolved/total if total > 0 else 0)
    st.caption(f"{resolved}/{total} Issues Resolved")

# ============================================
# REST OF YOUR CODE CONTINUES EXACTLY THE SAME...
# (Keep all pages: Dashboard, Report Issue, AI Detection, Issue Tracker, Analytics, Heatmap)
# ============================================
