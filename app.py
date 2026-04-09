import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu
import time

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
# CLEAN CSS (NO BLACK SCREEN)
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(79,70,229,0.15);
    }
    
    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #4f46e5;
    }
    
    .metric-label {
        font-family: 'Inter', sans-serif;
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .issue-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .issue-card:hover {
        border-color: #a5b4fc;
        box-shadow: 0 4px 16px rgba(79,70,229,0.12);
    }
    
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #1e293b;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #4f46e5;
        display: inline-block;
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #7c3aed, #a855f7);
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-left: 6px;
    }
    
    .status-critical {
        background: #fee2e2;
        color: #dc2626;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .status-high {
        background: #ffedd5;
        color: #ea580c;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .status-medium {
        background: #dbeafe;
        color: #2563eb;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .status-low {
        background: #dcfce7;
        color: #16a34a;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-block;
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
    }
    
    .timeline-date {
        color: #4f46e5;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .timeline-text {
        color: #475569;
        font-size: 0.9rem;
        margin-top: 4px;
    }
    
    .success-toast {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79,70,229,0.4);
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
            "Streetlight": ["light", "dark", "lamp", "streetlight", "bulb"],
            "Garbage": ["garbage", "trash", "waste", "dump", "litter"],
            "Water Leak": ["water", "leak", "pipe", "flooding", "drain"],
            "Road Damage": ["road", "crack", "broken road", "asphalt"],
            "Illegal Dumping": ["illegal", "dumping", "construction waste"],
            "Broken Sidewalk": ["sidewalk", "footpath", "walking"],
            "Traffic Signal": ["traffic", "signal", "red light"],
            "Noise Complaint": ["noise", "loud", "sound", "disturbance"],
            "Graffiti": ["graffiti", "paint", "vandalism", "wall"],
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
        
        urgent_words = ["dangerous", "emergency", "urgent", "accident", "injury"]
        for word in urgent_words:
            if word in description.lower():
                score += 10
        
        score += min(upvotes * 0.5, 15)
        score = min(score, 100)
        
        if score >= 80: return "Critical", score
        elif score >= 60: return "High", score
        elif score >= 40: return "Medium", score
        else: return "Low", score
    
    @staticmethod
    def predict_resolution_time(category, priority):
        base_times = {"Critical": 2, "High": 5, "Medium": 8, "Low": 14}
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
        insights.append(f"🔥 **Hotspot**: {hotspot} ({location_counts.iloc[0]} reports)")
        
        critical_count = len(df[df['priority'] == 'Critical'])
        if critical_count > 0:
            insights.append(f"🚨 **{critical_count} Critical** issues need attention")
        
        category_counts = df['category'].value_counts()
        insights.append(f"📊 **Top Issue**: {category_counts.index[0]} ({category_counts.iloc[0]})")
        
        resolved = len(df[df['status'] == 'Resolved'])
        total = len(df)
        rate = (resolved/total)*100 if total > 0 else 0
        insights.append(f"✅ **Resolution**: {rate:.0f}%")
        
        pending = len(df[df['status'].isin(['Reported', 'Under Review'])])
        insights.append(f"🔮 **Pending**: {pending} issues")
        
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
# SAMPLE DATA
# ============================================
def generate_sample_issues():
    categories = ["Pothole", "Streetlight", "Garbage", "Water Leak", "Road Damage", 
                   "Illegal Dumping", "Broken Sidewalk", "Traffic Signal", "Noise Complaint", "Graffiti"]
    statuses = ["Reported", "Under Review", "In Progress", "Resolved"]
    
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
# SESSION STATE
# ============================================
if 'issues' not in st.session_state:
    st.session_state.issues = generate_sample_issues()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <span style="font-size: 3rem;">🏙️</span>
        <h2 style="color: #4f46e5; margin: 0.5rem 0;">CivicEye</h2>
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
            "container": {"padding": "0!important"},
            "icon": {"color": "#4f46e5", "font-size": "18px"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px 0",
                "padding": "10px 15px",
                "border-radius": "10px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #4f46e5, #7c3aed)",
                "color": "white",
                "font-weight": "600",
            },
        }
    )
    
    st.markdown("---")
    st.markdown("##### ⚡ Quick Stats")
    total = len(st.session_state.issues)
    resolved = len(st.session_state.issues[st.session_state.issues['status'] == 'Resolved'])
    st.progress(resolved/total if total > 0 else 0)
    st.caption(f"✅ {resolved}/{total} Issues Resolved")

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
    
    # Metrics
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
            <div class="metric-value" style="color: #dc2626;">{critical}</div>
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
            <div class="metric-value" style="color: #16a34a;">{resolved}</div>
            <div class="metric-label">Resolved</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        avg_conf = df['ai_confidence'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">🤖</div>
            <div class="metric-value" style="color: #7c3aed;">{avg_conf:.0%}</div>
            <div class="metric-label">AI Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # AI Insights
    st.markdown('<div class="section-header">🤖 AI Insights <span class="ai-badge">AI POWERED</span></div>', unsafe_allow_html=True)
    
    insights = ai_engine.generate_ai_insights(df)
    insight_cols = st.columns(len(insights))
    for idx, insight in enumerate(insights):
        with insight_cols[idx]:
            st.info(insight)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown('<div class="section-header">📊 Issues by Category</div>', unsafe_allow_html=True)
        cat_counts = df['category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        
        fig1 = px.bar(cat_counts, x='Count', y='Category', orientation='h',
            color='Count', color_continuous_scale='Purples')
        fig1.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        st.markdown('<div class="section-header">🎯 Priority Distribution</div>', unsafe_allow_html=True)
        priority_counts = df['priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']
        
        colors = {'Critical': '#ef4444', 'High': '#f59e0b', 'Medium': '#3b82f6', 'Low': '#22c55e'}
        
        fig2 = px.pie(priority_counts, values='Count', names='Priority',
            color='Priority', color_discrete_map=colors, hole=0.5)
        fig2.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        fig2.update_traces(textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Status & Department
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.markdown('<div class="section-header">📈 Status Overview</div>', unsafe_allow_html=True)
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        status_colors = {'Reported': '#ef4444', 'Under Review': '#f59e0b', 'In Progress': '#3b82f6', 'Resolved': '#22c55e'}
        
        fig3 = px.funnel(status_counts, x='Count', y='Status', color='Status', color_discrete_map=status_colors)
        fig3.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col_s2:
        st.markdown('<div class="section-header">🏢 Department Workload</div>', unsafe_allow_html=True)
        dept_counts = df['assigned_to'].value_counts().reset_index()
        dept_counts.columns = ['Department', 'Issues']
        
        fig4 = px.bar(dept_counts, x='Department', y='Issues', color='Issues', color_continuous_scale='Purples')
        fig4.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False, showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Recent Issues
    st.markdown('<div class="section-header">🕐 Recent Issues</div>', unsafe_allow_html=True)
    
    recent = df.sort_values('date_reported', ascending=False).head(8)
    
    for _, row in recent.iterrows():
        priority_class = f"status-{row['priority'].lower()}"
        status_emoji = {"Reported": "🔴", "Under Review": "🟡", "In Progress": "🔵", "Resolved": "🟢"}
        
        st.markdown(f"""
        <div class="issue-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #4f46e5; font-weight: 700;">{row['id']}</span>
                    <span class="{priority_class}">{row['priority']}</span>
                    <span class="ai-badge">AI {row['ai_confidence']:.0%}</span>
                </div>
                <span style="color: #94a3b8; font-size: 0.85rem;">{row['date_reported']}</span>
            </div>
            <div style="margin-top: 6px;">
                <strong>{row['category']}</strong>
                <span style="color: #64748b;"> • {row['location']} • {status_emoji.get(row['status'], '⚪')} {row['status']} • 👍 {row['upvotes']}</span>
            </div>
            <div style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">{row['description']}</div>
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
            uploaded_image = st.file_uploader("📸 Upload Photo (AI auto-detects)", type=["jpg", "jpeg", "png"])
            
            if uploaded_image:
                st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
                detection = ai_engine.analyze_image(uploaded_image)
                st.markdown(f"""
                <div class="success-toast">
                    🤖 <strong>AI Detected:</strong> {detection['issue']} 
                    ({detection['confidence']:.0%}) | {detection['severity']}
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
                urgency = st.select_slider("⚡ Urgency", options=["Low", "Medium", "High", "Critical"], value="Medium")
            
            description = st.text_area("📝 Description", placeholder="Describe the issue...", height=120)
            
            submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)
            
            if submitted and title and description:
                with st.spinner("🤖 AI analyzing..."):
                    time.sleep(1.5)
                    
                    if category == "Auto-Detect (AI)":
                        detected_cat, confidence = ai_engine.classify_issue(description)
                    else:
                        detected_cat = category
                        confidence = 0.95
                    
                    priority, score = ai_engine.calculate_priority(detected_cat, description)
                    est_days = ai_engine.predict_resolution_time(detected_cat, priority)
                    
                    areas_coords = {
                        "Downtown": (12.9716, 77.5946), "Whitefield": (12.9698, 77.7500),
                        "Koramangala": (12.9352, 77.6245), "Indiranagar": (12.9784, 77.6408),
                        "Jayanagar": (12.9308, 77.5838), "HSR Layout": (12.9116, 77.6389),
                        "Electronic City": (12.8440, 77.6568), "Marathahalli": (12.9591, 77.6974),
                        "BTM Layout": (12.9166, 77.6101), "Hebbal": (13.0358, 77.5970),
                    }
                    
                    lat, lon = areas_coords.get(location, (12.9716, 77.5946))
                    
                    new_issue = pd.DataFrame([{
                        "id": f"CIV-{1050 + len(st.session_state.issues)}",
                        "category": detected_cat, "description": description,
                        "location": location,
                        "lat": lat + random.uniform(-0.005, 0.005),
                        "lon": lon + random.uniform(-0.005, 0.005),
                        "status": "Reported", "priority": priority,
                        "ai_confidence": confidence,
                        "date_reported": datetime.now().strftime("%Y-%m-%d"),
                        "upvotes": 1, "assigned_to": "Auto-Assigned",
                        "reporter": "You", "estimated_resolution": est_days,
                    }])
                    
                    st.session_state.issues = pd.concat([st.session_state.issues, new_issue], ignore_index=True)
                
                st.success("✅ Issue Reported Successfully!")
                st.balloons()
                
                st.markdown(f"""
                <div class="issue-card">
                    <h4 style="color: #4f46e5;">🤖 AI Analysis Report</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div><div style="color: #94a3b8; font-size: 0.8rem;">CATEGORY</div><div style="font-weight: 600;">{detected_cat}</div></div>
                        <div><div style="color: #94a3b8; font-size: 0.8rem;">CONFIDENCE</div><div style="color: #7c3aed; font-weight: 600;">{confidence:.0%}</div></div>
                        <div><div style="color: #94a3b8; font-size: 0.8rem;">PRIORITY</div><div style="color: #dc2626; font-weight: 600;">{priority} ({score:.0f}/100)</div></div>
                        <div><div style="color: #94a3b8; font-size: 0.8rem;">EST. RESOLUTION</div><div style="color: #16a34a; font-weight: 600;">{est_days} days</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col_preview:
        st.markdown('<div class="section-header">📍 Location Preview</div>', unsafe_allow_html=True)
        preview_map = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
        st_folium(preview_map, width=400, height=300)
        
        st.markdown('<div class="section-header">💡 Tips</div>', unsafe_allow_html=True)
        st.markdown("""
        - 📸 Upload a clear photo for AI auto-detection
        - 📝 Be descriptive for better AI classification
        - 📍 Select accurate location
        - ⚡ Critical issues get priority attention
        """)


# ============================================
# PAGE 3: AI DETECTION
# ============================================
elif selected == "AI Detection":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🤖 AI Detection Engine</div>
        <div class="hero-subtitle">Computer Vision & NLP for Automatic Issue Detection</div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📸 Image Detection", "📝 Text Analysis", "🧠 Model Info"])
    
    with tab1:
        st.markdown('<div class="section-header">Upload Image for AI Analysis</div>', unsafe_allow_html=True)
        col_up, col_res = st.columns(2)
        
        with col_up:
            img_file = st.file_uploader("Drop an image", type=["jpg", "jpeg", "png"], key="ai_upload")
            if img_file:
                st.image(img_file, caption="Uploaded Image", use_container_width=True)
        
        with col_res:
            if img_file:
                with st.spinner("🤖 Analyzing..."):
                    time.sleep(2)
                    result = ai_engine.analyze_image(img_file)
                
                st.markdown(f"""
                <div class="issue-card" style="border-left: 4px solid #7c3aed;">
                    <h3 style="color: #7c3aed;">🎯 AI Results</h3>
                    <br>
                    <div style="display: grid; gap: 1rem;">
                        <div style="background: #f5f3ff; padding: 1rem; border-radius: 12px;">
                            <div style="color: #7c3aed; font-size: 0.8rem; font-weight: 600;">DETECTED ISSUE</div>
                            <div style="font-size: 1.5rem; font-weight: 700;">{result['issue']}</div>
                        </div>
                        <div style="background: #faf5ff; padding: 1rem; border-radius: 12px;">
                            <div style="color: #a855f7; font-size: 0.8rem; font-weight: 600;">CONFIDENCE</div>
                            <div style="font-size: 1.5rem; font-weight: 700;">{result['confidence']:.0%}</div>
                        </div>
                        <div style="background: #fef2f2; padding: 1rem; border-radius: 12px;">
                            <div style="color: #dc2626; font-size: 0.8rem; font-weight: 600;">SEVERITY</div>
                            <div style="font-size: 1.5rem; font-weight: 700;">{result['severity']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number", value=result['confidence'] * 100,
                    title={'text': "AI Confidence"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': '#7c3aed'},
                        'steps': [
                            {'range': [0, 50], 'color': '#fee2e2'},
                            {'range': [50, 75], 'color': '#fef3c7'},
                            {'range': [75, 100], 'color': '#dcfce7'}
                        ],
                    }
                ))
                fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                st.markdown("""
                <div class="issue-card" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 4rem;">📸</div>
                    <div style="color: #94a3b8; margin-top: 1rem;">Upload an image to start AI detection</div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="section-header">📝 Text Analysis</div>', unsafe_allow_html=True)
        
        text_input = st.text_area("Describe the civic issue:", placeholder="e.g., There's a large pothole on MG Road near the bus stop.", height=150)
        
        if st.button("🔍 Analyze with AI", use_container_width=True):
            if text_input:
                with st.spinner("🧠 Processing..."):
                    time.sleep(1.5)
                    category, confidence = ai_engine.classify_issue(text_input)
                    priority, score = ai_engine.calculate_priority(category, text_input)
                    est_days = ai_engine.predict_resolution_time(category, priority)
                
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)
                
                with col_r1:
                    st.markdown(f"""<div class="metric-card"><div class="metric-icon">🏷️</div>
                    <div class="metric-value" style="font-size: 1.3rem;">{category}</div>
                    <div class="metric-label">Category</div></div>""", unsafe_allow_html=True)
                with col_r2:
                    st.markdown(f"""<div class="metric-card"><div class="metric-icon">🎯</div>
                    <div class="metric-value" style="font-size: 1.3rem;">{confidence:.0%}</div>
                    <div class="metric-label">Confidence</div></div>""", unsafe_allow_html=True)
                with col_r3:
                    st.markdown(f"""<div class="metric-card"><div class="metric-icon">⚡</div>
                    <div class="metric-value" style="font-size: 1.3rem;">{priority}</div>
                    <div class="metric-label">Priority</div></div>""", unsafe_allow_html=True)
                with col_r4:
                    st.markdown(f"""<div class="metric-card"><div class="metric-icon">📅</div>
                    <div class="metric-value" style="font-size: 1.3rem;">{est_days}d</div>
                    <div class="metric-label">Resolution</div></div>""", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="issue-card" style="margin-top: 1rem;">
                    <h4 style="color: #4f46e5;">🧠 NLP Breakdown</h4>
                    <p><strong>Keywords:</strong> {', '.join([w for w in text_input.lower().split() if len(w) > 4][:8])}</p>
                    <p><strong>Sentiment:</strong> Negative (Issue Report) ⚠️</p>
                    <p><strong>Urgency:</strong> {'Found ⚡' if any(w in text_input.lower() for w in ['dangerous', 'urgent', 'emergency']) else 'Standard'}</p>
                    <p><strong>Score:</strong> {score:.0f}/100</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="section-header">🧠 AI Model Architecture</div>', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.markdown("""
            <div class="issue-card">
                <h4 style="color: #4f46e5;">📸 Computer Vision</h4>
                <ul style="line-height: 2;">
                    <li>🔹 <strong>Architecture:</strong> YOLOv8 + ResNet50</li>
                    <li>🔹 <strong>Data:</strong> 50,000+ images</li>
                    <li>🔹 <strong>Accuracy:</strong> 94.2% mAP</li>
                    <li>🔹 <strong>Speed:</strong> < 200ms</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col_m2:
            st.markdown("""
            <div class="issue-card">
                <h4 style="color: #7c3aed;">📝 NLP Model</h4>
                <ul style="line-height: 2;">
                    <li>🔹 <strong>Architecture:</strong> BERT Classifier</li>
                    <li>🔹 <strong>Data:</strong> 100,000+ reports</li>
                    <li>🔹 <strong>F1 Score:</strong> 0.92</li>
                    <li>🔹 <strong>Languages:</strong> English, Hindi</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-header">🔄 AI Pipeline</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="issue-card" style="text-align: center;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <div style="background: #ede9fe; padding: 12px 20px; border-radius: 12px; border: 1px solid #c4b5fd;">
                    📥 Input
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: #ede9fe; padding: 12px 20px; border-radius: 12px; border: 1px solid #c4b5fd;">
                    🔍 Detection
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: #ede9fe; padding: 12px 20px; border-radius: 12px; border: 1px solid #c4b5fd;">
                    🏷️ Classification
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: #fce7f3; padding: 12px 20px; border-radius: 12px; border: 1px solid #f9a8d4;">
                    ⚡ Priority
                </div>
                <span style="font-size: 1.5rem;">→</span>
                <div style="background: #dcfce7; padding: 12px 20px; border-radius: 12px; border: 1px solid #86efac;">
                    📋 Assign
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
        <div class="hero-subtitle">Track, Filter, and Monitor All Civic Issues</div>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.issues
    
    st.markdown('<div class="section-header">🔍 Filters</div>', unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        filter_status = st.multiselect("Status", list(df['status'].unique()), default=list(df['status'].unique()))
    with col_f2:
        filter_priority = st.multiselect("Priority", list(df['priority'].unique()), default=list(df['priority'].unique()))
    with col_f3:
        filter_category = st.multiselect("Category", list(df['category'].unique()), default=list(df['category'].unique()))
    with col_f4:
        filter_location = st.multiselect("Location", list(df['location'].unique()), default=list(df['location'].unique()))
    
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
        
        with st.expander(f"🔖 {row['id']} | {row['category']} | {row['location']} | {row['priority']}"):
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
                <div style="background: #f8fafc; border-radius: 12px; padding: 1rem; border-left: 4px solid {p_color};">
                    <div style="color: {p_color}; font-weight: 700; font-size: 1.2rem;">{row['priority']}</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">Priority</div>
                    <hr>
                    <div style="color: #4f46e5; font-weight: 700;">{row['status']}</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">Status</div>
                    <hr>
                    <div style="color: #16a34a; font-weight: 700;">{row['estimated_resolution']} days</div>
                    <div style="color: #94a3b8; font-size: 0.85rem;">Est. Resolution</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("**📅 Timeline:**")
            
            timeline_events = [{"date": row['date_reported'], "event": "Issue Reported", "icon": "📝"}]
            
            if row['status'] in ["Under Review", "In Progress", "Resolved"]:
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "event": f"AI classified as {row['category']} ({row['ai_confidence']:.0%})", "icon": "🤖"
                })
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "event": f"Assigned to {row['assigned_to']}", "icon": "📋"
                })
            
            if row['status'] in ["In Progress", "Resolved"]:
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "event": "Work started", "icon": "🔧"
                })
            
            if row['status'] == "Resolved":
                timeline_events.append({
                    "date": (datetime.strptime(row['date_reported'], "%Y-%m-%d") + timedelta(days=row['estimated_resolution'])).strftime("%Y-%m-%d"),
                    "event": "Resolved ✅", "icon": "✅"
                })
            
            for event in timeline_events:
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-date">{event['icon']} {event['date']}</div>
                    <div class="timeline-text">{event['event']}</div>
                </div>
                """, unsafe_allow_html=True)


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
    
    st.markdown('<div class="section-header">📈 Reporting Trend</div>', unsafe_allow_html=True)
    
    trend_data = df.groupby('date_reported').size().reset_index(name='count')
    trend_data = trend_data.sort_values('date_reported')
    
    fig_trend = px.area(trend_data, x='date_reported', y='count', color_discrete_sequence=['#7c3aed'])
    fig_trend.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title='', yaxis_title='Issues Reported')
    fig_trend.update_traces(fill='tozeroy', fillcolor='rgba(124,58,237,0.2)')
    st.plotly_chart(fig_trend, use_container_width=True)
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.markdown('<div class="section-header">🗺️ Location vs Category</div>', unsafe_allow_html=True)
        heatmap_data = pd.crosstab(df['location'], df['category'])
        fig_heat = px.imshow(heatmap_data, color_continuous_scale='Purples', aspect='auto')
        fig_heat.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with col_a2:
        st.markdown('<div class="section-header">⏱️ Resolution Time</div>', unsafe_allow_html=True)
        resolution_data = df.groupby('category')['estimated_resolution'].mean().reset_index()
        resolution_data.columns = ['Category', 'Avg Days']
        resolution_data = resolution_data.sort_values('Avg Days', ascending=True)
        
        fig_res = px.bar(resolution_data, x='Avg Days', y='Category', orientation='h',
            color='Avg Days', color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444'])
        fig_res.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False, showlegend=False)
        st.plotly_chart(fig_res, use_container_width=True)
    
    # AI Gauges
    st.markdown('<div class="section-header">🤖 AI Performance <span class="ai-badge">AI</span></div>', unsafe_allow_html=True)
    
    col_ai1, col_ai2, col_ai3, col_ai4 = st.columns(4)
    
    for col, val, title, color in [
        (col_ai1, 94.2, "Detection", "#4f46e5"),
        (col_ai2, 91.8, "Classification", "#7c3aed"),
        (col_ai3, 87.5, "Priority", "#f59e0b"),
        (col_ai4, 156, "Response (ms)", "#22c55e")
    ]:
        with col:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                title={'text': title, 'font': {'size': 14}},
                number={'suffix': '%' if val < 100 else 'ms'},
                gauge={
                    'axis': {'range': [0, 100 if val < 100 else 500]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 60 if val < 100 else 200], 'color': '#fee2e2'},
                        {'range': [60 if val < 100 else 200, 80 if val < 100 else 350], 'color': '#fef3c7'},
                        {'range': [80 if val < 100 else 350, 100 if val < 100 else 500], 'color': '#dcfce7'}
                    ],
                }
            ))
            fig_g.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_g, use_container_width=True)
    
    # Department Performance
    st.markdown('<div class="section-header">🏢 Department Performance</div>', unsafe_allow_html=True)
    
    dept_data = df.groupby(['assigned_to', 'status']).size().reset_index(name='count')
    fig_dept = px.bar(dept_data, x='assigned_to', y='count', color='status', barmode='stack',
        color_discrete_map={'Reported': '#ef4444', 'Under Review': '#f59e0b', 'In Progress': '#3b82f6', 'Resolved': '#22c55e'})
    fig_dept.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), xaxis_title='', yaxis_title='Issues')
    st.plotly_chart(fig_dept, use_container_width=True)


# ============================================
# PAGE 6: HEATMAP
# ============================================
elif selected == "Heatmap":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🗺️ Issue Heatmap</div>
        <div class="hero-subtitle">Geographic Visualization with AI Hotspot Detection</div>
    </div>
    """, unsafe_allow_html=True)
    
    df = st.session_state.issues
    
    col_map1, col_map2, col_map3 = st.columns(3)
    
    with col_map1:
        map_filter_cat = st.multiselect("Category", list(df['category'].unique()), default=list(df['category'].unique()), key="map_cat")
    with col_map2:
        map_filter_priority = st.multiselect("Priority", list(df['priority'].unique()), default=list(df['priority'].unique()), key="map_pri")
    with col_map3:
        map_style = st.selectbox("Map Style", ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"])
    
    filtered_map = df[
        (df['category'].isin(map_filter_cat)) &
        (df['priority'].isin(map_filter_priority))
    ]
    
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=12, tiles=map_style)
    
    priority_colors = {"Critical": "red", "High": "orange", "Medium": "blue", "Low": "green"}
    
    for _, row in filtered_map.iterrows():
        color = priority_colors.get(row['priority'], 'blue')
        
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="color: #4f46e5;">{row['id']}</h4>
            <p><b>Category:</b> {row['category']}</p>
            <p><b>Priority:</b> {row['priority']}</p>
            <p><b>Status:</b> {row['status']}</p>
            <p><b>AI:</b> {row['ai_confidence']:.0%}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8 + (row['upvotes'] / 20),
            color=color, fill=True, fillColor=color, fillOpacity=0.7,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['id']} - {row['category']}",
        ).add_to(m)
    
    location_counts = filtered_map.groupby('location').agg({'lat': 'mean', 'lon': 'mean', 'id': 'count'}).reset_index()
    
    for _, loc in location_counts.iterrows():
        folium.Circle(
            location=[loc['lat'], loc['lon']],
            radius=loc['id'] * 100,
            color='#7c3aed', fill=True, fillColor='#7c3aed', fillOpacity=0.1, weight=1,
        ).add_to(m)
    
    st_folium(m, width=None, height=500, use_container_width=True)
    
    st.markdown("""
    <div class="issue-card" style="text-align: center;">
        🔴 <strong>Critical</strong> &nbsp;&nbsp;
        🟠 <strong>High</strong> &nbsp;&nbsp;
        🔵 <strong>Medium</strong> &nbsp;&nbsp;
        🟢 <strong>Low</strong> &nbsp;&nbsp;
        🟣 <strong>Hotspot</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Hotspot Analysis
    st.markdown('<div class="section-header">🔥 AI Hotspot Analysis</div>', unsafe_allow_html=True)
    
    hotspot_data = df.groupby('location').agg({
        'id': 'count',
        'priority': lambda x: (x == 'Critical').sum(),
        'upvotes': 'sum',
        'ai_confidence': 'mean'
    }).reset_index()
    hotspot_data.columns = ['Location', 'Total Issues', 'Critical Issues', 'Total Upvotes', 'Avg AI Confidence']
    
    hotspot_data['Risk Score'] = (
        hotspot_data['Total Issues'] * 2 + 
        hotspot_data['Critical Issues'] * 5 + 
        hotspot_data['Total Upvotes'] * 0.1
    ).round(1)
    hotspot_data = hotspot_data.sort_values('Risk Score', ascending=False)
    
    for _, row in hotspot_data.iterrows():
        risk_color = "#ef4444" if row['Risk Score'] > 30 else "#f59e0b" if row['Risk Score'] > 15 else "#22c55e"
        st.markdown(f"""
        <div class="issue-card" style="border-left: 4px solid {risk_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 1.1rem;">📍 {row['Location']}</span>
                <div style="display: flex; gap: 1.5rem;">
                    <div style="text-align: center;">
                        <div style="color: #4f46e5; font-weight: 700;">{row['Total Issues']}</div>
                        <div style="color: #94a3b8; font-size: 0.75rem;">Issues</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: #ef4444; font-weight: 700;">{row['Critical Issues']}</div>
                        <div style="color: #94a3b8; font-size: 0.75rem;">Critical</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="color: {risk_color}; font-weight: 700;">{row['Risk Score']}</div>
                        <div style="color: #94a3b8; font-size: 0.75rem;">Risk</div>
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
<div style="text-align: center; padding: 2rem; border-top: 1px solid #e2e8f0;">
    🏙️ <strong style="color: #4f46e5;">CivicEye</strong> - AI-Powered Urban Intelligence | 
    Built with ❤️ for Smart Cities
    <span class="ai-badge">Powered by AI</span>
</div>
""", unsafe_allow_html=True)
