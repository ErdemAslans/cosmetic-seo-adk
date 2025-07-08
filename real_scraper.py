#!/usr/bin/env python3
"""
Real Scraper - Gerçek sitelerden veri çeken sistem
Rossmann.com.tr'den kozmetik ürün bilgilerini çeker
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any


class RossmannScraper:
    """Rossmann.com.tr için özel scraper"""
    
    def __init__(self):
        self.base_url = "https://www.rossmann.com.tr"
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
    
    async def discover_product_urls(self, search_term: str = "serum", max_products: int = 5) -> List[str]:
        """Ürün URL'lerini keşfet"""
        print(f"🔍 Rossmann'dan '{search_term}' arıyorum...")
        
        try:
            # Arama sayfasını ziyaret et
            search_url = f"{self.base_url}/catalogsearch/result/?q={search_term}"
            
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    print(f"❌ Arama sayfası yüklenemedi: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'lxml')
                
                # Ürün linklerini bul
                product_links = []
                
                # Rossmann'ın ürün link yapısını bul
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Ürün sayfası pattern'ini kontrol et
                    if ('/tr/' in href or '/p/' in href) and not any(x in href.lower() for x in [
                        'search', 'category', 'catalog', 'brand', 'login', 'register', 'cart'
                    ]):
                        full_url = urljoin(self.base_url, href)
                        
                        # Ürün sayfası gibi görünüyorsa ekle
                        if self.looks_like_product_url(full_url):
                            product_links.append(full_url)
                
                # Tekrarları kaldır ve sınırla
                unique_links = list(set(product_links))[:max_products]
                
                print(f"✅ {len(unique_links)} ürün URL'si bulundu")
                return unique_links
                
        except Exception as e:
            print(f"❌ URL keşfi hatası: {e}")
            return []
    
    def looks_like_product_url(self, url: str) -> bool:
        """URL'nin ürün sayfası olup olmadığını kontrol et"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Rossmann ürün URL pattern'leri
        product_patterns = [
            '/p/',           # Ürün kodu ile
            '/tr/',          # Türkçe ürün sayfaları
            '-p-',           # Ürün ayırıcısı
            '.html'          # HTML sayfaları
        ]
        
        return any(pattern in path for pattern in product_patterns)
    
    async def scrape_product(self, url: str) -> Dict[str, Any]:
        """Tek ürünün bilgilerini çek"""
        print(f"📦 Ürün bilgisi çekiliyor: {url}")
        
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
                    "images": self.extract_images(soup)
                }
                
                # Temizle ve doğrula
                product = self.clean_product_data(product)
                
                if product.get("name"):
                    print(f"✅ Ürün çıkarıldı: {product['name'][:50]}...")
                    return product
                else:
                    print(f"⚠️ Ürün adı bulunamadı: {url}")
                    return {"error": "Ürün adı bulunamadı", "url": url}
                
        except Exception as e:
            print(f"❌ Ürün çıkarma hatası {url}: {e}")
            return {"error": str(e), "url": url}
    
    def extract_name(self, soup: BeautifulSoup) -> str:
        """Ürün adını çıkar"""
        selectors = [
            "h1.page-title span",
            "h1.page-title",
            "h1",
            ".product-name",
            ".product-title",
            "[data-role='product-title']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ""
    
    def extract_brand(self, soup: BeautifulSoup) -> str:
        """Marka adını çıkar"""
        selectors = [
            ".product-brand",
            "[data-brand]",
            ".brand-name",
            ".manufacturer"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Meta data'dan marka çıkarmaya çalış
        brand_meta = soup.find("meta", property="product:brand")
        if brand_meta:
            return brand_meta.get("content", "")
        
        return ""
    
    def extract_price(self, soup: BeautifulSoup) -> str:
        """Fiyat bilgisini çıkar"""
        selectors = [
            ".price",
            ".regular-price",
            ".special-price",
            "[data-price]",
            ".price-box .price"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                # Fiyat pattern'ini temizle
                price_match = re.search(r'[\d.,]+\s*(?:TL|₺|EUR|USD)', price_text)
                if price_match:
                    return price_match.group()
        
        return ""
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Ürün açıklamasını çıkar"""
        selectors = [
            ".product-description",
            ".product-details",
            ".product-info",
            ".description",
            "[data-role='product-description']",
            ".product-view .std"
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
    
    def extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Ürün resimlerini çıkar"""
        images = []
        
        # Farklı resim selektörleri
        img_selectors = [
            ".product-image img",
            ".gallery-image img",
            ".product-gallery img",
            ".product-media img"
        ]
        
        for selector in img_selectors:
            for img in soup.select(selector):
                src = img.get("src") or img.get("data-src")
                if src and not src.startswith("data:"):
                    full_url = urljoin(self.base_url, src)
                    images.append(full_url)
        
        return list(set(images))[:3]  # En fazla 3 resim
    
    def clean_product_data(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Ürün verisini temizle"""
        # Boş stringleri temizle
        for key, value in product.items():
            if isinstance(value, str):
                product[key] = value.strip()
        
        return product


class SimpleSEOGenerator:
    """Basit SEO generator"""
    
    def __init__(self):
        self.cosmetic_terms = [
            "serum", "krem", "maske", "temizleyici", "tonik", "yağ",
            "cilt", "yüz", "göz", "nemlendirici", "anti-aging", "vitamin",
            "retinol", "hyaluronic", "collagen", "peptide", "niacinamide"
        ]
    
    def generate_seo(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """SEO verileri üret"""
        # Keyword çıkarma
        keywords = self.extract_keywords(product)
        
        # Primary keyword seçimi
        primary_keyword = self.select_primary_keyword(keywords, product)
        
        # SEO metadataları
        title = self.generate_title(product, primary_keyword)
        meta_description = self.generate_meta_description(product)
        slug = self.generate_slug(primary_keyword or product.get("name", ""))
        
        return {
            "keywords": keywords,
            "primary_keyword": primary_keyword,
            "title": title,
            "meta_description": meta_description,
            "slug": slug,
            "focus_keyphrase": primary_keyword
        }
    
    def extract_keywords(self, product: Dict[str, Any]) -> List[str]:
        """Keywordleri çıkar"""
        keywords = []
        
        text = f"{product.get('name', '')} {product.get('description', '')}".lower()
        
        # Marka ekle
        if product.get("brand"):
            keywords.append(product["brand"].lower())
        
        # Kozmetik terimlerini bul
        for term in self.cosmetic_terms:
            if term in text:
                keywords.append(term)
        
        # Ürün adından önemli kelimeleri çıkar
        name_words = product.get("name", "").lower().split()
        for word in name_words:
            if len(word) > 3 and word not in ["için", "with", "and", "the"]:
                keywords.append(word)
        
        return list(set(keywords))[:15]
    
    def select_primary_keyword(self, keywords: List[str], product: Dict[str, Any]) -> str:
        """Primary keyword seç"""
        if not keywords:
            return "kozmetik ürün"
        
        name = product.get("name", "").lower()
        
        # İsimde geçen ilk keyword'ü primary yap
        for keyword in keywords:
            if keyword in name:
                return keyword
        
        return keywords[0]
    
    def generate_title(self, product: Dict[str, Any], primary_keyword: str) -> str:
        """SEO title üret"""
        name = product.get("name", "")
        brand = product.get("brand", "")
        
        if brand and brand.lower() not in name.lower():
            title = f"{brand} {name}"
        else:
            title = name
        
        return title[:60]
    
    def generate_meta_description(self, product: Dict[str, Any]) -> str:
        """Meta description üret"""
        description = product.get("description", "")
        name = product.get("name", "")
        
        if description:
            meta = description[:150]
        else:
            meta = f"{name} - Rossmann'da en uygun fiyatlarla."
        
        return meta + "..." if len(meta) > 157 else meta
    
    def generate_slug(self, text: str) -> str:
        """URL slug üret"""
        if not text:
            return "urun"
        
        # Türkçe karakterleri değiştir
        replacements = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
        }
        
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        
        # Temizle ve slug formatına çevir
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        return slug[:40] or "urun"


async def main():
    """Ana fonksiyon"""
    print("🚀 GERÇEK ROSSMANN SCRAPER")
    print("=" * 60)
    print("Rossmann.com.tr'den gerçek ürün verileri çekiyor\n")
    
    seo_generator = SimpleSEOGenerator()
    results = []
    
    async with RossmannScraper() as scraper:
        # Ürün URL'lerini keşfet
        urls = await scraper.discover_product_urls("serum", 3)
        
        if not urls:
            print("❌ Hiç ürün URL'si bulunamadı")
            return
        
        print(f"🔍 {len(urls)} ürün URL'si bulundu\n")
        
        # Her ürünü işle
        for i, url in enumerate(urls, 1):
            print(f"📦 Ürün {i}/{len(urls)} işleniyor...")
            
            # Ürün verisini çek
            product = await scraper.scrape_product(url)
            
            if "error" in product:
                print(f"❌ Hata: {product['error']}")
                continue
            
            # SEO verisi üret
            seo_data = seo_generator.generate_seo(product)
            
            result = {
                "product": product,
                "seo": seo_data,
                "scraped_at": time.time()
            }
            results.append(result)
            
            # Sonucu göster
            print(f"✅ Ürün: {product.get('name', 'Bilinmeyen')[:40]}...")
            print(f"   🏷️ Marka: {product.get('brand', 'Bilinmeyen')}")
            print(f"   💰 Fiyat: {product.get('price', 'Bilinmeyen')}")
            print(f"   🎯 Primary Keyword: {seo_data.get('primary_keyword', 'N/A')}")
            print(f"   📝 Keywords: {', '.join(seo_data.get('keywords', [])[:5])}")
            print()
    
    # Sonuçları göster
    print("=" * 60)
    print("📊 SCRAPING SONUÇLARI")
    print("=" * 60)
    
    print(f"🔍 Bulunan URL: {len(urls)}")
    print(f"✅ İşlenen Ürün: {len(results)}")
    print(f"📈 Başarı Oranı: {len(results)/len(urls)*100:.1f}%")
    
    if results:
        print(f"\n📋 İŞLENEN ÜRÜNLER:")
        for i, result in enumerate(results, 1):
            product = result["product"]
            seo = result["seo"]
            print(f"{i}. {product.get('name', 'Bilinmeyen')}")
            print(f"   🌐 URL: {product['url']}")
            print(f"   🎯 SEO Title: {seo['title'][:50]}...")
            print(f"   📝 Meta: {seo['meta_description'][:50]}...")
        
        # JSON'a kaydet
        try:
            with open("rossmann_results.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n💾 Sonuçlar rossmann_results.json dosyasına kaydedildi")
        except Exception as e:
            print(f"⚠️ JSON kaydetme hatası: {e}")
        
        # CSV format
        print(f"\n📄 CSV FORMAT:")
        print("name,brand,price,primary_keyword,url")
        for result in results:
            p = result["product"]
            s = result["seo"]
            print(f'"{p.get("name", "")[:30]}","{p.get("brand", "")}","{p.get("price", "")}","{s.get("primary_keyword", "")}","{p["url"]}"')
    
    print(f"\n✨ Gerçek veri çekme tamamlandı!")
    print("🎯 Bu gerçek Rossmann.com.tr verileriydi!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Scraping durduruldu")
    except Exception as e:
        print(f"💥 Hata: {e}")