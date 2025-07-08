#!/usr/bin/env python3
"""
Demo Test - Sahte veri ile sistem testı
Google ADK tabanlı sistemin demo gösterimi
"""

import asyncio
import json
from typing import Dict, Any, List
from loguru import logger


# Demo ürün verileri
DEMO_PRODUCTS = [
    {
        "url": "https://example.com/product/vitamin-c-serum",
        "name": "Vitamin C Brightening Serum - 30ml",
        "brand": "BeautyLab",
        "price": "299.90 TL",
        "description": "Bu güçlü Vitamin C serumu cildinizi aydınlatır ve leke karşıtı etkisi sağlar. %15 L-Ascorbic Acid ve Hyaluronic Acid içeren formülü ile cildinizi nemlendirir ve kırışıklık karşıtı etki gösterir. Tüm cilt tipleri için uygundur. Sabah ve akşam temiz cilde uygulanır.",
        "ingredients": ["L-Ascorbic Acid", "Hyaluronic Acid", "Vitamin E", "Ferulic Acid", "Aqua"],
        "features": ["Aydınlatıcı", "Leke karşıtı", "Nemlendirici", "Anti-aging"],
        "usage": "Sabah ve akşam temiz cilde 2-3 damla uygulayın. Güneş koruyucu kullanımı önerilir."
    },
    {
        "url": "https://example.com/product/retinol-night-cream",
        "name": "Retinol Night Renewal Cream - 50ml",
        "brand": "SkinCare Pro",
        "price": "459.90 TL",
        "description": "Gece boyunca cildinizi yenileyen güçlü retinol kremi. %0.5 Retinol ve Peptide kompleksi içerir. İnce çizgi ve kırışıklıkları azaltır, cilt dokusunu düzeltir. Olgun ciltler için özel olarak geliştirilmiştir. Sadece gece kullanımına uygundur.",
        "ingredients": ["Retinol", "Peptides", "Ceramides", "Shea Butter", "Glycerin"],
        "features": ["Anti-aging", "Yenileyici", "Kırışıklık karşıtı", "Sıkılaştırıcı"],
        "usage": "Sadece gece temiz cilde ince bir tabaka halinde uygulayın. Güneş hassasiyeti yapabilir."
    },
    {
        "url": "https://example.com/product/hyaluronic-acid-mask",
        "name": "Hyaluronic Acid Intensive Hydrating Mask",
        "brand": "Aqua Beauty",
        "price": "179.90 TL",
        "description": "Yoğun nemlendirici etkisi olan hyaluronic acid maske. Kuru ve susuz ciltler için ideal. 15 dakikada derinlemesine nem sağlar. Cilt bariyerini güçlendirir ve esnek görünüm kazandırır. Haftalık 2-3 kez kullanılabilir.",
        "ingredients": ["Hyaluronic Acid", "Aloe Vera", "Cucumber Extract", "Panthenol"],
        "features": ["Yoğun nemlendirici", "Sakinleştirici", "Tamir edici", "Esnek cilt"],
        "usage": "Temiz cilde 15-20 dakika uygulayın, ardından ılık su ile durulayın."
    }
]


class DemoSEOExtractor:
    """Demo SEO çıkarıcı - Gerçek AI modellerini simüle eder"""
    
    def __init__(self):
        self.cosmetic_terms = {
            "ingredients": [
                "vitamin c", "retinol", "hyaluronic acid", "niacinamide", "salicylic acid",
                "glycolic acid", "peptides", "ceramides", "squalane", "bakuchiol"
            ],
            "benefits": [
                "moisturizing", "anti-aging", "brightening", "firming", "soothing",
                "hydrating", "nourishing", "repairing", "protective", "clarifying"
            ],
            "product_types": [
                "serum", "cream", "mask", "cleanser", "toner", "oil", "treatment", "moisturizer"
            ],
            "skin_types": [
                "dry", "oily", "combination", "sensitive", "normal", "mature", "acne-prone"
            ]
        }
    
    async def process_products(self) -> List[Dict[str, Any]]:
        """Tüm demo ürünleri işle"""
        logger.info("🤖 Demo SEO Extractor başlıyor...")
        
        results = []
        
        for i, product in enumerate(DEMO_PRODUCTS, 1):
            logger.info(f"📦 Ürün {i}/{len(DEMO_PRODUCTS)} işleniyor: {product['name']}")
            
            # Agent pipeline simülasyonu
            analyzed_data = await self.analyze_product(product)
            seo_data = await self.generate_seo(product, analyzed_data)
            quality_data = await self.validate_quality(product, seo_data)
            
            result = {
                "product": product,
                "analysis": analyzed_data,
                "seo": seo_data,
                "quality": quality_data
            }
            
            results.append(result)
            
            # Demo için kısa bekleme
            await asyncio.sleep(0.5)
        
        return results
    
    async def analyze_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzer Agent simülasyonu"""
        logger.info(f"🧹 Analyzing: {product['name'][:30]}...")
        
        text = f"{product['name']} {product['description']}".lower()
        
        # Kozmetik terimlerini bul
        found_terms = {
            "ingredients": [term for term in self.cosmetic_terms["ingredients"] if term in text],
            "benefits": [term for term in self.cosmetic_terms["benefits"] if term in text],
            "product_types": [term for term in self.cosmetic_terms["product_types"] if term in text],
            "skin_types": [term for term in self.cosmetic_terms["skin_types"] if term in text]
        }
        
        # Dil tespiti (basit)
        language = "tr" if any(tr_word in text for tr_word in ["cilt", "yüz", "krem", "maske"]) else "en"
        
        return {
            "extracted_terms": found_terms,
            "language": language,
            "content_length": len(product["description"]),
            "has_ingredients": bool(product.get("ingredients")),
            "has_features": bool(product.get("features"))
        }
    
    async def generate_seo(self, product: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """SEO Agent simülasyonu"""
        logger.info(f"🎯 Generating SEO: {product['name'][:30]}...")
        
        # Keyword üretimi
        keywords = []
        
        # Marka ve ürün adından
        if product.get("brand"):
            keywords.append(product["brand"].lower())
        
        # Bulunan terimlerden
        for category, terms in analysis["extracted_terms"].items():
            keywords.extend(terms)
        
        # Ürün tipinden
        text = product["name"].lower()
        for ptype in ["serum", "cream", "mask", "cleanser"]:
            if ptype in text:
                keywords.append(ptype)
        
        # Primary keyword seçimi
        primary_keyword = keywords[0] if keywords else "cosmetic product"
        
        # SEO title üretimi
        brand = product.get("brand", "")
        name = product["name"]
        title = f"{brand} {name}" if brand else name
        title = title[:60]  # Karakter sınırı
        
        # Meta description
        description = product["description"]
        meta_desc = description[:157] + "..." if len(description) > 160 else description
        
        # URL slug
        slug = self.create_slug(primary_keyword)
        
        return {
            "keywords": list(set(keywords))[:15],  # Unique keywords
            "primary_keyword": primary_keyword,
            "secondary_keywords": keywords[1:6] if len(keywords) > 1 else [],
            "long_tail_keywords": [
                f"best {primary_keyword}",
                f"{primary_keyword} for sensitive skin",
                f"organic {primary_keyword}"
            ],
            "title": title,
            "meta_description": meta_desc,
            "slug": slug,
            "focus_keyphrase": primary_keyword,
            "keyword_density": {primary_keyword: 3.2}
        }
    
    async def validate_quality(self, product: Dict[str, Any], seo: Dict[str, Any]) -> Dict[str, Any]:
        """Quality Agent simülasyonu"""
        logger.info(f"✅ Validating: {product['name'][:30]}...")
        
        errors = []
        warnings = []
        
        # Keyword sayısı kontrolü
        if len(seo["keywords"]) < 5:
            errors.append("Too few keywords")
        
        # Title uzunluk kontrolü
        if len(seo["title"]) > 60:
            errors.append("Title too long")
        
        # Meta description kontrolü
        if len(seo["meta_description"]) > 160:
            errors.append("Meta description too long")
        elif len(seo["meta_description"]) < 50:
            warnings.append("Meta description too short")
        
        # Primary keyword title'da var mı?
        if seo["primary_keyword"] not in seo["title"].lower():
            warnings.append("Primary keyword not in title")
        
        # Kalite skoru hesaplama
        quality_score = 100
        quality_score -= len(errors) * 20  # Her hata için -20
        quality_score -= len(warnings) * 5  # Her uyarı için -5
        quality_score = max(0, quality_score)
        
        is_valid = len(errors) == 0 and quality_score >= 70
        
        return {
            "is_valid": is_valid,
            "quality_score": quality_score,
            "errors": errors,
            "warnings": warnings,
            "recommendations": self.generate_recommendations(errors, warnings)
        }
    
    def generate_recommendations(self, errors: List[str], warnings: List[str]) -> List[str]:
        """Öneri üretimi"""
        recommendations = []
        
        if errors:
            recommendations.append("Fix critical errors before publishing")
        
        if warnings:
            recommendations.append("Address warnings to improve SEO quality")
        
        if not errors and not warnings:
            recommendations.append("SEO quality is excellent!")
        
        return recommendations
    
    def create_slug(self, text: str) -> str:
        """URL slug oluştur"""
        import re
        slug = text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug[:40]


async def main():
    """Demo ana fonksiyon"""
    print("🎭 COSMETIC SEO EXTRACTOR - DEMO MODE")
    print("=" * 60)
    print("Bu demo, Google ADK tabanlı sistemin nasıl çalışacağını gösterir.")
    print("Gerçek web scraping yerine örnek veriler kullanılır.\n")
    
    extractor = DemoSEOExtractor()
    
    try:
        # Ürünleri işle
        results = await extractor.process_products()
        
        # Sonuçları göster
        print("\n" + "=" * 60)
        print("📊 DEMO RESULTS")
        print("=" * 60)
        
        total_products = len(results)
        valid_products = sum(1 for r in results if r["quality"]["is_valid"])
        avg_quality = sum(r["quality"]["quality_score"] for r in results) / total_products
        
        print(f"📦 Total Products: {total_products}")
        print(f"✅ Valid Products: {valid_products}")
        print(f"📈 Success Rate: {valid_products/total_products*100:.1f}%")
        print(f"⭐ Avg Quality Score: {avg_quality:.1f}")
        
        print(f"\n📋 PROCESSED PRODUCTS:")
        for i, result in enumerate(results, 1):
            product = result["product"]
            seo = result["seo"]
            quality = result["quality"]
            
            print(f"\n{i}. {product['name']}")
            print(f"   🏷️ Brand: {product['brand']}")
            print(f"   💰 Price: {product['price']}")
            print(f"   🎯 Primary Keyword: {seo['primary_keyword']}")
            print(f"   📝 Keywords: {len(seo['keywords'])}")
            print(f"   ⭐ Quality Score: {quality['quality_score']}")
            print(f"   ✅ Valid: {'Yes' if quality['is_valid'] else 'No'}")
            
            if quality["errors"]:
                print(f"   ❌ Errors: {', '.join(quality['errors'])}")
            if quality["warnings"]:
                print(f"   ⚠️ Warnings: {', '.join(quality['warnings'])}")
        
        # JSON dosyasına kaydet
        output_file = "demo_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Bu demo gerçek sistemi simüle eder")
        print("2. Gerçek Google ADK sistemi için: pip install google-adk")
        print("3. Gemini API key'i ile çalışan agent'ları aktifleştirin")
        print("4. Gerçek web sitelerinden veri çekimi için Selenium ekleyin")
        
        print(f"\n✨ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    # Logging ayarla
    logger.add("logs/demo_test.log", level="INFO")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted")
    except Exception as e:
        print(f"💥 Demo error: {e}")