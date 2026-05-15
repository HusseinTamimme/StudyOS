import streamlit as st
import PyPDF2
import pandas as pd
import datetime
import re
import random
import io

# Custom CSS
st.markdown("""
<style>
    .main {padding: 2rem;}
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .metric-card {background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);}
    .hero-section {background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 3rem; border-radius: 20px; text-align: center;}
    .crash-badge {background: linear-gradient(135deg, #ef4444, #f97316); color: white; padding: 0.5rem 1rem; border-radius: 50px; font-weight: bold;}
    .organized-badge {background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 0.5rem 1rem; border-radius: 50px; font-weight: bold;}
    .topic-card {background: #f8fafc; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #3b82f6;}
    .flashcard {background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin: 1rem 0;}
    h1, h2, h3 {color: #1e40af;}
    .stMetric {background: white; padding: 1rem; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

# Hide Streamlit footer and menu
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Sample lecture content
SAMPLE_LECTURE = """
LECTURE: OPERATING SYSTEMS FUNDAMENTALS

1. PROCESSES
A process is a program in execution. It has:
- Process Control Block (PCB): Contains process state, program counter, CPU registers, etc.
- Process states: New, Ready, Running, Waiting, Terminated
- Process creation: fork() system call creates child process

2. THREADS
Thread is lightweight process. Benefits:
- Faster context switching
- Shared memory between threads of same process
- Types: User-level threads, Kernel-level threads

3. CPU SCHEDULING
Purpose: Determine which process gets CPU and when
Scheduling criteria:
- CPU utilization, Throughput, Turnaround time, Waiting time, Response time
Algorithms:
- FCFS (First Come First Serve)
- SJF (Shortest Job First)
- Priority Scheduling
- Round Robin (RR) with time quantum

4. DEADLOCKS
Deadlock: Two or more processes indefinitely blocked
Conditions (Coffman conditions):
1. Mutual Exclusion
2. Hold and Wait
3. No Preemption
4. Circular Wait
Prevention: Break one of the 4 conditions
Avoidance: Banker's Algorithm
Detection: Resource Allocation Graph

5. MEMORY MANAGEMENT
Logical vs Physical address space
Contiguous allocation: Fixed/Variable partitioning, Fragmentation
Non-contiguous: Paging, Segmentation

6. VIRTUAL MEMORY
Demand paging, Pure swapping
Page fault handling
Page replacement algorithms:
- FIFO (First In First Out)
- Optimal
- LRU (Least Recently Used)
Thrashing: When working set > physical memory

KEY DEFINITIONS:
- Context Switch: Saving/restoring process/thread state
- Multiprogramming: Multiple programs in memory simultaneously
- Time-sharing: Multiple users share system interactively
"""

# Initialize session state
def init_session_state():
    defaults = {
        'lecture_text': '',
        'lecture_title': 'Operating Systems Fundamentals',
        'summary': '',
        'key_points': [],
        'definitions': [],
        'flashcards': [],
        'quiz_questions': [],
        'detected_topics': [],
        'weak_topics': [],
        'exam_date': None,
        'days_left': 0,
        'quiz_score': 0,
        'readiness': 0,
        'completed_topics': [],
        'current_page': 'home',
        'chat_history': []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# PDF extraction function
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip() if text.strip() else None
    except Exception:
        return None

# AI Simulation Functions
def generate_summary(text):
    lines = text.split('\n')
    key_lines = [line.strip() for line in lines if len(line.strip()) > 20 and any(word in line.lower() for word in ['process', 'thread', 'scheduling', 'deadlock', 'memory', 'virtual'])]
    summary = " ".join(key_lines[:5])
    return summary[:500] + "..." if len(summary) > 500 else summary

def extract_key_points(text):
    points = re.findall(r'\d+\.\s*([A-Z\s]+)', text)
    return points[:8] if points else ['Processes', 'Threads', 'CPU Scheduling', 'Deadlocks', 'Memory Management', 'Virtual Memory']

def extract_definitions(text):
    defs = re.findall(r'([A-Z][A-Za-z\s]+):\s*([A-Za-z\s,.-]+?)(?=\n\d|\n[A-Z]{2,}|\Z)', text, re.DOTALL)
    return [{"term": d[0].strip(), "definition": d[1].strip()[:200]} for d in defs[:6]]

def generate_flashcards(text):
    topics = ['Process', 'Thread', 'Deadlock', 'Page Fault', 'CPU Scheduling', 'Virtual Memory']
    flashcards = []
    for topic in topics:
        flashcards.append({
            "question": f"What is a {topic.lower()}?",
            "answer": f"{topic} is a fundamental OS concept involving {random.choice(['execution', 'resource management', 'scheduling', 'memory allocation'])}."
        })
    return flashcards[:8]

def generate_quiz(text):
    questions = [
        {
            "question": "What does PCB stand for?",
            "options": ["Process Control Block", "Program Control Buffer", "Process CPU Buffer", "Program Context Block"],
            "correct": 0
        },
        {
            "question": "Which scheduling algorithm uses time quantum?",
            "options": ["FCFS", "SJF", "Round Robin", "Priority"],
            "correct": 2
        },
        {
            "question": "Deadlock requires how many conditions?",
            "options": ["2", "3", "4", "5"],
            "correct": 2
        },
        {
            "question": "What causes thrashing?",
            "options": ["Too many processes", "Insufficient memory", "Poor scheduling", "Too much memory"],
            "correct": 1
        },
        {
            "question": "Virtual memory uses:",
            "options": ["Only physical memory", "Only secondary storage", "Both physical and secondary", "Cache only"],
            "correct": 2
        }
    ]
    return random.sample(questions, min(5, len(questions)))

def detect_topics(text):
    return ['Processes', 'Threads', 'CPU Scheduling', 'Deadlocks', 'Memory Management', 'Virtual Memory']

def calculate_readiness(quiz_score, completed_topics, total_topics, days_left):
    topic_completion = min(100, (len(completed_topics) / total_topics * 100) * 1.4) if total_topics > 0 else 0
    quiz_perf = (quiz_score / 5 * 100) * 0.4 if quiz_score > 0 else 20
    time_factor = max(0, 100 - (days_left * 5)) * 0.2 if days_left > 0 else 50
    readiness = topic_completion + quiz_perf + time_factor
    return min(100, max(0, readiness))

def generate_next_best_action(weak_topics, days_left):
    if days_left <= 3:
        return f"🚨 CRASH MODE: Review '{weak_topics[0] if weak_topics else 'Deadlocks'}' NOW (25 mins)"
    else:
        return f"📚 Start with '{weak_topics[0] if weak_topics else 'Processes'}' flashcards (15 mins)"

def answer_from_lecture(question, lecture_text):
    q_lower = question.lower()
    topics = {
        'process': 'A process is a program in execution with its own Process Control Block (PCB) containing state information.',
        'thread': 'A thread is a lightweight process that shares memory with other threads in the same process.',
        'scheduling': 'CPU scheduling determines which process gets the CPU. Common algorithms: FCFS, SJF, Round Robin.',
        'deadlock': 'Deadlock occurs when processes are stuck waiting for each other. Requires 4 conditions: Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait.',
        'memory': 'Memory management handles allocation of physical memory to processes using paging and segmentation.',
        'virtual': 'Virtual memory allows processes to use more memory than physically available through demand paging.'
    }
    
    for key, answer in topics.items():
        if key in q_lower:
            return answer
    
    return "I couldn't find this clearly in your lecture. Try asking about Processes, Threads, Scheduling, Deadlocks, Memory, or Virtual Memory."

# Sidebar Navigation
st.sidebar.title("📚 StudyOS")
st.sidebar.markdown("**From exam panic to a clear study plan in 60 seconds.**")

pages = {
    "🏠 Home": "home",
    "📤 Upload Lecture": "upload",
    "📖 Study Workspace": "workspace",
    "🚀 Crash Mode": "crash",
    "📊 Calm Dashboard": "dashboard",
    "💬 AI Chat": "chat",
    "❓ Quiz": "quiz"
}

selected_page = st.sidebar.radio("Navigate:", list(pages.keys()), key="nav")
current_page = pages[selected_page]

# Update current page
st.session_state.current_page = current_page

# Home Page
if current_page == "home":
    st.markdown("""
    <div class="hero-section">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">StudyOS</h1>
        <h2 style="font-size: 1.5rem; margin-bottom: 2rem;">From exam panic to a clear study plan in 60 seconds</h2>
        <p style="font-size: 1.2rem; margin-bottom: 3rem;">
            📚 Upload lecture → 🎯 Enter exam date → 🚀 Get your personalized study plan
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ❌ Before StudyOS
        <div style="background: #fee2e2; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
            <ul style="font-size: 1.1rem;">
                <li>📄 6 scattered PDFs</li>
                <li>✍️ Manual flashcards (2 hours)</li>
                <li>❓ No readiness signal</li>
                <li>😱 Exam panic</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        ### ✅ After StudyOS
        <div style="background: #dcfce7; padding: 1.5rem; border-radius: 15px; margin: 1rem 0;">
            <ul style="font-size: 1.1rem;">
                <li>⚡ Auto-generated workspace</li>
                <li>🚨 Crash Mode (if exam near)</li>
                <li>📈 Weakness detection</li>
                <li>🧘 Calm Dashboard</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.button("🚀 Start Demo", type="primary", on_click=lambda: st.session_state.update(current_page="upload"))

# Upload Lecture Page
elif current_page == "upload":
    st.header("📤 Upload Your Lecture")
    
    col1, col2 = st.columns([3,1])
    
    with col1:
        uploaded_file = st.file_uploader("Choose PDF file", type="pdf")
    
    with col2:
        if st.button("🎓 Use Sample OS Lecture", type="secondary"):
            st.session_state.lecture_text = SAMPLE_LECTURE
            st.session_state.lecture_title = "Operating Systems Fundamentals"
            st.success("✅ Sample lecture loaded!")
    
    st.date_input("📅 Exam Date", key="exam_date_input")
    
    if st.button("🎯 Process Lecture & Generate Study Plan", type="primary"):
        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)
            if text:
                st.session_state.lecture_text = text
            else:
                st.session_state.lecture_text = SAMPLE_LECTURE
                st.warning("⚠️ PDF reading failed. Using sample lecture.")
        elif not st.session_state.lecture_text:
            st.session_state.lecture_text = SAMPLE_LECTURE
        
        st.session_state.exam_date = st.session_state.exam_date_input
        if st.session_state.exam_date:
            st.session_state.days_left = (st.session_state.exam_date - datetime.date.today()).days
        
        # Generate all study materials
        st.session_state.summary = generate_summary(st.session_state.lecture_text)
        st.session_state.key_points = extract_key_points(st.session_state.lecture_text)
        st.session_state.definitions = extract_definitions(st.session_state.lecture_text)
        st.session_state.flashcards = generate_flashcards(st.session_state.lecture_text)
        st.session_state.quiz_questions = generate_quiz(st.session_state.lecture_text)
        st.session_state.detected_topics = detect_topics(st.session_state.lecture_text)
        st.session_state.weak_topics = random.sample(st.session_state.detected_topics, 2)
        
        st.session_state.readiness = calculate_readiness(
            st.session_state.quiz_score,
            len(st.session_state.completed_topics),
            len(st.session_state.detected_topics),
            st.session_state.days_left
        )
        
        st.success("🎉 Study materials generated successfully!")
        st.rerun()

# Study Workspace
elif current_page == "workspace":
    st.header("📖 Study Workspace")
    
    if not st.session_state.lecture_text:
        st.warning("👆 Please upload a lecture first on the Upload page.")
        st.stop()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Summary", "🎯 Key Points", "📚 Definitions", "🃏 Flashcards", "📅 Study Plan"])
    
    with tab1:
        st.markdown(f"**{st.session_state.lecture_title}**")
        st.markdown(st.session_state.summary)
    
    with tab2:
        for point in st.session_state.key_points:
            st.markdown(f"**• {point}**")
    
    with tab3:
        for defn in st.session_state.definitions:
            with st.expander(defn["term"]):
                st.write(defn["definition"])
    
    with tab4:
        for card in st.session_state.flashcards:
            with st.expander(card["question"]):
                st.success(card["answer"])
    
    with tab5:
        st.markdown("### 📅 Personalized Study Plan")
        st.markdown(f"- **Next action**: {generate_next_best_action(st.session_state.weak_topics, st.session_state.days_left)}")
        st.markdown("- **Daily schedule**: 25min study → 5min break → 15min review → 10min quiz")

# Crash Mode
elif current_page == "crash":
    st.header("🚀 Crash Mode")
    
    if not st.session_state.exam_date:
        st.session_state.exam_date = st.date_input("Enter exam date for Crash Mode")
        st.stop()
    
    if st.session_state.days_left <= 3:
        st.markdown('<div class="crash-badge">🚨 CRASH MODE ACTIVATED — Exam in {} days!</div>'.format(st.session_state.days_left), unsafe_allow_html=True)
        
        st.markdown("### 🔥 Critical Topics (High exam probability)")
        for topic in st.session_state.weak_topics:
            st.markdown(f'<div class="topic-card">📌 **{topic}** - Review NOW</div>', unsafe_allow_html=True)
        
        st.markdown("### ⚡ 2-Hour Crash Plan")
        st.markdown("""
        1. **25min**: Deadlocks (most likely exam question)
        2. **5min**: Break & breathe  
        3. **25min**: CPU Scheduling algorithms
        4. **5min**: Break
        5. **20min**: Quiz yourself
        6. **10min**: Review wrong answers
        """)
        
        st.markdown("### 🎯 Most Likely Exam Questions")
        st.markdown("- Explain the 4 deadlock conditions")
        st.markdown("- Compare FCFS vs Round Robin")
        st.markdown("- What causes page faults?")
        
    else:
        st.markdown('<div class="organized-badge">🗓️ Organized Mode — You have time for full preparation</div>', unsafe_allow_html=True)
        st.info("Set exam date within 3 days to activate Crash Mode")

# Calm Dashboard
elif current_page == "dashboard":
    st.header("📊 Calm Dashboard")
    st.markdown("**The panic becomes a plan.**")
    
    if not st.session_state.lecture_text:
        # Use sample data for demo
        st.session_state.detected_topics = detect_topics(SAMPLE_LECTURE)
        st.session_state.weak_topics = ['Deadlocks', 'CPU Scheduling']
        st.session_state.days_left = 2
        st.session_state.readiness = 71
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{st.session_state.days_left} days left</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        progress = st.session_state.readiness / 100
        st.markdown(f"""
        <div class="metric-card">
            <h2>{int(st.session_state.readiness)}%</h2>
            <div style="background: #e5e7eb; height: 20px; border-radius: 10px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #3b82f6, #1e40af); height: 100%; width: {progress*100}%;"></div>
            </div>
            <p>Readiness Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(st.session_state.weak_topics)} topics</h3>
            <p>Remaining</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Next Best Study Action")
    st.markdown(f"**{generate_next_best_action(st.session_state.weak_topics, st.session_state.days_left)}**")
    
    st.markdown("### 📋 Today's Study Schedule")
    st.markdown("""
    - **25min**: Review weakest topic  
    - **5min**: Break 🧘
    - **15min**: Flashcards
    - **10min**: Quiz wrong answers
    - **25min**: Deep dive weak topic
    """)

# AI Chat
elif current_page == "chat":
    st.header("💬 AI Study Assistant")
    st.info("Ask anything about your lecture content!")
    
    # Chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about processes, threads, scheduling, deadlocks, memory..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            answer = answer_from_lecture(prompt, st.session_state.lecture_text)
            st.markdown(answer)
        
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

# Quiz Page
elif current_page == "quiz":
    st.header("❓ Practice Quiz")
    
    if not st.session_state.lecture_text:
        st.session_state.quiz_questions = generate_quiz(SAMPLE_LECTURE)
    
    if st.button("🔄 New Quiz", type="secondary"):
        st.session_state.quiz_questions = generate_quiz(st.session_state.lecture_text)
        st.session_state.quiz_score = 0
    
    if st.session_state.quiz_questions:
        score = st.session_state.quiz_score
        total = len(st.session_state.quiz_questions)
        
        # Show results if quiz completed
        if score > 0:
            st.markdown(f"### 📊 Your Score: {score}/{total} ({int(score/total*100)}%)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Mark topics complete"):
                    st.session_state.completed_topics = st.session_state.detected_topics[:2]
                    st.session_state.readiness = calculate_readiness(score, 2, len(st.session_state.detected_topics), st.session_state.days_left)
                    st.rerun()
            
            with col2:
                if st.button("🔄 Retake Quiz"):
                    st.session_state.quiz_score = 0
                    st.rerun()
        
        # Active quiz
        else:
            answers = []
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}:** {q['question']}")
                ans = st.radio("Choose:", [opt for opt in q['options']], key=f"q{i}")
                answers.append(q['options'].index(ans))
            
            if st.button("📤 Submit Quiz", type="primary"):
                correct = sum(1 for i, ans in enumerate(answers) if ans == st.session_state.quiz_questions[i]['correct'])
                st.session_state.quiz_score = correct
                st.rerun()
