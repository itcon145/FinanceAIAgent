import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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
st.set_page_config(page_title="Monte Carlo Simulation AI", page_icon="📊", layout="wide")
st.title("📊 Monte Carlo Simulation AI – Risk & Forecast Analysis")
st.write("Upload financial data and run Monte Carlo simulations to assess risk and future scenarios!")

# File uploader
uploaded_file = st.file_uploader("📂 Upload your dataset (Excel format)", type=["xlsx"])

if uploaded_file:
    # Read the Excel file
    df = pd.read_excel(uploaded_file)

    # Check for required columns
    required_columns = ["Revenue", "COGS", "Operating Expenses", "Interest Rate Impact", "Market Growth Rate"]
    if not all(col in df.columns for col in required_columns):
        st.error("⚠️ The uploaded file must contain 'Revenue', 'COGS', 'Operating Expenses', 'Interest Rate Impact', and 'Market Growth Rate' columns!")
        st.stop()

    # Monte Carlo parameters
    num_simulations = 1000  # Number of Monte Carlo runs
    forecast_months = 12  # How many months ahead to simulate

    # Define uncertainty ranges based on historical data
    revenue_mean = df["Revenue"].mean()
    revenue_std = df["Revenue"].std()

    cogs_mean_pct = (df["COGS"] / df["Revenue"]).mean()
    cogs_std_pct = (df["COGS"] / df["Revenue"]).std()

    op_exp_mean = df["Operating Expenses"].mean()
    op_exp_std = df["Operating Expenses"].std()

    interest_mean = df["Interest Rate Impact"].mean()
    interest_std = df["Interest Rate Impact"].std()

    market_growth_mean = df["Market Growth Rate"].mean()
    market_growth_std = df["Market Growth Rate"].std()

    # Run Monte Carlo simulations
    simulated_net_profits = []

    for _ in range(num_simulations):
        simulated_revenue = np.random.normal(revenue_mean, revenue_std, forecast_months)
        simulated_cogs = simulated_revenue * np.random.normal(cogs_mean_pct, cogs_std_pct, forecast_months)
        simulated_op_exp = np.random.normal(op_exp_mean, op_exp_std, forecast_months)
        simulated_interest = simulated_revenue * np.random.normal(interest_mean, interest_std, forecast_months)

        simulated_gross_profit = simulated_revenue - simulated_cogs
        simulated_net_profit = simulated_gross_profit - simulated_op_exp - simulated_interest

        total_net_profit = np.sum(simulated_net_profit)
        simulated_net_profits.append(total_net_profit)

    # Convert results to DataFrame
    sim_results_df = pd.DataFrame({"Total Net Profit": simulated_net_profits})

    # Plot the distribution of simulated net profits
    st.subheader("📊 Monte Carlo Simulation: Net Profit Distribution")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(sim_results_df["Total Net Profit"], bins=50, kde=True, color="blue", ax=ax)
    ax.axvline(sim_results_df["Total Net Profit"].mean(), color="red", linestyle="dashed", linewidth=2, label="Mean")
    ax.axvline(np.percentile(sim_results_df["Total Net Profit"], 5), color="green", linestyle="dashed", linewidth=2, label="5th Percentile")
    ax.axvline(np.percentile(sim_results_df["Total Net Profit"], 95), color="green", linestyle="dashed", linewidth=2, label="95th Percentile")
    ax.set_title("Monte Carlo Simulation: Net Profit Distribution")
    ax.set_xlabel("Total Net Profit (12 months)")
    ax.set_ylabel("Frequency")
    ax.legend()
    st.pyplot(fig)

    # Summary statistics
    mean_profit = sim_results_df['Total Net Profit'].mean()
    worst_case = np.percentile(sim_results_df['Total Net Profit'], 5)
    best_case = np.percentile(sim_results_df['Total Net Profit'], 95)
    std_dev = sim_results_df['Total Net Profit'].std()

    st.subheader("📊 Monte Carlo Simulation Results (Net Profit for Next 12 Months)")
    st.write(f"**Mean Net Profit:** ${mean_profit:,.2f}")
    st.write(f"**5th Percentile (Worst Case):** ${worst_case:,.2f}")
    st.write(f"**95th Percentile (Best Case):** ${best_case:,.2f}")
    st.write(f"**Standard Deviation:** ${std_dev:,.2f}")

    # AI Section
    st.subheader("🤖 AI-Powered Risk Analysis & Strategic Insights")

    # AI Summary of Monte Carlo Simulation Results
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an AI financial strategist providing insights on Monte Carlo simulation results."},
            {"role": "user", "content": f"Here are the Monte Carlo simulation results:\nMean Profit: ${mean_profit:,.2f}\nWorst Case (5th percentile): ${worst_case:,.2f}\nBest Case (95th percentile): ${best_case:,.2f}\nStandard Deviation: ${std_dev:,.2f}\nWhat are the key insights and risk factors?"}
        ],
        model="llama3-8b-8192",
    )

    st.write(response.choices[0].message.content)

    # AI Chat - Users Can Ask Questions
    st.subheader("🗣️ Chat with AI About Monte Carlo Results")

    user_query = st.text_input("🔍 Ask the AI about Monte Carlo simulation outcomes:")
    if user_query:
        chat_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI financial analyst helping users understand risk assessment using Monte Carlo simulations."},
                {"role": "user", "content": f"Monte Carlo Simulation Data:\nMean Profit: ${mean_profit:,.2f}\nWorst Case (5th percentile): ${worst_case:,.2f}\nBest Case (95th percentile): ${best_case:,.2f}\nStandard Deviation: ${std_dev:,.2f}\n{user_query}"}
            ],
            model="llama3-8b-8192",
        )
        st.write(chat_response.choices[0].message.content)
