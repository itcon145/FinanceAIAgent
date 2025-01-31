import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from fpdf import FPDF

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Streamlit App UI
st.set_page_config(page_title="Finance & AI Knowledge Hub", page_icon="📚", layout="wide")
st.title("📚 Finance & AI Knowledge Hub – Learn Anything, Step by Step")
st.write("Ask any question related to Finance, FP&A, Financial Modeling, Stock Market Analysis, Python, AI, or anything in between. AI will generate a structured Wikipedia-style article, gradually increasing difficulty from beginner to expert level.")

# User Input
user_prompt = st.text_area("📝 Enter your question (e.g., 'What is Discounted Cash Flow?'):")

if st.button("🚀 Generate Explanation"):
    if user_prompt:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI expert in Finance, AI, and Financial Modeling. "
                        "You will generate a structured Wikipedia-style explanation for a given topic, "
                        "starting with simple terms for beginners and progressively increasing in difficulty until expert-level knowledge is achieved. "
                        "Use clear, step-by-step explanations with examples."
                    ),
                },
                {"role": "user", "content": f"Explain {user_prompt} in a structured manner, starting from simple terms and increasing difficulty step by step."}
            ],
            model="deepseek-r1-distill-llama-70b",
        )

        ai_response = response.choices[0].message.content

        # **Display AI-Generated Article**
        st.subheader("📖 AI-Generated Explanation")
        st.write(ai_response)

        # **Option to Download as PDF**
        st.subheader("📥 Download as PDF")

        if st.button("📄 Generate PDF"):
            try:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()
                pdf.set_font("Arial", style="B", size=16)
                pdf.cell(200, 10, "Finance & AI Knowledge Hub", ln=True, align="C")
                pdf.ln(10)
                pdf.set_font("Arial", size=12)

                for line in ai_response.split("\n"):
                    pdf.multi_cell(0, 10, line)
                    pdf.ln(2)

                pdf_file_path = "finance_ai_knowledge.pdf"
                pdf.output(pdf_file_path)

                st.download_button(label="📥 Download Explanation as PDF", data=open(pdf_file_path, "rb"), file_name="finance_ai_knowledge.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"⚠️ Error generating PDF: {e}")
