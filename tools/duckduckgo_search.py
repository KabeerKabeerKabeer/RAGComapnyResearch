from typing import List, Dict
from duckduckgo_search import DDGS
from utils.logger import search_logger


class DuckDuckGoSearch:
    """
    DuckDuckGo search fallback tool.
    """
    
    def __init__(self):
        self.ddgs = DDGS()
        
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform DuckDuckGo search.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            search_logger.info(f"[DuckDuckGo] Searching: {query}")
            results = list(self.ddgs.text(query, max_results=max_results))
            
            # Format results to match Tavily structure
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "content": result.get("body", ""),
                    "published_date": None
                })
            
            search_logger.info(f"[DuckDuckGo] Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            search_logger.error(f"[DuckDuckGo] Search failed: {str(e)}")
            return []
    
    def multi_search(self, queries: List[str], max_results: int = 3) -> List[Dict]:
        """
        Perform multiple searches and aggregate results.
        
        Args:
            queries: List of search queries
            max_results: Maximum results per query
            
        Returns:
            Deduplicated list of results
        """
        all_results = []
        seen_urls = set()
        
        for query in queries:
            results = self.search(query, max_results)
            
            for result in results:
                url = result.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(result)
        
        search_logger.info(f"[DuckDuckGo] Multi-search complete: {len(all_results)} unique results")
        return all_results
