import sys, os
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.getcwd())
from src.graph import create_graph

initial_state = {
    "messages": [],
    "portfolio": [],
    "research_data": {},
    "user_question": "Analyze NVDA",
    "focus_symbols": [],
    "analysis_report": "",
    "next_agent": "",
    "high_level_plan": [],
    "research_plan": {},
    "debate_output": {},
    "analysis_cache_key": "",
    "revision_count": 0
}

app = create_graph()
for s in app.stream(initial_state):
    print(s)
