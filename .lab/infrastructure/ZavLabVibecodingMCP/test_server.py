#!/usr/bin/env python3
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TestServer")

@mcp.tool()
def hello(name: str):
    """Say hello"""
    return f"Hello {name}!"

if __name__ == "__main__":
    mcp.run()
