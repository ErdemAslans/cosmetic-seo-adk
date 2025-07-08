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
# Orchestration functionality is handled by flows in ADK
# from google.adk.flows import llm_flows

from agents.scout_agent import create_scout_agent
from agents.scraper_agent import create_scraper_agent
from agents.analyzer_agent import create_analyzer_agent
from agents.seo_agent import create_seo_agent
from agents.quality_agent import create_quality_agent
from agents.storage_agent import create_storage_agent

from config.sites import SITE_CONFIGS

# Load environment variables
load_dotenv()


class CosmeticSEOOrchestrator:
    """Main orchestrator for the cosmetic SEO extraction pipeline"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cosmetic_seo")
        self.data_dir = "data"
        self.max_products = int(os.getenv("MAX_PRODUCTS", 100))
        
        # Initialize agents
        self.scout_agent = create_scout_agent()
        self.scraper_agent = create_scraper_agent()
        self.analyzer_agent = create_analyzer_agent()
        self.seo_agent = create_seo_agent()
        self.quality_agent = create_quality_agent()
        self.storage_agent = create_storage_agent(self.database_url, self.data_dir)
        
        logger.info("Cosmetic SEO Orchestrator initialized with Google ADK")
    
    async def process_site(self, site_name: str, max_products: int = 50) -> Dict[str, Any]:
        """Process a single e-commerce site"""
        logger.info(f"Starting processing for site: {site_name}")
        
        try:
            # Step 1: Scout - Discover product URLs
            logger.info(f"Step 1: Discovering URLs from {site_name}")
            scout_result = await self.scout_agent.process_discovery_request(site_name, max_products)
            
            if "error" in scout_result:
                logger.error(f"Scout failed for {site_name}: {scout_result['error']}")
                return {"site": site_name, "error": scout_result["error"]}
            
            discovered_urls = scout_result.get("discovered_urls", [])
            logger.info(f"Discovered {len(discovered_urls)} URLs from {site_name}")
            
            if not discovered_urls:
                return {"site": site_name, "message": "No URLs discovered"}
            
            # Process URLs in batches to avoid overwhelming
            batch_size = 10
            processed_products = []
            
            for i in range(0, len(discovered_urls), batch_size):
                batch_urls = discovered_urls[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {len(batch_urls)} URLs")
                
                batch_results = await self._process_url_batch(batch_urls, site_name)
                processed_products.extend(batch_results)
                
                # Add delay between batches to respect rate limits
                await asyncio.sleep(2)
            
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
    
    async def _process_url_batch(self, urls: List[str], site_name: str) -> List[Dict[str, Any]]:
        """Process a batch of URLs through the complete pipeline"""
        processed_products = []
        
        for url in urls:
            try:
                result = await self._process_single_product(url, site_name)
                if result and "error" not in result:
                    processed_products.append(result)
                
                # Rate limiting
                await asyncio.sleep(float(os.getenv("RATE_LIMIT_SECONDS", 3)))
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                continue
        
        return processed_products
    
    async def _process_single_product(self, url: str, site_name: str) -> Dict[str, Any]:
        """Process a single product through the complete pipeline"""
        try:
            # Step 2: Scraper - Extract product data
            scraper_result = await self.scraper_agent.process_scraping_request(url, site_name)
            
            if "error" in scraper_result:
                logger.warning(f"Scraping failed for {url}: {scraper_result['error']}")
                return {"url": url, "error": scraper_result["error"]}
            
            product_data = scraper_result.get("product_data")
            if not product_data:
                return {"url": url, "error": "No product data extracted"}
            
            # Step 3: Analyzer - Clean and analyze data
            analyzer_result = await self.analyzer_agent.process_analysis_request(product_data)
            
            if "error" in analyzer_result:
                logger.warning(f"Analysis failed for {url}: {analyzer_result['error']}")
                return {"url": url, "error": analyzer_result["error"]}
            
            # Step 4: SEO Agent - Generate SEO metadata
            seo_result = await self.seo_agent.process_seo_request(analyzer_result)
            
            if "error" in seo_result:
                logger.warning(f"SEO generation failed for {url}: {seo_result['error']}")
                return {"url": url, "error": seo_result["error"]}
            
            # Step 5: Quality Agent - Validate quality
            extracted_terms = analyzer_result.get("extracted_terms", {})
            quality_result = await self.quality_agent.process_quality_validation(
                product_data, seo_result.get("seo_data", {}), extracted_terms
            )
            
            if "error" in quality_result:
                logger.warning(f"Quality validation failed for {url}: {quality_result['error']}")
                return {"url": url, "error": quality_result["error"]}
            
            # Step 6: Storage Agent - Store validated data
            storage_result = await self.storage_agent.process_storage_request(
                product_data, seo_result.get("seo_data", {}), quality_result
            )
            
            if "error" in storage_result:
                logger.warning(f"Storage failed for {url}: {storage_result['error']}")
                return {"url": url, "error": storage_result["error"]}
            
            logger.info(f"Successfully processed product: {url}")
            
            return {
                "url": url,
                "product_name": product_data.get("name", "Unknown"),
                "quality_score": quality_result.get("quality_score", 0),
                "is_valid": quality_result.get("is_valid", False),
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
            max_products_per_site = self.max_products // len(SITE_CONFIGS)
            
            site_result = await self.process_site(site_name, max_products_per_site)
            results[site_name] = site_result
            
            if "processed_products" in site_result:
                total_products += site_result["processed_products"]
                # Count successful products (those with valid quality scores)
                for product in site_result.get("products", []):
                    if product.get("is_valid", False):
                        successful_products += 1
        
        # Generate final report
        report = await self.storage_agent.generate_summary_report()
        
        logger.info(f"Extraction complete: {total_products} products processed, {successful_products} validated")
        
        return {
            "summary": {
                "total_products_processed": total_products,
                "successful_products": successful_products,
                "success_rate": successful_products / total_products if total_products > 0 else 0,
                "sites_processed": len(SITE_CONFIGS)
            },
            "site_results": results,
            "final_report": report,
            "completed_at": time.time()
        }
    
    async def run_sample_extraction(self, site_name: str = "trendyol", max_products: int = 10) -> Dict[str, Any]:
        """Run a sample extraction for testing"""
        logger.info(f"Running sample extraction: {site_name}, max_products: {max_products}")
        
        result = await self.process_site(site_name, max_products)
        report = await self.storage_agent.generate_summary_report()
        
        return {
            "sample_result": result,
            "report": report
        }


async def main():
    """Main entry point"""
    orchestrator = CosmeticSEOOrchestrator()
    
    # Check if running in test mode
    test_mode = os.getenv("TEST_MODE", "false").lower() == "true"
    
    if test_mode:
        logger.info("Running in TEST MODE - processing small sample")
        result = await orchestrator.run_sample_extraction("trendyol", 5)
    else:
        logger.info("Running FULL EXTRACTION")
        result = await orchestrator.run_full_extraction()
    
    logger.info("Extraction completed successfully")
    logger.info(f"Final result: {result['summary'] if 'summary' in result else result}")


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