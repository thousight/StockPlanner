from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from src.graph.state import AgentState
from src.graph.agents.off_topic.prompts import OFF_TOPIC_SYSTEM_PROMPT
from src.graph.utils.prompt import convert_state_to_prompt
from src.graph.agents.off_topic.next_agents import get_off_topic_next_agents_prompt
from src.graph.agents.off_topic.off_topic_answer import OffTopicAnswer
from src.graph.utils.agents import get_next_interaction_id, with_logging

@with_logging
async def off_topic_agent(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Off-Topic Agent: ONLY handles casual conversation, greetings (like "hi" or "hello"), or queries entirely unrelated to finance. DO NOT route any market, economy, or stock questions here, even if they are broad or in a foreign language.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    structured_llm = llm.with_structured_output(OffTopicAnswer, method="function_calling")
    
    system_msg = SystemMessage(content=OFF_TOPIC_SYSTEM_PROMPT.format(
        current_context=convert_state_to_prompt(state),
        available_next_agents=get_off_topic_next_agents_prompt()
    ))
    
    # We pass the history and the current question
    response = await structured_llm.ainvoke([system_msg])
    
    return {
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "off_topic",
            "answer": response.answer,
            "next_agent": response.next_agent
        }]
    }
