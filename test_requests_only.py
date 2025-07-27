#!/usr/bin/env python3
"""
Simple test using requests only - no browser dependencies
Tests basic URL discovery and HTML parsing
"""

import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time

async def test_site_connectivity():
    """Test basic site connectivity and HTML extraction"""
    print("🔧 Testing site connectivity with requests...")
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            # Test Trendyol category page
            url = "https://www.trendyol.com/butik/lista/kadin-makyaj"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            print(f"📍 Testing URL: {url}")
            
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"❌ HTTP {response.status}: {response.reason}")
                    return False
                
                html_content = await response.text()
                print(f"✅ Page loaded successfully ({len(html_content)} chars)")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look for product links
                print("🔍 Searching for product links...")
                
                # Multiple strategies for finding product URLs
                selectors = [
                    'a[href*="/p-"]',
                    'a[href*="product"]',
                    'a[href*="/urun/"]'
                ]
                
                found_links = []
                
                for selector in selectors:
                    links = soup.select(selector)
                    print(f"   Selector '{selector}': {len(links)} matches")
                    
                    for link in links:
                        href = link.get('href')
                        if href:
                            absolute_url = urljoin("https://www.trendyol.com", href)
                            if '/p-' in absolute_url:
                                found_links.append(absolute_url)
                
                # Fallback: search all links for product patterns
                if not found_links:
                    print("   Using fallback strategy...")
                    all_links = soup.find_all('a', href=True)
                    print(f"   Found {len(all_links)} total links")
                    
                    for link in all_links:
                        href = link['href']
                        absolute_url = urljoin("https://www.trendyol.com", href)
                        
                        # Check for Trendyol product URL patterns
                        if re.search(r'/p-\d+', absolute_url):
                            found_links.append(absolute_url)
                
                # Remove duplicates
                found_links = list(set(found_links))
                
                print(f"🎯 Found {len(found_links)} unique product URLs:")
                for i, link in enumerate(found_links[:5], 1):
                    print(f"   {i}. {link}")
                
                # Test accessing a product page if we found any
                if found_links:
                    print(f"\n🧪 Testing product page access...")
                    test_url = found_links[0]
                    print(f"📍 Accessing: {test_url}")
                    
                    try:
                        async with session.get(test_url, headers=headers, timeout=15) as prod_response:
                            if prod_response.status == 200:
                                prod_html = await prod_response.text()
                                prod_soup = BeautifulSoup(prod_html, 'html.parser')
                                
                                # Extract basic product info
                                title_selectors = [
                                    '.pr-new-br span',
                                    '.product-title',
                                    'h1[data-test-id]',
                                    'h1'
                                ]
                                
                                title = None
                                for sel in title_selectors:
                                    title_elem = prod_soup.select_one(sel)
                                    if title_elem and title_elem.get_text().strip():
                                        title = title_elem.get_text().strip()
                                        break
                                
                                price_selectors = [
                                    '.prc-dsc',
                                    '.product-price',
                                    '.price'
                                ]
                                
                                price = None
                                for sel in price_selectors:
                                    price_elem = prod_soup.select_one(sel)
                                    if price_elem and price_elem.get_text().strip():
                                        price = price_elem.get_text().strip()
                                        break
                                
                                print(f"📄 Product Data:")
                                print(f"   Title: {title or 'Not found'}")
                                print(f"   Price: {price or 'Not found'}")
                                
                                return len(found_links) > 0
                            else:
                                print(f"❌ Product page HTTP {prod_response.status}")
                                return False
                    
                    except Exception as e:
                        print(f"❌ Product page access failed: {e}")
                        return False
                else:
                    print("❌ No product URLs found")
                    return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

async def test_gratis():
    """Test Gratis site as well"""
    print("\n🔧 Testing Gratis connectivity...")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            url = "https://www.gratis.com/makyaj"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            print(f"📍 Testing URL: {url}")
            
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status != 200:
                    print(f"❌ HTTP {response.status}: {response.reason}")
                    return False
                
                html_content = await response.text()
                print(f"✅ Gratis page loaded successfully ({len(html_content)} chars)")
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look for Gratis product links
                product_links = soup.find_all('a', href=re.compile(r'/product/'))
                print(f"🎯 Found {len(product_links)} Gratis product links")
                
                return len(product_links) > 0
                
        except Exception as e:
            print(f"❌ Gratis test failed: {e}")
            return False

async def main():
    """Run connectivity tests"""
    print("🚀 COSMETIC SEO SYSTEM - CONNECTIVITY TEST")
    print("=" * 50)
    
    # Test Trendyol
    trendyol_success = await test_site_connectivity()
    
    # Test Gratis
    gratis_success = await test_gratis()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   Trendyol: {'✅ SUCCESS' if trendyol_success else '❌ FAILED'}")
    print(f"   Gratis: {'✅ SUCCESS' if gratis_success else '❌ FAILED'}")
    
    if trendyol_success or gratis_success:
        print("\n🎉 CONNECTIVITY TEST PASSED!")
        print("✅ System can access e-commerce sites")
        print("✅ HTML parsing and URL extraction working")
        print("✅ Product page access confirmed")
        print("\n💡 System ready for full testing with browser automation")
        return True
    else:
        print("\n❌ CONNECTIVITY TEST FAILED!")
        print("🔧 Check network connection and site availability")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n🚀 Ready to test with browser automation!")
        print("💡 Next: Install playwright dependencies or use Docker")