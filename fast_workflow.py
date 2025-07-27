#!/usr/bin/env python3
"""
Fast Workflow - Complete cosmetic SEO extraction in under 10 seconds
"""

import asyncio
import time
from typing import Dict, Any, List
from loguru import logger
import json
from datetime import datetime

from agents.modern_scraper_agent import ModernScraperAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.seo_agent import SEOAgent
from agents.quality_agent import QualityAgent
from agents.storage_agent import StorageAgent

class FastWorkflow:
    """Optimized workflow for sub-10 second processing"""
    
    def __init__(self, database_url: str = None):
        self.scraper = ModernScraperAgent()
        self.analyzer = AnalyzerAgent()
        self.seo_agent = SEOAgent()
        self.quality_agent = QualityAgent()
        
        # Initialize storage agent with database URL if provided
        if database_url:
            self.storage_agent = StorageAgent(database_url)
        else:
            # Use environment variable or default to file-only storage
            import os
            db_url = os.getenv('DATABASE_URL')
            if db_url:
                self.storage_agent = StorageAgent(db_url)
            else:
                logger.warning("No database URL provided, using file-only storage")
                self.storage_agent = None
        
        self.metrics = {}
    
    async def process(self, site_name: str, category: str, limit: int = 10, progress_callback=None) -> Dict[str, Any]:
        """Main processing pipeline with extreme optimization"""
        start_time = time.time()
        logger.info(f"🚀 FAST WORKFLOW: Starting {site_name} - {category} (limit: {limit})")
        
        try:
            # Step 1: Fast discovery and scraping (target: 3-4 seconds)
            if progress_callback:
                await progress_callback(15, "🔍 URL discovery başlatılıyor...", "scout")
            
            scrape_start = time.time()
            scrape_result = await self.scraper.discover_and_scrape(site_name, category, limit)
            self.metrics['scraping_time'] = time.time() - scrape_start
            
            if progress_callback:
                await progress_callback(35, f"✅ {scrape_result.get('urls_found', 0)} URL bulundu, ürün verisi çıkarılıyor...", "scraper")
            
            if not scrape_result.get('success'):
                return {
                    'success': False,
                    'error': scrape_result.get('error', 'Scraping failed'),
                    'metrics': self.metrics
                }
            
            products = scrape_result.get('products', [])
            logger.info(f"✅ Scraped {len(products)} products in {self.metrics['scraping_time']:.2f}s")
            
            # Step 2: Parallel analysis and SEO generation (target: 3-4 seconds)
            if progress_callback:
                await progress_callback(55, "🧠 Ürün analizi ve SEO generation başlatılıyor...", "analyzer")
            
            analysis_start = time.time()
            enriched_products = await self._parallel_enrichment(products)
            self.metrics['analysis_time'] = time.time() - analysis_start
            logger.info(f"✅ Analysis completed in {self.metrics['analysis_time']:.2f}s")
            
            if progress_callback:
                await progress_callback(85, "💾 Veritabanına kaydediliyor...", "storage")
            
            # Step 3: Quick storage (target: < 1 second)
            storage_start = time.time()
            storage_results = await self._fast_storage(enriched_products, site_name, category)
            self.metrics['storage_time'] = time.time() - storage_start
            
            # Calculate totals
            self.metrics['total_time'] = time.time() - start_time
            self.metrics['products_processed'] = len(enriched_products)
            self.metrics['success_rate'] = len([p for p in enriched_products if p.get('seo_data')]) / max(1, len(products))
            
            if progress_callback:
                await progress_callback(100, f"🎉 Tamamlandı! {len(enriched_products)} ürün {self.metrics['total_time']:.1f}s'de işlendi", "completed")
            
            logger.info(f"🎯 COMPLETED in {self.metrics['total_time']:.2f}s!")
            logger.info(f"📊 Breakdown: Scrape={self.metrics['scraping_time']:.2f}s, Analysis={self.metrics['analysis_time']:.2f}s, Storage={self.metrics['storage_time']:.2f}s")
            
            return {
                'success': True,
                'products': enriched_products,
                'metrics': self.metrics,
                'storage': storage_results
            }
            
        except Exception as e:
            logger.error(f"Fast workflow error: {e}")
            self.metrics['total_time'] = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'metrics': self.metrics
            }
        finally:
            # Cleanup
            await self.scraper.close()
    
    async def _parallel_enrichment(self, products: List[Dict]) -> List[Dict]:
        """Enrich all products in parallel"""
        # Create tasks for each product
        tasks = []
        for product in products:
            if product:  # Skip None/empty products
                tasks.append(self._enrich_single_product(product))
        
        # Process all in parallel with concurrency limit
        enriched = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed enrichments
        return [p for p in enriched if p and not isinstance(p, Exception)]
    
    async def _process_enrichment_task(self, task):
        """Process a single enrichment task"""
        return await task
    
    async def _enrich_single_product(self, product: Dict) -> Dict:
        """Enrich a single product with analysis and SEO"""
        try:
            # Skip if no valid data
            if not product.get('name'):
                return product
            
            # Use cache key based on product URL or name
            cache_key = f"enriched_{product.get('url', product.get('name', ''))}"
            
            # Simple cache implementation (no optimizer dependency)
            if not hasattr(self, '_cache'):
                self._cache = {}
            
            cached = self._cache.get(cache_key)
            if cached:
                return cached
            
            # Step 1: Quick analysis
            analysis_data = await self._quick_analyze(product)
            
            # Step 2: SEO generation
            seo_data = await self._quick_seo(analysis_data)
            
            # Step 3: Quality score
            quality_score = self._quick_quality_score(seo_data)
            
            # Combine results
            enriched = {
                **product,
                'analysis': analysis_data,
                'seo_data': seo_data,
                'quality_score': quality_score,
                'processed_at': datetime.now().isoformat()
            }
            
            # Cache result
            self._cache[cache_key] = enriched
            
            return enriched
            
        except Exception as e:
            logger.debug(f"Enrichment error for product: {e}")
            return product
    
    async def _quick_analyze(self, product: Dict) -> Dict:
        """Quick product analysis"""
        try:
            # Prepare data in analyzer format
            analyzer_input = {
                'scraped_products': [{
                    'url': product.get('url', ''),
                    'scraped_data': product
                }]
            }
            
            # Run analyzer
            result = await self.analyzer.run(analyzer_input)
            
            if result.get('analyzed_products'):
                return result['analyzed_products'][0]
            
            # Fallback to basic analysis
            return {
                'cleaned_product': product,
                'extracted_terms': {
                    'ingredients': [],
                    'benefits': [],
                    'product_types': [product.get('category', 'cosmetic')]
                }
            }
            
        except:
            return {'cleaned_product': product, 'extracted_terms': {}}
    
    async def _quick_seo(self, analysis_data: Dict) -> Dict:
        """Quick SEO generation"""
        try:
            # Run SEO agent
            seo_input = {'analyzed_data': analysis_data}
            result = await self.seo_agent.run(seo_input)
            
            if 'error' not in result:
                return result
            
            # Fallback to basic SEO
            product = analysis_data.get('cleaned_product', {})
            return {
                'title': f"{product.get('brand', '')} {product.get('name', '')}".strip()[:60],
                'meta_description': product.get('description', '')[:155],
                'keywords': [],
                'primary_keyword': product.get('category', 'cosmetic'),
                'slug': product.get('name', '').lower().replace(' ', '-')[:50]
            }
            
        except:
            return {}
    
    def _quick_quality_score(self, seo_data: Dict) -> int:
        """Calculate quick quality score"""
        score = 0
        
        # Basic scoring
        if seo_data.get('title'):
            score += 20
            if len(seo_data['title']) >= 30:
                score += 10
        
        if seo_data.get('meta_description'):
            score += 20
            if len(seo_data['meta_description']) >= 100:
                score += 10
        
        if seo_data.get('keywords'):
            score += 20
            if len(seo_data['keywords']) >= 5:
                score += 10
        
        if seo_data.get('primary_keyword'):
            score += 10
        
        return min(score, 100)
    
    async def _fast_storage(self, products: List[Dict], site_name: str, category: str) -> Dict:
        """Fast storage of results"""
        try:
            # Prepare storage data
            storage_data = {
                'site': site_name,
                'category': category,
                'products': products,
                'metrics': self.metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store to file (async)
            filename = f"fast_results_{site_name}_{category}_{int(time.time())}.json"
            with open(f"data/web_results/{filename}", 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, ensure_ascii=False, indent=2)
            
            # Store to database if available
            if self.storage_agent:
                try:
                    await self.storage_agent.store_batch(products)
                    logger.info("✅ Data stored to database")
                except Exception as e:
                    logger.warning(f"Database storage failed: {e}")
            
            return {
                'filename': filename,
                'count': len(products),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Storage error: {e}")
            return {'status': 'error', 'error': str(e)}


async def run_fast_workflow(site_name: str = 'trendyol', category: str = 'parfüm', limit: int = 10):
    """Run the fast workflow"""
    import os
    db_url = os.getenv('DATABASE_URL')
    workflow = FastWorkflow(database_url=db_url)
    result = await workflow.process(site_name, category, limit)
    
    # Print results
    if result['success']:
        print(f"\n✅ SUCCESS! Processed {result['metrics']['products_processed']} products in {result['metrics']['total_time']:.2f} seconds")
        print(f"\n📊 Performance Metrics:")
        print(f"   - Scraping: {result['metrics']['scraping_time']:.2f}s")
        print(f"   - Analysis: {result['metrics']['analysis_time']:.2f}s") 
        print(f"   - Storage: {result['metrics']['storage_time']:.2f}s")
        print(f"   - Success Rate: {result['metrics']['success_rate']*100:.1f}%")
        
        # Show sample results
        if result['products']:
            print(f"\n📦 Sample Product:")
            product = result['products'][0]
            print(f"   Name: {product.get('name', 'N/A')}")
            print(f"   Brand: {product.get('brand', 'N/A')}")
            print(f"   Price: {product.get('price', 0)}")
            if product.get('seo_data'):
                print(f"   SEO Title: {product['seo_data'].get('title', 'N/A')}")
                print(f"   Keywords: {', '.join(product['seo_data'].get('keywords', [])[:5])}")
    else:
        print(f"\n❌ ERROR: {result.get('error')}")
    
    return result


if __name__ == "__main__":
    # Test the fast workflow
    import sys
    
    site = sys.argv[1] if len(sys.argv) > 1 else 'trendyol'
    category = sys.argv[2] if len(sys.argv) > 2 else 'parfüm'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    print(f"🚀 Running FAST workflow for {site} - {category} (limit: {limit})")
    asyncio.run(run_fast_workflow(site, category, limit))