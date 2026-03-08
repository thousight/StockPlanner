import re
import logging
from typing import Optional

from langchain_core.runnables import RunnableConfig

from src.graph.state import AgentState
from src.graph.agents.research.prompts import CODE_GEN_PROMPT
from src.graph.tools.code_executor import execute_python_code
from src.graph.utils.agents import get_llm, get_session_info, create_interaction, with_logging

logger = logging.getLogger(__name__)

@with_logging
async def code_generator_agent(state: AgentState, config: Optional[RunnableConfig] = None):
    """
    Quantitative Research Specialist: Writes and executes Python code for data analysis.
    Use this agent for ANY mathematical calculation (e.g., square roots, averages, complex formulas), 
    statistical analysis, simulations, data manipulation, or calculating financial ratios.
    Implements a hybrid self-correction loop (Self-Debug + Reflexion).
    """
    llm = get_llm(temperature=0)
    info = get_session_info(state)
    
    # 1. Prepare Context
    user_ctx = state.get("user_context", {})
    data_context = {
        "portfolio": user_ctx.get("portfolio", []),
        "market_context": state.get("market_context", "")
    }
    
    retries = 0
    max_retries = 3
    error_context = ""
    last_code = ""
    
    while retries <= max_retries:
        prompt_input = {
            "task_description": state.get("user_input", "Perform quantitative analysis."),
            "data_context": str(data_context),
            "error_context": f"\n### Previous Attempt Error:\n{error_context}\n\n### Previous Code:\n```python\n{last_code}\n```\nAnalyze the error, reflect on the fix, and provide the corrected code." if error_context else ""
        }
        
        prompt = CODE_GEN_PROMPT.format(**prompt_input)
        response = await llm.ainvoke(prompt)
        content = response.content
        
        # Extract Audit and Code
        code_blocks = re.findall(r"```python\n(.*?)```", content, re.DOTALL)
        if not code_blocks:
            error_context = "No Python code block found. Ensure code is wrapped in ```python ... ```."
            retries += 1
            continue
            
        code = code_blocks[-1].strip()
        last_code = code
        
        audit_match = re.search(r"\*\*Audit\*\*:(.*?)(?:\n|```)", content, re.IGNORECASE | re.DOTALL)
        audit_text = audit_match.group(1).strip() if audit_match else "Self-audit complete."
        
        # 4. Execute Code
        execution_result = await execute_python_code(code, data=data_context, thread_id=info["thread_id"])
        
        if "Execution Failed" in execution_result:
            error_context = execution_result
            retries += 1
            logger.warning(f"CodeGenerator retry {retries}/{max_retries} due to error: {execution_result[:100]}...")
        else:
            # Success
            return {
                "agent_interactions": [
                    create_interaction(
                        state, 
                        agent="code_generator", 
                        answer=f"Quantitative analysis complete.\n\n**Audit**: {audit_text}\n\n**Execution Result**:\n{execution_result}", 
                        next_agent="analyst"
                    )
                ]
            }
            
    # 5. Final Failure
    return {
        "agent_interactions": [
            create_interaction(
                state, 
                agent="code_generator", 
                answer=f"Quantitative analysis failed after {max_retries} attempts.\n\nFinal Error Details:\n{error_context}", 
                next_agent="analyst"
            )
        ]
    }
