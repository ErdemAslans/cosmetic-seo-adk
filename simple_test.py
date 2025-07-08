#!/usr/bin/env python3
"""
Basit test - Google ADK olmadan çalışan sürüm
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from loguru import logger
from urllib.parse import urljoin

# Site konfigürasyonu
TRENDYOL_CONFIG = {
    "name": "trendyol",
    "base_url": "https://www.trendyol.com",
    "category_path": "/kozmetik-x-c40",
    "product_link_selector": "div.p-card-wrppr a",
    "rate_limit": 3.0
}

class SimpleCosmeticExtractor:
    """Basit kozmetik ürün çıkarıcı"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def discover_urls(self, max_products: int = 5) -> List[str]:
        """Ürün URL'lerini keşfet"""
        logger.info(f"🔍 Trendyol'dan {max_products} ürün URL'si arıyorum...")
        
        try:
            url = TRENDYOL_CONFIG["base_url"] + TRENDYOL_CONFIG["category_path"]
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    logger.error(f"❌ Sayfa yüklenemedi: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Ürün linklerini bul
                links = []
                for link in soup.select(TRENDYOL_CONFIG["product_link_selector"])[:max_products]:
                    href = link.get("href")
                    if href:
                        full_url = urljoin(TRENDYOL_CONFIG["base_url"], href)
                        links.append(full_url)
                
                logger.info(f"✅ {len(links)} ürün URL'si bulundu")
                return links
                
        except Exception as e:
            logger.error(f"❌ URL keşfi hatası: {e}")
            return []
    
    async def extract_product_info(self, url: str) -> Dict[str, Any]:
        """Temel ürün bilgilerini çıkar"""
        logger.info(f"📦 Ürün bilgisi çıkarılıyor: {url}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            async with self.session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    return {"error": f"HTTP {response.status}"}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Temel bilgileri çıkar
                product = {
                    "url": url,
                    "name": self._extract_text(soup, "h1"),
                    "price": self._extract_text(soup, ".prc-dsc, .prc-slg"),
                    "description": self._extract_text(soup, ".product-desc, .detail-desc"),
                    "brand": self._extract_text(soup, ".brand, .product-brand")
                }
                
                # Boş değerleri temizle
                product = {k: v for k, v in product.items() if v}
                
                if product.get("name"):
                    logger.info(f"✅ Ürün çıkarıldı: {product['name'][:50]}...")
                    return product
                else:
                    logger.warning(f"⚠️ Ürün adı bulunamadı: {url}")
                    return {"error": "Ürün adı bulunamadı"}
                
        except Exception as e:
            logger.error(f"❌ Ürün çıkarma hatası {url}: {e}")
            return {"error": str(e)}
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """CSS selector ile metin çıkar"""
        try:
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else ""
        except:
            return ""
    
    def generate_simple_seo(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Basit SEO verileri üret"""
        name = product.get("name", "")
        description = product.get("description", "")
        
        # Basit keyword çıkarma
        keywords = []
        text = (name + " " + description).lower()
        
        # Kozmetik terimleri
        cosmetic_terms = [
            "serum", "krem", "maske", "temizleyici", "tonik", "yağ",
            "cilt", "yüz", "göz", "nemlendirici", "anti-aging", "vitamin"
        ]
        
        for term in cosmetic_terms:
            if term in text:
                keywords.append(term)
        
        # Marka ekle
        if product.get("brand"):
            keywords.insert(0, product["brand"].lower())
        
        # SEO başlık
        title = name[:60] if name else "Kozmetik Ürün"
        
        # Meta açıklama
        meta_desc = description[:160] if description else f"{name} - Kozmetik ürünü"
        
        return {
            "keywords": keywords[:10],
            "primary_keyword": keywords[0] if keywords else "kozmetik",
            "title": title,
            "meta_description": meta_desc,
            "slug": self._create_slug(name)
        }
    
    def _create_slug(self, text: str) -> str:
        """URL slug oluştur"""
        if not text:
            return "urun"
        
        import re
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = slug[:50]
        return slug or "urun"


async def run_simple_test():
    """Basit test çalıştır"""
    logger.info("🚀 Basit Kozmetik SEO Çıkarıcı Testi Başlıyor")
    logger.info("Bu test ADK olmadan çalışan basit bir sürümdür\n")
    
    async with SimpleCosmeticExtractor() as extractor:
        # 1. URL'leri keşfet
        urls = await extractor.discover_urls(3)
        
        if not urls:
            print("❌ Hiç ürün URL'si bulunamadı")
            return
        
        print(f"🔍 {len(urls)} ürün URL'si bulundu")
        
        # 2. Her ürünü işle
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n📦 Ürün {i}/{len(urls)} işleniyor...")
            
            # Ürün bilgilerini çıkar
            product = await extractor.extract_product_info(url)
            
            if "error" in product:
                print(f"❌ Hata: {product['error']}")
                continue
            
            # SEO verileri üret
            seo_data = extractor.generate_simple_seo(product)
            
            result = {
                "product": product,
                "seo": seo_data
            }
            results.append(result)
            
            # Sonucu göster
            print(f"✅ Ürün: {product.get('name', 'Bilinmeyen')[:40]}...")
            print(f"   🏷️ Marka: {product.get('brand', 'Bilinmeyen')}")
            print(f"   💰 Fiyat: {product.get('price', 'Bilinmeyen')}")
            print(f"   🎯 Ana Keyword: {seo_data.get('primary_keyword', 'N/A')}")
            print(f"   📝 Keyword Sayısı: {len(seo_data.get('keywords', []))}")
            
            # Rate limiting
            await asyncio.sleep(3)
        
        # Özet
        print(f"\n" + "="*60)
        print(f"📊 TEST SONUÇLARI")
        print(f"="*60)
        print(f"🔍 Keşfedilen URL: {len(urls)}")
        print(f"✅ İşlenen Ürün: {len(results)}")
        print(f"📈 Başarı Oranı: {len(results)/len(urls)*100:.1f}%")
        
        if results:
            print(f"\n📋 İŞLENEN ÜRÜNLER:")
            for i, result in enumerate(results, 1):
                product = result["product"]
                seo = result["seo"]
                print(f"{i}. {product.get('name', 'Bilinmeyen')[:50]}")
                print(f"   Keywords: {', '.join(seo.get('keywords', [])[:5])}")
        
        print(f"\n✅ Basit test tamamlandı!")
        print(f"📌 Bu test ADK olmadan çalışan temel bir sürümdür.")
        print(f"🚀 Gelişmiş özellikler için ADK tabanlı sistem kullanın.")
        
        return results


if __name__ == "__main__":
    # Logging ayarla
    logger.add("logs/simple_test.log", level="INFO")
    
    try:
        asyncio.run(run_simple_test())
    except KeyboardInterrupt:
        print("\n⏹️ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        logger.error(f"Test hatası: {e}")
        print(f"💥 Test hatası: {e}")