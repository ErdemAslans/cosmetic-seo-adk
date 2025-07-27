from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class ProductData(BaseModel):
    """Product data model for cosmetic products"""
    url: HttpUrl
    site: str
    name: str
    brand: Optional[str] = None
    price: Optional[str] = None
    description: str
    ingredients: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    usage: Optional[str] = None
    reviews: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.now)


class SEOData(BaseModel):
    """SEO metadata for products"""
    product_url: HttpUrl
    keywords: List[str]
    primary_keyword: str
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    title: str = Field(..., max_length=60)
    meta_description: str = Field(..., max_length=160)
    slug: str
    focus_keyphrase: str
    keyword_density: Dict[str, float]
    quality_score: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.now)


class SiteConfig(BaseModel):
    """Configuration for e-commerce sites"""
    name: str
    base_url: HttpUrl
    category_paths: List[str]
    selectors: Dict[str, Union[str, List[str]]]
    rate_limit: float = 3.0
    max_pages: int = 100
    headers: Dict[str, str] = Field(default_factory=dict)


class AgentTask(BaseModel):
    """Task model for inter-agent communication"""
    id: str
    agent_name: str
    action: str
    data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retries: int = 0


class CosmeticTerms(BaseModel):
    """Cosmetic industry terms for analysis"""
    ingredients: List[str] = Field(default_factory=lambda: [
        "retinol", "vitamin c", "hyaluronic acid", "niacinamide", "salicylic acid",
        "glycolic acid", "peptides", "ceramides", "squalane", "bakuchiol",
        "zinc oxide", "titanium dioxide", "benzoyl peroxide", "tea tree oil",
        "aloe vera", "jojoba oil", "argan oil", "rosehip oil", "collagen"
    ])
    
    benefits: List[str] = Field(default_factory=lambda: [
        "moisturizing", "hydrating", "anti-aging", "anti-wrinkle", "brightening",
        "firming", "lifting", "smoothing", "clarifying", "purifying", "balancing",
        "soothing", "calming", "nourishing", "rejuvenating", "regenerating",
        "protecting", "repairing", "revitalizing", "mattifying", "plumping"
    ])
    
    product_types: List[str] = Field(default_factory=lambda: [
        "serum", "cream", "lotion", "gel", "oil", "mask", "cleanser", "toner",
        "essence", "emulsion", "ampoule", "balm", "mist", "spray", "scrub",
        "exfoliant", "peel", "treatment", "moisturizer", "sunscreen", "primer"
    ])
    
    skin_types: List[str] = Field(default_factory=lambda: [
        "dry", "oily", "combination", "sensitive", "normal", "acne-prone",
        "mature", "aging", "dull", "dehydrated", "problematic", "reactive"
    ])