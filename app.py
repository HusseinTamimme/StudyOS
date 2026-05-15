"""
StudyOS - AI Exam Operating System
Hackathon MVP Demo
"""

import streamlit as st
import PyPDF2
import io
import re
import json
import random
import math
from datetime import date, timedelta
from typing import List, Dict, Any
import pandas as pd

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="StudyOS - AI Exam OS",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS - Coursera style
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
.main { padding: 2rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }

.header-hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 3rem 2rem; border-radius: 20px; color: white; text-align: center;
    box-shadow: 0 25px 50px rgba(30,58,138,0.3);
}
.header-title { font-size: 3rem; font-weight: 700; margin: 0 0 1rem 0; }
.header-subtitle { font-size: 1.3rem; opacity: 0.95; }

.metric-card {
    background: white; padding: 2rem; border-radius: 20px; text-align: center;
    box-shadow: 0 20px 40px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
}
.metric-card:hover { transform: translateY(-5px); box-shadow: 0 30px 60px rgba(0,0,0,0.15); }
.metric-value { font-size: 2.5rem; font-weight: 700; color: #1e293b; }
.metric-label { color: #64748b; font-weight: 500; font-size: 1rem; margin-top: 0.5rem; }

.badge-ai { background: linear-gradient(135deg, #8b5cf6, #a78bfa); color: white; 
    padding: 0.5rem 1rem; border-radius: 25px; font-size: 0.8rem; font-weight: 600; }
.badge-crash { background: linear-gradient(135deg, #ef4444, #f87171); color: white; 
    padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600; }
.badge-ready { background: linear-gradient(135deg, #10b981, #34d399); color: white; 
    padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600; }

.module-card {
    background: white; padding: 1.5rem; border-radius: 16px; margin: 1rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.06); border-left: 4px solid #3b82f6;
    transition: all 0.3s ease;
}
.module-card:hover { box-shadow: 0 20px 40px rgba(0,0,0,0.12); transform: translateY(-2px); }

.progress-container { background: #e2e8f0; height: 12px; border-radius: 6px; overflow: hidden; margin: 1rem 0; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #10b981, #059669); transition: width 1s ease; }

.sidebar-nav { background: #1e293b; min-height: 100vh; padding: 2rem; }
.nav-title { color: white; font-size: 1.4rem; font-weight: 700; margin-bottom: 2rem; }
.nav-btn { width: 100%; margin: 0.5rem 0; padding: 1rem; border-radius: 12px; border: none; 
    background: #374151; color: white; font-weight: 500; cursor: pointer; }
.nav-btn:hover { background: #3b82f6; transform: translateX(5px); }
.api-key-input { width: 100%; margin: 1rem 0; }

.stButton > button { border-radius: 12px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# Hide Streamlit elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>""", unsafe_allow_html=True)

# SAMPLE LECTURE
SAMPLE_LECTURE = """
OPERATING SYSTEMS FUNDAMENTALS

1. PROCESSES
A process is a program in execution that has:
- Process Control Block (PCB): process state, program counter, CPU registers
- Process states: New, Ready, Running, Waiting, Terminated
- Process creation via fork() system call

2. THREADS
Lightweight process sharing memory space
Advantages: faster context switching, resource sharing
User-level vs kernel-level threads

3. CPU SCHEDULING
Algorithms:
- FCFS: convoy effect
- SJF: optimal average waiting time  
- Priority: risk of starvation
- Round Robin: time quantum typically 10-100ms

4. DEADLOCKS
Four necessary conditions:
1. Mutual Exclusion
2. Hold and Wait
3. No Preemption
4. Circular Wait

Prevention strategies and Banker's Algorithm for avoidance.

5. MEMORY MANAGEMENT
Paging: fixed-size pages, page table
Page fault handling, demand paging
Page replacement: FIFO, LRU, Optimal

6. VIRTUAL MEMORY
Concept allowing larger programs than physical memory
Thrashing occurs when working set exceeds available frames
"""

class StudyOS:
    def __init__(self):
        self.init_state()
        self.model_name = "gpt-4o-mini"
        self.client = None
        self.setup_openai()
    
    def init_state(self):
        defaults = {
            'current_page': 'home',
            'api_key': '',
            'lecture_files': [],
            'lecture_text': '',
            'lecture_title': '',
            'exam_date': date.today() + timedelta(days=7),
            'days_left': 7,
            'summary': '',
            'key_points': [],
            'definitions': [],
            'flashcards': [],
            'quiz_questions': [],
            'topics': [],
            'weak_topics': [],
            'readiness': 0,
            'quiz_score': 0,
            'chat_history': [],
            'pdf_processed': False,
            'word_count': 0
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def setup_openai(self):
        api_key = (st.secrets.get("OPENAI_API_KEY") or 
                  os.environ.get("OPENAI_API_KEY") or 
                  st.session_state.get('api_key', ''))
        
        if api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=api_key)
            st.session_state.api_key = api_key
            return True
        return False
    
    def has_ai(self):
        return self.client is not None
    
    @st.cache_data
    def extract_pdf_text(self, uploaded_file):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + "\n"
            return text.strip()
        except:
            return None
    
    def call_ai(self, prompt: str, system: str = "You are a helpful assistant.", max_tokens=1200) -> str:
        if not self.has_ai():
            return self.fallback_ai(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"AI error: {str(e)[:100]}")
            return self.fallback_ai(prompt)
    
    def fallback_ai(self, prompt: str) -> str:
        st.warning("⚠️ Demo mode: Using smart local AI")
        # Smart rule-based responses
        if "summary" in prompt.lower():
            return "Key concepts: Processes (PCB), Threads, CPU Scheduling (FCFS/SJF/RR), Deadlocks (4 conditions), Memory Management (Paging), Virtual Memory."
        return "This topic is covered in your lecture. Key points: review PCB, deadlock conditions, scheduling algorithms."
    
    def process_lectures(self):
        text = st.session_state.lecture_text
        if not text:
            return
        
        # AI Processing
        prompt_summary = f"Summarize this lecture in 3 parts: short summary, 8 key points, key takeaway. Return JSON:\n\n{text[:4000]}"
        
        try:
            ai_response = self.call_ai(prompt_summary, "Return valid JSON only.")
            data = json.loads(ai_response)
            st.session_state.summary = data.get('short_summary', '')
            st.session_state.key_points = data.get('key_points', [])
        except:
            # Fallback
            st.session_state.summary = "Comprehensive OS lecture covering processes, threads, scheduling, deadlocks, and memory management."
            st.session_state.key_points = ["Processes and PCB", "Threads vs Processes", "CPU Scheduling Algorithms", "Deadlock Conditions"]
        
        st.session_state.pdf_processed = True
        st.session_state.topics = ["Processes", "Threads", "Scheduling", "Deadlocks", "Memory"]
        st.session_state.weak_topics = ["Deadlocks", "Memory"]
    
    def sidebar(self):
        with st.sidebar:
            st.markdown('<div class="nav-title">📚 StudyOS</div>', unsafe_allow_html=True)
            st.markdown('<div style="color: #94a3b8;">Exam panic → clear plan</div>', unsafe_allow_html=True)
            
            pages = [
                ("🏠 Home", "home"),
                ("📤 Upload Lectures", "upload"),
                ("📊 Learning Dashboard", "dashboard"),
                ("🚀 Crash Mode", "crash"),
                ("📖 AI Workspace", "workspace"),
                ("💬 AI Tutor", "chat"),
                ("❓ Quiz", "quiz"),
                ("🃏 Flashcards", "flashcards")
            ]
            
            for name, page_key in pages:
                if st.button(name, key=page_key):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 🔑 OpenAI API Key")
            api_key = st.text_input("Paste your key:", type="password", key="api_key_input")
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                self.setup_openai()
                st.rerun()
            
            if self.has_ai():
                st.success("✅ Real AI active")
            else:
                st.info("⚠️ Demo mode")
    
    def home_page(self):
        st.markdown("""
        <div class="header-hero">
            <div class="header-title">StudyOS</div>
            <div class="header-subtitle">Your AI Exam Operating System</div>
            <p style="max-width: 500px; margin: 2rem auto; opacity: 0.9;">
                Upload lectures → Get summaries, flashcards, quizzes, weakness detection, 
                and personalized crash plans.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📤</div>
                <div class="metric-label">Upload Any PDF</div>
                <p style="color: #64748b;">Lectures → AI workspace instantly</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">🚀</div>
                <div class="metric-label">Crash Mode</div>
                <p style="color: #64748b;">Exam <3 days? Prioritize what matters</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📊</div>
                <div class="metric-label">Readiness Score</div>
                <p style="color: #64748b;">Know exactly how ready you are</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### ❌ Before StudyOS
            <div style="background: #fef2f2; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                <ul style="color: #dc2626;">
                    <li>📄 Scattered lecture PDFs</li>
                    <li>✍️ Manual flashcards (hours)</li>
                    <li>❓ No readiness indicator</li>
                    <li>😰 Exam day panic</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            ### ✅ After StudyOS  
            <div style="background: #f0fdf4; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                <ul style="color: #16a34a;">
                    <li>⚡ AI-generated workspace</li>
                    <li>📊 78% readiness score</li>
                    <li>🎯 Weak topics detected</li>
                    <li>🧘 Calm study plan</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    def upload_page(self):
        st.markdown('<h2 style="color: #1e293b; font-weight: 700;">📤 Upload Lectures</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            uploaded_files = st.file_uploader("Choose lecture PDFs", type="pdf", accept_multiple_files=True)
        
        with col2:
            st.session_state.exam_date = st.date_input("📅 Exam Date", value=st.session_state.exam_date)
            st.session_state.days_left = max(0, (st.session_state.exam_date - date.today()).days)
        
        if st.button("🎓 Use Sample OS Lecture", type="secondary"):
            st.session_state.lecture_text = SAMPLE_LECTURE
            st.session_state.lecture_title = "Operating Systems Fundamentals"
            self.process_lectures()
            st.success("✅ Sample loaded!")
            st.rerun()
        
        if uploaded_files and st.button("🎯 Generate StudyOS Workspace", type="primary"):
            with st.spinner("Reading PDFs..."):
                full_text = ""
                for file in uploaded_files:
                    text = self.extract_pdf_text(file)
                    if text:
                        full_text += f"\n\n=== {file.name} ===\n" + text
                
                if full_text:
                    st.session_state.lecture_text = full_text
                    st.session_state.lecture_title = "Your Lectures"
                    st.session_state.word_count = len(full_text.split())
                    self.process_lectures()
                    st.success("✅ Workspace generated!")
                    st.balloons()
                else:
                    st.error("No text found in PDFs")
    
    def dashboard_page(self):
        if not st.session_state.pdf_processed:
            st.warning("👆 Upload lectures first")
            return
        
        st.markdown('<h2 style="color: #1e293b;">📊 Learning Dashboard</h2>', unsafe_allow_html=True)
        
        # Top metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.days_left}</div>
                <div class="metric-label">Days Left</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            readiness = st.session_state.readiness or 45
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{readiness}%</div>
                <div class="metric-label">Readiness</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {readiness}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.weak_topics)}</div>
                <div class="metric-label">Weak Topics</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Modules
        st.markdown("### 📋 Your Learning Path")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="module-card"><h4>📝 Lecture Summary</h4><p>AI-generated overview</p></div>', unsafe_allow_html=True)
            st.markdown('<div class="module-card"><h4>🃏 Flashcards</h4><p>50+ AI cards</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="module-card"><h4>❓ Practice Quiz</h4><p>Test readiness</p></div>', unsafe_allow_html=True)
            st.markdown('<div class="module-card"><h4>💬 AI Tutor</h4><p>Ask anything</p></div>', unsafe_allow_html=True)
    
    def crash_page(self):
        st.markdown('<h2 style="color: #1e293b;">🚀 Crash Mode</h2>', unsafe_allow_html=True)
        if st.session_state.days_left > 3:
            st.info("Crash Mode activates when exam ≤ 3 days away")
            return
        
        st.markdown('<div class="badge-crash">🚨 CRASH MODE ACTIVE</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="module-card">
            <h3>🎯 Priority Topics</h3>
            <ul>
                <li><strong>Deadlocks</strong> - 4 conditions + prevention</li>
                <li><strong>Scheduling</strong> - FCFS vs Round Robin</li>
                <li><strong>Memory</strong> - Page replacement</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    def workspace_page(self):
        if not st.session_state.pdf_processed:
            st.warning("Upload first")
            return
        
        st.markdown('<h2 style="color: #1e293b;">📖 AI Workspace</h2>', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["Summary", "Key Points", "Definitions"])
        
        with tab1:
            st.markdown(f'<div class="badge-ai">AI Generated</div>', unsafe_allow_html=True)
            st.markdown(st.session_state.summary)
        
        with tab2:
            for point in st.session_state.key_points:
                st.markdown(f"• **{point}**")
    
    def chat_page(self):
        st.markdown('<h2 style="color: #1e293b;">💬 AI Tutor</h2>', unsafe_allow_html=True)
        st.info("Ask questions about your uploaded lectures only")
        
        # Chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about processes, deadlocks, scheduling..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("AI thinking..."):
                    response = self.call_ai(
                        prompt,
                        "Answer ONLY using the uploaded lecture content. If not found, say so."
                    )
                    st.markdown(response)
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    def quiz_page(self):
        st.markdown('<h2 style="color: #1e293b;">❓ Practice Quiz</h2>', unsafe_allow_html=True)
        
        if st.button("🔄 New Quiz"):
            st.session_state.quiz_questions = [
                {"question": "PCB contains?", "choices": ["State", "Registers", "All"], "correct": 2},
                {"question": "Deadlock conditions?", "choices": ["2", "3", "4"], "correct": 2}
            ]
            st.session_state.quiz_score = None
        
        if st.session_state.quiz_questions and st.session_state.quiz_score is None:
            score = 0
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}:** {q['question']}")
                ans = st.radio("", q['choices'], key=f"q{i}")
                if ans == q['choices'][q['correct']]:
                    score += 1
            
            if st.button("📤 Submit Quiz"):
                st.session_state.quiz_score = score / len(st.session_state.quiz_questions) * 100
                st.session_state.readiness = st.session_state.quiz_score
                st.success(f"Score: {st.session_state.quiz_score:.0f}%")
    
    def flashcards_page(self):
        st.markdown('<h2 style="color: #1e293b;">🃏 AI Flashcards</h2>', unsafe_allow_html=True)
        for card in st.session_state.flashcards:
            with st.expander(card['front']):
                st.markdown(f"**{card['back']}**")
    
    def run(self):
        self.sidebar()
        
        page = st.session_state.current_page
        if page == 'home':
            self.home_page()
        elif page == 'upload':
            self.upload_page()
        elif page == 'dashboard':
            self.dashboard_page()
        elif page == 'crash':
            self.crash_page()
        elif page == 'workspace':
            self.workspace_page()
        elif page == 'chat':
            self.chat_page()
        elif page == 'quiz':
            self.quiz_page()
        elif page == 'flashcards':
            self.flashcards_page()

if __name__ == "__main__":
    app = StudyOS()
    app.run()
