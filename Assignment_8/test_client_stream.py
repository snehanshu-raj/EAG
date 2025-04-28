# import aiohttp
# import asyncio

# async def listen_to_sse(url: str):
#     """Simple function to connect to an SSE server and print incoming events."""
#     headers = {
#         "Accept": "text/event-stream"
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, headers=headers) as response:
#             print(f"Connected to {url} with status {response.status}")
#             async for line in response.content:
#                 decoded_line = line.decode('utf-8').strip()
#                 if decoded_line:  # Ignore empty lines
#                     print(f"Received: {decoded_line}")

# if __name__ == "__main__":
#     server_url = "http://localhost:8080/stream"
#     asyncio.run(listen_to_sse(server_url))

import asyncio
import logging
from mcp.client.sse import sse_client
from mcp import ClientSession

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

headers = {
    "Accept": "text/event-stream"
}

async def connect_to_sse_server(server_url: str):
    """Connect to the SSE MCP server, listen and print raw messages."""
    logger.debug(f"Connecting to SSE MCP server at {server_url}")

    # Establish SSE connection
    async with sse_client(url=server_url, headers=headers) as streams:
        read_stream, write_stream = streams
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            response = await session.list_tools()
            tools = response.tools
            logger.info(f"Connected to SSE MCP Server at {server_url}. Available tools: {[tool.name for tool in tools]}")

            result = await session.call_tool("test", arguments={})

# Run the client
if __name__ == "__main__":
    server_url = "http://localhost:8080/sse"  # Replace with your server's URL if different
    asyncio.run(connect_to_sse_server(server_url))
