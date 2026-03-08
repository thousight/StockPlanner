from typing import Optional
from langchain_core.runnables import RunnableConfig
from src.graph.state import AgentState
from src.graph.agents.analyst.subgraph import create_debate_graph
from src.graph.utils.agents import with_logging, get_next_interaction_id, create_interaction

@with_logging
async def analyst_agent(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Adversarial Analyst: Orchestrates a 'Bull vs. Bear' debate out of research results, and synthesizes a final report.
    """
    user_input = state.get("user_input", "Analyze the current portfolio and provide recommendations.")
    
    # Retrieve all research data from specialized interactions
    research_agents = ["fundamental_researcher", "sentiment_researcher", "macro_researcher", "narrative_researcher", "code_generator", "research"]
    research_data = []
    for interaction in state.get("agent_interactions", []):
        if interaction.get("agent") in research_agents:
            research_data.append(f"--- Data from {interaction['agent']} ---\n{interaction['answer']}")
    
    research_context = "\n\n".join(research_data)

    # Analysis is now always computed fresh
    debate_graph = create_debate_graph()
    debate_input = {
        "research_data": research_context,
        "user_input": user_input,
        "session_context": state.get("session_context", {}),
        "agent_interactions": state.get("agent_interactions", [])
    }
    
    debate_results = await debate_graph.ainvoke(debate_input, config=config)
    report = debate_results.get("final_report", "")
    
    initial_interactions_count = len(state.get("agent_interactions", []))

    # Get the newly generated interactions from subgraph
    new_interactions = debate_results.get("agent_interactions", [])[initial_interactions_count:]
    
    # Parse Follow-up from report
    next_agent = "summarizer"
    if "FOLLOW_UP:" in report:
        follow_up_line = report.split("FOLLOW_UP:")[-1].strip()
        if "None" not in follow_up_line:
            # Format is [agent_name] | [specific_question]
            try:
                agent_name = follow_up_line.split("|")[0].strip()
                if agent_name in ["fundamental_researcher", "sentiment_researcher", "macro_researcher", "code_generator", "supervisor"]:
                    next_agent = agent_name
            except Exception:
                pass

    # Increment code_revision_count if routing to code_generator
    code_revision_count = state.get("code_revision_count", 0)
    if next_agent == "code_generator":
        code_revision_count += 1

    # Add the Analyst's own final output interaction
    analyst_interaction = create_interaction(
        state,
        agent="analyst",
        answer=report,
        next_agent=next_agent,
        debate_output={
            "bull_argument": debate_results.get("bull_argument", ""),
            "bear_argument": debate_results.get("bear_argument", ""),
            "confidence_score": debate_results.get("confidence_score", 0)
        }
    )
    # Adjustment for multiple interactions from subgraph
    analyst_interaction["id"] += len(new_interactions)
    new_interactions.append(analyst_interaction)
    
    return {
        "agent_interactions": new_interactions,
        "code_revision_count": code_revision_count
    }
