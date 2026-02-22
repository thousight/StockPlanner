from langchain_core.prompts import ChatPromptTemplate

SUPERVISOR_PROMPT = ChatPromptTemplate.from_template("""
You are a Strategic Investment Planner. Your role is to decompose a user's financial request into a high-level plan of a list of tasks and delegate each task to the appropriate specialized agent.

Current Context:
{current_context}

Available Agents:
{available_agents}

Your Task:
1. Decompose the request into a list of high-level steps (the 'steps').
2. Identify the 'next_agent' to execute the first or next step.
""")

SUPERVISOR_PLAN_PROMPT = ChatPromptTemplate.from_template("""
Determine the next steps and the agent for the plan.
""")