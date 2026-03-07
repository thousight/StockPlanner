import re
import logging
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from src.graph.state import AgentState, AgentInteraction
from src.graph.agents.research.prompts import CODE_GEN_PROMPT
from src.graph.tools.code_executor import execute_python_code
from src.graph.utils.agents import get_next_interaction_id, with_logging
from src.graph.utils.prompt import convert_state_to_prompt

logger = logging.getLogger(__name__)

@with_logging
async def code_generator_agent(state: AgentState):
    """
    Quantitative Research Specialist: Writes and executes Python code for data analysis.
    Implements a hybrid self-correction loop (Self-Debug + Reflexion).
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # 1. Prepare Context
    # Extract data context for the agent (Portfolio, etc.)
    data_context = {
        "portfolio": state["user_context"].get("portfolio", []),
        "market_context": state.get("market_context", "")
    }
    
    retries = 0
    max_retries = 3
    error_context = ""
    last_code = ""
    
    while retries <= max_retries:
        # Prepare Prompt
        # We pass the full context if it's a retry
        prompt_input = {
            "task_description": state["user_input"],
            "data_context": str(data_context),
            "error_context": f"\n### Previous Attempt Error:\n{error_context}\n\n### Previous Code:\n```python\n{last_code}\n```\nAnalyze the error, reflect on the fix, and provide the corrected code." if error_context else ""
        }
        
        prompt = CODE_GEN_PROMPT.format(**prompt_input)
        
        # 2. Invoke LLM
        response = await llm.ainvoke(prompt)
        content = response.content
        
        # 3. Extract Audit and Code
        # Audit: brief summary
        # Code: wrapped in ```python ... ```
        
        # Use regex to find the last code block in case there are multiple explanations
        code_blocks = re.findall(r"```python\n(.*?)```", content, re.DOTALL)
        if not code_blocks:
            error_context = "No Python code block found. Ensure code is wrapped in ```python ... ```."
            retries += 1
            continue
            
        code = code_blocks[-1].strip()
        last_code = code
        
        # Extract Audit (Case-insensitive)
        audit_match = re.search(r"\*\*Audit\*\*:(.*?)(?:\n|```)", content, re.IGNORECASE | re.DOTALL)
        audit_text = audit_match.group(1).strip() if audit_match else "Self-audit complete."
        
        # 4. Execute Code
        execution_result = await execute_python_code(code, data=data_context)
        
        if "Execution Failed" in execution_result:
            # Self-correction trigger
            error_context = execution_result
            retries += 1
            logger.warning(f"CodeGenerator retry {retries}/{max_retries} due to error: {execution_result[:100]}...")
        else:
            # Success
            return {
                "agent_interactions": [{
                    "id": get_next_interaction_id(state),
                    "agent": "code_generator",
                    "answer": f"Quantitative analysis complete.\n\n**Audit**: {audit_text}\n\n**Execution Result**:\n{execution_result}",
                    "next_agent": "analyst"
                }]
            }
            
    # 5. Final Failure
    return {
        "agent_interactions": [{
            "id": get_next_interaction_id(state),
            "agent": "code_generator",
            "answer": f"Quantitative analysis failed after {max_retries} attempts.\n\nFinal Error Details:\n{error_context}",
            "next_agent": "analyst"
        }]
    }
