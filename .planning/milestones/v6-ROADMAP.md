# Roadmap - Milestone 6: User Long-term Memory

This roadmap focuses on building a persistent user memory using `pgvector` to enable highly personalized financial coaching.

## Phase 25: pgvector & HNSW Schema
**Goal:** Implementation of the physical storage layer for vectors.
- [ ] Database migration to add `pgvector` extension and user-memory table.
- [ ] Implementation of HNSW indexing for multi-tenant vector searches.
- [ ] Integration with an embedding model (OpenAI `text-embedding-3-small`).

## Phase 26: Memory Extraction Agent
**Goal:** Implementation of the background agent for automated profiling.
- [ ] Background node in LangGraph to identify "Profile Facts" from conversations.
- [ ] Structured extraction of risk tolerance, income, age, and goals.
- [ ] Semantic deduplication (upsert logic for existing facts).

## Phase 27: On-Demand Memory Retrieval
**Goal:** Implement the "Context Injector" for research and analysis.
- [ ] Retrieval tool for agents to query long-term memory.
- [ ] Logic for merging retrieved memory with the current agent context.
- [ ] Implementation of an "Importance Score" to filter irrelevant historical facts.

## Phase 28: User Management API
**Goal:** Finalize user controls and auditing.
- [ ] API endpoints for viewing and deleting granular memory records.
- [ ] Implementation of memory-to-thread tracing for auditing.
- [ ] Final stress tests and performance tuning of the HNSW index.
