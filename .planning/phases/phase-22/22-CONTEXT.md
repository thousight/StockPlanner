# Phase 22 Context: Code Generation & Verification

## Phase Goal
Create a specialized agent (`CodeGeneratorAgent`) responsible for writing, auditing, and self-correcting Python analysis scripts for the secure sandbox.

## Key Decisions

### 1. Agent Persona & Formatting
- **Persona:** Senior Financial Quantitative Developer.
- **Output Format:** **Markdown Code Blocks**. The agent provides a brief explanation followed by the code block.
- **Enforced Structure:** All generated code must follow a **Standard Function** pattern:
  ```python
  def run(input_data):
      # Analysis logic here
      return result
  
  print(run(input_data))
  ```
- **Reference Data:** The agent is aware that injected data is available via the `input_data` variable.

### 2. Verification & Self-Correction
- **Strategy:** **Self-Reflection**. The agent performs an internal "Audit" step (Chain of Thought) to check for logic errors and security violations before outputting the final code.
- **Correction Loop:** **Internal Retry Loop**. If code fails either the `ASTValidator` or the `PythonSandbox` execution, the same node will attempt to fix the code.
- **Retry Limit:** Maximum of **3 attempts** for self-correction.
- **Correction Context:** The agent receives the **Full Context** (previous code attempt + the sanitized error message) to inform the fix.

### 3. Toolbox & Constraints
- **Whitelisted Libraries:** Prompt the agent to use `pandas`, `numpy`, `math`, `datetime`, `scipy`, and `statistics`.
- **Security Guardrails:** The system relies on the `ASTValidator` for silent blocking of forbidden imports/functions. No explicit "No Network" warning is required in the system prompt to keep focus on the task.

### 4. Metadata & Logging
- **Minimal Metadata:** Focus on the code and its explanation.
- **Traceability:** Every code attempt and its resulting error (if any) must be logged within the LangGraph state for debugging.

## Code Context & Integration
- **New Agent:** `src/graph/agents/research/code_gen.py`.
- **New Prompt:** `CODE_GEN_PROMPT` in `src/graph/agents/research/prompts.py`.
- **Graph Integration:** The `CodeGenerator` node will be added to the research squad, capable of being triggered by the supervisor for complex math/data tasks.

## Next Steps
1.  **Phase 22 Research:** Draft the quantitative prompt instructions and few-shot examples for the generator.
2.  **Phase 22 Plan:** Define the implementation of the internal retry loop and state management for code attempts.
