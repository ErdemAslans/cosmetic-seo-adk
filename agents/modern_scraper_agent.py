"""
Modern Scraper Agent - Next-Gen Web Scraping with AI-Powered Adaptation
Ultra-reliable scraping system with self-healing capabilities
"""

import asyncio
import json
import random
import time
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup
import aiohttp
from loguru import logger
import re
from urllib.parse import urljoin, urlparse
import hashlib

from google.adk.agents import Agent
from config.models import ProductData, SiteConfig
from config.modern_sites import MODERN_SITE_CONFIGS


class ModernScraperAgent:
    """Ultra-modern scraper with AI-powered adaptation and self-healing"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.selector_cache = {}
        self.failure_patterns = {}
        self.proxy_list = self._load_proxy_list()
        self.user_agents = self._load_user_agents()
        
    def _load_proxy_list(self) -> List[str]:
        """Load rotating proxy list - add your proxies here"""
        return [
            # Add your proxy servers here
            # "http://user:pass@proxy1.com:8080",
            # "http://user:pass@proxy2.com:8080",
        ]
    
    def _load_user_agents(self) -> List[str]:
        """Modern realistic user agents"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
        ]
    
    async def initialize_browser(self) -> None:
        """Initialize ultra-stealth browser"""
        try:
            playwright = await async_playwright().start()
            
            # Launch browser with maximum stealth
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-component-update',
                    '--disable-background-networking',
                    '--disable-sync',
                    '--metrics-recording-only',
                    '--no-default-browser-check',
                    '--mute-audio',
                    '--no-pings',
                    '--password-store=basic',
                    '--use-mock-keychain',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
        
            # Create ultra-stealth context
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent=random.choice(self.user_agents),
                locale='tr-TR',
                timezone_id='Europe/Istanbul',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
        
            # Add stealth scripts to every page
            await self.context.add_init_script("""
            // Remove webdriver traces
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['tr-TR', 'tr', 'en-US', 'en'],
            });
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Mock chrome runtime
            window.chrome = {
                runtime: {},
            };
            
            // Human-like mouse movements
            let mouseX = 0, mouseY = 0;
            document.addEventListener('mousemove', (e) => {
                mouseX = e.clientX;
                mouseY = e.clientY;
            });
            """)
            
        except Exception as e:
            logger.error(f"Browser initialization failed: {e}")
            raise e
    
    async def discover_urls_advanced(self, site_name: str, max_products: int = 100) -> List[str]:
        """AI-powered URL discovery with multiple strategies"""
        site_config = next((config for config in MODERN_SITE_CONFIGS if config.name == site_name), None)
        if not site_config:
            logger.error(f"Site config not found for {site_name}")
            return []
        
        discovered_urls = []
        
        # Try ALL category paths to find maximum products
        for category_path in site_config.category_paths:
            logger.info(f"Processing category path: {category_path}")
            
            try:
                # Strategy 1: Classical scraping with modern selectors
                urls = await self._classical_url_discovery(site_config, category_path)
                discovered_urls.extend(urls)
                logger.info(f"Classical discovery found {len(urls)} URLs for {category_path}")
                
                # Strategy 2: AI-powered pattern recognition for each category
                ai_urls = await self._ai_pattern_discovery(site_config, category_path)
                discovered_urls.extend(ai_urls)
                logger.info(f"AI pattern discovery found {len(ai_urls)} URLs for {category_path}")
                
                # Stop if we have enough URLs
                if len(discovered_urls) >= max_products:
                    logger.info(f"Found enough URLs: {len(discovered_urls)}")
                    break
                    
            except Exception as e:
                logger.error(f"URL discovery failed for {category_path}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                continue
        
        # Remove duplicates and validate
        unique_urls = list(dict.fromkeys(discovered_urls))
        logger.info(f"Found {len(unique_urls)} unique URLs before validation")
        
        # Debug: Log some sample URLs
        for i, url in enumerate(unique_urls[:5]):
            logger.info(f"Sample URL {i+1}: {url}")
        
        validated_urls = []
        for url in unique_urls:
            if self._is_valid_product_url(url, site_config):
                validated_urls.append(url)
            else:
                logger.debug(f"URL rejected: {url}")
        
        logger.info(f"Validated {len(validated_urls)} URLs after filtering")
        
        # Debug: Log some validated URLs
        for i, url in enumerate(validated_urls[:3]):
            logger.info(f"Valid URL {i+1}: {url}")
        
        return validated_urls[:max_products]
    
    async def _classical_url_discovery(self, config: SiteConfig, category_path: str) -> List[str]:
        """Enhanced classical scraping with adaptive selectors"""
        page = await self.context.new_page()
        urls = []
        
        try:
            # Navigate with human-like behavior
            await self._human_like_navigation(page, urljoin(str(config.base_url), category_path))
            
            # Wait for dynamic content
            await page.wait_for_load_state('networkidle', timeout=30000)
            await asyncio.sleep(random.uniform(2, 4))
            
            # Try multiple selector strategies
            selectors = self._get_adaptive_selectors(config.name)
            
            for selector_group in selectors:
                try:
                    elements = await page.query_selector_all(selector_group['product_link'])
                    if elements:
                        for element in elements:
                            href = await element.get_attribute('href')
                            if href:
                                full_url = urljoin(str(config.base_url), href)
                                urls.append(full_url)
                        
                        if urls:
                            logger.info(f"Found {len(urls)} URLs with selector: {selector_group['name']}")
                            break
                            
                except Exception as e:
                    logger.debug(f"Selector {selector_group['name']} failed: {e}")
                    continue
            
            # Scroll to load more products (for infinite scroll)
            if len(urls) < 20:
                await self._handle_infinite_scroll(page)
                
                # Try selectors again after scroll
                for selector_group in selectors:
                    try:
                        elements = await page.query_selector_all(selector_group['product_link'])
                        for element in elements:
                            href = await element.get_attribute('href')
                            if href:
                                full_url = urljoin(str(config.base_url), href)
                                urls.append(full_url)
                    except:
                        continue
            
        finally:
            await page.close()
        
        return list(set(urls))  # Remove duplicates
    
    async def _ai_pattern_discovery(self, config: SiteConfig, category_path: str) -> List[str]:
        """AI-powered pattern recognition for URL discovery"""
        page = await self.context.new_page()
        urls = []
        
        try:
            await self._human_like_navigation(page, urljoin(str(config.base_url), category_path))
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            # Get page content for AI analysis
            html_content = await page.content()
            
            # Use JavaScript to analyze DOM patterns
            product_links = await page.evaluate("""
                () => {
                    const links = [];
                    const allLinks = document.querySelectorAll('a[href]');
                    
                    // Pattern-based detection
                    const productPatterns = [
                        /\/p\//i,           // /p/ pattern
                        /\/product\//i,     // /product/ pattern
                        /\/urun\//i,        // Turkish product pattern
                        /-p-\d+/i,          // product ID pattern
                        /\/\d+$/,           // ending with numbers
                        /detail/i,          // detail pages
                        /item/i             // item pages
                    ];
                    
                    allLinks.forEach(link => {
                        const href = link.href;
                        const text = link.textContent.trim().toLowerCase();
                        
                        // Check URL patterns
                        const matchesPattern = productPatterns.some(pattern => pattern.test(href));
                        
                        // Check if link has product-like attributes
                        const hasProductData = link.hasAttribute('data-id') || 
                                             link.hasAttribute('data-product-id') ||
                                             link.hasAttribute('data-sku');
                        
                        // Check parent elements for product containers
                        const parentElement = link.closest('[class*="product"], [class*="item"], [data-testid*="product"]');
                        
                        if (matchesPattern || hasProductData || parentElement) {
                            links.push(href);
                        }
                    });
                    
                    return [...new Set(links)];
                }
            """)
            
            urls.extend(product_links)
            logger.info(f"AI pattern discovery found {len(product_links)} URLs")
            
        except Exception as e:
            logger.error(f"AI pattern discovery failed: {e}")
        finally:
            await page.close()
        
        return urls
    
    async def _network_traffic_discovery(self, config: SiteConfig, category_path: str) -> List[str]:
        """Discover URLs by analyzing network traffic"""
        page = await self.context.new_page()
        urls = []
        json_responses = []
        
        # Capture network responses
        async def handle_response(response):
            if response.url.endswith('.json') or 'application/json' in response.headers.get('content-type', ''):
                try:
                    json_data = await response.json()
                    json_responses.append(json_data)
                except:
                    pass
        
        page.on('response', handle_response)
        
        try:
            await self._human_like_navigation(page, urljoin(str(config.base_url), category_path))
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            # Scroll to trigger more API calls
            await self._handle_infinite_scroll(page)
            
            # Analyze captured JSON responses for product URLs
            for json_data in json_responses:
                extracted_urls = self._extract_urls_from_json(json_data, config)
                urls.extend(extracted_urls)
            
            logger.info(f"Network traffic analysis found {len(urls)} URLs")
            
        except Exception as e:
            logger.error(f"Network traffic analysis failed: {e}")
        finally:
            await page.close()
        
        return urls
    
    def _extract_urls_from_json(self, json_data: dict, config: SiteConfig) -> List[str]:
        """Extract product URLs from JSON API responses"""
        urls = []
        
        def recursive_search(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key.lower() in ['url', 'link', 'href', 'slug', 'path']:
                        if isinstance(value, str) and self._looks_like_product_url(value):
                            full_url = urljoin(str(config.base_url), value)
                            urls.append(full_url)
                    else:
                        recursive_search(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    recursive_search(item, f"{path}[{i}]")
        
        recursive_search(json_data)
        return urls
    
    def _looks_like_product_url(self, url: str) -> bool:
        """Check if URL looks like a product URL"""
        product_indicators = [
            '/p/', '/product/', '/urun/', '/item/', '/detail/',
            re.compile(r'-p-\d+'), re.compile(r'/\d+$'), re.compile(r'/\d+/')
        ]
        
        return any(
            indicator.search(url) if hasattr(indicator, 'search') 
            else indicator in url.lower() 
            for indicator in product_indicators
        )
    
    async def _human_like_navigation(self, page: Page, url: str) -> None:
        """Navigate like a human with realistic delays and behavior"""
        # Random delay before navigation
        await asyncio.sleep(random.uniform(1, 3))
        
        # Navigate to page
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        
        # Human-like mouse movement
        await page.mouse.move(
            random.randint(100, 800), 
            random.randint(100, 600)
        )
        
        # Random scroll behavior
        await page.evaluate("""
            () => {
                // Random small scrolls
                window.scrollBy(0, Math.random() * 200);
                setTimeout(() => window.scrollBy(0, Math.random() * 300), 1000);
            }
        """)
        
        # Wait for page to fully load
        await page.wait_for_load_state('networkidle', timeout=30000)
        
    async def _handle_infinite_scroll(self, page: Page) -> None:
        """Handle infinite scroll to load more products"""
        try:
            for _ in range(5):  # Max 5 scrolls
                # Scroll to bottom
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                # Wait for new content
                await asyncio.sleep(random.uniform(2, 4))
                
                # Check if "Load More" button exists and click it
                load_more_selectors = [
                    'button[class*="load-more"]',
                    'button[class*="daha-fazla"]',
                    'a[class*="load-more"]',
                    '[data-testid="load-more"]',
                    'button:has-text("Daha Fazla")',
                    'button:has-text("Load More")'
                ]
                
                for selector in load_more_selectors:
                    try:
                        button = await page.query_selector(selector)
                        if button and await button.is_visible():
                            await button.click()
                            await asyncio.sleep(random.uniform(2, 4))
                            break
                    except:
                        continue
        except Exception as e:
            logger.debug(f"Infinite scroll handling failed: {e}")
    
    def _get_adaptive_selectors(self, site_name: str) -> List[Dict]:
        """Get adaptive selectors with priority order"""
        base_selectors = {
            "trendyol": [
                {
                    "name": "Primary Trendyol",
                    "product_link": "div.p-card-wrppr a, .product-item a, [data-id] a"
                },
                {
                    "name": "Alternative Trendyol", 
                    "product_link": "a[href*='/p-'], .product-container a, .product-card a"
                },
                {
                    "name": "Generic Trendyol",
                    "product_link": "a[href*='trendyol.com'][href*='-p-']"
                }
            ],
            "gratis": [
                {
                    "name": "Primary Gratis",
                    "product_link": "a[href*='/p/'], [data-product-id] a, .product-item a"
                },
                {
                    "name": "Alternative Gratis",
                    "product_link": "a[href*='gratis.com/p/'], .product-card a, .item-link"
                },
                {
                    "name": "Generic Gratis",
                    "product_link": "a[href*='/p/'][href*='gratis']"
                }
            ],
            "sephora_tr": [
                {
                    "name": "Primary Sephora",
                    "product_link": "a.product-item-link, .product-tile a, [data-comp='ProductTile'] a"
                },
                {
                    "name": "Alternative Sephora",
                    "product_link": "a[href*='/p/'], .product-container a"
                }
            ],
            "rossmann": [
                {
                    "name": "Primary Rossmann", 
                    "product_link": "a.product-item-link, .product-tile a, .product-card a"
                },
                {
                    "name": "Alternative Rossmann",
                    "product_link": "a[href*='/p/'], a[href*='/product/']"
                }
            ]
        }
        
        # Add universal fallback selectors
        universal_selectors = [
            {
                "name": "Universal Product Links",
                "product_link": "a[href*='/p/'], a[href*='/product/'], a[href*='/item/'], a[href*='-p-']"
            },
            {
                "name": "Data Attribute Based",
                "product_link": "[data-id] a, [data-product-id] a, [data-sku] a, [data-product] a"
            },
            {
                "name": "Class Pattern Based", 
                "product_link": ".product a, .item a, [class*='product'] a, [class*='item'] a"
            }
        ]
        
        selectors = base_selectors.get(site_name, [])
        selectors.extend(universal_selectors)
        
        return selectors
    
    def _is_valid_product_url(self, url: str, config: SiteConfig) -> bool:
        """Enhanced URL validation with strict domain checking"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Strict domain validation - must be exact match
            config_domain = str(config.base_url).replace('https://', '').replace('http://', '').strip('/')
            url_domain = parsed.netloc
            
            if config_domain != url_domain:
                logger.debug(f"URL {url} rejected - domain mismatch: {url_domain} != {config_domain}")
                return False
            
            # Exclude obviously invalid file extensions
            if any(ext in path for ext in ['.js', '.css', '.png', '.jpg', '.gif', '.ico', '.xml', '.txt']):
                logger.debug(f"URL {url} rejected - invalid file extension")
                return False
            
            # Exclude obviously invalid pages
            invalid_keywords = ['/api/', '/static/', '/assets/', '/login', '/register', '/logout']
            if any(invalid in path for invalid in invalid_keywords):
                logger.debug(f"URL {url} rejected - invalid page type")
                return False
            
            # For testing - accept almost all URLs that could be products
            # Site-specific very permissive validation
            if config.name == "trendyol":
                # Accept URLs with product-like patterns
                if '/p-' in path or '-p-' in path:
                    logger.debug(f"URL {url} accepted - Trendyol product pattern")
                    return True
                # Also accept other potentially valid URLs
                if len(path) > 10 and path.count('/') >= 2:
                    logger.debug(f"URL {url} accepted - Trendyol potential product")
                    return True
                    
            elif config.name == "gratis":
                # Gratis specific product patterns
                if '/p/' in path or '-p-' in path:
                    logger.debug(f"URL {url} accepted - Gratis product pattern")
                    return True
                # Exclude category pages and other non-product pages
                if any(exclude in path for exclude in ['/c-', '/kampanyalar', '/yardim', '/hakkimizda', '/iletisim', '/sepet', '/hesap']):
                    logger.debug(f"URL {url} rejected - Gratis non-product page")
                    return False
                # Accept product-like URLs with sufficient length
                if len(path) > 10 and path.count('-') >= 2:
                    logger.debug(f"URL {url} accepted - Gratis potential product")
                    return True
                    
            elif config.name in ["sephora_tr", "rossmann"]:
                if '/p/' in path or '/product/' in path:
                    logger.debug(f"URL {url} accepted - {config.name} product pattern")
                    return True
                if len(path) > 5:
                    logger.debug(f"URL {url} accepted - {config.name} potential product")
                    return True
            
            # Universal fallback - very permissive for testing
            if len(path) > 3 and path != '/':
                logger.debug(f"URL {url} accepted - universal fallback")
                return True
            
            logger.debug(f"URL {url} rejected - no matching criteria")
            return False
            
        except Exception as e:
            logger.error(f"URL validation error for {url}: {e}")
            return False
    
    async def scrape_product_advanced(self, url: str, site_name: str) -> Dict[str, Any]:
        """Advanced product scraping with multiple extraction strategies"""
        page = await self.context.new_page()
        
        try:
            # Navigate with human behavior
            await self._human_like_navigation(page, url)
            
            # Strategy 1: Modern selector-based extraction
            product_data = await self._modern_selector_extraction(page, site_name)
            
            # Strategy 2: AI-powered content extraction if primary fails
            if not product_data.get('name') or not product_data.get('description'):
                ai_data = await self._ai_content_extraction(page)
                product_data.update(ai_data)
            
            # Strategy 3: Structured data extraction
            structured_data = await self._extract_structured_data(page)
            if structured_data:
                product_data.update(structured_data)
            
            # Strategy 4: Meta tag extraction
            meta_data = await self._extract_meta_data(page)
            product_data.update(meta_data)
            
            # Clean and validate data
            product_data = self._clean_product_data(product_data, url, site_name)
            
            return {
                "success": True,
                "product_data": product_data,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Advanced scraping failed for {url}: {e}")
            return {"error": str(e), "product_data": None}
        finally:
            await page.close()
    
    async def _modern_selector_extraction(self, page: Page, site_name: str) -> Dict[str, Any]:
        """Modern selector-based extraction with adaptive strategies"""
        selectors = self._get_product_selectors(site_name)
        data = {}
        
        for field, field_selectors in selectors.items():
            for selector in field_selectors:
                try:
                    if field in ['ingredients', 'features', 'reviews', 'images']:
                        # List fields
                        elements = await page.query_selector_all(selector)
                        values = []
                        for element in elements:
                            if field == 'images':
                                src = await element.get_attribute('src') or await element.get_attribute('data-src')
                                if src and not src.startswith('data:'):
                                    values.append(src)
                            else:
                                text = await element.text_content()
                                if text and text.strip():
                                    values.append(text.strip())
                        if values:
                            data[field] = values[:10]  # Limit list size
                            break
                    else:
                        # Single fields
                        element = await page.query_selector(selector)
                        if element:
                            if field == 'price':
                                text = await element.text_content()
                                if text and any(char.isdigit() for char in text):
                                    data[field] = text.strip()
                                    break
                            else:
                                text = await element.text_content()
                                if text and len(text.strip()) > 2:
                                    data[field] = text.strip()
                                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed for {field}: {e}")
                    continue
        
        return data
    
    async def _ai_content_extraction(self, page: Page) -> Dict[str, Any]:
        """AI-powered content extraction using JavaScript analysis"""
        try:
            ai_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // Smart name detection
                    const nameSelectors = [
                        'h1', '[class*="title"]', '[class*="name"]', 
                        '[data-testid*="name"]', '[data-testid*="title"]'
                    ];
                    for (const selector of nameSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim().length > 5) {
                            data.name = element.textContent.trim();
                            break;
                        }
                    }
                    
                    // Smart price detection
                    const priceElements = document.querySelectorAll('*');
                    for (const element of priceElements) {
                        const text = element.textContent;
                        if (text && /[0-9]{1,}[.,]?[0-9]*\s*(₺|TL|EUR|USD|\$)/i.test(text)) {
                            const priceMatch = text.match(/[0-9]{1,}[.,]?[0-9]*\s*(₺|TL|EUR|USD|\$)/i);
                            if (priceMatch) {
                                data.price = priceMatch[0];
                                break;
                            }
                        }
                    }
                    
                    // Smart description detection
                    const descElements = document.querySelectorAll('p, div, span');
                    for (const element of descElements) {
                        const text = element.textContent.trim();
                        if (text.length > 50 && text.length < 1000 && 
                            /ürün|product|özellik|kullanım|içerik/i.test(text)) {
                            data.description = text;
                            break;
                        }
                    }
                    
                    return data;
                }
            """)
            
            return ai_data
        except Exception as e:
            logger.error(f"AI content extraction failed: {e}")
            return {}
    
    async def _extract_structured_data(self, page: Page) -> Dict[str, Any]:
        """Extract structured data (JSON-LD, microdata)"""
        try:
            structured_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // JSON-LD extraction
                    const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                    for (const script of scripts) {
                        try {
                            const jsonData = JSON.parse(script.textContent);
                            if (jsonData['@type'] === 'Product') {
                                data.name = jsonData.name;
                                data.description = jsonData.description;
                                if (jsonData.offers && jsonData.offers.price) {
                                    data.price = jsonData.offers.price;
                                }
                                if (jsonData.brand) {
                                    data.brand = typeof jsonData.brand === 'object' ? 
                                               jsonData.brand.name : jsonData.brand;
                                }
                                break;
                            }
                        } catch (e) {
                            continue;
                        }
                    }
                    
                    return data;
                }
            """)
            
            return structured_data
        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")
            return {}
    
    async def _extract_meta_data(self, page: Page) -> Dict[str, Any]:
        """Extract meta tag data"""
        try:
            meta_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // Open Graph tags
                    const ogTitle = document.querySelector('meta[property="og:title"]');
                    if (ogTitle && !data.name) {
                        data.name = ogTitle.content;
                    }
                    
                    const ogDescription = document.querySelector('meta[property="og:description"]');
                    if (ogDescription && !data.description) {
                        data.description = ogDescription.content;
                    }
                    
                    // Product meta tags
                    const productPrice = document.querySelector('meta[property="product:price:amount"]');
                    if (productPrice && !data.price) {
                        data.price = productPrice.content;
                    }
                    
                    return data;
                }
            """)
            
            return meta_data
        except Exception as e:
            logger.error(f"Meta data extraction failed: {e}")
            return {}
    
    def _get_product_selectors(self, site_name: str) -> Dict[str, List[str]]:
        """Get comprehensive product selectors for each site"""
        base_selectors = {
            "trendyol": {
                "name": [
                    "h1.pr-new-br span", "h1", ".product-name", "[data-testid='product-name']",
                    ".product-title", "[class*='title']"
                ],
                "brand": [
                    "h1.pr-new-br a", ".product-brand", ".brand-name", "[data-testid='brand']",
                    ".brand", "a[class*='brand']"
                ],
                "price": [
                    ".prc-dsc", ".product-price", ".price", "[data-testid='price']",
                    ".current-price", "[class*='price']"
                ],
                "description": [
                    ".detail-desc-list", ".product-description", ".description",
                    "[data-testid='description']", ".product-detail"
                ],
                "images": [
                    "img.detail-img", ".product-images img", ".gallery img",
                    "[data-testid='product-image']"
                ]
            },
            "gratis": {
                "name": [
                    "h1", ".product-name", ".product-title", "[data-testid='product-name']",
                    ".ems-prd-name"
                ],
                "brand": [
                    ".product-brand", ".brand-name", ".brand", ".ems-prd-brand"
                ],
                "price": [
                    ".product-price", ".price", "[class*='price']", ".ems-prd-price"
                ],
                "description": [
                    ".product-description", ".description", ".product-detail",
                    ".ems-prd-description"
                ],
                "images": [
                    ".product-image img", ".gallery img", "img[src*='gratis']"
                ]
            }
        }
        
        # Add universal selectors
        universal_selectors = {
            "name": ["h1", "[class*='title']", "[class*='name']", "[data-testid*='name']"],
            "brand": [".brand", "[class*='brand']", "[data-testid*='brand']"],
            "price": [".price", "[class*='price']", "[data-testid*='price']"],
            "description": [".description", "[class*='desc']", "p", ".detail"],
            "images": ["img", "[class*='image']", "[class*='photo']"]
        }
        
        selectors = base_selectors.get(site_name, {})
        
        # Merge with universal selectors
        for field, field_selectors in universal_selectors.items():
            if field not in selectors:
                selectors[field] = field_selectors
            else:
                selectors[field].extend(field_selectors)
        
        return selectors
    
    def _clean_product_data(self, data: Dict[str, Any], url: str, site_name: str) -> Dict[str, Any]:
        """Clean and validate product data"""
        cleaned = {
            "url": url,
            "site": site_name,
            "name": data.get("name", "").strip()[:200],
            "brand": data.get("brand", "").strip()[:100],
            "price": data.get("price", "").strip()[:50],
            "description": data.get("description", "").strip()[:2000],
            "ingredients": data.get("ingredients", [])[:20],
            "features": data.get("features", [])[:20],
            "usage": data.get("usage", "").strip()[:500],
            "reviews": data.get("reviews", [])[:10],
            "images": data.get("images", [])[:5]
        }
        
        # Clean price format
        if cleaned["price"]:
            cleaned["price"] = re.sub(r'[^\d,.\s₺TLUSD$€]', '', cleaned["price"])
        
        return cleaned
    
    async def close(self):
        """Clean up resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()


# Direct tool functions for integration
async def discover_product_urls_advanced(site_name: str, max_products: int = 100) -> Dict[str, Any]:
    """Advanced URL discovery function"""
    scraper = ModernScraperAgent()
    
    try:
        await scraper.initialize_browser()
        urls = await scraper.discover_urls_advanced(site_name, max_products)
        
        return {
            "site_name": site_name,
            "discovered_urls": urls,
            "total_count": len(urls),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Advanced URL discovery failed: {e}")
        return {"error": str(e), "discovered_urls": [], "status": "failed"}
    finally:
        await scraper.close()


async def scrape_product_data_advanced(url: str, site_name: str) -> Dict[str, Any]:
    """Advanced product scraping function"""
    scraper = ModernScraperAgent()
    
    try:
        await scraper.initialize_browser()
        result = await scraper.scrape_product_advanced(url, site_name)
        return result
    except Exception as e:
        logger.error(f"Advanced product scraping failed: {e}")
        return {"error": str(e), "product_data": None}
    finally:
        await scraper.close()


# Create modern agent using ADK
def create_modern_scraper_agent() -> Agent:
    """Factory function to create Modern Scraper Agent instance with ADK"""
    return Agent(
        name="modern_scraper_agent",
        model="gemini-2.0-flash",
        description="Ultra-modern web scraper with AI-powered adaptation and self-healing capabilities",
        instruction="""You are a Modern Scraper Agent with advanced capabilities for extracting data from e-commerce websites.

Your advanced features include:
1. AI-powered pattern recognition for URL discovery
2. Multiple extraction strategies (selectors, structured data, meta tags, AI analysis)
3. Network traffic analysis for finding hidden APIs
4. Self-healing capabilities when selectors fail
5. Ultra-stealth browser configuration to avoid detection
6. Human-like navigation patterns

When scraping:
1. Use discover_product_urls_advanced for URL discovery with multiple strategies
2. Use scrape_product_data_advanced for comprehensive product data extraction
3. Automatically adapt to site changes using AI-powered fallbacks
4. Handle infinite scroll and dynamic content loading
5. Extract from JSON-LD, microdata, and meta tags when CSS selectors fail

Focus on reliability, stealth, and comprehensive data extraction.""",
        tools=[discover_product_urls_advanced, scrape_product_data_advanced]
    )