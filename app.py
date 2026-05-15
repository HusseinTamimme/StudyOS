import streamlit as st
import pandas as pd
from datetime import date, timedelta
from textwrap import dedent
from PyPDF2 import PdfReader


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyOS Demo",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SAFE HTML RENDERER
# ============================================================

def html(content: str):
    st.markdown(dedent(content).strip(), unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "exam_date" not in st.session_state:
    st.session_state.exam_date = date.today() + timedelta(days=2)

if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""

if "workspace_generated" not in st.session_state:
    st.session_state.workspace_generated = False

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 67

if "weak_topics" not in st.session_state:
    st.session_state.weak_topics = ["Deadlocks", "Memory Management"]


# ============================================================
# CUSTOM CSS
# ============================================================

html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

#MainMenu, footer, header {
    visibility: hidden;
}

[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top center, rgba(116, 87, 246, 0.13), transparent 34%),
        linear-gradient(180deg, #fbfaff 0%, #f7f8fc 100%);
}

.block-container {
    padding-top: 0rem;
    padding-left: 2.3rem;
    padding-right: 2.3rem;
    max-width: 1200px;
}

/* Navbar */
.navbar {
    height: 66px;
    background: rgba(255, 255, 255, 0.94);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid #ececf4;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.8rem;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999999;
    box-shadow: 0 8px 30px rgba(30, 30, 60, 0.04);
}

.logo-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7057ff, #9d7cff);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    font-weight: 900;
}

.logo-text {
    font-size: 22px;
    font-weight: 900;
    color: #222434;
    letter-spacing: -0.7px;
}

.logo-text span {
    color: #7357f6;
}

.nav-links {
    display: flex;
    gap: 12px;
}

.nav-link {
    padding: 9px 16px;
    border-radius: 12px;
    color: #85889a;
    font-size: 14px;
    font-weight: 800;
}

.nav-link-active {
    background: #f0edff;
    color: #7357f6;
}

.user-wrap {
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-text {
    text-align: right;
    line-height: 1.1;
}

.user-name {
    font-size: 13px;
    color: #252737;
    font-weight: 900;
}

.user-plan {
    font-size: 11px;
    color: #9a9caf;
    font-weight: 700;
}

.avatar {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #7057ff, #9d7cff);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 13px;
}

/* Hero */
.hero {
    margin-top: 110px;
    text-align: center;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #f0edff;
    color: #7357f6;
    padding: 8px 15px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 18px;
}

.hero-title {
    font-size: 52px;
    line-height: 1.08;
    font-weight: 900;
    color: #232536;
    margin-bottom: 18px;
    letter-spacing: -2px;
}

.gradient-text {
    background: linear-gradient(135deg, #6d55ff, #9f7cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 18px;
    color: #85889a;
    max-width: 760px;
    margin: 0 auto 36px auto;
    line-height: 1.7;
    font-weight: 700;
}

/* General Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid #ececf4;
    border-radius: 28px;
    box-shadow: 0 20px 55px rgba(40, 40, 70, 0.06);
}

.section-card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid #ececf4;
    border-radius: 28px;
    padding: 28px;
    box-shadow: 0 20px 55px rgba(40, 40, 70, 0.06);
    margin-top: 30px;
}

.section-title {
    font-size: 28px;
    font-weight: 900;
    color: #252737;
    letter-spacing: -0.8px;
    margin-bottom: 8px;
}

.section-subtitle {
    font-size: 14px;
    color: #85889a;
    font-weight: 700;
    line-height: 1.6;
}

/* Calm Dashboard */
.calm-card {
    max-width: 940px;
    margin: 0 auto 34px auto;
    padding: 30px;
}

.calm-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    gap: 20px;
    margin-bottom: 22px;
}

.calm-title {
    font-size: 28px;
    font-weight: 900;
    color: #232536;
    letter-spacing: -0.8px;
}

.calm-subtitle {
    color: #85889a;
    font-weight: 700;
    margin-top: 5px;
}

.mode-pill {
    background: #fff4f4;
    color: #d92d20;
    border: 1px solid #ffd1d1;
    padding: 8px 13px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 900;
    white-space: nowrap;
}

.next-action {
    background: linear-gradient(135deg, #f4f1ff, #ffffff);
    border: 1px solid #e5ddff;
    border-radius: 22px;
    padding: 20px;
    margin-top: 18px;
}

.next-action-label {
    color: #7357f6;
    font-weight: 900;
    font-size: 13px;
    margin-bottom: 5px;
}

.next-action-text {
    color: #252737;
    font-size: 16px;
    font-weight: 800;
}

/* Upload */
.upload-shell {
    max-width: 940px;
    margin: 0 auto;
}

.upload-card {
    background: rgba(255, 255, 255, 0.96);
    border: 2px dashed #dfd7ff;
    border-radius: 30px;
    padding: 42px 34px;
    text-align: center;
    box-shadow: 0 28px 80px rgba(116, 87, 246, 0.10);
}

.upload-icon {
    width: 78px;
    height: 78px;
    border-radius: 24px;
    background: linear-gradient(135deg, #7057ff, #9d7cff);
    color: white;
    font-size: 35px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 22px auto;
    box-shadow: 0 18px 34px rgba(116, 87, 246, 0.24);
}

.upload-title {
    font-size: 24px;
    font-weight: 900;
    color: #252737;
    margin-bottom: 8px;
    letter-spacing: -0.4px;
}

.upload-desc {
    color: #9a9caf;
    font-size: 14px;
    font-weight: 700;
}

.privacy-note {
    color: #9a9caf;
    font-size: 12px;
    font-weight: 800;
    margin-top: 14px;
}

/* Feature Cards */
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    max-width: 940px;
    margin: 30px auto 0 auto;
}

.feature-card {
    background: rgba(255, 255, 255, 0.96);
    border-radius: 24px;
    padding: 24px;
    border: 1px solid #ececf4;
    box-shadow: 0 18px 44px rgba(40, 40, 70, 0.05);
}

.feature-icon {
    width: 46px;
    height: 46px;
    border-radius: 15px;
    background: #f0edff;
    color: #7357f6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 14px;
}

.feature-title {
    font-size: 17px;
    font-weight: 900;
    color: #252737;
    margin-bottom: 8px;
}

.feature-desc {
    font-size: 13px;
    color: #85889a;
    line-height: 1.55;
    font-weight: 650;
}

/* Mode Boxes */
.crash-box {
    background: linear-gradient(135deg, #fff4f4, #fffafa);
    border: 1px solid #ffd6d6;
    border-radius: 22px;
    padding: 22px;
    margin-top: 12px;
}

.crash-title {
    color: #d92d20;
    font-weight: 900;
    font-size: 19px;
    margin-bottom: 8px;
}

.success-box {
    background: linear-gradient(135deg, #effdf7, #f8fffc);
    border: 1px solid #c8f3df;
    border-radius: 22px;
    padding: 22px;
    margin-top: 12px;
}

.success-title {
    color: #039855;
    font-weight: 900;
    font-size: 19px;
    margin-bottom: 8px;
}

.mini-label {
    color: #7357f6;
    background: #f0edff;
    border-radius: 999px;
    padding: 6px 11px;
    font-size: 12px;
    font-weight: 900;
    display: inline-block;
    margin-bottom: 10px;
}

/* Streamlit Widgets */
[data-testid="stFileUploader"] {
    max-width: 530px;
    margin: 18px auto 0 auto;
}

[data-testid="stFileUploader"] label {
    display: none;
}

[data-testid="stFileUploader"] section {
    background: white;
    border: 1px solid #ececf4;
    border-radius: 18px;
}

[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #7057ff, #9d7cff) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 900 !important;
    padding: 0.65rem 1.25rem !important;
    box-shadow: 0 12px 24px rgba(116, 87, 246, 0.22);
}

.stMetric {
    background: white;
    border: 1px solid #ececf4;
    padding: 20px;
    border-radius: 22px;
    box-shadow: 0 14px 32px rgba(40, 40, 70, 0.05);
}

.stButton > button {
    background: linear-gradient(135deg, #7057ff, #9d7cff);
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 900;
    padding: 0.7rem 1.25rem;
    box-shadow: 0 12px 24px rgba(116, 87, 246, 0.18);
}

.stButton > button:hover {
    color: white;
    border: none;
    transform: translateY(-1px);
}

div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

hr {
    margin-top: 2rem;
    margin-bottom: 2rem;
}

/* Responsive */
@media (max-width: 900px) {
    .nav-links {
        display: none;
    }

    .hero-title {
        font-size: 38px;
    }

    .hero-subtitle {
        font-size: 15px;
    }

    .card-grid {
        grid-template-columns: 1fr;
    }

    .navbar {
        padding: 0 1.2rem;
    }

    .calm-header {
        flex-direction: column;
    }
}
</style>
""")


# ============================================================
# DEMO DATA
# ============================================================

LECTURE_TOPICS = [
    "Process Management",
    "CPU Scheduling",
    "Memory Management",
    "Deadlocks",
    "File Systems"
]

FLASHCARDS = [
    {
        "front": "What is a process?",
        "back": "A process is a program in execution. It includes the program code, current activity, memory, and system resources."
    },
    {
        "front": "What is CPU scheduling?",
        "back": "CPU scheduling decides which process gets CPU time next, helping improve system efficiency and responsiveness."
    },
    {
        "front": "What is a deadlock?",
        "back": "A deadlock happens when processes wait forever because each process holds a resource and waits for another."
    },
    {
        "front": "What is memory management?",
        "back": "Memory management controls how programs use RAM efficiently, safely, and without interfering with each other."
    }
]

QUIZ = [
    {
        "question": "Which concept describes a program in execution?",
        "options": ["Thread", "Process", "File", "Kernel"],
        "answer": "Process",
        "topic": "Process Management"
    },
    {
        "question": "Which scheduling algorithm gives each process a fixed time slice?",
        "options": ["FCFS", "SJF", "Round Robin", "Priority Scheduling"],
        "answer": "Round Robin",
        "topic": "CPU Scheduling"
    },
    {
        "question": "Deadlock occurs when processes...",
        "options": [
            "Finish too quickly",
            "Use too much memory",
            "Wait forever for resources",
            "Have no priority"
        ],
        "answer": "Wait forever for resources",
        "topic": "Deadlocks"
    }
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        return text.strip()

    except Exception:
        return ""


def days_until_exam():
    remaining = st.session_state.exam_date - date.today()
    return max(remaining.days, 0)


def calculate_readiness():
    if st.session_state.quiz_submitted:
        quiz_factor = st.session_state.quiz_score / 100
    else:
        quiz_factor = 0.67

    lecture_progress = 0.72
    weakness_penalty = len(st.session_state.weak_topics) * 0.035

    readiness = int(((lecture_progress * 0.6) + (quiz_factor * 0.4) - weakness_penalty) * 100)
    return max(min(readiness, 100), 0)


def current_mode():
    return "Crash Mode" if days_until_exam() <= 3 else "Organized Mode"


# ============================================================
# UI RENDER FUNCTIONS
# ============================================================

def render_navbar():
    html("""
    <div class="navbar">
        <div class="logo-wrap">
            <div class="logo-icon">🎓</div>
            <div class="logo-text">Study<span>OS</span></div>
        </div>

        <div class="nav-links">
            <div class="nav-link nav-link-active">Dashboard</div>
            <div class="nav-link">My Lectures</div>
            <div class="nav-link">Study Planner</div>
            <div class="nav-link">AI Chat</div>
        </div>

        <div class="user-wrap">
            <div class="user-text">
                <div class="user-name">Hussein T.</div>
                <div class="user-plan">Premium</div>
            </div>
            <div class="avatar">HT</div>
        </div>
    </div>
    """)


def render_hero():
    html("""
    <div class="hero">
        <div class="hero-badge">The Operating System for University Students</div>

        <div class="hero-title">
            Turn exam panic into<br>
            a clear <span class="gradient-text">study plan</span>
        </div>

        <div class="hero-subtitle">
            Upload lecture PDFs and StudyOS creates summaries, flashcards, quizzes,
            weakness detection, and a personalized exam plan in seconds.
        </div>
    </div>
    """)


def render_calm_dashboard():
    mode = current_mode()

    if mode == "Crash Mode":
        pill_text = "🚨 Crash Mode Active"
    else:
        pill_text = "✅ Organized Mode Active"

    html(f"""
    <div class="glass-card calm-card">
        <div class="calm-header">
            <div>
                <div class="calm-title">Calm Dashboard</div>
                <div class="calm-subtitle">
                    One screen that tells the student exactly where they stand.
                </div>
            </div>
            <div class="mode-pill">{pill_text}</div>
        </div>
    </div>
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Days Until Exam", f"{days_until_exam()} days")

    with col2:
        st.metric("Exam Readiness", f"{calculate_readiness()}%")

    with col3:
        st.metric("Topics Left", "2")

    html("""
    <div class="next-action">
        <div class="next-action-label">NEXT BEST ACTION</div>
        <div class="next-action-text">
            Review Deadlocks, then take a 5-question quiz before moving to File Systems.
        </div>
    </div>
    """)


def render_upload_area():
    html("""
    <div class="upload-shell">
        <div class="upload-card">
            <div class="upload-icon">☁️</div>
            <div class="upload-title">Upload your lecture PDF</div>
            <div class="upload-desc">
                StudyOS will generate a full study workspace from your material.
            </div>
            <div class="privacy-note">
                🛡 Demo mode · Supports lecture PDFs · Private processing
            </div>
        </div>
    </div>
    """)


def render_feature_cards():
    html("""
    <div class="card-grid">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">PDF to Workspace</div>
            <div class="feature-desc">
                Summaries, key points, flashcards, quizzes, and study plan from one upload.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon">🚨</div>
            <div class="feature-title">Smart Exam Mode</div>
            <div class="feature-desc">
                Automatically switches from organized planning to Crash Mode near the exam.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Weakness Detection</div>
            <div class="feature-desc">
                Tracks quiz mistakes and tells the student which topics to revisit first.
            </div>
        </div>
    </div>
    """)


def render_section(title, subtitle):
    html(f"""
    <div class="section-card">
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
    </div>
    """)


# ============================================================
# APP START
# ============================================================

render_navbar()
render_hero()
render_calm_dashboard()

st.markdown("<br>", unsafe_allow_html=True)

render_upload_area()

uploaded_file = st.file_uploader(
    "Upload lecture PDF",
    type=["pdf"],
    label_visibility="collapsed"
)

render_feature_cards()


# ============================================================
# PROCESS UPLOAD
# ============================================================

if uploaded_file is not None:
    with st.spinner("StudyOS is generating your workspace..."):
        extracted_text = extract_pdf_text(uploaded_file)
        st.session_state.uploaded_text = extracted_text
        st.session_state.workspace_generated = True

    st.success("Lecture processed successfully. Your study workspace is ready.")


# ============================================================
# DEMO WORKSPACE
# ============================================================

if st.session_state.workspace_generated:
    render_section(
        "Generated Study Workspace",
        "StudyOS analyzed the lecture and created everything the student needs to revise smarter."
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("Summaries", "1")

    with metric2:
        st.metric("Flashcards", "18")

    with metric3:
        st.metric("Quiz Questions", "10")

    with metric4:
        st.metric("Readiness", f"{calculate_readiness()}%")

    st.markdown("## 1. Generated Summary")

    st.write(
        """
        This lecture introduces key Operating Systems concepts including process management,
        CPU scheduling, memory management, deadlocks, and file systems. StudyOS identified
        the most exam-relevant definitions, comparisons, and likely question areas.
        """
    )

    if st.session_state.uploaded_text:
        with st.expander("Preview extracted lecture text"):
            st.write(st.session_state.uploaded_text[:1600])

    st.markdown("## 2. Key Points")

    st.markdown(
        """
        - A process is a program in execution.
        - CPU scheduling decides which process gets CPU time next.
        - Round Robin scheduling gives each process a fixed time slice.
        - Deadlock happens when processes wait forever for resources.
        - Memory management controls how programs use RAM safely and efficiently.
        """
    )

    st.markdown("## 3. Generated Flashcards")

    for card in FLASHCARDS:
        with st.expander(card["front"]):
            st.write(card["back"])

    st.markdown("## 4. Smart Exam Planner")

    st.session_state.exam_date = st.date_input(
        "Choose your exam date",
        value=st.session_state.exam_date
    )

    remaining_days = days_until_exam()

    st.metric("Time Remaining", f"{remaining_days} days")

    if remaining_days <= 3:
        html("""
        <div class="crash-box">
            <div class="crash-title">Crash Mode Activated</div>
            Your exam is close. StudyOS stops giving a long schedule and focuses only on
            high-impact topics, likely exam questions, and rapid revision.
        </div>
        """)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("### High-Priority Topics")
            st.markdown(
                """
                1. Deadlocks  
                2. CPU Scheduling  
                3. Memory Management  
                """
            )

        with col_b:
            st.markdown("### Rapid Revision Plan")
            st.markdown(
                """
                - Review Deadlocks summary  
                - Study generated flashcards  
                - Take the weakness quiz  
                - Revisit wrong-answer topics  
                """
            )

        st.markdown("### Likely Exam Questions")
        st.markdown(
            """
            - Explain the four necessary conditions for deadlock.
            - Compare FCFS, SJF, and Round Robin scheduling.
            - Explain the difference between paging and segmentation.
            """
        )

    else:
        html("""
        <div class="success-box">
            <div class="success-title">Organized Mode Activated</div>
            Your exam is not too close yet. StudyOS created a structured day-by-day plan.
        </div>
        """)

        plan_df = pd.DataFrame(
            {
                "Day": ["Day 1", "Day 2", "Day 3", "Day 4"],
                "Focus": [
                    "Process Management",
                    "CPU Scheduling",
                    "Memory Management",
                    "Deadlocks + Quiz"
                ],
                "Task": [
                    "Read summary and flashcards",
                    "Practice scheduling questions",
                    "Review definitions",
                    "Take quiz and revise weak topics"
                ]
            }
        )

        st.dataframe(plan_df, use_container_width=True)

    st.markdown("## 5. Quiz & Weakness Detection")

    answers = []

    with st.form("quiz_form"):
        for index, question in enumerate(QUIZ):
            selected_answer = st.radio(
                question["question"],
                question["options"],
                key=f"quiz_question_{index}"
            )
            answers.append(selected_answer)

        submitted = st.form_submit_button("Submit Quiz")

    if submitted:
        correct_count = 0
        weak_topics = []

        for selected_answer, question in zip(answers, QUIZ):
            if selected_answer == question["answer"]:
                correct_count += 1
            else:
                weak_topics.append(question["topic"])

        score = int((correct_count / len(QUIZ)) * 100)

        st.session_state.quiz_submitted = True
        st.session_state.quiz_score = score
        st.session_state.weak_topics = weak_topics

        st.metric("Quiz Score", f"{score}%")

        if weak_topics:
            st.warning("Weak topics detected:")
            for topic in weak_topics:
                st.write(f"- {topic}")
        else:
            st.success("Excellent. No weak topics detected.")

    st.markdown("### Weakness Profile")

    weakness_df = pd.DataFrame(
        {
            "Topic": [
                "Process Management",
                "CPU Scheduling",
                "Memory Management",
                "Deadlocks",
                "File Systems"
            ],
            "Status": [
                "Strong",
                "Medium",
                "Needs Review",
                "Weak",
                "Not Started"
            ],
            "Recommended Action": [
                "Quick review only",
                "Practice one more question",
                "Review definitions",
                "Revise immediately",
                "Start after weak topics"
            ]
        }
    )

    st.dataframe(weakness_df, use_container_width=True)

    st.markdown("## 6. Subject-Scoped AI Chat")

    st.info("Demo mode: this assistant answers as if it is grounded in the uploaded lecture.")

    user_question = st.text_input("Ask something from this lecture")

    if user_question:
        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            st.write(
                """
                Based on your uploaded Operating Systems lecture, this topic is important
                because it is connected to exam questions about process behavior, scheduling,
                memory usage, or deadlock conditions. Start by reviewing the definition, then
                test yourself using the generated flashcards.
                """
            )

        if st.button("Quiz me on this"):
            st.write("Mini quiz: Which method helps you test recall quickly?")
            st.radio(
                "Choose one:",
                ["Passive reading", "Flashcards", "Ignoring weak topics", "Only highlighting"],
                key="mini_quiz"
            )

else:
    st.markdown("<br><br>", unsafe_allow_html=True)

    html("""
    <div class="section-card">
        <div class="mini-label">Demo Story</div>
        <div class="section-title">The panic becomes a plan</div>
        <div class="section-subtitle">
            Upload a lecture PDF to show the full flow: generated summary, flashcards,
            Smart Exam Mode, Crash Mode, weakness detection, and subject-scoped AI chat.
        </div>
    </div>
    """)
