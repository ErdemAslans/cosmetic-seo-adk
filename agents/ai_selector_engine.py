"""
🧠 AI-POWERED SELECTOR ADAPTATION ENGINE - Production-Ready
Self-learning selector system that adapts to site changes automatically
Specialized for Turkish cosmetic e-commerce sites with ML-powered pattern recognition
"""

import asyncio
import json
import hashlib
import re
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import aiofiles
from playwright.async_api import Page
from bs4 import BeautifulSoup
from loguru import logger
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict, Counter
import pickle


@dataclass
class SelectorPattern:
    """Represents a CSS selector pattern with metadata"""
    selector: str
    field_name: str
    site_name: str
    success_rate: float
    last_used: datetime
    usage_count: int
    pattern_type: str  # 'css', 'xpath', 'text_pattern', 'ml_generated'
    confidence_score: float
    extraction_quality: float
    context_hash: str  # Hash of surrounding HTML structure


@dataclass  
class ExtractionResult:
    """Result of a data extraction attempt"""
    success: bool
    data: Any
    selector_used: str
    extraction_time: float
    quality_score: float
    error_message: Optional[str] = None


class HTMLPatternAnalyzer:
    """Advanced HTML pattern analysis for intelligent selector generation"""
    
    def __init__(self):
        self.common_cosmetic_patterns = {
            'product_name': [
                r'product[_-]?name',
                r'title',
                r'product[_-]?title',
                r'name',
                r'item[_-]?name'
            ],
            'brand': [
                r'brand',
                r'manufacturer',
                r'maker',
                r'vendor',
                r'company'
            ],
            'price': [
                r'price',
                r'cost',
                r'amount',
                r'value',
                r'money',
                r'currency'
            ],
            'description': [
                r'description',
                r'desc',
                r'details',
                r'info',
                r'content',
                r'summary'
            ],
            'ingredients': [
                r'ingredients?',
                r'içerik',
                r'composition',
                r'formula',
                r'components'
            ]
        }
        
        self.turkish_field_patterns = {
            'product_name': ['ürün', 'adı', 'isim', 'başlık'],
            'brand': ['marka', 'üretici', 'firma'],
            'price': ['fiyat', 'tutar', 'ücret', 'para'],
            'description': ['açıklama', 'detay', 'bilgi', 'tanım'],
            'ingredients': ['içerik', 'bileşen', 'madde']
        }
    
    def analyze_html_structure(self, html: str, target_field: str) -> List[str]:
        """Analyze HTML structure to generate potential selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        candidate_selectors = []
        
        # 1. Attribute-based detection
        for pattern in self.common_cosmetic_patterns.get(target_field, []):
            # Class-based selectors
            elements = soup.find_all(class_=re.compile(pattern, re.I))
            for elem in elements:
                classes = ' '.join(elem.get('class', []))
                candidate_selectors.append(f".{classes.replace(' ', '.')}")
            
            # ID-based selectors
            elements = soup.find_all(id=re.compile(pattern, re.I))
            for elem in elements:
                candidate_selectors.append(f"#{elem.get('id')}")
            
            # Data attribute selectors
            elements = soup.find_all(attrs={re.compile(r'data-.*'): re.compile(pattern, re.I)})
            for elem in elements:
                for attr, value in elem.attrs.items():
                    if attr.startswith('data-') and re.search(pattern, str(value), re.I):
                        candidate_selectors.append(f"[{attr}='{value}']")
        
        # 2. Turkish pattern detection
        turkish_patterns = self.turkish_field_patterns.get(target_field, [])
        for tr_pattern in turkish_patterns:
            elements = soup.find_all(class_=re.compile(tr_pattern, re.I))
            for elem in elements:
                classes = ' '.join(elem.get('class', []))
                if classes:
                    candidate_selectors.append(f".{classes.replace(' ', '.')}")
        
        # 3. Structural pattern analysis
        if target_field == 'product_name':
            # Look for h1, h2 tags in product context
            headers = soup.find_all(['h1', 'h2', 'h3'])
            for header in headers:
                if self._is_likely_product_name(header.get_text()):
                    candidate_selectors.extend(self._generate_selector_variations(header))
        
        elif target_field == 'price':
            # Look for price patterns
            price_elements = soup.find_all(text=re.compile(r'[₺$€]\s*\d+|[\d.,]+\s*[₺$€]|[\d.,]+\s*TL'))
            for elem in price_elements:
                if elem.parent:
                    candidate_selectors.extend(self._generate_selector_variations(elem.parent))
        
        # 4. Context-aware selectors
        candidate_selectors.extend(self._generate_contextual_selectors(soup, target_field))
        
        # Remove duplicates and sort by potential effectiveness
        unique_selectors = list(set(candidate_selectors))
        return self._rank_selectors(unique_selectors, target_field)
    
    def _is_likely_product_name(self, text: str) -> bool:
        """Check if text is likely a product name"""
        if not text or len(text) < 3:
            return False
        
        # Too short or too long
        if len(text) < 5 or len(text) > 200:
            return False
        
        # Contains product indicators
        product_indicators = ['ml', 'gr', 'adet', 'piece', 'set', 'kit']
        return any(indicator in text.lower() for indicator in product_indicators)
    
    def _generate_selector_variations(self, element) -> List[str]:
        """Generate multiple selector variations for an element"""
        selectors = []
        
        # Direct tag selector
        selectors.append(element.name)
        
        # Class-based selectors
        if element.get('class'):
            classes = element.get('class')
            selectors.append('.' + '.'.join(classes))
            # Individual class selectors
            for cls in classes:
                selectors.append(f'.{cls}')
        
        # ID selector
        if element.get('id'):
            selectors.append(f"#{element.get('id')}")
        
        # Parent-child selectors
        if element.parent and element.parent.name != '[document]':
            parent_selector = self._get_element_selector(element.parent)
            if parent_selector:
                selectors.append(f"{parent_selector} > {element.name}")
                if element.get('class'):
                    selectors.append(f"{parent_selector} > .{'.'.join(element.get('class'))}")
        
        return selectors
    
    def _get_element_selector(self, element) -> str:
        """Get best selector for a single element"""
        if element.get('id'):
            return f"#{element.get('id')}"
        elif element.get('class'):
            return '.' + '.'.join(element.get('class'))
        else:
            return element.name
    
    def _generate_contextual_selectors(self, soup: BeautifulSoup, target_field: str) -> List[str]:
        """Generate selectors based on common e-commerce patterns"""
        selectors = []
        
        # Common e-commerce containers
        containers = [
            '.product-info', '.product-details', '.item-details',
            '.product-container', '.product-wrapper', '.product-content',
            '.product-summary', '.product-data'
        ]
        
        for container in containers:
            container_elem = soup.select_one(container)
            if container_elem:
                # Look for target field within container
                if target_field == 'product_name':
                    headers = container_elem.find_all(['h1', 'h2', 'h3'])
                    for header in headers[:2]:  # First 2 headers most likely
                        selectors.append(f"{container} {header.name}")
                
                elif target_field == 'price':
                    # Common price selectors within product containers
                    price_selectors = [
                        '.price', '.cost', '.amount', '.value',
                        '.current-price', '.sale-price', '.product-price'
                    ]
                    for price_sel in price_selectors:
                        selectors.append(f"{container} {price_sel}")
        
        return selectors
    
    def _rank_selectors(self, selectors: List[str], target_field: str) -> List[str]:
        """Rank selectors by their likelihood of success"""
        scored_selectors = []
        
        for selector in selectors:
            score = 0
            
            # Specificity score
            if '#' in selector:
                score += 10  # ID selectors are highly specific
            if '>' in selector:
                score += 5   # Direct child selectors are good
            if '.' in selector:
                score += 3   # Class selectors are decent
            
            # Field-specific scoring
            field_keywords = self.common_cosmetic_patterns.get(target_field, [])
            for keyword in field_keywords:
                if re.search(keyword, selector, re.I):
                    score += 8
            
            # Turkish keyword bonus
            turkish_keywords = self.turkish_field_patterns.get(target_field, [])
            for tr_keyword in turkish_keywords:
                if re.search(tr_keyword, selector, re.I):
                    score += 10
            
            # Penalize overly complex selectors
            complexity = selector.count(' ') + selector.count('>') + selector.count('+')
            score -= min(complexity * 2, 10)
            
            scored_selectors.append((score, selector))
        
        # Sort by score descending
        scored_selectors.sort(key=lambda x: x[0], reverse=True)
        return [selector for score, selector in scored_selectors]


class MLSelectorGenerator:
    """Machine Learning-based selector generation using Gemini AI"""
    
    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
        else:
            self.model = None
            logger.warning("No Gemini API key provided, ML selector generation disabled")
    
    async def generate_selectors_ai(self, html: str, target_field: str, site_name: str) -> List[str]:
        """Use AI to generate intelligent selectors"""
        if not self.model:
            return []
        
        try:
            # Create focused HTML excerpt (first 10KB to avoid token limits)
            html_excerpt = html[:10000] if len(html) > 10000 else html
            
            prompt = f"""
            Analyze this HTML from {site_name} Turkish e-commerce site and generate the best CSS selectors 
            to extract the {target_field} field.
            
            Context: This is a cosmetic product page from a Turkish e-commerce website.
            Target field: {target_field}
            
            HTML excerpt:
            {html_excerpt}
            
            Please provide 5-10 CSS selectors ranked by effectiveness, considering:
            1. Turkish language patterns (ürün, fiyat, marka, etc.)
            2. Common e-commerce HTML structures
            3. Selector specificity and reliability
            4. Site-specific patterns for {site_name}
            
            Return only CSS selectors, one per line, most effective first.
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.model.generate_content(prompt)
            )
            
            if response and response.text:
                # Parse AI response to extract selectors
                selectors = []
                for line in response.text.strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('//'):
                        # Clean up the selector
                        selector = re.sub(r'^[\d\.\-\*\s]+', '', line)  # Remove numbering
                        selector = selector.strip('`"\'')  # Remove quotes and backticks
                        if selector and len(selector) > 2:
                            selectors.append(selector)
                
                logger.info(f"🤖 Generated {len(selectors)} AI selectors for {target_field}")
                return selectors[:10]  # Limit to top 10
                
        except Exception as e:
            logger.error(f"AI selector generation error: {e}")
        
        return []


class SelectorDatabase:
    """SQLite database for storing and managing selector patterns"""
    
    def __init__(self, db_path: str = "selector_patterns.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the selector database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS selector_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    selector TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    site_name TEXT NOT NULL,
                    success_rate REAL DEFAULT 0.0,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    pattern_type TEXT DEFAULT 'css',
                    confidence_score REAL DEFAULT 0.0,
                    extraction_quality REAL DEFAULT 0.0,
                    context_hash TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(selector, field_name, site_name)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_site_field 
                ON selector_patterns(site_name, field_name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_success_rate 
                ON selector_patterns(success_rate DESC)
            """)
    
    def save_pattern(self, pattern: SelectorPattern):
        """Save or update a selector pattern"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO selector_patterns 
                (selector, field_name, site_name, success_rate, last_used, usage_count,
                 pattern_type, confidence_score, extraction_quality, context_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.selector, pattern.field_name, pattern.site_name,
                pattern.success_rate, pattern.last_used, pattern.usage_count,
                pattern.pattern_type, pattern.confidence_score, 
                pattern.extraction_quality, pattern.context_hash
            ))
    
    def get_best_selectors(self, site_name: str, field_name: str, limit: int = 10) -> List[SelectorPattern]:
        """Get best performing selectors for a site and field"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT selector, field_name, site_name, success_rate, last_used, usage_count,
                       pattern_type, confidence_score, extraction_quality, context_hash
                FROM selector_patterns 
                WHERE site_name = ? AND field_name = ?
                ORDER BY success_rate DESC, usage_count DESC, last_used DESC
                LIMIT ?
            """, (site_name, field_name, limit))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append(SelectorPattern(
                    selector=row[0],
                    field_name=row[1], 
                    site_name=row[2],
                    success_rate=row[3],
                    last_used=datetime.fromisoformat(row[4]),
                    usage_count=row[5],
                    pattern_type=row[6],
                    confidence_score=row[7],
                    extraction_quality=row[8],
                    context_hash=row[9]
                ))
            
            return patterns
    
    def update_pattern_success(self, selector: str, site_name: str, field_name: str, 
                             success: bool, quality_score: float = 0.0):
        """Update pattern success metrics"""
        with sqlite3.connect(self.db_path) as conn:
            # Get current stats
            cursor = conn.execute("""
                SELECT usage_count, success_rate FROM selector_patterns 
                WHERE selector = ? AND site_name = ? AND field_name = ?
            """, (selector, site_name, field_name))
            
            row = cursor.fetchone()
            if row:
                usage_count, current_success_rate = row
                new_usage_count = usage_count + 1
                
                # Calculate new success rate using weighted average
                if success:
                    new_success_rate = ((current_success_rate * usage_count) + 1) / new_usage_count
                else:
                    new_success_rate = (current_success_rate * usage_count) / new_usage_count
                
                # Update the record
                conn.execute("""
                    UPDATE selector_patterns 
                    SET usage_count = ?, success_rate = ?, last_used = CURRENT_TIMESTAMP,
                        extraction_quality = ?
                    WHERE selector = ? AND site_name = ? AND field_name = ?
                """, (new_usage_count, new_success_rate, quality_score, 
                      selector, site_name, field_name))


class AdaptiveSelectorEngine:
    """Main engine for adaptive selector management"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.html_analyzer = HTMLPatternAnalyzer()
        self.ml_generator = MLSelectorGenerator(gemini_api_key)
        self.database = SelectorDatabase()
        self.selector_cache = {}
        self.performance_metrics = defaultdict(lambda: defaultdict(float))
        
    async def extract_field(self, page: Page, field_name: str, site_name: str, 
                           html: Optional[str] = None) -> ExtractionResult:
        """Extract field using adaptive selector strategy"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Get HTML content if not provided
            if not html:
                html = await page.content()
            
            # Try cached successful selectors first
            cached_selectors = self.database.get_best_selectors(site_name, field_name, 5)
            
            for pattern in cached_selectors:
                if pattern.success_rate > 0.7:  # High confidence threshold
                    result = await self._try_extract(page, pattern.selector)
                    if result.success:
                        # Update success metrics
                        extraction_time = asyncio.get_event_loop().time() - start_time
                        self.database.update_pattern_success(
                            pattern.selector, site_name, field_name, True, result.quality_score
                        )
                        
                        return ExtractionResult(
                            success=True,
                            data=result.data,
                            selector_used=pattern.selector,
                            extraction_time=extraction_time,
                            quality_score=result.quality_score
                        )
            
            # If cached selectors fail, generate new ones
            await self._discover_new_selectors(html, field_name, site_name)
            
            # Try newly discovered selectors
            new_selectors = self.database.get_best_selectors(site_name, field_name, 10)
            
            for pattern in new_selectors:
                result = await self._try_extract(page, pattern.selector)
                if result.success:
                    extraction_time = asyncio.get_event_loop().time() - start_time
                    self.database.update_pattern_success(
                        pattern.selector, site_name, field_name, True, result.quality_score
                    )
                    
                    return ExtractionResult(
                        success=True,
                        data=result.data,
                        selector_used=pattern.selector,
                        extraction_time=extraction_time,
                        quality_score=result.quality_score
                    )
                else:
                    # Mark as failed
                    self.database.update_pattern_success(
                        pattern.selector, site_name, field_name, False
                    )
            
            # Final fallback: GPT-based extraction
            result = await self._gpt_fallback_extraction(html, field_name, site_name)
            extraction_time = asyncio.get_event_loop().time() - start_time
            
            return ExtractionResult(
                success=result is not None,
                data=result,
                selector_used="gpt_fallback",
                extraction_time=extraction_time,
                quality_score=0.8 if result else 0.0
            )
            
        except Exception as e:
            extraction_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Extraction error for {field_name} on {site_name}: {e}")
            
            return ExtractionResult(
                success=False,
                data=None,
                selector_used="none",
                extraction_time=extraction_time,
                quality_score=0.0,
                error_message=str(e)
            )
    
    async def _try_extract(self, page: Page, selector: str) -> ExtractionResult:
        """Try to extract data using a specific selector"""
        try:
            # Wait for element with timeout
            element = await page.wait_for_selector(selector, timeout=3000, state='attached')
            
            if element:
                # Get text content
                text = await element.inner_text()
                text = text.strip() if text else ""
                
                if text and len(text) > 0:
                    quality_score = self._calculate_quality_score(text, selector)
                    return ExtractionResult(
                        success=True,
                        data=text,
                        selector_used=selector,
                        extraction_time=0.0,  # Will be set by caller
                        quality_score=quality_score
                    )
            
            return ExtractionResult(
                success=False,
                data=None,
                selector_used=selector,
                extraction_time=0.0,
                quality_score=0.0
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                data=None,
                selector_used=selector,
                extraction_time=0.0,
                quality_score=0.0,
                error_message=str(e)
            )
    
    def _calculate_quality_score(self, text: str, selector: str) -> float:
        """Calculate quality score for extracted text"""
        score = 0.0
        
        # Basic text quality checks
        if text and len(text) > 2:
            score += 0.3
        
        if 5 <= len(text) <= 500:  # Reasonable length
            score += 0.2
        
        # Selector specificity bonus
        if '#' in selector:  # ID selector
            score += 0.2
        elif '.' in selector:  # Class selector
            score += 0.1
        
        # Content quality heuristics
        if not re.search(r'^\s*$', text):  # Not empty/whitespace
            score += 0.2
        
        if not re.search(r'[<>{}]', text):  # No HTML artifacts
            score += 0.1
        
        return min(score, 1.0)
    
    async def _discover_new_selectors(self, html: str, field_name: str, site_name: str):
        """Discover and save new selectors for a field"""
        # HTML pattern analysis
        html_selectors = self.html_analyzer.analyze_html_structure(html, field_name)
        
        # AI-generated selectors
        ai_selectors = await self.ml_generator.generate_selectors_ai(html, field_name, site_name)
        
        # Combine and deduplicate
        all_selectors = list(set(html_selectors + ai_selectors))
        
        # Create selector patterns and save to database
        context_hash = hashlib.md5(html.encode()).hexdigest()[:16]
        
        for selector in all_selectors[:20]:  # Limit to top 20
            pattern = SelectorPattern(
                selector=selector,
                field_name=field_name,
                site_name=site_name,
                success_rate=0.0,  # Will be updated on usage
                last_used=datetime.now(),
                usage_count=0,
                pattern_type='ai_generated' if selector in ai_selectors else 'html_analysis',
                confidence_score=0.5,
                extraction_quality=0.0,
                context_hash=context_hash
            )
            
            self.database.save_pattern(pattern)
        
        logger.info(f"🔍 Discovered {len(all_selectors)} new selectors for {field_name} on {site_name}")
    
    async def _gpt_fallback_extraction(self, html: str, field_name: str, site_name: str) -> Optional[str]:
        """GPT-based fallback extraction when selectors fail"""
        if not self.ml_generator.model:
            return None
        
        try:
            # Use a smaller HTML excerpt for GPT
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract text content, focusing on likely areas
            text_content = soup.get_text()
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            
            # Focus on lines most likely to contain the target field
            relevant_lines = []
            field_keywords = {
                'product_name': ['ürün', 'product', 'name', 'title', 'başlık'],
                'brand': ['marka', 'brand', 'manufacturer', 'üretici'],
                'price': ['fiyat', 'price', '₺', 'TL', 'lira'],
                'description': ['açıklama', 'description', 'detay', 'detail']
            }
            
            keywords = field_keywords.get(field_name, [])
            for line in lines:
                if any(keyword.lower() in line.lower() for keyword in keywords):
                    relevant_lines.append(line)
            
            if not relevant_lines:
                relevant_lines = lines[:50]  # First 50 lines as fallback
            
            content_excerpt = '\n'.join(relevant_lines[:30])  # Limit content
            
            prompt = f"""
            Extract the {field_name} from this Turkish cosmetic product page content.
            
            Site: {site_name}
            Field to extract: {field_name}
            
            Content:
            {content_excerpt}
            
            Please return ONLY the extracted value, nothing else.
            If you cannot find the {field_name}, return "NOT_FOUND".
            """
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.ml_generator.model.generate_content(prompt)
            )
            
            if response and response.text:
                result = response.text.strip()
                if result and result != "NOT_FOUND" and len(result) < 1000:
                    logger.info(f"🤖 GPT fallback successful for {field_name}")
                    return result
            
        except Exception as e:
            logger.error(f"GPT fallback error: {e}")
        
        return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the selector engine"""
        total_patterns = 0
        successful_patterns = 0
        
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM selector_patterns")
            total_patterns = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM selector_patterns WHERE success_rate > 0.5")
            successful_patterns = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT site_name, field_name, AVG(success_rate), COUNT(*)
                FROM selector_patterns 
                GROUP BY site_name, field_name
            """)
            site_performance = cursor.fetchall()
        
        return {
            'total_patterns': total_patterns,
            'successful_patterns': successful_patterns,
            'success_rate': successful_patterns / max(total_patterns, 1),
            'site_performance': [
                {
                    'site': row[0],
                    'field': row[1], 
                    'avg_success_rate': row[2],
                    'pattern_count': row[3]
                }
                for row in site_performance
            ]
        }


# Factory function for easy integration
def create_adaptive_selector_engine(gemini_api_key: Optional[str] = None) -> AdaptiveSelectorEngine:
    """Create and initialize adaptive selector engine"""
    return AdaptiveSelectorEngine(gemini_api_key)


# Example usage
if __name__ == "__main__":
    async def test_selector_engine():
        """Test the adaptive selector engine"""
        engine = create_adaptive_selector_engine()
        
        # Mock test - in real usage, you'd pass a Playwright page
        print("🧪 Adaptive Selector Engine Test Complete")
        
        metrics = engine.get_performance_metrics()
        print(f"📊 Performance Metrics: {metrics}")
    
    asyncio.run(test_selector_engine())