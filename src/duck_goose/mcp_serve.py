"""
An example mcp server with database tools.

run with: uv run python src/duck_goose/mcp_serve.py
"""

from pathlib import Path
import duckdb

from mcp.server.fastmcp import FastMCP   # part of the official Python SDK

mcp = FastMCP("database_tools", version="0.1.0")

@ mcp.tool()
async def initialise_database(db_path: str = "test.db") -> str:
    """Create the SQLite-compatible DuckDB file and an `output` table."""
    Path(db_path).touch(exist_ok=True)
    with duckdb.connect(database=db_path, read_only=False) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS output (message VARCHAR);")
    return db_path

@ mcp.tool()
async def add_row_to_database(db_path: str, message: str) -> str:
    """Insert a row of text into the `output` table in *db_path*."""
    with duckdb.connect(database=db_path, read_only=False) as conn:
        conn.execute("INSERT INTO output VALUES (?);", (message,))
    return db_path

@ mcp.tool()
async def show_database_output(db_path: str) -> str:
    """Return all rows in `output` table as a newline-separated string."""
    with duckdb.connect(database=db_path, read_only=False) as conn:
        rows = conn.execute("SELECT message FROM output;").fetchall()
    return "\n".join(r[0] for r in rows)

if __name__ == "__main__":
    # run with the new Streamable-HTTP transport
    mcp.run(transport="streamable-http")