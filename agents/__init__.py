"""
Cosmetic SEO Agents Package

This package provides a comprehensive multi-agent system for cosmetic e-commerce
SEO analysis and optimization. It includes base classes, utilities, and specialized
agents for web scraping, data analysis, SEO generation, and quality validation.

Architecture Overview:
- BaseTool: Foundation class for all tools
- Utilities: Common helper functions and data structures
- Configuration: Centralized configuration management
- ModernScraperAgent: Core web scraping functionality
- Specialized agents for analysis, SEO, and validation

Available Agents:
- ScoutAgent: Product URL discovery
- ModernScraperAgent: Advanced data extraction (Playwright-based)
- AnalyzerAgent: Data cleaning and analysis
- SEOAgent: SEO metadata generation
- QualityAgent: SEO quality validation
- StorageAgent: Data persistence

Version: 2.0.0
"""

# Note: base_agent.py and base_scraper_agent.py have been consolidated
# Core functionality moved to utils.py and individual agent files

from .base_tool import (
    BaseTool,
    BaseDataValidationTool,
    BaseAnalysisTool,
    BaseScrapingTool,
    BaseStorageTool,
    BaseTransformTool,
    ToolRegistry,
    tool_registry,
    create_direct_tool_function,
    tool_error_handler
)

from .utils import (
    BaseAgent,
    RetryMixin,
    error_handler,
    ProductData,
    SEOData,
    TextCleaner,
    URLUtils,
    DataValidator,
    FileUtils,
    HashUtils,
    DateTimeUtils,
    CosmeticUtils,
    AsyncUtils
)

from .config import (
    ScrapingConfig,
    SiteConfig,
    AIConfig,
    DatabaseConfig,
    FileConfig,
    SiteConfigurations,
    EnvironmentConfig,
    SystemConfig,
    config  # Global configuration instance
)

# Version information
__version__ = "2.0.0"
__author__ = "Cosmetic SEO Team"
__description__ = "Multi-agent system for cosmetic e-commerce SEO analysis"

# Package metadata
__all__ = [
    # Base classes
    "BaseAgent",
    "BaseTool",
    
    # Mixins
    "RetryMixin",
    
    # Tool base classes
    "BaseDataValidationTool",
    "BaseAnalysisTool", 
    "BaseScrapingTool",
    "BaseStorageTool",
    "BaseTransformTool",
    
    # Tool registry
    "ToolRegistry",
    "tool_registry",
    "create_direct_tool_function",
    
    # Decorators
    "error_handler",
    "tool_error_handler",
    
    # Data structures
    "ProductData",
    "SEOData",
    
    # Utilities
    "TextCleaner",
    "URLUtils", 
    "DataValidator",
    "FileUtils",
    "HashUtils",
    "DateTimeUtils",
    "CosmeticUtils",
    "AsyncUtils",
    
    # Configuration
    "ScrapingConfig",
    "SiteConfig",
    "AIConfig", 
    "DatabaseConfig",
    "FileConfig",
    "SiteConfigurations",
    "EnvironmentConfig",
    "SystemConfig",
    "config"
]

# Module-level configuration
import logging

def setup_logging(level=logging.INFO):
    """Setup package-wide logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set specific logger levels
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

# Auto-setup logging on import
setup_logging()

def get_package_info():
    """Get package information."""
    return {
        "name": "cosmetic-seo-agents",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "python_version": ">=3.8",
        "dependencies": [
            "google-adk",
            "selenium", 
            "playwright",
            "beautifulsoup4",
            "asyncio",
            "aiohttp",
            "pandas",
            "numpy",
            "scikit-learn",
            "spacy",
            "nltk",
            "asyncpg",
            "aiosqlite"
        ],
        "agents": [
            "ScoutAgent",
            "ModernScraperAgent",
            "AnalyzerAgent", 
            "SEOAgent",
            "QualityAgent",
            "StorageAgent"
        ],
        "tools": [
            "BaseTool",
            "BaseDataValidationTool",
            "BaseAnalysisTool",
            "BaseScrapingTool", 
            "BaseStorageTool",
            "BaseTransformTool"
        ],
        "supported_sites": [
            "Trendyol",
            "Gratis", 
            "Sephora TR",
            "Rossmann"
        ],
        "features": [
            "Multi-agent architecture",
            "AI-powered data analysis",
            "Advanced web scraping",
            "SEO optimization",
            "Quality validation",
            "Async/concurrent processing",
            "Configurable and extensible"
        ]
    }

def validate_environment():
    """Validate environment and dependencies."""
    errors = []
    warnings = []
    
    try:
        import google.adk
    except ImportError:
        errors.append("google-adk not installed")
    
    try:
        import selenium
    except ImportError:
        warnings.append("selenium not available - ScraperAgent will be limited")
    
    try:
        import playwright
    except ImportError:
        warnings.append("playwright not available - ModernScraperAgent will be limited")
    
    try:
        import pandas
    except ImportError:
        warnings.append("pandas not available - some data export features will be limited")
    
    try:
        import spacy
    except ImportError:
        warnings.append("spacy not available - advanced NLP features will be limited")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

# Validate environment on import
_env_validation = validate_environment()
if not _env_validation["is_valid"]:
    logger = logging.getLogger(__name__)
    logger.error(f"Environment validation failed: {_env_validation['errors']}")
    for warning in _env_validation["warnings"]:
        logger.warning(warning)

# Export validation results
environment_status = _env_validation