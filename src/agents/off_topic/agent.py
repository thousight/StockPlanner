from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.state import AgentState
from src.agents.off_topic.prompts import OFF_TOPIC_SYSTEM_PROMPT
from src.utils.prompt import convert_state_to_prompt
from src.agents.off_topic.next_agents import get_off_topic_next_agents_prompt
from src.agents.off_topic.off_topic_answer import OffTopicAnswer
from src.agents.utils import get_next_interaction_id, get_current_question

def off_topic_agent(state: AgentState):
    """
    Off-Topic Agent: Handles queries that are completely unrelated to finance or the portfolio.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    structured_llm = llm.with_structured_output(OffTopicAnswer, method="function_calling")
    
    system_msg = SystemMessage(content=OFF_TOPIC_SYSTEM_PROMPT.format(
        current_context=convert_state_to_prompt(state),
        available_next_agents=get_off_topic_next_agents_prompt()
    ))
    
    # We pass the history and the current question
    response = structured_llm.invoke([system_msg])
    
    return {
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "step_id": response.step_id,
            "agent": "off_topic",
            "question": get_current_question(state, "Off-topic question"),
            "answer": response.reasoning,
            "next_agent": response.next_agent,
            "next_question": response.next_question
        }]
    }
