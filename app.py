import streamlit as st
import pandas as pd
from datetime import date
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
# This prevents random HTML code from appearing on screen.
# ============================================================

def html(content):
    st.markdown(dedent(content).strip(), unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "exam_date" not in st.session_state:
    st.session_state.exam_date = date.today()

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""


# ============================================================
# CUSTOM CSS
# ============================================================

html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

[data-testid="stSidebar"] {
    display: none;
}

[data-testid="collapsedControl"] {
    display: none;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top, rgba(124, 92, 255, 0.08), transparent 35%),
        linear-gradient(180deg, #fbfaff 0%, #f7f8fc 100%);
}

.block-container {
    padding-top: 0rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1200px;
}

/* Navbar */
.navbar {
    height: 64px;
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
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7457ff, #9d7cff);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 18px;
    font-weight: 800;
}

.logo-text {
    font-size: 21px;
    font-weight: 900;
    color: #232536;
    letter-spacing: -0.5px;
}

.logo-text span {
    color: #7357f6;
}

.nav-links {
    display: flex;
    align-items: center;
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
    color: #262837;
    font-weight: 900;
}

.user-plan {
    font-size: 11px;
    color: #9a9caf;
    font-weight: 700;
}

.avatar {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #7457ff, #9d7cff);
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
    margin-top: 112px;
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
    font-size: 54px;
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
    max-width: 740px;
    margin: 0 auto 38px auto;
    line-height: 1.7;
    font-weight: 700;
}

/* Calm Dashboard */
.dashboard-shell {
    max-width: 900px;
    margin: 0 auto 34px auto;
}

.dashboard-title {
    font-size: 26px;
    font-weight: 900;
    color: #232536;
    margin-bottom: 8px;
    text-align: center;
}

.dashboard-subtitle {
    color: #85889a;
    text-align: center;
    font-weight: 700;
    margin-bottom: 20px;
}

/* Upload card */
.upload-shell {
    max-width: 900px;
    margin: 0 auto;
}

.upload-card {
    background: rgba(255, 255, 255, 0.96);
    border: 2px dashed #dfd7ff;
    border-radius: 30px;
    padding: 56px 34px 34px 34px;
    text-align: center;
    box-shadow: 0 28px 80px rgba(116, 87, 246, 0.10);
}

.upload-icon {
    width: 82px;
    height: 82px;
    border-radius: 24px;
    background: linear-gradient(135deg, #7057ff, #9d7cff);
    color: white;
    font-size: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24px auto;
    box-shadow: 0 18px 34px rgba(116, 87, 246, 0.24);
}

.upload-title {
    font-size: 25px;
    font-weight: 900;
    color: #252737;
    margin-bottom: 8px;
    letter-spacing: -0.4px;
}

.upload-desc {
    color: #9a9caf;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 22px;
}

.privacy-note {
    color: #9a9caf;
    font-size: 12px;
    font-weight: 800;
    margin-top: 12px;
    text-align: center;
}

/* File uploader */
[data-testid="stFileUploader"] {
    max-width: 420px;
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

/* Feature cards */
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    max-width: 900px;
    margin: 34px auto 0 auto;
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

/* Section cards */
.section-card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid #ececf4;
    border-radius: 28px;
    padding: 28px;
    box-shadow: 0 18px 48px rgba(40, 40, 70, 0.05);
    margin-top: 30px;
}

.section-title {
    font-size: 27px;
    font-weight: 900;
    color: #252737;
    letter-spacing: -0.7px;
    margin-bottom: 8px;
}

.section-subtitle {
    font-size: 14px;
    color: #85889a;
    font-weight: 700;
    margin-bottom: 20px;
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

/* Streamlit widgets */
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
}
</style>
""")


# ============================================================
# DATA
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
        "back": "A process is a program in execution."
    },
    {
        "front": "What is CPU scheduling?",
        "back": "CPU scheduling decides which process gets CPU time next."
    },
    {
        "front": "What is a deadlock?",
        "back": "A deadlock happens when processes wait forever for resources held by each other."
    },
    {
        "front": "What is memory management?",
        "back": "Memory management controls how programs use RAM efficiently and safely."
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
        "question": "Which algorithm gives each process a fixed time slice?",
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
    today = date.today()
    remaining = st.session_state.exam_date - today
    return max(remaining.days, 0)


def calculate_readiness():
    base_progress = 0.64

    if st.session_state.quiz_submitted:
        quiz_factor = st.session_state.quiz_score / 100
    else:
        quiz_factor = 0.55

    readiness = int((base_progress * 0.6 + quiz_factor * 0.4) * 100)
    return readiness


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
            <div class="nav-link">Profile</div>
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
        <div class="hero-badge">AI-powered study workspace</div>

        <div class="hero-title">
            Transform lectures into your<br>
            complete <span class="gradient-text">study workspace</span>
        </div>

        <div class="hero-subtitle">
            Upload a PDF and get summaries, flashcards, quizzes, and a personalized study plan in seconds.
        </div>
    </div>
    """)


def render_calm_dashboard():
    html("""
    <div class="dashboard-shell">
        <div class="dashboard-title">Calm Dashboard</div>
        <div class="dashboard-subtitle">
            The student sees exactly where they stand before the exam.
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


def render_upload_card():
    html("""
    <div class="upload-shell">
        <div class="upload-card">
            <div class="upload-icon">☁️</div>
            <div class="upload-title">Drag & drop your lecture PDF</div>
            <div class="upload-desc">or click below to browse from your computer</div>
            <div class="privacy-note">🛡 Supports files up to 50MB · Encrypted & private</div>
        </div>
    </div>
    """)


def render_feature_cards():
    html("""
    <div class="card-grid">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Instant Summaries</div>
            <div class="feature-desc">
                Turn long lecture PDFs into clean summaries, definitions, and key points.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Smart Flashcards</div>
            <div class="feature-desc">
                Generate front/back flashcards directly from your actual lecture material.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Exam Readiness</div>
            <div class="feature-desc">
                Know how ready you are before the exam with clear progress signals.
            </div>
        </div>
    </div>
    """)


def render_section_header(title, subtitle):
    html(f"""
    <div class="section-card">
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
    </div>
    """)


# ============================================================
# MAIN APP
# ============================================================

render_navbar()
render_hero()
render_calm_dashboard()

st.markdown("<br>", unsafe_allow_html=True)

render_upload_card()

uploaded_file = st.file_uploader(
    "Upload lecture PDF",
    type=["pdf"],
    label_visibility="collapsed"
)

render_feature_cards()


# ============================================================
# BEFORE UPLOAD
# ============================================================

if uploaded_file is None:
    st.markdown("<br><br>", unsafe_allow_html=True)

    html("""
    <div class="section-card">
        <div class="mini-label">Demo Flow</div>
        <div class="section-title">Upload a lecture to begin</div>
        <div class="section-subtitle">
            After upload, StudyOS will show the generated summary, flashcards, quiz,
            Crash Mode, weakness detection, and subject AI chat.
        </div>
    </div>
    """)


# ============================================================
# AFTER UPLOAD
# ============================================================

if uploaded_file is not None:
    with st.spinner("StudyOS is generating your study workspace..."):
        extracted_text = extract_pdf_text(uploaded_file)
        st.session_state.uploaded_text = extracted_text

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("Lecture processed successfully. Your study workspace is ready.")

    render_section_header(
        "Generated Study Workspace",
        "StudyOS analyzed your lecture and created summaries, flashcards, quiz questions, and an exam plan."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Exam Readiness", f"{calculate_readiness()}%")

    with col2:
        st.metric("Flashcards Created", "18")

    with col3:
        st.metric("Quiz Questions", "10")

    st.markdown("## Generated Summary")

    st.write(
        """
        This lecture introduces important course concepts and highlights the material most likely
        to matter during exam preparation. StudyOS extracted the main ideas, definitions,
        and review points from the uploaded file.
        """
    )

    if st.session_state.uploaded_text:
        with st.expander("Preview extracted lecture text"):
            preview_text = st.session_state.uploaded_text[:1500]
            st.write(preview_text)

    st.markdown("## Key Points")

    st.markdown(
        """
        - The lecture contains several exam-relevant definitions.
        - The most important concepts were extracted automatically.
        - Flashcards were generated from the main ideas.
        - Quiz questions were created to test understanding.
        - The study plan changes depending on the exam date.
        """
    )

    st.markdown("## Generated Flashcards")

    for card in FLASHCARDS:
        with st.expander(card["front"]):
            st.write(card["back"])

    st.markdown("## Smart Exam Planner")

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
            Your exam is close. StudyOS is now prioritizing high-impact topics, likely exam questions,
            and rapid revision instead of a full long-term schedule.
        </div>
        """)

        st.markdown("### High-Priority Topics")
        st.markdown(
            """
            1. Deadlocks  
            2. CPU Scheduling  
            3. Memory Management  
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
            Your exam is not too close yet. StudyOS created a structured day-by-day study plan.
        </div>
        """)

        plan_df = pd.DataFrame(
            {
                "Day": ["Day 1", "Day 2", "Day 3", "Day 4"],
                "Focus": [
                    "Process Management",
                    "CPU Scheduling",
                    "Memory Management",
                    "Deadlocks"
                ],
                "Task": [
                    "Read summary and review flashcards",
                    "Practice scheduling questions",
                    "Review memory definitions",
                    "Take quiz and revise weak topics"
                ]
            }
        )

        st.dataframe(plan_df, use_container_width=True)

    st.markdown("## Quiz & Weakness Detection")

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

        st.metric("Quiz Score", f"{score}%")

        if weak_topics:
            st.warning("Weak topics detected:")
            for topic in weak_topics:
                st.write(f"- {topic}")
        else:
            st.success("Excellent. No weak topics detected.")

    st.markdown("## Weakness Profile")

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
                "Good",
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

    st.markdown("## Subject-Scoped AI Chat")

    st.info("Demo mode: this chat gives simulated answers based on the uploaded lecture.")

    user_question = st.text_input("Ask something from this lecture")

    if user_question:
        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            st.write(
                """
                Based on your uploaded lecture, this topic is important because it connects directly
                to the main exam concepts. You should review the definition first, then test yourself
                using flashcards and quiz questions.
                """
            )

        if st.button("Quiz me on this"):
            st.write("Mini quiz: Which study method helps you test recall quickly?")
            st.radio(
                "Choose one:",
                ["Passive reading", "Flashcards", "Ignoring weak topics", "Only highlighting"],
                key="mini_quiz"
            )
