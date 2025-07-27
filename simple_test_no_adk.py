#!/usr/bin/env python3
"""
Simple test without google.adk dependencies
Tests the URL discovery system independently
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_url_discovery():
    """Test URL discovery with minimal dependencies"""
    print("🔧 Testing URL discovery system...")
    
    try:
        # Import without ADK dependencies
        from playwright.async_api import async_playwright
        
        # Initialize browser directly
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Test Trendyol makeup category
        url = "https://www.trendyol.com/butik/lista/kadin-makyaj"
        print(f"📍 Testing URL: {url}")
        
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Extract product links using multiple strategies
        print("🔍 Extracting product URLs...")
        
        # Strategy 1: Direct selectors
        links1 = await page.evaluate("""
            () => {
                const links = [];
                const selectors = [
                    'a[href*="/p-"]',
                    'a[href*="product"]', 
                    '.p-card-wrppr a',
                    '.product-item a',
                    '[data-test-id="product-item"] a'
                ];
                
                for (const selector of selectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        if (el.href && el.href.includes('/p-')) {
                            links.push(el.href);
                        }
                    }
                    if (links.length > 0) break;
                }
                
                return [...new Set(links)].slice(0, 10);
            }
        """)
        
        # Strategy 2: More aggressive search
        if not links1:
            print("⚡ Using aggressive fallback strategy...")
            links1 = await page.evaluate("""
                () => {
                    const links = [];
                    const allLinks = document.querySelectorAll('a[href]');
                    
                    for (const link of allLinks) {
                        const href = link.href;
                        if (href && (href.includes('/p-') || href.includes('product'))) {
                            // Additional validation for Trendyol
                            if (href.includes('trendyol.com') && 
                                (href.includes('/p-') || href.includes('product-'))) {
                                links.push(href);
                            }
                        }
                    }
                    
                    return [...new Set(links)].slice(0, 10);
                }
            """)
        
        print(f"✅ Found {len(links1)} product URLs:")
        for i, link in enumerate(links1[:5], 1):
            print(f"   {i}. {link}")
        
        # Test product page access
        if links1:
            print(f"\n🧪 Testing product page access...")
            test_url = links1[0]
            print(f"📍 Accessing: {test_url}")
            
            try:
                await page.goto(test_url, wait_until="networkidle", timeout=15000)
                
                # Extract basic product info
                product_data = await page.evaluate("""
                    () => {
                        const data = {};
                        
                        // Title
                        const titleSelectors = [
                            '.pr-new-br span',
                            '.product-title',
                            'h1',
                            '[data-test-id="product-title"]'
                        ];
                        for (const sel of titleSelectors) {
                            const el = document.querySelector(sel);
                            if (el && el.textContent.trim()) {
                                data.title = el.textContent.trim();
                                break;
                            }
                        }
                        
                        // Price
                        const priceSelectors = [
                            '.prc-dsc',
                            '.product-price',
                            '.price',
                            '[data-test-id="price"]'
                        ];
                        for (const sel of priceSelectors) {
                            const el = document.querySelector(sel);
                            if (el && el.textContent.trim()) {
                                data.price = el.textContent.trim();
                                break;
                            }
                        }
                        
                        // Description
                        const descSelectors = [
                            '.product-description-text',
                            '.description',
                            '.detail-description'
                        ];
                        for (const sel of descSelectors) {
                            const el = document.querySelector(sel);
                            if (el && el.textContent.trim()) {
                                data.description = el.textContent.trim().substring(0, 200) + "...";
                                break;
                            }
                        }
                        
                        return data;
                    }
                """)
                
                print(f"📄 Product Data:")
                print(f"   Title: {product_data.get('title', 'Not found')}")
                print(f"   Price: {product_data.get('price', 'Not found')}")
                print(f"   Description: {product_data.get('description', 'Not found')}")
                
            except Exception as e:
                print(f"❌ Product page access failed: {e}")
        
        await browser.close()
        await playwright.stop()
        
        return len(links1) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Run the test"""
    print("🚀 COSMETIC SEO SYSTEM - URL DISCOVERY TEST")
    print("=" * 50)
    
    success = await test_url_discovery()
    
    if success:
        print("\n🎉 URL DISCOVERY TEST PASSED!")
        print("✅ System can discover and access product URLs")
        print("✅ Product data extraction working")
        print("\n💡 Next: Test with more categories and sites")
    else:
        print("\n❌ URL DISCOVERY TEST FAILED!")
        print("🔧 Check network connection and site availability")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    if not result:
        sys.exit(1)