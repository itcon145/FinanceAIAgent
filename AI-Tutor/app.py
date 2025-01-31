import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Streamlit App UI
st.set_page_config(page_title="AI Financial Tutor", page_icon="📚", layout="wide")
st.title("📚 AI Financial Tutor – Learn AI in Finance & FP&A")
st.write("Explore articles, YouTube videos, and exercises about AI in Finance.")

# **Pre-Loaded Content**
st.subheader("🎥 Featured Learning Videos")

video_links = {
    "AI for Finance Channel": "https://www.youtube.com/@christianmartinezAIforFinance",
    "Introduction to AI in Finance": "https://www.youtube.com/embed/NpK4bALWQ0A",
    "How AI is Changing FP&A": "https://www.youtube.com/embed/kophdbdaDl0",
    "AI for Budgeting & Forecasting": "https://www.youtube.com/embed/dn6zWMuI2q8",
    "Advanced AI in Finance Strategies": "https://www.youtube.com/embed/rN49URY3Q_c",
    "Machine Learning for FP&A": "https://www.youtube.com/embed/4PUOYq3j_YM",
}

for title, link in video_links.items():
    st.markdown(f"### 📌 {title}")
    if "youtube.com/embed" in link:
        st.video(link)
    else:
        st.markdown(f"🔗 [Watch on YouTube]({link})")

st.subheader("📖 Articles & Resources")
articles = {
    "📘 The Future of AI in Finance": "https://www.forbes.com/sites/forbestechcouncil/2023/07/10/the-future-of-ai-in-financial-services/",
    "📘 AI in FP&A: A Game Changer": "https://www.cfo.com/technology/ai-in-fpa-how-ai-is-transforming-financial-planning",
    "📘 Machine Learning in Financial Forecasting": "https://hbr.org/2022/05/how-machine-learning-is-changing-financial-planning",
}

for title, link in articles.items():
    st.markdown(f"📌 [{title}]({link})")

# **Interactive AI Tutor**
st.subheader("🤖 Ask the AI Tutor")

# **Fixing Chat Persistence with Streamlit Session State**
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_question = st.text_input("🔍 Ask a question about AI in Finance or FP&A:")

if st.button("💬 Ask AI"):
    if user_question:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI financial tutor providing insights about AI applications in finance and FP&A."},
                {"role": "user", "content": f"{user_question}"}
            ],
            model="llama3-8b-8192",
        )

        # Append user input and AI response to session state
        st.session_state.chat_history.append(("🧑‍🎓 You", user_question))
        st.session_state.chat_history.append(("🤖 AI Tutor", response.choices[0].message.content))

# **Display Chat History**
for sender, message in st.session_state.chat_history:
    st.write(f"**{sender}:** {message}")

# **Quizzes & Exercises**
st.subheader("📝 AI in Finance Quiz")

quiz_questions = {
    "What is the main use of AI in FP&A?": ["A. Automating reports", "B. Improving forecasting", "C. Reducing costs", "D. All of the above"],
    "Which AI technique is commonly used in financial forecasting?": ["A. Neural Networks", "B. Decision Trees", "C. Regression Analysis", "D. All of the above"],
    "What is a benefit of using AI for financial planning?": ["A. Faster decision-making", "B. Reduced human bias", "C. Increased accuracy", "D. All of the above"],
}

for question, options in quiz_questions.items():
    user_answer = st.radio(f"📌 {question}", options, key=question)
    if st.button(f"✅ Submit Answer for {question}"):
        if "D" in user_answer:
            st.success("🎉 Correct!")
        else:
            st.error("❌ Try again!")

