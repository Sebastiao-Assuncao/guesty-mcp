"""Authentication utilities for Guesty API integration."""

from mcp.server.fastmcp import Context
from typing import Dict, Optional
import os


def extract_guesty_credentials_from_headers(ctx: Context) -> Dict[str, str]:
    """Extract Guesty API credentials from request headers."""
    request_context = ctx.request_context
    meta = request_context.meta if hasattr(request_context, 'meta') else {}
    credentials = meta.get('credentials', {})
    
    client_id = credentials.get('guesty_client_id')
    client_secret = credentials.get('guesty_client_secret')
    
    if not client_id or not client_secret:
        raise ValueError("Missing Guesty API credentials (client_id and client_secret required)")
    
    return {
        'client_id': client_id,
        'client_secret': client_secret
    }