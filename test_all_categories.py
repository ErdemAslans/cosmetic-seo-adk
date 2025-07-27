#!/usr/bin/env python3
"""Test all categories for all sites with corrected URLs"""

import asyncio
from playwright.async_api import async_playwright
from config.modern_sites import MODERN_SITE_CONFIGS

async def test_all_categories():
    """Test all categories for all configured sites"""
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            
            for site_config in MODERN_SITE_CONFIGS:
                print(f"\n{'='*80}")
                print(f"🧪 TESTING ALL CATEGORIES FOR: {site_config.name.upper()}")
                print(f"{'='*80}")
                
                for i, category_path in enumerate(site_config.category_paths):
                    full_url = site_config.base_url + category_path
                    print(f"\n🔗 Testing category {i+1}/{len(site_config.category_paths)}: {full_url}")
                    
                    try:
                        # Navigate with timeout
                        await page.goto(full_url, timeout=30000)
                        await page.wait_for_load_state('networkidle', timeout=15000)
                        await asyncio.sleep(3)
                        
                        # Get page title
                        title = await page.title()
                        print(f"📄 Page title: {title}")
                        
                        # Scroll to load content
                        for scroll in range(3):
                            await page.mouse.wheel(0, 800)
                            await asyncio.sleep(1)
                        
                        # Test product link selectors
                        if isinstance(site_config.selectors.get("product_link"), list):
                            selectors = site_config.selectors["product_link"]
                        else:
                            selectors = [site_config.selectors.get("product_link", "")]
                        
                        total_products = 0
                        best_selector = None
                        best_count = 0
                        
                        for selector in selectors:
                            if not selector:
                                continue
                            try:
                                elements = await page.query_selector_all(selector)
                                count = len(elements)
                                total_products = max(total_products, count)
                                
                                if count > best_count:
                                    best_count = count
                                    best_selector = selector
                                    
                                if count > 0:
                                    print(f"  ✅ {selector}: {count} products")
                            except:
                                continue
                        
                        if total_products > 0:
                            print(f"🎯 BEST RESULT: {total_products} products found with '{best_selector}'")
                            
                            # Get sample product URLs
                            if best_selector:
                                sample_elements = await page.query_selector_all(best_selector)
                                sample_urls = []
                                for element in sample_elements[:3]:
                                    try:
                                        href = await element.get_attribute('href')
                                        if href:
                                            if href.startswith('/'):
                                                href = site_config.base_url + href
                                            sample_urls.append(href)
                                    except:
                                        continue
                                
                                if sample_urls:
                                    print("📦 Sample product URLs:")
                                    for j, url in enumerate(sample_urls):
                                        print(f"  {j+1}. {url}")
                        else:
                            print("❌ No products found with any selector")
                            
                            # Try universal fallback selectors
                            fallback_selectors = [
                                'a[href*="/p/"]', 'a[href*="/product/"]', 'a[href*="-p-"]',
                                '[class*="product"] a', '[class*="item"] a', 'article a'
                            ]
                            
                            print("🔄 Trying fallback selectors...")
                            for selector in fallback_selectors:
                                try:
                                    elements = await page.query_selector_all(selector)
                                    count = len(elements)
                                    if count > 0:
                                        print(f"  📌 {selector}: {count} elements")
                                except:
                                    continue
                        
                    except Exception as e:
                        print(f"❌ Error testing {full_url}: {e}")
                        continue
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_categories())