import streamlit as st
import pandas as pd
from datetime import date, timedelta
from PyPDF2 import PdfReader


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyOS Demo",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #faf9ff 0%, #f7f8fc 100%);
    }

    .main-title {
        font-size: 52px;
        font-weight: 900;
        text-align: center;
        color: #232536;
        margin-top: 20px;
        line-height: 1.1;
    }

    .gradient-text {
        background: linear-gradient(90deg, #6d5dfc, #9b7cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #777b8f;
        max-width: 780px;
        margin: 15px auto 35px auto;
        line-height: 1.6;
        font-weight: 500;
    }

    .badge {
        width: fit-content;
        margin: 10px auto;
        padding: 8px 16px;
        border-radius: 999px;
        background: #f0edff;
        color: #7357f6;
        font-weight: 800;
        font-size: 13px;
    }

    .section-card {
        background: white;
        padding: 28px;
        border-radius: 24px;
        border: 1px solid #ececf4;
        box-shadow: 0 14px 35px rgba(40, 40, 70, 0.05);
        margin-bottom: 25px;
    }

    .section-heading {
        font-size: 26px;
        font-weight: 900;
        color: #252737;
        margin-bottom: 8px;
    }

    .section-description {
        color: #777b8f;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 20px;
    }

    .feature-box {
        background: white;
        padding: 22px;
        border-radius: 22px;
        border: 1px solid #ececf4;
        box-shadow: 0 12px 28px rgba(40, 40, 70, 0.04);
        height: 100%;
    }

    .feature-title {
        font-weight: 900;
        color: #252737;
        font-size: 18px;
        margin-bottom: 8px;
    }

    .feature-text {
        color: #777b8f;
        font-size: 14px;
        line-height: 1.5;
    }

    .crash-box {
        background: #fff4f4;
        border: 1px solid #ffd2d2;
        color: #9f1d1d;
        padding: 20px;
        border-radius: 18px;
        font-weight: 700;
    }

    .organized-box {
        background: #f0fff7;
        border: 1px solid #bdeed4;
        color: #087443;
        padding: 20px;
        border-radius: 18px;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #ececf4;
        box-shadow: 0 12px 28px rgba(40, 40, 70, 0.04);
    }

    .stButton > button {
        background: linear-gradient(90deg, #6d5dfc, #9b7cff);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 0.7rem 1.2rem;
        font-weight: 800;
    }

    .stButton > button:hover {
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""

if "exam_date" not in st.session_state:
    st.session_state.exam_date = date.today() + timedelta(days=2)

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = None

if "weak_topics" not in st.session_state:
    st.session_state.weak_topics = ["Deadlocks", "Memory Management"]


# ============================================================
# DEMO DATA
# ============================================================

TOPICS = [
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
        "front": "What is deadlock?",
        "back": "Deadlock happens when processes wait forever for resources held by each other."
    },
    {
        "front": "What is memory management?",
        "back": "Memory management controls how programs use RAM safely and efficiently."
    }
]

QUIZ = [
    {
        "question": "Which concept describes a program in execution?",
        "options": ["Thread", "Process", "File", "Compiler"],
        "answer": "Process",
        "topic": "Process Management"
    },
    {
        "question": "Which scheduling algorithm uses a fixed time slice?",
        "options": ["FCFS", "SJF", "Round Robin", "Priority Scheduling"],
        "answer": "Round Robin",
        "topic": "CPU Scheduling"
    },
    {
        "question": "Deadlock means that processes...",
        "options": [
            "Finish quickly",
            "Wait forever for resources",
            "Use less memory",
            "Run in parallel"
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


def get_mode():
    if days_until_exam() <= 3:
        return "Crash Mode"
    return "Organized Mode"


def calculate_readiness():
    base = 72

    if st.session_state.quiz_score is not None:
        quiz_bonus = int((st.session_state.quiz_score - 60) * 0.25)
        base += quiz_bonus

    penalty = len(st.session_state.weak_topics) * 3
    readiness = base - penalty

    return max(0, min(100, readiness))


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎓 StudyOS")
st.sidebar.caption("The Operating System for University Students")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Upload Lecture",
        "Study Workspace",
        "Exam Mode",
        "Quiz & Weakness",
        "AI Study Chat"
    ]
)

st.sidebar.divider()

st.sidebar.info("Demo Subject: Operating Systems")


# ============================================================
# HERO
# ============================================================

st.markdown('<div class="badge">AI-powered study workspace</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="main-title">
        Turn lecture PDFs into<br>
        a complete <span class="gradient-text">study plan</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        StudyOS helps university students upload lectures, generate summaries,
        create flashcards, test themselves, detect weak topics, and prepare before exams.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PAGE: HOME
# ============================================================

if page == "Home":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Calm Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-description">
            Instead of asking “what should I study?”, the student sees exactly where they stand.
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Days Until Exam", f"{days_until_exam()} days")

    with col2:
        st.metric("Exam Readiness", f"{calculate_readiness()}%")

    with col3:
        st.metric("Topics Left", len(st.session_state.weak_topics))

    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Next Best Action")

    st.success("Review Deadlocks first, then take a short quiz to improve your readiness score.")

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-title">📄 PDF to Workspace</div>
                <div class="feature-text">
                    Upload a lecture and instantly generate summaries, flashcards, quiz questions, and a plan.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-title">🚨 Smart Exam Mode</div>
                <div class="feature-text">
                    The app switches between organized planning and Crash Mode based on the exam date.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-title">🧠 Weakness Detection</div>
                <div class="feature-text">
                    The app tracks quiz mistakes and recommends which topics to review first.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PAGE: UPLOAD LECTURE
# ============================================================

elif page == "Upload Lecture":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Upload Lecture</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-description">
            Upload a lecture PDF. In the real product, AI would process the lecture and generate a full workspace.
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Upload lecture PDF", type=["pdf"])

    if uploaded_file is not None:
        with st.spinner("Processing lecture..."):
            text = extract_pdf_text(uploaded_file)

        st.session_state.uploaded = True
        st.session_state.uploaded_text = text

        st.success("Lecture processed successfully. Study workspace generated.")

        if text:
            with st.expander("Preview extracted text"):
                st.write(text[:1500])
        else:
            st.warning("PDF uploaded, but no readable text was extracted. This may happen with scanned PDFs.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: STUDY WORKSPACE
# ============================================================

elif page == "Study Workspace":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Generated Study Workspace</div>', unsafe_allow_html=True)

    if not st.session_state.uploaded:
        st.info("No lecture uploaded yet. This page shows demo content.")
    else:
        st.success("Workspace generated from your uploaded lecture.")

    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Summaries", "1")

    with col2:
        st.metric("Flashcards", "18")

    with col3:
        st.metric("Quiz Questions", "10")

    st.subheader("Generated Summary")

    st.write(
        """
        This lecture introduces important Operating Systems concepts such as process management,
        CPU scheduling, memory management, deadlocks, and file systems. The main exam focus should be
        definitions, comparisons between scheduling algorithms, and the conditions that cause deadlock.
        """
    )

    st.subheader("Key Points")

    st.markdown(
        """
        - A process is a program in execution.
        - CPU scheduling decides which process runs next.
        - Round Robin uses a fixed time slice.
        - Deadlock happens when processes wait forever for resources.
        - Memory management controls RAM usage and protection.
        """
    )

    st.subheader("Generated Flashcards")

    for card in FLASHCARDS:
        with st.expander(card["front"]):
            st.write(card["back"])


# ============================================================
# PAGE: EXAM MODE
# ============================================================

elif page == "Exam Mode":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Smart Exam Mode</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-description">
            StudyOS changes the study strategy based on how close the exam is.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.exam_date = st.date_input(
        "Choose your exam date",
        value=st.session_state.exam_date
    )

    st.metric("Days Until Exam", f"{days_until_exam()} days")

    mode = get_mode()

    if mode == "Crash Mode":
        st.markdown(
            """
            <div class="crash-box">
                🚨 Crash Mode Activated: Your exam is close. Focus only on the highest-impact topics.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("High-Priority Topics")

        st.markdown(
            """
            1. Deadlocks  
            2. CPU Scheduling  
            3. Memory Management  
            """
        )

        st.subheader("Likely Exam Questions")

        st.markdown(
            """
            - Explain the four necessary conditions for deadlock.
            - Compare FCFS, SJF, and Round Robin.
            - Explain paging and segmentation.
            """
        )

        st.subheader("Rapid Revision Plan")

        st.markdown(
            """
            - Review generated summary.
            - Study flashcards.
            - Take the weakness quiz.
            - Revisit wrong-answer topics.
            """
        )

    else:
        st.markdown(
            """
            <div class="organized-box">
                ✅ Organized Mode Activated: Your exam is not close yet. Follow the day-by-day study plan.
            </div>
            """,
            unsafe_allow_html=True
        )

        plan = pd.DataFrame(
            {
                "Day": ["Day 1", "Day 2", "Day 3", "Day 4"],
                "Focus": [
                    "Process Management",
                    "CPU Scheduling",
                    "Memory Management",
                    "Deadlocks"
                ],
                "Task": [
                    "Read summary + flashcards",
                    "Practice scheduling questions",
                    "Review definitions",
                    "Take quiz and revise weak topics"
                ]
            }
        )

        st.dataframe(plan, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: QUIZ & WEAKNESS
# ============================================================

elif page == "Quiz & Weakness":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Quiz & Weakness Detection</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-description">
            The quiz is not only for testing. It teaches the app what the student is weak in.
        </div>
        """,
        unsafe_allow_html=True
    )

    answers = []

    with st.form("quiz_form"):
        for index, item in enumerate(QUIZ):
            answer = st.radio(
                item["question"],
                item["options"],
                key=f"quiz_{index}"
            )
            answers.append(answer)

        submitted = st.form_submit_button("Submit Quiz")

    if submitted:
        correct = 0
        weak_topics = []

        for selected, item in zip(answers, QUIZ):
            if selected == item["answer"]:
                correct += 1
            else:
                weak_topics.append(item["topic"])

        score = int((correct / len(QUIZ)) * 100)

        st.session_state.quiz_score = score
        st.session_state.weak_topics = weak_topics

        st.metric("Quiz Score", f"{score}%")

        if weak_topics:
            st.warning("Weak topics detected:")
            for topic in weak_topics:
                st.write(f"- {topic}")
        else:
            st.success("Excellent. No weak topics detected.")

    st.subheader("Current Weakness Profile")

    weakness_table = pd.DataFrame(
        {
            "Topic": TOPICS,
            "Status": [
                "Strong",
                "Medium",
                "Needs Review",
                "Weak",
                "Not Started"
            ],
            "Recommended Action": [
                "Quick review only",
                "Practice one question",
                "Review definitions",
                "Revise immediately",
                "Start after weak topics"
            ]
        }
    )

    st.dataframe(weakness_table, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# PAGE: AI STUDY CHAT
# ============================================================

elif page == "AI Study Chat":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown('<div class="section-heading">Subject-Scoped AI Chat</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-description">
            This is not a generic chatbot. It answers as if it is grounded in the student's uploaded lecture.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info("Demo mode: responses are simulated for the prototype.")

    question = st.text_input("Ask something from your lecture")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            st.write(
                """
                Based on your Operating Systems lecture, this topic is important because it connects
                to exam questions about processes, scheduling, memory, or deadlocks. Start with the
                definition, then test yourself using the generated flashcards.
                """
            )

        if st.button("Quiz me on this"):
            st.write("Mini quiz: Which method is best for active recall?")
            st.radio(
                "Choose one:",
                [
                    "Only rereading",
                    "Flashcards",
                    "Highlighting everything",
                    "Skipping weak topics"
                ]
            )

    st.markdown("</div>", unsafe_allow_html=True)
