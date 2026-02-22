import asyncio
from src.graph import create_graph

async def main():
    app = create_graph()
    initial_state = {
        "messages": [],
        "portfolio": [{"symbol": "AAPL", "quantity": 10, "avg_cost": 150}],
        "research_data": {},
        "user_question": "Analyze AAPL",
        "focus_symbols": [],
        "analysis_report": "",
        "next_agent": "",
        "high_level_plan": [],
        "research_plan": {},
        "debate_output": {},
        "analysis_cache_key": "",
        "revision_count": 0
    }
    
    try:
        for s in app.stream(initial_state, subgraphs=True):
            print(s)
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
