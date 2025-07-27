"""
🥷 ULTRA-STEALTH BROWSER ENGINE - Production-Ready Anti-Detection System
Advanced browser management with military-grade stealth capabilities
Specifically optimized for Turkish e-commerce sites (Trendyol, Gratis, Sephora, Rossmann)
"""

import asyncio
import random
import json
import base64
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger
import aiohttp
from urllib.parse import urlparse
from datetime import datetime, timedelta
import os


class FingerprintManager:
    """Advanced browser fingerprint randomization"""
    
    def __init__(self):
        self.turkish_locales = ['tr-TR', 'tr']
        self.istanbul_coords = {'latitude': 41.0082, 'longitude': 28.9784}
        self.ankara_coords = {'latitude': 39.9334, 'longitude': 32.8597}
        self.izmir_coords = {'latitude': 38.4237, 'longitude': 27.1428}
        
        self.user_agents = [
            # Latest Chrome versions with Turkish locale priority
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        
        self.viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1440, 'height': 900},
            {'width': 1536, 'height': 864},
            {'width': 1600, 'height': 900}
        ]
        
        self.screen_properties = [
            {'colorDepth': 24, 'pixelDepth': 24},
            {'colorDepth': 32, 'pixelDepth': 32},
        ]

    def generate_fingerprint(self) -> Dict[str, Any]:
        """Generate comprehensive browser fingerprint"""
        viewport = random.choice(self.viewports)
        coords = random.choice([self.istanbul_coords, self.ankara_coords, self.izmir_coords])
        screen = random.choice(self.screen_properties)
        
        return {
            'user_agent': random.choice(self.user_agents),
            'viewport': viewport,
            'geolocation': coords,
            'locale': 'tr-TR',
            'timezone': 'Europe/Istanbul',
            'screen': {
                **screen,
                'width': viewport['width'],
                'height': viewport['height']
            },
            'language': random.choice(['tr-TR,tr;q=0.9,en-US;q=0.8', 'tr-TR,tr;q=0.9,en;q=0.8']),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
        }

    def get_stealth_script(self) -> str:
        """Get comprehensive stealth JavaScript injection"""
        return """
        // Ultra-Stealth Anti-Detection Script for Turkish E-commerce
        
        // 1. Hide webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        
        // 2. Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                    description: "Portable Document Format",
                    filename: "internal-pdf-viewer",
                    length: 1,
                    name: "Chrome PDF Plugin"
                },
                {
                    0: {type: "application/pdf", suffixes: "pdf", description: ""},
                    description: "",
                    filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                    length: 1,
                    name: "Chrome PDF Viewer"
                }
            ]
        });
        
        // 3. Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['tr-TR', 'tr', 'en-US', 'en']
        });
        
        // 4. Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 5. Chrome runtime
        window.chrome = {
            runtime: {
                onConnect: undefined,
                onMessage: undefined
            }
        };
        
        // 6. Override getContext to avoid canvas fingerprinting
        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type, ...args) {
            if (type === '2d') {
                const context = getContext.call(this, type, ...args);
                const originalGetImageData = context.getImageData;
                context.getImageData = function(...args) {
                    const imageData = originalGetImageData.apply(this, args);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.floor(Math.random() * 10) - 5;
                        imageData.data[i + 1] += Math.floor(Math.random() * 10) - 5;
                        imageData.data[i + 2] += Math.floor(Math.random() * 10) - 5;
                    }
                    return imageData;
                };
                return context;
            }
            return getContext.call(this, type, ...args);
        };
        
        // 7. Override screen properties
        Object.defineProperties(screen, {
            width: { get: () => window.outerWidth },
            height: { get: () => window.outerHeight },
            availWidth: { get: () => window.outerWidth },
            availHeight: { get: () => window.outerHeight - 40 }
        });
        
        // 8. Mouse and keyboard events randomization
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (type === 'mousemove') {
                const wrappedListener = function(event) {
                    // Add tiny random delays to mouse movements
                    setTimeout(() => listener(event), Math.random() * 2);
                };
                return originalAddEventListener.call(this, type, wrappedListener, options);
            }
            return originalAddEventListener.call(this, type, listener, options);
        };
        
        // 9. Randomize Date.now() slightly
        const originalNow = Date.now;
        Date.now = function() {
            return originalNow() + Math.floor(Math.random() * 10);
        };
        
        // 10. Hide automation traces
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
        
        console.log('🥷 Ultra-Stealth mode activated for Turkish e-commerce');
        """


class ProxyManager:
    """Advanced proxy rotation and health monitoring"""
    
    def __init__(self, proxy_config: Dict[str, Any]):
        self.proxies = proxy_config.get('proxies', [])
        self.current_proxy_index = 0
        self.proxy_health = {}
        self.proxy_usage_count = {}
        self.banned_proxies = set()
        self.proxy_rotation_threshold = 50  # Rotate after 50 uses
        
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next healthy proxy with load balancing"""
        if not self.proxies:
            return None
            
        available_proxies = [p for p in self.proxies if p not in self.banned_proxies]
        if not available_proxies:
            logger.warning("All proxies are banned, clearing ban list")
            self.banned_proxies.clear()
            available_proxies = self.proxies
            
        # Find proxy with lowest usage
        best_proxy = min(available_proxies, 
                        key=lambda p: self.proxy_usage_count.get(p['server'], 0))
        
        self.proxy_usage_count[best_proxy['server']] = \
            self.proxy_usage_count.get(best_proxy['server'], 0) + 1
            
        return best_proxy
    
    def mark_proxy_failed(self, proxy: Dict[str, str], error_type: str):
        """Mark proxy as failed and potentially ban it"""
        proxy_server = proxy['server']
        
        if proxy_server not in self.proxy_health:
            self.proxy_health[proxy_server] = {'failures': 0, 'last_failure': None}
            
        self.proxy_health[proxy_server]['failures'] += 1
        self.proxy_health[proxy_server]['last_failure'] = datetime.now()
        
        # Ban proxy if too many failures
        if self.proxy_health[proxy_server]['failures'] >= 5:
            self.banned_proxies.add(proxy)
            logger.warning(f"Proxy {proxy_server} banned due to repeated failures")
    
    def should_rotate_proxy(self, proxy: Dict[str, str]) -> bool:
        """Check if proxy should be rotated based on usage"""
        return self.proxy_usage_count.get(proxy['server'], 0) >= self.proxy_rotation_threshold


class UltraStealthBrowser:
    """Production-ready stealth browser for Turkish e-commerce scraping"""
    
    def __init__(self, proxy_config: Optional[Dict[str, Any]] = None):
        self.playwright = None
        self.browser = None
        self.contexts = {}
        self.fingerprint_manager = FingerprintManager()
        self.proxy_manager = ProxyManager(proxy_config or {})
        self.session_lifetime = timedelta(hours=2)  # Rotate sessions every 2 hours
        self.created_sessions = {}
        
    async def initialize(self):
        """Initialize Playwright browser with ultra-stealth configuration"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            
        if self.browser is None:
            # Launch browser with maximum stealth
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    # Core anti-detection
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer',
                    '--disable-web-security',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    
                    # Performance & stealth
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                    '--disable-ipc-flooding-protection',
                    
                    # Turkish locale optimization
                    '--lang=tr-TR',
                    '--accept-lang=tr-TR,tr;q=0.9,en-US;q=0.8',
                    
                    # Additional stealth
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
                    
                    # Memory and performance
                    '--max-old-space-size=4096',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096'
                ]
            )
            logger.info("🥷 Ultra-Stealth browser initialized successfully")
    
    async def create_stealth_context(self, site_name: str) -> BrowserContext:
        """Create ultra-stealth context optimized for specific Turkish e-commerce site"""
        await self.initialize()
        
        # Check if we need to rotate existing context
        context_key = f"{site_name}_{int(time.time() // 3600)}"  # Hour-based rotation
        
        if context_key in self.contexts:
            return self.contexts[context_key]
        
        # Generate unique fingerprint
        fingerprint = self.fingerprint_manager.generate_fingerprint()
        
        # Get optimal proxy
        proxy_config = self.proxy_manager.get_next_proxy()
        
        # Create context with advanced stealth
        context = await self.browser.new_context(
            viewport=fingerprint['viewport'],
            user_agent=fingerprint['user_agent'],
            locale=fingerprint['locale'],
            timezone_id=fingerprint['timezone'],
            geolocation=fingerprint['geolocation'],
            permissions=['geolocation'],
            proxy=proxy_config,
            
            # Advanced headers for Turkish e-commerce
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': fingerprint['language'],
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': f'"{fingerprint["platform"]}"'
            },
            
            # SSL and security
            ignore_https_errors=True,
            java_script_enabled=True,
            
            # Stealth settings
            color_scheme='light',
            reduced_motion='no-preference'
        )
        
        # Inject comprehensive stealth script
        await context.add_init_script(self.fingerprint_manager.get_stealth_script())
        
        # Add site-specific optimizations
        if site_name == 'trendyol':
            await context.add_init_script("""
                // Trendyol-specific stealth enhancements
                Object.defineProperty(navigator, 'connection', {
                    get: () => ({
                        effectiveType: '4g',
                        rtt: 50 + Math.random() * 50,
                        downlink: 10 + Math.random() * 5
                    })
                });
            """)
        elif site_name == 'gratis':
            await context.add_init_script("""
                // Gratis-specific stealth enhancements
                window.addEventListener('beforeunload', () => {
                    // Simulate natural user behavior
                    localStorage.setItem('lastVisit', Date.now());
                });
            """)
        
        # Store context with cleanup
        self.contexts[context_key] = context
        self.created_sessions[context_key] = datetime.now()
        
        # Cleanup old contexts
        await self._cleanup_old_contexts()
        
        logger.info(f"🎭 Stealth context created for {site_name} with proxy: {proxy_config['server'] if proxy_config else 'None'}")
        return context
    
    async def create_stealth_page(self, context: BrowserContext, site_name: str) -> Page:
        """Create stealth page with site-specific optimizations"""
        page = await context.new_page()
        
        # Block unnecessary resources for faster loading
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", 
                        lambda route: route.abort())
        
        # Block tracking and analytics
        blocked_domains = [
            'google-analytics.com',
            'googletagmanager.com',
            'facebook.com',
            'doubleclick.net',
            'googleadservices.com',
            'googlesyndication.com',
            'hotjar.com',
            'intercom.io',
            'yandex.ru',
            'criteo.com'
        ]
        
        for domain in blocked_domains:
            await page.route(f"**/{domain}/**", lambda route: route.abort())
        
        # Add human-like behavior patterns
        await page.add_init_script("""
            // Simulate human scrolling patterns
            let scrollPattern = 0;
            const humanScroll = () => {
                if (scrollPattern % 3 === 0) {
                    window.scrollBy(0, 100 + Math.random() * 200);
                }
                scrollPattern++;
            };
            
            // Random scroll intervals
            setInterval(humanScroll, 2000 + Math.random() * 3000);
            
            // Simulate mouse movements
            document.addEventListener('DOMContentLoaded', () => {
                const moveMouseRandomly = () => {
                    const event = new MouseEvent('mousemove', {
                        clientX: Math.random() * window.innerWidth,
                        clientY: Math.random() * window.innerHeight
                    });
                    document.dispatchEvent(event);
                };
                
                setInterval(moveMouseRandomly, 1000 + Math.random() * 2000);
            });
        """)
        
        # Site-specific page setup
        if site_name == 'trendyol':
            # Trendyol-specific setup
            await page.set_extra_http_headers({
                'Referer': 'https://www.trendyol.com/',
                'Origin': 'https://www.trendyol.com'
            })
        elif site_name == 'gratis':
            # Gratis-specific setup  
            await page.set_extra_http_headers({
                'Referer': 'https://www.gratis.com/',
                'Origin': 'https://www.gratis.com'
            })
        elif site_name == 'sephora_tr':
            # Sephora-specific setup
            await page.set_extra_http_headers({
                'Referer': 'https://www.sephora.com.tr/',
                'Origin': 'https://www.sephora.com.tr'
            })
        elif site_name == 'rossmann':
            # Rossmann-specific setup
            await page.set_extra_http_headers({
                'Referer': 'https://www.rossmann.com.tr/',
                'Origin': 'https://www.rossmann.com.tr'
            })
        
        logger.info(f"🚀 Stealth page ready for {site_name}")
        return page
    
    async def navigate_with_stealth(self, page: Page, url: str, site_name: str) -> bool:
        """Navigate to URL with maximum stealth and error handling"""
        try:
            # Pre-navigation delay (human-like)
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Navigate with realistic timeouts
            response = await page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=30000
            )
            
            if not response or response.status >= 400:
                logger.warning(f"Navigation failed: {response.status if response else 'No response'}")
                return False
            
            # Post-navigation human behavior simulation
            await asyncio.sleep(random.uniform(2.0, 4.0))
            
            # Check for common blocking patterns
            content = await page.content()
            blocking_indicators = [
                'access denied',
                'blocked',
                'robot',
                'automation detected',
                'too many requests',
                'rate limit'
            ]
            
            content_lower = content.lower()
            for indicator in blocking_indicators:
                if indicator in content_lower:
                    logger.warning(f"Blocking detected: {indicator}")
                    return False
            
            # Simulate human reading time
            await asyncio.sleep(random.uniform(1.0, 2.0))
            
            logger.info(f"✅ Successfully navigated to {url}")
            return True
            
        except Exception as e:
            logger.error(f"Navigation error for {url}: {e}")
            return False
    
    async def wait_for_element_smart(self, page: Page, selector: str, timeout: int = 10000) -> Optional[Any]:
        """Smart element waiting with multiple fallback strategies"""
        try:
            # Primary wait strategy
            element = await page.wait_for_selector(selector, timeout=timeout, state='visible')
            if element:
                return element
                
        except Exception:
            # Fallback strategies
            try:
                # Try without visibility requirement
                element = await page.wait_for_selector(selector, timeout=5000, state='attached')
                if element:
                    return element
            except Exception:
                pass
            
            try:
                # Try with shorter timeout and different state
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    return element
            except Exception:
                pass
        
        logger.debug(f"Element not found: {selector}")
        return None
    
    async def random_human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Add human-like random delays"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def _cleanup_old_contexts(self):
        """Clean up old contexts to prevent memory leaks"""
        current_time = datetime.now()
        contexts_to_remove = []
        
        for context_key, created_time in self.created_sessions.items():
            if current_time - created_time > self.session_lifetime:
                contexts_to_remove.append(context_key)
        
        for context_key in contexts_to_remove:
            if context_key in self.contexts:
                try:
                    await self.contexts[context_key].close()
                    del self.contexts[context_key]
                    del self.created_sessions[context_key]
                    logger.info(f"🧹 Cleaned up old context: {context_key}")
                except Exception as e:
                    logger.error(f"Error cleaning up context {context_key}: {e}")
    
    async def close(self):
        """Clean shutdown of all browser resources"""
        try:
            # Close all contexts
            for context in self.contexts.values():
                await context.close()
            self.contexts.clear()
            self.created_sessions.clear()
            
            # Close browser
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            # Stop playwright
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
            logger.info("🏁 Ultra-Stealth browser closed successfully")
            
        except Exception as e:
            logger.error(f"Error during browser cleanup: {e}")
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get browser health and performance metrics"""
        return {
            'active_contexts': len(self.contexts),
            'proxy_health': self.proxy_manager.proxy_health,
            'banned_proxies': len(self.proxy_manager.banned_proxies),
            'session_age': {
                key: (datetime.now() - created).total_seconds() 
                for key, created in self.created_sessions.items()
            },
            'browser_status': 'healthy' if self.browser else 'not_initialized'
        }


# Factory function for easy integration
async def create_ultra_stealth_browser(proxy_config: Optional[Dict[str, Any]] = None) -> UltraStealthBrowser:
    """Create and initialize ultra-stealth browser"""
    browser = UltraStealthBrowser(proxy_config)
    await browser.initialize()
    return browser


# Example usage and testing
if __name__ == "__main__":
    async def test_stealth_browser():
        """Test the ultra-stealth browser with Turkish e-commerce sites"""
        
        # Example proxy configuration
        proxy_config = {
            'proxies': [
                # Add your proxy servers here
                # {'server': 'http://user:pass@proxy1.com:8080'},
                # {'server': 'http://user:pass@proxy2.com:8080'},
            ]
        }
        
        browser = await create_ultra_stealth_browser(proxy_config)
        
        test_sites = [
            ('trendyol', 'https://www.trendyol.com/kozmetik-x-c89'),
            ('gratis', 'https://www.gratis.com/makyaj-c-501'),
            ('sephora_tr', 'https://www.sephora.com.tr/makyaj-c302/'),
            ('rossmann', 'https://www.rossmann.com.tr/makyaj')
        ]
        
        for site_name, url in test_sites:
            try:
                logger.info(f"🧪 Testing {site_name}...")
                
                context = await browser.create_stealth_context(site_name)
                page = await browser.create_stealth_page(context, site_name)
                
                success = await browser.navigate_with_stealth(page, url, site_name)
                
                if success:
                    title = await page.title()
                    logger.info(f"✅ {site_name} test successful - Title: {title}")
                else:
                    logger.error(f"❌ {site_name} test failed")
                
                await page.close()
                
            except Exception as e:
                logger.error(f"Test error for {site_name}: {e}")
        
        # Print health metrics
        metrics = browser.get_health_metrics()
        logger.info(f"🔬 Browser health metrics: {metrics}")
        
        await browser.close()
    
    # Run test
    asyncio.run(test_stealth_browser())