from src.graph.state import AgentState
from langchain_core.runnables import RunnableConfig

async def commit_node(state: AgentState, config: RunnableConfig):
    """
    Final commit node: Simplified to bypass report persistence for now.
    Report saving will be reintroduced in Milestone 5 for daily portfolio reports.
    """
    # For now, we just clear the pending report to let the graph finish gracefully.
    return {"pending_report": None}
