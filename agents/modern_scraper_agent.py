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
        """Modern realistic user agents for Turkish market"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
    
    async def initialize_browser(self) -> None:
        """Initialize ultra-stealth browser with Playwright"""
        try:
            playwright = await async_playwright().start()
            
            # Proxy varsa kullan
            proxy_settings = None
            if self.proxy_list:
                proxy = random.choice(self.proxy_list)
                proxy_settings = {"server": proxy}
            
            # Launch browser with ULTRA-STEALTH - Advanced anti-detection
            self.browser = await playwright.chromium.launch(
                headless=True,
                proxy=proxy_settings,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer',
                    '--disable-web-security',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                    '--disable-ipc-flooding-protection',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-component-update',
                    '--disable-background-networking',
                    '--disable-sync',
                    '--no-default-browser-check',
                    '--mute-audio',
                    '--no-pings',
                    '--password-store=basic',
                    '--use-mock-keychain',
                    '--disable-hang-monitor',
                    '--disable-prompt-on-repost',
                    '--disable-domain-reliability',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-breakpad',
                    '--disable-client-side-phishing-detection',
                    '--disable-datasaver-prompt',
                    '--disable-desktop-notifications',
                    '--disable-device-discovery-notifications',
                    '--allow-running-insecure-content',
                    '--disable-features=AudioServiceOutOfProcess',
                    '--disable-features=VizServiceBase',
                    '--window-size=1920,1080'
                ]
            )
        
            # Create ultra-stealth context with realistic session persistence
            self.context = await self.browser.new_context(
                viewport={'width': random.choice([1920, 1366, 1536]), 'height': random.choice([1080, 768, 864])},
                user_agent=random.choice(self.user_agents),
                locale='tr-TR',
                timezone_id='Europe/Istanbul',
                ignore_https_errors=True,  # Ignore SSL certificate errors
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': f'"Not A(Brand";v="99", "Chromium";v="121", "Google Chrome";v="121"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                }
            )
            
            # Add realistic cookies to simulate returning user
            await self.context.add_cookies([
                {
                    'name': 'sessionId',
                    'value': f'sess_{random.randint(100000000, 999999999)}',
                    'domain': '.trendyol.com',
                    'path': '/'
                },
                {
                    'name': 'userPreferences',
                    'value': 'lang=tr&currency=TRY&region=istanbul',
                    'domain': '.trendyol.com', 
                    'path': '/'
                }
            ])
        
            # Add ULTRA-STEALTH scripts - Advanced anti-detection
            await self.context.add_init_script("""
            // 🥷 ULTRA-STEALTH MODE - Remove ALL automation traces
            
            // 1. Remove webdriver property completely
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
            
            // 2. Mock realistic plugins array
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    return Object.setPrototypeOf([
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                            description: "Portable Document Format", 
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        }
                    ], PluginArray.prototype);
                },
                configurable: true
            });
            
            // 3. Mock languages naturally
            Object.defineProperty(navigator, 'languages', {
                get: () => ['tr-TR', 'tr', 'en-US', 'en'],
                configurable: true
            });
            
            // 4. Mock hardware concurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8,
                configurable: true
            });
            
            // 5. Mock device memory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
                configurable: true
            });
            
            // 6. Mock connection
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 100,
                    downlink: 2.0
                }),
                configurable: true
            });
            
            // 7. Mock permissions query
            if (navigator.permissions && navigator.permissions.query) {
                const originalQuery = navigator.permissions.query;
                navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            }
            
            // 8. Mock chrome runtime with realistic properties
            if (!window.chrome) {
                window.chrome = {
                    runtime: {
                        onConnect: undefined,
                        onMessage: undefined,
                        connect: function() { return { onDisconnect: {} }; }
                    },
                    app: {
                        isInstalled: false,
                        InstallState: {
                            DISABLED: 'disabled',
                            INSTALLED: 'installed',
                            NOT_INSTALLED: 'not_installed'
                        }
                    }
                };
            }
            
            // 9. Override getParameter for WebGL fingerprinting
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Graphics 6100';
                }
                return getParameter(parameter);
            };
            
            // 10. Mock screen properties
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24,
                configurable: true
            });
            
            Object.defineProperty(screen, 'pixelDepth', {
                get: () => 24,
                configurable: true
            });
            
            // 11. Human-like mouse and keyboard events
            let mouseX = Math.floor(Math.random() * window.innerWidth);
            let mouseY = Math.floor(Math.random() * window.innerHeight);
            
            // Simulate subtle mouse movements
            setInterval(() => {
                mouseX += Math.floor(Math.random() * 3) - 1;
                mouseY += Math.floor(Math.random() * 3) - 1;
                
                document.dispatchEvent(new MouseEvent('mousemove', {
                    clientX: mouseX,
                    clientY: mouseY,
                    bubbles: true
                }));
            }, 100 + Math.random() * 100);
            
            // 12. Remove automation-controlled attribute
            delete navigator.__proto__.webdriver;
            
            // 13. Mock toString methods
            const originalToString = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === navigator.plugins) {
                    return 'function plugins() { [native code] }';
                }
                return originalToString.call(this);
            };
            
            // 14. Remove additional automation flags
            delete navigator.__webdriver_script_func;
            delete navigator.__webdriver_script_function;
            delete navigator.__selenium_unwrapped;
            delete navigator.__webdriver_unwrapped;
            delete navigator.__driver_evaluate;
            delete navigator.__webdriver_evaluate;
            delete navigator.__selenium_evaluate;
            delete navigator.__fxdriver_evaluate;
            delete navigator.__driver_unwrapped;
            delete navigator.__fxdriver_unwrapped;
            delete navigator.__webdriver_script_fn;
            
            // 15. Override chrome runtime
            window.chrome = {
                runtime: {
                    onConnect: undefined,
                    onMessage: undefined
                }
            };
            
            // 16. Mock battery API realistically
            if ('getBattery' in navigator) {
                navigator.getBattery = () => Promise.resolve({
                    charging: Math.random() > 0.5,
                    chargingTime: Math.random() > 0.5 ? 0 : Infinity,
                    dischargingTime: Math.random() * 28800 + 3600, // 1-8 hours
                    level: Math.random() * 0.5 + 0.5 // 50-100%
                });
            }
            
            // 17. Enhance screen properties
            Object.defineProperty(screen, 'availWidth', { get: () => 1920 });
            Object.defineProperty(screen, 'availHeight', { get: () => 1040 });
            
            // 18. Mock realistic connection
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    downlink: Math.random() * 10 + 5, // 5-15 Mbps
                    rtt: Math.random() * 100 + 50 // 50-150ms
                })
            });
            
            // 19. Intercept and modify requests to appear more natural
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                if (args[1]) {
                    args[1].headers = {
                        ...args[1].headers,
                        'sec-ch-ua': '"Not A(Brand";v="99", "Chromium";v="121", "Google Chrome";v="121"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"'
                    };
                }
                return originalFetch.apply(this, args);
            };
            
            console.log('🥷 ULTRA-STEALTH activated - All automation traces removed');
            """)
            
            # Add realistic request interception for better stealth
            await self.context.route("**/*", self._intercept_requests)
            
        except Exception as e:
            logger.error(f"Browser initialization failed: {e}")
            raise e
    
    async def _intercept_requests(self, route, request):
        """Intercept and modify requests to appear more natural"""
        try:
            # Add natural request timing
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
            # Modify headers to be more realistic
            headers = dict(request.headers)
            headers.update({
                'sec-ch-ua': '"Not A(Brand";v="99", "Chromium";v="121", "Google Chrome";v="121"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin'
            })
            
            await route.continue_(headers=headers)
        except Exception as e:
            logger.debug(f"Request interception failed: {e}")
            await route.continue_()
    
    async def discover_urls_advanced(self, site_name: str, max_products: int = 100, target_category: str = None) -> List[str]:
        """Ultra-intelligent URL discovery with category-aware filtering and deep learning"""
        site_config = next((config for config in MODERN_SITE_CONFIGS if config.name == site_name), None)
        if not site_config:
            logger.error(f"Site config not found for {site_name}")
            return []
        
        logger.info(f"🎯 ENHANCED SCOUT AGENT: Targeting '{target_category}' category on {site_name}")
        
        # SMART CATEGORY PATH SELECTION - Only search relevant paths
        relevant_paths = self._select_category_paths(site_config, target_category)
        logger.info(f"📍 Selected {len(relevant_paths)} relevant category paths for '{target_category}'")
        
        discovered_urls = []
        
        # Try ONLY relevant category paths for efficiency
        for category_path in relevant_paths:
            logger.info(f"Processing category path: {category_path}")
            full_url = urljoin(str(site_config.base_url), category_path)
            logger.info(f"Full URL: {full_url}")
            
            try:
                # Strategy 1: Universal intelligent discovery
                urls = await self._universal_url_discovery(site_config, category_path)
                discovered_urls.extend(urls)
                logger.info(f"Universal discovery found {len(urls)} URLs for {category_path}")
                
                # Debug: Log sample URLs from classical discovery
                for i, url in enumerate(urls[:3]):
                    logger.info(f"  Classical URL {i+1}: {url}")
                
                # Strategy 2: AI-powered pattern recognition for each category
                ai_urls = await self._ai_pattern_discovery(site_config, category_path)
                discovered_urls.extend(ai_urls)
                logger.info(f"AI pattern discovery found {len(ai_urls)} URLs for {category_path}")
                
                # Debug: Log sample URLs from AI discovery
                for i, url in enumerate(ai_urls[:3]):
                    logger.info(f"  AI URL {i+1}: {url}")
                
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
        
        # 🎯 ULTRA-ADVANCED CATEGORY FILTERING - Multiple validation layers
        if target_category and validated_urls:
            logger.info(f"🎯 Applying ULTRA-ADVANCED category filtering for '{target_category}'")
            
            # LAYER 1: Advanced URL pattern analysis
            pattern_filtered_urls = await self._ultra_advanced_url_pattern_filtering(
                validated_urls, target_category, site_config
            )
            
            # LAYER 2: Content-based validation (if needed)
            if len(pattern_filtered_urls) < max(5, len(validated_urls) // 3):
                logger.info("📄 Applying content-based validation for additional accuracy")
                content_filtered_urls = await self._ultra_advanced_content_filtering(
                    validated_urls, target_category, site_config
                )
                # Merge results, prioritizing pattern-filtered URLs
                final_urls = list(dict.fromkeys(pattern_filtered_urls + content_filtered_urls))
            else:
                final_urls = pattern_filtered_urls
            
            logger.info(f"🏆 Category filtering result: {len(validated_urls)} → {len(final_urls)} URLs")
            validated_urls = final_urls
        
        # Debug: Log some validated URLs
        for i, url in enumerate(validated_urls[:3]):
            logger.info(f"Final Valid URL {i+1}: {url}")
        
        return validated_urls[:max_products]
    
    def _select_category_paths(self, site_config: SiteConfig, target_category: str) -> List[str]:
        """Intelligently select most relevant category paths based on target category"""
        if not target_category:
            return site_config.category_paths
        
        # SMART CATEGORY MAPPING - Maps user categories to site paths
        category_keywords = {
            "makyaj": ["makyaj", "makeup", "cosmetics", "beauty", "ruj", "lipstick", "far", "eyeshadow", "fondöten"],
            "cilt bakımı": ["cilt", "skin", "bakım", "care", "serum", "krem", "cream", "moisturizer", "temizleyici"],
            "parfüm": ["parfüm", "perfume", "fragrance", "koku", "scent"],
            "saç bakımı": ["saç", "hair", "şampuan", "shampoo", "conditioner", "mask"],
            "vücut bakımı": ["vücut", "body", "losyon", "lotion", "scrub", "peeling"],
            "güzellik": ["güzellik", "beauty", "cosmetic", "wellness"],
            "kozmetik": ["kozmetik", "cosmetic", "beauty", "makeup", "skincare"]
        }
        
        target_keywords = category_keywords.get(target_category.lower(), [target_category.lower()])
        
        # Score each path based on keyword relevance
        path_scores = []
        for path in site_config.category_paths:
            score = 0
            path_lower = path.lower()
            
            # Direct keyword matches get highest score
            for keyword in target_keywords:
                if keyword in path_lower:
                    score += 10
            
            # Partial matches get medium score
            for keyword in target_keywords:
                if any(part in path_lower for part in keyword.split()):
                    score += 5
            
            path_scores.append((path, score))
        
        # Sort by relevance and take top paths
        path_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Take paths with score > 0, or all paths if none match
        relevant_paths = [path for path, score in path_scores if score > 0]
        if not relevant_paths:
            relevant_paths = site_config.category_paths[:3]  # Fallback to first 3
        
        logger.info(f"🎯 Category path selection for '{target_category}':")
        for path, score in path_scores[:5]:
            status = "✅" if path in relevant_paths else "❌"
            logger.info(f"   {status} {path} (score: {score})")
        
        return relevant_paths
    
    async def _ultra_advanced_url_pattern_filtering(self, urls: List[str], target_category: str, site_config: SiteConfig) -> List[str]:
        """🌟 ULTRA ADVANCED URL pattern filtering with ML-like intelligence"""
        if not urls or not target_category:
            return urls
        
        # COMPREHENSIVE URL PATTERN ANALYSIS
        category_url_patterns = {
            "makyaj": {
                "must_contain": ["makyaj", "makeup", "cosmetic", "beauty", "ruj", "lipstick", "far", "eyeshadow", "fondoten", "foundation", "maskara", "mascara"],
                "must_not_contain": ["cilt", "skin", "care", "bakim", "serum", "krem", "cream", "temizleyici", "cleanser", "parfum", "perfume", "sac", "hair", "vucut", "body"],
                "boost_keywords": ["lip", "eye", "face", "color", "renk", "dudak", "goz", "yuz"]
            },
            "cilt bakımı": {
                "must_contain": ["cilt", "skin", "care", "bakim", "serum", "krem", "cream", "temizleyici", "cleanser", "toner", "nemlendirici", "moisturizer"],
                "must_not_contain": ["makyaj", "makeup", "ruj", "lipstick", "far", "eyeshadow", "parfum", "perfume", "sac", "hair", "vucut", "body"],
                "boost_keywords": ["face", "yuz", "goz", "eye", "anti", "aging", "spf", "sun"]
            },
            "parfüm": {
                "must_contain": ["parfum", "perfume", "fragrance", "koku", "scent", "eau", "cologne", "deodorant"],
                "must_not_contain": ["makyaj", "makeup", "cilt", "skin", "bakim", "care", "sac", "hair", "vucut", "body"],
                "boost_keywords": ["spray", "mist", "women", "men", "kadin", "erkek"]
            },
            "saç bakımı": {
                "must_contain": ["sac", "hair", "sampuan", "shampoo", "conditioner", "krem", "mask", "serum", "treatment"],
                "must_not_contain": ["makyaj", "makeup", "cilt", "skin", "parfum", "perfume", "vucut", "body"],
                "boost_keywords": ["style", "stil", "gel", "wax", "spray", "foam"]
            },
            "vücut bakımı": {
                "must_contain": ["vucut", "body", "losyon", "lotion", "dus", "shower", "banyo", "bath", "el", "hand", "ayak", "foot"],
                "must_not_contain": ["makyaj", "makeup", "cilt", "skin", "yuz", "face", "parfum", "perfume", "sac", "hair"],
                "boost_keywords": ["butter", "oil", "yag", "scrub", "peeling"]
            }
        }
        
        target_patterns = category_url_patterns.get(target_category.lower(), {
            "must_contain": [target_category.lower()],
            "must_not_contain": [],
            "boost_keywords": []
        })
        
        filtered_urls = []
        
        for url in urls:
            url_lower = url.lower()
            score = 0
            
            # Check must-contain patterns
            contains_required = any(pattern in url_lower for pattern in target_patterns["must_contain"])
            if contains_required:
                score += 100
            
            # Penalty for must-not-contain patterns
            contains_forbidden = any(pattern in url_lower for pattern in target_patterns["must_not_contain"])
            if contains_forbidden:
                score -= 200  # Heavy penalty
            
            # Boost for relevant keywords
            for boost_word in target_patterns["boost_keywords"]:
                if boost_word in url_lower:
                    score += 25
            
            # Only include URLs with positive score
            if score > 0:
                filtered_urls.append((url, score))
        
        # Sort by score and return URLs
        filtered_urls.sort(key=lambda x: x[1], reverse=True)
        result_urls = [url for url, score in filtered_urls]
        
        logger.info(f"🎯 Ultra-advanced URL filtering: {len(urls)} -> {len(result_urls)} URLs for '{target_category}'")
        return result_urls
    
    async def _ultra_advanced_content_filtering(self, urls: List[str], target_category: str, site_config: SiteConfig) -> List[str]:
        """🌟 ULTRA ADVANCED content-based filtering with AI-powered analysis"""
        if not urls or not target_category or len(urls) < 5:
            return urls  # Skip for small lists
        
        # Advanced category keyword mapping with semantic analysis
        category_semantic_map = {
            "makyaj": {
                "primary_keywords": ["makyaj", "makeup", "cosmetic", "beauty", "güzellik"],
                "product_types": ["ruj", "lipstick", "far", "eyeshadow", "fondöten", "foundation", "maskara", "mascara", "allık", "blush", "kapatıcı", "concealer", "pudra", "powder", "eyeliner", "oje", "nail"],
                "body_parts": ["dudak", "lip", "göz", "eye", "yüz", "face", "kaş", "eyebrow", "kirpik", "eyelash"],
                "attributes": ["mat", "matte", "parlak", "glossy", "su geçirmez", "waterproof", "uzun süre", "long lasting"],
                "negative_indicators": ["cilt bakımı", "skincare", "serum", "nemlendirici", "moisturizer", "temizleyici", "cleanser", "parfüm", "perfume", "şampuan", "shampoo"]
            },
            "cilt bakımı": {
                "primary_keywords": ["cilt", "skin", "bakım", "care", "skincare"],
                "product_types": ["serum", "krem", "cream", "temizleyici", "cleanser", "toner", "nemlendirici", "moisturizer", "maske", "mask", "peeling", "scrub", "güneş kremi", "sunscreen"],
                "body_parts": ["yüz", "face", "göz", "eye", "boyun", "neck", "el", "hand"],
                "attributes": ["anti-aging", "yaşlanma karşıtı", "spf", "hassas", "sensitive", "kuru", "dry", "yağlı", "oily", "karma", "combination"],
                "negative_indicators": ["makyaj", "makeup", "ruj", "lipstick", "far", "eyeshadow", "parfüm", "perfume", "şampuan", "shampoo"]
            },
            "parfüm": {
                "primary_keywords": ["parfüm", "perfume", "fragrance", "koku", "scent"],
                "product_types": ["eau de parfum", "eau de toilette", "cologne", "deodorant", "body spray", "mist"],
                "body_parts": [],
                "attributes": ["erkek", "men", "kadın", "women", "unisex", "uzun süre", "long lasting", "taze", "fresh", "oriental", "woody", "floral"],
                "negative_indicators": ["makyaj", "makeup", "cilt bakımı", "skincare", "şampuan", "shampoo", "vücut losyonu", "body lotion"]
            },
            "saç bakımı": {
                "primary_keywords": ["saç", "hair", "saç bakımı", "hair care"],
                "product_types": ["şampuan", "shampoo", "saç kremi", "conditioner", "maske", "mask", "serum", "yağ", "oil", "köpük", "foam", "sprey", "spray", "jel", "gel", "wax", "mum"],
                "body_parts": ["saç", "hair", "saç derisi", "scalp"],
                "attributes": ["besleyici", "nourishing", "onarıcı", "repairing", "hacim", "volume", "parlaklık", "shine", "kuru", "dry", "yağlı", "oily", "boyalı", "colored"],
                "negative_indicators": ["makyaj", "makeup", "cilt bakımı", "skincare", "parfüm", "perfume", "vücut", "body"]
            },
            "vücut bakımı": {
                "primary_keywords": ["vücut", "body", "vücut bakımı", "body care"],
                "product_types": ["losyon", "lotion", "krem", "cream", "duş jeli", "shower gel", "banyo", "bath", "scrub", "peeling", "yağ", "oil", "butter"],
                "body_parts": ["vücut", "body", "el", "hand", "ayak", "foot", "bacak", "leg", "kol", "arm"],
                "attributes": ["nemlendirici", "moisturizing", "besleyici", "nourishing", "yumuşatıcı", "softening", "kuru cilt", "dry skin"],
                "negative_indicators": ["makyaj", "makeup", "yüz", "face", "cilt bakımı", "facial", "parfüm", "perfume", "saç", "hair"]
            }
        }
        
        target_semantic = category_semantic_map.get(target_category.lower(), {
            "primary_keywords": [target_category.lower()],
            "product_types": [],
            "body_parts": [],
            "attributes": [],
            "negative_indicators": []
        })
        
        validated_urls = []
        sample_urls = urls[:15]  # Sample for content analysis
        
        logger.info(f"🧠 Ultra-advanced content filtering for '{target_category}' - analyzing {len(sample_urls)} URLs...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
            context = await browser.new_context(user_agent=random.choice(self.user_agents))
            
            for i, url in enumerate(sample_urls):
                try:
                    page = await context.new_page()
                    await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                    await asyncio.sleep(random.uniform(0.5, 1.0))
                    
                    # Extract all text content for analysis
                    content_text = await page.evaluate("""
                        () => {
                            const title = document.title || '';
                            const metaDesc = document.querySelector('meta[name="description"]')?.content || '';
                            const h1 = document.querySelector('h1')?.textContent || '';
                            const productName = document.querySelector('.product-name, [data-testid="product-name"], .pr-new-br')?.textContent || '';
                            const productDesc = document.querySelector('.product-description, .detail-desc-item, .product-detail-description')?.textContent || '';
                            const breadcrumb = document.querySelector('.breadcrumb, .breadcrumb-nav, .navigation-path')?.textContent || '';
                            
                            return (title + ' ' + metaDesc + ' ' + h1 + ' ' + productName + ' ' + productDesc + ' ' + breadcrumb).toLowerCase();
                        }
                    """)
                    
                    await page.close()
                    
                    # Advanced semantic scoring
                    score = 0
                    content_lower = content_text.lower()
                    
                    # Primary keywords (highest weight)
                    primary_matches = sum(10 for keyword in target_semantic["primary_keywords"] if keyword in content_lower)
                    score += primary_matches
                    
                    # Product type matches (high weight)
                    product_matches = sum(8 for product_type in target_semantic["product_types"] if product_type in content_lower)
                    score += product_matches
                    
                    # Body part matches (medium weight)
                    body_part_matches = sum(5 for body_part in target_semantic["body_parts"] if body_part in content_lower)
                    score += body_part_matches
                    
                    # Attribute matches (medium weight)
                    attribute_matches = sum(3 for attribute in target_semantic["attributes"] if attribute in content_lower)
                    score += attribute_matches
                    
                    # Negative indicators (heavy penalty)
                    negative_matches = sum(15 for negative in target_semantic["negative_indicators"] if negative in content_lower)
                    score -= negative_matches
                    
                    # URL pattern bonus
                    url_lower = url.lower()
                    if any(keyword in url_lower for keyword in target_semantic["primary_keywords"]):
                        score += 5
                    
                    logger.info(f"   URL {i+1}: Score {score} - {url[:80]}...")
                    
                    if score > 10:  # Threshold for acceptance
                        validated_urls.append((url, score))
                    
                except Exception as e:
                    logger.warning(f"Content analysis failed for {url}: {e}")
                    # Include URL with neutral score if analysis fails
                    validated_urls.append((url, 5))
            
            await browser.close()
        
        # Sort by score and add remaining URLs with lower priority
        validated_urls.sort(key=lambda x: x[1], reverse=True)
        final_urls = [url for url, score in validated_urls]
        
        # Add remaining URLs that weren't analyzed
        remaining_urls = [url for url in urls if url not in final_urls]
        final_urls.extend(remaining_urls)
        
        logger.info(f"🎯 Content filtering complete: {len(final_urls)} URLs validated for '{target_category}'")
        return final_urls
    
    async def _validate_category_content(self, urls: List[str], target_category: str, site_config: SiteConfig) -> List[str]:
        """Validate URLs by checking product content matches target category"""
        if not urls or not target_category:
            return urls
        
        # Category keywords for content matching
        category_keywords = {
            "makyaj": [
                "makyaj", "makeup", "ruj", "lipstick", "far", "eyeshadow", "fondöten", "foundation", 
                "maskara", "mascara", "allık", "blush", "kapatıcı", "concealer", "pudra", "powder",
                "eyeliner", "göz", "eye", "dudak", "lip", "kaş", "eyebrow", "oje", "nail"
            ],
            "cilt bakımı": [
                "cilt", "skin", "bakım", "care", "serum", "krem", "cream", "temizleyici", "cleanser",
                "toner", "nemlendirici", "moisturizer", "güneş", "sun", "spf", "anti-aging",
                "yüz", "face", "göz kremi", "eye cream", "maske", "mask", "peeling", "scrub"
            ],
            "parfüm": [
                "parfüm", "perfume", "fragrance", "koku", "scent", "eau de", "cologne", "deodorant",
                "body spray", "mist", "attar", "essential oil"
            ],
            "saç bakımı": [
                "saç", "hair", "şampuan", "shampoo", "saç kremi", "conditioner", "maske", "mask",
                "serum", "yağ", "oil", "bakım", "treatment", "stil", "styling", "köpük", "foam",
                "sprey", "spray", "jel", "gel", "wax", "mum"
            ],
            "vücut bakımı": [
                "vücut", "body", "losyon", "lotion", "krem", "cream", "duş", "shower", "banyo", "bath",
                "scrub", "peeling", "yağ", "oil", "butter", "tereyağı", "el", "hand", "ayak", "foot"
            ]
        }
        
        target_keywords = category_keywords.get(target_category.lower(), [target_category.lower()])
        logger.info(f"Validating URLs against keywords: {target_keywords[:5]}...")
        
        validated_urls = []
        sample_size = min(len(urls), 20)  # Sample first 20 URLs for performance
        
        for i, url in enumerate(urls[:sample_size]):
            try:
                # Quick validation - check URL structure first
                url_contains_category = any(keyword in url.lower() for keyword in target_keywords)
                if url_contains_category:
                    validated_urls.append(url)
                    continue
                
                # For non-matching URLs, do a quick content check
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Check page title, product name, and category breadcrumbs
                            title = soup.find('title')
                            title_text = title.get_text(strip=True).lower() if title else ""
                            
                            # Look for product name and category info
                            product_info = ""
                            for selector in ['h1', '.product-name', '.breadcrumb', '.category']:
                                elements = soup.select(selector)
                                for elem in elements:
                                    product_info += elem.get_text(strip=True).lower() + " "
                            
                            combined_text = (title_text + " " + product_info).lower()
                            
                            # Check if any category keywords appear in content
                            if any(keyword in combined_text for keyword in target_keywords):
                                validated_urls.append(url)
                                logger.debug(f"✅ URL {i+1} validated by content: {url[:50]}...")
                            else:
                                logger.debug(f"❌ URL {i+1} rejected by content: {url[:50]}...")
                        
            except Exception as e:
                logger.debug(f"Content validation error for {url}: {e}")
                # On error, include URL if it passes URL-based validation
                if any(keyword in url.lower() for keyword in target_keywords):
                    validated_urls.append(url)
            
            # Rate limiting
            await asyncio.sleep(0.5)
        
        # Add remaining URLs without validation if we have too few
        if len(validated_urls) < max(5, len(urls) // 4):
            remaining_urls = urls[sample_size:]
            validated_urls.extend(remaining_urls[:10])
            logger.info(f"Added {len(remaining_urls[:10])} remaining URLs without validation")
        
        logger.info(f"Category content validation: {len(urls)} → {len(validated_urls)} URLs")
        return validated_urls
    
    async def _classical_url_discovery(self, config: SiteConfig, category_path: str) -> List[str]:
        """Enhanced classical scraping with adaptive selectors"""
        page = await self.context.new_page()
        urls = []
        
        try:
            full_url = urljoin(str(config.base_url), category_path)
            logger.info(f"Navigating to: {full_url}")
            
            # Navigate with human-like behavior
            await self._human_like_navigation(page, full_url)
            
            # Wait for dynamic content
            await page.wait_for_load_state('networkidle', timeout=30000)
            await asyncio.sleep(random.uniform(2, 4))
            
            # Check if page loaded successfully
            page_title = await page.title()
            logger.info(f"Page loaded, title: {page_title}")
            
            # Try multiple selector strategies
            selectors = self._get_adaptive_selectors(config.name)
            logger.info(f"Testing {len(selectors)} selector strategies for {config.name}")
            
            for i, selector_group in enumerate(selectors):
                try:
                    selector = selector_group['product_link']
                    logger.info(f"Testing selector {i+1}: {selector_group['name']} - {selector}")
                    
                    elements = await page.query_selector_all(selector)
                    logger.info(f"  Found {len(elements)} elements with this selector")
                    
                    if elements:
                        current_urls = []
                        for j, element in enumerate(elements):
                            href = await element.get_attribute('href')
                            if href:
                                full_product_url = urljoin(str(config.base_url), href)
                                current_urls.append(full_product_url)
                                if j < 3:  # Log first 3 URLs for debugging
                                    logger.info(f"    URL {j+1}: {full_product_url}")
                        
                        urls.extend(current_urls)
                        logger.info(f"  Added {len(current_urls)} URLs from selector: {selector_group['name']}")
                        
                        # If we found URLs with this selector, continue to try others too for Gratis
                        if current_urls and config.name == "gratis":
                            continue  # Try all selectors for Gratis
                        elif current_urls:
                            break  # For other sites, stop after first successful selector
                            
                except Exception as e:
                    logger.error(f"Selector {selector_group['name']} failed: {e}")
                    continue
            
            # Scroll to load more products (for infinite scroll)
            logger.info(f"Found {len(urls)} URLs before scrolling")
            if len(urls) < 20:
                logger.info("Attempting infinite scroll to load more products...")
                await self._handle_infinite_scroll(page)
                
                # Try selectors again after scroll
                for selector_group in selectors:
                    try:
                        selector = selector_group['product_link']
                        elements = await page.query_selector_all(selector)
                        scroll_urls = []
                        for element in elements:
                            href = await element.get_attribute('href')
                            if href:
                                full_product_url = urljoin(str(config.base_url), href)
                                scroll_urls.append(full_product_url)
                        
                        new_urls = [url for url in scroll_urls if url not in urls]
                        urls.extend(new_urls)
                        if new_urls:
                            logger.info(f"  Found {len(new_urls)} additional URLs after scroll")
                    except Exception as e:
                        logger.debug(f"Scroll retry failed for {selector_group['name']}: {e}")
                        continue
                        
            logger.info(f"Classical discovery total: {len(urls)} URLs")
            
        finally:
            await page.close()
        
        return list(set(urls))  # Remove duplicates
    
    async def _universal_url_discovery(self, config: SiteConfig, category_path: str) -> List[str]:
        """Universal intelligent URL discovery for any e-commerce site"""
        page = await self.context.new_page()
        all_urls = set()
        
        try:
            full_url = urljoin(str(config.base_url), category_path)
            logger.info(f"🌐 Universal discovery navigating to: {full_url}")
            
            # Navigate with human-like behavior
            await self._human_like_navigation(page, full_url)
            await page.wait_for_load_state('networkidle', timeout=30000)
            await asyncio.sleep(random.uniform(3, 6))
            
            page_title = await page.title()
            logger.info(f"📄 Page loaded: {page_title}")
            
            # PHASE 1: INTELLIGENT PATTERN DISCOVERY
            discovered_patterns = await self._discover_universal_product_patterns(page)
            logger.info(f"🧠 Discovered {len(discovered_patterns)} universal patterns")
            
            for pattern in discovered_patterns:
                try:
                    elements = await page.query_selector_all(pattern)
                    logger.info(f"  🔍 Pattern '{pattern}': {len(elements)} elements")
                    
                    for element in elements[:50]:  # Limit to prevent overload
                        href = await self._extract_product_url(element, str(config.base_url))
                        if href and self._is_universal_product_url(href):
                            all_urls.add(href)
                except Exception as e:
                    logger.debug(f"Pattern '{pattern}' failed: {e}")
                    continue
            
            logger.info(f"✅ Phase 1 found: {len(all_urls)} URLs")
            
            # PHASE 2: DYNAMIC CONTENT LOADING
            await self._universal_dynamic_loading(page)
            
            # Re-scan top patterns after dynamic loading
            for pattern in discovered_patterns[:3]:
                try:
                    elements = await page.query_selector_all(pattern)
                    for element in elements:
                        href = await self._extract_product_url(element, str(config.base_url))
                        if href and self._is_universal_product_url(href):
                            all_urls.add(href)
                except:
                    continue
            
            logger.info(f"✅ Phase 2 (dynamic) found: {len(all_urls)} URLs")
            
            # PHASE 3: FALLBACK TO SITE-SPECIFIC SELECTORS (ALWAYS RUN IF NO URLS)
            if len(all_urls) == 0:
                logger.info("🔄 PHASE 3: Using site-specific selectors (fallback)")
                
                selectors = self._get_adaptive_selectors(config.name)
                for selector_group in selectors:
                    try:
                        elements = await page.query_selector_all(selector_group['product_link'])
                        logger.info(f"  🎯 Site selector '{selector_group['name']}': {len(elements)} elements")
                        
                        for element in elements:
                            href = await self._extract_product_url(element, str(config.base_url))
                            if href and self._is_universal_product_url(href):
                                all_urls.add(href)
                    except:
                        continue
            
            # PHASE 4: BRUTE FORCE (LAST RESORT)
            if len(all_urls) == 0:
                logger.info("🔄 PHASE 4: Brute force link extraction (last resort)")
                try:
                    # Get ALL links and filter by URL pattern
                    all_links = await page.query_selector_all('a[href]')
                    logger.info(f"  🔗 Found {len(all_links)} total links")
                    
                    for link in all_links:
                        href = await self._extract_product_url(link, str(config.base_url))
                        if href and self._is_universal_product_url(href):
                            all_urls.add(href)
                            
                    logger.info(f"  🎯 Brute force found: {len(all_urls)} product URLs")
                except Exception as e:
                    logger.error(f"Brute force failed: {e}")
            
            logger.info(f"🎯 Universal discovery total: {len(all_urls)} URLs")
            return list(all_urls)[:100]  # Limit results
            
        except Exception as e:
            logger.error(f"Universal discovery failed: {e}")
            return []
        finally:
            await page.close()
    
    async def _discover_universal_product_patterns(self, page: Page) -> List[str]:
        """Advanced universal product pattern discovery for modern SPA sites"""
        patterns = []
        
        try:
            # Wait for content to potentially load
            await asyncio.sleep(3)
            
            # Get all elements for deep analysis
            all_elements = await page.query_selector_all('*')
            logger.info(f"🔍 Deep analysis of {len(all_elements)} DOM elements")
            
            # 1. ADVANCED LINK ANALYSIS WITH DEEPER INSPECTION
            all_links = await page.query_selector_all('a[href]')
            logger.info(f"🔗 Analyzing {len(all_links)} links")
            
            if len(all_links) < 20:  # Too few links - likely SPA not loaded
                logger.warning("⚠️ Very few links detected - implementing SPA content detection")
                await self._force_spa_content_loading(page)
                all_links = await page.query_selector_all('a[href]')
                logger.info(f"🔄 After SPA loading: {len(all_links)} links")
            
            # Enhanced link pattern analysis
            link_patterns = {}
            for link in all_links:
                try:
                    href = await link.get_attribute('href')
                    if not href or len(href) < 5:
                        continue
                    
                    # Get comprehensive element info safely
                    try:
                        element_info = await link.evaluate("""
                            el => ({
                                href: el.href,
                                className: el.className,
                                id: el.id,
                                tagName: el.tagName,
                                parentClass: el.parentElement?.className || '',
                                grandParentClass: el.parentElement?.parentElement?.className || '',
                                text: el.textContent?.trim() || '',
                                hasImages: el.querySelector('img') ? true : false
                            })
                        """)
                    except:
                        # Fallback to basic info
                        element_info = {
                            'href': href,
                            'className': await link.get_attribute('class') or '',
                            'text': await link.inner_text() or '',
                            'parentClass': '',
                            'grandParentClass': '',
                            'hasImages': False
                        }
                    
                    # Check if this looks like a product link
                    if self._analyze_link_for_product_indicators(element_info):
                        # Create multiple pattern candidates
                        if element_info['className']:
                            patterns.append(f"a.{element_info['className'].split()[0]}")
                        if element_info['parentClass']:
                            patterns.append(f".{element_info['parentClass'].split()[0]} a")
                        if element_info['grandParentClass']:
                            patterns.append(f".{element_info['grandParentClass'].split()[0]} a")
                        
                except Exception as e:
                    continue
            
            # 2. SMART CONTAINER DETECTION
            container_candidates = await page.evaluate("""
                () => {
                    const containers = [];
                    const elements = document.querySelectorAll('*');
                    
                    elements.forEach(el => {
                        const children = el.children;
                        if (children.length >= 6 && children.length <= 50) {  // Likely product grid
                            const className = el.className;
                            const hasLinks = el.querySelectorAll('a').length > children.length / 2;
                            const hasImages = el.querySelectorAll('img').length > 0;
                            
                            if (hasLinks && hasImages && className) {
                                containers.push({
                                    selector: '.' + className.split(' ')[0],
                                    childCount: children.length,
                                    linkCount: el.querySelectorAll('a').length
                                });
                            }
                        }
                    });
                    
                    return containers.slice(0, 10);  // Top 10 candidates
                }
            """)
            
            for container in container_candidates:
                patterns.append(f"{container['selector']} a")
                logger.info(f"📦 Smart container: {container['selector']} ({container['childCount']} items)")
            
            # 3. AGGRESSIVE FALLBACK PATTERNS FOR SPA SITES
            aggressive_patterns = [
                # Modern CSS selector patterns
                '[class*="product"] a', '[class*="item"] a', '[class*="card"] a',
                '[class*="tile"] a', '[class*="listing"] a', '[class*="grid"] a',
                
                # Data attribute patterns
                '[data-testid] a', '[data-cy] a', '[data-qa] a', '[data-track] a',
                
                # React/Vue component patterns
                '[class*="Product"] a', '[class*="Item"] a', '[class*="Card"] a',
                
                # Generic but effective patterns
                'div[class] > a', 'li > a', 'article > a',
                'div[class*="list"] a', 'div[class*="grid"] a',
                
                # URL-based patterns (most reliable)
                'a[href*="/p/"]', 'a[href*="/product/"]', 'a[href*="/item/"]',
                'a[href*="-p-"]', 'a[href*="/prd/"]', 'a[href*="/dp/"]'
            ]
            
            for pattern in aggressive_patterns:
                try:
                    elements = await page.query_selector_all(pattern)
                    if len(elements) > 0:
                        patterns.append(pattern)
                        if len(elements) >= 5:  # High-value pattern
                            logger.info(f"🎯 High-value pattern: {pattern} ({len(elements)} elements)")
                except:
                    continue
            
            # 4. LAST RESORT: IMAGE-BASED DETECTION
            if len(patterns) < 3:
                logger.warning("🚨 Few patterns found - using image-based detection")
                image_patterns = await page.evaluate("""
                    () => {
                        const patterns = [];
                        const images = document.querySelectorAll('img');
                        
                        images.forEach(img => {
                            const link = img.closest('a');
                            if (link && link.href) {
                                const parent = link.parentElement;
                                if (parent && parent.className) {
                                    patterns.push('.' + parent.className.split(' ')[0] + ' a');
                                }
                            }
                        });
                        
                        return [...new Set(patterns)].slice(0, 5);
                    }
                """)
                
                patterns.extend(image_patterns)
                logger.info(f"🖼️ Image-based patterns: {len(image_patterns)} found")
            
            # Remove duplicates and return top patterns
            unique_patterns = list(dict.fromkeys(patterns))  # Preserve order
            logger.info(f"✅ Total unique patterns discovered: {len(unique_patterns)}")
            
            return unique_patterns[:15]  # Return top 15 patterns
            
        except Exception as e:
            logger.error(f"Advanced pattern discovery failed: {e}")
            return []
    
    def _analyze_link_for_product_indicators(self, element_info: dict) -> bool:
        """Analyze if a link element looks like a product link"""
        try:
            href = element_info.get('href', '').lower()
            text = element_info.get('text', '').lower()
            class_name = element_info.get('className', '').lower()
            
            # Strong product indicators
            product_indicators = [
                '/p/', '/product/', '/item/', '/detail/', '/prd/', '/dp/',
                '-p-', '_p_', '/goods/', '/article/',
                # Trendyol specific patterns
                '/p-', '-p-', 'trendyol.com/', '/brand/', '/marka/'
            ]
            
            for indicator in product_indicators:
                if indicator in href:
                    return True
            
            # Class-based indicators
            class_indicators = ['product', 'item', 'card', 'tile']
            for indicator in class_indicators:
                if indicator in class_name:
                    return True
            
            # Text-based indicators (for e-commerce)
            if len(text) > 5 and any(word in text for word in ['₺', '$', '€', 'buy', 'price', 'add']):
                return True
            
            # Has images (common in product listings)
            if element_info.get('hasImages', False) and len(href) > 10:
                return True
            
            return False
            
        except:
            return False
    
    async def _force_spa_content_loading(self, page: Page):
        """Force SPA content loading using aggressive techniques"""
        try:
            logger.info("🚀 FORCING SPA CONTENT LOADING...")
            
            # 1. Trigger all possible loading events
            await page.evaluate("""
                // Force trigger all events that might load content
                ['scroll', 'resize', 'load', 'DOMContentLoaded', 'click', 'mouseover', 'focus'].forEach(event => {
                    window.dispatchEvent(new Event(event));
                    document.dispatchEvent(new Event(event));
                });
                
                // Force intersection observer triggers
                if (window.IntersectionObserver) {
                    const observer = new IntersectionObserver(() => {});
                    document.querySelectorAll('*').forEach(el => observer.observe(el));
                }
                
                // Force mutation observer activity
                if (window.MutationObserver) {
                    const observer = new MutationObserver(() => {});
                    observer.observe(document.body, { childList: true, subtree: true });
                }
            """)
            
            # 2. Aggressive scrolling
            for i in range(3):
                await page.evaluate(f'window.scrollTo(0, {i * 500})')
                await asyncio.sleep(1)
            
            # 3. Click on potential loading triggers
            potential_triggers = ['button', '.load', '.more', '.show', '[role="button"]']
            for trigger in potential_triggers:
                try:
                    elements = await page.query_selector_all(trigger)
                    for element in elements[:2]:  # Try first 2
                        try:
                            await element.click(timeout=1000)
                            await asyncio.sleep(1)
                        except:
                            continue
                except:
                    continue
            
            # 4. Wait for potential API calls
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.debug(f"Force SPA loading failed: {e}")
    
    async def _extract_product_url(self, element, base_url: str) -> str:
        """Extract and normalize product URL from element"""
        try:
            href = await element.get_attribute('href')
            if not href:
                return None
            
            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif href.startswith('#') or href.startswith('javascript:'):
                return None
            elif not href.startswith('http'):
                href = urljoin(base_url, href)
            
            return href
            
        except Exception:
            return None
    
    def _is_universal_product_url(self, url: str) -> bool:
        """Universal product URL validation for any e-commerce site"""
        if not url or len(url) < 10:
            return False
        
        url_lower = url.lower()
        
        # Exclude obviously non-product URLs  
        exclude_patterns = [
            '/category/', '/cat/', '/c/', '/search/', '/filter/', '/brand/',
            '/about', '/contact', '/help', '/faq', '/terms',
            '/privacy', '/login', '/register', '/account',
            '.pdf', '.jpg', '.png', '.gif', '.css', '.js',
            'mailto:', 'tel:', 'javascript:', '#',
            # Trendyol specific excludes (to avoid category pages)
            '/kozmetik-x-c', '/makyaj-x-c', '/butik/liste', '/sr?'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
        
        # Look for product indicators
        product_indicators = [
            '/p/', '/product/', '/item/', '/detail/', '/goods/',
            '-p-', '_p_', '/prd/', '/article/', '/dp/', '/pd/'
        ]
        
        for indicator in product_indicators:
            if indicator in url_lower:
                return True
                
        # Trendyol specific product URL pattern: /brand/product-name-p-12345
        import re
        if 'trendyol.com' in url_lower:
            # Trendyol pattern: /brand/product-name-p-12345
            if re.search(r'/[^/]+-p-\d+', url_lower):
                return True
            # Alternative: /product-name-p-12345
            if re.search(r'/\w+-p-\d+$', url_lower):
                return True
        
        # Check for product-like patterns (numbers, hyphens)
        if re.search(r'/[a-z]+-[a-z]+-\d+', url_lower) or re.search(r'/\w+/\d+', url_lower):
            return True
        
        return False
    
    async def _universal_dynamic_loading(self, page: Page):
        """Advanced SPA content loading for modern e-commerce sites"""
        try:
            logger.info("🧠 INTELLIGENT SPA LOADING - Detecting content patterns...")
            
            # 1. WAIT FOR JAVASCRIPT FRAMEWORKS TO INITIALIZE
            await self._wait_for_spa_initialization(page)
            
            # 2. INTERCEPT AND MONITOR API CALLS
            api_calls_detected = await self._monitor_api_calls(page)
            logger.info(f"📡 Detected {len(api_calls_detected)} API calls")
            
            # 3. INTELLIGENT CONTENT LOADING
            content_loaded = await self._trigger_intelligent_loading(page)
            
            # 4. WAIT FOR ACTUAL CONTENT TO APPEAR
            await self._wait_for_content_appearance(page)
            
            # 5. FINAL CONTENT STABILIZATION
            logger.info("⏳ Waiting for content stabilization...")
            await asyncio.sleep(5)  # Extended wait for all content
            
        except Exception as e:
            logger.debug(f"Advanced dynamic loading failed: {e}")
    
    async def _wait_for_spa_initialization(self, page: Page):
        """Wait for SPA frameworks (React, Vue, Angular) to initialize"""
        try:
            logger.info("🚀 Waiting for SPA framework initialization...")
            
            # Check for common SPA frameworks
            spa_checks = [
                "typeof React !== 'undefined'",
                "typeof Vue !== 'undefined'", 
                "typeof angular !== 'undefined'",
                "window.__NEXT_DATA__",
                "window.__NUXT__",
                "document.querySelector('[data-reactroot]')",
                "document.querySelector('[data-server-rendered]')"
            ]
            
            for i in range(10):  # Wait up to 10 seconds
                for check in spa_checks:
                    try:
                        result = await page.evaluate(check)
                        if result:
                            logger.info(f"✅ SPA framework detected: {check}")
                            await asyncio.sleep(2)  # Extra time for initialization
                            return
                    except:
                        continue
                
                await asyncio.sleep(1)
            
            logger.info("📱 No specific SPA framework detected, continuing with universal approach")
            
        except Exception as e:
            logger.debug(f"SPA initialization check failed: {e}")
    
    async def _monitor_api_calls(self, page: Page) -> List[str]:
        """Monitor and wait for API calls that load product data"""
        api_calls = []
        
        try:
            # Set up network request interception
            async def handle_request(request):
                url = request.url
                if any(keyword in url.lower() for keyword in [
                    'api', 'ajax', 'json', 'product', 'search', 'listing', 
                    'catalog', 'items', 'data', 'feed'
                ]):
                    api_calls.append(url)
                    logger.info(f"📡 API call detected: {url}")
            
            page.on('request', handle_request)
            
            # Trigger potential API calls
            await page.mouse.wheel(0, 100)  # Small scroll to trigger lazy loading
            await asyncio.sleep(3)
            
            # Remove listener
            page.remove_listener('request', handle_request)
            
        except Exception as e:
            logger.debug(f"API monitoring failed: {e}")
        
        return api_calls
    
    async def _trigger_intelligent_loading(self, page: Page) -> bool:
        """Intelligently trigger content loading using multiple strategies"""
        content_loaded = False
        
        try:
            # Strategy 1: Progressive scrolling with content detection
            logger.info("📜 Strategy 1: Progressive scrolling")
            initial_links = len(await page.query_selector_all('a[href]'))
            
            for scroll_step in range(5):
                # Scroll down gradually
                await page.evaluate(f'window.scrollTo(0, {(scroll_step + 1) * 300})')
                await asyncio.sleep(2)
                
                # Check if new content appeared
                current_links = len(await page.query_selector_all('a[href]'))
                if current_links > initial_links + 5:
                    logger.info(f"✅ New content detected: {current_links - initial_links} new links")
                    content_loaded = True
                    initial_links = current_links
            
            # Strategy 2: Hover over common loading trigger areas
            logger.info("🎯 Strategy 2: Hover triggers")
            hover_selectors = [
                '.container', '.content', '.main', '.products', 
                '.listing', '.grid', '.items', '#content', '#main'
            ]
            
            for selector in hover_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.hover()
                        await asyncio.sleep(1)
                except:
                    continue
            
            # Strategy 3: JavaScript-based content loading
            logger.info("⚡ Strategy 3: JavaScript loading triggers")
            await page.evaluate("""
                // Trigger common loading events
                window.dispatchEvent(new Event('scroll'));
                window.dispatchEvent(new Event('resize'));
                
                // Try to trigger intersection observers
                const observer = new IntersectionObserver(() => {});
                document.querySelectorAll('*').forEach(el => {
                    observer.observe(el);
                });
                
                // Simulate user interaction
                document.dispatchEvent(new Event('mousemove'));
                document.dispatchEvent(new Event('click'));
            """)
            
            await asyncio.sleep(3)
            
            # Strategy 4: Network idle waiting with timeout
            logger.info("🌐 Strategy 4: Network idle detection")
            try:
                await page.wait_for_load_state('networkidle', timeout=15000)
                content_loaded = True
            except:
                logger.debug("Network idle timeout reached")
            
        except Exception as e:
            logger.debug(f"Intelligent loading failed: {e}")
        
        return content_loaded
    
    async def _wait_for_content_appearance(self, page: Page):
        """Wait for actual product content to appear using smart detection"""
        try:
            logger.info("👀 Waiting for content to appear...")
            
            # Product content indicators
            content_indicators = [
                'a[href*="/p/"]', 'a[href*="/product/"]', 'a[href*="/item/"]',
                '[class*="product"]', '[class*="item"]', '[data-testid*="product"]',
                '.price', '.add-to-cart', '.buy-now', '[class*="price"]'
            ]
            
            for attempt in range(10):  # Wait up to 10 seconds
                for indicator in content_indicators:
                    try:
                        elements = await page.query_selector_all(indicator)
                        if len(elements) >= 3:  # Found multiple product elements
                            logger.info(f"✅ Content appeared: {len(elements)} {indicator} elements")
                            return True
                    except:
                        continue
                
                await asyncio.sleep(1)
            
            logger.info("⏳ Content appearance timeout - proceeding anyway")
            return False
            
        except Exception as e:
            logger.debug(f"Content appearance detection failed: {e}")
            return False
    
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
        """🥷 ULTRA-REALISTIC human navigation with advanced anti-detection"""
        # 1. Human-like pre-navigation delay
        await asyncio.sleep(random.uniform(3, 8))
        
        try:
            # 2. Navigate with realistic loading behavior
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # 3. Immediate human-like actions after page load
            await asyncio.sleep(random.uniform(1, 3))
            
            # 4. Check for real anti-bot measures (much more selective)
            content = await page.content()
            title = await page.title()
            
            # Only trigger on REAL blocking indicators
            real_block_indicators = [
                'you have been blocked', 
                'access denied',
                'please complete the security check',
                'enable javascript and cookies',
                'cloudflare bot detection',
                'suspicious activity detected'
            ]
            
            # Check if this is actually a blocking page
            is_really_blocked = any(indicator in content.lower() for indicator in real_block_indicators)
            is_empty_or_error = len(content) < 3000 and ('error' in title.lower() or 'blocked' in title.lower())
            
            if is_really_blocked or is_empty_or_error:
                logger.warning(f"Real bot detection on {url}")
                await self._execute_bot_evasion_sequence(page)
                await asyncio.sleep(random.uniform(15, 25))
            else:
                # Page loaded successfully
                logger.info(f"✅ Page loaded successfully: {title} ({len(content)} chars)")
            
            # 5. Natural human reading behavior simulation
            await self._simulate_reading_behavior(page)
            
            # 6. Realistic mouse movements (more human-like)
            await self._perform_natural_mouse_movements(page)
            
            # 7. Simulate scrolling behavior like human
            await self._human_scroll_pattern(page)
            
            # 8. Random tab interactions (very human)
            if random.random() < 0.3:  # 30% chance
                await page.keyboard.press('Tab')
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # 9. Wait for full page stabilization with longer timeout
            await page.wait_for_load_state('networkidle', timeout=60000)
            
            # 10. Extended final human-like pause (crucial for bot detection)
            await asyncio.sleep(random.uniform(5, 12))
            
        except Exception as e:
            logger.error(f"Navigation failed for {url}: {e}")
            # Enhanced recovery with realistic delays
            await asyncio.sleep(random.uniform(10, 20))
    
    async def _execute_bot_evasion_sequence(self, page: Page) -> None:
        """Execute advanced bot evasion when detected"""
        try:
            logger.info("🛡️ Executing advanced bot evasion sequence")
            
            # 1. Longer pause to simulate confusion/thinking
            await asyncio.sleep(random.uniform(8, 15))
            
            # 2. Change viewport to common real user resolution
            await page.set_viewport_size({'width': 1366, 'height': 768})
            await asyncio.sleep(random.uniform(2, 4))
            
            # 3. Simulate back/forward navigation (human curiosity)
            try:
                await page.go_back(timeout=10000)
                await asyncio.sleep(random.uniform(3, 6))
                await page.go_forward(timeout=10000)
                await asyncio.sleep(random.uniform(2, 5))
            except:
                pass
            
            # 4. Multiple realistic mouse movements and hovers
            for _ in range(random.randint(3, 6)):
                try:
                    # Hover over various page elements
                    elements = await page.query_selector_all('a, button, img, .product-item')
                    if elements:
                        element = random.choice(elements)
                        await element.hover(timeout=3000)
                        await asyncio.sleep(random.uniform(1, 3))
                except:
                    pass
            
            # 5. Simulate typing in search with realistic patterns
            search_selectors = ['input[type="search"]', 'input[placeholder*="ara"]', 'input[name="q"]', '[data-testid="suggestion"]']
            for selector in search_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        await asyncio.sleep(random.uniform(0.5, 1.5))
                        
                        # Simulate human typing with errors and corrections
                        search_terms = ["makyaj", "kozmetik", "cilt bakım"]
                        term = random.choice(search_terms)
                        
                        # Type with realistic speed and occasional errors
                        for char in term:
                            if random.random() < 0.05:  # 5% chance of typo
                                await page.keyboard.type(chr(ord(char) + 1), delay=random.randint(80, 200))
                                await asyncio.sleep(random.uniform(0.1, 0.3))
                                await page.keyboard.press('Backspace')
                                await asyncio.sleep(random.uniform(0.1, 0.2))
                            await page.keyboard.type(char, delay=random.randint(100, 300))
                        
                        await asyncio.sleep(random.uniform(1, 3))
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(random.uniform(0.5, 1))
                        break
                except:
                    continue
            
            # 6. Scroll with natural patterns (humans scroll a lot)
            for _ in range(random.randint(2, 5)):
                scroll_amount = random.randint(200, 800)
                await page.mouse.wheel(0, scroll_amount)
                await asyncio.sleep(random.uniform(1, 3))
                
            # 7. Simulate right-click context menu (humans do this)
            try:
                await page.mouse.click(random.randint(300, 800), random.randint(200, 600), button='right')
                await asyncio.sleep(random.uniform(0.5, 1))
                await page.keyboard.press('Escape')
            except:
                pass
                
            # 8. Extended final delay to let things settle
            await asyncio.sleep(random.uniform(10, 20))
            
            logger.info("✅ Bot evasion sequence completed")
                
        except Exception as e:
            logger.debug(f"Bot evasion sequence failed: {e}")
    
    async def _simulate_reading_behavior(self, page: Page) -> None:
        """Simulate human reading patterns"""
        try:
            # Scroll down slowly like reading
            for _ in range(random.randint(2, 4)):
                scroll_amount = random.randint(150, 400)
                await page.evaluate(f"""
                    () => {{
                        window.scrollBy({{
                            top: {scroll_amount},
                            left: 0,
                            behavior: 'smooth'
                        }});
                    }}
                """)
                # Human reading pause
                await asyncio.sleep(random.uniform(1.5, 4))
                
        except Exception as e:
            logger.debug(f"Reading simulation failed: {e}")
    
    async def _perform_natural_mouse_movements(self, page: Page) -> None:
        """Perform very natural mouse movements"""
        try:
            viewport_size = page.viewport_size
            width = viewport_size.get('width', 1920)
            height = viewport_size.get('height', 1080)
            
            # Multiple natural mouse movements
            for _ in range(random.randint(3, 7)):
                # Calculate natural movement path
                start_x = random.randint(50, width - 50)
                start_y = random.randint(50, height - 50)
                end_x = start_x + random.randint(-200, 200)
                end_y = start_y + random.randint(-200, 200)
                
                # Ensure coordinates are within bounds
                end_x = max(50, min(width - 50, end_x))
                end_y = max(50, min(height - 50, end_y))
                
                # Natural curved movement
                await page.mouse.move(start_x, start_y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Move with realistic speed variation
                steps = random.randint(15, 30)
                await page.mouse.move(end_x, end_y, steps=steps)
                await asyncio.sleep(random.uniform(0.2, 0.8))
                
                # Sometimes hover over elements
                if random.random() < 0.4:
                    try:
                        elements = await page.query_selector_all('a, button, .product')
                        if elements:
                            element = random.choice(elements)
                            await element.hover(timeout=2000)
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                    except:
                        pass
                        
        except Exception as e:
            logger.debug(f"Natural mouse movements failed: {e}")
    
    async def _human_scroll_pattern(self, page: Page) -> None:
        """Simulate realistic human scrolling patterns"""
        try:
            # Various scrolling patterns humans use
            scroll_patterns = [
                # Slow continuous scroll
                lambda: self._slow_continuous_scroll(page),
                # Quick scroll then pause
                lambda: self._quick_scroll_pause(page), 
                # Random direction scrolling
                lambda: self._random_direction_scroll(page)
            ]
            
            # Execute random scroll pattern
            pattern = random.choice(scroll_patterns)
            await pattern()
            
        except Exception as e:
            logger.debug(f"Human scroll pattern failed: {e}")
    
    async def _slow_continuous_scroll(self, page: Page) -> None:
        """Slow continuous scrolling like reading"""
        for _ in range(random.randint(2, 5)):
            scroll_amount = random.randint(100, 300)
            await page.evaluate(f"""
                () => {{
                    window.scrollBy({{
                        top: {scroll_amount},
                        left: 0,
                        behavior: 'smooth'
                    }});
                }}
            """)
            await asyncio.sleep(random.uniform(1, 3))
    
    async def _quick_scroll_pause(self, page: Page) -> None:
        """Quick scroll followed by longer pause"""
        scroll_amount = random.randint(300, 600)
        await page.evaluate(f"""
            () => {{
                window.scrollBy({{
                    top: {scroll_amount},
                    left: 0,
                    behavior: 'smooth'
                }});
            }}
        """)
        await asyncio.sleep(random.uniform(2, 5))
    
    async def _random_direction_scroll(self, page: Page) -> None:
        """Scroll in different directions randomly"""
        directions = [
            (0, random.randint(200, 400)),    # Down
            (0, -random.randint(100, 200)),   # Up  
            (random.randint(-100, 100), 0),   # Horizontal
        ]
        
        for dx, dy in random.sample(directions, random.randint(1, 2)):
            await page.evaluate(f"""
                () => {{
                    window.scrollBy({{
                        top: {dy},
                        left: {dx},
                        behavior: 'smooth'
                    }});
                }}
            """)
            await asyncio.sleep(random.uniform(0.5, 2))
        
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
                    "product_link": "div.p-card-wrppr a[href*='/p-'], .product-item a[href*='/p-'], .prd-link a[href*='/p-']"
                },
                {
                    "name": "Modern Trendyol Cards", 
                    "product_link": ".p-card-chldrn-cntnr a, [data-id*='product'] a, .product-card a, [class*='product-'] a[href*='-p-'], a[href*='-p-']:not([href*='/c']):not([href*='/brand/']) "
                },
                {
                    "name": "Trendyol Product Links", 
                    "product_link": "a[href*='/p-']:not([href*='/c-']):not([href*='/category']):not([href*='/brand']), .product-container a[href*='/p-']"
                },
                {
                    "name": "Trendyol Universal", 
                    "product_link": "a[href*='trendyol.com/'][href*='-p-'], [class*='card'] a[href*='-p-'], [data-testid*='product'] a"
                },
                {
                    "name": "Trendyol Aggressive", 
                    "product_link": "a[href*='-p-']:not([href*='/c']):not([href*='butik']):not([href*='search']), a[href][title], a[href*='trendyol'][href*='-p-']"
                },
                {
                    "name": "Generic Trendyol",
                    "product_link": "a[href*='trendyol.com'][href*='-p-']:not([href*='/c-'])"
                }
            ],
            "gratis": [
                {
                    "name": "Primary Gratis Products",
                    "product_link": "a[href*='-p-']:not([href*='-b-']), a[href*='/p/'], a[href*='/urun/'], a[href*='/product/']"
                },
                {
                    "name": "Gratis Product Cards", 
                    "product_link": ".product-card a, .product-item a, [class*='product'] a, [data-testid*='product'] a"
                },
                {
                    "name": "Gratis Link Patterns",
                    "product_link": "a[href*='gratis.com'][href*='-p-'], a[href*='gratis.com'][href*='/p/']"
                },
                {
                    "name": "Generic Gratis Links",
                    "product_link": "a[href]:not([href*='javascript']):not([href*='mailto']):not([href*='tel'])"
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
            
            # Site-specific STRICT validation
            if config.name == "trendyol":
                # Sadece -p-XXXXX pattern'i kabul et (minimum 5 digit)
                if re.search(r'-p-\d{5,}', path):
                    # Kategori/kampanya URL'lerini reddet
                    exclude_patterns = ['/butik/', '/sr/', '/magaza/', '/hesabim/', 
                                      '/sepetim/', '/kategori/', '/c-', '/kampanya',
                                      'uygun-fiyatli', 'indirimli', '/x-c', '/kozmetik-x-c',
                                      '/cilt-bakimi-x-c', '/makyaj-x-c', '/parfum-x-c', '/guzellik-x-c']
                    if not any(pattern in path for pattern in exclude_patterns):
                        logger.debug(f"URL {url} accepted - Trendyol strict product pattern")
                        return True
                logger.debug(f"URL {url} rejected - Trendyol strict validation failed")
                return False
                
            elif config.name == "gratis":
                # Gratis için çok geniş kabul - sadece belirgin sistem URL'lerini hariç tut
                exclude_patterns = ['/kategori/', '/marka/', '/hesap', '/sepet', '/giris', '/kayit', 
                                  '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', 
                                  '/api/', '/static/', '/search?', '?', '/contact', '/about']
                if any(pattern in path for pattern in exclude_patterns):
                    logger.debug(f"URL {url} rejected - Gratis excluded pattern")
                    return False
                logger.debug(f"URL {url} accepted - Gratis general acceptance")
                return True
                
            elif config.name == "sephora_tr":
                # Sephora için /p/ veya /product/ pattern'i (minimum 10 char)
                if re.search(r'/p/[a-zA-Z0-9-]{10,}', path) or re.search(r'/product/[a-zA-Z0-9-]{10,}', path):
                    logger.debug(f"URL {url} accepted - Sephora product pattern")
                    return True
                logger.debug(f"URL {url} rejected - Sephora strict validation failed")
                return False
                
            elif config.name == "rossmann":
                # Rossmann için /p/ veya /product/ pattern'i (minimum 8 char)
                if re.search(r'/p/[a-zA-Z0-9-]{8,}', path) or re.search(r'/product/[a-zA-Z0-9-]{8,}', path):
                    logger.debug(f"URL {url} accepted - Rossmann product pattern")
                    return True
                logger.debug(f"URL {url} rejected - Rossmann strict validation failed")
                return False
            
            # Hiçbir pattern match etmezse reddet
            logger.debug(f"URL {url} rejected - no strict pattern match")
            
            logger.debug(f"URL {url} rejected - no matching criteria")
            return False
            
        except Exception as e:
            logger.error(f"URL validation error for {url}: {e}")
            return False
    
    async def scrape_product_advanced(self, url: str, site_name: str) -> Dict[str, Any]:
        """🚀 ULTRA-DEEP product scraping with comprehensive content discovery"""
        page = await self.context.new_page()
        
        try:
            logger.info(f"🔍 DEEP SCRAPER: Starting comprehensive analysis of {url}")
            
            # Navigate with human behavior
            await self._human_like_navigation(page, url)
            
            # 🌟 NEW STRATEGY 1: Deep Page Exploration - Scroll and discover all content
            await self._deep_page_exploration(page, url)
            
            # 🌟 ENHANCED STRATEGY 2: Modern selector-based extraction with deep search
            product_data = await self._enhanced_modern_extraction(page, site_name)
            
            # 🌟 ENHANCED STRATEGY 3: AI-powered deep content discovery
            ai_data = await self._ai_deep_content_discovery(page, url)
            product_data.update(ai_data)
            
            # 🌟 NEW STRATEGY 4: Long description mining from page bottom
            long_descriptions = await self._extract_bottom_descriptions(page)
            if long_descriptions:
                product_data['long_descriptions'] = long_descriptions
                if not product_data.get('description') or len(product_data['description']) < 100:
                    product_data['description'] = long_descriptions[0] if long_descriptions else product_data.get('description', '')
            
            # 🌟 ENHANCED STRATEGY 5: Tab and accordion content extraction
            hidden_content = await self._extract_hidden_content(page)
            product_data.update(hidden_content)
            
            # Original strategies (enhanced)
            structured_data = await self._extract_structured_data(page)
            if structured_data:
                product_data.update(structured_data)
            
            meta_data = await self._extract_meta_data(page)
            product_data.update(meta_data)
            
            # 🌟 NEW STRATEGY 6: Image analysis for additional product info
            image_data = await self._extract_comprehensive_images(page)
            if image_data:
                product_data['images'] = image_data
            
            # Enhanced data cleaning with deep content preservation
            product_data = self._enhanced_clean_product_data(product_data, url, site_name)
            
            logger.info(f"✅ DEEP SCRAPER: Successfully extracted comprehensive data from {url}")
            logger.info(f"📊 Data richness: Description: {len(product_data.get('description', ''))}, Features: {len(product_data.get('features', []))}, Images: {len(product_data.get('images', []))}")
            
            return {
                "success": True,
                "product_data": product_data,
                "status": "success",
                "extraction_depth": "ultra_deep"
            }
            
        except Exception as e:
            logger.error(f"❌ Deep scraping failed for {url}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"error": str(e), "product_data": None}
        finally:
            await page.close()
    
    async def _deep_page_exploration(self, page: Page, url: str):
        """🌟 Deep page exploration - scroll down and discover all content sections"""
        try:
            logger.info(f"🚀 Starting deep page exploration for {url}")
            
            # Wait for initial content load
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Intelligent scrolling to discover all content
            await self._intelligent_scroll_discovery(page)
            
            # Click on tabs and expandable sections
            await self._activate_content_sections(page)
            
            # Wait for any lazy-loaded content
            await asyncio.sleep(2)
            
            logger.info("✅ Deep page exploration completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Deep exploration warning: {e}")
    
    async def _intelligent_scroll_discovery(self, page: Page):
        """Intelligently scroll through page to discover all content"""
        try:
            # Get initial page height
            previous_height = await page.evaluate("document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 10
            
            while scroll_attempts < max_attempts:
                # Scroll down gradually (human-like)
                await page.evaluate("window.scrollBy(0, window.innerHeight * 0.8)")
                await asyncio.sleep(1)
                
                # Check if new content loaded
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == previous_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0  # Reset if new content found
                    previous_height = new_height
                
                # Look for "Load More" or "Show More" buttons
                load_more_selectors = [
                    'button[class*="more"]', 'button[class*="load"]', 'a[class*="more"]',
                    'button:contains("Daha Fazla")', 'button:contains("Load More")',
                    'button:contains("Show More")', 'button:contains("Devamı")'
                ]
                
                for selector in load_more_selectors:
                    try:
                        await page.click(selector, timeout=2000)
                        await asyncio.sleep(2)
                        logger.info(f"📱 Clicked load more button: {selector}")
                        break
                    except:
                        continue
            
            # Scroll to bottom
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            
            logger.info(f"🔄 Completed intelligent scrolling discovery")
            
        except Exception as e:
            logger.warning(f"Scrolling discovery warning: {e}")
    
    async def _activate_content_sections(self, page: Page):
        """Activate tabs, accordions, and expandable content sections"""
        try:
            # Common tab selectors
            tab_selectors = [
                'div[class*="tab"] button', 'ul[class*="tab"] li', 'div[role="tab"]',
                '.tabs button', '.tab-list button', '[data-tab]'
            ]
            
            # Common accordion selectors  
            accordion_selectors = [
                'div[class*="accordion"] button', 'div[class*="collapse"] button',
                'details summary', '[data-toggle="collapse"]', '.accordion-toggle'
            ]
            
            # Common expandable content selectors
            expandable_selectors = [
                'button:contains("Detay")', 'button:contains("Detail")',
                'button:contains("Açıklama")', 'button:contains("Description")',
                'button:contains("Özellik")', 'button:contains("Features")',
                'a:contains("Daha fazla")', 'a:contains("Read more")'
            ]
            
            all_selectors = tab_selectors + accordion_selectors + expandable_selectors
            
            for selector in all_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements[:5]:  # Limit to avoid too many clicks
                        try:
                            await element.click()
                            await asyncio.sleep(0.5)  # Brief wait
                        except:
                            continue
                except:
                    continue
            
            logger.info(f"🎯 Activated content sections")
            
        except Exception as e:
            logger.warning(f"Content section activation warning: {e}")
    
    async def _extract_bottom_descriptions(self, page: Page) -> List[str]:
        """🎯 Extract long descriptions from bottom sections of the page"""
        try:
            # Scroll to bottom first
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            
            # Look for description sections in bottom areas
            bottom_description_selectors = [
                # Generic description selectors
                'div[class*="description"]:last-of-type',
                'div[class*="detail"]:last-of-type', 
                'section[class*="description"]',
                'div[class*="content"]:last-of-type',
                
                # E-commerce specific selectors
                '.product-description', '.product-details', '.product-content',
                '.description-full', '.full-description', '.detailed-description',
                
                # Turkish e-commerce selectors
                '.urun-aciklama', '.detay-aciklama', '.aciklama-detay',
                'div:contains("Ürün Açıklaması")', 'div:contains("Detaylı Açıklama")',
                
                # Bottom section selectors
                'div:last-child p', 'section:last-of-type div', 
                'main > div:last-child', 'article > div:last-child',
                
                # Long content indicators
                'div[class*="long"]', 'div[class*="full"]', 'div[class*="complete"]'
            ]
            
            descriptions = []
            
            for selector in bottom_description_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        text = await element.inner_text()
                        if text and len(text.strip()) > 50:  # Only substantial descriptions
                            clean_text = text.strip()
                            if clean_text not in descriptions:
                                descriptions.append(clean_text)
                except:
                    continue
            
            # Also search for long paragraphs in bottom half of page
            long_paragraphs = await page.evaluate("""
                () => {
                    const pageHeight = document.body.scrollHeight;
                    const bottomThreshold = pageHeight * 0.6; // Bottom 40% of page
                    
                    const paragraphs = Array.from(document.querySelectorAll('p, div'));
                    return paragraphs
                        .filter(p => {
                            const rect = p.getBoundingClientRect();
                            return rect.top > bottomThreshold && p.innerText.length > 100;
                        })
                        .map(p => p.innerText.trim())
                        .slice(0, 5); // Max 5 long paragraphs
                }
            """)
            
            descriptions.extend(long_paragraphs)
            
            # Remove duplicates and sort by length (longest first)
            unique_descriptions = list(dict.fromkeys(descriptions))
            unique_descriptions.sort(key=len, reverse=True)
            
            logger.info(f"🎯 Found {len(unique_descriptions)} bottom descriptions")
            return unique_descriptions[:3]  # Return top 3 longest
            
        except Exception as e:
            logger.error(f"Bottom description extraction error: {e}")
            return []
    
    async def _extract_hidden_content(self, page: Page) -> Dict[str, Any]:
        """Extract content from tabs, accordions, and hidden sections"""
        hidden_data = {
            'features': [],
            'ingredients': [],
            'usage': '',
            'additional_info': []
        }
        
        try:
            # JavaScript to extract all hidden/tab content
            hidden_content = await page.evaluate("""
                () => {
                    const result = {
                        features: [],
                        ingredients: [],
                        usage: '',
                        additional_info: []
                    };
                    
                    // Feature extraction from various sources
                    const featureSelectors = [
                        'div[class*="feature"]', 'ul[class*="feature"]',
                        'div[class*="benefit"]', 'div[class*="advantage"]',
                        'li', '.bullet-point', '.highlight'
                    ];
                    
                    featureSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            const text = el.innerText?.trim();
                            if (text && text.length > 10 && text.length < 200) {
                                result.features.push(text);
                            }
                        });
                    });
                    
                    // Ingredient extraction
                    const ingredientKeywords = ['ingredient', 'içerik', 'composition', 'formula'];
                    document.querySelectorAll('*').forEach(el => {
                        const text = el.innerText?.toLowerCase() || '';
                        if (ingredientKeywords.some(keyword => text.includes(keyword))) {
                            const content = el.innerText?.trim();
                            if (content && content.length > 20) {
                                result.ingredients.push(content);
                            }
                        }
                    });
                    
                    // Usage instructions
                    const usageKeywords = ['kullanım', 'usage', 'how to use', 'directions', 'nasıl kullanılır'];
                    document.querySelectorAll('*').forEach(el => {
                        const text = el.innerText?.toLowerCase() || '';
                        if (usageKeywords.some(keyword => text.includes(keyword)) && !result.usage) {
                            result.usage = el.innerText?.trim() || '';
                        }
                    });
                    
                    return result;
                }
            """)
            
            hidden_data.update(hidden_content)
            logger.info(f"🔍 Extracted hidden content: {len(hidden_data['features'])} features, {len(hidden_data['ingredients'])} ingredients")
            
        except Exception as e:
            logger.error(f"Hidden content extraction error: {e}")
        
        return hidden_data
    
    async def _extract_comprehensive_images(self, page: Page) -> List[str]:
        """Extract all product images comprehensively"""
        try:
            images = await page.evaluate("""
                () => {
                    const imageSelectors = [
                        'img[class*="product"]',
                        'img[class*="item"]',
                        'div[class*="gallery"] img',
                        'div[class*="slider"] img',
                        'div[class*="carousel"] img',
                        '.product-image img',
                        '.gallery img',
                        '.thumbnail img'
                    ];
                    
                    const imageUrls = new Set();
                    
                    imageSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(img => {
                            const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy');
                            if (src && !src.includes('placeholder') && !src.includes('loading')) {
                                imageUrls.add(src);
                            }
                        });
                    });
                    
                    return Array.from(imageUrls).slice(0, 10); // Max 10 images
                }
            """)
            
            logger.info(f"🖼️ Extracted {len(images)} comprehensive images")
            return images
            
        except Exception as e:
            logger.error(f"Image extraction error: {e}")
            return []
    
    async def _enhanced_modern_extraction(self, page: Page, site_name: str) -> Dict[str, Any]:
        """Enhanced modern extraction with deep content discovery"""
        # Use the original method but with enhanced selectors
        basic_data = await self._modern_selector_extraction(page, site_name)
        
        # Enhance with additional deep extraction
        enhanced_data = await page.evaluate("""
            () => {
                const data = {};
                
                // Enhanced name extraction
                if (!data.name) {
                    const nameSelectors = [
                        'h1', '.product-title', '.product-name', '.item-title',
                        '[class*="title"]:first-of-type', '[class*="name"]:first-of-type'
                    ];
                    for (const selector of nameSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText?.trim()) {
                            data.name = el.innerText.trim();
                            break;
                        }
                    }
                }
                
                // Enhanced description with priority for longer content
                const descriptionSelectors = [
                    '.product-description', '.description', '.content',
                    '[class*="detail"]', '[class*="info"]', 'p'
                ];
                
                let longestDescription = '';
                for (const selector of descriptionSelectors) {
                    document.querySelectorAll(selector).forEach(el => {
                        const text = el.innerText?.trim();
                        if (text && text.length > longestDescription.length) {
                            longestDescription = text;
                        }
                    });
                }
                
                if (longestDescription) {
                    data.description = longestDescription;
                }
                
                return data;
            }
        """)
        
        # Merge enhanced data with basic data
        basic_data.update(enhanced_data)
        return basic_data
    
    async def _ai_deep_content_discovery(self, page: Page, url: str) -> Dict[str, Any]:
        """AI-powered deep content discovery with comprehensive analysis"""
        try:
            # Enhanced AI extraction with deeper analysis
            ai_data = await page.evaluate("""
                () => {
                    const data = {
                        reviews: [],
                        specifications: {},
                        brand_info: '',
                        category_hints: []
                    };
                    
                    // Extract reviews/comments
                    const reviewSelectors = [
                        '.review', '.comment', '[class*="review"]', 
                        '[class*="feedback"]', '[class*="opinion"]'
                    ];
                    
                    reviewSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(el => {
                            const text = el.innerText?.trim();
                            if (text && text.length > 20 && text.length < 500) {
                                data.reviews.push(text);
                            }
                        });
                    });
                    
                    // Extract specifications
                    document.querySelectorAll('table tr, .spec-item, .specification').forEach(el => {
                        const text = el.innerText?.trim();
                        if (text && text.includes(':')) {
                            const [key, value] = text.split(':').map(s => s.trim());
                            if (key && value) {
                                data.specifications[key] = value;
                            }
                        }
                    });
                    
                    // Extract brand info
                    const brandSelectors = ['.brand', '[class*="brand"]', '[class*="manufacturer"]'];
                    for (const selector of brandSelectors) {
                        const el = document.querySelector(selector);
                        if (el && el.innerText?.trim()) {
                            data.brand_info = el.innerText.trim();
                            break;
                        }
                    }
                    
                    return data;
                }
            """)
            
            logger.info(f"🤖 AI deep discovery extracted {len(ai_data.get('reviews', []))} reviews, {len(ai_data.get('specifications', {}))} specs")
            return ai_data
            
        except Exception as e:
            logger.error(f"AI deep content discovery error: {e}")
            return {}
    
    def _enhanced_clean_product_data(self, data: Dict[str, Any], url: str, site_name: str) -> Dict[str, Any]:
        """Enhanced data cleaning that preserves deep content"""
        cleaned = self._clean_product_data(data, url, site_name)
        
        # Preserve long descriptions and additional content
        if 'long_descriptions' in data:
            cleaned['long_descriptions'] = data['long_descriptions']
        
        if 'specifications' in data:
            cleaned['specifications'] = data['specifications']
        
        # Ensure we have substantial description
        if cleaned.get('description') and len(cleaned['description']) < 50:
            if 'long_descriptions' in data and data['long_descriptions']:
                cleaned['description'] = data['long_descriptions'][0]
        
        return cleaned
    
    async def _modern_selector_extraction(self, page: Page, site_name: str) -> Dict[str, Any]:
        """Modern selector-based extraction with adaptive strategies and JavaScript fallback"""
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
            
            # JavaScript fallback if field is still empty
            if not data.get(field):
                try:
                    js_value = await page.evaluate(f"""
                        () => {{
                            // {field} için akıllı extraction
                            if ('{field}' === 'category') {{
                                const breadcrumb = document.querySelector('nav[aria-label="breadcrumb"], .breadcrumb, nav.breadcrumb');
                                if (breadcrumb) {{
                                    const links = breadcrumb.querySelectorAll('a');
                                    if (links.length > 1) {{
                                        return links[1].textContent.trim();
                                    }}
                                }}
                                // Alternative: look for category in page title or headings
                                const title = document.title;
                                if (title.includes('Makyaj')) return 'Makyaj';
                                if (title.includes('Cilt Bakım')) return 'Cilt Bakımı';
                                if (title.includes('Parfüm')) return 'Parfüm';
                                if (title.includes('Saç Bakım')) return 'Saç Bakımı';
                                return 'Kozmetik';
                            }}
                            
                            if ('{field}' === 'description') {{
                                // Tüm p tag'lerini kontrol et
                                const paragraphs = document.querySelectorAll('p');
                                for (const p of paragraphs) {{
                                    const text = p.textContent.trim();
                                    if (text.length > 100 && !text.includes('cookie') && !text.includes('gizlilik')) {{
                                        return text;
                                    }}
                                }}
                                
                                // Alternative: look for any meaningful text in divs
                                const divs = document.querySelectorAll('div');
                                for (const div of divs) {{
                                    const text = div.textContent.trim();
                                    if (text.length > 50 && text.length < 1000 && 
                                        (text.includes('ürün') || text.includes('kullanım') || text.includes('özellik'))) {{
                                        return text;
                                    }}
                                }}
                            }}
                            
                            if ('{field}' === 'name') {{
                                // Try multiple heading selectors
                                const headings = document.querySelectorAll('h1, h2, [class*="title"], [class*="name"]');
                                for (const heading of headings) {{
                                    const text = heading.textContent.trim();
                                    if (text.length > 10 && text.length < 200) {{
                                        return text;
                                    }}
                                }}
                            }}
                            
                            if ('{field}' === 'brand') {{
                                // Look for brand in various places
                                const brandSelectors = ['[class*="brand"]', '[class*="marka"]', 'h1 a', '.manufacturer'];
                                for (const selector of brandSelectors) {{
                                    const element = document.querySelector(selector);
                                    if (element) {{
                                        const text = element.textContent.trim();
                                        if (text.length > 2 && text.length < 50) {{
                                            return text;
                                        }}
                                    }}
                                }}
                            }}
                            
                            if ('{field}' === 'price') {{
                                // Look for price patterns
                                const priceElements = document.querySelectorAll('*');
                                for (const element of priceElements) {{
                                    const text = element.textContent.trim();
                                    if (text.match(/\d+[.,]\d+.*₺/) || text.match(/₺.*\d+[.,]\d+/)) {{
                                        return text;
                                    }}
                                }}
                            }}
                            
                            return '';
                        }}
                    """)
                    if js_value and js_value.strip():
                        data[field] = js_value.strip()
                        logger.debug(f"JavaScript fallback succeeded for {field}: {js_value[:50]}...")
                except Exception as e:
                    logger.debug(f"JavaScript fallback failed for {field}: {e}")
        
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
    
    async def discover_and_scrape(self, site_name: str, category: str, limit: int = 10) -> Dict[str, Any]:
        """Fast discovery and scraping method for compatibility with FastWorkflow"""
        try:
            await self.initialize_browser()
            
            # Discover URLs using the existing method
            urls = await self.discover_urls_advanced(site_name, limit, category)
            
            # Scrape products from discovered URLs
            products = []
            for url in urls[:limit]:
                try:
                    product_data = await self.scrape_product_advanced(url, site_name)
                    if product_data and product_data.get('success'):
                        products.append(product_data.get('data', {}))
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")
                    continue
            
            return {
                'success': True,
                'products': products,
                'urls_found': len(urls),
                'products_scraped': len(products)
            }
            
        except Exception as e:
            logger.error(f"discover_and_scrape error: {e}")
            return {
                'success': False,
                'error': str(e),
                'products': [],
                'urls_found': 0,
                'products_scraped': 0
            }
    
    async def close(self):
        """Clean up resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()


# Direct tool functions for integration
async def discover_product_urls_advanced(site_name: str, max_products: int = 100, target_category: str = None) -> Dict[str, Any]:
    """Ultra-intelligent URL discovery with category-aware filtering"""
    scraper = ModernScraperAgent()
    
    try:
        await scraper.initialize_browser()
        urls = await scraper.discover_urls_advanced(site_name, max_products, target_category)
        
        return {
            "site_name": site_name,
            "target_category": target_category,
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
        model="gemini-2.0-flash-thinking-exp",
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