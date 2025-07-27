"""
Constants for Cosmetic SEO Project

This module contains all common constants used across agents to eliminate
code duplication and provide a single source of truth.
"""

from typing import Dict, List

# User Agents for Web Scraping
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
]

# Chrome Browser Options for Anti-Bot Detection
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage", 
    "--disable-blink-features=AutomationControlled",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--ignore-ssl-errors=yes",
    "--ignore-certificate-errors",
    "--disable-features=VizDisplayCompositor",
    "--disable-setuid-sandbox"
]

# Playwright Browser Arguments
PLAYWRIGHT_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled", 
    "--disable-features=VizDisplayCompositor"
]

# Default Timeouts (in seconds)
DEFAULT_TIMEOUTS = {
    "page_load": 30,
    "element_wait": 10,
    "request": 30,
    "browser_launch": 60
}

# Delay Ranges (in seconds)
DELAY_RANGES = {
    "request_min": 1.0,
    "request_max": 3.0,
    "between_pages_min": 2.0,
    "between_pages_max": 5.0,
    "rate_limit_min": 0.5,
    "rate_limit_max": 1.5
}

# Site Configurations - Common Selectors
COMMON_SELECTORS = {
    "product_links": [
        "a[href*='/p/']",
        "a[href*='/product/']", 
        "a[href*='/urun/']",
        ".product-item a",
        ".product-card a",
        ".p-card-wrppr a"
    ],
    "product_title": [
        "h1",
        ".product-name h1",
        ".product-title",
        "[data-testid='product-title']"
    ],
    "brand": [
        ".product-brand a",
        ".brand-name",
        "[data-testid='brand']"
    ],
    "price": [
        ".price-current",
        ".prc-dsc", 
        ".price",
        "[data-testid='price']"
    ],
    "description": [
        ".product-description",
        ".product-details",
        ".detail-desc-item"
    ],
    "images": [
        ".product-images img",
        ".gallery-img img",
        ".product-gallery img"
    ]
}

# Product URL Validation Patterns
PRODUCT_URL_PATTERNS = {
    "trendyol": [r"/p/.*", r"/.*-p-\d+"],
    "gratis": [r"/.*"],
    "sephora": [r"/.*"],
    "rossmann": [r"/.*"]
}

# Cosmetic Categories (Turkish and English)
COSMETIC_CATEGORIES = {
    "tr": [
        "makyaj", "cilt bakımı", "saç bakımı", "parfüm", "kişisel bakım",
        "fondöten", "ruj", "maskara", "allık", "kapatıcı", "göz kalemi",
        "nemlendirici", "temizleyici", "tonik", "serum", "krem", "maske",
        "şampuan", "saç kremi", "saç maskesi", "deodorant", "duş jeli"
    ],
    "en": [
        "makeup", "skincare", "haircare", "fragrance", "personal care",
        "foundation", "lipstick", "mascara", "blush", "concealer", "eyeliner",
        "moisturizer", "cleanser", "toner", "serum", "cream", "mask",
        "shampoo", "conditioner", "hair mask", "deodorant", "body wash"
    ]
}

# Skin Types
SKIN_TYPES = [
    "normal", "kuru", "yağlı", "karma", "hassas", 
    "dry", "oily", "combination", "sensitive"
]

# Cosmetic Benefits/Properties
COSMETIC_BENEFITS = {
    "tr": [
        "nemlendirici", "anti-aging", "yaşlanma karşıtı", "beyazlatıcı", 
        "güneş koruyucu", "spf", "akne karşıtı", "leke giderici", 
        "sıkılaştırıcı", "besleyici", "onarıcı", "yatıştırıcı",
        "mat", "parlak", "doğal", "organik", "vegan", "hipoalerjenik"
    ],
    "en": [
        "moisturizing", "anti-aging", "brightening", "sun protection",
        "spf", "anti-acne", "spot correcting", "firming", "nourishing",
        "repairing", "soothing", "matte", "glowing", "natural", 
        "organic", "vegan", "hypoallergenic"
    ]
}

# Currency Symbols and Codes
CURRENCY_PATTERNS = {
    "₺": "TRY",
    "TL": "TRY", 
    "$": "USD",
    "€": "EUR",
    "£": "GBP"
}

# SEO Constants
SEO_LIMITS = {
    "title_min": 30,
    "title_max": 60,
    "title_optimal": 55,
    "meta_desc_min": 120,
    "meta_desc_max": 160,
    "meta_desc_optimal": 155,
    "url_slug_max": 100,
    "keywords_min": 3,
    "keywords_max": 10,
    "keywords_optimal": 7
}

# Quality Score Weights
QUALITY_WEIGHTS = {
    "title_length": 15,
    "meta_desc_length": 15,
    "keywords_count": 10,
    "url_slug_quality": 10,
    "keyword_relevance": 20,
    "content_quality": 20,
    "technical_seo": 10
}

# Common Turkish Characters Mapping
TURKISH_CHAR_MAP = {
    "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
    "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u"
}

# HTML Entities Mapping
HTML_ENTITIES = {
    "&amp;": "&",
    "&lt;": "<", 
    "&gt;": ">",
    "&quot;": '"',
    "&#39;": "'",
    "&nbsp;": " ",
    "&copy;": "©",
    "&reg;": "®",
    "&trade;": "™"
}

# Data Validation Rules
VALIDATION_RULES = {
    "product_title": {
        "min_length": 10,
        "max_length": 200,
        "required": True
    },
    "brand": {
        "min_length": 2,
        "max_length": 50,
        "required": False
    },
    "price": {
        "min_value": 0.01,
        "max_value": 999999,
        "required": False
    },
    "description": {
        "min_length": 20,
        "max_length": 5000,
        "required": False
    },
    "rating": {
        "min_value": 0,
        "max_value": 5,
        "required": False
    }
}

# File Formats and Extensions
SUPPORTED_FILE_FORMATS = {
    "json": ".json",
    "csv": ".csv", 
    "xlsx": ".xlsx",
    "xml": ".xml"
}

# Database Settings
DB_SETTINGS = {
    "connection_pool_size": 20,
    "connection_timeout": 30,
    "query_timeout": 60,
    "retry_attempts": 3
}

# Error Messages
ERROR_MESSAGES = {
    "invalid_url": "Invalid URL format provided",
    "no_products_found": "No products found on the page", 
    "scraping_failed": "Failed to scrape product data",
    "analysis_failed": "Failed to analyze product data",
    "seo_generation_failed": "Failed to generate SEO data",
    "quality_validation_failed": "Failed to validate SEO quality",
    "storage_failed": "Failed to store data",
    "missing_required_field": "Missing required field: {field}",
    "invalid_data_type": "Invalid data type for field: {field}",
    "rate_limit_exceeded": "Rate limit exceeded, please wait",
    "authentication_failed": "Authentication failed",
    "permission_denied": "Permission denied for operation"
}

# Success Messages  
SUCCESS_MESSAGES = {
    "products_found": "Found {count} products",
    "scraping_completed": "Successfully scraped {count} products",
    "analysis_completed": "Successfully analyzed product data",
    "seo_generated": "Successfully generated SEO data",
    "quality_validated": "SEO data quality validated successfully",
    "data_stored": "Data stored successfully",
    "operation_completed": "Operation completed successfully in {duration}"
}

# Retry Strategies
RETRY_STRATEGIES = {
    "network_error": {
        "max_attempts": 3,
        "delay": 2.0,
        "backoff_factor": 2.0
    },
    "rate_limit": {
        "max_attempts": 5, 
        "delay": 5.0,
        "backoff_factor": 1.5
    },
    "server_error": {
        "max_attempts": 2,
        "delay": 10.0,
        "backoff_factor": 1.0
    }
}

# Log Levels and Formats
LOG_CONFIG = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "level": "INFO",
    "max_file_size": "10MB",
    "backup_count": 5
}

# Cache Settings
CACHE_CONFIG = {
    "default_ttl": 3600,  # 1 hour
    "max_size": 1000,
    "cleanup_interval": 300  # 5 minutes
}