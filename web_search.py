"""
Web Search Tool

Search the web and return results with sources.
"""

import asyncio
import logging
from typing import Dict, Any, List
import httpx

from maira.tools.base import Tool, RiskLevel, ToolContext

logger = logging.getLogger(__name__)

class WebSearchTool(Tool):
    """Tool for web search using Brave Search API or fallback."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for current information. Returns titles, URLs, and snippets."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results (1-20)",
                    "minimum": 1,
                    "maximum": 20,
                    "default": 10
                }
            },
            "required": ["query"]
        }
    
    @property
    def risk_level(self) -> RiskLevel:
        return RiskLevel.LOW
    
    @property
    def required_capability(self) -> str:
        return "web_search"
    
    async def run(self, args: Dict[str, Any], ctx: ToolContext) -> Dict[str, Any]:
        """Execute web search."""
        query = args["query"]
        count = args.get("count", 10)
        
        logger.info(f"Web search: '{query}' (count: {count})")
        
        try:
            if self.api_key:
                return await self._search_brave(query, count)
            else:
                return await self._search_fallback(query, count)
                
        except Exception as e:
            logger.exception(f"Web search error: {e}")
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "sources_found": 0
            }
    
    async def _search_brave(self, query: str, count: int) -> Dict[str, Any]:
        """Search using Brave Search API."""
        params = {
            "q": query,
            "count": count,
            "search_lang": "en",
            "country": "US"
        }
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                self.base_url,
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Search API error: {response.status_code}")
            
            data = response.json()
            
            results = []
            
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "published": item.get("age", "")
                })
            
            return {
                "query": query,
                "results": results,
                "sources_found": len(results),
                "search_engine": "Brave"
            }
    
    async def _search_fallback(self, query: str, count: int) -> Dict[str, Any]:
        """Fallback search (mock results for demo)."""
        logger.warning("Using fallback search - no API key provided")
        
        # Simulate search delay
        await asyncio.sleep(1.0)
        
        # Mock results based on query
        mock_results = [
            {
                "title": f"Search result for '{query}' - Example Site",
                "url": "https://example.com/result1",
                "snippet": f"This is a mock search result for the query '{query}'. In a real implementation, this would return actual web search results.",
                "published": "2026-10-05"
            },
            {
                "title": f"More information about '{query}'",
                "url": "https://example.org/info",
                "snippet": f"Additional information and details about {query} can be found here.",
                "published": "2026-10-04"
            }
        ]
        
        results = mock_results[:count]
        
        return {
            "query": query,
            "results": results,
            "sources_found": len(results),
            "search_engine": "Fallback (Demo)"
        }