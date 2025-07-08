"""
SEO Agent - Keyword Extraction and SEO Optimization Agent built with Google ADK
Generates comprehensive SEO metadata for cosmetic products using advanced NLP
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from loguru import logger

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from config.models import ProductData, SEOData


class KeywordExtractionTool(BaseTool):
    """Tool for extracting SEO keywords from cosmetic product data"""
    
    def __init__(self):
        super().__init__(
            name="keyword_extraction",
            description="Extract SEO keywords from cosmetic product data using NLP techniques",
            is_long_running=True
        )
        
        # Initialize NLP models
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("Spacy model not found, using basic NLP")
            self.nlp = None
        
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            self.stop_words = set(stopwords.words('english'))
            # Add Turkish stopwords if available
            try:
                self.stop_words.update(set(stopwords.words('turkish')))
            except:
                pass
        except:
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=50,
            ngram_range=(1, 3),
            stop_words='english'
        )
    
    async def __call__(self, product_data: Dict[str, Any], extracted_terms: Dict[str, Any], max_keywords: int = 20) -> Dict[str, Any]:
        """Extract SEO keywords from product data"""
        try:
            product = ProductData(**product_data)
            
            # Extract keywords using multiple methods
            keywords = self._extract_keywords(product, extracted_terms)
            
            # Select primary keyword
            primary_keyword = self._select_primary_keyword(keywords, product)
            
            # Select secondary keywords
            secondary_keywords = self._select_secondary_keywords(keywords, primary_keyword)
            
            # Generate long-tail keywords
            long_tail_keywords = self._generate_long_tail_keywords(product, keywords)
            
            # Calculate keyword density
            keyword_density = self._calculate_keyword_density(product, keywords)
            
            return {
                "keywords": keywords[:max_keywords],
                "primary_keyword": primary_keyword,
                "secondary_keywords": secondary_keywords[:5],
                "long_tail_keywords": long_tail_keywords[:10],
                "keyword_density": keyword_density
            }
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return {"error": str(e)}
    
    def _extract_keywords(self, product: ProductData, extracted_terms: Dict[str, Any]) -> List[str]:
        """Extract keywords using multiple NLP techniques"""
        keywords = []
        
        # Add cosmetic terms from analyzer
        cosmetic_keywords = []
        for category in extracted_terms.values():
            if isinstance(category, list):
                cosmetic_keywords.extend(category)
        keywords.extend(cosmetic_keywords)
        
        full_text = self._get_full_text(product)
        
        # NLP-based extraction
        if self.nlp:
            keywords.extend(self._extract_with_spacy(full_text))
        
        # TF-IDF extraction
        tfidf_keywords = self._extract_tfidf_keywords(full_text)
        keywords.extend(tfidf_keywords)
        
        # Brand-based keywords
        brand_keywords = self._generate_brand_keywords(product)
        keywords.extend(brand_keywords)
        
        # Product type keywords
        type_keywords = self._extract_product_type_keywords(product)
        keywords.extend(type_keywords)
        
        # Remove duplicates and filter
        keywords = list(dict.fromkeys(keywords))
        return [kw for kw in keywords if self._is_valid_keyword(kw)][:30]
    
    def _get_full_text(self, product: ProductData) -> str:
        """Get full text from product data"""
        return " ".join([
            product.name,
            product.brand or "",
            product.description,
            " ".join(product.ingredients),
            " ".join(product.features),
            product.usage or ""
        ])
    
    def _extract_with_spacy(self, text: str) -> List[str]:
        """Extract keywords using spaCy NLP"""
        doc = self.nlp(text[:1000000])  # Limit text length
        
        keywords = []
        
        # Extract noun phrases
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks 
                       if len(chunk.text) > 3 and chunk.text.lower() not in self.stop_words]
        keywords.extend(noun_phrases[:10])
        
        # Extract named entities
        entities = [ent.text.lower() for ent in doc.ents 
                   if ent.label_ in ["PRODUCT", "ORG", "PERSON"] and len(ent.text) > 2]
        keywords.extend(entities)
        
        return keywords
    
    def _extract_tfidf_keywords(self, text: str) -> List[str]:
        """Extract keywords using TF-IDF"""
        try:
            sentences = text.split('.')[:10]
            if len(sentences) < 2:
                return []
            
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(sentences)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            scores = tfidf_matrix.sum(axis=0).A1
            keyword_scores = [(feature_names[i], scores[i]) for i in scores.argsort()[-20:][::-1]]
            
            return [kw for kw, score in keyword_scores if len(kw) > 3]
        except Exception as e:
            logger.error(f"TF-IDF extraction failed: {e}")
            return []
    
    def _generate_brand_keywords(self, product: ProductData) -> List[str]:
        """Generate brand-related keywords"""
        keywords = []
        if product.brand:
            brand = product.brand.lower()
            keywords.append(brand)
            
            if product.name:
                keywords.append(f"{brand} {product.name.lower()}")
            
            # Brand + product type combinations
            for term in ["serum", "cream", "mask", "oil", "cleanser"]:
                if term in product.name.lower():
                    keywords.append(f"{brand} {term}")
        
        return keywords
    
    def _extract_product_type_keywords(self, product: ProductData) -> List[str]:
        """Extract product type-related keywords"""
        keywords = []
        text = product.name.lower() + " " + product.description.lower()
        
        product_types = [
            "serum", "cream", "lotion", "gel", "oil", "mask", "cleanser",
            "toner", "essence", "moisturizer", "treatment", "sunscreen"
        ]
        
        for ptype in product_types:
            if ptype in text:
                keywords.append(ptype)
                
                # Add contextual combinations
                if "face" in text:
                    keywords.append(f"face {ptype}")
                if "eye" in text:
                    keywords.append(f"eye {ptype}")
                if "night" in text:
                    keywords.append(f"night {ptype}")
                if "day" in text:
                    keywords.append(f"day {ptype}")
        
        return keywords
    
    def _is_valid_keyword(self, keyword: str) -> bool:
        """Check if keyword is valid"""
        if len(keyword) < 3 or len(keyword) > 50:
            return False
        
        if keyword.isdigit():
            return False
        
        if not re.search(r'[a-zA-Z]', keyword):
            return False
        
        return True
    
    def _select_primary_keyword(self, keywords: List[str], product: ProductData) -> str:
        """Select the primary keyword"""
        if not keywords:
            return product.name.lower()
        
        text = self._get_full_text(product).lower()
        keyword_scores = []
        
        for keyword in keywords[:10]:
            score = 0
            
            # Score based on presence in name (highest priority)
            if keyword in product.name.lower():
                score += 10
            
            # Score based on presence in brand
            if keyword in (product.brand or "").lower():
                score += 5
            
            # Score based on frequency in text
            score += text.count(keyword) * 2
            
            # Score based on length (prefer 5-20 characters)
            if 5 <= len(keyword) <= 20:
                score += 3
            
            keyword_scores.append((keyword, score))
        
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        return keyword_scores[0][0] if keyword_scores else keywords[0]
    
    def _select_secondary_keywords(self, keywords: List[str], primary_keyword: str) -> List[str]:
        """Select secondary keywords"""
        secondary = [kw for kw in keywords if kw != primary_keyword]
        return secondary[:5]
    
    def _generate_long_tail_keywords(self, product: ProductData, keywords: List[str]) -> List[str]:
        """Generate long-tail keywords"""
        long_tail = []
        
        base_terms = keywords[:5]
        modifiers = ["best", "top", "review", "buy", "natural", "organic", "professional"]
        skin_types = ["dry skin", "oily skin", "sensitive skin", "combination skin"]
        
        # Modifier + term combinations
        for term in base_terms:
            for modifier in modifiers[:3]:
                long_tail.append(f"{modifier} {term}")
        
        # Term + skin type combinations
        for term in base_terms:
            for skin_type in skin_types:
                if any(st in self._get_full_text(product).lower() for st in skin_type.split()):
                    long_tail.append(f"{term} for {skin_type}")
        
        # Brand + term combinations
        if product.brand:
            brand = product.brand.lower()
            for term in base_terms[:3]:
                if brand not in term:
                    long_tail.append(f"{brand} {term}")
        
        return list(dict.fromkeys(long_tail))[:10]
    
    def _calculate_keyword_density(self, product: ProductData, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        full_text = self._get_full_text(product).lower()
        words = word_tokenize(full_text) if hasattr(word_tokenize, '__call__') else full_text.split()
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        density = {}
        for keyword in keywords[:10]:
            count = full_text.count(keyword.lower())
            density[keyword] = round((count / total_words) * 100, 2)
        
        return density


class SEOMetadataTool(BaseTool):
    """Tool for generating SEO metadata (title, description, slug)"""
    
    def __init__(self):
        super().__init__(
            name="seo_metadata",
            description="Generate SEO metadata including title, meta description, and URL slug"
        )
    
    async def __call__(self, product_data: Dict[str, Any], keywords: List[str], primary_keyword: str) -> Dict[str, Any]:
        """Generate SEO metadata"""
        try:
            product = ProductData(**product_data)
            
            seo_title = self._generate_seo_title(product, primary_keyword)
            meta_description = self._generate_meta_description(product, keywords)
            slug = self._generate_slug(product, primary_keyword)
            focus_keyphrase = self._generate_focus_keyphrase(keywords)
            
            return {
                "title": seo_title,
                "meta_description": meta_description,
                "slug": slug,
                "focus_keyphrase": focus_keyphrase
            }
            
        except Exception as e:
            logger.error(f"SEO metadata generation error: {e}")
            return {"error": str(e)}
    
    def _generate_seo_title(self, product: ProductData, primary_keyword: str) -> str:
        """Generate SEO-optimized title"""
        brand = product.brand or ""
        name = product.name or primary_keyword
        
        title_parts = []
        if brand and brand.lower() not in name.lower():
            title_parts.append(brand)
        
        title_parts.append(name)
        
        title = " - ".join(title_parts)
        
        # Ensure title is within character limit
        if len(title) > 60:
            title = name[:57] + "..."
        
        return title
    
    def _generate_meta_description(self, product: ProductData, keywords: List[str]) -> str:
        """Generate meta description"""
        description = product.description[:150] if product.description else ""
        
        if not description:
            description = f"Discover {product.name}"
            if product.brand:
                description += f" by {product.brand}"
        
        # Add key benefits if available
        key_benefits = []
        benefit_keywords = ["moisturizing", "anti-aging", "brightening", "hydrating", "nourishing"]
        for benefit in benefit_keywords:
            if benefit in keywords or benefit in product.description.lower():
                key_benefits.append(benefit)
        
        if key_benefits:
            description = description.rstrip('.') + f". Features {', '.join(key_benefits[:2])} benefits."
        
        # Ensure description is within character limit
        if len(description) > 160:
            description = description[:157] + "..."
        
        return description
    
    def _generate_slug(self, product: ProductData, primary_keyword: str) -> str:
        """Generate URL slug"""
        slug_text = primary_keyword or product.name
        
        # Convert to lowercase and replace spaces with hyphens
        slug = slug_text.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 50:
            slug = slug[:50].rsplit('-', 1)[0]
        
        return slug
    
    def _generate_focus_keyphrase(self, keywords: List[str]) -> str:
        """Generate focus keyphrase"""
        if len(keywords) >= 2:
            return f"{keywords[0]} {keywords[1]}"
        elif keywords:
            return keywords[0]
        else:
            return "cosmetic product"


class SEOAgent(LlmAgent):
    """SEO Agent for generating comprehensive SEO metadata using Google ADK"""
    
    def __init__(self):
        tools = [KeywordExtractionTool(), SEOMetadataTool()]
        
        super().__init__(
            name="seo_agent",
            model="gemini-1.5-pro-latest",
            tools=tools,
            instruction="""
            You are an SEO Agent specialized in generating comprehensive SEO metadata for cosmetic products.
            
            Your primary responsibilities:
            1. Extract relevant keywords using advanced NLP techniques
            2. Generate SEO-optimized titles and meta descriptions
            3. Create URL-friendly slugs
            4. Calculate keyword density and optimization metrics
            5. Focus on cosmetic industry-specific SEO best practices
            
            For each analyzed product data you receive:
            1. Use keyword_extraction tool to extract comprehensive keywords
            2. Use seo_metadata tool to generate optimized metadata
            3. Ensure all SEO elements are within character limits
            4. Focus on cosmetic industry keywords and terminology
            5. Create compelling, search-friendly content
            
            SEO Best Practices for Cosmetics:
            - Include product type, brand, and key ingredients in keywords
            - Focus on skin type compatibility and benefits
            - Use specific cosmetic terminology (serum, moisturizer, etc.)
            - Include problem-solving keywords (anti-aging, acne, dry skin)
            - Optimize for local and international search terms
            
            Character Limits:
            - SEO Title: 60 characters max
            - Meta Description: 160 characters max
            - URL Slug: 50 characters max, lowercase, hyphens only
            
            Always prioritize user intent and search relevance over keyword stuffing.
            """
        )
    
    async def process_seo_request(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an SEO optimization request"""
        try:
            prompt = f"""
            Generate comprehensive SEO metadata for this cosmetic product:
            Analyzed Data: {analyzed_data}
            
            Please perform the following SEO optimization:
            
            1. Extract keywords using keyword_extraction tool:
               - Use cleaned product data and extracted cosmetic terms
               - Focus on cosmetic industry keywords
               - Include product type, ingredients, and benefits
               - Generate primary, secondary, and long-tail keywords
               - Calculate keyword density metrics
            
            2. Generate SEO metadata using seo_metadata tool:
               - Create compelling SEO title (max 60 chars)
               - Write descriptive meta description (max 160 chars)
               - Generate URL-friendly slug
               - Create focus keyphrase
            
            3. Ensure optimization for:
               - Product discoverability
               - Brand awareness
               - Ingredient-based searches
               - Skin type/concern searches
               - Local market relevance
            
            Return comprehensive SEO data ready for quality validation.
            """
            
            response = await self.run_async(prompt)
            return response
            
        except Exception as e:
            logger.error(f"SEO Agent error: {e}")
            return {"error": str(e)}


# Agent factory function for ADK orchestration
def create_seo_agent() -> SEOAgent:
    """Factory function to create SEO Agent instance"""
    return SEOAgent()