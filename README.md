# Guesty MCP Server

A Model Context Protocol (MCP) server that provides intelligent tools for Guesty property management platform integration.

## Overview

This MCP server offers goal-oriented tools for property managers using Guesty, focusing on workflow automation and intelligent insights rather than simple API wrappers.

## Features

### 🏨 Portfolio Monitoring Tool
- Real-time portfolio dashboard with occupancy rates and performance metrics
- Upcoming check-ins/check-outs tracking
- Urgent task alerts and operational status
- Revenue and booking trend analysis

## Installation

```bash
pip install guesty-mcp
```

## Configuration

The MCP server requires Guesty API credentials:

1. Create API credentials in your Guesty dashboard (Integrations > API & Webhooks)
2. Configure your MCP client to pass credentials in the request context:

```json
{
  "credentials": {
    "guesty_client_id": "your_client_id",
    "guesty_client_secret": "your_client_secret"
  }
}
```

## Available Tools

### `guesty_monitor_portfolio`
Monitor property portfolio performance, occupancy, and operational status.

**Parameters:**
- `property_ids` (optional): Specific properties to monitor, or all if not specified
- `include_alerts` (default: true): Include urgent issues requiring attention
- `performance_metrics` (default: true): Include occupancy rates, revenue, and booking trends

**Example Usage:**
```python
result = await guesty_monitor_portfolio(
    property_ids=["prop123", "prop456"],
    include_alerts=True,
    performance_metrics=True
)
```

**Returns:**
- Portfolio summary with key metrics
- Individual property status and upcoming reservations
- Urgent alerts and pending tasks
- Performance trends and insights

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black guesty_mcp/
isort guesty_mcp/

# Type checking
mypy guesty_mcp/
```

## Architecture

Following MCP gold standards:
- **Intent-based design**: Tools focus on business goals, not API endpoints
- **Worker-facing language**: Parameters use property management terminology
- **API abstraction**: Complex operations hidden behind simple interfaces
- **Error handling**: Graceful degradation with user-friendly messages

## Roadmap

Upcoming tools:
- Reservation Intelligence (`guesty_analyze_reservations`)
- Guest Journey Orchestration (`guesty_orchestrate_guest_journey`) 
- Operations Coordination (`guesty_coordinate_operations`)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests.
