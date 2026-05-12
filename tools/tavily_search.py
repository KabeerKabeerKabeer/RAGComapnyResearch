from typing import List, Dict, Optional
from tavily import TavilyClient
from config import TAVILY_API_KEY
from utils.logger import search_logger


class TavilySearch:
    """
    Tavily search tool wrapper with error handling.
    """
    
    def __init__(self):
        self.client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
        
    def search(self, query: str, max_results: int = 5) -> Optional[List[Dict]]:
        """
        Perform Tavily search with error handling.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results or None on failure
        """
        if not self.client:
            search_logger.error("[Tavily] API key not configured")
            return None
            
        try:
            search_logger.info(f"[Tavily] Searching: {query}")
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            
            results = response.get("results", [])
            search_logger.info(f"[Tavily] Found {len(results)} results")
            
            return results
            
        except Exception as e:
            search_logger.error(f"[Tavily] Search failed: {str(e)}")
            return None
    
    def multi_search(self, queries: List[str], max_results: int = 3) -> List[Dict]:
        """
        Perform multiple searches and aggregate results.
        
        Args:
            queries: List of search query strings
            max_results: Maximum results per query
            
        Returns:
            Deduplicated list of all search results
        """
        all_results = []
        seen_urls = set()
        
        for query in queries:
            results = self.search(query, max_results)
            
            if results:
                for result in results:
                    url = result.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(result)
        
        search_logger.info(f"[Tavily] Multi-search complete: {len(all_results)} unique results")
        return all_results
