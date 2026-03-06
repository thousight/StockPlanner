# Requirements - Milestone 7: Evaluation & Observability

This milestone focuses on building a custom, in-house system for tracing every agent interaction, automatically evaluating the quality of responses, and creating a feedback loop for prompt optimization.

## 1. Trace & Span Infrastructure (Observability)

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-700** | **Full Trace Capture**: Implement a PostgreSQL schema to store `traces` (sessions) and `spans` (individual node/tool calls) with detailed inputs, outputs, and metadata. | P0 | [ ] |
| **REQ-701** | **Node Metrics**: Automatically log latency (ms), token usage (prompt/completion), and status (success/error) for every graph node. | P0 | [ ] |
| **REQ-702** | **Correlation IDs**: Integration with `asgi-correlation-id` to link API requests with graph traces for debugging. | P1 | [ ] |

## 2. Automated Evaluation (LLM-as-a-Judge)

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-710** | **In-house Judge Agent**: A specialized critic agent (using GPT-4o) to evaluate responses for faithfulness, relevance, and accuracy. | P0 | [ ] |
| **REQ-711** | **Evaluation Schema**: Storing evaluation scores and natural language reasoning for every trace in a `eval_results` table. | P0 | [ ] |
| **REQ-712** | **Gold Dataset Generator**: Tooling to automatically convert high-quality, human-verified user sessions into `eval_examples` for regression testing. | P1 | [ ] |

## 3. Automated Prompt Refinement

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-720** | **Failure Analysis View**: A database view to identify nodes with the highest error rates or lowest evaluation scores. | P0 | [ ] |
| **REQ-721** | **Refinement Loop**: An offline script (Meta-Agent) that analyzes low-score traces and suggests prompt improvements using a "Few-Shot" prompt optimization approach. | P1 | [ ] |
| **REQ-722** | **Version Tracking**: Store the specific prompt version and LLM configuration used for every span to enable A/B testing comparison. | P1 | [ ] |
