"""
Scout Agent - URL Discovery Agent built with Google ADK
Discovers cosmetic product URLs from e-commerce websites
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time
from loguru import logger

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from config.models import SiteConfig, ProductData, AgentTask
from config.sites import SITE_CONFIGS


class URLDiscoveryTool(BaseTool):
    """Tool for discovering product URLs from e-commerce sites"""
    
    def __init__(self):
        super().__init__(
            name="url_discovery",
            description="Discover product URLs from e-commerce category pages",
            is_long_running=True
        )
        self.site_configs = {config.name: config for config in SITE_CONFIGS}
        self.session = None
        
    async def __call__(self, site_name: str, max_products: int = 100) -> Dict[str, Any]:
        """Discover product URLs from the specified site"""
        
        if site_name not in self.site_configs:
            return {"error": f"Site {site_name} not configured"}
        
        config = self.site_configs[site_name]
        discovered_urls = []
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            for category_path in config.category_paths:
                urls = await self._crawl_category(category_path, config, max_products // len(config.category_paths))
                discovered_urls.extend(urls)
                
                if len(discovered_urls) >= max_products:
                    break
            
            logger.info(f"Scout discovered {len(discovered_urls)} URLs from {site_name}")
            
            return {
                "site_name": site_name,
                "discovered_urls": discovered_urls[:max_products],
                "total_count": len(discovered_urls[:max_products])
            }
            
        except Exception as e:
            logger.error(f"Error discovering URLs from {site_name}: {e}")
            return {"error": str(e)}
    
    async def _crawl_category(self, category_path: str, config: SiteConfig, max_urls: int) -> List[str]:
        """Crawl a category page to find product URLs"""
        product_urls = []
        page = 1
        
        while page <= config.max_pages and len(product_urls) < max_urls:
            try:
                url = urljoin(str(config.base_url), category_path)
                if page > 1:
                    url = f"{url}?page={page}"
                
                async with self.session.get(
                    url, 
                    headers=config.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch {url}: {response.status}")
                        break
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    product_links = self._extract_product_links(soup, config)
                    if not product_links:
                        break
                    
                    product_urls.extend(product_links)
                    
                    if not self._has_next_page(soup, config):
                        break
                    
                    page += 1
                    await asyncio.sleep(config.rate_limit)
                    
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                break
        
        return product_urls[:max_urls]
    
    def _extract_product_links(self, soup: BeautifulSoup, config: SiteConfig) -> List[str]:
        """Extract product links from the page"""
        links = []
        product_selector = config.selectors.get("product_link", "a.product-link")
        
        for link in soup.select(product_selector):
            href = link.get("href")
            if href:
                full_url = urljoin(str(config.base_url), href)
                if self._is_valid_product_url(full_url):
                    links.append(full_url)
        
        return links
    
    def _has_next_page(self, soup: BeautifulSoup, config: SiteConfig) -> bool:
        """Check if there's a next page"""
        next_selector = config.selectors.get("next_page", "a.next-page")
        return bool(soup.select_one(next_selector))
    
    def _is_valid_product_url(self, url: str) -> bool:
        """Check if URL is a valid product URL"""
        parsed = urlparse(url)
        invalid_patterns = [
            "/category/", "/search/", "/brand/", "/login", "/register",
            "/cart", "/checkout", "/account", "/help", "/about"
        ]
        return not any(pattern in parsed.path.lower() for pattern in invalid_patterns)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()


class ScoutAgent(LlmAgent):
    """Scout Agent for discovering cosmetic product URLs using Google ADK"""
    
    def __init__(self):
        tools = [URLDiscoveryTool()]
        
        super().__init__(
            name="scout_agent",
            model="gemini-1.5-pro-latest",
            tools=tools,
            instruction="""
            You are a Scout Agent specialized in discovering cosmetic product URLs from e-commerce websites.
            
            Your primary responsibilities:
            1. Use the url_discovery tool to find product URLs from specified e-commerce sites
            2. Focus on cosmetic products: skincare, makeup, haircare, fragrance
            3. Ensure discovered URLs are valid product pages, not category or navigation pages
            4. Respect rate limits and scraping ethics
            5. Return structured data about discovered products
            
            When given a site name, use the url_discovery tool to find product URLs.
            Always prioritize quality over quantity - better to find fewer high-quality product URLs
            than many invalid ones.
            
            Sites you can discover from:
            - trendyol: Turkish e-commerce site
            - sephora_tr: Sephora Turkey
            - gratis: Turkish cosmetics retailer
            """
        )
    
    async def run(self, site_name: str, max_products: int = 100) -> Dict[str, Any]:
        """Main run method for Scout Agent"""
        try:
            # Directly use the URLDiscoveryTool
            discovery_tool = self.tools[0]  # URLDiscoveryTool
            result = await discovery_tool(site_name, max_products)
            
            logger.info(f"Scout Agent discovered {result.get('total_count', 0)} URLs from {site_name}")
            return result
            
        except Exception as e:
            logger.error(f"Scout Agent error: {e}")
            return {"error": str(e)}
    
    async def run_async(self, site_name: str, max_products: int = 100) -> Dict[str, Any]:
        """Async run method for compatibility"""
        return await self.run(site_name, max_products)


# Agent factory function for ADK orchestration
def create_scout_agent() -> ScoutAgent:
    """Factory function to create Scout Agent instance"""
    return ScoutAgent()