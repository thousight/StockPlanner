import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

import sys

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(project_root)

# Load env if exists
load_dotenv()

from src.database.database import get_db, init_db
from src.database.crud import add_transaction, get_holdings, get_transactions
from src.agents.graph import create_graph

# Page Config
st.set_page_config(page_title="Stock Planner MVP", layout="wide")

# Initialize DB
init_db()

# Session State for Analysis
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

# --- Sidebar ---
st.sidebar.title="Configuration"
api_key = st.sidebar.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

if not os.environ.get("OPENAI_API_KEY"):
    st.sidebar.warning("Please enter your OpenAI API Key to use the AI Analysis features.")

# --- Main App ---
st.title("📈 AI Stock Planner (MVP)")

tab1, tab2 = st.tabs(["Manage Portfolio", "AI Analysis"])

# --- Tab 1: Portfolio Management ---
with tab1:
    st.header("Your Holdings")
    
    db = next(get_db())
    holdings = get_holdings(db)
    
    if holdings:
        df_holdings = pd.DataFrame(holdings)
        st.dataframe(df_holdings, width='stretch')
        
        total_value = df_holdings['total_cost'].sum() # Approximation based on cost for now
        st.metric("Total Invested", f"${total_value:,.2f}")
    else:
        st.info("No holdings found. Add a transaction below.")
        
    st.divider()
    st.subheader("Add Transaction")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        symbol = st.text_input("Ticker Symbol (e.g. AAPL)").upper()
    with col2:
        action = st.selectbox("Action", ["BUY", "SELL"])
    with col3:
        qty = st.number_input("Quantity", min_value=0.01, step=1.0)
    with col4:
        price = st.number_input("Price per Share", min_value=0.01, step=0.1)
        
    if st.button("Add Transaction"):
        if symbol and qty > 0 and price > 0:
            add_transaction(db, symbol, action, qty, price)
            st.success(f"Added {action} {qty} {symbol} @ ${price}")
            st.rerun()
        else:
            st.error("Please fill all fields.")
            
    st.divider()
    st.subheader("Transaction History")
    transactions = get_transactions(db)
    if transactions:
        data = [{
            "Date": t.date,
            "Symbol": t.symbol,
            "Action": t.action,
            "Qty": t.quantity,
            "Price": t.price_per_share
        } for t in transactions]
        st.dataframe(pd.DataFrame(data), width='stretch')

# --- Tab 2: AI Analysis ---
with tab2:
    st.header("Daily Portfolio Research & Analysis")
    
    if st.button("Run AI Analysis"):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("Missing OpenAI API Key.")
        elif not holdings:
            st.warning("Portfolio is empty.")
        else:
            with st.spinner("Agents are researching market data..."):
                try:
                    # Prepare State
                    initial_state = {
                        "messages": [],
                        "portfolio": holdings,
                        "research_data": {},
                        "analysis_report": ""
                    }
                    
                    # Run Graph
                    app = create_graph()
                    result = app.invoke(initial_state)
                    
                    st.session_state["analysis_result"] = result["analysis_report"]
                    st.success("Analysis Complete!")
                except Exception as e:
                    st.error(f"Error running analysis: {e}")
                    
    if st.session_state["analysis_result"]:
        st.markdown(st.session_state["analysis_result"])
