"""Tool registry for Guesty MCP server."""

from mcp.server import FastMCP
from mcp.server.fastmcp import Context
from typing import List, Optional, Dict, Any
from pydantic import Field
from typing_extensions import Annotated

from .tools.portfolio_monitor import guesty_monitor_portfolio_impl


def register_tools(mcp: FastMCP):
    """Register all Guesty MCP tools."""
    
    @mcp.tool()
    async def guesty_monitor_portfolio(
        ctx: Context,
        property_ids: Annotated[Optional[List[str]], Field(description="Specific properties to monitor, or all if not specified")] = None,
        include_alerts: Annotated[bool, Field(description="Include urgent issues requiring attention")] = True,
        performance_metrics: Annotated[bool, Field(description="Include occupancy rates, revenue, and booking trends")] = True
    ) -> Dict[str, Any]:
        """Monitor property portfolio performance, occupancy, and operational status.
        
        Provides a real-time dashboard view of all properties with key metrics,
        upcoming reservations, pending tasks, and urgent alerts requiring attention.
        Perfect for daily property management overview and identifying issues that need attention.
        """
        return await guesty_monitor_portfolio_impl(ctx, property_ids, include_alerts, performance_metrics)