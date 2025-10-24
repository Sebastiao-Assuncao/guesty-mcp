"""Main MCP server for Guesty integration."""

import logging
from mcp.server import FastMCP

from .registry import register_tools
from .settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("Guesty MCP Server")

# Register all tools
register_tools(mcp)


def main():
    """Main entry point for the server."""
    logger.info("🏨 Starting Guesty MCP Server")
    mcp.run()


if __name__ == "__main__":
    main()