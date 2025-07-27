#!/usr/bin/env python3
"""
Category Filtering Test Script
Tests the enhanced category filtering functionality in the Scout Agent
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.modern_scraper_agent import discover_product_urls_advanced
from loguru import logger

async def test_category_filtering():
    """Test category filtering across different sites and categories"""
    
    test_cases = [
        {
            "site": "gratis",
            "category": "makyaj", 
            "expected_keywords": ["makyaj", "makeup", "ruj", "lipstick", "far", "fondöten"],
            "max_products": 10
        },
        {
            "site": "gratis", 
            "category": "cilt bakımı",
            "expected_keywords": ["cilt", "skin", "bakım", "serum", "krem", "temizleyici"],
            "max_products": 10
        },
        {
            "site": "trendyol",
            "category": "makyaj",
            "expected_keywords": ["makyaj", "makeup", "ruj", "lipstick", "far"],
            "max_products": 5
        }
    ]
    
    logger.info("🧪 Starting Category Filtering Tests")
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n🔬 Test {i}: {test_case['site']} - {test_case['category']}")
        
        try:
            # Discover URLs with category filtering
            result = await discover_product_urls_advanced(
                site_name=test_case["site"],
                max_products=test_case["max_products"], 
                target_category=test_case["category"]
            )
            
            if result.get("status") == "success":
                urls = result.get("discovered_urls", [])
                logger.info(f"✅ Discovered {len(urls)} URLs")
                
                # Analyze URLs for category relevance
                relevant_count = 0
                for url in urls:
                    url_lower = url.lower()
                    if any(keyword in url_lower for keyword in test_case["expected_keywords"]):
                        relevant_count += 1
                        logger.debug(f"   ✅ Relevant URL: {url[:60]}...")
                    else:
                        logger.debug(f"   ❓ Non-obvious URL: {url[:60]}...")
                
                relevance_ratio = relevant_count / len(urls) if urls else 0
                logger.info(f"📊 Category relevance: {relevant_count}/{len(urls)} ({relevance_ratio:.1%})")
                
                # Show sample URLs
                if urls:
                    logger.info("🔗 Sample URLs:")
                    for j, url in enumerate(urls[:3]):
                        logger.info(f"   {j+1}. {url}")
                
            else:
                logger.error(f"❌ Test failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Test {i} exception: {e}")
            
        logger.info("-" * 60)
    
    logger.info("🏁 Category filtering tests completed!")

if __name__ == "__main__":
    asyncio.run(test_category_filtering())