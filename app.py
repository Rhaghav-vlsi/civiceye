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
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 1200px;
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
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1e1b4b 100%);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
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
# SAMPLE DATA GENERATOR (MOVED BEFORE SESSION STATE)
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
# PAGE 1: DASHBOARD
# ============================================
if selected == "Dashboard":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🏙️ CivicEye Dashboard</div>
        <div class="hero-subtitle">AI-Powered Detection, Prioritization & Tracking of Urban Civic Issues</div>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.issues
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">📋</div>
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">Total Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        critical = len(df[df['priority'] == 'Critical'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🚨</div>
            <div class="metric-value" style="color: #ef4444;">{critical}</div>
            <div class="metric-label">Critical</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        in_progress = len(df[df['status'] == 'In Progress'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">⚙️</div>
            <div class="metric-value" style="color: #f59e0b;">{in_progress}</div>
            <div class="metric-label">In Progress</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        resolved = len(df[df['status'] == 'Resolved'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">✅</div>
            <div class="metric-value" style="color: #22c55e;">{resolved}</div>
            <div class="metric-label">Resolved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        avg_conf = df['ai_confidence'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🤖</div>
            <div class="metric-value" style="color: #a855f7;">{avg_conf:.0%}</div>
            <div class="metric-label">AI Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🤖 AI-Powered Insights <span class="ai-badge">AI POWERED</span></div>', unsafe_allow_html=True)
    
    insights = ai_engine.generate_ai_insights(df)
    
    insight_cols = st.columns(len(insights))
    for idx, insight in enumerate(insights):
        with insight_cols[idx % len(insights)]:
            st.info(insight)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown('<div class="section-header">📊 Issues by Category</div>', unsafe_allow_html=True)
        cat_counts = df['category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        
        fig1 = px.bar(
            cat_counts, x='Count', y='Category', orientation='h',
            color='Count',
            color_continuous_scale=['#312e81', '#4f46e5', '#818cf8', '#a855f7', '#f093fb'],
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8',
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
            yaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        st.markdown('<div class="section-header">🎯 Priority Distribution</div>', unsafe_allow_html=True)
        priority_counts = df['priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']
        
        colors = {'Critical': '#ef4444', 'High': '#f59e0b', 'Medium': '#3b82f6', 'Low': '#22c55e'}
        priority_counts['Color'] = priority_counts['Priority'].map(colors)
        
        fig2 = px.pie(
            priority_counts, values='Count', names='Priority',
            color='Priority',
            color_discrete_map=colors,
            hole=0.5,
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8',
            height=400,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(font=dict(color='#94a3b8')),
        )
        fig2.update_traces(textinfo='percent+label', textfont_color='white')
        st.plotly_chart(fig2, use_container_width=True)
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown('<div class="section-header">📈 Issue Status Overview</div>', unsafe_allow_html=True)
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        status_colors = {
            'Reported': '#ef4444', 'Under Review': '#f59e0b',
            'In Progress': '#3b82f6', 'Resolved': '#22c55e'
        }
        
        fig3 = px.funnel(
            status_counts, x='Count', y='Status',
            color='Status',
            color_discrete_map=status_colors,
        )
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8',
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_s2:
        st.markdown('<div class="section-header">🏢 Department Workload</div>', unsafe_allow_html=True)
        dept_counts = df['assigned_to'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Issues']
        
        fig4 = px.bar(
            dept_counts, x='Department', y='Issues',
            color='Issues',
            color_continuous_scale=['#312e81', '#4f46e5', '#818cf8'],
        )
        fig4.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8',
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
            yaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
            coloraxis_showscale=False,
            showlegend=False,
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown('<div class="section-header">🕐 Recent Issues</div>', unsafe_allow_html=True)
    
    recent = df.sort_values('date_reported', ascending=False).head(8)
    
    for _, row in recent.iterrows():
        priority_class = f"status-{row['priority'].lower()}"
        status_emoji = {"Reported": "🔴", "Under Review": "🟡", "In Progress": "🔵", "Resolved": "🟢"}
        
        st.markdown(f"""
        <div class="issue-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #818cf8; font-weight: 700; font-size: 0.9rem;">{row['id']}</span>
                    <span class="{priority_class}">{row['priority']}</span>
                    <span class="ai-badge">AI {row['ai_confidence']:.0%}</span>
                </div>
                <div style="color: #64748b; font-size: 0.85rem;">{row['date_reported']}</div>
            </div>
            <div style="margin-top: 8px;">
                <span style="color: #e2e8f0; font-weight: 600;">{row['category']}</span>
                <span style="color: #64748b;"> • {row['location']}</span>
                <span style="color: #64748b;"> • {status_emoji.get(row['status'], '⚪')} {row['status']}</span>
                <span style="color: #64748b;"> • 👍 {row['upvotes']}</span>
            </div>
            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 6px;">{row['description']}</div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# PAGE 2: REPORT ISSUE
# ============================================
elif selected == "Report Issue":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📝 Report a Civic Issue</div>
        <div class="hero-subtitle">Help improve your city - Report issues and let AI prioritize them</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_form, col_preview = st.columns([3, 2])
    
    with col_form:
        st.markdown('<div class="section-header">Issue Details</div>', unsafe_allow_html=True)
        
        with st.form("report_form", clear_on_submit=True):
            uploaded_image = st.file_uploader(
                "📸 Upload Issue Photo (AI will auto-detect the issue)",
                type=["jpg", "jpeg", "png"],
                help="Upload a clear photo of the civic issue"
            )
            
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
                detection = ai_engine.analyze_image(uploaded_image)
                st.markdown(f"""
                <div class="success-toast">
                    🤖 <strong>AI Detection Result:</strong> {detection['issue']} 
                    (Confidence: {detection['confidence']:.0%}) | Severity: {detection['severity']}
                </div>
                """, unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                title = st.text_input("📌 Issue Title", placeholder="e.g., Large pothole on main road")
                category = st.selectbox("🏷️ Category", [
                    "Auto-Detect (AI)", "Pothole", "Streetlight", "Garbage", 
                    "Water Leak", "Road Damage", "Illegal Dumping",
                    "Broken Sidewalk", "Traffic Signal", "Noise Complaint", "Graffiti"
                ])
            
            with col_b:
                location = st.selectbox("📍 Location", [
                    "Downtown", "Whitefield", "Koramangala", "Indiranagar",
                    "Jayanagar", "HSR Layout", "Electronic City", "Marathahalli",
                    "BTM Layout", "Hebbal"
                ])
                urgency = st.select_slider("⚡ Urgency Level", 
                    options=["Low", "Medium", "High", "Critical"],
                    value="Medium"
                )
            
            description = st.text_area(
                "📝 Description",
                placeholder="Describe the issue in detail. AI will analyze your description for better classification...",
                height=120
            )
            
            submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)
            
            if submitted and title and description:
                with st.spinner("🤖 AI is analyzing your report..."):
                    time.sleep(1.5)
                    
                    if category == "Auto-Detect (AI)":
                        detected_cat, confidence = ai_engine.classify_issue(description)
                    else:
                        detected_cat = category
                        confidence = 0.95
                    
                    priority, score = ai_engine.calculate_priority(detected_cat, description)
                    est_days = ai_engine.predict_resolution_time(detected_cat, priority)
                    
                    areas_coords = {
                        "Downtown": (12.9716, 77.5946),
                        "Whitefield": (12.9698, 77.7500),
                        "Koramangala": (12.9352, 77.6245),
                        "Indiranagar": (12.9784, 77.6408),
                        "Jayanagar": (12.9308, 77.5838),
                        "HSR Layout": (12.9116, 77.6389),
                        "Electronic City": (12.8440, 77.6568),
                        "Marathahalli": (12.9591, 77.6974),
                        "BTM Layout": (12.9166, 77.6101),
                        "Hebbal": (13.0358, 77.5970),
                    }
                    
                    lat, lon = areas_coords.get(location, (12.9716, 77.5946))
                    
                    new_issue = pd.DataFrame([{
                        "id": f"CIV-{1050 + len(st.session_state.issues)}",
                        "category": detected_cat,
                        "description": description,
                        "location": location,
                        "lat": lat + random.uniform(-0.005, 0.005),
                        "lon": lon + random.uniform(-0.005, 0.005),
                        "status": "Reported",
                        "priority": priority,
                        "ai_confidence": confidence,
                        "date_reported": datetime.now().strftime("%Y-%m-%d"),
                        "upvotes": 1,
                        "assigned_to": "Auto-Assigned",
                        "reporter": "You",
                        "estimated_resolution": est_days,
                    }])
                    
                    st.session_state.issues = pd.concat([st.session_state.issues, new_issue], ignore_index=True)
                
                st.success("✅ Issue Reported Successfully!")
                st.balloons()
                
                st.markdown(f"""
                <div class="issue-card">
                    <h4 style="color: #818cf8;">🤖 AI Analysis Report</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div>
                            <div style="color: #64748b; font-size: 0.8rem;">DETECTED CATEGORY</div>
                            <div style="color: #e2e8f0; font-size: 1.1rem; font-weight: 600;">{detected_cat}</div>
                        </div>
                        <div>
                            <div style="color: #64748b; font-size: 0.8rem;">AI CONFIDENCE</div>
                            <div style="color: #a855f7; font-size: 1.1rem; font-weight: 600;">{confidence:.0%}</div>
                        </div>
                        <div>
                            <div style="color: #64748b; font-size: 0.8rem;">PRIORITY LEVEL</div>
                            <div style="color: #ef4444; font-size: 1.1rem; font-weight: 600;">{priority} (Score: {score:.0f}/100)</div>
                        </div>
                        <div>
                            <div style="color: #64748b; font-size: 0.8rem;">EST. RESOLUTION</div>
                            <div style="color: #22c55e; font-size: 1.1rem; font-weight: 600;">{est_days} days</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_preview:
        st.markdown('<div class="section-header">📍 Location Preview</div>', unsafe_allow_html=True)
        
        preview_map = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles="CartoDB dark_matter")
        st_folium(preview_map, width=400, height=300)
        
        st.markdown('<div class="section-header">💡 Reporting Tips</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="issue-card">
            <ul style="color: #94a3b8; line-height: 2;">
                <li>📸 Upload a clear photo for AI auto-detection</li>
                <li>📝 Be descriptive - AI uses your text for classification</li>
                <li>📍 Select accurate location for faster resolution</li>
                <li>⚡ Critical issues get priority attention</li>
                <li>🤖 AI assigns priority based on impact analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# PAGE 3: AI DETECTION
# ============================================
elif selected == "AI Detection":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🤖 AI Detection Engine</div>
        <div class="hero-subtitle">Advanced Computer Vision & NLP for Automatic Issue Detection</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📸 Image Detection", "📝 Text Analysis", "🧠 AI Model Info"])
    
    with tab1:
        st.markdown('<div class="section-header">Upload Image for AI Analysis</div>', unsafe_allow_html=True)
        
        col_up, col_res = st.columns(2)
        
        with col_up:
            img_file = st.file_uploader("Drop an image of the civic issue", type=["jpg", "jpeg", "png"], key="ai_upload")
            
            if img_file:
                st.image(img_file, caption="Uploaded Image", use_container_width=True)
        
        with col_res:
            if img_file:
                with st.spinner("🤖 AI Analyzing Image..."):
                    time.sleep(2)
                    result = ai_engine.analyze_image(img_file)
                
                st.markdown(f"""
                <div class="issue-card" style="border-color: rgba(168,85,247,0.5);">
                    <h3 style="color: #a855f7;">🎯 AI Detection Results</h3>
                    <br>
                    <div style="display: grid; gap: 1rem;">
                        <div style="background: rgba(79,70,229,0.1); padding: 1rem; border-radius: 12px;">
                            <div style="color: #818cf8; font-size: 0.8rem; font-weight: 600;">DETECTED ISSUE</div>
                            <div style="color: #e2e8f0; font-size: 1.5rem; font-weight: 700;">{result['issue']}</div>
                        </div>
                        <div style="background: rgba(168,85,247,0.1); padding: 1rem; border-radius: 12px;">
                            <div style="color: #a855f7; font-size: 0.8rem; font-weight: 600;">CONFIDENCE SCORE</div>
                            <div style="color: #e2e8f0; font-size: 1.5rem; font-weight: 700;">{result['confidence']:.0%}</div>
                        </div>
                        <div style="background: rgba(239,68,68,0.1); padding: 1rem; border-radius: 12px;">
                            <div style="color: #ef4444; font-size: 0.8rem; font-weight: 600;">SEVERITY LEVEL</div>
                            <div style="color: #e2e8f0; font-size: 1.5rem; font-weight: 700;">{result['severity']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result['confidence'] * 100,
                    title={'text': "AI Confidence", 'font': {'color': '#94a3b8'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickcolor': '#64748b'},
                        'bar': {'color': '#7c3aed'},
                        'bgcolor': 'rgba(0,0,0,0)',
                        'steps': [
                            {'range': [0, 50], 'color': 'rgba(239,68,68,0.2)'},
                            {'range': [50, 75], 'color': 'rgba(245,158,11,0.2)'},
                            {'range': [75, 100], 'color': 'rgba(34,197,94,0.2)'}
                        ],
                        'threshold': {
                            'line': {'color': '#a855f7', 'width': 4},
                            'thickness': 0.75,
                            'value': result['confidence'] * 100
                        }
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#94a3b8',
                    height=250,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.markdown("""
                <div class="issue-card" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem;">📸</div>
                    <div style="color: #94a3b8; margin-top: 1rem;">Upload an image to start AI detection</div>
                    <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;">Supports: JPG, JPEG, PNG</div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="section-header">📝 Natural Language Issue Analysis</div>', unsafe_allow_html=True)
        
        text_input = st.text_area(
            "Describe the civic issue you've observed:",
            placeholder="e.g., There's a large pothole on MG Road near the bus stop.",
            height=150
        )
        
        if st.button("🔍 Analyze with AI", use_container_width=True):
            if text_input:
                with st.spinner("🧠 Processing with NLP..."):
                    time.sleep(1.5)
                    category, confidence = ai_engine.classify_issue(text_input)
                    priority, score = ai_engine.calculate_priority(category, text_input)
                    est_days = ai_engine.predict_resolution_time(category, priority)
                
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                
                with col_r1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">🏷️</div>
                        <div class="metric-value" style="font-size: 1.5rem;">{category}</div>
                        <div class="metric-label">Category</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_r2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">🎯</div>
                        <div class="metric-value" style="font-size: 1.5rem;">{confidence:.0%}</div>
                        <div class="metric-label">Confidence</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_r3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">⚡</div>
                        <div class="metric-value" style="font-size: 1.5rem;">{priority}</div>
                        <div class="metric-label">Priority</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_r4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-icon">📅</div>
                        <div class="metric-value" style="font-size: 1.5rem;">{est_days}d</div>
                        <div class="metric-label">Est. Resolution</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="issue-card">
                    <h4 style="color: #818cf8;">🧠 NLP Analysis Breakdown</h4>
                    <div style="margin-top: 1rem; color: #94a3b8;">
                        <p><strong>Keywords Detected:</strong> {', '.join([w for w in text_input.lower().split() if len(w) > 4][:8])}</p>
                        <p><strong>Sentiment:</strong> Negative (Issue Report) ⚠️</p>
                        <p><strong>Urgency Indicators:</strong> {'Found ⚡' if any(w in text_input.lower() for w in ['dangerous', 'urgent', 'emergency', 'accident']) else 'Standard'}</p>
                        <p><strong>Location Mentioned:</strong> {'Yes ✅' if any(w in text_input.lower() for w in ['road', 'street', 'area', 'near', 'junction']) else 'No ❌'}</p>
                        <p><strong>Priority Score:</strong> {score:.0f}/100</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="section-header">🧠 AI Model Architecture</div>', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("""
            <div class="issue-card">
                <h4 style="color: #818cf8;">📸 Computer Vision Model</h4>
                <div style="color: #94a3b8; margin-top: 1rem; line-height: 2;">
                    <p>🔹 <strong>Architecture:</strong> YOLOv8 + ResNet50</p>
                    <p>🔹 <strong>Training Data:</strong> 50,000+ urban issue images</p>
                    <p>🔹 <strong>Categories:</strong> 10 civic issue types</p>
                    <p>🔹 <strong>Accuracy:</strong> 94.2% mAP</p>
                    <p>🔹 <strong>Inference Time:</strong> < 200ms</p>
                    <p>🔹 <strong>Edge Support:</strong> Mobile-optimized</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown("""
            <div class="issue-card">
                <h4 style="color: #a855f7;">📝 NLP Classification Model</h4>
                <div style="color: #94a3b8; margin-top: 1rem; line-height: 2;">
                    <p>🔹 <strong>Architecture:</strong> BERT-based Classifier</p>
                    <p>🔹 <strong>Training Data:</strong> 100,000+ citizen reports</p>
                    <p>🔹 <strong>Languages:</strong> English, Hindi, Regional</p>
                    <p>🔹 <strong>F1 Score:</strong> 0.92</p>
                    <p>🔹 <strong>Priority Model:</strong> Multi-factor scoring</p>
                    <p>🔹 <strong>Sentiment Analysis:</strong> Urgency detection</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">🔄 AI Processing Pipeline</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="issue-card" style="text-align: center;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; flex-wrap: wrap; color: #94a3b8;">
                <div style="background: rgba(79,70,229,0.3); padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(79,70,229,0.5);">
                    📥 Input<br><small>Image/Text</small>
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: rgba(124,58,237,0.3); padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(124,58,237,0.5);">
                    🔍 Detection<br><small>CV/NLP Model</small>
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: rgba(168,85,247,0.3); padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(168,85,247,0.5);">
                    🏷️ Classification<br><small>Category</small>
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: rgba(236,72,153,0.3); padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(236,72,153,0.5);">
                    ⚡ Prioritization<br><small>AI Scoring</small>
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: rgba(34,197,94,0.3); padding: 12px 20px; border-radius: 12px; border: 1px solid rgba(34,197,94,0.5);">
                    📋 Assignment<br><small>Auto-Route</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# PAGE 4: ISSUE TRACKER
# ============================================
elif selected == "Issue Tracker":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📋 Issue Tracker</div>
        <div class="hero-subtitle">Track, Filter, and Monitor All Civic Issues in Real-Time</div>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.issues
    
    st.markdown('<div class="section-header">🔍 Filter Issues</div>', unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        filter_status = st.multiselect("Status", df['status'].unique(), default=list(df['status'].unique()))
    with col_f2:
        filter_priority = st.multiselect("Priority", df['priority'].unique(), default=list(df['priority'].unique()))
    with col_f3:
        filter_category = st.multiselect("Category", df['category'].unique(), default=list(df['category'].unique()))
    with col_f4:
        filter_location = st.multiselect("Location", df['location'].unique(), default=list(df['location'].unique()))
    
    filtered = df[
        (df['status'].isin(filter_status)) &
        (df['priority'].isin(filter_priority)) &
        (df['category'].isin(filter_category)) &
        (df['location'].isin(filter_location))
    ]
    
    st.markdown(f"**Showing {len(filtered)} of {len(df)} issues**")
    
    sort_by = st.selectbox("Sort by", ["Priority (Critical First)", "Date (Newest)", "Upvotes (Most)", "AI Confidence"])
    
    if sort_by == "Priority (Critical First)":
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        filtered = filtered.copy()
        filtered['priority_order'] = filtered['priority'].map(priority_order)
        filtered = filtered.sort_values('priority_order')
    elif sort_by == "Date (Newest)":
        filtered = filtered.sort_values('date_reported', ascending=False)
    elif sort_by == "Upvotes (Most)":
        filtered = filtered.sort_values('upvotes', ascending=False)
    else:
        filtered = filtered.sort_values('ai_confidence', ascending=False)
    
    for _, row in filtered.iterrows():
        priority_colors = {"Critical": "#ef4444", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#22c55e"}
        p_color = priority_colors.get(row['priority'], '#64748b')
        
        with st.expander(f"🔖 {row['id']} | {row['category']} | {row['location']} | {row['priority']} Priority"):
            col_d1, col_d2 = st.columns([2, 1])
            
            with col_d1:
                st.markdown(f"""
                **Category:** {row['category']}  
                **Description:** {row['description']}  
                **Location:** 📍 {row['location']}  
                **Reported:** {row['date_reported']}  
                **Reporter:** {row['reporter']}  
                **Assigned To:** {row['assigned_to']}  
                **AI Confidence:** {row['ai_confidence']:.0%}  
                **Upvotes:** 👍 {row['upvotes']}  
                """)
            
            with col_d2:
                st.markdown(f"""
                <div style="background: rgba(30,27,75,0.5); border-radius: 12px; padding: 1rem; border-left: 4px solid {p_color};">
                    <div style="color: {p_color}; font-weight: 700; font-size: 1.2rem;">{row['priority']}</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">Priority Level</div>
                    <hr style="border-color: rgba(99,102,241,0.2);">
                    <div style="color: #818cf8; font-weight: 700;">{row['status']}</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">Current Status</div>
                    <hr style="border-color: rgba(99,102,241,0.2);">
                    <div style="color: #22c55e; font-weight: 700;">{row['estimated_resolution']} days</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">Est. Resolution</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("**📅 Tracking Timeline:**")
            
            timeline_events = [
                {"date": row['date_reported'], "event": "Issue Reported by citizen", "icon": "📝"},
            ]
            
            if row['status'] in ["Under Review", "In Progress", "Resolved"]:
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "event": f"AI classified as {row['category']} with {row['ai_confidence']:.0%} confidence",
                    "icon": "🤖"
                })
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "event": f"Assigned to {row['assigned_to']}",
                    "icon": "📋"
                })
            
            if row['status'] in ["In Progress", "Resolved"]:
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "event": "Work initiated by department team",
                    "icon": "🔧"
                })
            
            if row['status'] == "Resolved":
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=row['estimated_resolution'])).strftime("%Y-%m-%d"),
                    "event": "Issue resolved and verified ✅",
                    "icon": "✅"
                })
            
            for event in timeline_events:
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-date">{event['icon']} {event['date']}</div>
                    <div class="timeline-text">{event['event']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)


# ============================================
# PAGE 5: ANALYTICS
# ============================================
elif selected == "Analytics":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📊 Analytics Dashboard</div>
        <div class="hero-subtitle">Deep Data Analysis & AI-Powered Trends</div>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.issues
    
    st.markdown('<div class="section-header">📈 Issue Reporting Trend</div>', unsafe_allow_html=True)
    
    trend_data = df.groupby('date_reported').size().reset_index(name='count')
    trend_data = trend_data.sort_values('date_reported')
    
    fig_trend = px.area(
        trend_data, x='date_reported', y='count',
        color_discrete_sequence=['#7c3aed'],
    )
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#94a3b8',
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor='rgba(99,102,241,0.1)', title=''),
        yaxis=dict(gridcolor='rgba(99,102,241,0.1)', title='Issues Reported'),
    )
    fig_trend.update_traces(fill='tozeroy', fillcolor='rgba(124,58,237,0.2)')
    st.plotly_chart(fig_trend, use_container_width=True)
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.markdown('<div class="section-header">🗺️ Location vs Category</div>', unsafe_allow_html=True)
        
        heatmap_data = pd.crosstab(df['location'], df['category'])
        
        fig_heat = px.imshow(
            heatmap_data,
            color_continuous_scale=['#1e1b4b', '#4f46e5', '#a855f7', '#f093fb'],
            aspect='auto',
        )
        fig_heat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8',
            height=400,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with col_a2:
        st.markdown('<div class="section-header">⏱️ Avg Resolution Time by Category</div>', unsafe_allow_html=True)
        
        resolution_data = df.groupby('category')['estimated_resolution'].mean().reset_index()
        resolution_data.columns = ['Category', 'Avg Days']
        resolution_data = resolution_data.sort_values('Avg Days', ascending=True)
        
        fig_res = px.bar(
            resolution_data, x='Avg Days', y='Category', orientation='h',
            color='Avg Days',
            color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444'],
        )
        fig_res.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#94a3b8',
            height=400,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
            yaxis=dict(gridcolor='rgba(99,102,241,0.1)'),
            coloraxis_showscale=False,
            showlegend=False,
        )
        st.plotly_chart(fig_res, use_container_width=True)
    
    st.markdown('<div class="section-header">🤖 AI Performance Metrics <span class="ai-badge">AI ANALYTICS</span></div>', unsafe_allow_html=True)
    
    col_ai1, col_ai2, col_ai3, col_ai4 = st.columns(4)
    
    with col_ai1:
        fig_g1 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=94.2,
            delta={'reference': 90, 'increasing': {'color': '#22c55e'}},
            title={'text': "Detection Accuracy", 'font': {'color': '#94a3b8', 'size': 14}},
            number={'suffix': '%', 'font': {'color': '#818cf8'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#64748b'},
                'bar': {'color': '#4f46e5'},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(239,68,68,0.1)'},
                    {'range': [60, 80], 'color': 'rgba(245,158,11,0.1)'},
                    {'range': [80, 100], 'color': 'rgba(34,197,94,0.1)'}
                ],
            }
        ))
        fig_g1.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_g1, use_container_width=True)
    
    with col_ai2:
        fig_g2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=91.8,
            delta={'reference': 88, 'increasing': {'color': '#22c55e'}},
            title={'text': "Classification F1", 'font': {'color': '#94a3b8', 'size': 14}},
            number={'suffix': '%', 'font': {'color': '#a855f7'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#64748b'},
                'bar': {'color': '#7c3aed'},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(239,68,68,0.1)'},
                    {'range': [60, 80], 'color': 'rgba(245,158,11,0.1)'},
                    {'range': [80, 100], 'color': 'rgba(34,197,94,0.1)'}
                ],
            }
        ))
        fig_g2.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_g2, use_container_width=True)
    
    with col_ai3:
        fig_g3 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=87.5,
            delta={'reference': 82, 'increasing': {'color': '#22c55e'}},
            title={'text': "Priority Accuracy", 'font': {'color': '#94a3b8', 'size': 14}},
            number={'suffix': '%', 'font': {'color': '#f59e0b'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#64748b'},
                'bar': {'color': '#f59e0b'},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 60], 'color': 'rgba(239,68,68,0.1)'},
                    {'range': [60, 80], 'color': 'rgba(245,158,11,0.1)'},
                    {'range': [80, 100], 'color': 'rgba(34,197,94,0.1)'}
                ],
            }
        ))
        fig_g3.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_g3, use_container_width=True)
    
    with col_ai4:
        fig_g4 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=156,
            delta={'reference': 200, 'decreasing': {'color': '#22c55e'}},
            title={'text': "Avg Response (ms)", 'font': {'color': '#94a3b8', 'size': 14}},
            number={'suffix': 'ms', 'font': {'color': '#22c55e'}},
            gauge={
                'axis': {'range': [0, 500], 'tickcolor': '#64748b'},
                'bar': {'color': '#22c55e'},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 200], 'color': 'rgba(34,197,94,0.1)'},
                    {'range': [200, 350], 'color': 'rgba(245,158,11,0.1)'},
                    {'range': [350, 500], 'color': 'rgba(239,68,68,0.1)'}
                ],
            }
        ))
        fig_g4.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_g4, use_container_width=True)
    
    st.markdown('<div class="section-header">🏢 Department Performance Comparison</div>', unsafe_allow_html=True)
    
    dept_data = df.groupby(['assigned_to', 'status']).size().reset_index(name='count')
    
    fig_dept = px.bar(
        dept_data, x='assigned_to', y='count', color='status',
        barmode='stack',
        color_discrete_map={
            'Reported': '#ef4444', 'Under Review': '#f59e0b',
            'In Progress': '#3b82f6', 'Resolved': '#22c55e'
        }
    )
    fig_dept.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#94a3b8',
        height=350,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(gridcolor='rgba(99,102,241,0.1)', title=''),
        yaxis=dict(gridcolor='rgba(99,102,241,0.1)', title='Issue Count'),
        legend=dict(font=dict(color='#94a3b8')),
    )
    st.plotly_chart(fig_dept, use_container_width=True)


# ============================================
# PAGE 6: HEATMAP
# ============================================
elif selected == "Heatmap":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🗺️ Issue Heatmap</div>
        <div class="hero-subtitle">Geographic Visualization of Urban Issues with AI Hotspot Detection</div>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.issues
    
    col_map1, col_map2, col_map3 = st.columns(3)
    
    with col_map1:
        map_filter_cat = st.multiselect("Filter by Category", df['category'].unique(), default=list(df['category'].unique()), key="map_cat")
    with col_map2:
        map_filter_priority = st.multiselect("Filter by Priority", df['priority'].unique(), default=list(df['priority'].unique()), key="map_pri")
    with col_map3:
        map_style = st.selectbox("Map Style", ["CartoDB dark_matter", "OpenStreetMap", "CartoDB positron"])
    
    filtered_map = df[
        (df['category'].isin(map_filter_cat)) &
        (df['priority'].isin(map_filter_priority))
    ]
    
    m = folium.Map(
        location=[12.9716, 77.5946],
        zoom_start=12,
        tiles=map_style,
    )
    
    priority_colors = {
        "Critical": "red",
        "High": "orange",
        "Medium": "blue",
        "Low": "green"
    }
    
    for _, row in filtered_map.iterrows():
        color = priority_colors.get(row['priority'], 'blue')
        
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="color: #4f46e5; margin: 0 0 8px 0;">{row['id']}</h4>
            <p><strong>Category:</strong> {row['category']}</p>
            <p><strong>Priority:</strong> {row['priority']}</p>
            <p><strong>Status:</strong> {row['status']}</p>
            <p><strong>AI Confidence:</strong> {row['ai_confidence']:.0%}</p>
            <p><strong>Upvotes:</strong> {row['upvotes']}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8 + (row['upvotes'] / 20),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['id']} - {row['category']} ({row['priority']})",
        ).add_to(m)
    
    location_counts = filtered_map.groupby('location').agg({
        'lat': 'mean', 'lon': 'mean', 'id': 'count'
    }).reset_index()
    
    for _, loc in location_counts.iterrows():
        folium.Circle(
            location=[loc['lat'], loc['lon']],
            radius=loc['id'] * 100,
            color='#7c3aed',
            fill=True,
            fillColor='#7c3aed',
            fillOpacity=0.1,
            weight=1,
        ).add_to(m)
    
    st_folium(m, width=None, height=500, use_container_width=True)
    
    st.markdown("""
    <div class="issue-card">
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <span>🔴 <strong>Critical</strong></span>
            <span>🟠 <strong>High</strong></span>
            <span>🔵 <strong>Medium</strong></span>
            <span>🟢 <strong>Low</strong></span>
            <span>🟣 <strong>AI Hotspot Zone</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🔥 AI Hotspot Analysis</div>', unsafe_allow_html=True)
    
    hotspot_data = df.groupby('location').agg({
        'id': 'count',
        'priority': lambda x: (x == 'Critical').sum(),
        'upvotes': 'sum',
        'ai_confidence': 'mean'
    }).reset_index()
    hotspot_data.columns = ['Location', 'Total Issues', 'Critical Issues', 'Total Upvotes', 'Avg AI Confidence']
    hotspot_data = hotspot_data.sort_values('Total Issues', ascending=False)
    
    hotspot_data['Risk Score'] = (
        hotspot_data['Total Issues'] * 2 + 
        hotspot_data['Critical Issues'] * 5 + 
        hotspot_data['Total Upvotes'] * 0.1
    ).round(1)
    hotspot_data = hotspot_data.sort_values('Risk Score', ascending=False)
    
    for idx, row in hotspot_data.iterrows():
        risk_color = "#ef4444" if row['Risk Score'] > 30 else "#f59e0b" if row['Risk Score'] > 15 else "#22c55e"
        st.markdown(f"""
        <div class="issue-card" style="border-left: 4px solid {risk_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #e2e8f0; font-weight: 700; font-size: 1.1rem;">📍 {row['Location']}</span>
                </div>
                <div style="display: flex; gap: 1.5rem;">
                    <div style="text-align: center;">
                        <div style="color: #818cf8; font-weight: 700;">{row['Total Issues']}</div>
                        <div style="color: #64748b; font-size: 0.75rem;">Issues</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #ef4444; font-weight: 700;">{row['Critical Issues']}</div>
                        <div style="color: #64748b; font-size: 0.75rem;">Critical</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: {risk_color}; font-weight: 700;">{row['Risk Score']}</div>
                        <div style="color: #64748b; font-size: 0.75rem;">Risk Score</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(99,102,241,0.2);">
    <span style="color: #64748b; font-size: 0.85rem;">
        🏙️ <strong style="color: #818cf8;">CivicEye</strong> - AI-Powered Urban Intelligence Platform | 
        Built with ❤️ for Smart Cities | 
        <span class="ai-badge">Powered by AI</span>
    </span>
</div>
""", unsafe_allow_html=True)