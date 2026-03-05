from langchain_core.prompts import ChatPromptTemplate

SUPERVISOR_PROMPT = ChatPromptTemplate.from_template("""
You are a Strategic Investment Planner. Your role is to decompose a user's financial request into a high-level plan and delegate to our specialized research squad.

Current Context:
{current_context}

Available Agents:
{available_agents}

Your Task:
1. Analyze the user's request and the chat history.
2. Identify which specialized researchers are needed from the Available Agents list.
3. You can trigger MULTIPLE researchers in parallel by returning a list if the request is multi-faceted.
   - For example, if the request is "Analyze AAPL fundamentals vs social sentiment", return both `fundamental_researcher` and `sentiment_researcher`.
4. If the user asks for a translation of a previous answer, or a simple follow-up, route to the single most appropriate agent.

Output the 'next_agents' as a list of strings from the Available Agents list.
""")

SUPERVISOR_PLAN_PROMPT = ChatPromptTemplate.from_template("""
Determine the next steps and the list of agents for the plan.
""")
