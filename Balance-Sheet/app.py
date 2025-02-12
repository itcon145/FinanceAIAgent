import streamlit as st
import pandas as pd
import numpy as np
import os
from groq import Groq
from dotenv import load_dotenv

# Load API Key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in .env file or Streamlit secrets.")
    st.stop()

# Initialize AI Client
client = Groq(api_key=GROQ_API_KEY)

# Streamlit UI Setup
st.set_page_config(page_title="📊 Balance Sheet AI Quiz", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
        .title { text-align: center; font-size: 36px; font-weight: bold; color: #003366; }
        .subtitle { text-align: center; font-size: 20px; color: #004488; }
        .stButton>button { width: 100%; background-color: #003366; color: white; font-size: 16px; font-weight: bold; }
        .quiz-container { padding: 15px; border-radius: 10px; margin: 10px 0; background-color: #E3F2FD; }
        .quiz-title { font-size: 20px; font-weight: bold; color: #004488; }
        .quiz-desc { font-size: 16px; color: #003366; }
    </style>
""", unsafe_allow_html=True)

# **Title & Description**
st.markdown('<h1 class="title">📊 Balance Sheet AI Quiz</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Test your knowledge of balance sheet concepts with AI-generated questions.</p>', unsafe_allow_html=True)

# Define Balance Sheet Taxonomy
taxonomy = [
    "Assets",
    "Liabilities",
    "Equity",
    "Financial Ratios",
    "Revenue Recognition",
    "Working Capital",
    "Depreciation & Amortization"
]

# Select Quiz Topic
selected_topic = st.selectbox("📖 Select a Balance Sheet Topic:", taxonomy)

# Generate AI-Based Questions
if st.button("🎯 Generate Quiz Question"):
    with st.spinner("Generating question..."):
        prompt = f"""
        You are an expert FP&A professional. Create a multiple-choice question (MCQ) to test knowledge on {selected_topic}.
        The question should have:
        - A clear statement
        - Four answer choices (A, B, C, D)
        - One correct answer with an explanation.
        Format output as:
        **Question:** [your question]
        **A.** [option A]
        **B.** [option B]
        **C.** [option C]
        **D.** [option D]
        **Correct Answer:** [correct option]
        **Explanation:** [why it's correct]
        """

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a balance sheet expert who creates financial quizzes."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",
        )

        quiz_text = response.choices[0].message.content

        # Display Quiz Question
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        st.markdown(quiz_text.replace("**", ""))
        st.markdown('</div>', unsafe_allow_html=True)
