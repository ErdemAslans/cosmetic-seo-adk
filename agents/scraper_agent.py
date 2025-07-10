"""
Scraper Agent - Product Data Extraction Agent built with Google ADK
Extracts detailed product information from cosmetic product pages
"""

import asyncio
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from loguru import logger
import random
import time
import json

from google.adk.agents import Agent
from config.models import ProductData, SiteConfig
from config.sites import SITE_CONFIGS


# Global configs for sites
SITE_CONFIGS_DICT = {config.name: config for config in SITE_CONFIGS}


def _create_driver() -> webdriver.Chrome:
    """Create a Chrome WebDriver instance with anti-bot measures"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    options = Options()
    options.add_argument("--headless=new")  # New headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Additional anti-detection
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    
    driver = webdriver.Chrome(options=options)
    
    # Hide webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": random.choice(user_agents)
    })
    
    return driver


# Tool function for ADK
async def scrape_product_data(url: str, site_name: str) -> Dict[str, Any]:
    """Extract detailed product information from cosmetic product URLs.
    
    Args:
        url: The product page URL to scrape
        site_name: Name of the e-commerce site (e.g., 'trendyol', 'gratis')
        
    Returns:
        Dictionary containing scraped product data or error information
    """
    if site_name not in SITE_CONFIGS_DICT:
        return {"error": f"Site {site_name} not configured", "product_data": None}
    
    config = SITE_CONFIGS_DICT[site_name]
    driver = None
    
    try:
        driver = _create_driver()
        
        # Navigate to page with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get(url)
                
                # Wait for page to load
                wait = WebDriverWait(driver, 15)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Additional wait for dynamic content
                await asyncio.sleep(random.uniform(2, 4))
                
                # Check if we're blocked
                page_title = driver.title.lower()
                if any(blocked in page_title for blocked in ["access denied", "robot", "captcha"]):
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5)
                        continue
                    else:
                        return {"error": "Blocked by anti-bot protection", "product_data": None}
                
                break
                
            except TimeoutException:
                if attempt < max_retries - 1:
                    logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                    await asyncio.sleep(3)
                else:
                    return {"error": "Page load timeout after retries", "product_data": None}
        
        # Extract product data with site-specific selectors
        product_data = await _extract_product_data(driver, url, site_name, config)
        
        if product_data and product_data.get("name") and product_data.get("description"):
            return {
                "success": True,
                "product_data": product_data,
                "status": "success"
            }
        else:
            # Try enhanced fallback extraction
            product_data = await _enhanced_fallback_extraction(driver, url, site_name)
            if product_data and product_data.get("name"):
                return {
                    "success": True,
                    "product_data": product_data,
                    "status": "success_with_fallback"
                }
            else:
                return {"error": "Failed to extract product data", "product_data": None}
            
    except Exception as e:
        logger.error(f"Scraping error for {url}: {e}")
        return {"error": str(e), "product_data": None}
    finally:
        if driver:
            driver.quit()


async def _extract_product_data(
    driver: webdriver.Chrome, 
    url: str, 
    site_name: str,
    config: SiteConfig
) -> Dict[str, Any]:
    """Extract product data using site-specific selectors"""
    
    # Updated selectors for each site
    if site_name == "trendyol":
        selectors = {
            "name": ["h1.pr-new-br span", "h1.product-name", "h1", ".product-name-text"],
            "brand": ["h1.pr-new-br a", ".product-brand", "a.brand-name", ".pr-in-br a"],
            "price": [".prc-dsc", ".product-price-value", ".price", ".prc-box-dscntd"],
            "description": [".detail-desc-list", ".info-wrapper", ".product-description", ".pr-in-desc"],
            "ingredients": [".detail-attr-item:contains('İçerik') .detail-attr-value", ".ingredients"],
            "features": [".pr-in-features li", ".detail-attr-item", ".product-feature-content"],
            "images": ["img.detail-section-img", "img.product-image", ".product-slide img"]
        }
    elif site_name == "gratis":
        selectors = {
            "name": ["h1.product-name", "h1", ".ems-prd-name", ".product-title"],
            "brand": [".product-brand", ".brand-name", ".ems-prd-brand"],
            "price": [".product-price", ".price-value", ".ems-prd-price-selling"],
            "description": [".product-description", ".tab-content", ".ems-prd-description"],
            "ingredients": [".ingredients-content", ".tab-panel:contains('İçindekiler')"],
            "features": [".product-features li", ".feature-list li"],
            "images": [".product-image img", ".gallery-image img", ".ems-prd-image img"]
        }
    elif site_name == "sephora_tr":
        selectors = {
            "name": ["h1.ProductMeta__Title", "h1.product-name", "h1"],
            "brand": [".ProductMeta__Brand", ".product-brand", ".brand-name"],
            "price": [".Price__Value", ".product-price", ".price"],
            "description": [".ProductDetail__Description", ".product-description"],
            "ingredients": [".Ingredients__Content", ".ingredients-list"],
            "features": [".ProductBenefits li", ".benefits-list li"],
            "images": [".ProductImages img", ".product-gallery img"]
        }
    elif site_name == "rossmann":
        selectors = {
            "name": ["h1.product-title", "h1", ".product-name"],
            "brand": [".product-brand", ".brand", ".manufacturer"],
            "price": [".product-price", ".price-now", ".current-price"],
            "description": [".product-description", ".description-content"],
            "ingredients": [".ingredients", ".product-ingredients"],
            "features": [".product-features li", ".features-list li"],
            "images": [".product-image img", ".gallery img"]
        }
    else:
        # Use config selectors
        selectors = config.selectors
    
    # Extract data using multiple selectors
    product_data = {
        "url": url,
        "site": site_name,
        "name": _extract_text_multi(driver, selectors.get("name", ["h1"])),
        "brand": _extract_text_multi(driver, selectors.get("brand", [".brand"])),
        "price": _extract_text_multi(driver, selectors.get("price", [".price"])),
        "description": _extract_text_multi(driver, selectors.get("description", [".description"])),
        "ingredients": _extract_list_multi(driver, selectors.get("ingredients", [])),
        "features": _extract_list_multi(driver, selectors.get("features", [])),
        "usage": _extract_text_multi(driver, selectors.get("usage", [".usage"])),
        "reviews": _extract_reviews(driver, site_name),
        "images": _extract_images_multi(driver, selectors.get("images", []))
    }
    
    # Clean up the data
    for key, value in product_data.items():
        if isinstance(value, str):
            product_data[key] = value.strip()
        elif isinstance(value, list):
            product_data[key] = [v.strip() for v in value if v and v.strip()]
    
    return product_data


def _extract_text_multi(driver: webdriver.Chrome, selectors: List[str]) -> str:
    """Try multiple selectors to extract text"""
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            text = element.text.strip()
            if text:
                return text
        except NoSuchElementException:
            continue
    return ""


def _extract_list_multi(driver: webdriver.Chrome, selectors: List[str]) -> List[str]:
    """Try multiple selectors to extract list"""
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            items = [elem.text.strip() for elem in elements if elem.text.strip()]
            if items:
                return items
        except NoSuchElementException:
            continue
    return []


def _extract_images_multi(driver: webdriver.Chrome, selectors: List[str]) -> List[str]:
    """Try multiple selectors to extract images"""
    images = []
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                src = elem.get_attribute("src") or elem.get_attribute("data-src") or elem.get_attribute("data-original")
                if src and not src.startswith("data:") and src not in images:
                    images.append(src)
            if len(images) >= 5:
                break
        except NoSuchElementException:
            continue
    return images[:5]


def _extract_reviews(driver: webdriver.Chrome, site_name: str, limit: int = 10) -> List[str]:
    """Extract customer reviews based on site"""
    review_selectors = {
        "trendyol": [".comment-text", ".review-text", ".pr-xsm-cm-tx"],
        "gratis": [".review-content", ".comment-text"],
        "sephora_tr": [".ReviewItem__Text", ".review-text"],
        "rossmann": [".review-text", ".comment-content"]
    }
    
    selectors = review_selectors.get(site_name, [".review-text"])
    reviews = []
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)[:limit]
            for elem in elements:
                text = elem.text.strip()
                if text and len(text) > 10:
                    reviews.append(text)
            if reviews:
                break
        except NoSuchElementException:
            continue
    
    return reviews


async def _enhanced_fallback_extraction(driver: webdriver.Chrome, url: str, site_name: str) -> Dict[str, Any]:
    """Enhanced fallback extraction using multiple strategies"""
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    # Try JSON-LD structured data
    json_ld_data = _extract_json_ld(soup)
    if json_ld_data:
        return json_ld_data
    
    # Try meta tags
    meta_data = _extract_meta_tags(soup)
    
    # Common patterns extraction
    product_data = {
        "url": url,
        "site": site_name,
        "name": meta_data.get("name", "") or _extract_by_patterns(soup, ["h1", "h2", ".product-name", "[itemprop='name']"]),
        "brand": meta_data.get("brand", "") or _extract_by_patterns(soup, [".brand", "[itemprop='brand']", ".manufacturer"]),
        "price": meta_data.get("price", "") or _extract_price_from_soup(soup),
        "description": meta_data.get("description", "") or _extract_description_from_soup(soup),
        "ingredients": [],
        "features": [],
        "usage": "",
        "reviews": [],
        "images": _extract_images_from_soup(soup)
    }
    
    return product_data


def _extract_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """Extract product data from JSON-LD structured data"""
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get("@type") == "Product":
                return {
                    "name": data.get("name", ""),
                    "brand": data.get("brand", {}).get("name", "") if isinstance(data.get("brand"), dict) else data.get("brand", ""),
                    "price": str(data.get("offers", {}).get("price", "")),
                    "description": data.get("description", ""),
                    "images": [data.get("image")] if data.get("image") else []
                }
        except:
            continue
    return None


def _extract_meta_tags(soup: BeautifulSoup) -> Dict[str, Any]:
    """Extract product data from meta tags"""
    meta_data = {}
    
    # Open Graph tags
    og_title = soup.find("meta", {"property": "og:title"})
    if og_title:
        meta_data["name"] = og_title.get("content", "")
    
    og_description = soup.find("meta", {"property": "og:description"})
    if og_description:
        meta_data["description"] = og_description.get("content", "")
    
    # Product specific meta tags
    product_price = soup.find("meta", {"property": "product:price:amount"})
    if product_price:
        meta_data["price"] = product_price.get("content", "")
    
    return meta_data


def _extract_by_patterns(soup: BeautifulSoup, patterns: List[str]) -> str:
    """Extract text using multiple patterns"""
    for pattern in patterns:
        element = soup.select_one(pattern)
        if element:
            text = element.get_text(strip=True)
            if text:
                return text
    return ""


def _extract_price_from_soup(soup: BeautifulSoup) -> str:
    """Extract price using various patterns"""
    price_patterns = [
        ".price", ".product-price", "[itemprop='price']", 
        ".current-price", ".sale-price", ".prc-box"
    ]
    
    for pattern in price_patterns:
        elements = soup.select(pattern)
        for elem in elements:
            text = elem.get_text(strip=True)
            # Check if it contains numbers and currency symbols
            if any(char.isdigit() for char in text) and any(curr in text for curr in ["₺", "TL", "TRY", "USD", "$"]):
                return text
    return ""


def _extract_description_from_soup(soup: BeautifulSoup) -> str:
    """Extract description using various strategies"""
    # Look for description in specific elements
    desc_patterns = [
        ".product-description", ".description", "[itemprop='description']",
        ".detail-desc", ".product-info", ".content-description"
    ]
    
    for pattern in desc_patterns:
        element = soup.select_one(pattern)
        if element:
            text = element.get_text(strip=True)
            if len(text) > 50:  # Reasonable description length
                return text
    
    # Look for paragraphs that might be descriptions
    paragraphs = soup.find_all(["p", "div"], limit=20)
    for p in paragraphs:
        text = p.get_text(strip=True)
        if 50 < len(text) < 1000 and any(keyword in text.lower() for keyword in ["ürün", "product", "özellik", "kullanım"]):
            return text
    
    return ""


def _extract_images_from_soup(soup: BeautifulSoup) -> List[str]:
    """Extract product images from soup"""
    images = []
    img_patterns = [
        "img.product-image", "img.gallery-image", 
        ".product-gallery img", ".detail-section img"
    ]
    
    for pattern in img_patterns:
        elements = soup.select(pattern)
        for elem in elements:
            src = elem.get("src") or elem.get("data-src") or elem.get("data-original")
            if src and not src.startswith("data:") and src not in images:
                images.append(src)
        if len(images) >= 5:
            break
    
    return images[:5]


# Create Scraper Agent using ADK
def create_scraper_agent() -> Agent:
    """Factory function to create Scraper Agent instance with ADK"""
    return Agent(
        name="scraper_agent",
        model="gemini-2.0-flash",
        description="Specialized agent for extracting detailed product information from cosmetic e-commerce pages",
        instruction="""You are a Scraper Agent specialized in extracting detailed information from cosmetic product pages.

Your primary task is to use the scrape_product_data tool to extract comprehensive product information.

When given a product URL and site name:
1. Call scrape_product_data with the URL and site_name
2. Ensure all critical fields are extracted (especially name and description)
3. Return the structured product data

Focus on extracting:
- Product name and brand
- Price information
- Detailed product description
- Ingredients list (critical for cosmetics)
- Product features and benefits
- Usage instructions
- Customer reviews
- Product images

If initial extraction fails, the tool will automatically try fallback methods including:
- Alternative CSS selectors
- JSON-LD structured data
- Meta tags
- Common HTML patterns

Always return the complete extracted data, even if some fields are empty.""",
        tools=[scrape_product_data]
    )