import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
import sys
from langchain_core.messages import HumanMessage, AIMessage
from datetime import datetime

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Load env if exists
load_dotenv()

from src.database.database import get_db, init_db
from src.database.crud import add_transaction, get_holdings, cleanup_expired_cache
from src.graph import create_graph

# Page Config
st.set_page_config(page_title="Stock Planner", layout="wide")

# Initialize DB
init_db()

if not os.environ.get("OPENAI_API_KEY"):
    st.error("🔑 OPENAI_API_KEY not found in .env file. Please add it to run the application.")
    st.stop()

# Session State for Analysis
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "debate_output" not in st.session_state:
    st.session_state["debate_output"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Reusable function to run the agent graph
def run_agent_graph(holdings, user_input=None, history=None):
    with st.status("Agents are researching market data...", expanded=True) as status:
        try:
            # Prepare State
            client_ua = ""
            if hasattr(st, "context") and hasattr(st.context, "headers"):
                client_ua = st.context.headers.get("User-Agent", "")
            initial_state = {
                "session_context": {
                    "messages": history or [],
                    "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_agent": client_ua,
                    "revision_count": 0
                },
                "user_context": {
                    "portfolio": holdings,
                },
                "user_input": user_input or "",
                "output": "",
                "agent_interactions": []
            }
            
            # Run Graph
            app = create_graph()
            
            final_report = ""
            debate_output = {}
            shown_interaction_ids = set()
                    
            # Stream events from the graph including subgraphs
            for event in app.stream(initial_state, subgraphs=True):
                # LangGraph with subgraphs=True yields tuples: (namespace, state_update)
                namespace, s = event
                
                if not namespace and "__end__" in s:
                    final_state = s["__end__"]
                    final_report = final_state.get("output", "")
                    
                    # Extract debate arguments from individual agent interactions
                    bull_interaction = next((i for i in reversed(final_state.get("agent_interactions", [])) if i.get("agent") == "bull"), None)
                    bear_interaction = next((i for i in reversed(final_state.get("agent_interactions", [])) if i.get("agent") == "bear"), None)
                    
                    debate_output = {
                        "bull_argument": bull_interaction.get("answer", "") if bull_interaction else "No bullish case provided.",
                        "bear_argument": bear_interaction.get("answer", "") if bear_interaction else "No bearish case provided.",
                    }
                    continue
                    
                if "__end__" not in s:
                    for agent_name, agent_data in s.items():
                        # Extract interactions for general status update
                        interactions = agent_data.get("agent_interactions", [])
                        
                        for interaction in interactions:
                            int_id = interaction.get("id", "?")
                            if int_id in shown_interaction_ids:
                                continue
                            shown_interaction_ids.add(int_id)
                            
                            int_agent = interaction.get("agent", agent_name)
                            int_next = interaction.get("next_agent", "N/A")
                            
                            icon = "🤖"
                            if int_agent == "supervisor": icon = "👔"
                            elif int_agent == "research": icon = "🔍"
                            elif int_agent == "generator": icon = "⚖️"
                            elif int_agent == "bull": icon = "📈"
                            elif int_agent == "bear": icon = "📉"
                            elif int_agent == "synthesizer": icon = "📝"
                            elif int_agent == "off_topic": icon = "👋"
                            elif int_agent == "summarizer": icon = "✨"
                            elif int_agent == "analyst": icon = "📊"
                            
                            status.write(f"{icon} **[{int_id}] {int_agent.capitalize()}** completed. Routing to **{int_next.capitalize()}**.")
                            
                            answer_text = interaction.get("answer", "")
                            if answer_text:
                                with status.expander(f"View details from {int_agent.capitalize()}", expanded=False) if hasattr(status, "expander") else st.expander(f"View details from {int_agent.capitalize()}", expanded=False):
                                    st.markdown(answer_text)
                        
                        if interactions:
                            curr_interaction = interactions[-1]
                            int_id = curr_interaction.get("id", "?")
                            next_dest = curr_interaction.get("next_agent", "N/A")
                            status.update(label=f"[{int_id}] Routing to {next_dest.capitalize()}...", state="running")
    
                        if "output" in agent_data:
                            final_report = agent_data["output"]
            
            status.update(label="Process Complete!", state="complete", expanded=False)
            return final_report, debate_output
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Graph execution failed:\\n{error_trace}")
            status.update(label="Error in analysis.", state="error")
            return f"An error occurred: {e}", debate_output
                
    # Perform cache maintenance outside the agent graph
    with get_db() as db:
        cleanup_expired_cache(db)
            
    return final_report, debate_output



# --- Main App ---
st.title("📈 AI Stock Planner")

tab1, tab2, tab3 = st.tabs(["Manage Portfolio", "AI Analysis", "Ask AI"])

# --- Tab 1: Portfolio Management ---
with tab1:
    st.header("Your Holdings")
    with next(get_db()) as db:
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
            with next(get_db()) as db:
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
            
        st.divider()
        st.markdown(st.session_state["analysis_result"])

# --- Tab 3: Ask AI (Chat Interface) ---
with tab3:
    st.header("Chat with your AI Advisor")
    
    messages_container = st.container(height=700, border=False)
    
    with messages_container:
        # Display chat messages from history on app rerun
        for message in st.session_state["chat_history"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # React to user input
    if user_q := st.chat_input("Ask a question about your portfolio or the market..."):
        if not os.environ.get("OPENAI_API_KEY"):
            st.error("Missing OpenAI API Key.")
        elif not holdings:
            st.warning("Portfolio is empty.")
        else:
            with messages_container:
                # Display user message in chat message container
                st.chat_message("human").markdown(user_q)
                
                # Format history for Langchain BaseMessages
                langchain_history = []
                for msg in st.session_state["chat_history"]:
                    if msg["role"] == "human":
                        langchain_history.append(HumanMessage(content=msg["content"]))
                    else:
                        langchain_history.append(AIMessage(content=msg["content"]))
                        
                # Add new user message to session state
                st.session_state["chat_history"].append({"role": "human", "content": user_q})
                
                with st.chat_message("ai"):
                    report, debate = run_agent_graph(holdings, user_input=user_q, history=langchain_history)
                    if report:
                        if debate:
                            with st.expander("View Adversarial Debate Details", expanded=False):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.subheader("🐂 Bull Case")
                                    st.markdown(debate.get("bull_argument", ""))
                                with col2:
                                    st.subheader("🐻 Bear Case")
                                    st.markdown(debate.get("bear_argument", ""))
                        st.markdown(report)
                        st.session_state["chat_history"].append({"role": "ai", "content": report})
                    else:
                        err_msg = "Sorry, I encountered an error answering your question."
                        st.markdown(err_msg)
                        st.session_state["chat_history"].append({"role": "ai", "content": err_msg})
