#!/usr/bin/env python3
"""
Real Cosmetic SEO Extractor - Tam sistem (Google ADK olmadan ama gerçek veri ile)
"""

import asyncio
import os
import json
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger

# Gerçek scraper'ları import et
from real_scraper import RossmannScraper, SimpleSEOGenerator

# Load environment variables
load_dotenv()

class RealCosmeticSEOSystem:
    """Gerçek veri ile çalışan tam kozmetik SEO sistemi"""
    
    def __init__(self):
        self.max_products = int(os.getenv("MAX_PRODUCTS", 50))
        self.rate_limit = float(os.getenv("RATE_LIMIT_SECONDS", 3))
        self.output_dir = "data/real_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info("Real Cosmetic SEO System initialized")
    
    async def process_rossmann(self, search_terms: List[str], max_per_term: int = 10) -> Dict[str, Any]:
        """Rossmann'dan gerçek veri çek"""
        logger.info(f"Processing Rossmann with {len(search_terms)} search terms")
        
        all_results = []
        seo_generator = SimpleSEOGenerator()
        
        async with RossmannScraper() as scraper:
            for term in search_terms:
                logger.info(f"Searching for: {term}")
                
                # URL'leri keşfet
                urls = await scraper.discover_product_urls(term, max_per_term)
                logger.info(f"Found {len(urls)} URLs for '{term}'")
                
                # Her URL'den veri çek
                for i, url in enumerate(urls, 1):
                    logger.info(f"Processing {i}/{len(urls)}: {url}")
                    
                    try:
                        # Ürün verisini çek
                        product = await scraper.scrape_product(url)
                        
                        if "error" in product:
                            logger.warning(f"Scraping error: {product['error']}")
                            continue
                        
                        # SEO verisi üret
                        seo_data = seo_generator.generate_seo(product)
                        
                        # Kalite skoru hesapla
                        quality_score = self._calculate_quality_score(product, seo_data)
                        
                        result = {
                            "search_term": term,
                            "product": product,
                            "seo": seo_data,
                            "quality_score": quality_score,
                            "is_valid": quality_score >= 70,
                            "scraped_at": time.time()
                        }
                        
                        all_results.append(result)
                        logger.info(f"✅ Processed: {product.get('name', 'Unknown')[:40]}... (Score: {quality_score})")
                        
                        # Rate limiting
                        await asyncio.sleep(self.rate_limit)
                        
                    except Exception as e:
                        logger.error(f"Error processing {url}: {e}")
                        continue
        
        return {
            "source": "rossmann",
            "total_products": len(all_results),
            "valid_products": sum(1 for r in all_results if r["is_valid"]),
            "results": all_results
        }
    
    def _calculate_quality_score(self, product: Dict[str, Any], seo_data: Dict[str, Any]) -> int:
        """Kalite skoru hesapla"""
        score = 100
        
        # Ürün verisi kontrolü
        if not product.get("name"):
            score -= 30
        if not product.get("price"):
            score -= 10
        if not product.get("description") or len(product.get("description", "")) < 50:
            score -= 20
        if not product.get("brand"):
            score -= 10
        
        # SEO verisi kontrolü
        keywords = seo_data.get("keywords", [])
        if len(keywords) < 3:
            score -= 15
        if len(seo_data.get("title", "")) > 60:
            score -= 5
        if len(seo_data.get("meta_description", "")) > 160:
            score -= 5
        
        return max(0, score)
    
    async def process_multiple_sites(self) -> Dict[str, Any]:
        """Birden fazla siteyi işle"""
        logger.info("Starting multi-site processing")
        
        # Rossmann için arama terimleri
        rossmann_terms = ["serum", "vitamin c", "retinol", "hyaluronic", "niacinamide"]
        
        results = {}
        
        # Rossmann'ı işle
        rossmann_result = await self.process_rossmann(rossmann_terms, 5)
        results["rossmann"] = rossmann_result
        
        # Gelecekte diğer siteler eklenebilir
        # results["gratis"] = await self.process_gratis(...)
        # results["watsons"] = await self.process_watsons(...)
        
        return results
    
    async def save_results(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Sonuçları kaydet"""
        timestamp = int(time.time())
        files_created = {}
        
        try:
            # JSON formatında kaydet
            json_file = f"{self.output_dir}/cosmetic_seo_results_{timestamp}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            files_created["json"] = json_file
            
            # CSV formatında kaydet
            csv_file = f"{self.output_dir}/cosmetic_seo_results_{timestamp}.csv"
            await self._save_csv(results, csv_file)
            files_created["csv"] = csv_file
            
            # Özet rapor
            summary_file = f"{self.output_dir}/summary_report_{timestamp}.txt"
            await self._save_summary(results, summary_file)
            files_created["summary"] = summary_file
            
            logger.info(f"Results saved to {len(files_created)} files")
            return files_created
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return {}
    
    async def _save_csv(self, results: Dict[str, Any], filename: str):
        """CSV formatında kaydet"""
        import csv
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "source", "search_term", "product_name", "brand", "price", 
                "primary_keyword", "keywords_count", "quality_score", "is_valid", "url"
            ])
            
            # Data
            for source, data in results.items():
                for result in data.get("results", []):
                    product = result["product"]
                    seo = result["seo"]
                    
                    writer.writerow([
                        source,
                        result.get("search_term", ""),
                        product.get("name", ""),
                        product.get("brand", ""),
                        product.get("price", ""),
                        seo.get("primary_keyword", ""),
                        len(seo.get("keywords", [])),
                        result.get("quality_score", 0),
                        result.get("is_valid", False),
                        product.get("url", "")
                    ])
    
    async def _save_summary(self, results: Dict[str, Any], filename: str):
        """Özet rapor kaydet"""
        total_products = 0
        valid_products = 0
        avg_quality = 0
        
        summary_lines = [
            "🎭 COSMETIC SEO EXTRACTION SUMMARY",
            "=" * 50,
            f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        for source, data in results.items():
            source_total = data.get("total_products", 0)
            source_valid = data.get("valid_products", 0)
            
            total_products += source_total
            valid_products += source_valid
            
            if source_total > 0:
                source_avg = sum(r.get("quality_score", 0) for r in data.get("results", [])) / source_total
            else:
                source_avg = 0
            
            summary_lines.extend([
                f"📊 {source.upper()} RESULTS:",
                f"   Total Products: {source_total}",
                f"   Valid Products: {source_valid}",
                f"   Success Rate: {source_valid/source_total*100:.1f}%" if source_total > 0 else "   Success Rate: 0%",
                f"   Avg Quality: {source_avg:.1f}",
                ""
            ])
        
        if total_products > 0:
            avg_quality = sum(
                r.get("quality_score", 0) 
                for data in results.values() 
                for r in data.get("results", [])
            ) / total_products
        
        summary_lines.extend([
            "🎯 OVERALL SUMMARY:",
            f"   Total Products Processed: {total_products}",
            f"   Valid Products: {valid_products}",
            f"   Overall Success Rate: {valid_products/total_products*100:.1f}%" if total_products > 0 else "   Overall Success Rate: 0%",
            f"   Average Quality Score: {avg_quality:.1f}",
            "",
            "✅ EXTRACTION COMPLETED SUCCESSFULLY!"
        ])
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines))

async def main():
    """Ana fonksiyon"""
    logger.info("🚀 Starting Real Cosmetic SEO Extraction System")
    
    system = RealCosmeticSEOSystem()
    
    try:
        # Tam sistemi çalıştır
        logger.info("Processing multiple sites...")
        results = await system.process_multiple_sites()
        
        # Sonuçları kaydet
        logger.info("Saving results...")
        files = await system.save_results(results)
        
        # Özet yazdır
        total_products = sum(data.get("total_products", 0) for data in results.values())
        valid_products = sum(data.get("valid_products", 0) for data in results.values())
        
        logger.info("=" * 60)
        logger.info("🎯 EXTRACTION COMPLETED")
        logger.info("=" * 60)
        logger.info(f"📦 Total Products: {total_products}")
        logger.info(f"✅ Valid Products: {valid_products}")
        logger.info(f"📈 Success Rate: {valid_products/total_products*100:.1f}%" if total_products > 0 else "📈 Success Rate: 0%")
        logger.info(f"💾 Files created: {list(files.values())}")
        logger.info("✨ Real cosmetic SEO extraction completed successfully!")
        
    except Exception as e:
        logger.error(f"System error: {e}")
        raise

if __name__ == "__main__":
    # Configure logging
    logger.add(
        "logs/real_cosmetic_seo.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Extraction interrupted by user")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")