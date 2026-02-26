from langchain_core.prompts import ChatPromptTemplate

RESEARCH_PLANNER_SYSTEM_PROMPT = ChatPromptTemplate.from_template("""
You are a Senior Research Analyst. Your goal is to create a detailed local research plan to gather financial and news data for the specified focus areas.

Current Context:
{current_context}

Available Tools:
{available_tools}

Available Next Agents:
{available_next_agents}

Your Task:
1. Define specific search queries or data points to fetch.
2. Use the appropriate tools from the available list. You MUST provide the necessary parameters for each tool using the `tool_params` field (e.g., {{"symbol": "NVDA"}}).
3. Determine the `next_agent` to route to after gathering data.

Output your plan as a structured JSON object.
""")

RESEARCH_PLANNER_PLAN_PROMPT = ChatPromptTemplate.from_template("""
Generate a local research plan.
""")