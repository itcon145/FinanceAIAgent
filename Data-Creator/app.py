import streamlit as st
import pandas as pd
import numpy as np
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
st.set_page_config(page_title="Synthetic Data Creator", page_icon="📊", layout="wide")
st.title("📊 Synthetic Data Creator – AI-Powered Data Generation")
st.write("Describe the type of dataset you need, and AI will generate it for you!")

# User Input for Data Description
user_prompt = st.text_area("📝 Describe the dataset you want to create (e.g., '100 rows of sales data with date, product, revenue, and customer ID'): ")

if st.button("🚀 Generate Synthetic Data"):
    if user_prompt:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI that generates structured synthetic data for Excel. Users will describe the dataset, and you will create column names, data types, and a sample dataset."},
                {"role": "user", "content": f"Generate a structured dataset based on this description: {user_prompt}. Provide column names and example rows in a tabular format."}
            ],
            model="llama3-8b-8192",
        )

        ai_generated_data = response.choices[0].message.content

        # **Parsing AI Response & Creating DataFrame**
        try:
            lines = ai_generated_data.split("\n")
            columns = lines[0].split("|")[1:-1]  # Extract column names
            columns = [col.strip() for col in columns]  # Clean column names

            # Extract Data Rows
            data_rows = []
            for line in lines[2:]:  # Skip first two lines (headers)
                if "|" in line:
                    row_values = line.split("|")[1:-1]  # Extract row values
                    row_values = [value.strip() for value in row_values]
                    data_rows.append(row_values)

            # Convert to DataFrame
            df = pd.DataFrame(data_rows, columns=columns)

            # Convert numeric columns
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col])  # Convert numbers if possible
                except:
                    pass  # Ignore errors (e.g., text fields)

            # **Display Preview**
            st.subheader("📊 Preview of Generated Data")
            st.dataframe(df)

            # **Downloadable Excel File**
            file_path = "synthetic_data.xlsx"
            df.to_excel(file_path, index=False)
            st.download_button(label="📥 Download Excel File", data=open(file_path, "rb"), file_name="synthetic_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e:
            st.error(f"⚠️ Error parsing AI-generated data: {e}")
