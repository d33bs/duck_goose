# duck_goose

An experiment with model context protocol (MCP).

## Requirements

1. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/) (environment management for Python)
1. Install `ollama` (e.g. `brew install ollama`) (model management and server for llm model)
1. See below for instructions.

## Demonstrations goal

The goal of all demonstrations here involves asking an LLM to create a database and single table with records "duck", "duck", "goose".
We ask the LLM to perform this work using MCP or local [Tools](https://modelcontextprotocol.io/docs/concepts/tools).
This allows the LLM to agentically achieve this work without specifying explicit programmatic instructions to accomplish this work.

## Running the demonstrations

We use `poethepoet` to create declarative tasks which run the demonstrations found here.
You may list these by using `uv run poe`.
Run these demo by using `uv run poe <task name>`.

The following tasks exist:

- `uv run poe local_tool_demo`: Run a local tool-based LLM example.
- `uv run poe mcp_demo`: Run an mcp-based tool LLM example.
