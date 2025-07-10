"""
Analyzer Agent - Data Cleaning and Analysis Agent built with Google ADK
Cleans, normalizes and analyzes cosmetic product data
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from bs4 import BeautifulSoup
from langdetect import detect
from loguru import logger

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from config.models import ProductData, CosmeticTerms


class DataCleaningTool(BaseTool):
    """Tool for cleaning and normalizing product data"""
    
    def __init__(self):
        super().__init__(
            name="data_cleaning",
            description="Clean and normalize cosmetic product data"
        )
        self.cosmetic_terms = CosmeticTerms()
    
    async def __call__(self, product_data: Dict[str, Any], language: str = "auto") -> Dict[str, Any]:
        """Clean and normalize product data"""
        try:
            product = ProductData(**product_data)
            cleaned_product = self._clean_product_data(product)
            
            # Detect language
            detected_language = self._detect_language(cleaned_product.description)
            
            # Extract cosmetic terms
            extracted_terms = self._extract_cosmetic_terms(cleaned_product)
            
            # Categorize content
            content_sections = self._categorize_content(cleaned_product)
            
            # Calculate text statistics
            text_stats = self._calculate_text_stats(cleaned_product)
            
            return {
                "cleaned_product": cleaned_product.model_dump(),
                "language": detected_language,
                "extracted_terms": extracted_terms,
                "content_sections": content_sections,
                "text_stats": text_stats
            }
            
        except Exception as e:
            logger.error(f"Data cleaning error: {e}")
            return {"error": str(e)}
    
    def _clean_product_data(self, product: ProductData) -> ProductData:
        """Clean and normalize product data"""
        product_dict = product.model_dump()
        
        # Clean text fields
        product_dict["name"] = self._clean_text(product_dict["name"])
        product_dict["brand"] = self._clean_text(product_dict["brand"])
        product_dict["description"] = self._clean_html(product_dict["description"])
        product_dict["usage"] = self._clean_html(product_dict.get("usage", ""))
        
        # Clean lists
        product_dict["ingredients"] = [
            self._clean_text(ing) for ing in product_dict["ingredients"] if ing
        ]
        product_dict["features"] = [
            self._clean_text(feat) for feat in product_dict["features"] if feat
        ]
        product_dict["reviews"] = [
            self._clean_text(rev) for rev in product_dict["reviews"] 
            if rev and len(rev) > 10
        ]
        
        # Normalize price
        product_dict["price"] = self._normalize_price(product_dict.get("price", ""))
        
        return ProductData(**product_dict)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove unwanted characters but keep cosmetic-relevant symbols
        text = re.sub(r'[^\w\s\-.,!?€$₺%°]', '', text)
        
        return text.strip()
    
    def _clean_html(self, html_text: str) -> str:
        """Clean HTML and extract text"""
        if not html_text:
            return ""
        
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return self._clean_text(text)
    
    def _normalize_price(self, price: str) -> str:
        """Normalize price format"""
        if not price:
            return ""
        
        # Keep only digits, comma, period, and currency symbols
        price = re.sub(r'[^\d,.\s€$₺]', '', price)
        return price.strip()
    
    def _detect_language(self, text: str) -> str:
        """Detect language of the text"""
        try:
            if len(text) > 50:
                return detect(text)
            return "unknown"
        except:
            return "unknown"
    
    def _extract_cosmetic_terms(self, product: ProductData) -> Dict[str, List[str]]:
        """Extract cosmetic-specific terms from product data"""
        full_text = " ".join([
            product.name,
            product.description,
            " ".join(product.ingredients),
            " ".join(product.features),
            product.usage or ""
        ]).lower()
        
        extracted = {
            "found_ingredients": [],
            "found_benefits": [],
            "found_product_types": [],
            "found_skin_types": []
        }
        
        # Find ingredients
        for ingredient in self.cosmetic_terms.ingredients:
            if ingredient.lower() in full_text:
                extracted["found_ingredients"].append(ingredient)
        
        # Find benefits
        for benefit in self.cosmetic_terms.benefits:
            if benefit.lower() in full_text:
                extracted["found_benefits"].append(benefit)
        
        # Find product types
        for product_type in self.cosmetic_terms.product_types:
            if product_type.lower() in full_text:
                extracted["found_product_types"].append(product_type)
        
        # Find skin types
        for skin_type in self.cosmetic_terms.skin_types:
            if skin_type.lower() in full_text:
                extracted["found_skin_types"].append(skin_type)
        
        return extracted
    
    def _categorize_content(self, product: ProductData) -> Dict[str, Any]:
        """Categorize product content sections"""
        return {
            "main_description": product.description,
            "ingredients_list": product.ingredients,
            "key_features": product.features,
            "usage_instructions": product.usage or "",
            "customer_feedback": product.reviews[:5] if product.reviews else []
        }
    
    def _calculate_text_stats(self, product: ProductData) -> Dict[str, int]:
        """Calculate text statistics"""
        full_text = " ".join([
            product.name,
            product.description,
            " ".join(product.ingredients),
            " ".join(product.features),
            product.usage or ""
        ])
        
        words = full_text.split()
        
        return {
            "total_words": len(words),
            "unique_words": len(set(words)),
            "description_length": len(product.description),
            "ingredients_count": len(product.ingredients),
            "features_count": len(product.features),
            "reviews_count": len(product.reviews)
        }


class CosmeticAnalysisTool(BaseTool):
    """Tool for cosmetic-specific analysis"""
    
    def __init__(self):
        super().__init__(
            name="cosmetic_analysis",
            description="Perform cosmetic industry-specific analysis on product data"
        )
    
    async def __call__(self, product_data: Dict[str, Any], extracted_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cosmetic industry analysis"""
        try:
            product = ProductData(**product_data)
            
            # Product categorization
            category = self._categorize_product(product, extracted_terms)
            
            # Skin type compatibility
            skin_compatibility = self._analyze_skin_compatibility(product, extracted_terms)
            
            # Ingredient analysis
            ingredient_analysis = self._analyze_ingredients(product)
            
            # Market positioning
            market_position = self._analyze_market_position(product)
            
            return {
                "product_category": category,
                "skin_compatibility": skin_compatibility,
                "ingredient_analysis": ingredient_analysis,
                "market_position": market_position
            }
            
        except Exception as e:
            logger.error(f"Cosmetic analysis error: {e}")
            return {"error": str(e)}
    
    def _categorize_product(self, product: ProductData, extracted_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize the cosmetic product"""
        text = (product.name + " " + product.description).lower()
        
        # Primary category
        primary_category = "unknown"
        if any(term in text for term in ["serum", "essence", "ampoule"]):
            primary_category = "skincare_treatment"
        elif any(term in text for term in ["cream", "lotion", "moisturizer"]):
            primary_category = "skincare_moisturizer"
        elif any(term in text for term in ["cleanser", "wash", "foam"]):
            primary_category = "skincare_cleanser"
        elif any(term in text for term in ["foundation", "concealer", "bb cream"]):
            primary_category = "makeup_base"
        elif any(term in text for term in ["lipstick", "gloss", "balm"]):
            primary_category = "makeup_lips"
        elif any(term in text for term in ["perfume", "cologne", "fragrance"]):
            primary_category = "fragrance"
        elif any(term in text for term in ["shampoo", "conditioner"]):
            primary_category = "haircare"
        
        # Sub-category based on found product types
        sub_categories = extracted_terms.get("found_product_types", [])
        
        return {
            "primary": primary_category,
            "sub_categories": sub_categories,
            "confidence": 0.8 if primary_category != "unknown" else 0.3
        }
    
    def _analyze_skin_compatibility(self, product: ProductData, extracted_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skin type compatibility"""
        text = (product.name + " " + product.description).lower()
        found_skin_types = extracted_terms.get("found_skin_types", [])
        
        # Default compatibility
        compatibility = {
            "dry": 0.5,
            "oily": 0.5,
            "combination": 0.5,
            "sensitive": 0.5,
            "normal": 0.7
        }
        
        # Adjust based on ingredients and descriptions
        if "hyaluronic acid" in text or "moisturizing" in text:
            compatibility["dry"] = 0.9
        
        if "salicylic acid" in text or "oil control" in text:
            compatibility["oily"] = 0.9
            compatibility["sensitive"] = 0.3
        
        if "gentle" in text or "sensitive" in text:
            compatibility["sensitive"] = 0.8
        
        return {
            "skin_type_scores": compatibility,
            "recommended_for": [k for k, v in compatibility.items() if v > 0.7],
            "found_skin_types": found_skin_types
        }
    
    def _analyze_ingredients(self, product: ProductData) -> Dict[str, Any]:
        """Analyze product ingredients"""
        ingredients_text = " ".join(product.ingredients).lower()
        
        # Active ingredients
        actives = []
        active_ingredients = [
            "retinol", "vitamin c", "niacinamide", "hyaluronic acid",
            "salicylic acid", "glycolic acid", "peptides"
        ]
        
        for active in active_ingredients:
            if active in ingredients_text:
                actives.append(active)
        
        # Safety flags
        safety_flags = []
        if "retinol" in ingredients_text:
            safety_flags.append("photosensitive_ingredient")
        if "salicylic acid" in ingredients_text:
            safety_flags.append("exfoliating_ingredient")
        
        return {
            "active_ingredients": actives,
            "total_ingredients": len(product.ingredients),
            "safety_flags": safety_flags,
            "natural_score": self._calculate_natural_score(product.ingredients)
        }
    
    def _calculate_natural_score(self, ingredients: List[str]) -> float:
        """Calculate naturalness score based on ingredients"""
        if not ingredients:
            return 0.0
        
        natural_keywords = [
            "oil", "extract", "butter", "water", "natural", "organic",
            "botanical", "plant", "herb", "flower", "fruit", "seed"
        ]
        
        natural_count = 0
        for ingredient in ingredients:
            if any(keyword in ingredient.lower() for keyword in natural_keywords):
                natural_count += 1
        
        return min(natural_count / len(ingredients), 1.0)
    
    def _analyze_market_position(self, product: ProductData) -> Dict[str, Any]:
        """Analyze market positioning"""
        text = (product.name + " " + product.description).lower()
        
        # Price tier estimation
        price_tier = "unknown"
        if product.price:
            # Simple price analysis (would need more sophisticated logic)
            if any(word in text for word in ["luxury", "premium", "professional"]):
                price_tier = "premium"
            elif any(word in text for word in ["affordable", "budget", "value"]):
                price_tier = "budget"
            else:
                price_tier = "mid_range"
        
        # Target demographic
        target_demo = []
        if "anti-aging" in text or "mature" in text:
            target_demo.append("mature_skin")
        if "acne" in text or "teenage" in text:
            target_demo.append("young_adults")
        if "gentle" in text or "baby" in text:
            target_demo.append("sensitive_users")
        
        return {
            "price_tier": price_tier,
            "target_demographic": target_demo,
            "positioning_keywords": [
                word for word in ["luxury", "professional", "natural", "organic", "clinical"]
                if word in text
            ]
        }


class AnalyzeProductDataTool(BaseTool):
    """Main tool for analyzing product data with all sub-processes"""
    
    def __init__(self):
        super().__init__(
            name="analyze_product_data",
            description="Analyze and clean cosmetic product data comprehensively",
            is_long_running=True
        )
        self.data_cleaning_tool = DataCleaningTool()
        self.cosmetic_analysis_tool = CosmeticAnalysisTool()
    
    async def __call__(self, product_data: Dict[str, Any], language: str = "auto") -> Dict[str, Any]:
        """Analyze product data comprehensively"""
        try:
            # Step 1: Clean and normalize data
            cleaned_result = await self.data_cleaning_tool(product_data, language)
            
            if "error" in cleaned_result:
                return cleaned_result
            
            # Step 2: Perform cosmetic industry analysis
            analysis_result = await self.cosmetic_analysis_tool(
                cleaned_result['cleaned_product'], 
                cleaned_result['extracted_terms']
            )
            
            if "error" in analysis_result:
                return analysis_result
            
            # Combine all results
            return {
                "cleaned_product": cleaned_result['cleaned_product'],
                "language": cleaned_result['language'],
                "extracted_terms": cleaned_result['extracted_terms'],
                "content_sections": cleaned_result['content_sections'],
                "text_stats": cleaned_result['text_stats'],
                "product_category": analysis_result['product_category'],
                "skin_compatibility": analysis_result['skin_compatibility'],
                "ingredient_analysis": analysis_result['ingredient_analysis'],
                "market_position": analysis_result['market_position'],
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Product data analysis error: {e}")
            return {"error": str(e)}


class AnalyzerAgent(LlmAgent):
    """Analyzer Agent for cleaning and analyzing cosmetic product data using Google ADK"""
    
    def __init__(self):
        tools = [AnalyzeProductDataTool()]
        
        super().__init__(
            name="analyzer_agent",
            model="gemini-1.5-pro-latest",
            tools=tools,
            instruction="""
            You are an Analyzer Agent specialized in cleaning and analyzing cosmetic product data.
            
            Your primary responsibilities:
            1. Clean and normalize raw product data from scraping
            2. Extract cosmetic industry-specific terms and concepts
            3. Analyze product ingredients and their effects
            4. Categorize products by type and target audience
            5. Assess skin type compatibility
            6. Prepare data for SEO analysis
            
            For each product data you receive:
            1. Use analyze_product_data tool to comprehensively process the data
            2. Extract key cosmetic terms (ingredients, benefits, product types)
            3. Analyze language and content structure
            4. Prepare comprehensive analyzed data for SEO processing
            
            Focus on:
            - Data quality and consistency
            - Cosmetic industry terminology extraction
            - Ingredient analysis and effects
            - Product categorization
            - Skin type compatibility assessment
            - Market positioning insights
            
            Ensure the cleaned data is ready for effective SEO keyword generation.
            """
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main run method for the analyzer agent"""
        try:
            # Extract product data from input
            product_data = input_data.get('product_data')
            language = input_data.get('language', 'auto')
            
            if not product_data:
                return {"error": "product_data is required"}
            
            # Use the main analysis tool
            analysis_tool = self.tools[0]  # AnalyzeProductDataTool
            result = await analysis_tool(product_data, language)
            
            return result
            
        except Exception as e:
            logger.error(f"Analyzer Agent error: {e}")
            return {"error": str(e)}
    
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async run method for compatibility"""
        return await self.run(input_data)
    
    async def process_analysis_request(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a product data analysis request (legacy method)"""
        return await self.run({'product_data': product_data})


# Agent factory function for ADK orchestration
def create_analyzer_agent() -> AnalyzerAgent:
    """Factory function to create Analyzer Agent instance"""
    return AnalyzerAgent()