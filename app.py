import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from groq import Groq
import os
from dotenv import load_dotenv

# Load API key securely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Ensure API key exists
if not GROQ_API_KEY:
    st.error("API Key is missing! Set it in a .env file before running the app.")
    st.stop()

# Streamlit UI
st.title("📊 FP&A AI Commentary Dashboard")
st.write("This app forecasts financial data and provides FP&A commentary using AI.")

# Upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read data
    data = pd.read_excel(uploaded_file)

    # Convert date
    data['ds'] = pd.to_datetime(data['ds'])
    data.rename(columns={'y': 'Revenue'}, inplace=True)

    # Display data preview
    st.subheader("📅 Data Preview")
    st.dataframe(data.head())

    # Forecasting with Prophet
    model = Prophet(yearly_seasonality=True)
    model.fit(data)
    future = model.make_future_dataframe(periods=180)
    forecast = model.predict(future)

    # Plot Forecast
    st.subheader("📈 Revenue Forecast")
    fig1 = model.plot(forecast)
    st.pyplot(fig1)

    # Display forecast data
    st.subheader("🔍 Forecasted Data")
    st.dataframe(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

    # Prepare summary for AI
    forecast_summary = f"""
    Financial Forecast Summary:
    - Forecasted Period: {forecast['ds'].iloc[-180].strftime('%Y-%m-%d')} to {forecast['ds'].iloc[-1].strftime('%Y-%m-%d')}
    - Expected Revenue Range:
      - Lower Bound: ${forecast['yhat_lower'].iloc[-180:].min():,.2f}
      - Upper Bound: ${forecast['yhat_upper'].iloc[-180:].max():,.2f}
    - Average Forecasted Revenue: ${forecast['yhat'].iloc[-180:].mean():,.2f}
    """

    st.subheader("💬 FP&A AI Commentary")

    # AI Commentary
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an expert FP&A analyst providing AI-driven financial insights."},
            {"role": "user", "content": f"The financial forecast is summarized as follows:\n{forecast_summary}\nPlease provide FP&A analysis and recommendations."}
        ],
        model="llama3-8b-8192",
    )

    ai_commentary = response.choices[0].message.content

    # Display commentary
    st.write(ai_commentary)
