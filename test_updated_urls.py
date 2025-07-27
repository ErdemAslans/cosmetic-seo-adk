#!/usr/bin/env python3
"""
Test with updated URLs for Turkish e-commerce sites
"""

import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

async def test_updated_urls():
    """Test with current working URLs"""
    print("🔧 Testing updated URLs...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    # Test URLs for different sites
    test_urls = [
        {
            "name": "Trendyol Main",
            "url": "https://www.trendyol.com",
            "expected_pattern": r'/p-\d+'
        },
        {
            "name": "Trendyol Beauty", 
            "url": "https://www.trendyol.com/sr?q=kozmetik",
            "expected_pattern": r'/p-\d+'
        },
        {
            "name": "Gratis Main",
            "url": "https://www.gratis.com",
            "expected_pattern": r'/product/'
        },
        {
            "name": "Sephora TR",
            "url": "https://www.sephora.com.tr",
            "expected_pattern": r'/product/'
        }
    ]
    
    async with aiohttp.ClientSession(connector=connector) as session:
        results = []
        
        for site in test_urls:
            print(f"\n📍 Testing {site['name']}: {site['url']}")
            
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache"
                }
                
                async with session.get(site['url'], headers=headers, timeout=30) as response:
                    print(f"   Status: {response.status} {response.reason}")
                    
                    if response.status == 200:
                        html_content = await response.text()
                        print(f"   Content length: {len(html_content)} chars")
                        
                        # Quick check for product links
                        pattern_matches = re.findall(site['expected_pattern'], html_content)
                        print(f"   Found {len(set(pattern_matches))} potential product URLs")
                        
                        soup = BeautifulSoup(html_content, 'html.parser')
                        all_links = soup.find_all('a', href=True)
                        print(f"   Total links: {len(all_links)}")
                        
                        product_links = []
                        for link in all_links[:100]:  # Check first 100 links
                            href = link['href']
                            if re.search(site['expected_pattern'], href):
                                absolute_url = urljoin(site['url'], href)
                                product_links.append(absolute_url)
                        
                        product_links = list(set(product_links))[:5]  # Get first 5 unique
                        
                        if product_links:
                            print(f"   ✅ SUCCESS - Found {len(product_links)} product URLs:")
                            for i, link in enumerate(product_links, 1):
                                print(f"      {i}. {link}")
                            results.append((site['name'], True, product_links))
                        else:
                            print(f"   ⚠️  No product URLs found with pattern {site['expected_pattern']}")
                            results.append((site['name'], False, []))
                    else:
                        print(f"   ❌ Failed with status {response.status}")
                        results.append((site['name'], False, []))
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append((site['name'], False, []))
        
        return results

async def test_specific_trendyol():
    """Test specific Trendyol category URL"""
    print("\n🎯 Testing specific Trendyol category...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        # Try the working category URL from our previous tests
        url = "https://www.trendyol.com/kozmetik-x-c1234"
        
        print(f"📍 Testing: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        
        try:
            async with session.get(url, headers=headers, timeout=30) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    # Look for any product URLs in the HTML
                    product_urls = re.findall(r'https://www\.trendyol\.com/[^"]+/p-\d+', html)
                    product_urls = list(set(product_urls))[:10]
                    
                    print(f"   Found {len(product_urls)} product URLs in HTML")
                    for i, url in enumerate(product_urls, 1):
                        print(f"      {i}. {url}")
                    
                    return len(product_urls) > 0
                else:
                    print(f"   Failed: {response.status}")
                    return False
        except Exception as e:
            print(f"   Error: {e}")
            return False

async def main():
    """Run the updated URL tests"""
    print("🚀 COSMETIC SEO SYSTEM - UPDATED URL TEST")
    print("=" * 50)
    
    # Test general URLs
    results = await test_updated_urls()
    
    # Test specific Trendyol
    trendyol_specific = await test_specific_trendyol()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"=" * 30)
    
    success_count = 0
    for name, success, links in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   {name}: {status}")
        if success:
            success_count += 1
    
    print(f"   Trendyol Specific: {'✅ SUCCESS' if trendyol_specific else '❌ FAILED'}")
    
    overall_success = success_count > 0 or trendyol_specific
    
    if overall_success:
        print(f"\n🎉 URL DISCOVERY TEST PASSED!")
        print(f"✅ {success_count} sites accessible")
        print(f"✅ Product URL patterns detected")
        print(f"✅ HTML parsing working correctly")
        print(f"\n💡 System ready for full implementation")
    else:
        print(f"\n❌ All sites failed - possible network issues")
        print(f"🔧 Check internet connection and site availability")
    
    return overall_success

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n🚀 SYSTEM IS READY!")
        print("💡 The URL discovery mechanism is working")
        print("🔧 Next: Set up browser automation or use Docker")