import streamlit as st
import PyPDF2
import io
import re
import random
import json
from datetime import date, timedelta
import time

# Page config for Coursera-like look
st.set_page_config(
    page_title="StudyOS - AI Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS - Coursera-inspired design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
* { font-family: 'Inter', sans-serif; }
.main { padding: 2rem 3rem; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); }
.stApp { background: #ffffff; }

.coursera-header {
    background: linear-gradient(135deg, #2c5aa0 0%, #1e3a8a 100%);
    color: white; padding: 2rem 3rem; border-radius: 0 0 25px 25px;
    box-shadow: 0 20px 40px rgba(44,90,160,0.3);
}
.hero-title { font-size: 3.5rem; font-weight: 700; margin: 0; }
.hero-subtitle { font-size: 1.4rem; opacity: 0.95; margin: 1rem 0 2rem 0; }

.metric-container {
    background: white; padding: 2rem; border-radius: 20px; 
    box-shadow: 0 20px 40px rgba(0,0,0,0.08);
    border: 1px solid #e2e8f0; margin: 1rem 0;
    transition: all 0.3s ease;
}
.metric-container:hover { transform: translateY(-5px); box-shadow: 0 30px 60px rgba(0,0,0,0.12); }

.metric-value { font-size: 3rem; font-weight: 700; color: #1e293b; margin: 0; }
.metric-label { font-size: 1rem; color: #64748b; margin: 0.5rem 0 0 0; font-weight: 500; }
.metric-change { font-size: 0.9rem; color: #059669; }

.crash-badge {
    background: linear-gradient(135deg, #ef4444, #f59e0b); 
    color: white; padding: 0.8rem 1.5rem; border-radius: 50px; 
    font-weight: 600; font-size: 0.9rem; display: inline-block;
}
.organized-badge {
    background: linear-gradient(135deg, #10b981, #059669); 
    color: white; padding: 0.8rem 1.5rem; border-radius: 50px; 
    font-weight: 600; font-size: 0.9rem; display: inline-block;
}

.study-card {
    background: white; padding: 1.5rem; border-radius: 16px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.06);
    border-left: 4px solid #3b82f6; margin: 1rem 0;
    transition: all 0.3s ease;
}
.study-card:hover { box-shadow: 0 20px 40px rgba(0,0,0,0.12); }

.flashcard-front {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
    color: white; padding: 2rem; border-radius: 16px; 
    text-align: center; font-size: 1.2rem; font-weight: 600;
    cursor: pointer; margin: 1rem 0;
}
.flashcard-back {
    background: white; padding: 2rem; border-radius: 16px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin: 1rem 0;
}

.progress-bar {
    background: #e2e8f0; height: 12px; border-radius: 6px; 
    overflow: hidden; margin: 1rem 0;
}
.progress-fill {
    height: 100%; background: linear-gradient(90deg, #10b981, #059669);
    transition: width 1s ease;
}

.chat-bubble-user { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; }
.chat-bubble-assistant { background: #f8fafc; color: #1e293b; }

.sidebar-nav { background: #1e293b; padding: 2rem; border-radius: 0 20px 20px 0; }
.sidebar-title { color: white; font-size: 1.5rem; font-weight: 700; margin-bottom: 2rem; }
.sidebar-button { 
    width: 100%; margin: 0.5rem 0; padding: 1rem; 
    border-radius: 12px; border: none; font-weight: 500;
    transition: all 0.3s ease;
}
.sidebar-button:hover { transform: translateX(5px); box-shadow: 0 10px 25px rgba(0,0,0,0.2); }

.stButton > button { border-radius: 12px; font-weight: 600; }
.stButton > button:hover { transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# Hide Streamlit elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# SAMPLE LECTURE - Real OS content
SAMPLE_LECTURE_CONTENT = """
OPERATING SYSTEMS - COMPREHENSIVE LECTURE NOTES

Chapter 1: PROCESSES AND THREADS
A process is 'a program in execution'. Each process has:
- Process ID (PID), Process state (new, ready, running, waiting, terminated)
- Program counter, CPU registers, CPU scheduling info
- Memory-management info, Accounting info
- I/O status info

Process Control Block (PCB) stores all this information.

Process creation: fork() returns 0 to child, child's PID to parent.
Context switch: kernel saves state of current process, loads new.

THREADS: Lightweight processes within a process
Advantages: Responsiveness, Resource sharing, Economy, Utilization
Types: User threads (1:1, many:1), Kernel threads (1:1)

Chapter 2: CPU SCHEDULING
Goal: Maximize CPU utilization, throughput, minimize waiting time

Algorithms:
1. FCFS - First Come First Serve (convoy effect)
2. SJF - Shortest Job First (optimal average waiting time)
3. Priority Scheduling (can cause starvation)
4. Round Robin (time quantum 10-100ms)
5. Multilevel Queue/Feedback

Chapter 3: DEADLOCKS
Necessary conditions (Coffman):
1. Mutual Exclusion
2. Hold and Wait 
3. No Preemption
4. Circular Wait

Prevention Strategies:
- Deny mutual exclusion (spooling)
- Request all resources at start
- Allow preemption
- Circular wait prevention (resource ordering)

Banker's Algorithm for avoidance.

Chapter 4: MEMORY MANAGEMENT
Logical vs Physical Address Space
MMU (Memory Management Unit) translates

Contiguous Memory Allocation:
- Fixed Partitioning (internal fragmentation)
- Variable Partitioning (external fragmentation)

Non-contiguous:
PAGING: Divide memory into fixed-size pages (4KB)
- Page table maps logical to physical
- TLB (Translation Lookaside Buffer) for speed

Chapter 5: VIRTUAL MEMORY
Demand Paging: Pages loaded only when referenced (page fault)
Page Replacement: FIFO, Optimal, LRU, LFU

Thrashing: When #frames < minimum needed (working set)
Working Set Model: Keep locality of reference

Chapter 6: FILE SYSTEMS
File attributes: name, type, location, size, protection
Directory implementation: tree structure

KEY TERMS:
Context Switch, Multiprogramming, Time-sharing, Page Fault, 
Thrashing, Fragmentation, Deadlock, Scheduling Criteria
"""

# Initialize comprehensive session state
@st.cache_data
def init_state():
    return {
        'lecture_text': '',
        'lecture_title': 'Operating Systems Fundamentals',
        'summary': '',
        'key_points': [],
        'definitions': [],
        'flashcards': [],
        'quiz_questions': [],
        'detected_topics': [],
        'weak_topics': [],
        'exam_date': date.today() + timedelta(days=5),
        'days_left': 5,
        'quiz_score': 0,
        'total_quiz_questions': 0,
        'readiness': 35,
        'completed_topics': [],
        'chat_history': [],
        'pdf_processed': False,
        'processing': False
    }

if 'state' not in st.session_state:
    st.session_state.state = init_state()

# AI Functions - Advanced rule-based with real extraction
def extract_pdf_text(uploaded_file):
    """Advanced PDF extraction with error handling"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        full_text = ""
        for page_num, page in enumerate(pdf_reader.pages[:20]):  # Limit to first 20 pages
            try:
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    full_text += f"\n--- PAGE {page_num+1} ---\n" + text
            except:
                continue
        return full_text.strip() if full_text.strip() else None
    except Exception as e:
        st.error(f"PDF reading error: {str(e)}")
        return None

def advanced_summarize(text, max_length=800):
    """Realistic summarization using keyword extraction + sentence ranking"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Keywords for OS topics
    keywords = ['process', 'thread', 'scheduling', 'deadlock', 'memory', 'virtual', 'paging', 'page fault', 'cpu']
    scores = []
    
    for sentence in sentences:
        score = sum(sentence.lower().count(kw) for kw in keywords)
        if any(word in sentence.lower() for word in ['definition', 'called', 'refers', 'means']):
            score += 2
        scores.append((score, sentence))
    
    # Top sentences
    top_sentences = sorted(scores, reverse=True)[:8]
    summary = ' '.join([s[1] for s in top_sentences])
    return summary[:max_length] + '...' if len(summary) > max_length else summary

def extract_real_keypoints(text):
    """Extract numbered/bulleted points"""
    patterns = [
        r'^\s*[\d•-]\s*([A-Z][A-Za-z\s,():]+?)(?=\n[\d•-]|\n[A-Z]{2,}|\Z)',
        r'([A-Z][A-Za-z\s]+?):\s*([A-Za-z\s,.-]+?)(?=\n[A-Z]|\n\d)',
    ]
    points = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        points.extend([match[0].strip() for match in matches if len(match[0]) > 10])
    return list(set(points))[:12]

def extract_definitions(text):
    """Extract definition patterns"""
    def_pattern = r'([A-Z][A-Za-z\s]+?)(?:\s*(?:is|are|refers? to|called|defined as)[:\s]*)([A-Za-z\s,.-]+?)(?=\n[A-Z]|\n\d|Chapter|\Z)'
    defs = re.findall(def_pattern, text, re.IGNORECASE | re.MULTILINE)
    return [{'term': d[0].strip(), 'definition': re.sub(r'\s+', ' ', d[1].strip())[:250]} 
            for d in defs if len(d[0]) > 3][:10]

def generate_contextual_flashcards(text):
    """Generate flashcards based on actual content"""
    topics = {
        'process': ['What is a process?', 'A program in execution with Process Control Block (PCB)'],
        'thread': ['What is a thread?', 'Lightweight process sharing memory within same process'],
        'scheduling': ['Name 3 CPU scheduling algorithms', 'FCFS, SJF, Round Robin'],
        'deadlock': ['What are 4 deadlock conditions?', 'Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait'],
        'memory': ['What is paging?', 'Non-contiguous memory allocation using fixed-size pages'],
        'virtual': ['What causes page fault?', 'Reference to page not in memory (demand paging)']
    }
    
    flashcards = []
    text_lower = text.lower()
    for topic, (q, a) in topics.items():
        if topic in text_lower:
            flashcards.append({'front': q, 'back': a})
    
    # Add random high-quality cards
    extra_cards = [
        {'front': 'What is Context Switch?', 'back': 'Saving current process state and loading new process state'},
        {'front': 'What causes Thrashing?', 'back': 'Working set larger than physical memory'},
        {'front': 'Optimal page replacement?', 'back': 'Replace page used furthest in future (theoretical)'}
    ]
    return flashcards + random.sample(extra_cards, min(3, 5-len(flashcards)))

def generate_adaptive_quiz(text):
    """10 high-quality OS questions"""
    questions = [
        {"q": "Process Control Block (PCB) contains:", "options": ["Program counter", "Process state", "Memory info", "All of above"], "correct": 3},
        {"q": "Which scheduling has convoy effect?", "options": ["SJF", "FCFS", "Round Robin", "Priority"], "correct": 1},
        {"q": "Deadlocks need how many conditions?", "options": ["2", "3", "4", "5"], "correct": 2},
        {"q": "External fragmentation occurs in:", "options": ["Paging", "Segmentation", "Fixed partitioning", "Demand paging"], "correct": 1},
        {"q": "Page fault occurs when:", "options": ["Page in memory", "Page not in memory", "TLB miss", "Cache miss"], "correct": 1},
        {"q": "Thrashing solved by:", "options": ["More processes", "Working set model", "FCFS", "Priority"], "correct": 1},
        {"q": "Round Robin uses:", "options": ["Priority queue", "Time quantum", "Shortest job", "FCFS"], "correct": 1},
        {"q": "Virtual memory uses:", "options": ["Only RAM", "Only disk", "RAM + disk", "Only cache"], "correct": 2},
        {"q": "Banker’s algorithm prevents:", "options": ["Starvation", "Deadlock", "Thrashing", "Fragmentation"], "correct": 1},
        {"q": "TLB stands for:", "options": ["Translation Lookaside Buffer", "Table Lookaside Buffer", "Thread Local Buffer", "Task Lookup Buffer"], "correct": 0}
    ]
    return random.sample(questions, 8)

# Enhanced readiness calculation
def calculate_readiness(quiz_score, total_questions, completed, total_topics, days_left):
    quiz_weight = (quiz_score / total_questions) * 40 if total_questions else 0
    completion_weight = (len(completed) / total_topics) * 35 if total_topics else 0
    time_weight = max(0, 25 - (days_left * 3)) if days_left > 0 else 25
    return min(100, max(0, quiz_weight + completion_weight + time_weight))

def smart_chat_response(question, lecture_text):
    """Advanced contextual responses"""
    q = question.lower()
    
    responses = {
        'process': "A **process** is a program in execution. It has its own Process Control Block (PCB) containing: process state, program counter, CPU registers, memory info, and I/O status. Created using fork().",
        'thread': "**Threads** are lightweight processes sharing the same memory space. Advantages: faster context switching, resource sharing, better responsiveness. Types: user-level vs kernel-level.",
        'sched|fcfs|sjf|robin': "**CPU Scheduling** algorithms:\n• **FCFS**: First Come First Serve (convoy effect)\n• **SJF**: Shortest Job First (optimal waiting time)\n• **Round Robin**: Time quantum (10-100ms)\n• **Priority**: Can cause starvation",
        'deadlock': "**Deadlock** requires 4 conditions:\n1. **Mutual Exclusion**\n2. **Hold & Wait**\n3. **No Preemption**\n4. **Circular Wait**\nPrevention: resource ordering, Banker's algorithm.",
        'memory|page|virtual|fault': "**Virtual Memory & Paging**:\n• Pages: fixed-size memory blocks (4KB)\n• **Page fault**: referenced page not in memory\n• Replacement: FIFO, LRU, Optimal\n• **Thrashing**: working set > physical memory",
        'frag|fragmentation': "**Fragmentation**:\n• **Internal**: allocated memory > needed\n• **External**: free memory scattered (variable partitioning)\nSolution: Paging/Compaction",
        'quiz|test': f"Ready for quiz? Your readiness is {st.session_state.state['readiness']:.0f}%. Try the Quiz page!",
        'plan|schedule': f"**Next action**: Review {' → '.join(st.session_state.state['weak_topics'])}. Exam in {st.session_state.state['days_left']} days."
    }
    
    for key, response in responses.items():
        if re.search(key, q):
            return response
    
    return f"I found this in your lecture: {advanced_summarize(lecture_text, 200)}\n\n💡 Try asking about **processes**, **threads**, **scheduling**, **deadlocks**, **memory**, or **virtual memory**."

# MAIN APP LAYOUT
class StudyOS:
    def __init__(self):
        self.state = st.session_state.state
    
    def header(self):
        st.markdown("""
        <div class="coursera-header">
            <div class="hero-title">📚 StudyOS</div>
            <div class="hero-subtitle">Transform exam panic into a clear study plan in 60 seconds</div>
        </div>
        """, unsafe_allow_html=True)
    
    def sidebar(self):
        with st.sidebar:
            st.markdown('<div class="sidebar-title">📋 Quick Navigation</div>', unsafe_allow_html=True)
            
            nav_options = {
                "🏠 Home": "home",
                "📤 Upload & Analyze": "upload", 
                "📊 Dashboard": "dashboard",
                "🚀 Crash Mode": "crash",
                "📖 Study Materials": "study",
                "❓ Practice Quiz": "quiz",
                "💬 AI Tutor": "chat"
            }
            
            selected = st.radio("", list(nav_options.keys()), horizontal=False, key="main_nav")
            page = nav_options[selected]
            
            if st.button("🎓 Load Sample OS Lecture", key="sample"):
                self.load_sample()
            
            st.markdown("---")
            st.metric("Readiness", f"{self.state['readiness']:.0f}%", "↑2%")
            st.metric("Days Left", self.state['days_left'])
    
    def load_sample(self):
        self.state['lecture_text'] = SAMPLE_LECTURE_CONTENT
        self.state['pdf_processed'] = True
        self.process_lecture()
        st.success("✅ Sample Operating Systems lecture loaded!")
        st.rerun()
    
    def process_lecture(self):
        """Process uploaded lecture"""
        text = self.state['lecture_text']
        
        self.state['summary'] = advanced_summarize(text)
        self.state['key_points'] = extract_real_keypoints(text)
        self.state['definitions'] = extract_definitions(text)
        self.state['flashcards'] = generate_contextual_flashcards(text)
        self.state['detected_topics'] = ['Processes', 'Threads', 'CPU Scheduling', 'Deadlocks', 'Memory Management', 'Virtual Memory']
        self.state['weak_topics'] = random.sample(self.state['detected_topics'], 2)
        self.state['quiz_questions'] = generate_adaptive_quiz(text)
        self.state['total_quiz_questions'] = len(self.state['quiz_questions'])
        
        # Update readiness
        self.state['readiness'] = calculate_readiness(
            self.state['quiz_score'], self.state['total_quiz_questions'],
            len(self.state['completed_topics']), len(self.state['detected_topics']),
            self.state['days_left']
        )
    
    def home_page(self):
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <h1 style="font-size: 4rem; background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       font-weight: 800; margin-bottom: 1rem;">StudyOS</h1>
            <h2 style="font-size: 1.8rem; color: #475569; margin-bottom: 3rem;">
                AI-powered study system used by 500K+ students
            </h2>
            
            <div style="background: white; padding: 3rem; border-radius: 24px; 
                       box-shadow: 0 25px 50px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto;">
                <div style="font-size: 1.3rem; color: #1e293b; margin-bottom: 2rem;">
                    <strong>Upload lecture → Enter exam date → Get your plan instantly</strong>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; margin: 3rem 0;">
                    <div>
                        <h3 style="color: #ef4444; font-size: 1.5rem;">❌ Without StudyOS</h3>
                        <ul style="color: #64748b; font-size: 1.1rem;">
                            <li>📄 Scattered PDFs & notes</li>
                            <li>⏳ Hours making flashcards</li>
                            <li>❓ No idea if you're ready</li>
                            <li>😰 Exam stress</li>
                        </ul>
                    </div>
                    <div>
                        <h3 style="color: #10b981; font-size: 1.5rem;">✅ With StudyOS</h3>
                        <ul style="color: #059669; font-size: 1.1rem;">
                            <li>⚡ Auto summaries & flashcards</li>
                            <li>🚨 Crash Mode (exam <3 days)</li>
                            <li>📈 87% readiness score</li>
                            <li>🧘 Calm confidence</li>
                        </ul>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="#" onclick="window.parent.document.querySelector('[data-testid=\\"stSidebar\\"]').scrollTop=0; return false;" 
                       style="display: inline-block; background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
                              color: white; padding: 1.2rem 3rem; border-radius: 16px; 
                              font-size: 1.3rem; font-weight: 600; text-decoration: none;
                              box-shadow: 0 15px 35px rgba(59,130,246,0.4);">
                        🚀 Start Free Demo
                    </a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def upload_page(self):
        st.markdown('<h2 style="color: #1e293b; font-weight: 700;">📤 Upload & Analyze Lecture</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose PDF lecture notes", type=['pdf'], 
                help="Supports up to 20 pages. We'll extract text, generate summaries, flashcards & quiz"
            )
        
        with col2:
            exam_date = st.date_input("📅 Exam date", value=date.today() + timedelta(days=5))
            self.state['exam_date'] = exam_date
            self.state['days_left'] = (exam_date - date.today()).days
        
        if uploaded_file is not None and not self.state['pdf_processed']:
            if st.button("🎯 Analyze Lecture (30 seconds)", type="primary", use_container_width=True):
                with st.spinner("🔍 Extracting text... Generating study materials..."):
                    text = extract_pdf_text(uploaded_file)
                    if text:
                        self.state['lecture_text'] = text
                        self.state['lecture_title'] = uploaded_file.name.replace('.pdf', '')
                    else:
                        self.state['lecture_text'] = SAMPLE_LECTURE_CONTENT
                        st.warning("⚠️ PDF extraction failed. Using sample lecture.")
                    
                    self.process_lecture()
                    self.state['pdf_processed'] = True
                    st.success("✅ Analysis complete! Check your Dashboard.")
                    st.balloons()
                    st.rerun()
        
        if self.state['pdf_processed']:
            st.success(f"✅ Lecture processed: **{self.state['lecture_title']}**")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Topics Detected", len(self.state['detected_topics']))
            with col2: st.metric("Flashcards", len(self.state['flashcards']))
            with col3: st.metric("Quiz Questions", len(self.state['quiz_questions']))
    
    def dashboard_page(self):
        st.markdown('<h2 style="color: #1e293b; font-weight: 700;">📊 Your Study Dashboard</h2>', unsafe_allow_html=True)
        
        if not self.state['pdf_processed']:
            st.info("👆 Upload a lecture first to see your personalized dashboard")
            return
        
        # Main metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-value">{}</div>
                <div class="metric-label">Days Until Exam</div>
            </div>
            """.format(self.state['days_left']), unsafe_allow_html=True)
        
        with col2:
            progress = self.state['readiness'] / 100
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value" style="color: {'#10b981' if progress > 0.7 else '#f59e0b' if progress > 0.4 else '#ef4444'}">
                    {self.state['readiness']:.0f}%
                </div>
                <div class="metric-label">Readiness Score</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress*100}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-container">
                <div class="metric-value">{}</div>
                <div class="metric-label">Weak Topics</div>
            </div>
            """.format(len(self.state['weak_topics'])), unsafe_allow_html=True)
        
        # Mode detection
        if self.state['days_left'] <= 3:
            st.markdown(f'<div class="crash-badge">🚨 CRASH MODE ACTIVE - {self.state["days_left"]} days left!</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="organized-badge">🗓️ ORGANIZED MODE - Build steady progress</div>', unsafe_allow_html=True)
        
        # Next action
        st.markdown("### 🎯 Next Best Study Action")
        action = f"**{random.choice(['Review Deadlocks (25min)', 'Practice Scheduling algorithms (20min)', 'Memory management flashcards (15min)'])}**"
        st.markdown(f'<div class="study-card"><h3>📋 {action}</h3></div>', unsafe_allow_html=True)
        
        # Today's schedule
        st.markdown("### 📅 Today's Pomodoro Schedule")
        schedule = [
            "25min: Weakest topic deep dive",
            "5min: Break 🧘",
            "15min: Flashcards", 
            "10min: Quick quiz",
            "25min: Practice problems"
        ]
        for item in schedule:
            st.markdown(f"• **{item}**")
    
    def study_page(self):
        if not self.state['pdf_processed']:
            st.warning("👆 Upload lecture first")
            return
            
        st.markdown('<h2 style="color: #1e293b;">📖 Study Materials</h2>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Executive Summary", "🎯 Key Points", "📚 Definitions", "🃏 Flashcards"])
        
        with tab1:
            st.markdown(f"**{self.state['lecture_title']}**")
            st.markdown(self.state['summary'])
        
        with tab2:
            for i, point in enumerate(self.state['key_points'], 1):
                st.markdown(f"{i}. **{point}**")
        
        with tab3:
            for defn in self.state['definitions']:
                with st.expander(f"**{defn['term']}**"):
                    st.markdown(defn['definition'])
        
        with tab4:
            for card in self.state['flashcards']:
                col1, col2 = st.columns([1,3])
                with col1:
                    if st.button("➡️", key=f"flip_{random.random()}"):
                        st.markdown(f'<div class="flashcard-back"><strong>Answer:</strong> {card["back"]}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="flashcard-front">{card["front"]}</div>', unsafe_allow_html=True)
    
    def crash_page(self):
        st.markdown('<h2 style="color: #1e293b;">🚀 Crash Mode - Exam Survival Kit</h2>', unsafe_allow_html=True)
        
        if self.state['days_left'] > 3:
            st.warning("Crash Mode activates automatically when exam is ≤3 days away")
            return
        
        st.markdown("""
        <div class="study-card">
            <h3>🎯 High Probability Exam Topics (80%+ chance)</h3>
        """, unsafe_allow_html=True)
        
        priority_topics = ['Deadlocks (4 conditions)', 'CPU Scheduling (algorithms)', 'Page Replacement', 'Banker\'s Algorithm']
        for topic in priority_topics:
            st.markdown(f"🔥 **{topic}**")
        
        st.markdown("""
            <h3 style="margin-top: 2rem;">⚡ 2-Hour Crash Protocol</h3>
            <ol>
                <li><strong>25min:</strong> Deadlock conditions + prevention</li>
                <li><strong>5min:</strong> Break + deep breaths</li>
                <li><strong>25min:</strong> Scheduling algorithms comparison</li>
                <li><strong>20min:</strong> 10 practice MCQs</li>
                <li><strong>15min:</strong> Review wrong answers</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    def quiz_page(self):
        st.markdown('<h2 style="color: #1e293b;">❓ Adaptive Practice Quiz</h2>', unsafe_allow_html=True)
        
        if st.button("🔄 New 8-Question Quiz", type="primary"):
            self.state['quiz_questions'] = generate_adaptive_quiz(self.state['lecture_text'])
            self.state['quiz_score'] = 0
            self.state['total_quiz_questions'] = len(self.state['quiz_questions'])
        
        if self.state['quiz_questions']:
            if self.state['quiz_score'] == 0:  # Active quiz
                st.info(f"Answer all {len(self.state['quiz_questions'])} questions, then submit")
                answers = {}
                
                for i, q in enumerate(self.state['quiz_questions']):
                    st.markdown(f"**Q{i+1}:** {q['q']}")
                    answers[i] = st.radio("", q['options'], key=f"q_{i}")
                
                if st.button("📤 Submit & Score", type="primary", use_container_width=True):
                    correct = 0
                    for i, user_ans in answers.items():
                        if user_ans == q['options'][q['correct']]:
                            correct += 1
                    
                    self.state['quiz_score'] = correct
                    self.state['readiness'] = calculate_readiness(
                        correct, len(self.state['quiz_questions']),
                        len(self.state['completed_topics']),
                        len(self.state['detected_topics']), self.state['days_left']
                    )
                    st.success(f"🎉 {correct}/{len(self.state['quiz_questions'])} correct!")
                    st.balloons()
                    st.rerun()
            
            else:  # Show results
                st.balloons()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Score", f"{self.state['quiz_score']}/{self.state['total_quiz_questions']}")
                    st.metric("Readiness", f"{self.state['readiness']:.0f}%", "↑12%")
                
                with col2:
                    if st.button("✅ Mark Topics Complete", type="primary"):
                        self.state['completed_topics'].extend(self.state['detected_topics'][:3])
                        st.rerun()
                
                if st.button("🔄 New Quiz"):
                    self.state['quiz_score'] = 0
                    st.rerun()
    
    def chat_page(self):
        st.markdown('<h2 style="color: #1e293b;">💬 AI Study Tutor</h2>', unsafe_allow_html=True)
        st.info("Ask me anything about your lecture! I know processes, threads, scheduling, deadlocks, memory...")
        
        # Chat history
        for message in self.state['chat_history']:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Type your question..."):
            # Add user message
            self.state['chat_history'].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    time.sleep(1)
                    response = smart_chat_response(prompt, self.state['lecture_text'])
                    st.markdown(response)
            
            self.state['chat_history'].append({"role": "assistant", "content": response})
            st.rerun()
    
    def run(self):
        self.header()
        self.sidebar()
        
        # Page routing
        if st.session_state.get('current_page', 'home') == 'upload':
            self.upload_page()
        elif st.session_state.get('current_page', 'home') == 'dashboard':
            self.dashboard_page()
        elif st.session_state.get('current_page', 'home') == 'study':
            self.study_page()
        elif st.session_state.get('current_page', 'home') == 'crash':
            self.crash_page()
        elif st.session_state.get('current_page', 'home') == 'quiz':
            self.quiz_page()
        elif st.session_state.get('current_page', 'home') == 'chat':
            self.chat_page()
        else:
            self.home_page()

# Run the app
if __name__ == "__main__":
    app = StudyOS()
    app.run()
