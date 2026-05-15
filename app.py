import streamlit as st
import pandas as pd
from datetime import date
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="StudyOS Demo",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown("""
<style>
/* Hide Streamlit default UI */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(180deg, #faf9ff 0%, #f6f7fb 100%);
    font-family: 'Inter', sans-serif;
}

/* Main container */
.block-container {
    padding-top: 0rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1200px;
}

/* Navbar */
.navbar {
    height: 64px;
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid #ececf4;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2.8rem;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999;
}

.logo-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo-icon {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c5cff, #9b7cff);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 17px;
    font-weight: 700;
}

.logo-text {
    font-size: 20px;
    font-weight: 800;
    color: #202230;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 14px;
}

.nav-link {
    padding: 9px 16px;
    border-radius: 12px;
    color: #7c7f91;
    font-size: 14px;
    font-weight: 700;
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
    font-weight: 800;
}

.user-plan {
    font-size: 11px;
    color: #9a9caf;
    font-weight: 600;
}

.avatar {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #7c5cff, #9b7cff);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}

/* Hero */
.hero {
    margin-top: 92px;
    text-align: center;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    background: #f0edff;
    color: #7357f6;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 18px;
}

.hero-title {
    font-size: 48px;
    line-height: 1.08;
    font-weight: 900;
    color: #202230;
    margin-bottom: 14px;
}

.gradient-text {
    background: linear-gradient(135deg, #6953ff, #9b7cff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 18px;
    color: #8a8d9f;
    max-width: 650px;
    margin: 0 auto 36px auto;
    line-height: 1.6;
    font-weight: 600;
}

/* Upload card */
.upload-card {
    background: white;
    border: 2px dashed #e3ddff;
    border-radius: 28px;
    padding: 48px 32px;
    text-align: center;
    box-shadow: 0 24px 60px rgba(116, 87, 246, 0.08);
    max-width: 880px;
    margin: 0 auto 34px auto;
}

.upload-icon {
    width: 78px;
    height: 78px;
    border-radius: 22px;
    background: linear-gradient(135deg, #7057ff, #9b7cff);
    color: white;
    font-size: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 22px auto;
    box-shadow: 0 16px 30px rgba(116, 87, 246, 0.22);
}

.upload-title {
    font-size: 24px;
    font-weight: 900;
    color: #252737;
    margin-bottom: 6px;
}

.upload-desc {
    color: #9a9caf;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 20px;
}

.privacy-note {
    color: #9a9caf;
    font-size: 12px;
    font-weight: 700;
    margin-top: 16px;
}

/* Streamlit upload button styling */
[data-testid="stFileUploader"] {
    max-width: 360px;
    margin: 0 auto;
}

[data-testid="stFileUploader"] section {
    border: none;
    padding: 0;
}

[data-testid="stFileUploader"] label {
    display: none;
}

[data-testid="stFileUploader"] button {
    background: linear-gradient(135deg, #7057ff, #9b7cff) !important;
    color: white !important;
    border-radius: 14px !important;
    border: none !important;
    font-weight: 800 !important;
    padding: 0.6rem 1.2rem !important;
}

/* Cards */
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    max-width: 880px;
    margin: 0 auto;
}

.feature-card {
    background: white;
    border-radius: 24px;
    padding: 24px;
    border: 1px solid #ececf4;
    box-shadow: 0 16px 42px rgba(40, 40, 70, 0.04);
}

.feature-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
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
    color: #8a8d9f;
    line-height: 1.5;
    font-weight: 600;
}

/* Result section */
.result-card {
    background: white;
    border-radius: 26px;
    padding: 28px;
    border: 1px solid #ececf4;
    box-shadow: 0 18px 45px rgba(40, 40, 70, 0.05);
    margin-top: 28px;
}

.section-title {
    font-size: 24px;
    font-weight: 900;
    color: #252737;
    margin-bottom: 12px;
}

/* Streamlit components */
.stButton > button {
    background: linear-gradient(135deg, #7057ff, #9b7cff);
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 800;
    padding: 0.7rem 1.2rem;
}

.stMetric {
    background: white;
    border: 1px solid #ececf4;
    padding: 20px;
    border-radius: 22px;
    box-shadow: 0 12px 30px rgba(40, 40, 70, 0.04);
}

@media (max-width: 900px) {
    .card-grid {
        grid-template-columns: 1fr;
    }

    .hero-title {
        font-size: 36px;
    }

    .nav-links {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)


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


def render_navbar(active_page="Dashboard"):
    pages = ["Dashboard", "My Lectures", "Study Planner", "Profile"]

    nav_items = ""
    for page in pages:
        active_class = "nav-link-active" if page == active_page else ""
        nav_items += f'<div class="nav-link {active_class}">{page}</div>'

    st.markdown(f"""
    <div class="navbar">
        <div class="logo-wrap">
            <div class="logo-icon">🎓</div>
            <div class="logo-text">Study<span style="color:#7357f6;">OS</span></div>
        </div>

        <div class="nav-links">
            {nav_items}
        </div>

        <div class="user-wrap">
            <div class="user-text">
                <div class="user-name">Hussein T.</div>
                <div class="user-plan">Premium</div>
            </div>
            <div class="avatar">HT</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_feature_cards():
    st.markdown("""
    <div class="card-grid">
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Instant Summaries</div>
            <div class="feature-desc">Turn long lecture PDFs into clean summaries and key points.</div>
        </div>

        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">Smart Flashcards</div>
            <div class="feature-desc">Generate front/back cards from your real lecture material.</div>
        </div>

        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Exam Readiness</div>
            <div class="feature-desc">Track your preparation with a clear readiness score.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------
# Navbar
# -----------------------------
render_navbar("Dashboard")


# -----------------------------
# Hero + Upload UI
# -----------------------------
st.markdown("""
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

<div class="upload-card">
    <div class="upload-icon">☁️</div>
    <div class="upload-title">Drag & drop your lecture PDF</div>
    <div class="upload-desc">or click below to browse from your computer</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    label_visibility="collapsed"
)

st.markdown("""
<div class="privacy-note">
    🛡 Supports files up to 50MB · Encrypted & private
</div>
""", unsafe_allow_html=True)

render_feature_cards()


# -----------------------------
# Generated Results
# -----------------------------
if uploaded_file:
    with st.spinner("StudyOS is generating your workspace..."):
        extracted_text = extract_pdf_text(uploaded_file)

    st.success("Lecture processed successfully.")

    st.markdown("""
    <div class="result-card">
        <div class="section-title">Generated Study Workspace</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Exam Readiness", "71%")

    with col2:
        st.metric("Flashcards Created", "18")

    with col3:
        st.metric("Quiz Questions", "10")

    st.markdown("### Lecture Summary")
    st.write("""
    This lecture introduces the main concepts from the uploaded material.
    StudyOS identified the most important definitions, key ideas, and exam-focused topics.
    """)

    st.markdown("### Key Points")
    st.markdown("""
    - The lecture contains several exam-relevant definitions.
    - The most important concepts were extracted automatically.
    - Flashcards and quiz questions were generated from the uploaded PDF.
    - A study plan can now be created based on the exam date.
    """)

    st.markdown("### Generated Flashcards")

    with st.expander("What is the main idea of this lecture?"):
        st.write("The lecture explains the core concepts students need to understand before the exam.")

    with st.expander("Why is this topic important?"):
        st.write("Because it is likely to appear in definitions, explanations, or comparison questions.")

    with st.expander("What should the student review first?"):
        st.write("The student should start with the key definitions and weak topics.")

    st.markdown("### Crash Mode Preview")

    st.error("Crash Mode active: Your exam is close. Focus on high-impact topics only.")

    st.markdown("""
    **Today’s plan:**
    1. Review the generated summary  
    2. Study the flashcards  
    3. Take the quiz  
    4. Revisit weak topics  
    """)

else:
    st.markdown("<br>", unsafe_allow_html=True)
