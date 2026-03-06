"""
chat_app.py
-----------
Frontend Chat Interface designed to match the provided dashboard aesthetic.
Built with Streamlit and custom CSS/HTML injection.
"""

import streamlit as st
import requests
import os

API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000/query")

# Set Page Config
st.set_page_config(
    page_title="Stratify AI Workspace",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# Custom Aesthetics Injection (Global CSS)
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Backgrounds */
.stApp {
    background-color: #f6f8fb;
}
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #edf2f7;
}
[data-testid="stHeader"] {
    display: none;
}
[data-testid="block-container"] {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1100px;
}

/* Typography */
.greeting-title {
    font-size: 2.8rem;
    font-weight: 500;
    color: #4299e1;
    letter-spacing: -0.5px;
    margin-bottom: 0px;
}
.greeting-subtitle {
    font-size: 2.4rem;
    font-weight: 500;
    color: #718096;
    margin-top: -5px;
    margin-bottom: 2.5rem;
    letter-spacing: -0.5px;
}

/* Sidebar Custom CSS */
.sidebar-profile {
    display: flex;
    align-items: center;
    padding: 1rem 0 2rem 1rem;
}
.sidebar-profile img {
    border-radius: 50%;
    width: 36px;
    height: 36px;
    margin-right: 12px;
}
.sidebar-item {
    display: flex;
    align-items: center;
    color: #4a5568;
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 500;
    padding: 8px 16px;
    margin-bottom: 4px;
    border-radius: 12px;
    transition: 0.2s;
    cursor: pointer;
}
.sidebar-item i {
    width: 24px;
    color: #a0aec0;
}
.sidebar-item:hover, .sidebar-item.active {
    background-color: #f7fafc;
    color: #1a202c;
    font-weight: 600;
}
.sidebar-section {
    font-size: 0.75rem;
    color: #a0aec0;
    font-weight: 500;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    padding-left: 16px;
}
.upgrade-box {
    margin: 2rem 16px 1rem 16px;
    padding: 1rem;
    background-color: #f7fafc;
    border: 1px solid #edf2f7;
    border-radius: 12px;
}
.upgrade-btn {
    background: #4299e1;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 12px;
    cursor: pointer;
    width: 100%;
}

/* Dashboard Cards */
.dash-card {
    background-color: white;
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid white;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02), 0 2px 4px -1px rgba(0,0,0,0.01);
    height: 100%;
    cursor: pointer;
    transition: 0.2s;
}
.dash-card:hover {
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
    border-color: #f7fafc;
}
.card-title {
    font-size: 0.8rem;
    color: #a0aec0;
    font-weight: 500;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.file-item {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    font-size: 0.9rem;
    color: #2d3748;
    font-weight: 600;
}
.task-badge {
    padding: 4px 10px;
    border-radius: 16px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 8px;
}

/* My Tasks table */
.tasks-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    margin-bottom: 1rem;
}
.task-row {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px dashed #edf2f7;
    font-size: 0.9rem;
    color: #2d3748;
}
.main-search-input {
    border: 1px solid #e2e8f0;
    border-radius: 30px;
    padding: 10px 20px;
    font-size: 0.9rem;
    color: #a0aec0;
    background: white;
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: text;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Left Sidebar Setup
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-profile">
        <img src="https://i.pravatar.cc/150?img=11" alt="Sam">
        <span style="font-weight: 600; font-size: 0.95rem; color: #2d3748;">Sam Smith</span>
    </div>
    
    <div class="sidebar-item active" style="background-color: #f7fafc; color: #2d3748; font-weight: 600;">
        <i class="fa-solid fa-house"></i> Home
    </div>
    <div class="sidebar-item"><i class="fa-regular fa-comment"></i> New Chat</div>
    <div class="sidebar-item"><i class="fa-solid fa-list-check"></i> My Tasks</div>
    <div class="sidebar-item"><i class="fa-solid fa-video"></i> My Meetings</div>
    <div class="sidebar-item"><i class="fa-regular fa-bookmark"></i> Saved Files</div>
    <div class="sidebar-item"><i class="fa-solid fa-share-nodes"></i> Shared with me</div>
    
    <div class="sidebar-section">Today</div>
    <div class="sidebar-item" style="font-size: 0.85rem; font-weight: 500;">Research Assistance Request</div>
    <div class="sidebar-item" style="font-size: 0.85rem; font-weight: 500;">Summarizing Last Meeting</div>
    <div class="sidebar-item" style="font-size: 0.85rem; font-weight: 500;">Prioritizing Tasks Request</div>
    
    <div class="sidebar-section">Yesterday</div>
    <div class="sidebar-item" style="font-size: 0.85rem; font-weight: 500;">Document Summary Request</div>
    
    <div class="upgrade-box">
        <div style="display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-circle-notch" style="color:#a0aec0;"></i>
            <span style="font-size:0.8rem; font-weight:600; color:#2d3748;">Only 5 AI reports left</span>
        </div>
        <div style="font-size:0.75rem; color:#718096; margin-top:4px;">Get deeper insights with Pro</div>
        <button class="upgrade-btn">Upgrade Now</button>
    </div>
    
    <div class="sidebar-item" style="margin-top: 1rem;"><i class="fa-solid fa-gear"></i> Settings</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session State & Logic
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Dynamic Views: Dashboard OR Chat History
# ---------------------------------------------------------------------------
if len(st.session_state.messages) == 0:
    # --- DASHBOARD VIEW ---
    st.markdown("""
        <div>
            <div class="greeting-title" style="background: linear-gradient(90deg, #4299e1 0%, #4fd1c5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block;">Welcome, Sam! <span style="font-size: 2.2rem; -webkit-text-fill-color: initial;">👋</span></div>
            <div class="greeting-subtitle">How can I help you today?</div>
        </div>
    """, unsafe_allow_html=True)

    # Top Grid
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="dash-card">
            <div class="card-title"><i class="fa-regular fa-clock"></i> Previously viewed files</div>
            <div class="file-item">
                <div style="background:#fce000; width:22px; height:22px; border-radius:4px; display:flex; align-items:center; justify-content:center; margin-right:12px; font-weight:bold; font-size:10px;">M</div>
                Miro - Product Analytics and Statistics
            </div>
            <div class="file-item">
                <div style="background:#f24e1e; width:22px; height:22px; border-radius:4px; display:flex; align-items:center; justify-content:center; color:white; margin-right:12px; font-weight:bold; font-size:10px;">F</div>
                Figma - UX Research
            </div>
            <div class="file-item" style="margin-bottom:0;">
                <div style="background:#f56565; width:22px; height:22px; border-radius:4px; display:flex; align-items:center; justify-content:center; color:white; margin-right:12px; font-weight:bold; font-size:8px;">PDF</div>
                Q2 Strategic Goals & Objectives.pdf
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="dash-card">
            <div class="card-title"><i class="fa-solid fa-wand-magic-sparkles"></i> Summarize your last meeting</div>
            <div style="display:flex; align-items:center; margin-top:20px;">
                <img src="https://i.pravatar.cc/150?img=5" style="width:44px; height:44px; border-radius:50%; margin-right:16px;">
                <div>
                    <div style="font-weight:600; color:#2d3748; display:flex; align-items:center; gap:8px;">
                        <span style="background:#48bb78; border-radius:4px; padding: 2px 6px; display:inline-flex; align-items:center; justify-content:center; color:white; font-size:10px;"><i class="fa-solid fa-video"></i></span>
                        UX Strategy Meet up
                    </div>
                    <div style="font-size:0.75rem; color:#a0aec0; margin-top:4px;">1 Apr, 2025, 14:00 pm</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bottom Grid
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div class="dash-card" style="padding: 1.2rem 1.5rem;">
            <div class="card-title" style="margin-bottom:0.5rem;"><i class="fa-regular fa-lightbulb"></i> Suggested Task</div>
            <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">Conduct UX Research</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="dash-card" style="padding: 1.2rem 1.5rem;">
            <div class="card-title" style="margin-bottom:0.5rem;"><i class="fa-regular fa-lightbulb"></i> Suggested Task</div>
            <div style="font-weight:600; color:#2d3748; font-size:1.1rem;">Write a prospect email</div>
        </div>
        """, unsafe_allow_html=True)

    # My Tasks section
    st.markdown("""
    <div class="tasks-header">
        <div style="display:flex; align-items:center; gap:10px;">
            <i class="fa-regular fa-folder" style="color:#2d3748; font-size:1.2rem;"></i>
            <span style="font-weight: 600; font-size: 1.2rem; color:#2d3748;">My Tasks</span>
            <span style="font-size: 0.85rem; color: #a0aec0; font-weight:600; background:#edf2f7; padding:2px 8px; border-radius:12px;">1/3</span>
            <span style="color:#a0aec0; font-size:0.9rem; margin-left:16px;"><i class="fa-solid fa-magnifying-glass"></i> Search file name...</span>
        </div>
        <button style="border:1px solid #d6bcfa; background:white; padding:8px 16px; border-radius:20px; color:#805ad5; font-size:0.9rem; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:8px;">
            <i class="fa-solid fa-wand-magic-sparkles"></i> Prioritize Tasks
        </button>
    </div>
    
    <div style="background:white; border-radius:16px; padding:0.5rem 1.5rem; border:1px solid white; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);">
        <div class="task-row">
            <span style="color:#e53e3e; margin-right:12px; font-size:12px;"><i class="fa-solid fa-square"></i></span>
            <span style="flex-grow:1; font-weight:600;">Design Meeting</span>
            <span style="color:#718096; font-size:0.85rem; margin-right:16px;">2 pm</span>
            <span class="task-badge" style="background:#ebf4ff; color:#3182ce;"><i class="fa-solid fa-video" style="margin-right:4px;"></i> Join now</span>
        </div>
        <div class="task-row">
            <span style="color:#3182ce; margin-right:12px; font-size:12px;"><i class="fa-solid fa-square"></i></span>
            <span style="flex-grow:1; font-weight:600;">Refine UI components based on user feedback</span>
            <span class="task-badge" style="background:#fff5f5; color:#e53e3e;">Urgent</span>
            <span class="task-badge" style="background:#fff5f5; color:#e53e3e; border:1px solid #fed7d7;">By today</span>
        </div>
        <div class="task-row">
            <span style="color:#3182ce; margin-right:12px; font-size:12px;"><i class="fa-solid fa-square"></i></span>
            <span style="flex-grow:1; font-weight:600;">Prepare a prototype for usability testing</span>
            <span class="task-badge" style="background:#ebf8ff; color:#3182ce;"><i class="fa-regular fa-clock" style="margin-right:4px;"></i> In progress</span>
            <span class="task-badge" style="background:#e6fffa; color:#319795;"><i class="fa-regular fa-calendar" style="margin-right:4px;"></i> By tomorrow</span>
        </div>
        <div class="task-row" style="border-bottom:none;">
            <span style="color:#3182ce; margin-right:12px; font-size:12px;"><i class="fa-solid fa-square"></i></span>
            <span style="flex-grow:1; font-weight:600;">Collaborate with developers on implementation detail</span>
            <span class="task-badge" style="background:#f7fafc; color:#718096;"><i class="fa-regular fa-circle" style="margin-right:4px;"></i> To do</span>
            <span class="task-badge" style="background:#e6fffa; color:#319795;"><i class="fa-regular fa-calendar" style="margin-right:4px;"></i> By tomorrow</span>
        </div>
    </div>
    <br><br><br>
    """, unsafe_allow_html=True)
else:
    # --- CHAT HISTORY VIEW ---
    st.markdown("""
        <div><h2 style="color: #2d3748; font-weight: 500; letter-spacing: -0.5px;">Workspace Chat</h2></div>
        <hr style="opacity: 0.2;">
    """, unsafe_allow_html=True)
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Sticky Bottom Input & Backend Integration
# ---------------------------------------------------------------------------
# Use custom markdown to force a style on the st.chat_input container 
st.markdown("""
<style>
/* Style the bottom padding and input container to float like the image */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    min-width: 400px;
    background: white !important;
    border-radius: 30px !important;
    border: 1px solid white !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05), 0 4px 6px rgba(0,0,0,0.02) !important;
    padding: 0 !important;
}
[data-testid="stChatInput"] textarea {
    font-size: 1rem !important;
}
</style>
""", unsafe_allow_html=True)

query = st.chat_input(" ✨ Ask or search for anything. Use @ to tag a file or collection.")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    st.rerun()

# RAG Integration trigger
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    user_msg_content = st.session_state.messages[-1]["content"]
    
    with st.chat_message("assistant"):
        with st.spinner("Processing request..."):
            try:
                response = requests.post(API_URL, json={"query": user_msg_content}, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    answer_text = data.get("answer", "")
                    st.markdown(answer_text)
                    st.session_state.messages.append({"role": "assistant", "content": answer_text})
                else:
                    error_msg = f"⚠️ Backend error: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except requests.exceptions.ConnectionError:
                error_msg = "⚠️ Could not connect to the backend service. Is the FastAPI server running on port 8000?"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                
    st.rerun()
