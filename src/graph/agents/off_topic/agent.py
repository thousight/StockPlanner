from typing import Optional

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig

from src.graph.state import AgentState
from src.graph.agents.off_topic.prompts import OFF_TOPIC_SYSTEM_PROMPT
from src.graph.utils.prompt import convert_state_to_prompt
from src.graph.agents.off_topic.next_agents import get_off_topic_next_agents_prompt
from src.graph.agents.off_topic.off_topic_answer import OffTopicAnswer
from src.graph.utils.agents import create_interaction, get_llm, with_logging

@with_logging
async def off_topic_agent(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Off-Topic Agent: ONLY handles casual conversation, greetings (like "hi" or "hello"), or queries entirely unrelated to finance.
    """
    # Off-topic uses higher temperature for natural greetings
    llm = get_llm(temperature=0.7)
    structured_llm = llm.with_structured_output(OffTopicAnswer, method="function_calling")
    
    system_msg = SystemMessage(content=OFF_TOPIC_SYSTEM_PROMPT.format(
        current_context=convert_state_to_prompt(state),
        available_next_agents=get_off_topic_next_agents_prompt()
    ))
    
    response = await structured_llm.ainvoke([system_msg])
    
    return {
        "agent_interactions": [
            create_interaction(
                state, 
                agent="off_topic", 
                answer=response.answer, 
                next_agent=response.next_agent
            )
        ]
    }
