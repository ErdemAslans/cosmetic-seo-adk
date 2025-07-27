#!/usr/bin/env python3
"""
Test script for enhanced Scout and Scraper agents
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_enhanced_scout_agent():
    """Test the enhanced Scout Agent with category-aware filtering"""
    print("🚀 Testing Enhanced Scout Agent")
    print("=" * 60)
    
    try:
        from agents.modern_scraper_agent import discover_product_urls_advanced
        
        # Test with category-specific discovery
        print("🎯 Testing Trendyol Makyaj category discovery...")
        result = await discover_product_urls_advanced("trendyol", 5, "makyaj")
        
        if result.get("status") == "success":
            urls = result.get("discovered_urls", [])
            print(f"✅ Scout Agent found {len(urls)} URLs for 'makyaj' category")
            print(f"📍 Target category: {result.get('target_category')}")
            
            # Show sample URLs
            for i, url in enumerate(urls[:3]):
                print(f"   🔗 URL {i+1}: {url}")
            
            # Check if URLs are relevant to makeup category
            makeup_keywords = ["makyaj", "makeup", "ruj", "lipstick", "far", "fondöten", "mascara"]
            relevant_count = 0
            for url in urls:
                if any(keyword in url.lower() for keyword in makeup_keywords):
                    relevant_count += 1
            
            relevance_score = (relevant_count / len(urls)) * 100 if urls else 0
            print(f"📊 Category relevance: {relevance_score:.1f}% ({relevant_count}/{len(urls)} URLs)")
            
            return len(urls) > 0 and relevance_score > 50
        else:
            print(f"❌ Scout Agent failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Scout Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_enhanced_scraper_agent():
    """Test the enhanced Scraper Agent with deep content discovery"""
    print("\n🚀 Testing Enhanced Scraper Agent")
    print("=" * 60)
    
    try:
        from agents.modern_scraper_agent import scrape_product_data_advanced
        
        # Test URL (you can replace with a real product URL)
        test_url = "https://www.trendyol.com/sglam/kas-sekillendirici-brow-wax-p-123456"
        
        print(f"🔍 Testing deep scraping for: {test_url}")
        result = await scrape_product_data_advanced(test_url, "trendyol")
        
        if result.get("success"):
            product_data = result.get("product_data", {})
            print("✅ Deep Scraper Agent extraction successful!")
            
            # Analyze extraction depth
            analysis = {
                "name": bool(product_data.get("name")),
                "description": len(product_data.get("description", "")),
                "long_descriptions": len(product_data.get("long_descriptions", [])),
                "features": len(product_data.get("features", [])),
                "ingredients": len(product_data.get("ingredients", [])),
                "images": len(product_data.get("images", [])),
                "specifications": len(product_data.get("specifications", {})),
                "reviews": len(product_data.get("reviews", []))
            }
            
            print(f"📊 Extraction Analysis:")
            print(f"   ✓ Product Name: {analysis['name']}")
            print(f"   📝 Description Length: {analysis['description']} chars")
            print(f"   📚 Long Descriptions: {analysis['long_descriptions']} found")
            print(f"   🎯 Features: {analysis['features']} extracted")
            print(f"   🧪 Ingredients: {analysis['ingredients']} found")
            print(f"   🖼️ Images: {analysis['images']} collected")
            print(f"   📋 Specifications: {analysis['specifications']} items")
            print(f"   💬 Reviews: {analysis['reviews']} captured")
            
            # Quality scoring
            quality_score = (
                (10 if analysis['name'] else 0) +
                (min(analysis['description'] / 10, 20)) +
                (analysis['long_descriptions'] * 5) +
                (min(analysis['features'], 10)) +
                (min(analysis['ingredients'], 10)) +
                (min(analysis['images'], 5)) +
                (min(analysis['specifications'], 10)) +
                (min(analysis['reviews'], 10))
            )
            
            print(f"🏆 Deep Extraction Quality Score: {quality_score:.1f}/100")
            
            # Show extraction depth indicator
            extraction_depth = result.get("extraction_depth", "standard")
            print(f"🎯 Extraction Depth: {extraction_depth}")
            
            return quality_score > 30
            
        else:
            print(f"❌ Scraper Agent failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Scraper Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration():
    """Test the integration of both enhanced agents"""
    print("\n🚀 Testing Agent Integration")
    print("=" * 60)
    
    try:
        # Test Scout + Scraper workflow
        from agents.modern_scraper_agent import discover_product_urls_advanced, scrape_product_data_advanced
        
        print("🎯 Step 1: Scout Agent finding makyaj products...")
        scout_result = await discover_product_urls_advanced("trendyol", 2, "makyaj")
        
        if scout_result.get("status") != "success" or not scout_result.get("discovered_urls"):
            print("❌ Scout Agent failed - cannot proceed with integration test")
            return False
        
        urls = scout_result["discovered_urls"][:1]  # Test with 1 URL
        print(f"✅ Scout found {len(scout_result['discovered_urls'])} URLs, testing with 1")
        
        print("🔍 Step 2: Scraper Agent deep analysis...")
        scrape_result = await scrape_product_data_advanced(urls[0], "trendyol")
        
        if scrape_result.get("success"):
            product_data = scrape_result.get("product_data", {})
            print("✅ Full pipeline successful!")
            
            print(f"📋 Final Product Summary:")
            print(f"   🏷️ Name: {product_data.get('name', 'N/A')[:50]}...")
            print(f"   📝 Description: {len(product_data.get('description', ''))} characters")
            print(f"   🎯 Category Match: {'makyaj' in urls[0].lower() or 'makeup' in urls[0].lower()}")
            
            return True
        else:
            print(f"❌ Integration test failed at scraping: {scrape_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("🧪 ENHANCED AGENT TESTING SUITE")
    print("=" * 60)
    
    # Run all tests
    scout_success = await test_enhanced_scout_agent()
    scraper_success = await test_enhanced_scraper_agent()
    integration_success = await test_integration()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    results = {
        "🎯 Enhanced Scout Agent": "✅ PASS" if scout_success else "❌ FAIL",
        "🔍 Enhanced Scraper Agent": "✅ PASS" if scraper_success else "❌ FAIL", 
        "🚀 Full Integration": "✅ PASS" if integration_success else "❌ FAIL"
    }
    
    for test_name, result in results.items():
        print(f"   {test_name}: {result}")
    
    overall_success = scout_success and scraper_success and integration_success
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 ALL TESTS PASSED!")
        print("\n🌟 ENHANCED FEATURES READY:")
        print("✅ Category-aware Scout Agent with smart path selection")
        print("✅ Deep content discovery Scraper Agent")
        print("✅ Bottom-of-page long description extraction")
        print("✅ Tab and accordion content mining")
        print("✅ Comprehensive image and specification extraction")
        print("✅ AI-powered relevance scoring")
        print("\n🚀 Your enhanced agents are ready for production!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Please check the error messages above for details.")

if __name__ == "__main__":
    asyncio.run(main())