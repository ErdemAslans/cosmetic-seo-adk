#!/usr/bin/env python3
"""Manual URL inspection to understand real DOM structure"""

import asyncio
from playwright.async_api import async_playwright

async def inspect_urls_manually():
    """Go to each URL manually and analyze the real DOM structure"""
    
    test_urls = [
        "https://www.trendyol.com/makyaj-x-c100",
        "https://www.trendyol.com/kozmetik/makyaj-x-c105", 
        "https://www.gratis.com/makyaj-c-1",
        "https://www.gratis.com/makyaj"
    ]
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])  # Container mode
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            
            for url in test_urls:
                print(f"\n{'='*80}")
                print(f"🔍 MANUALLY INSPECTING: {url}")
                print(f"{'='*80}")
                
                try:
                    # Navigate and wait extensively
                    await page.goto(url, timeout=60000)
                    print("✅ Page loaded, waiting for content...")
                    
                    # Wait for network idle
                    await page.wait_for_load_state('networkidle', timeout=30000)
                    await asyncio.sleep(10)  # Extra long wait
                    
                    # Get page info
                    title = await page.title()
                    print(f"📄 Title: {title}")
                    
                    # Get all links
                    all_links = await page.query_selector_all('a[href]')
                    print(f"🔗 Total links found: {len(all_links)}")
                    
                    # Analyze product-like links
                    product_links = []
                    for link in all_links:
                        href = await link.get_attribute('href')
                        if href and any(pattern in href.lower() for pattern in ['/p/', '/product/', '/item/', '-p-', '/prd/', '/detail/']):
                            product_links.append(href)
                    
                    print(f"🛍️ Potential product links: {len(product_links)}")
                    if product_links:
                        print("Sample product URLs:")
                        for i, purl in enumerate(product_links[:5]):
                            print(f"  {i+1}. {purl}")
                    
                    # Check common selectors
                    selectors_to_test = [
                        'a[href*="/p/"]',
                        'a[href*="/product/"]', 
                        'a[href*="-p-"]',
                        '[class*="product"] a',
                        '[class*="item"] a',
                        '[class*="card"] a',
                        '.product-item a',
                        '.prd a',
                        '[data-testid*="product"] a',
                        'div[class] > a',
                        'article a'
                    ]
                    
                    print("\n📊 Selector Analysis:")
                    working_selectors = []
                    
                    for selector in selectors_to_test:
                        elements = await page.query_selector_all(selector)
                        count = len(elements)
                        print(f"  {selector}: {count} elements")
                        
                        if count > 0:
                            working_selectors.append((selector, count))
                            
                            # Get sample URLs from this selector
                            sample_urls = []
                            for element in elements[:3]:
                                try:
                                    href = await element.get_attribute('href')
                                    if href:
                                        sample_urls.append(href)
                                except:
                                    pass
                            
                            if sample_urls:
                                print(f"    Sample URLs: {sample_urls}")
                    
                    # Try scrolling to load more content
                    print("\n🔄 Testing scroll loading...")
                    initial_link_count = len(await page.query_selector_all('a[href]'))
                    
                    for i in range(3):
                        await page.mouse.wheel(0, 1000)
                        await asyncio.sleep(3)
                    
                    final_link_count = len(await page.query_selector_all('a[href]'))
                    print(f"📈 Links after scroll: {initial_link_count} → {final_link_count}")
                    
                    # Check for lazy loading containers
                    print("\n📦 Container Analysis:")
                    containers = await page.evaluate("""
                        () => {
                            const results = [];
                            const elements = document.querySelectorAll('*');
                            
                            elements.forEach(el => {
                                const children = el.children;
                                if (children.length >= 4 && children.length <= 100) {
                                    const links = el.querySelectorAll('a').length;
                                    const images = el.querySelectorAll('img').length;
                                    
                                    if (links > 0 && images > 0) {
                                        results.push({
                                            tag: el.tagName,
                                            className: el.className || '',
                                            children: children.length,
                                            links: links,
                                            images: images
                                        });
                                    }
                                }
                            });
                            
                            return results.slice(0, 10);
                        }
                    """)
                    
                    for container in containers:
                        print(f"  {container['tag']}.{container['className']}: {container['children']} children, {container['links']} links, {container['images']} images")
                    
                    print(f"\n✅ BEST SELECTORS FOR {url}:")
                    for selector, count in sorted(working_selectors, key=lambda x: x[1], reverse=True)[:5]:
                        print(f"  🎯 {selector}: {count} elements")
                    
                    print("\n" + "="*80)
                    
                except Exception as e:
                    print(f"❌ Error inspecting {url}: {e}")
                    continue
            
            await browser.close()
            
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_urls_manually())