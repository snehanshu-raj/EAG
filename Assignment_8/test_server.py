from typing import AsyncGenerator
import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server.sse import SseServerTransport
from mcp.server import Server
import uvicorn
import asyncio
from starlette.responses import StreamingResponse
from pydantic import BaseModel

class CustomMessage(BaseModel):
    message: str

import logging
logging.basicConfig(level=logging.DEBUG)

mcp = FastMCP("test")

# Define the resource that streams data
@mcp.tool()
async def test() -> AsyncGenerator[str, None]:
    """Streams data to the client."""
    for i in range(5):
        logging.debug(f"Sending chunk {i}")  # Log chunk number
        yield f"Data chunk {i}\n"
        await asyncio.sleep(1)  # Simulate delay between chunks

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

# Define the Starlette application for handling SSE and POST requests
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application to handle the MCP server with SSE."""
    
    sse = SseServerTransport("/messages/")

    async def sse_test(request: Request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):            
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

            async def event_publisher():
                async for chunk in test():  # Consume the async generator
                    # yield f"data: {chunk}\n\n"  # Format the SSE event data
                    yield CustomMessage(message="Custom Data Test").model_dump_json(by_alias=True, exclude_none=True)
                    await asyncio.sleep(1)  # Optional: simulate delay between chunks

            return StreamingResponse(event_publisher(), media_type="text/event-stream")  # Return SSE response

    # Define the route to handle SSE connections for streaming data from MCP tools
    async def handle_sse(request: Request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):            
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

    return Starlette(
        debug=debug,
        routes=[
            Route("/stream", endpoint=sse_test),  # Route to handle streaming test tool data
            Route("/sse", endpoint=handle_sse),  # Route to handle incoming SSE connections
            Mount("/messages/", app=sse.handle_post_message),  # Mount to handle POST requests
        ],
    )

# Start the MCP server and expose it to Starlette
if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # Access the internal MCP server instance

    import argparse

    # Parse command-line arguments for host and port
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server and create the app
    starlette_app = create_starlette_app(mcp_server, debug=True)

    # Run the application with Uvicorn server
    uvicorn.run(starlette_app, host=args.host, port=args.port)