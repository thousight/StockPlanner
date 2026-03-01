from src.database.session import AsyncSessionLocal
from src.database.models import Report
from src.graph.state import AgentState
from langchain_core.runnables import RunnableConfig

async def commit_node(state: AgentState, config: RunnableConfig):
    """
    Final commit node: Persists the pending report to the database.
    """
    pending_report = state.get("pending_report")
    if not pending_report:
        return {}
    
    thread_id = config.get("configurable", {}).get("thread_id", "unknown")
    
    async with AsyncSessionLocal() as session:
        # Use content from pending_report if available, otherwise fallback to final output
        report_content = pending_report.get("content") or state.get("output")
        symbol = pending_report.get("symbol")
        
        if report_content:
            report = Report(
                thread_id=thread_id,
                symbol=symbol,
                content=report_content,
            )
            session.add(report)
            await session.commit()
            print(f"DEBUG: Report committed to database for thread {thread_id} and symbol {symbol}.")
        else:
            print("DEBUG: No content to commit for report.")
            
    # Clear pending_report after successful write
    return {"pending_report": None}
