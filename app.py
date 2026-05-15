import streamlit as st
import pandas as pd
from datetime import date
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="StudyOS Demo",
    page_icon="📚",
    layout="wide"
)

# -----------------------------
# Demo Data
# -----------------------------
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
    },
]

# -----------------------------
# Session State
# -----------------------------
if "uploaded_text" not in st.session_state:
    st.session_state.uploaded_text = ""

if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = []

if "exam_date" not in st.session_state:
    st.session_state.exam_date = None

# -----------------------------
# Helper Functions
# -----------------------------
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def calculate_readiness():
    total_topics = len(LECTURE_TOPICS)
    completed_topics = 3

    quiz_results = st.session_state.quiz_results
    if quiz_results:
        quiz_score = sum(quiz_results) / len(quiz_results)
    else:
        quiz_score = 0.55

    readiness = int(((completed_topics / total_topics) * 0.6 + quiz_score * 0.4) * 100)
    return readiness


def get_days_until_exam():
    if st.session_state.exam_date is None:
        return 2

    today = date.today()
    delta = st.session_state.exam_date - today
    return max(delta.days, 0)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📚 StudyOS")
st.sidebar.caption("The Operating System for University Students")

page = st.sidebar.radio(
    "Navigation",
    [
        "Calm Dashboard",
        "Upload Lecture",
        "Smart Exam Mode",
        "Quiz & Weakness Detection",
        "Subject AI Chat"
    ]
)

st.sidebar.divider()
st.sidebar.success("Demo Subject: Operating Systems")

# -----------------------------
# Page 1: Calm Dashboard
# -----------------------------
if page == "Calm Dashboard":
    st.title("Calm Dashboard")
    st.caption("Turn exam panic into a clear plan.")

    days_left = get_days_until_exam()
    readiness = calculate_readiness()
    topics_left = len(LECTURE_TOPICS) - 3

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Days Until Exam", f"{days_left} days")

    with col2:
        st.metric("Exam Readiness", f"{readiness}%")

    with col3:
        st.metric("Topics Left", topics_left)

    st.divider()

    if days_left <= 3:
        st.error("Crash Mode is active. Focus only on the highest-impact topics.")
    else:
        st.info("Organized Mode is active. Follow your day-by-day study plan.")

    st.subheader("Next Best Action")
    st.write("Review **Deadlocks** and take a 5-question quiz before moving to File Systems.")

    st.subheader("Topic Progress")

    progress_data = pd.DataFrame({
        "Topic": LECTURE_TOPICS,
        "Status": ["Completed", "Completed", "Completed", "Weak", "Not Started"],
        "Score": [90, 78, 74, 45, 0]
    })

    st.dataframe(progress_data, use_container_width=True)

# -----------------------------
# Page 2: Upload Lecture
# -----------------------------
elif page == "Upload Lecture":
    st.title("Upload Lecture")
    st.caption("Upload your lecture PDF and StudyOS creates your study workspace.")

    uploaded_file = st.file_uploader("Upload lecture PDF", type=["pdf"])

    if uploaded_file:
        with st.spinner("Processing lecture..."):
            text = extract_pdf_text(uploaded_file)
            st.session_state.uploaded_text = text

        st.success("Lecture processed successfully.")

        st.subheader("Generated Summary")
        st.write("""
        This lecture introduces core Operating Systems concepts including process management,
        CPU scheduling, memory management, and deadlock handling. The most important exam areas
        are process states, scheduling algorithms, and deadlock conditions.
        """)

        st.subheader("Key Points")
        st.markdown("""
        - A process is a program in execution.
        - CPU scheduling improves system efficiency.
        - Round Robin scheduling uses time slices.
        - Deadlock happens when processes wait forever for resources.
        - Memory management controls how programs use RAM.
        """)

        st.subheader("Generated Flashcards")
        for card in FLASHCARDS:
            with st.expander(card["front"]):
                st.write(card["back"])

        st.subheader("Generated MCQ Preview")
        st.info("3 quiz questions created from this lecture.")

    else:
        st.info("Upload a PDF to generate summary, flashcards, quiz, and study plan.")

# -----------------------------
# Page 3: Smart Exam Mode
# -----------------------------
elif page == "Smart Exam Mode":
    st.title("Smart Exam Mode")
    st.caption("StudyOS changes strategy based on how close your exam is.")

    exam_date = st.date_input("Select your exam date", value=date.today())
    st.session_state.exam_date = exam_date

    days_left = get_days_until_exam()

    st.metric("Days Until Exam", f"{days_left} days")

    if days_left <= 3:
        st.error("Crash Mode Activated")

        st.subheader("High-Priority Topics")
        st.markdown("""
        1. Deadlocks  
        2. CPU Scheduling  
        3. Memory Management  
        """)

        st.subheader("Likely Exam Questions")
        st.markdown("""
        - Explain the four necessary conditions for deadlock.
        - Compare FCFS, SJF, and Round Robin scheduling.
        - Explain the difference between paging and segmentation.
        """)

        st.subheader("Rapid Revision Plan")
        st.write("Today: Review Deadlocks and CPU Scheduling. Then take the weakness quiz.")

    else:
        st.success("Organized Mode Activated")

        st.subheader("Day-by-Day Study Plan")
        plan = pd.DataFrame({
            "Day": ["Day 1", "Day 2", "Day 3", "Day 4"],
            "Focus": [
                "Process Management",
                "CPU Scheduling",
                "Memory Management",
                "Deadlocks + Quiz"
            ],
            "Task": [
                "Read summary + flashcards",
                "Solve scheduling questions",
                "Review key definitions",
                "Take quiz and revise weak topics"
            ]
        })

        st.dataframe(plan, use_container_width=True)

# -----------------------------
# Page 4: Quiz & Weakness Detection
# -----------------------------
elif page == "Quiz & Weakness Detection":
    st.title("Quiz & Weakness Detection")
    st.caption("StudyOS learns what the student is weak in.")

    st.subheader("Mini Quiz")

    answers = []

    with st.form("quiz_form"):
        for i, q in enumerate(QUIZ):
            answer = st.radio(
                q["question"],
                q["options"],
                key=f"q_{i}"
            )
            answers.append(answer)

        submitted = st.form_submit_button("Submit Quiz")

    if submitted:
        results = []

        for user_answer, q in zip(answers, QUIZ):
            is_correct = user_answer == q["answer"]
            results.append(is_correct)

        st.session_state.quiz_results = results

        score = int(sum(results) / len(results) * 100)
        st.metric("Quiz Score", f"{score}%")

        weak_topics = [
            q["topic"]
            for user_answer, q in zip(answers, QUIZ)
            if user_answer != q["answer"]
        ]

        if weak_topics:
            st.warning("Weak topics detected:")
            for topic in weak_topics:
                st.write(f"- {topic}")
        else:
            st.success("Great job. No weak topics detected.")

    st.divider()

    st.subheader("Weakness Profile")
    weakness_data = pd.DataFrame({
        "Topic": ["Process Management", "CPU Scheduling", "Deadlocks"],
        "Performance": ["Strong", "Medium", "Weak"],
        "Recommended Action": [
            "Quick revision only",
            "Practice one more question",
            "Review definitions and take another quiz"
        ]
    })

    st.dataframe(weakness_data, use_container_width=True)

# -----------------------------
# Page 5: Subject AI Chat
# -----------------------------
elif page == "Subject AI Chat":
    st.title("Subject-Scoped AI Chat")
    st.caption("Ask questions from your Operating Systems lectures.")

    st.info("Demo mode: answers are simulated based on uploaded lecture content.")

    user_question = st.text_input("Ask a question")

    if user_question:
        st.chat_message("user").write(user_question)

        response = """
        Based on your Operating Systems lecture, deadlock happens when a group of processes
        wait forever because each process is holding a resource and waiting for another resource
        held by another process. The key conditions are mutual exclusion, hold and wait,
        no preemption, and circular wait.
        """

        st.chat_message("assistant").write(response)

        if st.button("Quiz me on this"):
            st.write("Mini quiz: Which condition means a process is holding one resource while waiting for another?")
            st.radio(
                "Choose one:",
                ["Mutual exclusion", "Hold and wait", "Circular wait", "Paging"]
            )
