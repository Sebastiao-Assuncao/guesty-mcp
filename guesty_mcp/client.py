"""Guesty API client with OAuth 2.0 authentication."""

import httpx
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from .settings import settings
import logging

logger = logging.getLogger(__name__)


class GuestyAPIClient:
    """Guesty API client with OAuth 2.0 authentication and retry logic."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://open-api.guesty.com/v1"
        self.token_url = "https://open-api.guesty.com/oauth2/token"
        self.access_token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=settings.request_timeout_s)

    async def get_access_token(self) -> str:
        """Get OAuth 2.0 access token."""
        if self.access_token:
            return self.access_token
            
        logger.info("→ Getting Guesty access token")
        
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "open-api"
        }
        
        response = await self.client.post(
            self.token_url,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            logger.error(f"✗ Token request failed: {response.status_code} {response.text}")
            raise Exception(f"Failed to get access token: {response.status_code}")
        
        token_response = response.json()
        self.access_token = token_response["access_token"]
        logger.info("✓ Access token obtained")
        return self.access_token

    @retry(stop=stop_after_attempt(settings.max_retries), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Guesty API."""
        token = await self.get_access_token()
        
        headers = kwargs.pop('headers', {})
        headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        
        url = f"{self.base_url}{endpoint}"
        logger.info(f"→ {method.upper()} {endpoint}")
        
        response = await self.client.request(method, url, headers=headers, **kwargs)
        
        if response.status_code >= 400:
            logger.error(f"✗ API request failed: {response.status_code} {response.text}")
            raise Exception(f"API request failed: {response.status_code} {response.text}")
        
        logger.info(f"✓ Request successful: {response.status_code}")
        return response.json()

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request to Guesty API."""
        return await self.make_request("GET", endpoint, params=params)

    async def aclose(self):
        """Close the HTTP client."""
        await self.client.aclose()