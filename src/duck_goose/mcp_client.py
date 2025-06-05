"""
An example module for a Python research software project.
"""

import pathlib
from typing import Any, Dict
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main() -> None:

    # Clean up any existing database file
    if pathlib.Path("temp.db").exists():
        pathlib.Path("temp.db").unlink()

    client = MultiServerMCPClient(
        {
            "duckdb-tools": {
                "url": "http://localhost:8000/mcp/",  # FastMCP's default streamable-HTTP path
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()

    # show available tools
    print(f"Available tools: {tools}")

    llama32_chat = ChatOllama(model="llama3.2", temperature=0)

    # bind the tools to the llm
    llm_with_tools = llama32_chat.bind_tools(
        tools=tools
    )

    # System message
    sys_msg = SystemMessage(
        content=(
            "You are a helpful assistant tasked with using tools"
            " to help someone accomplish database-related tasks."
        )
    )

    # Node
    async def assistant(state: MessagesState) -> Dict[str, Any]:
        msg = await llm_with_tools.ainvoke([sys_msg] + state["messages"])
        return {"messages": [msg]}
    
    # Graph
    builder = StateGraph(MessagesState)

    # Define nodes: these do the work
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # if the assistant decides to use a tool, use it.
        # otherwise, end the loop.
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    react_graph = builder.compile()

    # Message list
    messages = [
        HumanMessage(
            content=(
                """
    1. Initialize a database at the path temp.db using the
    tool `initialize_database`.
    2. Add rows to that database with the messages
    'duck', 'duck', and 'goose' using the tool `add_row_to_database`.
    3. Finally, show the output of the database using the
    tool `show_database_output`.

    The output of the database will be:
    ```
    temp.db

    +--------+
    | message |
    +--------+
    | duck    |
    | duck    |
    | goose   |
    +--------+
    """
            )
        ),
    ]

    # Invoke the model with a list of messages
    messages = await react_graph.ainvoke({"messages": messages}, {"recursion_limit": 100})

    for m in messages["messages"]:
        m.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())