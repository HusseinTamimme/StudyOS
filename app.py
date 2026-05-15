import streamlit as st
import PyPDF2
import io
import re
import random
import json
from datetime import date, timedelta
import time

# Page config
st.set_page_config(
    page_title="StudyOS - AI Study Assistant", 
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Coursera-style CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

.main { 
    padding: 2rem 3rem; 
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
}

.coursera-header {
    background: linear-gradient(135deg, #2c5aa0 0%, #1e3a8a 100%);
    color: white; padding: 1.5rem 2rem; border-radius: 0 0 20px 20px;
    box-shadow: 0 20px 40px rgba(44,90,160,0.3);
}
.hero-title { font-size: 2.5rem; font-weight: 700; margin: 0; }
.hero-subtitle { font-size: 1.2rem; opacity: 0.95; margin: 0.5rem 0 1rem 0; }

.metric-container {
    background: white; padding: 2rem; border-radius: 20px; 
    box-shadow: 0 20px 40px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}
.metric-container:hover { transform: translateY(-5px); box-shadow: 0 30px 60px rgba(0,0,0,0.12); }

.crash-badge { background: linear-gradient(135deg, #ef4444, #f59e0b); color: white; 
    padding: 0.8rem 1.5rem; border-radius: 50px; font-weight: 600; font-size: 0.9rem; }
.organized-badge { background: linear-gradient(135deg, #10b981, #059669); color: white; 
    padding: 0.8rem 1.5rem; border-radius: 50px; font-weight: 600; font-size: 0.9rem; }

.study-card { background: white; padding: 1.5rem; border-radius: 16px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.06); border-left: 4px solid #3b82f6; }

.sidebar-nav { background: #1e293b; padding: 2rem; border-radius: 0 20px 20px 0; min-height: 100vh; }
.sidebar-title { color: white; font-size: 1.5rem; font-weight: 700; margin-bottom: 2rem; }
.nav-button { 
    width: 100%; margin: 0.5rem 0; padding: 1rem; border-radius: 12px; border: none; 
    font-weight: 500; background: #374151; color: white; transition: all 0.3s ease;
}
.nav-button:hover { background: #3b82f6; transform: translateX(5px); }
.nav-button.selected { background: #3b82f6 !important; }

.stButton > button { border-radius: 12px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Hide Streamlit menu
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# SAMPLE CONTENT
SAMPLE_LECTURE = """
OPERATING SYSTEMS LECTURE - PROCESSES, SCHEDULING, DEADLOCKS

1. PROCESSES
Process = program in execution
Process Control Block (PCB): PID, state, program counter, registers, memory limits
States: new → ready → running → waiting → terminated
fork() creates child process

2. THREADS  
Lightweight process, shares memory with other threads
User threads vs Kernel threads (1:1 mapping)

3. CPU SCHEDULING
FCFS: convoy effect
SJF: optimal avg waiting time  
Priority: starvation risk
Round Robin: time quantum 10-100ms

4. DEADLOCKS (4 conditions)
Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait
Banker's Algorithm: safe state checking

5. MEMORY MANAGEMENT
Paging: logical → physical via page table
Page fault → demand paging → page replacement (FIFO/LRU)
Thrashing: working set > physical memory
"""

# Session State
@st.cache_data
def init_session_state():
    return {
        'page': 'home',
        'lecture_text': '',
        'lecture_title': '',
        'summary': '',
        'key_points': [],
        'definitions': [],
        'flashcards': [],
        'quiz_questions': [],
        'topics': [],
        'weak_topics': [],
        'exam_date': date.today() + timedelta(days=5),
        'days_left': 5,
        'quiz_score': 0,
        'readiness': 0,
        'chat_history': [],
        'pdf_processed': False
    }

if 'app_state' not in st.session_state:
    st.session_state.app_state = init_session_state()
    st.session_state.page = 'home'

state = st.session_state.app_state

# FUNCTIONS
def extract_pdf(file):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ""
        for page in reader.pages[:15]:
            text += page.extract_text() + "\n"
        return text.strip()
    except:
        return None

def process_lecture(text):
    state['summary'] = text[:800] + "..." if len(text) > 800 else text
    state['key_points'] = re.findall(r'^\s*[\d•-]\s*([A-Z][^\n]{10,100})', text, re.MULTILINE)[:10]
    state['topics'] = ['Processes', 'Threads', 'Scheduling', 'Deadlocks', 'Memory', 'Virtual Memory']
    state['weak_topics'] = random.sample(state['topics'], 2)
    state['flashcards'] = [
        {"front": "What is PCB?", "back": "Process Control Block - stores process state"},
        {"front": "Deadlock conditions?", "back": "4: Mutual Exclusion, Hold&Wait, No Preemption, Circular Wait"}
    ]
    state['quiz_questions'] = [
        {"q": "PCB stands for?", "options": ["Process Control Block", "Program CPU Buffer", "Process Cache Block"], "ans": 0},
        {"q": "Deadlock needs?", "options": ["2 conditions", "3 conditions", "4 conditions"], "ans": 2}
    ]
    state['pdf_processed'] = True

def calculate_readiness():
    return min(95, 30 + (state['quiz_score'] * 10) + random.randint(0, 30))

# COURsera-STYLE SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown('<div class="sidebar-title">📚 StudyOS</div>', unsafe_allow_html=True)
    st.markdown('<div style="color: #94a3b8; font-size: 0.9rem;">Exam panic → clear plan</div>', unsafe_allow_html=True)
    
    pages = {
        "🏠 Home": "home",
        "📤 Upload Lecture": "upload", 
        "📊 Dashboard": "dashboard",
        "🚀 Crash Mode": "crash",
        "📖 Study": "study",
        "❓ Quiz": "quiz",
        "💬 AI Chat": "chat"
    }
    
    for page_name, page_key in pages.items():
        if st.button(page_name, key=page_key, help=f"Go to {page_name}"):
            state['page'] = page_key
            st.rerun()
    
    st.markdown("---")
    if state['pdf_processed']:
        st.metric("Readiness", f"{calculate_readiness():.0f}%")
        st.metric("Days Left", state['days_left'])
    st.markdown("---")
    if st.button("🎓 Load Sample", key="sample"):
        state['lecture_text'] = SAMPLE_LECTURE
        state['lecture_title'] = "OS Fundamentals"
        process_lecture(SAMPLE_LECTURE)
        st.success("✅ Sample loaded!")
        st.rerun()

# HEADER
st.markdown("""
<div class="coursera-header">
    <div class="hero-title">StudyOS</div>
    <div class="hero-subtitle">AI Study Assistant • 500K+ students</div>
</div>
""", unsafe_allow_html=True)

# PAGE ROUTING
if state['page'] == 'home':
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h1 style="font-size: 3rem; background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;"> 
            Welcome to StudyOS
        </h1>
        <p style="font-size: 1.4rem; color: #475569; max-width: 600px; margin: 2rem auto;">
            Upload your lecture → Enter exam date → Get flashcards, quizzes, 
            and personalized study plan instantly
        </p>
        
        <div style="background: white; padding: 2rem; border-radius: 20px; 
                   box-shadow: 0 20px 40px rgba(0,0,0,0.1); display: inline-block;">
            <h3 style="color: #1e293b;">Ready to start?</h3>
            <p>Go to <strong>📤 Upload Lecture</strong> in sidebar</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif state['page'] == 'upload':
    st.markdown('<h2 style="color: #1e293b;">📤 Upload & Process Lecture</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3,1])
    with col1:
        uploaded = st.file_uploader("📄 Choose PDF", type="pdf")
    with col2:
        exam_date = st.date_input("📅 Exam Date", value=date.today()+timedelta(days=5))
        state['exam_date'] = exam_date
        state['days_left'] = max(0, (exam_date-date.today()).days)
    
    if uploaded and not state['pdf_processed']:
        if st.button("🎯 PROCESS LECTURE (30s)", type="primary"):
            with st.spinner("Analyzing..."):
                text = extract_pdf(uploaded)
                if text:
                    state['lecture_text'] = text
                    state['lecture_title'] = uploaded.name[:-4]
                else:
                    state['lecture_text'] = SAMPLE_LECTURE
                    st.warning("Using sample")
                process_lecture(state['lecture_text'])
                st.success("✅ COMPLETE!")
                st.balloons()
    
    if state['pdf_processed']:
        st.success(f"✅ **{state['lecture_title']}** processed!")
        col1, col2, col3 = st.columns(3)
        col1.metric("Topics", len(state['topics']))
        col2.metric("Flashcards", len(state['flashcards']))
        col3.metric("Quiz Qs", len(state['quiz_questions']))

elif state['page'] == 'dashboard':
    st.markdown('<h2 style="color: #1e293b;">📊 Study Dashboard</h2>', unsafe_allow_html=True)
    
    if not state['pdf_processed']:
        st.warning("Upload lecture first!")
    else:
        # METRICS ROW
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 2.5rem; color: #ef4444;">{state['days_left']}</div>
                <div style="color: #64748b; font-weight: 500;">Days Left</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            readiness = calculate_readiness()
            state['readiness'] = readiness
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 2.5rem; color: #10b981;">{readiness:.0f}%</div>
                <div style="color: #64748b;">Readiness</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div style="font-size: 2.5rem; color: #f59e0b;">{len(state['weak_topics'])}</div>
                <div style="color: #64748b;">Weak Topics</div>
            </div>
            """, unsafe_allow_html=True)
        
        # MODE
        if state['days_left'] <= 3:
            st.markdown('<div class="crash-badge">🚨 CRASH MODE - Exam imminent!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="organized-badge">✅ Organized Mode</div>', unsafe_allow_html=True)
        
        # ACTION CARDS
        st.markdown("### 🎯 Next Actions")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="study-card"><strong>📚 Review:</strong> {state["weak_topics"][0]}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="study-card"><strong>⏱️ Today:</strong> 25min + 5min break</div>', unsafe_allow_html=True)

elif state['page'] == 'study':
    st.markdown('<h2 style="color: #1e293b;">📖 Study Materials</h2>', unsafe_allow_html=True)
    if state['pdf_processed']:
        tab1, tab2, tab3 = st.tabs(["Summary", "Key Points", "Flashcards"])
        
        with tab1: st.markdown(state['summary'])
        with tab2:
            for point in state['key_points']:
                st.markdown(f"• **{point}**")
        
        with tab3:
            for card in state['flashcards']:
                with st.expander(card['front']):
                    st.success(card['back'])

elif state['page'] == 'crash':
    st.markdown('<h2 style="color: #1e293b;">🚀 Crash Mode</h2>', unsafe_allow_html=True)
    st.markdown('<div class="crash-badge">ACTIVE - Focus on high-yield topics!</div>', unsafe_allow_html=True)
    st.markdown("""
    ### 🔥 TOP 3 Exam Topics
    1. **Deadlocks** - 4 conditions + Banker's
    2. **Scheduling** - FCFS vs Round Robin  
    3. **Page Replacement** - FIFO/LRU
    
    ### ⚡ 90-Minute Plan
    - 25m Deadlocks
    - 5m Break
    - 25m Scheduling  
    - 10m Quiz
    """)

elif state['page'] == 'quiz':
    st.markdown('<h2 style="color: #1e293b;">❓ Practice Quiz</h2>', unsafe_allow_html=True)
    
    if st.button("🔄 New Quiz"):
        state['quiz_score'] = 0
    
    if state['quiz_score'] == 0:
        answers = []
        for i, q in enumerate(state['quiz_questions']):
            st.markdown(f"**Q{i+1}:** {q['q']}")
            ans = st.radio("", q['options'], key=f"q{i}")
            answers.append(q['options'].index(ans))
        
        if st.button("Submit"):
            correct = sum(a == q['ans'] for a, q in zip(answers, state['quiz_questions']))
            state['quiz_score'] = correct
            st.success(f"{correct}/{len(state['quiz_questions'])}")
    else:
        st.success(f"Score: {state['quiz_score']}/{len(state['quiz_questions'])}")
        if st.button("New Quiz"): state['quiz_score'] = 0

elif state['page'] == 'chat':
    st.markdown('<h2 style="color: #1e293b;">💬 AI Tutor</h2>', unsafe_allow_html=True)
    
    for msg in state['chat_history']:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about your lecture..."):
        state['chat_history'].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = "Processes are programs in execution with PCB. Deadlocks need 4 conditions..."
            st.markdown(response)
        
        state['chat_history'].append({"role": "assistant", "content": response})
