"""
An example module for a Python research software project.
"""

from typing import Any, Dict

import duckdb
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
import pathlib

# Clean up any existing database file
if pathlib.Path("temp.db").exists():
    pathlib.Path("temp.db").unlink()


def intialize_database(database_path: str = "test.db") -> str:
    """
    Initialize a database.
    """
    with duckdb.connect(database=database_path, read_only=False) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS output (message VARCHAR);")
    return database_path


def add_row_to_database(database_path: str, message: str) -> str:
    """
    Add a row to the database.
    """
    with duckdb.connect(database=database_path, read_only=False) as conn:
        conn.execute(f"INSERT INTO output (message) VALUES ('{message}');")
    return database_path


def show_database_output(database_path: str) -> str:
    """
    Show the output of the database.
    """
    with duckdb.connect(database=database_path, read_only=False) as conn:
        result = conn.execute("SELECT * FROM output;").fetchall()
        result_str = "\n".join([str(row) for row in result])
    return result_str


llama32_chat = ChatOllama(model="llama3.2", temperature=0)

llm_with_tools = llama32_chat.bind_tools(
    (tools := [intialize_database, add_row_to_database, show_database_output])
)

# System message
sys_msg = SystemMessage(
    content=(
        "You are a helpful assistant tasked with using tools"
        " to help someone accomplish database-related tasks."
    )
)


# Node
def assistant(state: MessagesState) -> Dict[str, Any]:
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


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
messages = react_graph.invoke({"messages": messages}, {"recursion_limit": 100})

for m in messages["messages"]:
    m.pretty_print()
