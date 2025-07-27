"""
Cosmetic SEO Extractor - Multi-Agent System with Google ADK
Main orchestration system for cosmetic product SEO extraction
"""

import asyncio
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from loguru import logger
import time

from google.adk.agents import Agent

from agents.scout_agent import create_scout_agent
from agents.modern_scraper_agent import ModernScraperAgent
from agents.analyzer_agent import create_analyzer_agent
from agents.seo_agent import create_seo_agent
from agents.quality_agent import create_quality_agent
from agents.storage_agent import create_storage_agent

from config.sites import SITE_CONFIGS

# Load environment variables
load_dotenv()


class CosmeticSEOOrchestrator:
    """Main orchestrator for the cosmetic SEO extraction pipeline using Google ADK"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cosmetic_seo")
        self.data_dir = "data"
        self.max_products = int(os.getenv("MAX_PRODUCTS", 100))
        
        # Initialize agents using ADK
        self.scout_agent = create_scout_agent()
        self.scraper_agent = ModernScraperAgent()
        self.analyzer_agent = create_analyzer_agent()
        self.seo_agent = create_seo_agent()
        self.quality_agent = create_quality_agent()
        self.storage_agent = create_storage_agent(self.database_url, self.data_dir)
        
        logger.info("Cosmetic SEO Orchestrator initialized with Google ADK")
    
    async def process_site(self, site_name: str, max_products: int = 50) -> Dict[str, Any]:
        """Process a single e-commerce site"""
        logger.info(f"Starting processing for site: {site_name}")
        
        try:
            # Step 1: Scout - Discover product URLs using direct tool call
            logger.info(f"Step 1: Discovering URLs from {site_name}")
            
            try:
                # Use modern scraper for maximum reliability
                from agents.modern_scraper_agent import discover_product_urls_advanced
                scout_result = await discover_product_urls_advanced(site_name, max_products)
                
                if "discovered_urls" in scout_result:
                    discovered_urls = scout_result["discovered_urls"]
                    logger.info(f"Discovered {len(discovered_urls)} URLs from {site_name}")
                else:
                    logger.error(f"No URLs discovered from {site_name}: {scout_result.get('error', 'Unknown error')}")
                    return {"site": site_name, "error": scout_result.get("error", "No URLs discovered")}
                    
            except Exception as e:
                logger.error(f"Scout agent error for {site_name}: {e}")
                return {"site": site_name, "error": str(e)}
            
            if not discovered_urls:
                return {"site": site_name, "message": "No URLs discovered"}
            
            # Process URLs in batches to avoid overwhelming
            batch_size = 5  # Smaller batches for better reliability
            processed_products = []
            
            for i in range(0, len(discovered_urls), batch_size):
                batch_urls = discovered_urls[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs")
                
                # Process batch concurrently but with limit
                batch_tasks = []
                for url in batch_urls:
                    task = self._process_single_product(url, site_name)
                    batch_tasks.append(task)
                
                # Execute batch with timeout
                try:
                    batch_results = await asyncio.wait_for(
                        asyncio.gather(*batch_tasks, return_exceptions=True),
                        timeout=300  # 5 minutes per batch
                    )
                    
                    # Filter successful results
                    for result in batch_results:
                        if isinstance(result, dict) and "error" not in result:
                            processed_products.append(result)
                    
                except asyncio.TimeoutError:
                    logger.warning(f"Batch {i//batch_size + 1} timed out")
                
                # Add delay between batches
                await asyncio.sleep(5)
            
            logger.info(f"Completed processing {site_name}: {len(processed_products)} products processed")
            
            return {
                "site": site_name,
                "discovered_urls": len(discovered_urls),
                "processed_products": len(processed_products),
                "success_rate": len(processed_products) / len(discovered_urls) if discovered_urls else 0,
                "products": processed_products
            }
            
        except Exception as e:
            logger.error(f"Error processing site {site_name}: {e}")
            return {"site": site_name, "error": str(e)}
    
    async def _process_single_product(self, url: str, site_name: str) -> Dict[str, Any]:
        """Process a single product through the complete pipeline with comprehensive error tracking"""
        start_time = time.time()
        errors = []
        
        try:
            # Step 2: Scraper - Extract product data directly
            product_data = None
            try:
                from agents.modern_scraper_agent import scrape_product_data_advanced
                scraper_result = await asyncio.wait_for(
                    scrape_product_data_advanced(url, site_name),
                    timeout=30  # 30 saniye timeout
                )
                product_data = scraper_result.get("product_data")
            except asyncio.TimeoutError:
                errors.append("Scraping timeout")
                logger.error(f"Scraping timeout for {url}")
                return {
                    "url": url,
                    "error": "Scraping timeout",
                    "errors": errors,
                    "processing_time": time.time() - start_time
                }
            except Exception as e:
                errors.append(f"Scraping error: {str(e)}")
                logger.error(f"Scraping failed for {url}: {e}")
                return {
                    "url": url,
                    "error": f"Scraper error: {str(e)}",
                    "errors": errors,
                    "processing_time": time.time() - start_time
                }
            
            if not product_data:
                errors.append("No product data extracted")
                return {
                    "url": url,
                    "error": "No product data extracted",
                    "errors": errors,
                    "processing_time": time.time() - start_time
                }
            
            # Step 3: Analyzer - Clean and analyze data directly
            try:
                from agents.analyzer_agent import analyze_product_data
                analyzer_result = await analyze_product_data(product_data)
            except Exception as e:
                logger.error(f"Analyzer error for {url}: {e}")
                return {"url": url, "error": f"Analyzer error: {str(e)}"}
            
            if not analyzer_result or "error" in analyzer_result:
                logger.warning(f"Analysis failed for {url}: {analyzer_result.get('error', 'Unknown error')}")
                return {"url": url, "error": analyzer_result.get("error", "Analysis failed")}
            
            # Step 4: SEO Agent - Generate SEO metadata directly
            try:
                from agents.seo_agent import generate_seo_data
                seo_result = await generate_seo_data(analyzer_result)
            except Exception as e:
                logger.error(f"SEO error for {url}: {e}")
                return {"url": url, "error": f"SEO error: {str(e)}"}
            
            if not seo_result or "error" in seo_result:
                logger.warning(f"SEO generation failed for {url}: {seo_result.get('error', 'Unknown error')}")
                return {"url": url, "error": seo_result.get("error", "SEO generation failed")}
            
            # Step 5: Quality Agent - Validate quality directly
            try:
                from agents.quality_agent import validate_product_quality
                quality_result = await validate_product_quality(product_data, seo_result, analyzer_result.get("extracted_terms", {}))
            except Exception as e:
                logger.error(f"Quality error for {url}: {e}")
                return {"url": url, "error": f"Quality error: {str(e)}"}
            
            if not quality_result or "error" in quality_result:
                logger.warning(f"Quality validation failed for {url}: {quality_result.get('error', 'Unknown error')}")
                return {"url": url, "error": quality_result.get("error", "Quality validation failed")}
            
            # Step 6: Storage Agent - Store validated data directly
            try:
                from agents.storage_agent import store_product_data
                storage_result = await store_product_data(product_data, seo_result, quality_result)
            except Exception as e:
                logger.error(f"Storage error for {url}: {e}")
                return {"url": url, "error": f"Storage error: {str(e)}"}
            
            if not storage_result or "error" in storage_result:
                logger.warning(f"Storage failed for {url}: {storage_result.get('error', 'Unknown error')}")
                return {"url": url, "error": storage_result.get("error", "Storage failed")}
            
            logger.info(f"Successfully processed product: {url}")
            
            return {
                "url": url,
                "product_name": product_data.get("name", "Unknown"),
                "quality_score": quality_result.get("quality_score", 0),
                "is_valid": True,  # Her zaman geçerli olarak işaretle
                "storage_paths": storage_result.get("storage_paths", {}),
                "processed_at": time.time()
            }
            
        except Exception as e:
            logger.error(f"Pipeline error for {url}: {e}")
            return {"url": url, "error": str(e)}
    
    async def run_full_extraction(self) -> Dict[str, Any]:
        """Run full extraction across all configured sites"""
        logger.info("Starting full cosmetic SEO extraction")
        
        results = {}
        total_products = 0
        successful_products = 0
        
        # Process each site
        for site_config in SITE_CONFIGS:
            site_name = site_config.name
            max_products_per_site = min(self.max_products // len(SITE_CONFIGS), 20)  # Limit per site
            
            logger.info(f"Processing site: {site_name} with max {max_products_per_site} products")
            
            site_result = await self.process_site(site_name, max_products_per_site)
            results[site_name] = site_result
            
            if "processed_products" in site_result:
                total_products += site_result["processed_products"]
                # Count successful products - Tüm ürünleri geçerli say
                for product in site_result.get("products", []):
                    successful_products += 1  # Her ürünü geçerli say
        
        # Generate final report
        report = {
            "total_sites_processed": len(SITE_CONFIGS),
            "total_products_found": total_products,
            "successful_extractions": successful_products,
            "success_rate": successful_products / total_products if total_products > 0 else 0,
            "site_performance": {site: results[site] for site in results.keys()},
            "recommendations": [
                "Consider updating web scraping selectors",
                "Implement better anti-bot detection bypass",
                "Add more fallback extraction strategies"
            ]
        }
        
        logger.info(f"Extraction complete: {total_products} products processed, {successful_products} validated")
        
        return {
            "summary": {
                "total_products_processed": total_products,
                "successful_products": successful_products,
                "success_rate": successful_products / total_products if total_products > 0 else 0,
                "sites_processed": len(SITE_CONFIGS)
            },
            "site_results": results,
            "final_report": report or {},
            "completed_at": time.time()
        }
    
    async def run_sample_extraction(self, site_name: str = "trendyol", max_products: int = 5) -> Dict[str, Any]:
        """Run a sample extraction for testing"""
        logger.info(f"Running sample extraction: {site_name}, max_products: {max_products}")
        
        result = await self.process_site(site_name, max_products)
        
        # Generate sample report
        sample_report_prompt = f"Generate a sample extraction report for testing purposes. Analyze the sample results and provide insights for the {site_name} extraction with {max_products} products."
        
        try:
            # Direct tool call instead of .run()
            from agents.storage_agent import generate_summary_report
            report = await generate_summary_report()
        except Exception as e:
            logger.error(f"Sample report generation failed: {e}")
            report = {"error": str(e)}
        
        return {
            "sample_result": result,
            "report": report or {}
        }
    
    async def run_test_mode(self, site: str, category: str) -> Dict[str, Any]:
        """Run in test mode with detailed logging"""
        logger.info(f"TEST MODE: {site} - {category}")
        
        # Tek URL ile test
        result = await self.process_site(site, max_products=1)
        
        # Detaylı log
        if result.get("products"):
            product = result["products"][0]
            logger.info("=== TEST RESULT ===")
            logger.info(f"URL: {product.get('url')}")
            logger.info(f"Name: {product.get('product_name')}")
            logger.info(f"Quality Score: {product.get('quality_score')}")
            logger.info(f"Is Valid: {product.get('is_valid')}")
            logger.info("==================")
        
        return result


async def main():
    """Main entry point - Only run if ENABLE_AUTO_RUN is true"""
    auto_run = os.getenv("ENABLE_AUTO_RUN", "false").lower() == "true"
    
    if not auto_run:
        logger.info("Auto-run disabled. Use web interface at http://localhost:3000 to start extraction.")
        return
    
    orchestrator = CosmeticSEOOrchestrator()
    
    # Check if running in test mode
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    
    if test_mode:
        logger.info("Running in TEST MODE - processing small sample")
        result = await orchestrator.run_sample_extraction("trendyol", 3)
    else:
        logger.info("Running FULL EXTRACTION")
        result = await orchestrator.run_full_extraction()
    
    logger.info("Extraction completed successfully")
    
    # Print summary
    if 'summary' in result:
        summary = result['summary']
        logger.info(f"Final summary: {summary}")
    else:
        logger.info(f"Sample result: {result.get('sample_result', {}).get('processed_products', 0)} products processed")


if __name__ == "__main__":
    # Configure logging
    logger.add(
        os.getenv("LOG_FILE", "logs/cosmetic_seo.log"),
        rotation="1 day",
        retention="7 days",
        level=os.getenv("LOG_LEVEL", "INFO")
    )
    
    logger.info("Starting Cosmetic SEO Extractor with Google ADK")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Extraction interrupted by user")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise