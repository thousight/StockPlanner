---
status: investigating
trigger: "Investigate why human messages are not showing up in thread history."
created: 2024-05-24T12:00:00Z
updated: 2024-05-24T12:00:00Z
---

## Current Focus

hypothesis: graph.astream or the graph nodes might be losing the initial HumanMessage in the state, or add_messages annotation in AgentState is not behaving as expected.
test: Create a reproduction script that calls the graph and checks if the human message is present in the final state.
expecting: HumanMessage to be present in final state if things were working.
next_action: Examine AgentState definition and graph setup.

## Symptoms

expected: Human messages should be saved to thread history in the chat_messages table.
actual: Human messages are missing from thread history.
errors: None reported, just missing data.
reproduction: Call the API and check if chat_messages table contains the human message. (User says a previous reproduction script bypassed the graph, need one that uses it).
started: Recently reported.

## Eliminated

## Evidence

## Resolution

root_cause: 
fix: 
verification: 
files_changed: []
