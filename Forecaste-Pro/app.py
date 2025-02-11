import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
import os
from groq import Groq
from dotenv import load_dotenv
from io import BytesIO

# --------------------------------------------------------------------------------
# Load environment variables for API Keys
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------------------------------------------------------------------
# Page Config
st.set_page_config(page_title="Financial Forecaster", layout="wide")

st.title("🔮 Financial Forecaster - AI-Powered Predictions")

# --------------------------------------------------------------------------------
# Check for API Key
if not GROQ_API_KEY:
    st.error("🚨 GROQ API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# Initialize Groq client (for LLM)
client = Groq(api_key=GROQ_API_KEY)

# --------------------------------------------------------------------------------
# Sidebar Inputs
st.sidebar.header("User Inputs")

uploaded_file = st.sidebar.file_uploader("📂 Upload your financial data (Excel)", type=["xlsx"])
forecast_length = st.sidebar.slider("⏳ Forecast Length (days)", min_value=30, max_value=365, value=180)

# Prophet advanced configuration
st.sidebar.subheader("Prophet Configuration")
add_weekly_seasonality = st.sidebar.checkbox("Enable Weekly Seasonality", value=True)
add_yearly_seasonality = st.sidebar.checkbox("Enable Yearly Seasonality", value=True)
seasonality_mode = st.sidebar.selectbox("Seasonality Mode", ["additive", "multiplicative"])

# Frequency selection
freq_map = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "MS"  # Start of the month
}
selected_frequency = st.sidebar.selectbox("Frequency (if needed)", list(freq_map.keys()))

# --------------------------------------------------------------------------------
# Main Application Logic
if uploaded_file:
    # Step 1: Load Data
    df = pd.read_excel(uploaded_file)

    st.subheader("📊 Data Preview")
    st.write("Below is a preview of your data (first 5 rows):")
    st.dataframe(df.head())

    # -- Ensure there's at least one numeric column for target
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        st.error("No numeric columns found in the uploaded file. Please upload a valid financial dataset.")
        st.stop()

    # Step 2: Select or detect Date Column
    # We look for a column that might already be datetime
    possible_date_cols = df.select_dtypes(include=["datetime", "object"]).columns.tolist()

    st.markdown("### Date Column Selection")
    if possible_date_cols:
        date_column = st.selectbox("Select the date column from your file:", possible_date_cols)
    else:
        st.warning("No obvious date column found. We'll generate a date range automatically.")
        date_column = None

    # Step 3: Select the target numeric column
    st.markdown("### Target Column Selection")
    target_column = st.selectbox("Select the numeric column to forecast:", numeric_cols)

    # Step 4: (Optional) Categorical filtering
    st.markdown("### Categorical Filter (Optional)")
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns
    if len(categorical_columns) > 0:
        selected_category_column = st.selectbox(
            "Select a categorical column to filter by (Optional):",
            [None] + list(categorical_columns)
        )
        if selected_category_column:
            unique_values = df[selected_category_column].unique()
            selected_value = st.selectbox(f"Filter {selected_category_column} by:", unique_values)
            df = df[df[selected_category_column] == selected_value]

    # Step 5: Generate forecast button
    generate_forecast = st.button("🚀 Generate Forecast")

    if generate_forecast:
        # Prepare data
        forecast_data = df.copy()

        # Convert selected date column to datetime
        if date_column and date_column in forecast_data.columns:
            forecast_data[date_column] = pd.to_datetime(forecast_data[date_column], errors="coerce")
            # Drop rows with invalid or missing dates
            forecast_data = forecast_data.dropna(subset=[date_column])
            forecast_data = forecast_data.sort_values(by=date_column)
            forecast_data = forecast_data.rename(columns={date_column: "ds"})
        else:
            # If no date column was found or selected, create a date range
            forecast_data = forecast_data.reset_index(drop=True)
            forecast_data["ds"] = pd.date_range(
                start="2022-01-01",
                periods=len(forecast_data),
                freq=freq_map[selected_frequency]
            )

        # Drop rows with missing target
        forecast_data = forecast_data.dropna(subset=[target_column])

        # Rename target column
        forecast_data = forecast_data.rename(columns={target_column: "y"})

        # Initialize Prophet Model
        model = Prophet(
            yearly_seasonality=add_yearly_seasonality,
            weekly_seasonality=add_weekly_seasonality,
            seasonality_mode=seasonality_mode
        )
        model.fit(forecast_data[["ds", "y"]])

        # Future DataFrame and forecast
        future = model.make_future_dataframe(periods=forecast_length, freq=freq_map[selected_frequency])
        forecast = model.predict(future)

        # Display Forecast Data
        st.subheader("🔍 Forecasted Data Preview")
        st.dataframe(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail())

        # Provide Download Button
        st.markdown("### Download Forecast Results")
        forecast_buffer = BytesIO()
        forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].to_excel(forecast_buffer, index=False)
        st.download_button(
            label="📥 Download Excel",
            data=forecast_buffer,
            file_name="financial_forecast_results.xlsx"
        )

        # Plot Forecast
        st.subheader("📈 Forecast Visualization")
        fig1 = model.plot(forecast, xlabel="Date", ylabel=target_column)
        st.pyplot(fig1)

        # Forecast Components
        st.subheader("📊 Forecast Components")
        fig2 = model.plot_components(forecast)
        st.pyplot(fig2)

        # Summaries for AI
        if len(forecast) >= forecast_length:
            forecast_period = forecast.tail(forecast_length)
        else:
            forecast_period = forecast

        forecast_summary = f"""
Financial Forecast Summary:
- Forecasted Period: {forecast_period['ds'].iloc[0].strftime('%Y-%m-%d')} to {forecast_period['ds'].iloc[-1].strftime('%Y-%m-%d')}
- Expected Range:
  - Lower Bound: ${forecast_period['yhat_lower'].min():,.2f}
  - Upper Bound: ${forecast_period['yhat_upper'].max():,.2f}
- Average Forecasted Value: ${forecast_period['yhat'].mean():,.2f}
"""

        # Send to LLM for insights
        st.subheader("🤖 AI-Generated Strategic Insights")

        # Construct the prompt for the model
        messages = [
            {
                "role": "system", 
                "content": "You are an expert FP&A analyst providing insights on financial forecasts."
            },
            {
                "role": "user", 
                "content": (
                    f"The financial forecast is summarized below:\n\n"
                    f"{forecast_summary}\n\n"
                    "Please provide a detailed analysis including:\n"
                    "1. Key trends or anomalies observed.\n"
                    "2. Potential reasons or drivers behind these trends.\n"
                    "3. Strategic recommendations for stakeholders.\n"
                )
            }
        ]

        try:
            response = client.chat.completions.create(
                messages=messages,
                model="llama3-8b-8192",
            )
            ai_commentary = response.choices[0].message.content
        except Exception as e:
            ai_commentary = f"Error retrieving AI commentary: {str(e)}"

        # Display AI Commentary
        st.subheader("💡 AI-Powered Forecast Insights")
        st.write(ai_commentary)

else:
    st.info("Please upload an Excel file to get started.")
