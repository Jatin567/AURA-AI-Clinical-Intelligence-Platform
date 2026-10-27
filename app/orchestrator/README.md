# AI Orchestrator Intelligence Pipeline

This module connects the AURA Knowledge Platform, Hybrid Retrieval Engine, Clinical Intelligence Layer, Memory System, and Tool Framework into a deterministic execution pipeline.

## Execution Graph

The Orchestrator defines a deterministic `ExecutionGraph` to route every user query:
`Intent -> Retrieval -> Prompt -> LLM -> Safety -> Composer`

## Gateway

The `ConversationGateway` is the only external HTTP entry point. It handles authentication, SSE streams, and instantiates an `AISession` object which flows deterministically through the graph.

## Prompt Layers

`prompt_layers.py` contains isolated Builders (`SystemPromptBuilder`, `PatientPromptBuilder`, etc.) which the `FinalPromptAssembler` stitches securely to avoid string duplication or memory injection leaks.
