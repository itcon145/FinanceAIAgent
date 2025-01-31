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

# **🎨 Custom Purple Theme Styling**
st.markdown("""
    <style>
        body { background-color: #2E0249; color: white; }
        .title { text-align: center; font-size: 38px; font-weight: bold; color: #BB86FC; }
        .subtitle { text-align: center; font-size: 20px; color: #CF9FFF; }
        .stButton>button { width: 100%; background-color: #BB86FC; color: black; font-size: 16px; font-weight: bold; }
        .stSelectbox, .stTextInput { text-align: center; }
        .agent-container { padding: 10px; border-radius: 10px; margin: 10px 0; background-color: #4A0072; }
        .agent-title { font-size: 20px; font-weight: bold; color: #FF79C6; }
        .agent-desc { font-size: 16px; color: #E5CFF7; }
    </style>
""", unsafe_allow_html=True)

# **📢 Title & Description**
st.markdown('<h1 class="title">🤖 The Army of the 12 AI Agents for Finance & FP&A</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover AI-powered tools to enhance your financial planning & analysis workflow!</p>', unsafe_allow_html=True)

# **🔗 AI Agent Links & Descriptions**
ai_agents = {
    "📊 Finance AI Forecaster": ("https://finance-ai-forecaster.streamlit.app/", "Like having a crystal ball for financial predictions. Forecast your data using AI."),
    "🤖 Finance Robo Commentator": ("https://finance-robo-commentator.streamlit.app/", "Automated, insightful commentary on your financial data."),
    "📈 AI Finance Data Visualizer": ("https://ai-finance-data-visualizer.streamlit.app/", "Transform financial data into stunning, insightful visualizations."),
    "📊 Dashboard Pro": ("https://dashboard-pro.streamlit.app/", "Build dynamic, interactive dashboards for your finance and FP&A needs."),
    "📉 Variance Analyzer": ("https://variance-analyzer.streamlit.app/", "Easily analyze and explain budget vs. actual variances."),
    "🔮 Scenario Modeller": ("https://scenario-modeller.streamlit.app/", "Run powerful financial scenario planning with AI."),
    "🎲 Monte Carlo Simulator": ("https://monte-carlo-simulator.streamlit.app/", "Use AI to simulate multiple financial scenarios with probability-based modeling."),
    "📉 Stock Analyzer AI Finance": ("https://stock-analyzer-ai-finance.streamlit.app/", "Analyze stocks, trends, and financial statements using AI."),
    "🎓 AI for Finance Tutor": ("https://ai-for-finance-tutor.streamlit.app/", "An interactive learning hub with videos, articles, and exercises on AI in finance."),
    "📑 Financial Modelling AI": ("https://financial-modelling-ai.streamlit.app/", "Instantly builds complex financial models with AI."),
    "📚 AI Finance Knowledge": ("https://ai-finance-knowledge.streamlit.app/", "Get Wikipedia-style AI-generated explanations for finance and FP&A concepts."),
    "📖 Financial Data Storyteller": ("https://financial-data-storyteller.streamlit.app/", "Turn numbers into compelling financial stories and reports."),
}

st.subheader("🛠️ Explore the AI Agents")
for agent, (url, description) in ai_agents.items():
    st.markdown(f'<div class="agent-container">', unsafe_allow_html=True)
    st.markdown(f'<p class="agent-title">{agent}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="agent-desc">{description}</p>', unsafe_allow_html=True)
    st.markdown(f'<a href="{url}" target="_blank"><button style="background-color:#BB86FC; color:black; font-weight:bold; width:100%;">🚀 Visit {agent}</button></a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# **🤖 AI-Powered Assistant – Help Users Choose the Right AI Agent**
st.subheader("🤖 AI-Powered Assistant: Find the Best AI Agent for You")
user_question = st.text_area("📝 What do you need help with? (e.g., 'I need help analyzing budget variances', 'I want to visualize my finance data'):")

if st.button("🔍 Find the Best AI Agent"):
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant helping users find the best AI agent for their finance and FP&A needs. "
                           "Based on their question, recommend the most suitable AI agent from the list."
            },
            {"role": "user", "content": f"Which AI Agent should I use for this need: {user_question}?"}
        ],
        model="llama3-8b-8192",
    )

    recommendation = response.choices[0].message.content
    st.subheader("🤖 Recommended AI Agent")
    st.write(recommendation)
