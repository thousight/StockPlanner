from src.database.session import AsyncSessionLocal
from src.database.models import Report, ReportCategory
from src.graph.state import AgentState
from src.services.complexity import requires_interrupt
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

async def commit_node(state: AgentState, config: RunnableConfig):
    """
    Final commit node: Persists the pending report to the database with conditional safety interrupts.
    """
    pending_report = state.get("pending_report")
    if not pending_report:
        return {}

    # 1. Ensure Off-Topic agent results never generate reports.
    interactions = state.get("agent_interactions", [])
    if any(i.get("agent") == "off_topic" for i in interactions):
        return {"pending_report": None}

    # 2. Complexity check for safety interrupt
    score = pending_report.get("complexity_score", 0.0)
    if requires_interrupt(score):
        # Payload for interrupt includes Title, Topic, Category
        interrupt_payload = {
            "title": pending_report.get("title"),
            "topic": pending_report.get("topic"),
            "category": pending_report.get("category"),
            "message": "Safety Check: Final verification required before committing results. Please approve to continue or reject to skip."
        }
        
        # This will pause execution. When resumed, it returns the user's action.
        resume_signal = interrupt(interrupt_payload)
        
        # 3. Handle rejection (Acknowledge & Continue pattern)
        if isinstance(resume_signal, str) and resume_signal.lower() == "reject":
            return {
                "pending_report": None,
                "output": "Understood. I've acknowledged your request and will not commit this report to the database. Is there anything else you'd like to discuss?"
            }

    # 4. Standard commit logic
    thread_id = config.get("configurable", {}).get("thread_id", "unknown")
    user_id = state.get("user_context", {}).get("user_id", "unknown")
    
    async with AsyncSessionLocal() as session:
        # Use content from pending_report if available, otherwise fallback to final output
        report_content = pending_report.get("content") or state.get("output")
        symbol = pending_report.get("symbol")
        
        if report_content:
            # Map string category to Enum
            try:
                category_enum = ReportCategory[pending_report.get("category", "GENERAL")]
            except KeyError:
                category_enum = ReportCategory.GENERAL

            report = Report(
                user_id=user_id,
                thread_id=thread_id,
                title=pending_report.get("title", "Analysis Report"),
                topic=pending_report.get("topic", "General"),
                symbol=symbol,
                category=category_enum,
                tags=pending_report.get("tags", []),
                content=report_content,
            )
            session.add(report)
            await session.commit()
            await session.refresh(report) # Ensure report.id is populated
            report_id = report.id
            print(f"DEBUG: Report committed to database for thread {thread_id} and symbol {symbol}. ID: {report_id}")
        else:
            print("DEBUG: No content to commit for report.")
            report_id = None
            
    # Clear pending_report after successful write, and store last_report_id
    return {"pending_report": None, "last_report_id": report_id}
