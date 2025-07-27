#!/usr/bin/env python3
"""
Test Fast System - Verify all optimizations work
"""

import asyncio
import time
from loguru import logger
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_fast_workflow():
    """Test the fast workflow system"""
    try:
        from fast_workflow import run_fast_workflow
        
        print("🚀 Testing FAST workflow system...")
        print("=" * 60)
        
        # Test with different configurations
        test_configs = [
            ('trendyol', 'parfüm', 5),
            ('gratis', 'makyaj', 3),
        ]
        
        for site, category, limit in test_configs:
            print(f"\n📋 Test: {site} - {category} (limit: {limit})")
            print("-" * 40)
            
            start_time = time.time()
            result = await run_fast_workflow(site, category, limit)
            test_time = time.time() - start_time
            
            if result['success']:
                print(f"✅ SUCCESS in {test_time:.2f}s")
                print(f"   Products: {result['metrics']['products_processed']}")
                print(f"   Success Rate: {result['metrics']['success_rate']*100:.1f}%")
            else:
                print(f"❌ FAILED: {result.get('error')}")
            
            # Quick break between tests
            await asyncio.sleep(1)
        
        print("\n" + "=" * 60)
        print("🎯 Fast workflow test completed!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

async def test_seo_agent():
    """Test the fixed SEO agent"""
    try:
        from agents.seo_agent import KeywordExtractionTool
        
        print("\n🧪 Testing SEO Agent fix...")
        
        tool = KeywordExtractionTool()
        product_data = {
            'name': 'Test Parfüm Oriental 50ml',
            'brand': 'Test Brand',
            'description': 'Oriental parfüm kadınlar için',
            'price': 100.0,
            'ingredients': ['test ingredient'],
            'features': ['test feature'],
            'usage': 'Test usage'
        }
        
        extracted_terms = {'cosmetic_terms': ['parfüm', 'oriental']}
        
        result = await tool(product_data, extracted_terms)
        
        if 'error' in result:
            print(f"❌ SEO Agent error: {result['error']}")
        else:
            print("✅ SEO Agent working correctly")
            print(f"   Primary keyword: {result.get('primary_keyword', 'N/A')}")
            print(f"   Keywords count: {len(result.get('keywords', []))}")
        
    except Exception as e:
        print(f"❌ SEO test error: {e}")

async def test_web_app():
    """Test web app integration"""
    try:
        from web_app import CosmeticSEOWebSystem
        
        print("\n🌐 Testing Web App integration...")
        
        system = CosmeticSEOWebSystem()
        
        # Check if fast workflow is initialized
        if hasattr(system, 'fast_workflow'):
            print("✅ Fast workflow integrated in web app")
        else:
            print("❌ Fast workflow not found in web app")
        
        # Test sites configuration
        print(f"✅ Configured sites: {list(system.sites.keys())}")
        
    except Exception as e:
        print(f"❌ Web app test error: {e}")

async def main():
    """Run all tests"""
    print("🔧 COSMETIC SEO SYSTEM - PERFORMANCE TEST")
    print("=" * 60)
    
    # Test 1: SEO Agent fix
    await test_seo_agent()
    
    # Test 2: Web app integration  
    await test_web_app()
    
    # Test 3: Fast workflow (main test)
    await test_fast_workflow()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())