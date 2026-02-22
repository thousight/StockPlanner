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
st.set_page_config(page_title="Stock Planner", layout="wide")

# Initialize DB
init_db()

# Session State for Analysis
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "debate_output" not in st.session_state:
    st.session_state["debate_output"] = None

# Reusable function to run the agent graph
def run_agent_graph(holdings, user_question=None):
    with st.status("Agents are researching market data...", expanded=True) as status:
        try:
            # Prepare State
            initial_state = {
                "messages": [],
                "portfolio": holdings,
                "research_data": {},
                "user_question": user_question or "",
                "focus_symbols": [],
                "analysis_report": "",
                "next_node": "",
                "high_level_plan": [],
                "research_plan": {},
                "debate_output": {},
                "analysis_cache_key": "",
                "revision_count": 0
            }
            
            # Run Graph
            app = create_graph()
            
            final_report = ""
            debate_output = {}
            
            # Stream events from the graph
            for s in app.stream(initial_state):
                if "__end__" not in s:
                    node_name = list(s.keys())[0]
                    node_data = s[node_name]
                    
                    if node_name == "supervisor":
                        plan = node_data.get("high_level_plan", [])
                        next_worker = node_data.get("next_node", "N/A")
                        status.write(f"**Supervisor Plan:** {', '.join(plan)}")
                        status.update(label=f"Supervisor routing to: {next_worker.capitalize()}...", state="running")
                    elif node_name == "research":
                        local_plan = node_data.get("research_plan", {}).get("queries", [])
                        status.write(f"**Research Plan:** {', '.join(local_plan)}")
                        status.update(label="Researching market data...", state="running")
                    elif node_name == "analyst":
                        status.update(label="Orchestrating adversarial debate...", state="running")
                        # Capture results from analyst node if it's the last step
                        if "analysis_report" in node_data:
                            final_report = node_data["analysis_report"]
                            debate_output = node_data.get("debate_output", {})
                else:
                    # Final state extraction if not caught during stream
                    final_state = s["__end__"]
                    final_report = final_state.get("analysis_report", "")
                    debate_output = final_state.get("debate_output", {})
            
            status.update(label="Process Complete!", state="complete", expanded=False)
            return final_report, debate_output
        except Exception as e:
            status.update(label="Error occurred", state="error")
            st.error(f"Error running agent: {e}")
            return None, None

# --- Sidebar ---
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

if not os.environ.get("OPENAI_API_KEY"):
    st.sidebar.warning("Please enter your OpenAI API Key to use the AI Analysis features.")

# --- Main App ---
st.title("📈 AI Stock Planner")

tab1, tab2, tab3 = st.tabs(["Manage Portfolio", "AI Analysis", "Ask AI"])

# --- Tab 1: Portfolio Management ---
with tab1:
    st.header("Your Holdings")
    db = next(get_db())
    holdings = get_holdings(db)
    
    if holdings:
        df_holdings = pd.DataFrame(holdings)
        st.dataframe(df_holdings, width='stretch')
        total_value = df_holdings['total_cost'].sum()
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

# --- Tab 2: AI Analysis ---
with tab2:
    st.header("Portfolio Research & Analysis")
    if st.button("Run AI Analysis"):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("Missing OpenAI API Key.")
        elif not holdings:
            st.warning("Portfolio is empty.")
        else:
            report, debate = run_agent_graph(holdings)
            if report:
                st.session_state["analysis_result"] = report
                st.session_state["debate_output"] = debate
                st.success("Analysis Ready!")
                    
    if st.session_state["analysis_result"]:
        # Show adversarial debate in expanders
        if st.session_state["debate_output"]:
            debate = st.session_state["debate_output"]
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("🐂 Bull Analyst Case", expanded=False):
                    st.markdown(debate.get("bull_argument", "No bullish case provided."))
            with col2:
                with st.expander("🐻 Bear Analyst Case", expanded=False):
                    st.markdown(debate.get("bear_argument", "No bearish case provided."))
            st.caption(f"**Moderator Confidence Score:** {debate.get('confidence_score', 'N/A')}/100")
            
        st.divider()
        st.markdown(st.session_state["analysis_result"])

# --- Tab 3: Ask AI ---
with tab3:
    st.header("Ask AI about your Portfolio")
    user_q = st.text_input("Your Question:")
    if st.button("Ask AI"):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("Missing OpenAI API Key.")
        elif not holdings:
            st.warning("Portfolio is empty.")
        elif not user_q:
            st.error("Please enter a question.")
        else:
            report, debate = run_agent_graph(holdings, user_question=user_q)
            if report:
                st.session_state["analysis_result"] = report # Shared state for report
                st.session_state["debate_output"] = debate
                st.success("Answer Ready!")

    if st.session_state["analysis_result"]:
         # Reuse the same display logic as Tab 2
         if st.session_state["debate_output"]:
            debate = st.session_state["debate_output"]
            with st.expander("View Adversarial Debate Details", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🐂 Bull Case")
                    st.markdown(debate.get("bull_argument", ""))
                with col2:
                    st.subheader("🐻 Bear Case")
                    st.markdown(debate.get("bear_argument", ""))
         st.markdown(st.session_state["analysis_result"])
