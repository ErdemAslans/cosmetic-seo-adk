"""
Scout Agent - URL Discovery Agent built with Google ADK
Discovers cosmetic product URLs from e-commerce websites
"""

import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import time
from loguru import logger
import random

from google.adk.agents import Agent
from config.models import SiteConfig, ProductData, AgentTask
from config.sites import SITE_CONFIGS


# Tool functions for ADK
async def discover_product_urls(site_name: str, max_products: int = 100) -> Dict[str, Any]:
    """Discover product URLs from e-commerce category pages.
    
    Args:
        site_name: Name of the e-commerce site to scout (e.g., 'trendyol', 'gratis')
        max_products: Maximum number of product URLs to discover
        
    Returns:
        Dictionary containing discovered URLs and metadata
    """
    site_configs = {config.name: config for config in SITE_CONFIGS}
    
    if site_name not in site_configs:
        return {"error": f"Site {site_name} not configured", "discovered_urls": []}
    
    config = site_configs[site_name]
    discovered_urls = []
    
    # Create SSL context that handles certificate issues
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # User agents for rotation
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
    ]
    
    # Create connector with SSL context
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            for category_path in config.category_paths:
                urls = await _crawl_category(
                    session, category_path, config, 
                    max_products // len(config.category_paths),
                    user_agents
                )
                discovered_urls.extend(urls)
                
                if len(discovered_urls) >= max_products:
                    break
            
            logger.info(f"Scout discovered {len(discovered_urls)} URLs from {site_name}")
            
            return {
                "site_name": site_name,
                "discovered_urls": discovered_urls[:max_products],
                "total_count": len(discovered_urls[:max_products]),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error discovering URLs from {site_name}: {e}")
            return {"error": str(e), "discovered_urls": [], "status": "failed"}


async def _crawl_category(
    session: aiohttp.ClientSession, 
    category_path: str, 
    config: SiteConfig, 
    max_urls: int,
    user_agents: List[str]
) -> List[str]:
    """Crawl a category page to find product URLs"""
    product_urls = []
    page = 1
    
    while page <= config.max_pages and len(product_urls) < max_urls:
        try:
            url = urljoin(str(config.base_url), category_path)
            
            # Add pagination based on site
            if page > 1:
                if config.name == "trendyol":
                    url = f"{url}?pi={page}"
                elif config.name == "gratis":
                    url = f"{url}?page={page}"
                else:
                    url = f"{url}?page={page}"
            
            # Enhanced headers with rotation
            headers = {
                **config.headers,
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'DNT': '1'
            }
            
            async with session.get(
                url, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    break
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                product_links = _extract_product_links(soup, config)
                if not product_links:
                    logger.warning(f"No product links found on {url}")
                    break
                
                product_urls.extend(product_links)
                
                if not _has_next_page(soup, config):
                    break
                
                page += 1
                # Random delay to avoid rate limiting
                await asyncio.sleep(config.rate_limit + random.uniform(0.5, 1.5))
                
        except Exception as e:
            logger.error(f"Error crawling {category_path}: {e}")
            break
    
    return product_urls[:max_urls]


def _extract_product_links(soup: BeautifulSoup, config: SiteConfig) -> List[str]:
    """Extract product links from the page with updated selectors"""
    links = []
    
    # Updated selectors for each site
    if config.name == "trendyol":
        # Trendyol updated selectors
        selectors = [
            "div.p-card-wrppr a",  # Product card wrapper
            "div.prdct-cntnr-wrppr a",  # Product container
            "div.product-listing a.product-down",  # Product listing
            "a[href*='/p-']",  # Links containing product pattern
        ]
    elif config.name == "gratis":
        selectors = [
            "div.product-item a.product-link",
            "div.ems-prd-inner a",
            "a.ems-prd-link",
            "div.product a[href*='/p/']"
        ]
    elif config.name == "sephora_tr":
        selectors = [
            "a.product-item-link",
            "div.product-item a",
            "a[href*='/p/']",
            "article.product-item a"
        ]
    elif config.name == "rossmann":
        selectors = [
            "div.product-item a",
            "a.product-link",
            "div.product-card a",
            "a[href*='/p/']"
        ]
    else:
        # Fallback to config selector
        selectors = [config.selectors.get("product_link", "a.product-link")]
    
    # Try each selector until we find products
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            logger.debug(f"Found {len(elements)} elements with selector: {selector}")
            for element in elements:
                href = element.get("href")
                if href:
                    full_url = urljoin(str(config.base_url), href)
                    if _is_valid_product_url(full_url, config):
                        links.append(full_url)
            if links:  # If we found links, stop trying other selectors
                break
    
    return list(set(links))  # Remove duplicates


def _has_next_page(soup: BeautifulSoup, config: SiteConfig) -> bool:
    """Check if there's a next page with updated selectors"""
    next_selectors = {
        "trendyol": ["a.pagination-next", "div.pagination a:last-child", "a[title='Sonraki']"],
        "gratis": ["a.next-page", "li.next a", "a[rel='next']"],
        "sephora_tr": ["a.next", "button.next-page", "a[aria-label='Next']"],
        "rossmann": ["a.pagination-next", "li.next a", "a.next-page"]
    }
    
    selectors = next_selectors.get(config.name, ["a.next-page"])
    
    for selector in selectors:
        if soup.select_one(selector):
            return True
    return False


def _is_valid_product_url(url: str, config: SiteConfig) -> bool:
    """Check if URL is a valid product URL based on site patterns"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    # Site-specific product URL patterns
    if config.name == "trendyol":
        # Trendyol product URLs contain '/p-' followed by product ID
        return '/p-' in path and not any(pattern in path for pattern in [
            '/butik/', '/sr/', '/magaza/', '/hesabim/', '/sepetim/'
        ])
    elif config.name == "gratis":
        # Gratis product URLs end with '/p/' followed by product code
        return '/p/' in path and path.count('/p/') == 1
    elif config.name == "sephora_tr":
        # Sephora product URLs contain '/p/' pattern
        return '/p/' in path
    elif config.name == "rossmann":
        # Rossmann product URLs contain '/p/' pattern
        return '/p/' in path
    
    # General invalid patterns
    invalid_patterns = [
        "/category/", "/search/", "/brand/", "/login", "/register",
        "/cart", "/checkout", "/account", "/help", "/about", "/kampanya"
    ]
    return not any(pattern in path for pattern in invalid_patterns)


# Create Scout Agent using ADK
def create_scout_agent() -> Agent:
    """Factory function to create Scout Agent instance with ADK"""
    return Agent(
        name="scout_agent",
        model="gemini-2.0-flash",
        description="Specialized agent for discovering cosmetic product URLs from e-commerce websites",
        instruction="""You are a Scout Agent specialized in discovering cosmetic product URLs from e-commerce websites.

Your primary task is to use the discover_product_urls tool to find product URLs from specified e-commerce sites.

When asked to scout a site:
1. Call discover_product_urls with the site name and optional max_products parameter
2. Return the discovered URLs in a structured format
3. Report any errors or issues encountered

Available sites:
- trendyol: Turkish e-commerce platform
- gratis: Turkish cosmetics retailer  
- sephora_tr: Sephora Turkey
- rossmann: Rossmann Turkey

Always prioritize finding valid product URLs over quantity. Focus on cosmetic products including skincare, makeup, haircare, and fragrance.""",
        tools=[discover_product_urls]
    )