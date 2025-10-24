"""Tests for portfolio monitoring tool."""

import pytest
from unittest.mock import AsyncMock, patch
from mcp.server.fastmcp import Context

from guesty_mcp.tools.portfolio_monitor import guesty_monitor_portfolio_impl


@pytest.fixture
def mock_context():
    """Mock MCP context with test credentials."""
    context = AsyncMock(spec=Context)
    context.request_context.meta = {
        'credentials': {
            'guesty_client_id': 'test_client_id',
            'guesty_client_secret': 'test_client_secret'
        }
    }
    return context


@pytest.mark.asyncio
async def test_portfolio_monitor_basic(mock_context):
    """Test basic portfolio monitoring functionality."""
    with patch('guesty_mcp.tools.portfolio_monitor.GuestyAPIClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock API responses
        mock_client.get.side_effect = [
            {"results": [{"_id": "prop1", "title": "Test Property"}]},  # listings
            {"results": []},  # reservations
            {"results": []}   # tasks
        ]
        
        result = await guesty_monitor_portfolio_impl(
            mock_context,
            property_ids=None,
            include_alerts=True,
            performance_metrics=True
        )
        
        assert "portfolio_summary" in result
        assert "property_status" in result
        assert "alerts" in result
        assert result["total_properties_analyzed"] == 1
        
        # Verify client was closed
        mock_client.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_portfolio_monitor_with_specific_properties(mock_context):
    """Test portfolio monitoring with specific property IDs."""
    with patch('guesty_mcp.tools.portfolio_monitor.GuestyAPIClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock individual property responses
        mock_client.get.side_effect = [
            {"_id": "prop1", "title": "Property 1"},
            {"_id": "prop2", "title": "Property 2"},
            {"results": []},  # reservations
            {"results": []}   # tasks
        ]
        
        result = await guesty_monitor_portfolio_impl(
            mock_context,
            property_ids=["prop1", "prop2"],
            include_alerts=True,
            performance_metrics=True
        )
        
        assert result["total_properties_analyzed"] == 2
        assert len(result["property_status"]) == 2


@pytest.mark.asyncio
async def test_portfolio_monitor_authentication_error(mock_context):
    """Test error handling for authentication failures."""
    # Remove credentials from context
    mock_context.request_context.meta = {}
    
    with pytest.raises(ValueError, match="Missing Guesty API credentials"):
        await guesty_monitor_portfolio_impl(
            mock_context,
            property_ids=None,
            include_alerts=True,
            performance_metrics=True
        )
