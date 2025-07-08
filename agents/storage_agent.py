"""
Storage Agent - Data Persistence Agent built with Google ADK
Stores validated cosmetic product and SEO data to multiple formats
"""

import json
import csv
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
# Using psycopg2 instead of asyncpg for database connections
# import asyncpg
import pandas as pd
from loguru import logger
import aiofiles

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from config.models import ProductData, SEOData


class DatabaseStorageTool(BaseTool):
    """Tool for storing data to PostgreSQL database"""
    
    def __init__(self, database_url: str):
        super().__init__(
            name="database_storage",
            description="Store product and SEO data to PostgreSQL database",
            is_long_running=True
        )
        self.database_url = database_url
        self.pool = None
    
    async def _get_pool(self):
        """Get database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.database_url)
            await self._initialize_database()
        return self.pool
    
    async def _initialize_database(self):
        """Initialize database tables"""
        async with self.pool.acquire() as conn:
            # Products table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    site TEXT NOT NULL,
                    name TEXT NOT NULL,
                    brand TEXT,
                    price TEXT,
                    description TEXT,
                    ingredients TEXT[],
                    features TEXT[],
                    usage TEXT,
                    reviews TEXT[],
                    images TEXT[],
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # SEO data table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS seo_data (
                    id SERIAL PRIMARY KEY,
                    product_url TEXT REFERENCES products(url) ON DELETE CASCADE,
                    keywords TEXT[],
                    primary_keyword TEXT,
                    secondary_keywords TEXT[],
                    long_tail_keywords TEXT[],
                    title TEXT,
                    meta_description TEXT,
                    slug TEXT UNIQUE,
                    focus_keyphrase TEXT,
                    keyword_density JSONB,
                    quality_score FLOAT,
                    validation_status TEXT,
                    generated_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Quality validation table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS quality_validations (
                    id SERIAL PRIMARY KEY,
                    product_url TEXT REFERENCES products(url) ON DELETE CASCADE,
                    is_valid BOOLEAN,
                    quality_score FLOAT,
                    errors TEXT[],
                    warnings TEXT[],
                    recommendations TEXT[],
                    best_practices_score FLOAT,
                    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_products_url ON products(url);
                CREATE INDEX IF NOT EXISTS idx_products_site ON products(site);
                CREATE INDEX IF NOT EXISTS idx_seo_primary_keyword ON seo_data(primary_keyword);
                CREATE INDEX IF NOT EXISTS idx_seo_slug ON seo_data(slug);
                CREATE INDEX IF NOT EXISTS idx_quality_score ON seo_data(quality_score);
            ''')
    
    async def __call__(self, product_data: Dict[str, Any], seo_data: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data to database"""
        try:
            pool = await self._get_pool()
            product = ProductData(**product_data)
            
            # Parse SEO data carefully
            seo_dict = seo_data.copy()
            if 'product_url' not in seo_dict:
                seo_dict['product_url'] = str(product.url)
            if 'generated_at' not in seo_dict:
                seo_dict['generated_at'] = datetime.now()
            
            seo = SEOData(**seo_dict)
            
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # Store product data
                    await conn.execute('''
                        INSERT INTO products (url, site, name, brand, price, description, 
                                            ingredients, features, usage, reviews, images, scraped_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        ON CONFLICT (url) DO UPDATE SET
                            name = EXCLUDED.name,
                            brand = EXCLUDED.brand,
                            price = EXCLUDED.price,
                            description = EXCLUDED.description,
                            ingredients = EXCLUDED.ingredients,
                            features = EXCLUDED.features,
                            usage = EXCLUDED.usage,
                            reviews = EXCLUDED.reviews,
                            images = EXCLUDED.images,
                            scraped_at = EXCLUDED.scraped_at,
                            updated_at = CURRENT_TIMESTAMP
                    ''', 
                    str(product.url), product.site, product.name, 
                    product.brand, product.price, product.description,
                    product.ingredients, product.features, product.usage,
                    product.reviews[:10], product.images[:5], product.scraped_at
                    )
                    
                    # Store SEO data
                    quality_score = validation_data.get("quality_score", 0.0)
                    validation_status = "valid" if validation_data.get("is_valid", False) else "invalid"
                    
                    await conn.execute('''
                        INSERT INTO seo_data (product_url, keywords, primary_keyword, secondary_keywords,
                                            long_tail_keywords, title, meta_description, slug,
                                            focus_keyphrase, keyword_density, quality_score, 
                                            validation_status, generated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        ON CONFLICT (slug) DO UPDATE SET
                            keywords = EXCLUDED.keywords,
                            primary_keyword = EXCLUDED.primary_keyword,
                            secondary_keywords = EXCLUDED.secondary_keywords,
                            long_tail_keywords = EXCLUDED.long_tail_keywords,
                            title = EXCLUDED.title,
                            meta_description = EXCLUDED.meta_description,
                            focus_keyphrase = EXCLUDED.focus_keyphrase,
                            keyword_density = EXCLUDED.keyword_density,
                            quality_score = EXCLUDED.quality_score,
                            validation_status = EXCLUDED.validation_status,
                            generated_at = EXCLUDED.generated_at,
                            updated_at = CURRENT_TIMESTAMP
                    ''',
                    str(seo.product_url), seo.keywords[:20], seo.primary_keyword,
                    seo.secondary_keywords, seo.long_tail_keywords, seo.title,
                    seo.meta_description, seo.slug, seo.focus_keyphrase,
                    json.dumps(seo.keyword_density), quality_score, 
                    validation_status, seo.generated_at
                    )
                    
                    # Store quality validation data
                    await conn.execute('''
                        INSERT INTO quality_validations (product_url, is_valid, quality_score,
                                                        errors, warnings, recommendations, best_practices_score)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ''',
                    str(product.url), validation_data.get("is_valid", False),
                    validation_data.get("quality_score", 0.0),
                    validation_data.get("errors", []),
                    validation_data.get("warnings", []),
                    validation_data.get("recommendations", []),
                    validation_data.get("best_practices_score", 0.0)
                    )
            
            return {"success": True, "message": "Data stored to database successfully"}
            
        except Exception as e:
            logger.error(f"Database storage error: {e}")
            return {"error": str(e)}


class FileStorageTool(BaseTool):
    """Tool for storing data to files (CSV, JSON)"""
    
    def __init__(self, data_dir: str = "data"):
        super().__init__(
            name="file_storage",
            description="Store product and SEO data to CSV and JSON files"
        )
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "products").mkdir(exist_ok=True)
        (self.data_dir / "exports").mkdir(exist_ok=True)
        
        self.csv_path = self.data_dir / "exports" / "cosmetic_products_seo.csv"
        self.csv_headers_written = self.csv_path.exists()
    
    async def __call__(self, product_data: Dict[str, Any], seo_data: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data to files"""
        try:
            product = ProductData(**product_data)
            
            # Save to CSV
            await self._save_to_csv(product, seo_data, validation_data)
            
            # Save to JSON
            json_path = await self._save_to_json(product, seo_data, validation_data)
            
            return {
                "success": True,
                "csv_path": str(self.csv_path),
                "json_path": str(json_path)
            }
            
        except Exception as e:
            logger.error(f"File storage error: {e}")
            return {"error": str(e)}
    
    async def _save_to_csv(self, product: ProductData, seo_data: Dict[str, Any], validation_data: Dict[str, Any]):
        """Save data to CSV file"""
        csv_row = {
            "url": str(product.url),
            "site": product.site,
            "product_name": product.name,
            "brand": product.brand or "",
            "price": product.price or "",
            "primary_keyword": seo_data.get("primary_keyword", ""),
            "seo_keywords": ", ".join(seo_data.get("keywords", [])[:10]),
            "seo_title": seo_data.get("title", ""),
            "meta_description": seo_data.get("meta_description", ""),
            "slug": seo_data.get("slug", ""),
            "focus_keyphrase": seo_data.get("focus_keyphrase", ""),
            "quality_score": validation_data.get("quality_score", 0.0),
            "is_valid": validation_data.get("is_valid", False),
            "scraped_at": product.scraped_at.isoformat()
        }
        
        fieldnames = list(csv_row.keys())
        
        async with aiofiles.open(self.csv_path, mode='a', newline='', encoding='utf-8') as f:
            if not self.csv_headers_written:
                await f.write(",".join(fieldnames) + "\n")
                self.csv_headers_written = True
            
            # Escape quotes in values
            csv_values = [str(csv_row[field]).replace('"', '""') for field in fieldnames]
            csv_line = ",".join([f'"{value}"' for value in csv_values])
            await f.write(csv_line + "\n")
    
    async def _save_to_json(self, product: ProductData, seo_data: Dict[str, Any], validation_data: Dict[str, Any]) -> Path:
        """Save data to individual JSON file"""
        slug = seo_data.get("slug", f"product_{int(datetime.now().timestamp())}")
        filename = f"{slug}.json"
        filepath = self.data_dir / "products" / filename
        
        json_data = {
            "product": product.model_dump(),
            "seo": seo_data,
            "validation": validation_data,
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "system_version": "cosmetic-seo-adk-1.0"
            }
        }
        
        # Convert URL objects to strings for JSON serialization
        json_data["product"]["url"] = str(product.url)
        if "product_url" in json_data["seo"]:
            json_data["seo"]["product_url"] = str(json_data["seo"]["product_url"])
        
        async with aiofiles.open(filepath, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps(json_data, indent=2, ensure_ascii=False, default=str))
        
        return filepath


class ReportingTool(BaseTool):
    """Tool for generating summary reports"""
    
    def __init__(self, database_url: str):
        super().__init__(
            name="generate_report",
            description="Generate summary reports about stored data",
            is_long_running=True
        )
        self.database_url = database_url
        self.pool = None
    
    async def _get_pool(self):
        """Get database connection pool"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.database_url)
        return self.pool
    
    async def __call__(self, report_type: str = "summary") -> Dict[str, Any]:
        """Generate report"""
        try:
            pool = await self._get_pool()
            
            async with pool.acquire() as conn:
                # Basic statistics
                total_products = await conn.fetchval("SELECT COUNT(*) FROM products")
                total_seo_entries = await conn.fetchval("SELECT COUNT(*) FROM seo_data")
                valid_entries = await conn.fetchval("SELECT COUNT(*) FROM seo_data WHERE validation_status = 'valid'")
                
                # Site breakdown
                sites_data = await conn.fetch('''
                    SELECT site, COUNT(*) as count 
                    FROM products 
                    GROUP BY site 
                    ORDER BY count DESC
                ''')
                
                # Quality metrics
                avg_quality_score = await conn.fetchval('''
                    SELECT AVG(quality_score) 
                    FROM seo_data 
                    WHERE quality_score IS NOT NULL
                ''')
                
                # Top keywords
                top_keywords = await conn.fetch('''
                    SELECT primary_keyword, COUNT(*) as count 
                    FROM seo_data 
                    WHERE primary_keyword IS NOT NULL
                    GROUP BY primary_keyword 
                    ORDER BY count DESC 
                    LIMIT 20
                ''')
                
                # Quality distribution
                quality_distribution = await conn.fetch('''
                    SELECT 
                        CASE 
                            WHEN quality_score >= 90 THEN 'Excellent (90-100)'
                            WHEN quality_score >= 80 THEN 'Good (80-89)'
                            WHEN quality_score >= 70 THEN 'Fair (70-79)'
                            WHEN quality_score >= 60 THEN 'Poor (60-69)'
                            ELSE 'Very Poor (<60)'
                        END as quality_range,
                        COUNT(*) as count
                    FROM seo_data
                    WHERE quality_score IS NOT NULL
                    GROUP BY quality_range
                    ORDER BY MIN(quality_score) DESC
                ''')
            
            return {
                "total_products": total_products,
                "total_seo_entries": total_seo_entries,
                "valid_entries": valid_entries,
                "validation_rate": round((valid_entries / total_seo_entries) * 100, 1) if total_seo_entries > 0 else 0,
                "sites_breakdown": [dict(row) for row in sites_data],
                "average_quality_score": round(float(avg_quality_score), 2) if avg_quality_score else 0,
                "top_keywords": [dict(row) for row in top_keywords],
                "quality_distribution": [dict(row) for row in quality_distribution],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return {"error": str(e)}


class StorageAgent(LlmAgent):
    """Storage Agent for persisting validated data using Google ADK"""
    
    def __init__(self, database_url: str, data_dir: str = "data"):
        tools = [
            DatabaseStorageTool(database_url),
            FileStorageTool(data_dir),
            ReportingTool(database_url)
        ]
        
        super().__init__(
            name="storage_agent",
            model="gemini-1.5-pro-latest",
            tools=tools,
            instruction="""
            You are a Storage Agent specialized in persisting validated cosmetic product and SEO data.
            
            Your primary responsibilities:
            1. Store validated product and SEO data to multiple storage formats
            2. Maintain data integrity and consistency across storage systems
            3. Generate comprehensive reports about stored data
            4. Ensure data is properly indexed and searchable
            5. Handle storage errors gracefully and provide backup options
            
            For each storage request:
            1. Use database_storage tool to store data in PostgreSQL
            2. Use file_storage tool to create CSV and JSON exports
            3. Validate successful storage across all formats
            4. Generate storage confirmation with file paths
            
            Storage Formats:
            - PostgreSQL: Structured relational storage with indexing
            - CSV: Export format for analysis and reporting
            - JSON: Individual product files for detailed records
            
            Data Validation:
            - Ensure all required fields are present
            - Validate data types and constraints
            - Handle duplicate entries appropriately
            - Maintain referential integrity
            
            Only store data that has passed quality validation to maintain high data standards.
            """
        )
    
    async def process_storage_request(self, product_data: Dict[str, Any], seo_data: Dict[str, Any], validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a data storage request"""
        try:
            # Check if data passed quality validation
            is_valid = validation_data.get("is_valid", False)
            quality_score = validation_data.get("quality_score", 0)
            
            if not is_valid and quality_score < 60:
                return {
                    "error": "Data quality too low for storage",
                    "quality_score": quality_score,
                    "recommendation": "Improve data quality before storage"
                }
            
            prompt = f"""
            Store validated cosmetic product and SEO data:
            Product Data: {product_data}
            SEO Data: {seo_data}
            Validation Data: {validation_data}
            
            Please perform comprehensive data storage:
            
            1. Store to database using database_storage tool:
               - Save product information to products table
               - Save SEO data to seo_data table
               - Save validation results to quality_validations table
               - Ensure referential integrity
            
            2. Store to files using file_storage tool:
               - Append to CSV export file for analysis
               - Create individual JSON file for detailed record
               - Ensure proper file organization
            
            3. Confirm successful storage:
               - Verify database storage completion
               - Confirm file creation
               - Provide storage paths and references
            
            Return comprehensive storage confirmation with all storage locations.
            """
            
            response = await self.run_async(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Storage Agent error: {e}")
            return {"error": str(e)}
    
    async def generate_summary_report(self) -> Dict[str, Any]:
        """Generate a summary report of stored data"""
        try:
            prompt = """
            Generate a comprehensive summary report of all stored cosmetic product data.
            
            Use the generate_report tool to create a detailed report including:
            - Total number of products and SEO entries
            - Validation rates and quality metrics
            - Site-wise breakdown of products
            - Top performing keywords
            - Quality score distribution
            - Processing statistics
            
            Provide insights and recommendations based on the data.
            """
            
            response = await self.run_async(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return {"error": str(e)}


# Agent factory function for ADK orchestration
def create_storage_agent(database_url: str, data_dir: str = "data") -> StorageAgent:
    """Factory function to create Storage Agent instance"""
    return StorageAgent(database_url, data_dir)