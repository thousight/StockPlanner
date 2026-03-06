# Requirements - Milestone 6: User Long-term Memory

This milestone focuses on providing the agent team with a persistent "memory" of each user to enable personalized financial advice and historical context across different conversation threads.

## 1. Storage & Schema

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-600** | **pgvector Integration**: Extend the PostgreSQL schema to support `vector` types with HNSW indexing for user-specific memories. | P0 | [ ] |
| **REQ-601** | **Multi-tenant Isolation**: Strict user-level partitioning of the vector store (no cross-user retrieval). | P0 | [ ] |
| **REQ-602** | **Memory Schema**: Define structured data models for user profile facts (risk tolerance, age, income range). | P1 | [ ] |

## 2. Memory Life Cycle

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-610** | **Extraction Agent**: A specialized background agent that identifies and extracts new facts from user-agent interactions. | P0 | [ ] |
| **REQ-611** | **Semantic Search (On-Demand)**: Implement a retrieval tool that researchers or analysts can call when they need specific user context. | P0 | [ ] |
| **REQ-612** | **Memory Relevance (Ranking)**: Score and rank retrieved memories based on semantic similarity to the current query. | P1 | [ ] |

## 3. User Controls & Compliance

| ID | Requirement | Priority | Status |
|---|---|---|---|
| **REQ-620** | **Granular Deletion**: Provide an endpoint for users to view and delete specific memory records. | P0 | [ ] |
| **REQ-621** | **Fact Auditing**: Ability to trace a specific memory back to the source interaction or conversation thread. | P1 | [ ] |
| **REQ-622** | **Memory Summarization**: Periodically synthesize granular memories into higher-level user profiles to prevent context bloat. | P1 | [ ] |
