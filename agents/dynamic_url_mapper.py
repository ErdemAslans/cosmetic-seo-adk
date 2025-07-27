"""
Dynamic URL Mapper - Otomatik kategori URL keşfi
Trendyol gibi sitelerin sürekli değişen kategori URL'lerini otomatik bulur
"""

import asyncio
import aiohttp
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from loguru import logger
import json
from datetime import datetime, timedelta

class DynamicURLMapper:
    """Dinamik URL mapping sistemi"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 saat cache
        self.session = None
        
        # Site-specific patterns
        self.site_patterns = {
            'trendyol': {
                'base_url': 'https://www.trendyol.com',
                'category_patterns': [
                    r'/([^/]*cilt[^/]*)-x-c(\d+)',
                    r'/([^/]*makyaj[^/]*)-x-c(\d+)',
                    r'/([^/]*parfum[^/]*)-x-c(\d+)',
                    r'/([^/]*kozmetik[^/]*)-x-c(\d+)',
                    r'/([^/]*guzellik[^/]*)-x-c(\d+)',
                    r'/([^/]*sac[^/]*)-x-c(\d+)'
                ],
                'menu_selectors': [
                    'a[href*="kozmetik"]',
                    'a[href*="cilt"]',
                    'a[href*="makyaj"]',
                    'a[href*="parfum"]',
                    'nav a',
                    '.category-menu a',
                    '.main-nav a'
                ]
            },
            'gratis': {
                'base_url': 'https://www.gratis.com',
                'category_patterns': [
                    r'/([^/]*cilt[^/]*)-c-(\d+)',
                    r'/([^/]*makyaj[^/]*)-c-(\d+)',
                    r'/([^/]*parfum[^/]*)-c-(\d+)'
                ],
                'menu_selectors': ['nav a', '.menu a', 'a[href*="-c-"]']
            }
        }
    
    async def discover_category_urls(self, site_name: str, target_categories: List[str]) -> Dict[str, str]:
        """Belirli kategoriler için URL'leri otomatik keşfet"""
        cache_key = f"category_urls_{site_name}_{hash(tuple(target_categories))}"
        
        # Cache kontrolü
        if cache_key in self.cache:
            cache_time, cached_data = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                logger.info(f"🚀 Cache hit for {site_name} categories")
                return cached_data
        
        logger.info(f"🔍 Discovering category URLs for {site_name}: {target_categories}")
        
        try:
            # Multiple discovery strategies
            urls = {}
            
            # Strategy 1: Ana sayfa menü scraping
            menu_urls = await self._scrape_main_menu(site_name, target_categories)
            urls.update(menu_urls)
            
            # Strategy 2: Sitemap analysis
            sitemap_urls = await self._analyze_sitemap(site_name, target_categories)
            urls.update(sitemap_urls)
            
            # Strategy 3: Search-based discovery
            search_urls = await self._search_based_discovery(site_name, target_categories)
            urls.update(search_urls)
            
            # Strategy 4: Pattern-based URL generation
            pattern_urls = await self._pattern_based_discovery(site_name, target_categories)
            urls.update(pattern_urls)
            
            # Validate URLs
            validated_urls = await self._validate_category_urls(urls)
            
            # Cache results
            self.cache[cache_key] = (time.time(), validated_urls)
            
            logger.info(f"✅ Discovered {len(validated_urls)} category URLs for {site_name}")
            return validated_urls
            
        except Exception as e:
            logger.error(f"URL discovery error for {site_name}: {e}")
            return {}
    
    async def _scrape_main_menu(self, site_name: str, categories: List[str]) -> Dict[str, str]:
        """Ana sayfa menüsünden kategori URL'lerini çıkar"""
        site_config = self.site_patterns.get(site_name, {})
        base_url = site_config.get('base_url', '')
        selectors = site_config.get('menu_selectors', [])
        
        if not base_url:
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    if response.status != 200:
                        return {}
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    found_urls = {}
                    
                    # Her selector'ı dene
                    for selector in selectors:
                        try:
                            links = soup.select(selector)
                            for link in links:
                                href = link.get('href', '')
                                text = link.get_text(strip=True).lower()
                                
                                if href:
                                    full_url = urljoin(base_url, href)
                                    
                                    # Kategori eşleştirme
                                    for category in categories:
                                        if self._matches_category(text, category, href):
                                            found_urls[category] = full_url
                                            logger.debug(f"Found {category}: {full_url}")
                                            break
                        except Exception as e:
                            logger.debug(f"Selector error {selector}: {e}")
                            continue
                    
                    return found_urls
                    
        except Exception as e:
            logger.error(f"Menu scraping error: {e}")
            return {}
    
    async def _analyze_sitemap(self, site_name: str, categories: List[str]) -> Dict[str, str]:
        """Sitemap'ten kategori URL'lerini analiz et"""
        site_config = self.site_patterns.get(site_name, {})
        base_url = site_config.get('base_url', '')
        
        if not base_url:
            return {}
        
        sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_categories.xml",
            f"{base_url}/category-sitemap.xml"
        ]
        
        found_urls = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for sitemap_url in sitemap_urls:
                    try:
                        async with session.get(sitemap_url, timeout=10) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # XML'den URL'leri çıkar
                                urls = re.findall(r'<loc>(.*?)</loc>', content)
                                
                                for url in urls:
                                    for category in categories:
                                        if self._matches_category_url(url, category):
                                            found_urls[category] = url
                                            logger.debug(f"Sitemap found {category}: {url}")
                                            break
                    except:
                        continue
        except:
            pass
        
        return found_urls
    
    async def _search_based_discovery(self, site_name: str, categories: List[str]) -> Dict[str, str]:
        """Site içi arama ile kategori URL'lerini bul"""
        site_config = self.site_patterns.get(site_name, {})
        base_url = site_config.get('base_url', '')
        
        if not base_url:
            return {}
        
        found_urls = {}
        
        # Site-specific search patterns
        search_patterns = {
            'trendyol': f"{base_url}/sr?q={{category}}",
            'gratis': f"{base_url}/arama?q={{category}}"
        }
        
        search_pattern = search_patterns.get(site_name)
        if not search_pattern:
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for category in categories:
                    search_url = search_pattern.format(category=category.replace(' ', '%20'))
                    
                    try:
                        async with session.get(search_url, allow_redirects=True) as response:
                            if response.status == 200:
                                # Redirect URL'i kontrol et
                                final_url = str(response.url)
                                
                                if self._is_valid_category_url(final_url, site_name):
                                    found_urls[category] = final_url
                                    logger.debug(f"Search found {category}: {final_url}")
                    except:
                        continue
        except:
            pass
        
        return found_urls
    
    async def _pattern_based_discovery(self, site_name: str, categories: List[str]) -> Dict[str, str]:
        """Pattern-based URL generation ve test"""
        site_config = self.site_patterns.get(site_name, {})
        base_url = site_config.get('base_url', '')
        
        if not base_url:
            return {}
        
        found_urls = {}
        
        # Common category ID ranges to test
        if site_name == 'trendyol':
            category_ranges = range(80, 120)  # c80-c120 arası test et
            
            async with aiohttp.ClientSession() as session:
                for category in categories:
                    # Generate possible URLs
                    possible_urls = []
                    
                    # Pattern 1: /kategori-x-cID
                    category_slug = category.lower().replace(' ', '-').replace('ı', 'i')
                    for cat_id in category_ranges:
                        possible_urls.extend([
                            f"{base_url}/{category_slug}-x-c{cat_id}",
                            f"{base_url}/kozmetik/{category_slug}-x-c{cat_id}",
                            f"{base_url}/{category_slug}-c{cat_id}"
                        ])
                    
                    # Test URLs in parallel
                    for url in possible_urls[:20]:  # Test first 20
                        try:
                            async with session.head(url, timeout=5) as response:
                                if response.status == 200:
                                    found_urls[category] = url
                                    logger.info(f"Pattern found {category}: {url}")
                                    break
                        except:
                            continue
                        
                        if category in found_urls:
                            break
        
        return found_urls
    
    def _matches_category(self, text: str, category: str, href: str) -> bool:
        """Text ve href'in kategoriye uyup uymadığını kontrol et"""
        text = text.lower()
        category = category.lower()
        href = href.lower()
        
        # Direct match
        if category in text or category in href:
            return True
        
        # Synonym matching
        synonyms = {
            'cilt bakımı': ['cilt', 'skincare', 'skin', 'bakım'],
            'makyaj': ['makeup', 'makyaj', 'cosmetic'],
            'parfüm': ['parfum', 'perfume', 'fragrance', 'koku'],
            'kozmetik': ['cosmetic', 'beauty', 'güzellik'],
            'saç bakımı': ['sac', 'hair', 'shampoo']
        }
        
        if category in synonyms:
            for synonym in synonyms[category]:
                if synonym in text or synonym in href:
                    return True
        
        return False
    
    def _matches_category_url(self, url: str, category: str) -> bool:
        """URL'in kategoriye uyup uymadığını kontrol et"""
        url_lower = url.lower()
        category_lower = category.lower().replace(' ', '-')
        
        # Direct match
        if category_lower in url_lower:
            return True
        
        # Pattern match
        category_patterns = {
            'cilt bakımı': ['cilt', 'skin'],
            'makyaj': ['makyaj', 'makeup'],
            'parfüm': ['parfum', 'perfume'],
            'kozmetik': ['kozmetik', 'cosmetic']
        }
        
        if category in category_patterns:
            for pattern in category_patterns[category]:
                if pattern in url_lower:
                    return True
        
        return False
    
    def _is_valid_category_url(self, url: str, site_name: str) -> bool:
        """URL'in geçerli kategori URL'i olup olmadığını kontrol et"""
        site_config = self.site_patterns.get(site_name, {})
        patterns = site_config.get('category_patterns', [])
        
        for pattern in patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    async def _validate_category_urls(self, urls: Dict[str, str]) -> Dict[str, str]:
        """URL'lerin gerçekten çalıştığını doğrula"""
        validated = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for category, url in urls.items():
                    try:
                        async with session.head(url, timeout=10) as response:
                            if response.status == 200:
                                validated[category] = url
                            elif response.status in [301, 302]:
                                # Redirect varsa yeni URL'i al
                                validated[category] = str(response.headers.get('Location', url))
                    except:
                        # URL çalışmıyor, skip
                        continue
        except:
            # Validation failed, return original
            return urls
        
        return validated

    async def update_site_config(self, site_name: str, categories: List[str]) -> Dict[str, str]:
        """Site konfigürasyonunu güncel URL'lerle güncelle"""
        logger.info(f"🔄 Updating {site_name} configuration with current URLs...")
        
        # Discover current URLs
        current_urls = await self.discover_category_urls(site_name, categories)
        
        if current_urls:
            # Save to config file
            config_file = f"config/{site_name}_dynamic_urls.json"
            config_data = {
                'site': site_name,
                'updated_at': datetime.now().isoformat(),
                'categories': current_urls,
                'ttl': self.cache_ttl
            }
            
            try:
                import os
                os.makedirs('config', exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ Updated {site_name} config with {len(current_urls)} categories")
            except Exception as e:
                logger.error(f"Config save error: {e}")
        
        return current_urls

# Global mapper instance
url_mapper = DynamicURLMapper()

# Convenience functions
async def get_current_category_urls(site_name: str, categories: List[str]) -> Dict[str, str]:
    """Get current category URLs for a site"""
    return await url_mapper.discover_category_urls(site_name, categories)

async def update_trendyol_urls():
    """Update Trendyol URLs specifically"""
    categories = ['cilt bakımı', 'makyaj', 'parfüm', 'kozmetik', 'güzellik', 'saç bakımı']
    return await url_mapper.update_site_config('trendyol', categories)

async def update_all_sites():
    """Update all sites"""
    sites = {
        'trendyol': ['cilt bakımı', 'makyaj', 'parfüm', 'kozmetik', 'güzellik'],
        'gratis': ['cilt bakımı', 'makyaj', 'parfüm', 'saç bakımı']
    }
    
    results = {}
    for site, categories in sites.items():
        results[site] = await url_mapper.update_site_config(site, categories)
    
    return results