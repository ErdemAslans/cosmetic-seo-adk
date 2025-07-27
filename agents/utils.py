"""
Utility Functions for Cosmetic SEO Project

This module provides common utility functions used across all agents and tools,
implementing DRY principle and providing reusable functionality.
"""

import re
import json
import hashlib
import time
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from urllib.parse import urljoin, urlparse, quote, unquote
from datetime import datetime, timezone
import logging
import asyncio
from dataclasses import dataclass
from pathlib import Path
from functools import wraps

logger = logging.getLogger(__name__)


# Base Agent Functionality (moved from base_agent.py)
def error_handler(func: Callable) -> Callable:
    """Decorator for error handling in agent methods."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return {"error": str(e), "success": False}
    return wrapper


class RetryMixin:
    """Mixin for retry functionality."""
    
    async def retry_with_backoff(self, func: Callable, max_retries: int = 3, 
                               base_delay: float = 1.0, max_delay: float = 60.0):
        """Execute function with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = min(base_delay * (2 ** attempt), max_delay)
                logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                await asyncio.sleep(delay)


class BaseAgent(RetryMixin):
    """Base agent class with common functionality."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(self.name)
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Base run method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement run method")
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(f"[{self.name}] {message}")
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(f"[{self.name}] {message}")


# Data Classes for Common Structures
@dataclass
class ProductData:
    """Standardized product data structure."""
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    features: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    images: Optional[List[str]] = None
    url: Optional[str] = None
    sku: Optional[str] = None
    availability: Optional[bool] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "brand": self.brand,
            "price": self.price,
            "currency": self.currency,
            "description": self.description,
            "ingredients": self.ingredients,
            "features": self.features,
            "categories": self.categories,
            "images": self.images,
            "url": self.url,
            "sku": self.sku,
            "availability": self.availability,
            "rating": self.rating,
            "reviews_count": self.reviews_count
        }


@dataclass
class SEOData:
    """Standardized SEO data structure."""
    title: str
    meta_description: str
    keywords: List[str]
    url_slug: str
    h1: Optional[str] = None
    h2_tags: Optional[List[str]] = None
    alt_texts: Optional[List[str]] = None
    schema_markup: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "meta_description": self.meta_description,
            "keywords": self.keywords,
            "url_slug": self.url_slug,
            "h1": self.h1,
            "h2_tags": self.h2_tags,
            "alt_texts": self.alt_texts,
            "schema_markup": self.schema_markup
        }


# Text Processing Utilities
class TextCleaner:
    """Utility class for text cleaning and normalization."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep Turkish characters
        text = re.sub(r'[^\w\s\-.,!?()çÇğĞıİöÖşŞüÜ]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract all numbers from text."""
        if not text:
            return []
        
        # Pattern to match numbers (including decimals and Turkish comma notation)
        pattern = r'\d+[.,]?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                # Convert Turkish comma notation to decimal
                number_str = match.replace(',', '.')
                numbers.append(float(number_str))
            except ValueError:
                continue
        
        return numbers
    
    @staticmethod
    def extract_price(text: str) -> Optional[Tuple[float, str]]:
        """Extract price and currency from text."""
        if not text:
            return None
        
        # Common currency patterns
        currency_patterns = {
            r'₺': 'TRY',
            r'TL': 'TRY',
            r'\$': 'USD',
            r'€': 'EUR',
            r'£': 'GBP'
        }
        
        for symbol, currency in currency_patterns.items():
            # Pattern to match price with currency
            pattern = rf'({symbol})\s*(\d+[.,]?\d*)|(\d+[.,]?\d*)\s*({symbol})'
            match = re.search(pattern, text)
            
            if match:
                # Extract number
                price_text = match.group(2) or match.group(3)
                if price_text:
                    try:
                        price = float(price_text.replace(',', '.'))
                        return price, currency
                    except ValueError:
                        continue
        
        return None
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        # Decode common HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' '
        }
        
        for entity, replacement in html_entities.items():
            clean_text = clean_text.replace(entity, replacement)
        
        return clean_text.strip()
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to specified length."""
        if not text or len(text) <= max_length:
            return text
        
        # Try to truncate at word boundary
        truncated = text[:max_length - len(suffix)]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:  # If we can save at least 30% of the length
            truncated = truncated[:last_space]
        
        return truncated + suffix


class URLUtils:
    """Utility class for URL operations."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def build_absolute_url(url: str, base_url: str) -> str:
        """Build absolute URL from relative URL."""
        if not url:
            return ""
        if url.startswith(('http://', 'https://')):
            return url
        return urljoin(base_url, url)
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    @staticmethod
    def create_slug(text: str) -> str:
        """Create URL slug from text."""
        if not text:
            return ""
        
        # Convert to lowercase
        slug = text.lower()
        
        # Replace Turkish characters
        turkish_chars = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
        }
        
        for turkish, latin in turkish_chars.items():
            slug = slug.replace(turkish, latin)
        
        # Remove special characters and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
        
        return slug
    
    @staticmethod
    def get_url_parameters(url: str) -> Dict[str, str]:
        """Extract URL parameters."""
        try:
            from urllib.parse import parse_qs
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return {k: v[0] if v else '' for k, v in params.items()}
        except:
            return {}


class DataValidator:
    """Utility class for data validation."""
    
    @staticmethod
    def validate_product_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate product data structure."""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['title']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Required field '{field}' is missing or empty")
        
        # Recommended fields
        recommended_fields = ['brand', 'price', 'description']
        for field in recommended_fields:
            if not data.get(field):
                warnings.append(f"Recommended field '{field}' is missing")
        
        # Data type validation
        if data.get('price') and not isinstance(data['price'], (int, float)):
            try:
                float(data['price'])
            except (ValueError, TypeError):
                errors.append("Price must be a number")
        
        if data.get('ingredients') and not isinstance(data['ingredients'], list):
            errors.append("Ingredients must be a list")
        
        if data.get('rating') and not (0 <= float(data.get('rating', 0)) <= 5):
            errors.append("Rating must be between 0 and 5")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": max(0, 100 - len(errors) * 20 - len(warnings) * 5)
        }
    
    @staticmethod
    def validate_seo_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate SEO data structure."""
        errors = []
        warnings = []
        
        # Title validation
        title = data.get('title', '')
        if not title:
            errors.append("SEO title is required")
        elif len(title) > 60:
            warnings.append(f"SEO title is too long ({len(title)} chars, recommended: 50-60)")
        elif len(title) < 30:
            warnings.append(f"SEO title is too short ({len(title)} chars, recommended: 50-60)")
        
        # Meta description validation
        meta_desc = data.get('meta_description', '')
        if not meta_desc:
            errors.append("Meta description is required")
        elif len(meta_desc) > 160:
            warnings.append(f"Meta description is too long ({len(meta_desc)} chars, recommended: 150-160)")
        elif len(meta_desc) < 120:
            warnings.append(f"Meta description is too short ({len(meta_desc)} chars, recommended: 150-160)")
        
        # Keywords validation
        keywords = data.get('keywords', [])
        if not keywords:
            warnings.append("No keywords specified")
        elif len(keywords) > 10:
            warnings.append(f"Too many keywords ({len(keywords)}, recommended: 5-10)")
        
        # URL slug validation
        url_slug = data.get('url_slug', '')
        if not url_slug:
            warnings.append("URL slug is missing")
        elif len(url_slug) > 100:
            warnings.append(f"URL slug is too long ({len(url_slug)} chars)")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": max(0, 100 - len(errors) * 15 - len(warnings) * 3)
        }


class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    async def save_json(data: Union[Dict, List], filepath: str) -> bool:
        """Save data to JSON file asynchronously."""
        try:
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving JSON file {filepath}: {e}")
            return False
    
    @staticmethod
    async def load_json(filepath: str) -> Optional[Union[Dict, List]]:
        """Load data from JSON file asynchronously."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {e}")
            return None
    
    @staticmethod
    async def save_csv(data: List[Dict], filepath: str) -> bool:
        """Save data to CSV file asynchronously."""
        try:
            import pandas as pd
            
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to DataFrame and save
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            
            return True
        except Exception as e:
            logger.error(f"Error saving CSV file {filepath}: {e}")
            return False
    
    @staticmethod
    def get_unique_filename(filepath: str) -> str:
        """Generate unique filename if file already exists."""
        path = Path(filepath)
        counter = 1
        
        while path.exists():
            stem = path.stem
            if stem.endswith(f'_{counter-1}') and counter > 1:
                stem = stem[:-len(f'_{counter-1}')]
            
            new_name = f"{stem}_{counter}{path.suffix}"
            path = path.parent / new_name
            counter += 1
        
        return str(path)


class HashUtils:
    """Utility class for hashing operations."""
    
    @staticmethod
    def create_content_hash(content: str) -> str:
        """Create MD5 hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def create_url_hash(url: str) -> str:
        """Create hash for URL (useful for caching)."""
        return hashlib.sha256(url.encode('utf-8')).hexdigest()[:16]
    
    @staticmethod
    def create_data_signature(data: Dict[str, Any]) -> str:
        """Create signature for data dict."""
        # Sort keys to ensure consistent hashing
        sorted_data = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()[:12]


class DateTimeUtils:
    """Utility class for datetime operations."""
    
    @staticmethod
    def get_timestamp() -> str:
        """Get current UTC timestamp as ISO string."""
        return datetime.now(timezone.utc).isoformat()
    
    @staticmethod
    def get_unix_timestamp() -> int:
        """Get current Unix timestamp."""
        return int(datetime.now().timestamp())
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable format."""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


class CosmeticUtils:
    """Utility class for cosmetic-specific operations."""
    
    # Common cosmetic terms in Turkish and English
    COSMETIC_CATEGORIES = {
        'tr': [
            'makyaj', 'cilt bakımı', 'saç bakımı', 'parfüm', 'kişisel bakım',
            'fondöten', 'ruj', 'maskara', 'allık', 'kapatıcı', 'göz kalemi',
            'nemlendirici', 'temizleyici', 'tonik', 'serum', 'krem',
            'şampuan', 'saç kremi', 'saç maskesi'
        ],
        'en': [
            'makeup', 'skincare', 'haircare', 'fragrance', 'personal care',
            'foundation', 'lipstick', 'mascara', 'blush', 'concealer', 'eyeliner',
            'moisturizer', 'cleanser', 'toner', 'serum', 'cream',
            'shampoo', 'conditioner', 'hair mask'
        ]
    }
    
    SKIN_TYPES = ['normal', 'kuru', 'yağlı', 'karma', 'hassas', 'dry', 'oily', 'combination', 'sensitive']
    
    COSMETIC_BENEFITS = {
        'tr': [
            'nemlendirici', 'anti-aging', 'beyazlatıcı', 'güneş koruyucu',
            'akne karşıtı', 'leke giderici', 'sıkılaştırıcı', 'besleyici'
        ],
        'en': [
            'moisturizing', 'anti-aging', 'brightening', 'sun protection',
            'anti-acne', 'spot correcting', 'firming', 'nourishing'
        ]
    }
    
    @classmethod
    def extract_cosmetic_terms(cls, text: str, language: str = 'tr') -> List[str]:
        """Extract cosmetic-related terms from text."""
        if not text:
            return []
        
        text_lower = text.lower()
        found_terms = []
        
        # Check categories
        for term in cls.COSMETIC_CATEGORIES.get(language, []):
            if term in text_lower:
                found_terms.append(term)
        
        # Check benefits
        for term in cls.COSMETIC_BENEFITS.get(language, []):
            if term in text_lower:
                found_terms.append(term)
        
        # Check skin types
        for term in cls.SKIN_TYPES:
            if term in text_lower:
                found_terms.append(term)
        
        return list(set(found_terms))
    
    @classmethod
    def detect_skin_type_compatibility(cls, text: str) -> List[str]:
        """Detect skin type compatibility from product text."""
        if not text:
            return []
        
        text_lower = text.lower()
        compatible_types = []
        
        for skin_type in cls.SKIN_TYPES:
            if skin_type in text_lower:
                compatible_types.append(skin_type)
        
        return compatible_types
    
    @classmethod
    def generate_cosmetic_keywords(cls, product_data: Dict[str, Any]) -> List[str]:
        """Generate cosmetic-specific keywords from product data."""
        keywords = []
        
        # Extract from title
        title = product_data.get('title', '')
        if title:
            keywords.extend(cls.extract_cosmetic_terms(title))
        
        # Extract from description
        description = product_data.get('description', '')
        if description:
            keywords.extend(cls.extract_cosmetic_terms(description))
        
        # Add brand if available
        brand = product_data.get('brand', '')
        if brand:
            keywords.append(brand.lower())
        
        # Add categories
        categories = product_data.get('categories', [])
        if categories:
            keywords.extend([cat.lower() for cat in categories])
        
        return list(set(keywords))


# Async utilities
class AsyncUtils:
    """Utility class for async operations."""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float):
        """Run coroutine with timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    @staticmethod
    async def batch_process(
        items: List[Any],
        process_func,
        batch_size: int = 10,
        max_concurrent: int = 5
    ) -> List[Any]:
        """Process items in batches with concurrency control."""
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        
        async def process_with_semaphore(item):
            async with semaphore:
                return await process_func(item)
        
        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[process_with_semaphore(item) for item in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
        
        return results