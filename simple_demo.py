#!/usr/bin/env python3
"""
Simple Demo - Bağımlılık olmadan çalışan demo
"""

import json
import time

# Demo ürün verileri
DEMO_PRODUCTS = [
    {
        "url": "https://example.com/product/vitamin-c-serum",
        "name": "Vitamin C Brightening Serum - 30ml",
        "brand": "BeautyLab",
        "price": "299.90 TL",
        "description": "Bu güçlü Vitamin C serumu cildinizi aydınlatır ve leke karşıtı etkisi sağlar. %15 L-Ascorbic Acid ve Hyaluronic Acid içeren formülü ile cildinizi nemlendirir ve kırışıklık karşıtı etki gösterir. Tüm cilt tipleri için uygundur.",
        "ingredients": ["L-Ascorbic Acid", "Hyaluronic Acid", "Vitamin E", "Ferulic Acid"],
        "features": ["Aydınlatıcı", "Leke karşıtı", "Nemlendirici", "Anti-aging"]
    },
    {
        "url": "https://example.com/product/retinol-night-cream",
        "name": "Retinol Night Renewal Cream - 50ml",
        "brand": "SkinCare Pro",
        "price": "459.90 TL",
        "description": "Gece boyunca cildinizi yenileyen güçlü retinol kremi. %0.5 Retinol ve Peptide kompleksi içerir. İnce çizgi ve kırışıklıkları azaltır, cilt dokusunu düzeltir. Olgun ciltler için özel olarak geliştirilmiştir.",
        "ingredients": ["Retinol", "Peptides", "Ceramides", "Shea Butter"],
        "features": ["Anti-aging", "Yenileyici", "Kırışıklık karşıtı", "Sıkılaştırıcı"]
    },
    {
        "url": "https://example.com/product/hyaluronic-acid-mask",
        "name": "Hyaluronic Acid Intensive Hydrating Mask",
        "brand": "Aqua Beauty",
        "price": "179.90 TL",
        "description": "Yoğun nemlendirici etkisi olan hyaluronic acid maske. Kuru ve susuz ciltler için ideal. 15 dakikada derinlemesine nem sağlar. Cilt bariyerini güçlendirir ve esnek görünüm kazandırır.",
        "ingredients": ["Hyaluronic Acid", "Aloe Vera", "Cucumber Extract"],
        "features": ["Yoğun nemlendirici", "Sakinleştirici", "Tamir edici"]
    }
]

class SimpleSEOGenerator:
    def __init__(self):
        self.cosmetic_keywords = [
            "serum", "cream", "mask", "vitamin c", "retinol", "hyaluronic acid",
            "anti-aging", "moisturizing", "brightening", "hydrating", "nourishing"
        ]
    
    def extract_keywords(self, product):
        """Basit keyword çıkarma"""
        text = f"{product['name']} {product['description']}".lower()
        
        keywords = []
        
        # Marka ekle
        if product.get("brand"):
            keywords.append(product["brand"].lower())
        
        # Kozmetik terimlerini bul
        for keyword in self.cosmetic_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        # İçeriklerden ekle
        for ingredient in product.get("ingredients", []):
            keywords.append(ingredient.lower())
        
        # Tekrarları kaldır
        return list(set(keywords))[:15]
    
    def generate_seo(self, product):
        """SEO verileri üret"""
        keywords = self.extract_keywords(product)
        primary_keyword = keywords[0] if keywords else "cosmetic"
        
        # SEO title
        title = f"{product['brand']} - {product['name']}" if product.get('brand') else product['name']
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Meta description
        desc = product['description']
        if len(desc) > 160:
            desc = desc[:157] + "..."
        
        # URL slug
        slug = primary_keyword.replace(" ", "-").replace(".", "")[:40]
        
        return {
            "keywords": keywords,
            "primary_keyword": primary_keyword,
            "title": title,
            "meta_description": desc,
            "slug": slug
        }
    
    def validate_quality(self, seo):
        """Kalite kontrolü"""
        errors = []
        warnings = []
        
        if len(seo["keywords"]) < 3:
            errors.append("Too few keywords")
        
        if len(seo["title"]) > 60:
            errors.append("Title too long")
        
        if len(seo["meta_description"]) > 160:
            errors.append("Meta description too long")
        elif len(seo["meta_description"]) < 50:
            warnings.append("Meta description too short")
        
        # Kalite skoru
        quality_score = 100 - (len(errors) * 20) - (len(warnings) * 5)
        quality_score = max(0, quality_score)
        
        return {
            "is_valid": len(errors) == 0,
            "quality_score": quality_score,
            "errors": errors,
            "warnings": warnings
        }

def main():
    print("🎭 COSMETIC SEO EXTRACTOR - SIMPLE DEMO")
    print("=" * 60)
    print("Google ADK tabanlı sistemin basit demonstrasyonu")
    print("Gerçek AI modelleri yerine basit algoritmalar kullanır\n")
    
    generator = SimpleSEOGenerator()
    results = []
    
    for i, product in enumerate(DEMO_PRODUCTS, 1):
        print(f"📦 Processing Product {i}/{len(DEMO_PRODUCTS)}: {product['name']}")
        
        # SEO verisi üret
        seo_data = generator.generate_seo(product)
        
        # Kalite kontrolü
        quality_data = generator.validate_quality(seo_data)
        
        result = {
            "product": product,
            "seo": seo_data,
            "quality": quality_data
        }
        results.append(result)
        
        # Sonucu göster
        print(f"   🎯 Primary Keyword: {seo_data['primary_keyword']}")
        print(f"   📝 Keywords Count: {len(seo_data['keywords'])}")
        print(f"   ⭐ Quality Score: {quality_data['quality_score']}")
        print(f"   ✅ Valid: {'Yes' if quality_data['is_valid'] else 'No'}")
        
        if quality_data["errors"]:
            print(f"   ❌ Errors: {', '.join(quality_data['errors'])}")
        if quality_data["warnings"]:
            print(f"   ⚠️ Warnings: {', '.join(quality_data['warnings'])}")
        print()
        
        time.sleep(0.5)  # Simülasyon için bekle
    
    # Özet
    print("=" * 60)
    print("📊 SUMMARY RESULTS")
    print("=" * 60)
    
    total = len(results)
    valid = sum(1 for r in results if r["quality"]["is_valid"])
    avg_quality = sum(r["quality"]["quality_score"] for r in results) / total
    
    print(f"📦 Total Products Processed: {total}")
    print(f"✅ Valid Products: {valid}")
    print(f"📈 Success Rate: {valid/total*100:.1f}%")
    print(f"⭐ Average Quality Score: {avg_quality:.1f}")
    
    # En iyi sonuçları göster
    print(f"\n🏆 TOP RESULTS:")
    sorted_results = sorted(results, key=lambda x: x["quality"]["quality_score"], reverse=True)
    
    for i, result in enumerate(sorted_results, 1):
        product = result["product"]
        seo = result["seo"]
        quality = result["quality"]
        
        print(f"{i}. {product['name'][:40]}...")
        print(f"   🏷️ Brand: {product['brand']}")
        print(f"   🎯 Keywords: {', '.join(seo['keywords'][:5])}")
        print(f"   ⭐ Score: {quality['quality_score']}")
        print()
    
    # CSV benzeri çıktı
    print("📄 CSV-STYLE OUTPUT:")
    print("url,name,brand,primary_keyword,keywords_count,quality_score,is_valid")
    for result in results:
        p = result["product"]
        s = result["seo"]
        q = result["quality"]
        print(f"{p['url']},{p['name']},{p['brand']},{s['primary_keyword']},{len(s['keywords'])},{q['quality_score']},{q['is_valid']}")
    
    # JSON dosyasına kaydet
    try:
        with open("demo_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: demo_results.json")
    except Exception as e:
        print(f"⚠️ Could not save JSON: {e}")
    
    print(f"\n🎯 WHAT THIS DEMONSTRATES:")
    print("✅ Multi-agent pipeline simulation")
    print("✅ Cosmetic-specific keyword extraction")
    print("✅ SEO metadata generation")
    print("✅ Quality validation and scoring")
    print("✅ Multiple output formats")
    
    print(f"\n🚀 REAL SYSTEM FEATURES:")
    print("• Google ADK multi-agent orchestration")
    print("• Gemini AI for intelligent processing")
    print("• Real web scraping with Selenium")
    print("• PostgreSQL database storage")
    print("• Advanced NLP with spaCy/NLTK")
    print("• 700+ product processing capability")
    
    print(f"\n✨ Simple demo completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted")
    except Exception as e:
        print(f"💥 Demo error: {e}")