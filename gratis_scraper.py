#!/usr/bin/env python3
"""
Gratis Scraper - Gratis.com için özel scraper
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any
from loguru import logger


class GratisScraper:
    """Gratis.com için özel scraper"""
    
    def __init__(self):
        self.base_url = "https://www.gratis.com"
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def discover_product_urls(self, search_term: str = "yüz kremi", max_products: int = 5) -> List[str]:
        """Ürün URL'lerini keşfet"""
        logger.info(f"Gratis'ta '{search_term}' arıyorum...")
        
        try:
            # Gratis arama URL'si - birden fazla format dene
            search_term_encoded = search_term.replace(' ', '%20')
            search_urls = [
                f"{self.base_url}/search?q={search_term_encoded}",
                f"{self.base_url}/arama?q={search_term.replace(' ', '+')}", 
                f"{self.base_url}/ara?term={search_term_encoded}",
                f"{self.base_url}/kozmetik",  # Fallback: kozmetik kategorisi
            ]
            
            html = None
            for search_url in search_urls:
                try:
                    logger.info(f"Deneniyor: {search_url}")
                    async with self.session.get(search_url) as response:
                        if response.status == 200:
                            html = await response.text()
                            logger.info(f"✅ Başarılı: {search_url}")
                            break
                        else:
                            logger.warning(f"❌ Başarısız: {search_url} - Status: {response.status}")
                except Exception as e:
                    logger.warning(f"❌ Hata: {search_url} - {e}")
                    continue
            
            if not html:
                logger.error("❌ Hiçbir arama URL'si çalışmadı")
                return []
                
            soup = BeautifulSoup(html, 'lxml')
                
                # Ürün linklerini bul
                product_links = []
                
                # Gratis ürün link pattern'leri
                selectors = [
                    'a[href*="/urun/"]',
                    'a[href*="/product/"]',
                    'a.product-item-link',
                    'a.product-link',
                    '.product-item a',
                    '.product-card a'
                ]
                
                for selector in selectors:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href and self.looks_like_product_url(href):
                            full_url = urljoin(self.base_url, href)
                            if full_url not in product_links:
                                product_links.append(full_url)
                
                # Tekrarları kaldır ve sınırla
                unique_links = list(set(product_links))[:max_products]
                
                logger.info(f"✅ {len(unique_links)} ürün URL'si bulundu")
                return unique_links
                
        except Exception as e:
            logger.error(f"❌ URL keşfi hatası: {e}")
            return []
    
    def looks_like_product_url(self, url: str) -> bool:
        """URL'nin ürün sayfası olup olmadığını kontrol et"""
        url_lower = url.lower()
        
        # Gratis ürün URL pattern'leri
        product_patterns = [
            '/urun/',
            '/product/',
            '-p-',
            '/item/',
            '/detail/'
        ]
        
        # Hariç tutulacak pattern'ler
        exclude_patterns = [
            '/kategori/', '/category/', '/search/', '/arama/',
            '/brand/', '/marka/', '/blog/', '/haber/',
            '/kampanya/', '/indirim/', '/sepet/', '/cart/'
        ]
        
        # Ürün pattern'i var mı?
        has_product_pattern = any(pattern in url_lower for pattern in product_patterns)
        
        # Hariç tutulacak pattern var mı?
        has_exclude_pattern = any(pattern in url_lower for pattern in exclude_patterns)
        
        return has_product_pattern and not has_exclude_pattern
    
    async def scrape_product(self, url: str) -> Dict[str, Any]:
        """Tek ürünün bilgilerini çek"""
        logger.info(f"📦 Gratis ürün bilgisi çekiliyor: {url}")
        
        try:
            await asyncio.sleep(2)  # Rate limiting
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return {"error": f"HTTP {response.status}", "url": url}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Ürün bilgilerini çıkar
                product = {
                    "url": url,
                    "name": self.extract_name(soup),
                    "brand": self.extract_brand(soup),
                    "price": self.extract_price(soup),
                    "description": self.extract_description(soup),
                    "images": self.extract_images(soup),
                    "category": self.extract_category(soup),
                    "features": self.extract_features(soup)
                }
                
                # Temizle ve doğrula
                product = self.clean_product_data(product)
                
                if product.get("name"):
                    logger.info(f"✅ Gratis ürün çıkarıldı: {product['name'][:50]}...")
                    return product
                else:
                    logger.warning(f"⚠️ Ürün adı bulunamadı: {url}")
                    return {"error": "Ürün adı bulunamadı", "url": url}
                
        except Exception as e:
            logger.error(f"❌ Ürün çıkarma hatası {url}: {e}")
            return {"error": str(e), "url": url}
    
    def extract_name(self, soup: BeautifulSoup) -> str:
        """Ürün adını çıkar"""
        selectors = [
            "h1.product-name",
            "h1.product-title",
            "h1[data-product-name]",
            ".product-detail-name h1",
            ".product-header h1",
            "h1",
            ".product-name",
            ".product-title"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                if len(name) > 5:  # Anlamlı uzunlukta ise
                    return name
        
        return ""
    
    def extract_brand(self, soup: BeautifulSoup) -> str:
        """Marka adını çıkar"""
        selectors = [
            ".product-brand",
            ".brand-name",
            "[data-brand]",
            ".manufacturer",
            ".product-brand-name",
            "span.brand"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                brand = element.get_text(strip=True)
                if len(brand) > 1:
                    return brand
        
        # Meta data'dan marka çıkarmaya çalış
        brand_meta = soup.find("meta", property="product:brand")
        if brand_meta:
            return brand_meta.get("content", "")
        
        # Ürün adından marka çıkarmaya çalış
        name = soup.select_one("h1")
        if name:
            name_text = name.get_text(strip=True)
            # İlk kelime genellikle marka
            words = name_text.split()
            if words:
                return words[0]
        
        return ""
    
    def extract_price(self, soup: BeautifulSoup) -> str:
        """Fiyat bilgisini çıkar"""
        selectors = [
            ".price-current",
            ".product-price",
            ".price-new",
            ".sale-price",
            ".current-price",
            "[data-price]",
            ".price",
            ".price-box .price"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Fiyat pattern'ini temizle
                price_match = re.search(r'[\d.,]+\s*(?:TL|₺|EUR|USD|Lira)', price_text)
                if price_match:
                    return price_match.group()
        
        return ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Ürün açıklamasını çıkar"""
        selectors = [
            ".product-description",
            ".product-details", 
            ".product-content",
            ".description",
            ".product-info",
            "[data-role='product-description']",
            ".product-detail-description",
            "#product-description",
            ".product-summary"
        ]
        
        description_parts = []
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if len(text) > 20:  # Anlamlı uzunlukta ise
                    description_parts.append(text)
        
        # En uzun açıklamayı al
        if description_parts:
            return max(description_parts, key=len)
        
        return ""
    
    def extract_category(self, soup: BeautifulSoup) -> str:
        """Kategori bilgisini çıkar"""
        selectors = [
            ".breadcrumb a:last-child",
            ".category-name",
            "[data-category]",
            ".product-category"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                category = element.get_text(strip=True)
                if len(category) > 2:
                    return category
        
        return ""
    
    def extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Ürün özelliklerini çıkar"""
        features = []
        
        # Özellik listelerini bul
        feature_selectors = [
            ".product-features li",
            ".features-list li",
            ".product-specs li",
            ".specifications li"
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for elem in elements:
                feature = elem.get_text(strip=True)
                if len(feature) > 3 and feature not in features:
                    features.append(feature)
        
        return features[:10]  # En fazla 10 özellik
    
    def extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Ürün resimlerini çıkar"""
        images = []
        
        # Farklı resim selektörleri
        img_selectors = [
            ".product-image img",
            ".product-gallery img",
            ".product-photos img",
            ".product-slider img",
            ".main-image img"
        ]
        
        for selector in img_selectors:
            for img in soup.select(selector):
                src = img.get("src") or img.get("data-src") or img.get("data-lazy")
                if src and not src.startswith("data:"):
                    full_url = urljoin(self.base_url, src)
                    if full_url not in images:
                        images.append(full_url)
        
        return images[:3]  # En fazla 3 resim
    
    def clean_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Ürün verisini temizle"""
        # Boş stringleri temizle
        for key, value in product.items():
            if isinstance(value, str):
                product[key] = value.strip()
            elif isinstance(value, list):
                product[key] = [v.strip() if isinstance(v, str) else v for v in value]
        
        return product


# Test için ana fonksiyon
async def test_gratis_scraper():
    """Gratis scraper test"""
    print("🧪 Gratis Scraper Test")
    print("=" * 50)
    
    async with GratisScraper() as scraper:
        # URL keşfi
        urls = await scraper.discover_product_urls("yüz kremi", 3)
        print(f"Bulunan URL'ler: {len(urls)}")
        
        # İlk URL'yi test et
        if urls:
            product = await scraper.scrape_product(urls[0])
            print(f"Test ürün: {json.dumps(product, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(test_gratis_scraper())