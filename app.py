"""
StudyOS - AI Exam Operating System
Corrected Streamlit Hackathon MVP
"""

import os
import io
import re
import json
import random
from datetime import date, timedelta
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
from PyPDF2 import PdfReader

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


MODEL_NAME = "gpt-4o-mini"


SAMPLE_LECTURE = """
OPERATING SYSTEMS FUNDAMENTALS

1. INTRODUCTION TO OPERATING SYSTEMS
An operating system manages computer hardware and software resources. It provides services for programs and acts as an interface between users and hardware.

2. PROCESSES AND PROCESS CONTROL BLOCK
A process is a program in execution. Each process has a Process Control Block, also called PCB.
The PCB stores the process state, program counter, CPU registers, memory limits, open files, scheduling information, and accounting information.

3. THREADS
A thread is a lightweight unit of execution within a process. Threads inside the same process share memory and resources.
Threads improve responsiveness and allow parallelism, but they also require synchronization to avoid race conditions.

4. CPU SCHEDULING
CPU scheduling decides which ready process gets the CPU next.
First Come First Served is simple but may cause the convoy effect.
Shortest Job First gives optimal average waiting time but requires knowing the next CPU burst.
Round Robin gives each process a time quantum and is commonly used in time-sharing systems.
Priority Scheduling chooses the process with highest priority, but starvation can happen.

5. DEADLOCKS
Deadlock happens when processes wait forever because each process is holding a resource and waiting for another resource.
The four Coffman conditions are mutual exclusion, hold and wait, no preemption, and circular wait.
Deadlock can be handled through prevention, avoidance, detection, and recovery.
The Banker’s Algorithm is used for deadlock avoidance.

6. MEMORY MANAGEMENT
Memory management controls how processes are loaded into memory.
Paging divides logical memory into pages and physical memory into frames.
The page table maps pages to frames.
A page fault happens when a process tries to access a page that is not currently in memory.

7. VIRTUAL MEMORY
Virtual memory allows programs to run even if they are larger than physical memory.
Demand paging loads pages only when needed.
Thrashing happens when the system spends more time swapping pages than executing processes.

8. PAGE REPLACEMENT
When memory is full, the operating system chooses a page to remove.
FIFO replaces the oldest page.
LRU replaces the least recently used page.
Optimal replacement removes the page that will not be used for the longest time in the future.

SUMMARY
The most important exam topics are processes, threads, CPU scheduling, deadlocks, memory management, virtual memory, and page replacement.
"""


DEFAULT_TOPICS = [
    "Processes",
    "Threads",
    "CPU Scheduling",
    "Deadlocks",
    "Memory Management",
    "Virtual Memory",
    "Page Replacement",
]


st.set_page_config(
    page_title="StudyOS - AI Exam OS",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #2563eb 100%);
    color: white;
    padding: 3rem 2rem;
    border-radius: 28px;
    box-shadow: 0 24px 60px rgba(37, 99, 235, 0.25);
    margin-bottom: 2rem;
}

.hero h1 {
    font-size: 3.2rem;
    line-height: 1.05;
    font-weight: 800;
    margin-bottom: 0.75rem;
}

.hero p {
    font-size: 1.15rem;
    color: #dbeafe;
    max-width: 850px;
}

.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 1.4rem;
    box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
    margin-bottom: 1rem;
}

.metric-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 1.5rem;
    box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
    text-align: center;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 800;
    color: #0f172a;
}

.metric-label {
    color: #64748b;
    font-weight: 600;
    margin-top: 0.25rem;
}

.badge {
    display: inline-block;
    padding: 0.45rem 0.8rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    margin: 0.15rem;
}

.badge-blue {
    background: #dbeafe;
    color: #1d4ed8;
}

.badge-green {
    background: #dcfce7;
    color: #15803d;
}

.badge-red {
    background: #fee2e2;
    color: #dc2626;
}

.badge-purple {
    background: #ede9fe;
    color: #6d28d9;
}

.module-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-left: 5px solid #2563eb;
    border-radius: 20px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.05);
}

.soft-section {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 1.3rem;
    border-radius: 20px;
}

.progress-wrap {
    background: #e2e8f0;
    height: 14px;
    border-radius: 999px;
    overflow: hidden;
    margin: 0.8rem 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #2563eb, #10b981);
    border-radius: 999px;
}

.small-muted {
    color: #64748b;
    font-size: 0.95rem;
}

.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    border: 1px solid #dbeafe !important;
}

[data-testid="stSidebar"] {
    background: #0f172a;
}

[data-testid="stSidebar"] * {
    color: white;
}

[data-testid="stSidebar"] .stTextInput label {
    color: white !important;
}

[data-testid="stSidebar"] .stMetric label {
    color: #cbd5e1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def init_session_state() -> None:
    defaults = {
        "current_page": "home",
        "api_key": "",
        "lecture_files": [],
        "lecture_text": "",
        "lecture_title": "",
        "exam_date": date.today() + timedelta(days=7),
        "days_left": 7,
        "summary": {},
        "key_points": [],
        "definitions": [],
        "flashcards": [],
        "quiz_questions": [],
        "topics": [],
        "weak_topics": [],
        "readiness": 0.0,
        "quiz_score": None,
        "quiz_submitted": False,
        "chat_history": [],
        "pdf_processed": False,
        "word_count": 0,
        "quiz_answers": {},
        "reviewed_flashcards": [],
        "completed_topics": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def get_secret_key() -> str:
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return ""


def get_openai_client():
    api_key = (
        st.session_state.get("api_key", "")
        or os.environ.get("OPENAI_API_KEY", "")
        or get_secret_key()
    )

    if not api_key or OpenAI is None:
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def has_real_ai() -> bool:
    return get_openai_client() is not None


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def extract_pdf_text(uploaded_file) -> str:
    try:
        uploaded_file.seek(0)
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        pages_text = []

        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages_text.append(page_text)
            except Exception:
                continue

        return clean_text("\n".join(pages_text))
    except Exception:
        return ""


def safe_json_parse(response: str, fallback: Any) -> Any:
    if not response:
        return fallback

    try:
        cleaned = response.strip()
        cleaned = re.sub(r"^```json", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"^```", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        first_brace = cleaned.find("{")
        first_bracket = cleaned.find("[")

        if first_brace == -1 and first_bracket == -1:
            return fallback

        if first_bracket != -1 and (first_brace == -1 or first_bracket < first_brace):
            cleaned = cleaned[first_bracket:]
        else:
            cleaned = cleaned[first_brace:]

        return json.loads(cleaned)
    except Exception:
        return fallback


def call_ai(prompt: str, system_prompt: str, max_tokens: int = 1200) -> str:
    client = get_openai_client()

    if client is None:
        return ""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.25,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception:
        return ""


def detect_topics_locally(text: str) -> List[str]:
    lower = text.lower()
    topic_keywords = {
        "Processes": ["process", "pcb", "program counter"],
        "Threads": ["thread", "multithreading", "race condition"],
        "CPU Scheduling": ["scheduling", "fcfs", "sjf", "round robin", "priority"],
        "Deadlocks": ["deadlock", "coffman", "banker"],
        "Memory Management": ["memory management", "paging", "page table", "frame"],
        "Virtual Memory": ["virtual memory", "demand paging", "thrashing"],
        "Page Replacement": ["fifo", "lru", "optimal replacement", "page replacement"],
    }

    topics = []
    for topic, keywords in topic_keywords.items():
        if any(keyword in lower for keyword in keywords):
            topics.append(topic)

    return topics or DEFAULT_TOPICS.copy()


def generate_local_workspace(text: str) -> Dict[str, Any]:
    topics = detect_topics_locally(text)

    definitions = [
        {
            "term": "Process",
            "definition": "A program in execution with its own state, resources, and Process Control Block.",
        },
        {
            "term": "Process Control Block",
            "definition": "A data structure that stores process state, program counter, CPU registers, memory information, and scheduling data.",
        },
        {
            "term": "Thread",
            "definition": "A lightweight unit of execution that shares resources with other threads in the same process.",
        },
        {
            "term": "Deadlock",
            "definition": "A situation where processes wait forever because each process holds a resource and waits for another.",
        },
        {
            "term": "Page Fault",
            "definition": "An event that occurs when a process accesses a page that is not currently in physical memory.",
        },
    ]

    flashcards = [
        {
            "front": "What is a process?",
            "back": "A process is a program in execution with its own state and PCB.",
        },
        {
            "front": "What does PCB store?",
            "back": "Process state, program counter, CPU registers, memory limits, open files, and scheduling information.",
        },
        {
            "front": "What are the four Coffman deadlock conditions?",
            "back": "Mutual exclusion, hold and wait, no preemption, and circular wait.",
        },
        {
            "front": "What is Round Robin scheduling?",
            "back": "A CPU scheduling algorithm where each process gets a fixed time quantum.",
        },
        {
            "front": "What is thrashing?",
            "back": "A condition where the system spends more time swapping pages than executing processes.",
        },
    ]

    quiz_questions = [
        {
            "question": "What is a process?",
            "choices": [
                "A program in execution",
                "A storage device",
                "A network protocol",
                "A compiler error",
            ],
            "correct": 0,
            "explanation": "A process is a program in execution.",
            "topic": "Processes",
        },
        {
            "question": "Which item is commonly stored in the PCB?",
            "choices": [
                "Monitor brightness",
                "Program counter",
                "Keyboard language",
                "Internet speed",
            ],
            "correct": 1,
            "explanation": "The PCB stores the program counter, process state, registers, and other process metadata.",
            "topic": "Processes",
        },
        {
            "question": "Which scheduling algorithm uses a time quantum?",
            "choices": ["FCFS", "SJF", "Round Robin", "FIFO page replacement"],
            "correct": 2,
            "explanation": "Round Robin gives each process a fixed time quantum.",
            "topic": "CPU Scheduling",
        },
        {
            "question": "How many Coffman conditions are required for deadlock?",
            "choices": ["2", "3", "4", "5"],
            "correct": 2,
            "explanation": "The four Coffman conditions are mutual exclusion, hold and wait, no preemption, and circular wait.",
            "topic": "Deadlocks",
        },
        {
            "question": "What happens during a page fault?",
            "choices": [
                "A process accesses a page not currently in memory",
                "The CPU overheats",
                "The monitor refreshes",
                "A file is deleted",
            ],
            "correct": 0,
            "explanation": "A page fault occurs when the referenced page is not in physical memory.",
            "topic": "Memory Management",
        },
    ]

    key_points = [
        "Operating systems manage hardware, software resources, and program execution.",
        "A process is represented internally using a Process Control Block.",
        "Threads allow lightweight execution within the same process.",
        "CPU scheduling decides which ready process receives CPU time.",
        "Round Robin is useful for time-sharing because it uses a time quantum.",
        "Deadlock requires four Coffman conditions to occur.",
        "Paging maps logical pages to physical memory frames.",
        "Virtual memory allows programs to run even when they exceed physical memory.",
        "Page replacement algorithms decide which page to remove when memory is full.",
    ]

    return {
        "summary": {
            "short_summary": "This lecture explains the core responsibilities of an operating system, including process management, CPU scheduling, deadlocks, memory management, virtual memory, and page replacement.",
            "detailed_summary": [
                "Processes are programs in execution and are tracked using Process Control Blocks.",
                "CPU scheduling algorithms such as FCFS, SJF, Round Robin, and Priority Scheduling determine how CPU time is assigned.",
                "Deadlocks occur when processes are stuck waiting for resources because the four Coffman conditions hold.",
                "Memory management uses paging, page tables, virtual memory, and page replacement to manage limited physical memory.",
            ],
            "key_takeaway": "For exams, focus on processes, scheduling, deadlocks, paging, virtual memory, and page replacement algorithms.",
        },
        "key_points": key_points,
        "definitions": definitions,
        "flashcards": flashcards,
        "quiz_questions": quiz_questions,
        "topics": topics,
    }


def generate_ai_workspace(text: str) -> Dict[str, Any]:
    fallback = generate_local_workspace(text)
    context = text[:12000]

    system_prompt = """
You are StudyOS AI. Generate study materials from university lecture content.
Return only valid JSON. Do not include markdown fences.
"""

    prompt = f"""
Create study materials from this lecture.

Return this exact JSON structure:
{{
  "summary": {{
    "short_summary": "...",
    "detailed_summary": ["...", "...", "..."],
    "key_takeaway": "..."
  }},
  "key_points": ["...", "..."],
  "definitions": [
    {{"term": "...", "definition": "..."}}
  ],
  "flashcards": [
    {{"front": "...", "back": "..."}}
  ],
  "quiz_questions": [
    {{
      "question": "...",
      "choices": ["...", "...", "...", "..."],
      "correct": 0,
      "explanation": "...",
      "topic": "..."
    }}
  ],
  "topics": ["...", "..."]
}}

Rules:
- Generate 8 to 12 key points.
- Generate 5 to 8 definitions.
- Generate 6 to 10 flashcards.
- Generate 5 MCQs.
- correct must be the zero-based index of the correct choice.
- Keep all content grounded in the lecture.

Lecture:
{context}
"""

    response = call_ai(prompt, system_prompt, max_tokens=1800)
    parsed = safe_json_parse(response, fallback)

    if not isinstance(parsed, dict):
        return fallback

    workspace = fallback.copy()

    for key in [
        "summary",
        "key_points",
        "definitions",
        "flashcards",
        "quiz_questions",
        "topics",
    ]:
        if parsed.get(key):
            workspace[key] = parsed[key]

    workspace["quiz_questions"] = normalize_quiz(workspace.get("quiz_questions", []))
    workspace["topics"] = workspace.get("topics") or detect_topics_locally(text)

    return workspace


def normalize_quiz(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []

    for q in questions:
        if not isinstance(q, dict):
            continue

        choices = q.get("choices", [])
        if not isinstance(choices, list) or len(choices) < 2:
            continue

        correct = q.get("correct", q.get("answer", 0))

        if isinstance(correct, str):
            if correct in choices:
                correct = choices.index(correct)
            else:
                correct = 0

        try:
            correct = int(correct)
        except Exception:
            correct = 0

        correct = max(0, min(correct, len(choices) - 1))

        normalized.append(
            {
                "question": str(q.get("question", "Question unavailable")),
                "choices": [str(c) for c in choices[:4]],
                "correct": correct,
                "explanation": str(q.get("explanation", "Review the related lecture section.")),
                "topic": str(q.get("topic", "General")),
            }
        )

    return normalized or generate_local_workspace(SAMPLE_LECTURE)["quiz_questions"]


def process_lecture_text(title: str, text: str, files_info: List[Dict[str, Any]] | None = None) -> None:
    text = clean_text(text)

    if not text or len(text.split()) < 20:
        text = SAMPLE_LECTURE
        title = "Sample Operating Systems Lecture"

    st.session_state["lecture_text"] = text
    st.session_state["lecture_title"] = title
    st.session_state["word_count"] = len(text.split())
    st.session_state["lecture_files"] = files_info or []
    st.session_state["days_left"] = max(0, (st.session_state["exam_date"] - date.today()).days)

    workspace = generate_ai_workspace(text)

    st.session_state["summary"] = workspace["summary"]
    st.session_state["key_points"] = workspace["key_points"]
    st.session_state["definitions"] = workspace["definitions"]
    st.session_state["flashcards"] = workspace["flashcards"]
    st.session_state["quiz_questions"] = workspace["quiz_questions"]
    st.session_state["topics"] = workspace["topics"]
    st.session_state["weak_topics"] = workspace["topics"][:2]
    st.session_state["completed_topics"] = max(1, len(workspace["topics"]) // 3)
    st.session_state["quiz_score"] = None
    st.session_state["quiz_answers"] = {}
    st.session_state["quiz_submitted"] = False
    st.session_state["reviewed_flashcards"] = []
    st.session_state["readiness"] = calculate_readiness()
    st.session_state["pdf_processed"] = True


def calculate_readiness() -> float:
    topics = st.session_state.get("topics", [])
    total_topics = max(1, len(topics))
    completed_topics = len(st.session_state.get("reviewed_flashcards", []))
    completed_topics = max(st.session_state.get("completed_topics", 0), completed_topics)
    quiz_score = st.session_state.get("quiz_score")

    if quiz_score is None:
        quiz_score = 60.0

    days_left = st.session_state.get("days_left", 7)
    weak_topics = st.session_state.get("weak_topics", [])

    topic_completion = min(1.0, completed_topics / total_topics)
    quiz_component = max(0.0, min(1.0, quiz_score / 100.0))

    if days_left >= 7:
        time_component = 1.0
    elif days_left >= 3:
        time_component = 0.75
    elif days_left >= 1:
        time_component = 0.55
    else:
        time_component = 0.35

    weakness_penalty = min(0.15, len(weak_topics) * 0.04)

    readiness = (
        topic_completion * 35
        + quiz_component * 40
        + time_component * 10
        + 15
        - weakness_penalty * 100
    )

    return round(max(0.0, min(100.0, readiness)), 1)


def get_next_best_action() -> str:
    weak_topics = st.session_state.get("weak_topics", [])
    topics = st.session_state.get("topics", DEFAULT_TOPICS)
    days_left = st.session_state.get("days_left", 7)

    target = weak_topics[0] if weak_topics else topics[0] if topics else "your weakest topic"

    if days_left <= 1:
        return f"Review {target} for 25 minutes, then take a short quiz and revise only wrong answers."
    if days_left <= 3:
        return f"Crash plan: study {target} for 25 minutes, review flashcards for 15 minutes, then take a 5-question quiz."
    return f"Continue learning: review {target}, finish one module, and test yourself with a quiz."


def retrieve_relevant_context(question: str, lecture_text: str, max_chars: int = 10000) -> str:
    chunks = re.split(r"(?<=[.!?])\s+|\n+", lecture_text)
    question_terms = set(re.findall(r"[a-zA-Z]{4,}", question.lower()))

    scored = []
    for chunk in chunks:
        chunk = chunk.strip()
        if len(chunk) < 30:
            continue
        terms = set(re.findall(r"[a-zA-Z]{4,}", chunk.lower()))
        score = len(question_terms.intersection(terms))
        if score > 0:
            scored.append((score, chunk))

    scored.sort(reverse=True, key=lambda item: item[0])

    selected = " ".join(chunk for _, chunk in scored[:12])
    if not selected:
        selected = lecture_text[:max_chars]

    return selected[:max_chars]


def local_chat_answer(question: str, lecture_text: str) -> str:
    lower = question.lower()

    topic_answers = {
        "deadlock": "According to the lecture, deadlock happens when processes wait forever because each process is holding a resource and waiting for another. The four Coffman conditions are mutual exclusion, hold and wait, no preemption, and circular wait.",
        "process": "According to the lecture, a process is a program in execution. The operating system tracks each process using a Process Control Block that stores state, program counter, registers, memory data, and scheduling information.",
        "pcb": "The PCB, or Process Control Block, stores process state, program counter, CPU registers, memory limits, open files, scheduling information, and accounting information.",
        "thread": "A thread is a lightweight unit of execution within a process. Threads share memory and resources with other threads in the same process.",
        "scheduling": "CPU scheduling decides which ready process receives the CPU next. The lecture mentions FCFS, SJF, Round Robin, and Priority Scheduling.",
        "round robin": "Round Robin scheduling gives each process a fixed time quantum. It is commonly used in time-sharing systems.",
        "memory": "Memory management controls how processes are loaded into memory. The lecture discusses paging, page tables, page faults, virtual memory, and page replacement.",
        "virtual": "Virtual memory allows programs to run even if they are larger than physical memory. Demand paging loads pages only when needed.",
        "page": "Paging divides logical memory into pages and physical memory into frames. A page table maps pages to frames.",
    }

    for keyword, answer in topic_answers.items():
        if keyword in lower:
            return answer

    topics = ", ".join(st.session_state.get("topics", DEFAULT_TOPICS))
    return f"I could not find that clearly in the uploaded lecture. Try asking about one of these detected topics: {topics}."


def chat_answer(question: str) -> str:
    lecture_text = st.session_state.get("lecture_text") or SAMPLE_LECTURE
    context = retrieve_relevant_context(question, lecture_text)

    system_prompt = """
You are StudyOS AI, a subject-scoped academic assistant.
Answer only using the uploaded lecture content.
If the answer is not clearly found in the lecture, say it is not clearly available in the uploaded material and suggest related topics.
Keep answers helpful, clear, and student-friendly.
"""

    prompt = f"""
Uploaded lecture context:
{context}

Student question:
{question}
"""

    response = call_ai(prompt, system_prompt, max_tokens=700)

    if response:
        return response

    return local_chat_answer(question, lecture_text)


def render_hero() -> None:
    st.markdown(
        """
<div class="hero">
    <div class="badge badge-green">Lecture Grounded</div>
    <div class="badge badge-blue">AI Workspace</div>
    <div class="badge badge-purple">Crash Mode</div>
    <h1>StudyOS</h1>
    <p>Your AI Exam Operating System. Upload lectures, generate study materials, detect weak topics, and turn exam panic into a clear plan.</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_metric_card(value: str, label: str, badge_class: str = "") -> None:
    st.markdown(
        f"""
<div class="metric-card">
    <div class="metric-value">{value}</div>
    <div class="metric-label">{label}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 📚 StudyOS")
        st.caption("From exam panic to a clear plan.")

        pages = {
            "🏠 Home": "home",
            "📤 Upload Lectures": "upload",
            "📊 Learning Dashboard": "dashboard",
            "📖 AI Workspace": "workspace",
            "🚀 Crash Mode": "crash",
            "🧘 Calm Dashboard": "calm",
            "💬 AI Tutor Chat": "chat",
            "❓ Quiz": "quiz",
            "🃏 Flashcards": "flashcards",
            "🗓️ Study Plan": "plan",
        }

        for label, key in pages.items():
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state["current_page"] = key
                st.rerun()

        st.divider()

        st.markdown("### 🔑 OpenAI")
        api_key = st.text_input(
            "Optional API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            help="The app works without this using demo mode.",
        )

        if api_key != st.session_state.get("api_key", ""):
            st.session_state["api_key"] = api_key
            st.rerun()

        if has_real_ai():
            st.success("Real AI Active")
            st.caption(MODEL_NAME)
        else:
            st.info("Demo Mode")

        if st.session_state.get("pdf_processed"):
            st.divider()
            st.metric("Readiness", f"{st.session_state['readiness']:.0f}%")
            st.metric("Days Left", st.session_state["days_left"])


def page_home() -> None:
    render_hero()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
<div class="card">
    <h3>📤 PDF to Workspace</h3>
    <p>Upload one or more lecture PDFs and generate summaries, definitions, flashcards, and quizzes.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
<div class="card">
    <h3>🚀 Crash Mode</h3>
    <p>When the exam is close, StudyOS removes the long plan and prioritizes what matters most.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
<div class="card">
    <h3>🧘 Calm Dashboard</h3>
    <p>See days left, readiness score, weak topics, and your next best study action.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("## The transformation")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
<div class="soft-section">
    <h3 style="color:#dc2626;">Before</h3>
    <ul>
        <li>Scattered PDFs</li>
        <li>Manual flashcards</li>
        <li>No readiness signal</li>
        <li>Exam panic</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
<div class="soft-section">
    <h3 style="color:#15803d;">After StudyOS</h3>
    <ul>
        <li>Generated study workspace</li>
        <li>Weak topics detected</li>
        <li>Readiness score</li>
        <li>Exact next action</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )

    if st.button("Start Demo", type="primary"):
        st.session_state["current_page"] = "upload"
        st.rerun()


def page_upload() -> None:
    render_hero()
    st.markdown("## 📤 Upload Lectures")

    col1, col2 = st.columns([2, 1])

    with col1:
        course_title = st.text_input(
            "Course / Subject Name",
            value=st.session_state.get("lecture_title") or "Operating Systems",
        )
        uploaded_files = st.file_uploader(
            "Upload lecture PDFs",
            type=["pdf"],
            accept_multiple_files=True,
        )

    with col2:
        st.session_state["exam_date"] = st.date_input(
            "Exam Date",
            value=st.session_state.get("exam_date", date.today() + timedelta(days=7)),
        )
        st.session_state["days_left"] = max(
            0, (st.session_state["exam_date"] - date.today()).days
        )
        st.metric("Days Left", st.session_state["days_left"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Use Sample Operating Systems Lecture", use_container_width=True):
            with st.spinner("Generating StudyOS workspace..."):
                process_lecture_text(
                    "Operating Systems",
                    SAMPLE_LECTURE,
                    files_info=[{"name": "sample_operating_systems.txt", "words": len(SAMPLE_LECTURE.split())}],
                )
            st.success("Sample workspace generated.")
            st.balloons()
            st.session_state["current_page"] = "dashboard"
            st.rerun()

    with col2:
        process_disabled = not uploaded_files
        if st.button(
            "Generate My StudyOS Workspace",
            type="primary",
            use_container_width=True,
            disabled=process_disabled,
        ):
            full_text_parts = []
            files_info = []

            with st.spinner("Reading your lecture PDFs..."):
                for uploaded_file in uploaded_files:
                    text = extract_pdf_text(uploaded_file)
                    words = len(text.split()) if text else 0

                    files_info.append({"name": uploaded_file.name, "words": words})

                    if words > 0:
                        full_text_parts.append(f"\n\n--- {uploaded_file.name} ---\n{text}")

            full_text = "\n".join(full_text_parts)

            if len(full_text.split()) < 20:
                st.warning(
                    "This PDF appears to contain scanned images or very little extractable text. Loading sample content so the demo continues."
                )
                full_text = SAMPLE_LECTURE
                course_title = "Sample Operating Systems Lecture"

            with st.spinner("Generating summaries, flashcards, quiz, and readiness score..."):
                process_lecture_text(course_title, full_text, files_info)

            st.success("Workspace generated successfully.")
            st.balloons()
            st.session_state["current_page"] = "dashboard"
            st.rerun()

    if st.session_state.get("lecture_files"):
        st.markdown("### Uploaded files")
        st.dataframe(pd.DataFrame(st.session_state["lecture_files"]), use_container_width=True)

    if st.session_state.get("pdf_processed"):
        st.success(
            f"Workspace ready: {st.session_state['word_count']:,} words processed."
        )


def page_dashboard() -> None:
    if not st.session_state.get("pdf_processed"):
        st.warning("Upload lectures first or use the sample lecture.")
        return

    render_hero()
    st.markdown(f"## 📊 {st.session_state['lecture_title']} Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(str(st.session_state["days_left"]), "Days Left")
    with col2:
        render_metric_card(f"{st.session_state['readiness']:.0f}%", "Readiness")
    with col3:
        render_metric_card(str(len(st.session_state["topics"])), "Detected Topics")
    with col4:
        render_metric_card(str(len(st.session_state["weak_topics"])), "Weak Topics")

    readiness = st.session_state["readiness"]
    st.markdown(
        f"""
<div class="card">
    <h3>Progress</h3>
    <div class="progress-wrap">
        <div class="progress-fill" style="width:{readiness}%"></div>
    </div>
    <p class="small-muted">Your readiness is based on topics, quiz performance, weak areas, and time left.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    mode_badge = (
        '<span class="badge badge-red">Crash Mode Active</span>'
        if st.session_state["days_left"] <= 3
        else '<span class="badge badge-green">Organized Mode</span>'
    )
    st.markdown(mode_badge, unsafe_allow_html=True)

    st.markdown("### Continue Learning")
    st.markdown(
        f"""
<div class="module-card">
    <h4>🎯 Next Best Study Action</h4>
    <p>{get_next_best_action()}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Weak Areas")
    for topic in st.session_state["weak_topics"]:
        st.markdown(f'<span class="badge badge-red">{topic}</span>', unsafe_allow_html=True)


def page_workspace() -> None:
    if not st.session_state.get("pdf_processed"):
        st.warning("Upload lectures first or use the sample lecture.")
        return

    render_hero()
    st.markdown("## 📖 AI Workspace")
    st.markdown('<span class="badge badge-purple">AI Generated</span>', unsafe_allow_html=True)

    summary = st.session_state.get("summary", {})
    if not isinstance(summary, dict):
        summary = {"short_summary": str(summary), "detailed_summary": [], "key_takeaway": ""}

    tabs = st.tabs(
        [
            "Summary",
            "Key Points",
            "Definitions",
            "Likely Exam Questions",
            "Rapid Review",
        ]
    )

    with tabs[0]:
        st.markdown("### Short Summary")
        st.markdown(summary.get("short_summary", "No summary available."))

        st.markdown("### Detailed Summary")
        for item in summary.get("detailed_summary", []):
            st.markdown(f"- {item}")

        st.markdown("### Key Takeaway")
        st.info(summary.get("key_takeaway", "Focus on the detected weak topics."))

    with tabs[1]:
        for point in st.session_state.get("key_points", []):
            st.markdown(f'<div class="module-card">{point}</div>', unsafe_allow_html=True)

    with tabs[2]:
        for item in st.session_state.get("definitions", []):
            st.markdown(
                f"""
<div class="module-card">
    <h4>{item.get("term", "Term")}</h4>
    <p>{item.get("definition", "Definition unavailable.")}</p>
</div>
""",
                unsafe_allow_html=True,
            )

    with tabs[3]:
        for q in st.session_state.get("quiz_questions", [])[:5]:
            st.markdown(f"- **{q['topic']}:** {q['question']}")

    with tabs[4]:
        st.markdown("### One-page rapid revision")
        for topic in st.session_state.get("topics", []):
            st.markdown(f"- Review **{topic}** and test yourself with one short question.")


def page_crash() -> None:
    if not st.session_state.get("pdf_processed"):
        st.warning("Upload lectures first or use the sample lecture.")
        return

    render_hero()
    st.markdown("## 🚀 Crash Mode")

    if st.session_state["days_left"] <= 3:
        st.markdown(
            '<span class="badge badge-red">Crash Mode Activated</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="card">
    <h3>Your exam is close.</h3>
    <p>StudyOS removed the long plan and prioritized the most important topics.</p>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown("### Critical Topics")
        critical_topics = st.session_state.get("weak_topics") or st.session_state.get("topics", [])[:3]
        for topic in critical_topics:
            st.markdown(f'<span class="badge badge-red">{topic}</span>', unsafe_allow_html=True)

        st.markdown("### Next 2 Hours")
        st.markdown(
            f"""
<div class="module-card">
    <ul>
        <li>25 min: Review {critical_topics[0] if critical_topics else "weakest topic"}</li>
        <li>5 min: Break</li>
        <li>20 min: Flashcards</li>
        <li>25 min: Take quiz</li>
        <li>20 min: Review wrong answers</li>
    </ul>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="badge badge-green">Organized Mode</span>',
            unsafe_allow_html=True,
        )
        st.info("Crash Mode activates automatically when the exam is 1–3 days away.")
        page_plan(show_header=False)


def page_calm() -> None:
    if not st.session_state.get("pdf_processed"):
        process_lecture_text(
            "Operating Systems",
            SAMPLE_LECTURE,
            files_info=[{"name": "sample_operating_systems.txt", "words": len(SAMPLE_LECTURE.split())}],
        )

    render_hero()
    st.markdown("## 🧘 Calm Dashboard")

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card(str(st.session_state["days_left"]), "Days Until Exam")
    with col2:
        render_metric_card(f"{st.session_state['readiness']:.0f}%", "Ready")
    with col3:
        render_metric_card(str(len(st.session_state["weak_topics"])), "Topics Remaining")

    readiness = st.session_state["readiness"]
    st.markdown(
        f"""
<div class="card">
    <h3>The panic becomes a plan.</h3>
    <div class="progress-wrap">
        <div class="progress-fill" style="width:{readiness}%"></div>
    </div>
    <h4>Next Best Study Action</h4>
    <p>{get_next_best_action()}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Today’s Plan")
    plan = [
        "25 min: Review weakest topic",
        "5 min: Break",
        "15 min: Flashcards",
        "10 min: Quiz wrong answers",
    ]
    for item in plan:
        st.markdown(f"- {item}")


def page_chat() -> None:
    if not st.session_state.get("pdf_processed"):
        st.info("No lecture uploaded yet. The chat will use the sample Operating Systems lecture.")
        if not st.session_state.get("lecture_text"):
            st.session_state["lecture_text"] = SAMPLE_LECTURE
            st.session_state["topics"] = DEFAULT_TOPICS.copy()

    render_hero()
    st.markdown("## 💬 AI Tutor Chat")
    st.caption("Answers are grounded in your uploaded lecture content.")

    if not has_real_ai():
        st.info("Demo mode: using local lecture-grounded answers. Add an OpenAI key for real AI responses.")

    suggestions = st.session_state.get("topics", DEFAULT_TOPICS)[:5]
    st.markdown("Suggested topics:")
    cols = st.columns(min(5, len(suggestions)))
    for i, topic in enumerate(suggestions):
        with cols[i]:
            if st.button(topic, key=f"suggest_{topic}"):
                st.session_state["chat_history"].append({"role": "user", "content": f"Explain {topic}"})
                st.session_state["chat_history"].append({"role": "assistant", "content": chat_answer(f"Explain {topic}")})
                st.rerun()

    for message in st.session_state.get("chat_history", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask anything from your lecture...")

    if prompt:
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        response = chat_answer(prompt)
        st.session_state["chat_history"].append({"role": "assistant", "content": response})

        st.rerun()


def page_quiz() -> None:
    if not st.session_state.get("pdf_processed"):
        st.warning("Upload lectures first or use the sample lecture.")
        return

    render_hero()
    st.markdown("## ❓ Quiz & Weakness Detection")

    if st.button("Reset Quiz"):
        st.session_state["quiz_score"] = None
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_submitted"] = False
        st.rerun()

    questions = st.session_state.get("quiz_questions", [])
    if not questions:
        st.warning("No quiz questions available.")
        return

    if st.session_state.get("quiz_score") is None:
        answers = {}

        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                st.markdown(f"### Q{i + 1}: {q['question']}")
                selected = st.radio(
                    "Choose one answer:",
                    options=list(range(len(q["choices"]))),
                    format_func=lambda idx, choices=q["choices"]: choices[idx],
                    key=f"quiz_q_{i}",
                )
                answers[i] = selected

            submitted = st.form_submit_button("Submit Quiz", type="primary")

        if submitted:
            correct = 0
            wrong_topics = []

            for i, selected_idx in answers.items():
                q = questions[i]
                if selected_idx == q["correct"]:
                    correct += 1
                else:
                    wrong_topics.append(q["topic"])

            score = round((correct / len(questions)) * 100, 1)
            st.session_state["quiz_score"] = score
            st.session_state["quiz_answers"] = answers
            st.session_state["quiz_submitted"] = True

            if wrong_topics:
                st.session_state["weak_topics"] = list(dict.fromkeys(wrong_topics))
            else:
                st.session_state["weak_topics"] = []

            st.session_state["completed_topics"] = max(
                st.session_state.get("completed_topics", 0),
                len(st.session_state.get("topics", [])) - len(st.session_state["weak_topics"]),
            )
            st.session_state["readiness"] = calculate_readiness()
            st.rerun()

    else:
        score = st.session_state["quiz_score"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Quiz Score", f"{score:.0f}%")
        with col2:
            st.metric("Updated Readiness", f"{st.session_state['readiness']:.0f}%")

        st.markdown("### Review")
        for i, q in enumerate(questions):
            user_choice = st.session_state["quiz_answers"].get(i)
            is_correct = user_choice == q["correct"]
            icon = "✅" if is_correct else "❌"
            st.markdown(f"**{icon} Q{i + 1}: {q['question']}**")
            if user_choice is not None:
                st.markdown(f"Your answer: {q['choices'][user_choice]}")
            st.markdown(f"Correct answer: {q['choices'][q['correct']]}")
            st.caption(q["explanation"])

        if st.button("Go to Calm Dashboard", type="primary"):
            st.session_state["current_page"] = "calm"
            st.rerun()


def page_flashcards() -> None:
    if not st.session_state.get("pdf_processed"):
        st.warning("Upload lectures first or use the sample lecture.")
        return

    render_hero()
    st.markdown("## 🃏 Flashcards")

    flashcards = st.session_state.get("flashcards", [])
    reviewed = set(st.session_state.get("reviewed_flashcards", []))

    st.progress(len(reviewed) / max(1, len(flashcards)))

    for i, card in enumerate(flashcards):
        with st.expander(f"Card {i + 1}: {card.get('front', 'Question')}"):
            st.markdown(f"**Answer:** {card.get('back', 'Answer unavailable.')}")
            if i not in reviewed:
                if st.button("Mark as Reviewed", key=f"review_card_{i}"):
                    st.session_state["reviewed_flashcards"].append(i)
                    st.session_state["completed_topics"] = max(
                        st.session_state.get("completed_topics", 0),
                        len(st.session_state["reviewed_flashcards"]),
                    )
                    st.session_state["readiness"] = calculate_readiness()
                    st.rerun()
            else:
                st.success("Reviewed")


def page_plan(show_header: bool = True) -> None:
    if not st.session_state.get("pdf_processed"):
        st.warning("Upload lectures first or use the sample lecture.")
        return

    if show_header:
        render_hero()
        st.markdown("## 🗓️ Study Plan")

    topics = st.session_state.get("topics", DEFAULT_TOPICS)
    days_left = max(1, st.session_state.get("days_left", 7))

    if days_left <= 3:
        st.markdown("### Crash Study Plan")
        plan = [
            ("Today", f"Review {topics[0] if topics else 'core topics'} and complete flashcards."),
            ("Tonight", "Take quiz, identify wrong answers, and revise weak topics."),
            ("Tomorrow", "Rapid review of definitions and likely exam questions."),
            ("Exam Morning", "Read the one-page rapid revision sheet only."),
        ]
    else:
        st.markdown("### Organized Study Plan")
        plan = []
        for i, topic in enumerate(topics):
            day_num = (i % days_left) + 1
            plan.append((f"Day {day_num}", f"Study {topic}, review flashcards, and answer practice questions."))

    for day, task in plan:
        st.markdown(
            f"""
<div class="module-card">
    <h4>{day}</h4>
    <p>{task}</p>
</div>
""",
            unsafe_allow_html=True,
        )


def main() -> None:
    render_sidebar()

    page = st.session_state.get("current_page", "home")

    if page == "home":
        page_home()
    elif page == "upload":
        page_upload()
    elif page == "dashboard":
        page_dashboard()
    elif page == "workspace":
        page_workspace()
    elif page == "crash":
        page_crash()
    elif page == "calm":
        page_calm()
    elif page == "chat":
        page_chat()
    elif page == "quiz":
        page_quiz()
    elif page == "flashcards":
        page_flashcards()
    elif page == "plan":
        page_plan()
    else:
        st.session_state["current_page"] = "home"
        st.rerun()


if __name__ == "__main__":
    main()
