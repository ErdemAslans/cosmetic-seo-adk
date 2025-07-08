#!/usr/bin/env python3
"""
Sample runner for testing the Cosmetic SEO Extractor
Tests the system with a small number of products
"""

import asyncio
import os
from dotenv import load_dotenv
from loguru import logger

from main import CosmeticSEOOrchestrator

load_dotenv()


async def run_sample_test():
    """Run a simple test of the system"""
    
    # Set test mode
    os.environ["TEST_MODE"] = "true"
    
    logger.info("🚀 Starting Cosmetic SEO Extractor Sample Test")
    logger.info("This will test the system with a small number of products")
    
    try:
        orchestrator = CosmeticSEOOrchestrator()
        
        # Test with Trendyol site, 3 products
        logger.info("Testing with Trendyol - 3 products")
        result = await orchestrator.run_sample_extraction("trendyol", 3)
        
        # Display results
        sample_result = result.get("sample_result", {})
        
        print("\n" + "="*60)
        print("📊 SAMPLE TEST RESULTS")
        print("="*60)
        
        if "error" in sample_result:
            print(f"❌ Error: {sample_result['error']}")
            return
        
        print(f"🌐 Site: {sample_result.get('site', 'Unknown')}")
        print(f"🔍 URLs Discovered: {sample_result.get('discovered_urls', 0)}")
        print(f"✅ Products Processed: {sample_result.get('processed_products', 0)}")
        print(f"📈 Success Rate: {sample_result.get('success_rate', 0):.1%}")
        
        products = sample_result.get('products', [])
        if products:
            print(f"\n📦 PROCESSED PRODUCTS:")
            for i, product in enumerate(products, 1):
                print(f"\n{i}. {product.get('product_name', 'Unknown Product')}")
                print(f"   🔗 URL: {product.get('url', 'N/A')}")
                print(f"   ⭐ Quality Score: {product.get('quality_score', 0):.1f}")
                print(f"   ✅ Valid: {'Yes' if product.get('is_valid', False) else 'No'}")
        
        # Display report summary
        report = result.get("report", {})
        if report and not isinstance(report, str):
            print(f"\n📈 DATABASE SUMMARY:")
            print(f"   Total Products: {report.get('total_products', 0)}")
            print(f"   Total SEO Entries: {report.get('total_seo_entries', 0)}")
            print(f"   Validation Rate: {report.get('validation_rate', 0):.1f}%")
            print(f"   Avg Quality Score: {report.get('average_quality_score', 0):.1f}")
        
        print("\n" + "="*60)
        print("✅ Sample test completed successfully!")
        print("="*60)
        
        # Show next steps
        print("\n🎯 NEXT STEPS:")
        print("1. Check data/exports/cosmetic_products_seo.csv for exported data")
        print("2. Check data/products/ for individual JSON files")
        print("3. Run full extraction: python main.py")
        print("4. Access ADK UI: docker-compose up adk-ui (then visit http://localhost:8000)")
        
    except Exception as e:
        logger.error(f"Sample test failed: {e}")
        print(f"\n❌ Sample test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your .env file configuration")
        print("3. Verify Google API credentials")
        print("4. Install required dependencies: pip install -r requirements.txt")


async def test_single_agent():
    """Test individual agents"""
    print("\n🧪 Testing Individual Agents...")
    
    from agents.scout_agent import create_scout_agent
    
    try:
        # Test Scout Agent
        scout = create_scout_agent()
        result = await scout.process_discovery_request("trendyol", 2)
        
        print(f"🕵️ Scout Agent Test: {'✅ SUCCESS' if 'discovered_urls' in result else '❌ FAILED'}")
        if 'discovered_urls' in result:
            print(f"   Found {len(result['discovered_urls'])} URLs")
        
    except Exception as e:
        print(f"🕵️ Scout Agent Test: ❌ FAILED - {e}")


if __name__ == "__main__":
    # Configure logging for sample test
    logger.add(
        "logs/sample_test.log",
        rotation="1 day",
        level="INFO"
    )
    
    print("🧪 Cosmetic SEO Extractor - Sample Test")
    print("This will test the system with a few products to verify it's working correctly.\n")
    
    try:
        asyncio.run(run_sample_test())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        print(f"\n💥 Test runner failed: {e}")