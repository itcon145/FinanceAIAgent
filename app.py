import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from groq import Groq
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Streamlit App
st.title("📊 SaaS Cohort Analysis with AI Commentary")
st.write("Upload an Excel file with cohort data, visualize it, and get AI-generated FP&A insights.")

# File uploader
uploaded_file = st.file_uploader("Upload your cohort data (Excel format)", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    # Ensure Date column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Cohort Analysis: Group by Product and calculate average invoice amount
    cohort = df.groupby(['Date', 'Product'])['Invoice'].mean().unstack(fill_value=0)

    # Display data
    st.subheader("📅 Cohort Data Preview")
    st.dataframe(df.head())

    # Generate heatmap
    st.subheader("📊 Cohort Analysis Heatmap")
    plt.figure(figsize=(10, 6))
    sns.heatmap(cohort, annot=True, fmt=".2f", cmap="Blues", linewidths=0.5)
    plt.title("Cohort Analysis: Average Invoice by Product", fontsize=14)
    plt.xlabel("Product", fontsize=12)
    plt.ylabel("Date", fontsize=12)
    plt.tight_layout()
    st.pyplot(plt)

    # Prepare summary for AI
    cohort_summary = f"""
    Cohort Analysis Summary:
    - Products: {', '.join(cohort.columns)}
    - Average Invoice by Product:
    {cohort.to_string()}
    """

    # AI Commentary
    st.subheader("💬 AI-Generated FP&A Commentary")

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an experienced CFO providing insights on cohort analysis."},
            {"role": "user", "content": f"The cohort analysis summary is:\n{cohort_summary}\nProvide an FP&A report."}
        ],
        model="llama3-8b-8192",
    )

    ai_commentary = response.choices[0].message.content
    st.write(ai_commentary)
