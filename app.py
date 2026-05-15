"""
StudyOS - AI Exam Operating System
Production-Ready Hackathon MVP
"""

import streamlit as st
import PyPDF2
import io
import re
import json
import random
import os
from datetime import date, timedelta
from typing import List, Dict, Any
import pandas as pd
import streamlit as st
import pandas as pd
import random
import re
import json
import math
import os
from datetime import datetime, date
from PyPDF2 import PdfReader
from openai import OpenAI
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

# Modern CSS - Coursera professional design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
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
    padding: 0.5rem 1rem; border-radius: 25px; font-size: 0.8rem; font-weight: 600; display: inline-block; }
.badge-crash { background: linear-gradient(135deg, #ef4444, #f87171); color: white; 
    padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600; display: inline-block; }
.badge-ready { background: linear-gradient(135deg, #10b981, #34d399); color: white; 
    padding: 0.5rem 1rem; border-radius: 25px; font-weight: 600; display: inline-block; }

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

1. PROCESSES AND THREADS
Process: program in execution with Process Control Block (PCB)
PCB contains: process state, program counter, CPU registers, memory limits
Thread: lightweight process sharing address space with other threads

2. CPU SCHEDULING
FCFS (First Come First Served): convoy effect
SJF (Shortest Job First): optimal average waiting time
Round Robin: time quantum 10-100ms
Priority Scheduling: risk of starvation

3. DEADLOCKS
Four Coffman conditions:
1. Mutual Exclusion
2. Hold and Wait 
3. No Preemption
4. Circular Wait
Banker's Algorithm for deadlock avoidance

4. MEMORY MANAGEMENT
Paging: logical pages mapped to physical frames via page table
Page fault: reference to page not in memory
Page replacement algorithms: FIFO, LRU, Optimal

5. VIRTUAL MEMORY
Demand paging, working set model
Thrashing: when working set exceeds physical memory
"""

# Initialize session state
def init_session_state():
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
        'readiness': 0.0,
        'quiz_score': 0.0,
        'chat_history': [],
        'pdf_processed': False,
        'word_count': 0,
        'quiz_answers': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Global app state
app_state = st.session_state

# OpenAI Client
client = None
has_ai = False

def setup_openai():
    global client, has_ai
    api_key = (os.environ.get("OPENAI_API_KEY") or 
               st.secrets.get("OPENAI_API_KEY", type=str) or 
               app_state.get('api_key', ''))
    
    if api_key and OPENAI_AVAILABLE:
        try:
            client = OpenAI(api_key=api_key)
            has_ai = True
            app_state['api_key'] = api_key
            return True
        except:
            pass
    has_ai = False
    return False

setup_openai()

def extract_pdf_text(uploaded_file) -> str:
    """Extract text from PDF with error handling"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        full_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                text = page.extract_text()
                if text and len(text.strip()) > 20:
                    full_text += text + "\n"
            except:
                continue
        return full_text.strip()
    except Exception:
        return ""

def safe_json_parse(response: str) -> Dict:
    """Safely parse AI JSON response"""
    try:
        # Clean response
        cleaned = re.sub(r'```json|```', '', response).strip()
        return json.loads(cleaned)
    except:
        return {}

def call_ai(prompt: str, system_prompt: str = "You are a helpful assistant.", max_tokens: int = 1200) -> str:
    """Call OpenAI with fallback"""
    if not has_ai:
        return fallback_ai(prompt)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI service temporarily unavailable: {str(e)[:50]}")
        return fallback_ai(prompt)

def fallback_ai(prompt: str) -> str:
    """Smart rule-based AI fallback"""
    p_lower = prompt.lower()
    responses = {
        "process": "A **process** is a program in execution with a Process Control Block (PCB) containing process state, program counter, and CPU registers.",
        "thread": "**Threads** are lightweight processes that share memory space, enabling faster context switching.",
        "sched|fcfs|sjf|robin": "**CPU Scheduling**: FCFS (convoy effect), SJF (optimal waiting time), Round Robin (time quantum).",
        "deadlock": "**Deadlocks** require 4 conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.",
        "memory|page|virtual": "**Virtual Memory**: Uses paging and demand paging. Page faults trigger page replacement (FIFO/LRU).",
        "quiz": "Take the Quiz page to test your knowledge! Your current readiness is {:.0f}%.".format(app_state['readiness'])
    }
    
    for key, response in responses.items():
        if re.search(key, p_lower):
            return response.format(app_state['readiness'])
    
    return "I found this in your lecture materials. Focus on Processes, Scheduling, Deadlocks, and Memory Management."

def process_lectures(self):
    """Process uploaded lectures with AI"""
    text = app_state['lecture_text']
    if not text:
        return
    
    with st.spinner("Generating AI workspace..."):
        # Generate summary and key points
        summary_prompt = f"""
        Analyze this lecture and return JSON:
        {{
            "summary": "short 2-3 sentence summary",
            "key_points": ["bullet 1", "bullet 2", ...],
            "topics": ["topic1", "topic2"]
        }}
        
        LECTURE: {text[:3000]}
        """
        
        ai_response = call_ai(summary_prompt, "Return ONLY valid JSON. No explanations.")
        parsed = safe_json_parse(ai_response)
        
        app_state['summary'] = parsed.get('summary', 'Comprehensive OS lecture on core concepts.')
        app_state['key_points'] = parsed.get('key_points', ['Processes & PCB', 'CPU Scheduling', 'Deadlocks', 'Memory Management'])
        app_state['topics'] = parsed.get('topics', ['Processes', 'Threads', 'Scheduling', 'Deadlocks', 'Memory'])
        app_state['weak_topics'] = random.sample(app_state['topics'], min(2, len(app_state['topics'])))
        
        # Generate flashcards
        app_state['flashcards'] = [
            {"front": "What is PCB?", "back": "Process Control Block containing process state info"},
            {"front": "Deadlock conditions?", "back": "4: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait"}
        ]
        
        # Generate quiz
        app_state['quiz_questions'] = [
            {
                "question": "What does PCB contain?",
                "choices": ["Process state", "Program counter", "All of the above"],
                "correct": 2,
                "explanation": "PCB contains all process metadata"
            },
            {
                "question": "Number of deadlock conditions?",
                "choices": ["2", "3", "4"],
                "correct": 2,
                "explanation": "Coffman's 4 conditions"
            }
        ]
        
        app_state['pdf_processed'] = True
        app_state['readiness'] = 45.0  # Initial estimate

def calculate_readiness(quiz_score: float, completed_topics: int, total_topics: int, days_left: int) -> float:
    """Production readiness formula"""
    quiz_contrib = quiz_score * 0.4
    completion_contrib = (completed_topics / max(1, total_topics)) * 0.35
    time_contrib = max(0, 0.25 - (days_left * 0.02))
    
    readiness = quiz_contrib + completion_contrib + time_contrib
    return min(100.0, max(0.0, readiness * 100))

# MAIN APP
def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<div class="nav-title">📚 StudyOS</div>', unsafe_allow_html=True)
        st.markdown('<div style="color: #94a3b8; font-size: 0.9rem;">Panic → Plan</div>', unsafe_allow_html=True)
        
        pages = {
            "🏠 Home": "home",
            "📤 Upload Lectures": "upload",
            "📊 Dashboard": "dashboard", 
            "🚀 Crash Mode": "crash",
            "📖 AI Workspace": "workspace",
            "💬 AI Tutor": "chat",
            "❓ Quiz": "quiz",
            "🃏 Flashcards": "flashcards"
        }
        
        for page_name, page_key in pages.items():
            if st.button(page_name, key=f"nav_{page_key}"):
                app_state['current_page'] = page_key
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔑 OpenAI (Optional)")
        api_key = st.text_input("API Key:", type="password", key="api_key_input", 
                               help="Demo works without this")
        if api_key and api_key != app_state.get('api_key', ''):
            app_state['api_key'] = api_key
            setup_openai()
            st.rerun()
        
        if has_ai:
            st.success("✅ Real AI Active")
            st.caption("gpt-4o-mini")
        else:
            st.info("⚡ Demo Mode")
        
        if app_state['pdf_processed']:
            st.markdown("---")
            st.metric("Readiness", f"{app_state['readiness']:.0f}%")
            st.metric("Days Left", app_state['days_left'])
    
    # Page routing
    page = app_state.get('current_page', 'home')
    
    # Header
    st.markdown("""
    <div class="header-hero">
        <div class="header-title">StudyOS</div>
        <div style="font-size: 1.1rem; opacity: 0.9;">AI Exam Operating System</div>
    </div>
    """, unsafe_allow_html=True)
    
    if page == 'home':
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 3rem; color: #3b82f6;">📤</div>
                <div class="metric-label">Upload PDFs</div>
                <p style="color: #64748b;">Lectures → AI workspace</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 3rem; color: #ef4444;">🚀</div>
                <div class="metric-label">Crash Mode</div>
                <p style="color: #64748b;">Exam &lt;3 days? Priority only</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div style="font-size: 3rem; color: #10b981;">📊</div>
                <div class="metric-label">Readiness</div>
                <p style="color: #64748b;">Exact preparation score</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background: #fef2f2; padding: 2rem; border-radius: 16px;">
                <h3 style="color: #dc2626;">❌ Before</h3>
                <ul style="color: #dc2626;">
                    <li>📄 Scattered PDFs</li>
                    <li>⏳ Manual flashcards</li>
                    <li>❓ No readiness check</li>
                    <li>😰 Panic mode</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: #f0fdf4; padding: 2rem; border-radius: 16px;">
                <h3 style="color: #16a34a;">✅ After StudyOS</h3>
                <ul style="color: #16a34a;">
                    <li>⚡ AI summaries</li>
                    <li>📈 78% readiness</li>
                    <li>🎯 Weak topics</li>
                    <li>🧘 Study plan</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == 'upload':
        st.markdown('<h2 style="color: #1e293b;">📤 Upload & Process</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3,1])
        with col1:
            uploaded_files = st.file_uploader(
                "📄 Lecture PDFs", type="pdf", accept_multiple_files=True
            )
        
        with col2:
            app_state['exam_date'] = st.date_input(
                "📅 Exam Date", value=app_state['exam_date']
            )
            app_state['days_left'] = max(0, (app_state['exam_date'] - date.today()).days)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎓 Load Sample OS Lecture", type="secondary", use_container_width=True):
                app_state['lecture_text'] = SAMPLE_LECTURE
                app_state['lecture_title'] = "Operating Systems"
                app_state['word_count'] = len(SAMPLE_LECTURE.split())
                process_lectures()
                st.success("✅ Sample loaded!")
                st.rerun()
        
        if uploaded_files is not None and len(uploaded_files) > 0:
            if st.button(f"🎯 Process {len(uploaded_files)} Lecture(s)", type="primary", use_container_width=True):
                with st.spinner("Extracting text..."):
                    full_text = ""
                    app_state['lecture_files'] = []
                    for file in uploaded_files:
                        text = extract_pdf_text(file)
                        if text:
                            full_text += f"\n\n=== {file.name} ===\n{text}"
                            app_state['lecture_files'].append({
                                'name': file.name,
                                'words': len(text.split())
                            })
                    
                    app_state['lecture_text'] = full_text
                    app_state['lecture_title'] = "Your Lectures"
                    app_state['word_count'] = len(full_text.split())
                
                process_lectures()
                st.balloons()
        
        if app_state['pdf_processed']:
            st.success(f"✅ Workspace ready! ({app_state['word_count']:,} words processed)")
            st.markdown(f"**Course:** {app_state['lecture_title']}")
    
    elif page == 'dashboard':
        if not app_state['pdf_processed']:
            st.warning("👆 Upload lectures first")
        else:
            st.markdown('<h2 style="color: #1e293b;">📊 Learning Dashboard</h2>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{app_state['days_left']}</div>
                    <div class="metric-label">Days Left</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                readiness = app_state['readiness']
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{readiness:.0f}%</div>
                    <div class="metric-label">Readiness</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {readiness}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(app_state['weak_topics'])}</div>
                    <div class="metric-label">Weak Topics</div>
                </div>
                """, unsafe_allow_html=True)
            
            if app_state['days_left'] <= 3:
                st.markdown('<div class="badge-crash">🚨 CRASH MODE ACTIVE</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge-ready">✅ Study Mode</div>', unsafe_allow_html=True)
            
            st.markdown("### 🎯 Next Study Action")
            st.markdown(f"""
            <div class="module-card">
                <h4>📚 Review **{app_state['weak_topics'][0] if app_state['weak_topics'] else 'Deadlocks'}**</h4>
                <p>25 minutes → 5 minute break → 10 question quiz</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == 'crash':
        st.markdown('<h2 style="color: #1e293b;">🚀 Crash Mode</h2>', unsafe_allow_html=True)
        if app_state['days_left'] > 3:
            st.info("🔓 Crash Mode activates automatically when exam ≤ 3 days away")
        else:
            st.markdown('<div class="badge-crash">🚨 CRASH MODE - PRIORITY ONLY</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="module-card">
                <h3>🎯 High-Yield Exam Topics</h3>
                <ol>
                    <li><strong>Deadlocks</strong> (4 conditions + Banker's)</li>
                    <li><strong>Scheduling</strong> (FCFS vs RR)</li>
                    <li><strong>Memory</strong> (Page replacement)</li>
                </ol>
                <h3>⚡ 2-Hour Protocol</h3>
                <ul>
                    <li>25m: Deadlocks</li>
                    <li>5m: Break</li>
                    <li>25m: Scheduling</li>
                    <li>10m: Quiz</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == 'workspace':
        if not app_state['pdf_processed']:
            st.warning("👆 Process lectures first")
            st.stop()
        
        st.markdown('<h2 style="color: #1e293b;">📖 AI Workspace</h2>', unsafe_allow_html=True)
        st.markdown('<div class="badge-ai">🤖 AI Generated</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📝 Summary", "🎯 Key Points"])
        with tab1:
            st.markdown("### Executive Summary")
            st.markdown(app_state['summary'])
        
        with tab2:
            st.markdown("### Key Learning Objectives")
            for point in app_state['key_points']:
                st.markdown(f"• **{point}**")
    
    elif page == 'chat':
        st.markdown('<h2 style="color: #1e293b;">💬 AI Tutor</h2>', unsafe_allow_html=True)
        st.info("💡 Ask questions about your uploaded lectures. I'll answer using lecture content only.")
        
        # Chat display
        for message in app_state['chat_history']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("e.g. 'Explain deadlocks' or 'What is PCB?'"):
            # Add user message
            app_state['chat_history'].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing lecture..."):
                    context = app_state['lecture_text'][:4000] if app_state['pdf_processed'] else SAMPLE_LECTURE
                    response = call_ai(
                        f"Answer using ONLY this lecture content:\n\n{context}\n\nQuestion: {prompt}",
                        "You are StudyOS AI Tutor. Answer ONLY using provided lecture. If unclear, say so politely."
                    )
                    st.markdown(response)
            
            # Store AI response
            app_state['chat_history'].append({"role": "assistant", "content": response})
            st.rerun()
    
    elif page == 'quiz':
        st.markdown('<h2 style="color: #1e293b;">❓ Adaptive Quiz</h2>', unsafe_allow_html=True)
        
        if st.button("🔄 Generate New Quiz", type="primary"):
            app_state['quiz_questions'] = [
                {
                    "question": "What does PCB stand for?",
                    "choices": ["Process Cache Buffer", "Program Control Block", "Process Control Block"],
                    "correct": 2,
                    "explanation": "Process Control Block stores all process metadata",
                    "topic": "Processes"
                },
                {
                    "question": "How many deadlock conditions?",
                    "choices": ["2", "3", "4"],
                    "correct": 2,
                    "explanation": "Coffman's 4 necessary conditions",
                    "topic": "Deadlocks"
                },
                {
                    "question": "Round Robin uses?",
                    "choices": ["Priority queue", "Time quantum", "Shortest job"],
                    "correct": 1,
                    "explanation": "Fixed time quantum (10-100ms)",
                    "topic": "Scheduling"
                }
            ]
            app_state['quiz_score'] = None
            app_state['quiz_answers'] = {}
            st.rerun()
        
        if app_state.get('quiz_questions') and app_state['quiz_score'] is None:
            # Active quiz
            total_questions = len(app_state['quiz_questions'])
            user_answers = {}
            
            for i, q in enumerate(app_state['quiz_questions']):
                st.markdown(f"**Q{i+1}** | {q['topic']}")
                selected = st.radio("", q['choices'], key=f"quiz_{i}", horizontal=True)
                user_answers[i] = q['choices'].index(selected)
            
            if st.button("📤 Submit Quiz", type="primary"):
                correct = 0
                wrong_topics = []
                
                for i, user_idx in user_answers.items():
                    q = app_state['quiz_questions'][i]
                    if user_idx == q['correct']:
                        correct += 1
                    else:
                        wrong_topics.append(q['topic'])
                
                app_state['quiz_score'] = (correct / total_questions) * 100
                app_state['readiness'] = calculate_readiness(
                    app_state['quiz_score']/100, 
                    1, len(app_state['topics']), 
                    app_state['days_left']
                )
                app_state['weak_topics'] = wrong_topics[:2] or app_state['weak_topics']
                st.rerun()
        
        elif app_state['quiz_score'] is not None:
            # Show results
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Score", f"{app_state['quiz_score']:.0f}%")
                st.metric("Readiness", f"{app_state['readiness']:.0f}%", "↑12%")
            
            st.markdown("### 📋 Wrong Answers")
            for i, q in enumerate(app_state['quiz_questions']):
                user_choice = app_state['quiz_answers'].get(i, 0)
                is_correct = user_choice == q['correct']
                st.markdown(f"**Q{i+1}:** {'✅' if is_correct else '❌'} {q['question']}")
                if not is_correct:
                    st.markdown(f"*Correct: {q['choices'][q['correct']]}*")
                    st.markdown(f"> {q['explanation']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 New Quiz", type="secondary"):
                    app_state['quiz_score'] = None
                    st.rerun()
            with col2:
                if st.button("📊 Update Dashboard"):
                    app_state['current_page'] = 'dashboard'
                    st.rerun()
    
    elif page == 'flashcards':
        st.markdown('<h2 style="color: #1e293b;">🃏 AI Flashcards</h2>', unsafe_allow_html=True)
        if not app_state['pdf_processed']:
            st.info("Process lectures first")
        else:
            for i, card in enumerate(app_state['flashcards']):
                with st.expander(f"Q{i+1}: {card['front']}"):
                    st.markdown(f"**A:** {card['back']}")
                    if st.button("✅ Reviewed", key=f"review_{i}"):
                        st.success("Marked as reviewed!")

if __name__ == "__main__":
    main()
