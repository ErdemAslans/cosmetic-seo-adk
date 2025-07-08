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

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from config.models import ProductData, SiteConfig
from config.sites import SITE_CONFIGS


class ProductScrapingTool(BaseTool):
    """Tool for scraping product details from cosmetic product pages"""
    
    def __init__(self):
        super().__init__(
            name="product_scraping",
            description="Extract detailed product information from cosmetic product URLs",
            is_long_running=True
        )
        self.site_configs = {config.name: config for config in SITE_CONFIGS}
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    def _create_driver(self) -> webdriver.Chrome:
        """Create a Chrome WebDriver instance"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    async def __call__(self, url: str, site_name: str) -> Dict[str, Any]:
        """Scrape product data from the given URL"""
        
        if site_name not in self.site_configs:
            return {"error": f"Site {site_name} not configured"}
        
        config = self.site_configs[site_name]
        driver = None
        
        try:
            driver = self._create_driver()
            product_data = await self._scrape_product(driver, url, site_name, config)
            
            if product_data:
                return {
                    "success": True,
                    "product_data": product_data.model_dump()
                }
            else:
                return {"error": "Failed to extract product data"}
                
        except Exception as e:
            logger.error(f"Scraping error for {url}: {e}")
            return {"error": str(e)}
        finally:
            if driver:
                driver.quit()
    
    async def _scrape_product(
        self, 
        driver: webdriver.Chrome, 
        url: str, 
        site_name: str,
        config: SiteConfig
    ) -> Optional[ProductData]:
        """Scrape product data from the page"""
        
        driver.get(url)
        await asyncio.sleep(random.uniform(2, 4))
        
        wait = WebDriverWait(driver, 10)
        
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            logger.error(f"Page load timeout for {url}")
            return None
        
        selectors = config.selectors
        
        product_data = {
            "url": url,
            "site": site_name,
            "name": self._extract_text(driver, selectors.get("name", "h1")),
            "brand": self._extract_text(driver, selectors.get("brand", ".brand")),
            "price": self._extract_text(driver, selectors.get("price", ".price")),
            "description": self._extract_text(driver, selectors.get("description", ".description")),
            "ingredients": self._extract_list(driver, selectors.get("ingredients", ".ingredients li")),
            "features": self._extract_list(driver, selectors.get("features", ".features li")),
            "usage": self._extract_text(driver, selectors.get("usage", ".usage")),
            "reviews": self._extract_reviews(driver, selectors.get("reviews", ".review-text")),
            "images": self._extract_images(driver, selectors.get("images", "img.product-image"))
        }
        
        # Fallback extraction if primary selectors fail
        if not product_data["name"] or not product_data["description"]:
            fallback_data = self._fallback_extraction(driver, url, site_name)
            for key, value in fallback_data.items():
                if not product_data[key] and value:
                    product_data[key] = value
        
        if product_data["name"] and product_data["description"]:
            return ProductData(**product_data)
        
        return None
    
    def _extract_text(self, driver: webdriver.Chrome, selector: str) -> str:
        """Extract text from element using CSS selector"""
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except NoSuchElementException:
            return ""
    
    def _extract_list(self, driver: webdriver.Chrome, selector: str) -> List[str]:
        """Extract list of text from elements using CSS selector"""
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            return [elem.text.strip() for elem in elements if elem.text.strip()]
        except NoSuchElementException:
            return []
    
    def _extract_reviews(self, driver: webdriver.Chrome, selector: str, limit: int = 10) -> List[str]:
        """Extract customer reviews"""
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)[:limit]
            return [elem.text.strip() for elem in elements if elem.text.strip()]
        except NoSuchElementException:
            return []
    
    def _extract_images(self, driver: webdriver.Chrome, selector: str) -> List[str]:
        """Extract product images"""
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            images = []
            for elem in elements:
                src = elem.get_attribute("src") or elem.get_attribute("data-src")
                if src and not src.startswith("data:"):
                    images.append(src)
            return images[:5]
        except NoSuchElementException:
            return []
    
    def _fallback_extraction(self, driver: webdriver.Chrome, url: str, site_name: str) -> Dict[str, Any]:
        """Fallback extraction using common selectors"""
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        # Extract name
        name = ""
        for selector in ['h1', 'h2', '.product-name', '.product-title', '[itemprop="name"]']:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                break
        
        # Extract description
        description = ""
        for selector in ['.product-description', '.description', '[itemprop="description"]', '.product-info']:
            element = soup.select_one(selector)
            if element:
                description = element.get_text(strip=True)
                break
        
        if not description:
            # Look for paragraphs that mention "product"
            desc_elements = soup.find_all(['p', 'div'], limit=10)
            for elem in desc_elements:
                text = elem.get_text(strip=True)
                if len(text) > 100 and "product" in text.lower():
                    description = text
                    break
        
        # Extract brand
        brand = ""
        for selector in ['.brand', '.product-brand', '[itemprop="brand"]', '.manufacturer']:
            element = soup.select_one(selector)
            if element:
                brand = element.get_text(strip=True)
                break
        
        # Extract price
        price = ""
        for selector in ['.price', '.product-price', '[itemprop="price"]', '.cost']:
            element = soup.select_one(selector)
            if element:
                price = element.get_text(strip=True)
                break
        
        return {
            "url": url,
            "site": site_name,
            "name": name,
            "brand": brand,
            "price": price,
            "description": description,
            "ingredients": [],
            "features": [],
            "usage": "",
            "reviews": [],
            "images": []
        }


class ScraperAgent(LlmAgent):
    """Scraper Agent for extracting cosmetic product data using Google ADK"""
    
    def __init__(self):
        tools = [ProductScrapingTool()]
        
        super().__init__(
            name="scraper_agent",
            model="gemini-1.5-pro-latest",
            tools=tools,
            instruction="""
            You are a Scraper Agent specialized in extracting detailed information from cosmetic product pages.
            
            Your primary responsibilities:
            1. Use the product_scraping tool to extract comprehensive product data
            2. Handle different e-commerce site structures and layouts
            3. Extract key information: name, brand, price, description, ingredients, features
            4. Gather customer reviews and product images
            5. Ensure data quality and completeness
            6. Handle errors gracefully and use fallback extraction methods
            
            For each product URL you receive:
            1. Use the product_scraping tool with the URL and site name
            2. Validate that all critical fields are extracted (name, description)
            3. Return structured product data
            
            Focus on extracting:
            - Product name and brand
            - Price information
            - Detailed product description
            - Ingredients list (very important for cosmetics)
            - Product features and benefits
            - Usage instructions
            - Customer reviews (first 5-10)
            - Product images
            
            Always prioritize data quality over speed. It's better to extract complete,
            accurate information than to rush through incomplete data.
            """
        )
    
    async def process_scraping_request(self, url: str, site_name: str) -> Dict[str, Any]:
        """Process a product scraping request"""
        try:
            prompt = f"""
            Extract detailed product information from this cosmetic product URL:
            URL: {url}
            Site: {site_name}
            
            Use the product_scraping tool to extract comprehensive product data.
            Make sure to get:
            1. Complete product name and brand
            2. Price information
            3. Detailed product description
            4. Full ingredients list (critical for cosmetics)
            5. Product features and benefits
            6. Usage instructions if available
            7. Customer reviews for insights
            8. Product images
            
            Return the extracted data in a structured format.
            """
            
            response = await self.run_async(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Scraper Agent error: {e}")
            return {"error": str(e)}


# Agent factory function for ADK orchestration
def create_scraper_agent() -> ScraperAgent:
    """Factory function to create Scraper Agent instance"""
    return ScraperAgent()