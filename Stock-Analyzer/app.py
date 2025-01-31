import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
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
st.set_page_config(page_title="Stock Market AI", page_icon="📈", layout="wide")
st.title("📈 Stock Market AI – Real-Time Analysis & Insights")
st.write("Enter a company name or stock ticker to fetch live market data, charts, and AI-driven insights!")

# User Input
company_name = st.text_input("🔍 Enter a Company Name or Ticker:", "AAPL")  # Default: Apple Inc.

if st.button("🚀 Get Stock Data"):
    try:
        # Fetch stock data
        stock = yf.Ticker(company_name)
        stock_data = stock.history(period="1y")  # 1-year historical data

        # Display Company Info
        st.subheader(f"🏢 Company Overview: {stock.info.get('shortName', 'N/A')}")
        st.write(f"**Sector:** {stock.info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {stock.info.get('industry', 'N/A')}")
        st.write(f"**Market Cap:** {stock.info.get('marketCap', 'N/A'):,}")
        st.write(f"**52-Week High:** ${stock.info.get('fiftyTwoWeekHigh', 'N/A'):,}")
        st.write(f"**52-Week Low:** ${stock.info.get('fiftyTwoWeekLow', 'N/A'):,}")
        st.write(f"**Dividend Yield:** {stock.info.get('dividendYield', 'N/A')}%")

        # Plot Stock Price Trends with Plotly
        st.subheader("📊 Stock Price Trend (Last Year)")
        fig_price = px.line(stock_data, x=stock_data.index, y="Close", title=f"{company_name} Stock Price Trend",
                            labels={"Close": "Stock Price (USD)", "index": "Date"}, template="plotly_dark")
        st.plotly_chart(fig_price)

        # Moving Averages
        stock_data["50-day MA"] = stock_data["Close"].rolling(window=50).mean()
        stock_data["200-day MA"] = stock_data["Close"].rolling(window=200).mean()

        st.subheader("📈 Moving Averages (50-day & 200-day)")
        fig_ma = go.Figure()
        fig_ma.add_trace(go.Scatter(x=stock_data.index, y=stock_data["Close"], mode="lines", name="Close Price", line=dict(color="blue")))
        fig_ma.add_trace(go.Scatter(x=stock_data.index, y=stock_data["50-day MA"], mode="lines", name="50-day MA", line=dict(color="orange", dash="dot")))
        fig_ma.add_trace(go.Scatter(x=stock_data.index, y=stock_data["200-day MA"], mode="lines", name="200-day MA", line=dict(color="red", dash="dot")))
        fig_ma.update_layout(title=f"{company_name} Moving Averages", xaxis_title="Date", yaxis_title="Stock Price (USD)", template="plotly_dark")
        st.plotly_chart(fig_ma)

        # Trading Volume
        st.subheader("📊 Trading Volume")
        fig_volume = px.bar(stock_data, x=stock_data.index, y="Volume", title=f"{company_name} Trading Volume",
                            labels={"Volume": "Shares Traded", "index": "Date"}, template="plotly_dark")
        st.plotly_chart(fig_volume)

        # AI Section
        st.subheader("🤖 AI-Powered Company & Industry Insights")

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI financial analyst providing stock market insights based on company data."},
                {"role": "user", "content": f"Here is the stock market data for {company_name}:\n"
                                            f"Sector: {stock.info.get('sector', 'N/A')}\n"
                                            f"Industry: {stock.info.get('industry', 'N/A')}\n"
                                            f"Market Cap: {stock.info.get('marketCap', 'N/A'):,}\n"
                                            f"52-Week High: ${stock.info.get('fiftyTwoWeekHigh', 'N/A'):,}\n"
                                            f"52-Week Low: ${stock.info.get('fiftyTwoWeekLow', 'N/A'):,}\n"
                                            f"Dividend Yield: {stock.info.get('dividendYield', 'N/A')}%\n"
                                            f"What are the key insights about this company and its industry?"}
            ],
            model="llama3-8b-8192",
        )

        st.write(response.choices[0].message.content)

        # AI Chat - Users Can Ask Questions
        st.subheader("🗣️ Chat with AI About This Stock")

        user_query = st.text_input("🔍 Ask the AI about this company or industry:")
        if user_query:
            chat_response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an AI financial analyst providing insights on stock market trends and companies."},
                    {"role": "user", "content": f"Stock Market Data for {company_name}:\n"
                                                f"Sector: {stock.info.get('sector', 'N/A')}\n"
                                                f"Industry: {stock.info.get('industry', 'N/A')}\n"
                                                f"Market Cap: {stock.info.get('marketCap', 'N/A'):,}\n"
                                                f"{user_query}"}
                ],
                model="llama3-8b-8192",
            )
            st.write(chat_response.choices[0].message.content)

    except Exception as e:
        st.error(f"⚠️ Error fetching stock data: {e}")
