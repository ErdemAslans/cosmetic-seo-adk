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
from agents.scraper_agent import create_scraper_agent
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
        self.scraper_agent = create_scraper_agent()
        self.analyzer_agent = create_analyzer_agent()
        self.seo_agent = create_seo_agent()
        self.quality_agent = create_quality_agent()
        self.storage_agent = create_storage_agent()
        
        logger.info("Cosmetic SEO Orchestrator initialized with Google ADK")
    
    async def process_site(self, site_name: str, max_products: int = 50) -> Dict[str, Any]:
        """Process a single e-commerce site"""
        logger.info(f"Starting processing for site: {site_name}")
        
        try:
            # Step 1: Scout - Discover product URLs using ADK
            logger.info(f"Step 1: Discovering URLs from {site_name}")
            
            # Use ADK's run method to get URLs
            scout_prompt = f"Discover {max_products} cosmetic product URLs from {site_name}. Use the discover_product_urls tool."
            
            async for event in self.scout_agent.run(scout_prompt):
                if event.type == "tool_call":
                    # Get the tool call result
                    tool_result = event.data
                    if tool_result and "discovered_urls" in tool_result:
                        discovered_urls = tool_result["discovered_urls"]
                        logger.info(f"Discovered {len(discovered_urls)} URLs from {site_name}")
                        break
            else:
                logger.error(f"No URLs discovered from {site_name}")
                return {"site": site_name, "error": "No URLs discovered"}
            
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
        """Process a single product through the complete pipeline using ADK"""
        try:
            # Step 2: Scraper - Extract product data using ADK
            scraper_prompt = f"Extract detailed product information from this URL: {url} for site: {site_name}. Use the scrape_product_data tool."
            
            scraper_result = None
            async for event in self.scraper_agent.run(scraper_prompt):
                if event.type == "tool_call":
                    scraper_result = event.data
                    break
            
            if not scraper_result or "error" in scraper_result:
                logger.warning(f"Scraping failed for {url}: {scraper_result.get('error', 'Unknown error')}")
                return {"url": url, "error": scraper_result.get("error", "Scraping failed")}
            
            product_data = scraper_result.get("product_data")
            if not product_data:
                return {"url": url, "error": "No product data extracted"}
            
            # Step 3: Analyzer - Clean and analyze data using ADK
            analyzer_prompt = f"Analyze and clean this product data: {product_data}. Use the analyze_product_data tool."
            
            analyzer_result = None
            async for event in self.analyzer_agent.run(analyzer_prompt):
                if event.type == "tool_call":
                    analyzer_result = event.data
                    break
            
            if not analyzer_result or "error" in analyzer_result:
                logger.warning(f"Analysis failed for {url}: {analyzer_result.get('error', 'Unknown error')}")
                return {"url": url, "error": analyzer_result.get("error", "Analysis failed")}
            
            # Step 4: SEO Agent - Generate SEO metadata using ADK
            seo_prompt = f"Generate SEO metadata for this analyzed product: {analyzer_result}. Use the generate_seo_data tool."
            
            seo_result = None
            async for event in self.seo_agent.run(seo_prompt):
                if event.type == "tool_call":
                    seo_result = event.data
                    break
            
            if not seo_result or "error" in seo_result:
                logger.warning(f"SEO generation failed for {url}: {seo_result.get('error', 'Unknown error')}")
                return {"url": url, "error": seo_result.get("error", "SEO generation failed")}
            
            # Step 5: Quality Agent - Validate quality using ADK
            quality_prompt = f"Validate quality of this product data: product_data={product_data}, seo_data={seo_result}. Use the validate_product_quality tool."
            
            quality_result = None
            async for event in self.quality_agent.run(quality_prompt):
                if event.type == "tool_call":
                    quality_result = event.data
                    break
            
            if not quality_result or "error" in quality_result:
                logger.warning(f"Quality validation failed for {url}: {quality_result.get('error', 'Unknown error')}")
                return {"url": url, "error": quality_result.get("error", "Quality validation failed")}
            
            # Step 6: Storage Agent - Store validated data using ADK
            storage_prompt = f"Store this validated product data: product_data={product_data}, seo_data={seo_result}, quality_data={quality_result}. Use the store_product_data tool."
            
            storage_result = None
            async for event in self.storage_agent.run(storage_prompt):
                if event.type == "tool_call":
                    storage_result = event.data
                    break
            
            if not storage_result or "error" in storage_result:
                logger.warning(f"Storage failed for {url}: {storage_result.get('error', 'Unknown error')}")
                return {"url": url, "error": storage_result.get("error", "Storage failed")}
            
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
            max_products_per_site = min(self.max_products // len(SITE_CONFIGS), 20)  # Limit per site
            
            logger.info(f"Processing site: {site_name} with max {max_products_per_site} products")
            
            site_result = await self.process_site(site_name, max_products_per_site)
            results[site_name] = site_result
            
            if "processed_products" in site_result:
                total_products += site_result["processed_products"]
                # Count successful products
                for product in site_result.get("products", []):
                    if product.get("is_valid", False):
                        successful_products += 1
        
        # Generate final report using ADK
        report_prompt = "Generate a summary report of the cosmetic SEO extraction process. Use the generate_summary_report tool."
        
        report = None
        try:
            async for event in self.storage_agent.run(report_prompt):
                if event.type == "tool_call":
                    report = event.data
                    break
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            report = {"error": str(e)}
        
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
        try:
            report_prompt = "Generate a sample report for testing. Use the generate_summary_report tool."
            
            report = None
            async for event in self.storage_agent.run(report_prompt):
                if event.type == "tool_call":
                    report = event.data
                    break
        except Exception as e:
            logger.error(f"Sample report generation failed: {e}")
            report = {"error": str(e)}
        
        return {
            "sample_result": result,
            "report": report or {}
        }


async def main():
    """Main entry point"""
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