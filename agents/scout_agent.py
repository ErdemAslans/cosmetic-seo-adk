"""
Refactored Scout Agent - URL Discovery Agent
Discovers cosmetic product URLs from e-commerce websites using base classes
"""

import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import random

from google.adk.agents import Agent
from config.models import SiteConfig, ProductData, AgentTask
from config.sites import SITE_CONFIGS

from .utils import BaseAgent, error_handler, RetryMixin
from .base_tool import BaseTool, tool_error_handler
from .constants import (
    USER_AGENTS, DEFAULT_TIMEOUTS, DELAY_RANGES, COMMON_SELECTORS, 
    ERROR_MESSAGES, SUCCESS_MESSAGES, PRODUCT_URL_PATTERNS
)
from .utils import URLUtils, TextCleaner
from .config import config


class ProductURLDiscoveryTool(BaseTool):
    """Tool for discovering product URLs from e-commerce sites."""
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for ADK registration."""
        return {
            "name": "discover_product_urls",
            "description": "Discover product URLs from e-commerce category pages",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_name": {
                        "type": "string",
                        "description": "Name of the e-commerce site (trendyol, gratis, sephora_tr, rossmann)"
                    },
                    "max_products": {
                        "type": "integer", 
                        "description": "Maximum number of product URLs to discover",
                        "default": 100
                    },
                    "category": {
                        "type": "string",
                        "description": "Specific category to search (optional)",
                        "default": ""
                    }
                },
                "required": ["site_name"]
            }
        }
    
    async def validate_input(self, site_name: str = None, max_products: int = 100, **kwargs) -> Dict[str, Any]:
        """Validate input parameters."""
        errors = []
        
        if not site_name:
            errors.append("site_name is required")
        elif site_name not in config.sites:
            errors.append(f"Unsupported site: {site_name}. Supported sites: {list(config.sites.keys())}")
        
        if max_products <= 0 or max_products > 1000:
            errors.append("max_products must be between 1 and 1000")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "details": errors
        }
    
    async def execute(self, site_name: str, max_products: int = 100, category: str = "", **kwargs) -> Dict[str, Any]:
        """Execute URL discovery."""
        site_config = config.sites[site_name]
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            discovered_urls = []
            
            # Get category paths to crawl
            category_paths = site_config.category_paths if hasattr(site_config, 'category_paths') else ['/']
            if category:
                category_paths = [path for path in category_paths if category.lower() in path.lower()]
            
            for category_path in category_paths:
                urls = await self._crawl_category(
                    session, 
                    category_path, 
                    site_config, 
                    max_products // len(category_paths)
                )
                discovered_urls.extend(urls)
                
                if len(discovered_urls) >= max_products:
                    break
                
                # Rate limiting
                await asyncio.sleep(random.uniform(*DELAY_RANGES["between_pages"]))
            
            return self.format_success_result(
                data={
                    "site_name": site_name,
                    "discovered_urls": discovered_urls[:max_products],
                    "total_count": len(discovered_urls[:max_products]),
                    "categories_searched": len(category_paths)
                },
                message=SUCCESS_MESSAGES["products_found"].format(count=len(discovered_urls[:max_products]))
            )
    
    async def _crawl_category(
        self, 
        session: aiohttp.ClientSession,
        category_path: str,
        site_config: SiteConfig,
        max_urls: int
    ) -> List[str]:
        """Crawl a category page to discover product URLs."""
        product_urls = []
        page = 1
        max_pages = getattr(site_config, 'max_pages', 5)
        
        while page <= max_pages and len(product_urls) < max_urls:
            try:
                url = URLUtils.build_absolute_url(category_path, site_config.base_url)
                
                # Add pagination
                if page > 1:
                    url = self._add_pagination(url, page, site_config.name)
                
                # Make request
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                if site_config.custom_headers:
                    headers.update(site_config.custom_headers)
                
                async with session.get(
                    url, 
                    headers=headers,
                    timeout=DEFAULT_TIMEOUTS["request"]
                ) as response:
                    if response.status != 200:
                        self.logger.warning(f"HTTP {response.status} for {url}")
                        break
                    
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract product links
                    page_urls = self._extract_product_links(soup, site_config)
                    
                    if not page_urls:
                        self.logger.info(f"No more products found on page {page}")
                        break
                    
                    product_urls.extend(page_urls)
                    self.logger.info(f"Found {len(page_urls)} URLs on page {page}")
                    
                    page += 1
                    
                    # Rate limiting
                    await asyncio.sleep(random.uniform(*DELAY_RANGES["request"]))
                    
            except Exception as e:
                self.logger.error(f"Error crawling page {page} of {category_path}: {e}")
                break
        
        return product_urls
    
    def _add_pagination(self, url: str, page: int, site_name: str) -> str:
        """Add pagination parameters to URL."""
        if site_name == "trendyol":
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}pi={page}"
        elif site_name == "gratis":
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}page={page}"
        elif site_name == "sephora_tr":
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}currentPage={page}"
        else:
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}p={page}"
    
    def _extract_product_links(self, soup: BeautifulSoup, site_config: SiteConfig) -> List[str]:
        """Extract product links from page HTML."""
        product_urls = []
        
        # Try site-specific selectors first
        selectors = site_config.selectors.get("product_links", COMMON_SELECTORS["product_links"])
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                links = soup.select(selector)
                
                for link in links:
                    href = link.get('href')
                    if href:
                        # Build absolute URL
                        absolute_url = URLUtils.build_absolute_url(href, site_config.base_url)
                        
                        # Validate product URL
                        if self._is_valid_product_url(absolute_url, site_config.name):
                            product_urls.append(absolute_url)
                
                if product_urls:
                    break
                    
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
                continue
        
        return list(set(product_urls))  # Remove duplicates
    
    def _is_valid_product_url(self, url: str, site_name: str) -> bool:
        """Validate if URL is a valid product URL."""
        if not URLUtils.is_valid_url(url):
            return False
        
        patterns = PRODUCT_URL_PATTERNS.get(site_name, [])
        if not patterns:
            return True
        
        import re
        for pattern in patterns:
            if re.search(pattern, url):
                return True
        
        return False


class ScoutAgent(BaseAgent, RetryMixin):
    """Scout Agent for discovering product URLs from e-commerce sites."""
    
    def __init__(self):
        tools = [ProductURLDiscoveryTool()]
        
        super().__init__(
            name="scout_agent",
            model=config.ai.default_model,
            tools=tools,
            instruction="""
            You are a specialized agent for discovering product URLs from e-commerce websites.
            
            Your capabilities:
            - Crawl category pages to find product URLs
            - Handle pagination automatically
            - Respect rate limits and anti-bot measures
            - Validate product URLs for accuracy
            - Support multiple e-commerce platforms
            
            Always prioritize:
            1. Respectful crawling with proper delays
            2. High-quality URL validation
            3. Efficient discovery strategies
            4. Error handling and recovery
            """
        )
    
    async def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scout agent input."""
        errors = []
        
        if "site_name" not in input_data:
            errors.append("site_name is required")
        
        if "max_products" in input_data:
            max_products = input_data["max_products"]
            if not isinstance(max_products, int) or max_products <= 0:
                errors.append("max_products must be a positive integer")
        
        return {
            "is_valid": len(errors) == 0,
            "error": "; ".join(errors) if errors else None,
            "details": errors
        }
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process URL discovery request."""
        site_name = input_data["site_name"]
        max_products = input_data.get("max_products", 100)
        category = input_data.get("category", "")
        
        # Use tool to discover URLs
        tool = ProductURLDiscoveryTool()
        result = await tool(
            site_name=site_name,
            max_products=max_products,
            category=category
        )
        
        return result


# Direct tool function for backward compatibility
@tool_error_handler
async def discover_product_urls(site_name: str, max_products: int = 100) -> Dict[str, Any]:
    """
    Direct function to discover product URLs.
    
    Args:
        site_name: Name of the e-commerce site to scout
        max_products: Maximum number of product URLs to discover
        
    Returns:
        Dictionary containing discovered URLs and metadata
    """
    tool = ProductURLDiscoveryTool()
    return await tool(site_name=site_name, max_products=max_products)


# Factory function for creating scout agent
def create_scout_agent() -> Agent:
    """Create and configure Scout Agent for ADK."""
    return Agent(
        name="scout_agent",
        model="gemini-2.0-flash-thinking-exp",
        tools=[discover_product_urls],
        instruction="""
        You are an expert at discovering cosmetic product URLs from e-commerce websites.
        You can crawl category pages and extract product URLs efficiently while respecting rate limits.
        
        Use the discover_product_urls function to find product URLs from supported sites:
        - trendyol
        - gratis  
        - sephora_tr
        - rossmann
        
        Always provide high-quality, validated product URLs.
        """
    )