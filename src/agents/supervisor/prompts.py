from langchain_core.prompts import ChatPromptTemplate

SUPERVISOR_PROMPT = ChatPromptTemplate.from_template("""
You are a Strategic Investment Planner. Your role is to decompose a user's financial request into a high-level plan of a list of tasks and delegate each task to the appropriate specialized agent.

Current Context:
{current_context}

Available Agents:
{available_agents}

Your Task:
1. Determine the first or next step required to fulfill the user's request.
2. Identify the 'next_agent' to execute this step from the Available Agents list.
""")

SUPERVISOR_PLAN_PROMPT = ChatPromptTemplate.from_template("""
Determine the next steps and the agent for the plan.
""")