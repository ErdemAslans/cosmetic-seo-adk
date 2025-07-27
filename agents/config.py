"""
Configuration Module for Cosmetic SEO Project

This module provides centralized configuration management for all agents,
including site-specific configurations, scraping parameters, and system settings.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScrapingConfig:
    """Configuration for web scraping operations."""
    
    # Browser settings
    headless: bool = True
    window_width: int = 1920
    window_height: int = 1080
    user_agent_rotation: bool = True
    
    # Timing settings
    page_load_timeout: int = 30
    element_wait_timeout: int = 10
    request_delay_min: float = 1.0
    request_delay_max: float = 3.0
    
    # Retry settings
    max_retries: int = 3
    retry_delay: float = 2.0
    backoff_factor: float = 2.0
    
    # SSL and security
    verify_ssl: bool = False
    ignore_https_errors: bool = True
    
    # Performance settings
    max_concurrent_requests: int = 5
    batch_size: int = 10
    
    # Anti-bot settings
    random_delays: bool = True
    rotate_user_agents: bool = True
    use_proxy: bool = False
    proxy_list: List[str] = field(default_factory=list)


@dataclass
class SiteConfig:
    """Configuration for specific e-commerce sites."""
    
    name: str
    domains: List[str]
    base_url: str
    
    # Selectors for different data types
    selectors: Dict[str, Any] = field(default_factory=dict)
    
    # Site-specific settings
    requires_javascript: bool = True
    has_infinite_scroll: bool = False
    requires_cookies: bool = False
    
    # Rate limiting
    requests_per_minute: int = 60
    concurrent_requests: int = 3
    
    # Special handling
    custom_headers: Dict[str, str] = field(default_factory=dict)
    login_required: bool = False
    
    def get_selector(self, data_type: str, fallback: Optional[str] = None) -> Optional[str]:
        """Get selector for specific data type."""
        return self.selectors.get(data_type, fallback)
    
    def get_selectors_list(self, data_type: str) -> List[str]:
        """Get list of selectors for data type (for fallback strategies)."""
        selector = self.selectors.get(data_type)
        if isinstance(selector, list):
            return selector
        elif isinstance(selector, str):
            return [selector]
        return []


@dataclass
class AIConfig:
    """Configuration for AI model settings."""
    
    # Model settings
    default_model: str = "gemini-2.0-flash-thinking-exp"
    fallback_model: str = "gemini-2.0-flash-thinking-exp"
    
    # Generation settings
    temperature: float = 0.3
    max_output_tokens: int = 8192
    
    # Safety settings
    enable_safety_filters: bool = True
    
    # Language settings
    default_language: str = "tr"
    supported_languages: List[str] = field(default_factory=lambda: ["tr", "en"])


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    
    # PostgreSQL settings (primary)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "cosmetic_seo"
    postgres_username: str = "postgres"
    postgres_password: str = ""
    
    # SQLite settings (fallback)
    sqlite_path: str = "data/cosmetic_seo.db"
    
    # Connection settings
    max_connections: int = 20
    connection_timeout: int = 30
    
    def get_postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
    
    def get_sqlite_url(self) -> str:
        """Get SQLite connection URL."""
        return f"sqlite:///{self.sqlite_path}"


@dataclass
class FileConfig:
    """Configuration for file operations."""
    
    # Directory paths
    data_dir: str = "data"
    web_results_dir: str = "data/web_results"
    logs_dir: str = "logs"
    cache_dir: str = "cache"
    
    # File formats
    default_export_format: str = "json"
    supported_formats: List[str] = field(default_factory=lambda: ["json", "csv", "xlsx"])
    
    # File naming
    timestamp_format: str = "%Y%m%d_%H%M%S"
    max_filename_length: int = 255
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.data_dir,
            self.web_results_dir,
            self.logs_dir,
            self.cache_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


class SiteConfigurations:
    """Centralized site configurations for all supported e-commerce sites."""
    
    @staticmethod
    def get_trendyol_config() -> SiteConfig:
        """Get Trendyol site configuration."""
        return SiteConfig(
            name="trendyol",
            domains=["trendyol.com", "www.trendyol.com"],
            base_url="https://www.trendyol.com",
            selectors={
                "product_links": [
                    ".p-card-wrppr a",
                    ".product-item a",
                    "[data-testid='product-card'] a"
                ],
                "product_title": [
                    ".pr-new-br span",
                    "h1.pr-new-br",
                    "[data-testid='product-title']",
                    ".product-name h1"
                ],
                "brand": [
                    ".product-brand a",
                    ".pr-new-br a",
                    "[data-testid='product-brand']"
                ],
                "price": [
                    ".prc-dsc",
                    ".price-current",
                    "[data-testid='price-current']"
                ],
                "description": [
                    ".product-detail-description",
                    ".detail-desc-item",
                    "[data-testid='product-description']"
                ],
                "images": [
                    ".product-images img",
                    ".gallery-img img",
                    "[data-testid='product-image']"
                ],
                "rating": [
                    ".rating-score",
                    ".star-w",
                    "[data-testid='product-rating']"
                ],
                "reviews_count": [
                    ".rating-text",
                    ".reviews-count",
                    "[data-testid='reviews-count']"
                ]
            },
            has_infinite_scroll=True,
            requests_per_minute=30,
            concurrent_requests=2
        )
    
    @staticmethod
    def get_gratis_config() -> SiteConfig:
        """Get Gratis site configuration."""
        return SiteConfig(
            name="gratis",
            domains=["gratis.com", "www.gratis.com"],
            base_url="https://www.gratis.com",
            selectors={
                "product_links": [
                    ".product-item a",
                    ".productItem a",
                    "[data-testid='product-link']"
                ],
                "product_title": [
                    ".product-name h1",
                    ".productName",
                    "[data-testid='product-title']"
                ],
                "brand": [
                    ".product-brand",
                    ".brand-name",
                    "[data-testid='product-brand']"
                ],
                "price": [
                    ".price-current",
                    ".currentPrice",
                    "[data-testid='current-price']"
                ],
                "description": [
                    ".product-description",
                    ".productDescription",
                    "[data-testid='product-description']"
                ],
                "images": [
                    ".product-gallery img",
                    ".productImages img",
                    "[data-testid='product-image']"
                ],
                "ingredients": [
                    ".ingredients-list",
                    ".product-ingredients",
                    "[data-testid='ingredients']"
                ]
            },
            requests_per_minute=40,
            concurrent_requests=3
        )
    
    @staticmethod
    def get_sephora_config() -> SiteConfig:
        """Get Sephora TR site configuration."""
        return SiteConfig(
            name="sephora_tr",
            domains=["sephora.com.tr", "www.sephora.com.tr"],
            base_url="https://www.sephora.com.tr",
            selectors={
                "product_links": [
                    ".product-tile a",
                    ".ProductTile a",
                    "[data-testid='product-tile']"
                ],
                "product_title": [
                    ".product-name h1",
                    ".ProductName",
                    "[data-testid='product-name']"
                ],
                "brand": [
                    ".product-brand a",
                    ".BrandName",
                    "[data-testid='brand-name']"
                ],
                "price": [
                    ".price",
                    ".Price",
                    "[data-testid='price']"
                ],
                "description": [
                    ".product-details",
                    ".ProductDetails",
                    "[data-testid='product-details']"
                ],
                "images": [
                    ".product-images img",
                    ".ProductImages img",
                    "[data-testid='product-image']"
                ],
                "rating": [
                    ".rating-stars",
                    ".RatingStars",
                    "[data-testid='rating']"
                ]
            },
            requires_cookies=True,
            requests_per_minute=50,
            concurrent_requests=3
        )
    
    @staticmethod
    def get_rossmann_config() -> SiteConfig:
        """Get Rossmann site configuration."""
        return SiteConfig(
            name="rossmann",
            domains=["rossmann.com.tr", "www.rossmann.com.tr"],
            base_url="https://www.rossmann.com.tr",
            selectors={
                "product_links": [
                    ".product-card a",
                    ".productCard a",
                    "[data-testid='product-card']"
                ],
                "product_title": [
                    ".product-title h1",
                    ".productTitle",
                    "[data-testid='product-title']"
                ],
                "brand": [
                    ".brand-name",
                    ".productBrand",
                    "[data-testid='brand']"
                ],
                "price": [
                    ".current-price",
                    ".currentPrice",
                    "[data-testid='price']"
                ],
                "description": [
                    ".product-info",
                    ".productInfo",
                    "[data-testid='description']"
                ],
                "images": [
                    ".product-image img",
                    ".productImage img",
                    "[data-testid='image']"
                ]
            },
            requests_per_minute=45,
            concurrent_requests=3
        )
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, SiteConfig]:
        """Get all site configurations."""
        return {
            "trendyol": cls.get_trendyol_config(),
            "gratis": cls.get_gratis_config(),
            "sephora_tr": cls.get_sephora_config(),
            "rossmann": cls.get_rossmann_config()
        }


class EnvironmentConfig:
    """Environment-based configuration management."""
    
    def __init__(self):
        self.load_from_env()
    
    def load_from_env(self):
        """Load configuration from environment variables."""
        # Database settings
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_database = os.getenv("POSTGRES_DATABASE", "cosmetic_seo")
        self.postgres_username = os.getenv("POSTGRES_USERNAME", "postgres")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "")
        
        # AI settings
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.default_model = os.getenv("DEFAULT_MODEL", "gemini-2.0-flash-thinking-exp")
        
        # Scraping settings
        self.headless_browser = os.getenv("HEADLESS_BROWSER", "true").lower() == "true"
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "logs/cosmetic_seo.log")
        
        # Development settings
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.development_mode = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"


class SystemConfig:
    """Main system configuration class."""
    
    def __init__(self):
        self.env = EnvironmentConfig()
        self.scraping = ScrapingConfig(
            headless=self.env.headless_browser,
            max_concurrent_requests=self.env.max_concurrent_requests
        )
        self.ai = AIConfig(
            default_model=self.env.default_model
        )
        self.database = DatabaseConfig(
            postgres_host=self.env.postgres_host,
            postgres_port=self.env.postgres_port,
            postgres_database=self.env.postgres_database,
            postgres_username=self.env.postgres_username,
            postgres_password=self.env.postgres_password
        )
        self.files = FileConfig()
        self.sites = SiteConfigurations.get_all_configs()
        
        # Ensure directories exist
        self.files.ensure_directories()
    
    def get_site_config(self, site_name: str) -> Optional[SiteConfig]:
        """Get configuration for specific site."""
        return self.sites.get(site_name.lower())
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.env.debug_mode
    
    def is_development_mode(self) -> bool:
        """Check if development mode is enabled."""
        return self.env.development_mode
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "scraping": {
                "headless": self.scraping.headless,
                "max_concurrent_requests": self.scraping.max_concurrent_requests,
                "max_retries": self.scraping.max_retries
            },
            "ai": {
                "default_model": self.ai.default_model,
                "temperature": self.ai.temperature,
                "max_output_tokens": self.ai.max_output_tokens
            },
            "database": {
                "postgres_host": self.database.postgres_host,
                "postgres_port": self.database.postgres_port,
                "postgres_database": self.database.postgres_database
            },
            "files": {
                "data_dir": self.files.data_dir,
                "web_results_dir": self.files.web_results_dir,
                "logs_dir": self.files.logs_dir
            },
            "sites": list(self.sites.keys()),
            "debug_mode": self.is_debug_mode(),
            "development_mode": self.is_development_mode()
        }


# Global configuration instance
config = SystemConfig()