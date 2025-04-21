from mcp.server.fastmcp import FastMCP
import mcp
import json
import sys
from search_handler import async_search
from asyncio import to_thread

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs.log",
    format='%(asctime)s - %(process)d - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

mcp = FastMCP("WebSearch")

@mcp.tool()
async def search_query(text: str = None, image_bytes: bytes = None, type: str = None) -> str:
    """Searches for the query text or query image"""
    logger.info(f"log from search.tool(): text: {text}, image_byes: {image_bytes}, type: {type}")
    if text != 'None':
        logger.info(f"calling: async text search")
        results = await async_search(text=text, type=type)
    else:
        logger.info(f"calling: async image search")
        results = await async_search(image_bytes=image_bytes, type=type)
    logger.info(f"results from search: {results}")

    return results

if __name__ == "__main__":
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution

    # asyncio.run(main())
