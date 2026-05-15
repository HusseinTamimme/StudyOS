import streamlit as st
import pandas as pd
from datetime import date, timedelta

from studyos_engine import (
    extract_pdf_text,
    generate_summary,
    generate_key_points,
    generate_flashcards,
    generate_quiz,
    estimate_readiness,
    answer_from_lecture,
    build_study_plan,
    detect_topics_from_text,
)


st.set_page_config(
    page_title="StudyOS",
    page_icon="🎓",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #faf9ff 0%, #f7f8fc 100%);
    }

    .hero-title {
        text-align: center;
        font-size: 52px;
        font-weight: 900;
        color: #232536;
        line-height: 1.1;
        margin-top: 20px;
    }

    .gradient {
        background: linear-gradient(90deg, #6d5dfc, #9b7cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        text-align: center;
        max-width: 760px;
        margin: 18px auto 35px auto;
        color: #777b8f;
        font-size: 18px;
        line-height: 1.6;
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

    .card {
        background: white;
        padding: 26px;
        border-radius: 24px;
        border: 1px solid #ececf4;
        box-shadow: 0 14px 35px rgba(40, 40, 70, 0.05);
        margin-bottom: 22px;
    }

    .card-title {
        font-size: 25px;
        font-weight: 900;
        color: #252737;
        margin-bottom: 8px;
    }

    .card-text {
        color: #777b8f;
        font-size: 15px;
        line-height: 1.6;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 20px;
        border-radius: 20px;
        border: 1px solid #ececf4;
        box-shadow: 0 12px 28px rgba(40, 40, 70, 0.04);
    }

    .crash {
        background: #fff4f4;
        border: 1px solid #ffd2d2;
        color: #9f1d1d;
        padding: 18px;
        border-radius: 18px;
        font-weight: 750;
    }

    .organized {
        background: #f0fff7;
        border: 1px solid #bdeed4;
        color: #087443;
        padding: 18px;
        border-radius: 18px;
        font-weight: 750;
    }

    .small-muted {
        color: #8a8d9f;
        font-size: 13px;
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
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "uploaded": False,
    "lecture_name": "",
    "lecture_text": "",
    "summary": "",
    "key_points": [],
    "flashcards": [],
    "quiz": [],
    "topics": [],
    "quiz_score": None,
    "weak_topics": [],
    "completed_topics": 0,
    "exam_date": date.today() + timedelta(days=2),
    "hours_per_day": 2.0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def days_until_exam() -> int:
    remaining = st.session_state.exam_date - date.today()
    return max(remaining.days, 0)


def app_mode() -> str:
    return "Crash Mode" if days_until_exam() <= 3 else "Organized Mode"


def readiness() -> int:
    total_topics = max(len(st.session_state.topics), 1)

    return estimate_readiness(
        uploaded=st.session_state.uploaded,
        quiz_score=st.session_state.quiz_score,
        weak_topics_count=len(st.session_state.weak_topics),
        completed_topics=st.session_state.completed_topics,
        total_topics=total_topics,
    )


def process_uploaded_pdf(uploaded_file):
    text = extract_pdf_text(uploaded_file)

    if not text:
        st.error("The PDF was uploaded, but no readable text was extracted. Try a text-based PDF.")
        return

    topics = detect_topics_from_text(text)
    summary = generate_summary(text)
    key_points = generate_key_points(text)
    flashcards = generate_flashcards(text)
    quiz = generate_quiz(text)

    st.session_state.uploaded = True
    st.session_state.lecture_name = uploaded_file.name
    st.session_state.lecture_text = text
    st.session_state.topics = topics
    st.session_state.summary = summary
    st.session_state.key_points = key_points
    st.session_state.flashcards = flashcards
    st.session_state.quiz = quiz
    st.session_state.completed_topics = max(1, len(topics) // 2)
    st.session_state.quiz_score = None
    st.session_state.weak_topics = []


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🎓 StudyOS")
st.sidebar.caption("The Operating System for University Students")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Lecture",
        "Study Workspace",
        "Exam Planner",
        "Quiz",
        "AI Study Chat",
    ]
)

st.sidebar.divider()

if st.session_state.uploaded:
    st.sidebar.success(f"Loaded: {st.session_state.lecture_name}")
else:
    st.sidebar.warning("No lecture uploaded yet")

st.sidebar.metric("Readiness", f"{readiness()}%")
st.sidebar.metric("Mode", app_mode())


# ============================================================
# HERO
# ============================================================

st.markdown('<div class="badge">AI-powered study workspace</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-title">
        Turn lecture PDFs into<br>
        a complete <span class="gradient">study system</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-subtitle">
        Upload a lecture PDF. StudyOS generates a summary, key points, flashcards,
        quiz questions, exam plan, weakness profile, and a subject-scoped study chat.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PAGE: DASHBOARD
# ============================================================

if page == "Dashboard":
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Calm Dashboard</div>
            <div class="card-text">
                The student opens one screen and immediately knows what to do next.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Days Until Exam", f"{days_until_exam()} days")

    with col2:
        st.metric("Exam Readiness", f"{readiness()}%")

    with col3:
        st.metric("Weak Topics", len(st.session_state.weak_topics))

    st.divider()

    if app_mode() == "Crash Mode":
        st.markdown(
            """
            <div class="crash">
                🚨 Crash Mode is active. Focus on high-impact topics, weak areas, and fast review.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="organized">
                ✅ Organized Mode is active. Follow your day-by-day study plan.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Next Best Action")

    if not st.session_state.uploaded:
        st.info("Upload a lecture PDF first to generate your study workspace.")
    elif st.session_state.weak_topics:
        st.success(f"Review **{st.session_state.weak_topics[0]}** first, then retake the quiz.")
    else:
        st.success("Take the generated quiz to identify your weak topics.")

    st.subheader("Topic Progress")

    if st.session_state.topics:
        progress_df = pd.DataFrame(
            {
                "Topic": st.session_state.topics,
                "Status": [
                    "Completed" if i < st.session_state.completed_topics else "Needs Review"
                    for i in range(len(st.session_state.topics))
                ],
            }
        )
        st.dataframe(progress_df, use_container_width=True)
    else:
        st.info("No topics detected yet. Upload a lecture to begin.")


# ============================================================
# PAGE: UPLOAD
# ============================================================

elif page == "Upload Lecture":
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Upload Lecture PDF</div>
            <div class="card-text">
                Upload a text-based lecture PDF. StudyOS will process the real content and build the workspace.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader("Choose a lecture PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Generate Study Workspace"):
            with st.spinner("Reading PDF and generating study materials..."):
                process_uploaded_pdf(uploaded_file)

            st.success("Study workspace generated successfully.")
            st.balloons()

    if st.session_state.uploaded:
        st.subheader("Uploaded Lecture")
        st.write(st.session_state.lecture_name)

        with st.expander("Preview extracted text"):
            st.write(st.session_state.lecture_text[:2500])


# ============================================================
# PAGE: STUDY WORKSPACE
# ============================================================

elif page == "Study Workspace":
    if not st.session_state.uploaded:
        st.warning("Upload a lecture first.")
        st.stop()

    st.markdown(
        """
        <div class="card">
            <div class="card-title">Generated Study Workspace</div>
            <div class="card-text">
                These materials were generated from your uploaded PDF.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Topics", len(st.session_state.topics))

    with col2:
        st.metric("Flashcards", len(st.session_state.flashcards))

    with col3:
        st.metric("Quiz Questions", len(st.session_state.quiz))

    with col4:
        st.metric("Readiness", f"{readiness()}%")

    st.subheader("Detected Topics")
    st.write(", ".join(st.session_state.topics))

    st.subheader("Generated Summary")
    st.write(st.session_state.summary)

    st.subheader("Key Points")
    for point in st.session_state.key_points:
        st.markdown(f"- {point}")

    st.subheader("Flashcards")
    if st.session_state.flashcards:
        for i, card in enumerate(st.session_state.flashcards, start=1):
            with st.expander(f"{i}. {card['front']}"):
                st.write(card["back"])
    else:
        st.info("No flashcards were generated. Try a longer lecture PDF.")


# ============================================================
# PAGE: EXAM PLANNER
# ============================================================

elif page == "Exam Planner":
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Smart Exam Planner</div>
            <div class="card-text">
                StudyOS changes the plan depending on how close the exam is.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.exam_date = st.date_input(
            "Exam date",
            value=st.session_state.exam_date
        )

    with col2:
        st.session_state.hours_per_day = st.number_input(
            "Available study hours per day",
            min_value=0.5,
            max_value=12.0,
            value=float(st.session_state.hours_per_day),
            step=0.5
        )

    st.metric("Days Until Exam", f"{days_until_exam()} days")

    if app_mode() == "Crash Mode":
        st.markdown(
            """
            <div class="crash">
                🚨 Crash Mode Activated: The exam is close. The app will ignore long planning
                and focus on high-impact revision.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Crash Priorities")

        priorities = st.session_state.weak_topics or st.session_state.topics[:3] or ["Review lecture summary"]

        for item in priorities:
            st.markdown(f"- **{item}**")

        st.subheader("Rapid Revision Strategy")
        st.markdown(
            """
            1. Read the generated summary.  
            2. Review flashcards.  
            3. Solve the quiz.  
            4. Revisit weak topics.  
            5. Ask the AI chat about confusing points.  
            """
        )

    else:
        st.markdown(
            """
            <div class="organized">
                ✅ Organized Mode Activated: You have enough time for a structured plan.
            </div>
            """,
            unsafe_allow_html=True
        )

    st.subheader("Generated Study Plan")

    plan = build_study_plan(
        topics=st.session_state.topics or ["Upload lecture first"],
        days_left=days_until_exam(),
        hours_per_day=st.session_state.hours_per_day,
    )

    st.dataframe(plan, use_container_width=True)


# ============================================================
# PAGE: QUIZ
# ============================================================

elif page == "Quiz":
    if not st.session_state.uploaded:
        st.warning("Upload a lecture first.")
        st.stop()

    st.markdown(
        """
        <div class="card">
            <div class="card-title">Quiz & Weakness Detection</div>
            <div class="card-text">
                The quiz is generated from your lecture. Your wrong answers become weak topics.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.quiz:
        st.info("No quiz questions were generated from this PDF.")
        st.stop()

    answers = []

    with st.form("lecture_quiz"):
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Question {i + 1}**")
            answer = st.radio(
                q["question"],
                q["options"],
                key=f"quiz_{i}"
            )
            answers.append(answer)

        submitted = st.form_submit_button("Submit Quiz")

    if submitted:
        correct = 0
        weak_topics = []

        for selected, q in zip(answers, st.session_state.quiz):
            if selected == q["answer"]:
                correct += 1
            else:
                weak_topics.append(q["topic"])

        score = int((correct / len(st.session_state.quiz)) * 100)

        st.session_state.quiz_score = score
        st.session_state.weak_topics = list(dict.fromkeys(weak_topics))

        st.metric("Quiz Score", f"{score}%")

        if st.session_state.weak_topics:
            st.warning("Weak topics detected:")
            for topic in st.session_state.weak_topics:
                st.write(f"- {topic}")
        else:
            st.success("Excellent. No weak topics detected.")

        st.subheader("Answer Review")

        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{i + 1}: Correct answer:** {q['answer']}")
            st.caption(q["explanation"])

    st.subheader("Current Weakness Profile")

    if st.session_state.weak_topics:
        weakness_df = pd.DataFrame(
            {
                "Weak Topic": st.session_state.weak_topics,
                "Recommended Action": [
                    "Review summary, flashcards, and ask the AI chat for clarification."
                    for _ in st.session_state.weak_topics
                ],
            }
        )
        st.dataframe(weakness_df, use_container_width=True)
    else:
        st.info("Take the quiz to generate a weakness profile.")


# ============================================================
# PAGE: AI CHAT
# ============================================================

elif page == "AI Study Chat":
    st.markdown(
        """
        <div class="card">
            <div class="card-title">Subject-Scoped AI Study Chat</div>
            <div class="card-text">
                Ask questions from your uploaded lecture. This version retrieves the most relevant lecture lines.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.uploaded:
        st.warning("Upload a lecture first.")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_question = st.chat_input("Ask something from your lecture")

    if user_question:
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        answer = answer_from_lecture(
            question=user_question,
            text=st.session_state.lecture_text
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.rerun()

    st.divider()

    if st.button("Quiz me on my weak topics"):
        weak = st.session_state.weak_topics or st.session_state.topics[:2]

        if weak:
            st.info(f"Focus quiz suggestion: Review {', '.join(weak)} and retake the generated quiz.")
        else:
            st.info("Take the lecture quiz first to detect weak topics.")
