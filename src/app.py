import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
import sys

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
            from datetime import datetime
            client_ua = ""
            if hasattr(st, "context") and hasattr(st.context, "headers"):
                client_ua = st.context.headers.get("User-Agent", "")
            initial_state = {
                "messages": history or [],
                "portfolio": holdings,
                "user_input": user_input or "",
                "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_agent": client_ua,
                "output": "",
                "high_level_plan": [],
                "agent_interactions": [],
                "analysis_cache_key": "",
                "revision_count": 0
            }
            
            # Run Graph
            app = create_graph()
            
            final_report = ""
            debate_output = {}
                    
            # Stream events from the graph including subgraphs
            for event in app.stream(initial_state, subgraphs=True):
                # LangGraph with subgraphs=True yields tuples: (namespace, state_update)
                namespace, s = event
                
                if not namespace and "__end__" in s:
                    final_state = s["__end__"]
                    final_report = final_state.get("output", "")
                    # Extract debate_output from interactions
                    analyst_interaction = next((i for i in reversed(final_state.get("agent_interactions", [])) if i.get("agent") == "analyst"), None)
                    debate_output = analyst_interaction.get("debate_output", {}) if analyst_interaction else {}
                    continue
                    
                if "__end__" not in s:
                    agent_name = list(s.keys())[0]
                    agent_data = s[agent_name]
                    
                    # Extract next_agent and ask from interactions for general status update
                    interactions = agent_data.get("agent_interactions", [])
                    curr_interaction = interactions[-1] if interactions else {}
                    int_id = curr_interaction.get("id", "?")
                    step_id = curr_interaction.get("step_id", "?")
                    next_dest = curr_interaction.get("next_agent", "N/A")
                    next_question = curr_interaction.get("next_question", "N/A")
                    
                    status_prefix = f"[{int_id} (Step {step_id})]"
                    status.update(label=f"{status_prefix} Agent {agent_name.capitalize()} working... routing to **{next_dest.capitalize()}** with instructions: *{next_question}*", state="running")
                    
                    if agent_name == "supervisor":
                        plan = agent_data.get("high_level_plan", [])
                        # plan is now a list of dicts: {"id": int, "description": str}
                        plan_md = "\n".join([f"{item['id']}. {item['description']}" for item in plan])
                        status.markdown(f"**Supervisor Plan:**\n{plan_md}")
                        status.update(label=f"{status_prefix} Supervisor routing to **{next_dest.capitalize()}** with instruction: *{next_question}*", state="running")
                    elif agent_name == "research":
                        status.update(label=f"{status_prefix} Researching market data for: *{next_question}*", state="running")
                    elif agent_name == "generator":
                        status.write(f"**Moderator Instructions:** Orchestrating debate...")
                        status.update(label="Analysts preparing arguments...", state="running")
                    elif agent_name == "bull":
                        status.write(f"📈 **Bull Analyst:** Argument prepared.")
                        status.update(label=f"{status_prefix} Bull Analyst completed...", state="running")
                    elif agent_name == "bear":
                        status.write(f"📉 **Bear Analyst:** Argument prepared.")
                        status.update(label=f"{status_prefix} Bear Analyst completed...", state="running")
                    elif agent_name == "synthesizer":
                        status.write(f"⚖️ **Moderator:** Synthesizing final report...")
                        status.update(label="Finalizing report...", state="running")
                    elif agent_name == "off_topic":
                        status.write(f"👋 **Assistant:** Replying to general question...")
                        status.update(label="Formulating response...", state="running")
                    elif agent_name == "summarizer":
                        status.write(f"📝 **Summarizer:** Synthesizing final response...")
                        status.update(label=f"{status_prefix} Creating final answer...", state="running")
                    elif agent_name == "analyst":
                        # The top-level analyst node wraps the subgraph
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
            st.caption(f"**Moderator Confidence Score:** {debate.get('confidence_score', 'N/A')}/100")
            
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
                from langchain_core.messages import HumanMessage, AIMessage
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
