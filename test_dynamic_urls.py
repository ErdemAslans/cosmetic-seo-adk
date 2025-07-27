#!/usr/bin/env python3
"""
Test Dynamic URL Discovery System
"""

import asyncio
import sys

async def test_trendyol_urls():
    """Test Trendyol URL discovery"""
    print("🔍 Testing Trendyol Dynamic URL Discovery")
    print("=" * 50)
    
    try:
        from agents.dynamic_url_mapper import get_current_category_urls, update_trendyol_urls
        
        # Test categories
        categories = ['cilt bakımı', 'makyaj', 'parfüm']
        
        print(f"🎯 Searching for: {categories}")
        
        # Discover current URLs
        result = await get_current_category_urls('trendyol', categories)
        
        print(f"\n✅ Results found: {len(result)}")
        for category, url in result.items():
            print(f"   📋 {category}: {url}")
        
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

async def test_gratis_urls():
    """Test Gratis URL discovery"""
    print("\n🔍 Testing Gratis Dynamic URL Discovery")
    print("=" * 50)
    
    try:
        from agents.dynamic_url_mapper import get_current_category_urls
        
        categories = ['makyaj', 'parfüm', 'cilt bakımı']
        
        print(f"🎯 Searching for: {categories}")
        
        result = await get_current_category_urls('gratis', categories)
        
        print(f"\n✅ Results found: {len(result)}")
        for category, url in result.items():
            print(f"   📋 {category}: {url}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

async def main():
    """Main test function"""
    print("🚀 DYNAMIC URL DISCOVERY TEST")
    print("=" * 60)
    
    # Test Trendyol
    trendyol_results = await test_trendyol_urls()
    
    # Test Gratis
    gratis_results = await test_gratis_urls()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print(f"✅ Trendyol URLs found: {len(trendyol_results)}")
    print(f"✅ Gratis URLs found: {len(gratis_results)}")
    
    if trendyol_results or gratis_results:
        print("\n🎉 Dynamic URL discovery is working!")
        print("💡 Your web app will now automatically find current category URLs")
        
        # Show example usage
        print("\n🌐 Web App Usage:")
        print("   POST /update-urls/trendyol - Update Trendyol URLs")
        print("   GET /current-urls/trendyol - Get current Trendyol URLs")
        print("   POST /update-urls/gratis - Update Gratis URLs")
        
    else:
        print("\n⚠️ No URLs found - check network connection or site availability")

if __name__ == "__main__":
    asyncio.run(main())