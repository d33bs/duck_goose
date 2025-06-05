"""
An example mcp server with database tools.

run with: uv run python src/duck_goose/mcp_serve.py
"""

import duckdb
from mcp.server.fastmcp import FastMCP  # part of the official Python SDK

mcp = FastMCP("database_tools", version="0.1.0")


@mcp.tool()
async def initialize_database(db_path: str = "test.db") -> str:
    """
    Initialize a database and create a table called output
    with one column called message, used in other tools.
    """
    with duckdb.connect(database=db_path, read_only=False) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS output (message VARCHAR);")
    return db_path


@mcp.tool()
async def add_row_to_database(db_path: str, message: str) -> str:
    """
    Add a row to the database.
    """
    with duckdb.connect(database=db_path, read_only=False) as conn:
        conn.execute("INSERT INTO output VALUES (?);", (message,))
    return db_path


@mcp.tool()
async def show_database_output(db_path: str) -> str:
    """
    Show the output of the database.
    """
    with duckdb.connect(database=db_path, read_only=False) as conn:
        rows = conn.execute("SELECT message FROM output;").fetchall()
    return "\n".join(r[0] for r in rows)


if __name__ == "__main__":
    # run with the new Streamable-HTTP transport
    mcp.run(transport="streamable-http")
