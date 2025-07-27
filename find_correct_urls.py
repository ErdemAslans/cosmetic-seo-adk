#!/usr/bin/env python3
"""Find the correct URLs by searching the sites manually"""

import asyncio
from playwright.async_api import async_playwright

async def find_correct_category_urls():
    """Find the actual working category URLs"""
    
    sites_to_explore = [
        {
            "name": "Trendyol",
            "base": "https://www.trendyol.com",
            "search_terms": ["makyaj", "kozmetik", "makeup"]
        },
        {
            "name": "Gratis", 
            "base": "https://www.gratis.com",
            "search_terms": ["makyaj", "kozmetik", "makeup"]
        }
    ]
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            
            for site in sites_to_explore:
                print(f"\n{'='*60}")
                print(f"🔍 EXPLORING: {site['name']}")
                print(f"{'='*60}")
                
                try:
                    # Go to homepage first
                    await page.goto(site['base'], timeout=30000)
                    await page.wait_for_load_state('networkidle', timeout=15000)
                    await asyncio.sleep(3)
                    
                    print(f"✅ Homepage loaded: {await page.title()}")
                    
                    # Look for category links
                    print("\n🔗 Looking for category navigation...")
                    
                    # Find navigation elements
                    nav_selectors = [
                        'nav a', '.nav a', '.menu a', '.category a',
                        '[class*="nav"] a', '[class*="menu"] a', '[class*="category"] a',
                        'header a', '.header a'
                    ]
                    
                    category_links = {}
                    
                    for selector in nav_selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            for element in elements:
                                text = await element.text_content()
                                href = await element.get_attribute('href')
                                
                                if text and href:
                                    text_lower = text.lower().strip()
                                    if any(term in text_lower for term in ['makyaj', 'kozmetik', 'makeup', 'cosmetic']):
                                        # Make absolute URL
                                        if href.startswith('/'):
                                            href = site['base'] + href
                                        category_links[text_lower] = href
                        except:
                            continue
                    
                    print("📂 Found category links:")
                    for text, link in category_links.items():
                        print(f"  • {text}: {link}")
                    
                    # Try searching
                    print("\n🔍 Trying search functionality...")
                    search_selectors = [
                        'input[type="search"]', 'input[name="search"]', 'input[placeholder*="ara"]',
                        'input[placeholder*="search"]', '.search input', '#search'
                    ]
                    
                    for selector in search_selectors:
                        try:
                            search_input = await page.query_selector(selector)
                            if search_input:
                                print(f"✅ Found search input: {selector}")
                                await search_input.fill("makyaj")
                                await search_input.press('Enter')
                                await asyncio.sleep(5)
                                
                                current_url = page.url
                                print(f"🎯 Search result URL: {current_url}")
                                
                                # Check if products loaded
                                product_indicators = [
                                    'a[href*="/p/"]', '[class*="product"]', '[class*="item"]', 
                                    '.price', '[class*="price"]'
                                ]
                                
                                for indicator in product_indicators:
                                    elements = await page.query_selector_all(indicator)
                                    if len(elements) > 5:
                                        print(f"✅ Found products with {indicator}: {len(elements)} elements")
                                
                                break
                        except Exception as e:
                            continue
                    
                    # Test the best category link
                    if category_links:
                        print(f"\n🧪 Testing best category link...")
                        best_link = list(category_links.values())[0]  # Take first one
                        
                        await page.goto(best_link, timeout=30000)
                        await page.wait_for_load_state('networkidle', timeout=15000)
                        await asyncio.sleep(5)
                        
                        # Extensive scroll to load products
                        for i in range(5):
                            await page.mouse.wheel(0, 800)
                            await asyncio.sleep(2)
                        
                        print(f"📄 Category page title: {await page.title()}")
                        print(f"🌐 Category URL: {page.url}")
                        
                        # Check for actual products
                        all_links = await page.query_selector_all('a[href]')
                        product_links = []
                        
                        for link in all_links:
                            href = await link.get_attribute('href')
                            if href and any(pattern in href.lower() for pattern in ['/p/', '/product/', '/item/', '-p-', '/prd/', '/urun/', '/detail/']):
                                product_links.append(href)
                        
                        print(f"🛍️ Found {len(product_links)} potential product links")
                        if product_links:
                            print("Sample product URLs:")
                            for i, purl in enumerate(product_links[:5]):
                                print(f"  {i+1}. {purl}")
                        
                        # Try different selectors  
                        print("\n📊 Selector testing on category page:")
                        test_selectors = [
                            'a[href*="/p/"]', 'a[href*="/product/"]', 'a[href*="/urun/"]', 
                            'a[href*="/item/"]', 'a[href*="-p-"]',
                            '[class*="product"] a', '[class*="item"] a', '[class*="card"] a',
                            '[data-testid*="product"] a', 'article a'
                        ]
                        
                        working_selectors = []
                        for selector in test_selectors:
                            try:
                                elements = await page.query_selector_all(selector)
                                count = len(elements)
                                if count > 0:
                                    working_selectors.append((selector, count))
                                    print(f"  ✅ {selector}: {count} elements")
                            except:
                                continue
                        
                        if working_selectors:
                            print(f"\n🎯 BEST WORKING URL FOR {site['name']}: {page.url}")
                            print("🎯 BEST SELECTORS:")
                            for selector, count in sorted(working_selectors, key=lambda x: x[1], reverse=True)[:3]:
                                print(f"  • {selector}: {count} elements")
                    
                except Exception as e:
                    print(f"❌ Error exploring {site['name']}: {e}")
                    continue
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(find_correct_category_urls())