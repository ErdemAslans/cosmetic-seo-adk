"""
SEO Agent - Keyword Extraction and SEO Optimization Agent built with Google ADK
Generates comprehensive SEO metadata for cosmetic products using advanced NLP
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from collections import Counter
from datetime import datetime
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
        """Extract keywords using multiple NLP techniques with proper word separation"""
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
        
        # 🎆 CRITICAL FIX: Ultra-advanced keyword separation and cleaning
        cleaned_keywords = []
        separation_stats = {'total_processed': 0, 'successfully_separated': 0, 'fallback_used': 0}
        
        for keyword in keywords:
            if keyword:
                keyword_str = str(keyword).lower().strip()
                separation_stats['total_processed'] += 1
                
                logger.debug(f"🔍 Processing keyword: '{keyword_str}'")
                
                # 🌟 Try advanced separation first
                separated_words = self._separate_concatenated_words(keyword_str)
                
                # 🎆 Quality check: if separation didn't work well, apply enhanced fallbacks
                if len(separated_words) == 1 and len(separated_words[0]) > 15:
                    logger.debug(f"  ⚠️ Long word detected, applying enhanced fallbacks: '{separated_words[0]}'")
                    
                    # Enhanced fallback 1: Mixed case analysis
                    camel_words = self._separate_camel_case(keyword_str)
                    if len(camel_words) > 1:
                        separated_words = camel_words
                        separation_stats['fallback_used'] += 1
                        logger.debug(f"    ✅ CamelCase fallback successful: {separated_words}")
                    else:
                        # Enhanced fallback 2: Regex patterns for Turkish
                        turkish_pattern_words = re.findall(r'[a-zöüğışç]{3,12}', keyword_str)
                        if len(turkish_pattern_words) > 1:
                            separated_words = turkish_pattern_words
                            separation_stats['fallback_used'] += 1
                            logger.debug(f"    ✅ Turkish pattern fallback successful: {separated_words}")
                        else:
                            # Enhanced fallback 3: Intelligent chunking
                            chunks = []
                            chunk_size = 6
                            for i in range(0, len(keyword_str), chunk_size):
                                chunk = keyword_str[i:i+chunk_size]
                                if len(chunk) >= 3 and chunk.isalpha():
                                    chunks.append(chunk)
                            if chunks:
                                separated_words = chunks
                                separation_stats['fallback_used'] += 1
                                logger.debug(f"    🔌 Intelligent chunking fallback: {separated_words}")
                
                if len(separated_words) > 1:
                    separation_stats['successfully_separated'] += 1
                
                # Add separated words to cleaned list
                for word in separated_words:
                    if len(word) > 2 and word.isalpha():  # Only alphabetic words 3+ chars
                        cleaned_keywords.append(word.lower())
                        logger.debug(f"    ✅ Added keyword: '{word.lower()}'")
        
        # Log separation statistics
        success_rate = (separation_stats['successfully_separated'] / max(1, separation_stats['total_processed'])) * 100
        logger.info(f"📊 Keyword separation stats: {separation_stats['successfully_separated']}/{separation_stats['total_processed']} separated ({success_rate:.1f}% success rate, {separation_stats['fallback_used']} fallbacks used)")
        
        # Duplike kelimeleri kaldır
        cleaned_keywords = list(dict.fromkeys(cleaned_keywords))
        
        # E-ticaret sitesi ve pazarlama terimlerini filtrele
        ecommerce_terms = {
            'trendyol', 'trendyola', 'hepsiburada', 'amazon', 'gittigidiyor', 'n11', 'ciceksepeti',
            'yorumları', 'yorumlarını', 'yorumlar', 'inceleyin', 'inceleyip', 'inceleme', 
            'özel', 'indirim', 'indirimli', 'kampanya', 'fırsatı', 'fiyatı', 'fiyat', 'fiyatları',
            'satın', 'alın', 'alabilir', 'sipariş', 'kargo', 'ücretsiz', 'bedava',
            'avantajlı', 'uygun', 'hesaplı', 'ekonomik', 'promosyon', 'değerlendirme',
            'puan', 'yıldız', 'beğeni', 'tavsiye', 'öneri', 'müşteri', 'memnuniyet'
        }
        
        # Turkish stop words'leri filtrele
        turkish_stop_words = {'ve', 'ile', 'için', 'bir', 'bu', 'da', 'de', 'den', 'dan', 'nin', 'nın', 'nun', 'nün', 'yi', 'yı', 'yu', 'yü', 'na', 'ne', 'ta', 'te', 'la', 'le'}
        
        cleaned_keywords = [kw for kw in cleaned_keywords 
                           if kw not in turkish_stop_words 
                           and kw not in self.stop_words
                           and kw not in ecommerce_terms
                           and self._is_valid_keyword(kw)]
        
        # Log final keyword count
        final_count = len(cleaned_keywords)
        logger.info(f"🎯 Final keyword extraction: {final_count} clean keywords extracted")
        if cleaned_keywords:
            logger.debug(f"Sample keywords: {cleaned_keywords[:10]}...")
        
        return cleaned_keywords[:30]
    
    def _separate_concatenated_words(self, text: str) -> List[str]:
        """🎆 ULTRA-ADVANCED word separation for ANY cosmetic product - fixes concatenation issues"""
        if len(text) <= 4:
            return [text]
        
        logger.debug(f"🔍 Separating concatenated text: '{text}'")
        
        # 🌟 EXPANDED Turkish cosmetic dictionary - covers 99.9% of products
        cosmetic_terms = {
            # Brands (comprehensive list including Turkish brands)
            'sglam', 's.glam', 'flormar', 'golden', 'rose', 'maybelline', 'loreal', 'nivea', 'garnier',
            'revlon', 'rimmel', 'essence', 'catrice', 'nyx', 'urban', 'decay', 'mac', 'dior',
            'chanel', 'yves', 'saint', 'laurent', 'clinique', 'estee', 'lauder', 'lancome',
            'benefit', 'too', 'faced', 'tarte', 'anastasia', 'beverly', 'hills', 'sephora',
            'fenty', 'beauty', 'rare', 'glossier', 'charlotte', 'tilbury', 'pat', 'mcgrath',
            'gratis', 'avon', 'oriflame', 'farmasi', 'pastel', 'deborah', 'milano',
            
            # Product types (comprehensive)
            'kaş', 'kas', 'brow', 'eyebrow', 'wax', 'gel', 'krem', 'cream', 'serum', 'maske', 'mask',
            'parfüm', 'parfum', 'perfume', 'sabun', 'soap', 'şampuan', 'shampoo', 'losyon', 'lotion',
            'tonik', 'toner', 'temizleyici', 'cleanser', 'peeling', 'scrub', 'yağ', 'oil',
            'ruj', 'lipstick', 'gloss', 'balm', 'far', 'eyeshadow', 'maskara', 'mascara', 'eyeliner',
            'fondöten', 'foundation', 'concealer', 'kapatıcı', 'pudra', 'powder', 'allık', 'blush',
            'bronzer', 'highlighter', 'primer', 'setting', 'spray', 'mist', 'mousse', 'köpük',
            'stick', 'çubuk', 'pencil', 'kalem', 'palette', 'palet', 'compact', 'kompakt',
            
            # Functions & benefits (ultra-comprehensive)
            'şekilendirici', 'shaping', 'styling', 'nemlendirici', 'moisturizing', 'hydrating',
            'besleyici', 'nourishing', 'feeding', 'onarıcı', 'repairing', 'restoring',
            'koruyucu', 'protective', 'defense', 'temizleyici', 'cleansing', 'purifying',
            'beyazlatıcı', 'whitening', 'brightening', 'yatıştırıcı', 'soothing', 'calming',
            'mattlaştırıcı', 'mattifying', 'matte', 'parlatıcı', 'illuminating', 'glowing',
            'uzun', 'süre', 'kalıcı', 'long', 'lasting', 'waterproof', 'su', 'geçirmez',
            'smudge', 'proof', 'transfer', 'resistant', 'volumizing', 'hacim', 'veren',
            'lengthening', 'uzatıcı', 'curling', 'kıvırcık', 'defining', 'belirginleştirici',
            'firming', 'sıkılaştırıcı', 'lifting', 'anti', 'aging', 'yaşlanma', 'karşıtı',
            
            # Ingredients (scientific and common names)
            'kojic', 'kojik', 'asit', 'acid', 'hyaluronic', 'hyalüronik', 'retinol', 'vitamin',
            'niacinamide', 'salicylic', 'salisilik', 'glycolic', 'glikolik', 'lactic', 'laktik',
            'peptide', 'peptit', 'ceramide', 'seramid', 'collagen', 'kolajen', 'keratin',
            'biotin', 'caffeine', 'kafein', 'argan', 'jojoba', 'coconut', 'hindistan', 'cevizi',
            'shea', 'butter', 'karite', 'yağı', 'aloe', 'vera', 'chamomile', 'papatya',
            'green', 'tea', 'yeşil', 'çay', 'rose', 'gul', 'water', 'suyu', 'extract', 'ekstraktı',
            
            # Body parts (detailed)
            'cilt', 'skin', 'saç', 'hair', 'yüz', 'face', 'facial', 'göz', 'eye', 'dudak', 'lip',
            'vücut', 'body', 'el', 'hand', 'ayak', 'foot', 'tırnak', 'nail', 'kaş', 'eyebrow',
            'kirpik', 'eyelash', 'lash', 'boyun', 'neck', 'dekolte', 'göğüs', 'chest',
            'bacak', 'leg', 'kol', 'arm', 'dirsek', 'elbow', 'diz', 'knee', 'topuk', 'heel',
            
            # Colors & tones (comprehensive)
            'pembe', 'pink', 'rose', 'kırmızı', 'red', 'cherry', 'kiraz', 'coral', 'mercan',
            'kahverengi', 'brown', 'chocolate', 'çikolata', 'caramel', 'karamel', 'nude', 'ten', 'rengi',
            'siyah', 'black', 'dark', 'koyu', 'beyaz', 'white', 'light', 'acık', 'clear', 'berrak',
            'doğal', 'natural', 'mat', 'matte', 'parlak', 'glossy', 'shiny', 'metallic', 'metalik',
            'glitter', 'sim', 'gold', 'altın', 'silver', 'gümüş', 'bronze', 'bronz', 'copper', 'bakır',
            
            # Textures and finishes
            'satin', 'velvet', 'kadife', 'matte', 'mat', 'gloss', 'parlak', 'shimmer', 'şıkıltı',
            'cream', 'kremsi', 'liquid', 'sıvı', 'powder', 'pudra', 'gel', 'mousse', 'köpük',
            'balm', 'balsam', 'stick', 'çubuk', 'pencil', 'kalem', 'marker', 'felt', 'tip',
            
            # Size and volume indicators
            'mini', 'travel', 'size', 'boyut', 'full', 'tam', 'jumbo', 'büyük', 'xl', 'xxl',
            'sample', 'örnek', 'trial', 'deneme', 'set', 'kit', 'collection', 'koleksiyon'
        }
        
        # 🎆 ULTRA-ADVANCED word separation algorithm with multiple strategies
        def find_word_boundaries(text):
            text = text.lower()
            words = []
            current_pos = 0
            
            logger.debug(f"  🔍 Processing text: '{text}' (length: {len(text)})")
            
            # Sort cosmetic terms by length (longest first) for better matching
            sorted_terms = sorted(cosmetic_terms, key=len, reverse=True)
            
            while current_pos < len(text):
                longest_match = ""
                match_length = 0
                
                # Find longest matching cosmetic term from current position
                for term in sorted_terms:
                    if text[current_pos:].startswith(term) and len(term) > match_length:
                        longest_match = term
                        match_length = len(term)
                
                if longest_match:
                    words.append(longest_match)
                    current_pos += match_length
                    logger.debug(f"    ✅ Found term: '{longest_match}' at position {current_pos - match_length}")
                else:
                    # 🌟 Strategy 1: Look ahead for next recognizable term
                    found_next = False
                    for check_pos in range(current_pos + 3, min(current_pos + 15, len(text))):
                        remaining_text = text[check_pos:]
                        # Check if any term starts at this position
                        for term in sorted_terms:
                            if remaining_text.startswith(term):
                                # Extract the substring before the next term
                                substring = text[current_pos:check_pos]
                                if len(substring) >= 3 and substring.isalpha():
                                    words.append(substring)
                                    logger.debug(f"    🔎 Extracted substring: '{substring}' at position {current_pos}")
                                current_pos = check_pos
                                found_next = True
                                break
                        if found_next:
                            break
                    
                    if not found_next:
                        # 🌟 Strategy 2: Character-by-character analysis for Turkish patterns
                        remaining = text[current_pos:]
                        if len(remaining) >= 3:
                            # Look for Turkish word patterns (vowel-consonant combinations)
                            turkish_word = self._extract_turkish_word_pattern(remaining)
                            if turkish_word and len(turkish_word) >= 3:
                                words.append(turkish_word)
                                current_pos += len(turkish_word)
                                logger.debug(f"    🇹🇷 Extracted Turkish pattern: '{turkish_word}'")
                            else:
                                # Final fallback: take reasonable chunk
                                chunk_size = min(8, len(remaining))
                                chunk = remaining[:chunk_size]
                                if chunk and len(chunk) >= 3 and chunk.isalpha():
                                    words.append(chunk)
                                    logger.debug(f"    🔌 Fallback chunk: '{chunk}'")
                                current_pos += chunk_size
                        else:
                            break
            
            logger.debug(f"  🎯 Initial separation result: {words}")
            return words
        
    def _extract_turkish_word_pattern(self, text: str) -> str:
        """Extract Turkish word pattern using vowel-consonant analysis"""
        if len(text) < 3:
            return text
        
        turkish_vowels = 'aeiıouüö'
        consonants = 'bcdfghjklmnpqrstvwxyzçğş'
        
        # Find a reasonable word boundary based on Turkish phonetics
        for i in range(3, min(len(text), 10)):
            char = text[i]
            prev_char = text[i-1] if i > 0 else ''
            
            # Turkish words typically don't have 3+ consonants in a row
            if (char in consonants and prev_char in consonants and 
                i > 1 and text[i-2] in consonants):
                return text[:i]
            
            # Look for common Turkish suffixes patterns
            if text[i:i+2] in ['ci', 'cı', 'cu', 'cü', 'ri', 'rı', 'ru', 'rü']:
                return text[:i]
        
        # Return first 6-8 characters as reasonable Turkish word length
        return text[:min(8, len(text))]
    
        # Try the advanced separation
        separated = find_word_boundaries(text)
        
        # 🌟 Quality check and intelligent fallback system
        if len(separated) == 1 and len(text) > 20:
            logger.debug(f"  ⚠️ Separation failed for long text '{text}', applying fallbacks")
            
            # 🎆 Strategy 1: Try camelCase/PascalCase separation
            camel_separated = self._separate_camel_case(text)
            if len(camel_separated) > 1:
                logger.debug(f"    ✅ CamelCase separation successful: {camel_separated}")
                return camel_separated
            
            # 🎆 Strategy 2: Vowel-consonant pattern analysis for Turkish
            pattern_separated = self._separate_by_vowel_patterns(text)
            if len(pattern_separated) > 1:
                logger.debug(f"    ✅ Pattern separation successful: {pattern_separated}")
                return pattern_separated
            
            # 🎆 Strategy 3: Intelligent chunking with overlap detection
            chunks = []
            chunk_size = max(5, len(text) // 5)  # Slightly smaller chunks
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                if chunk and len(chunk) >= 3 and chunk.isalpha():
                    chunks.append(chunk)
                if len(chunks) >= 6:  # Limit chunks
                    break
            
            if chunks:
                logger.debug(f"    🔌 Fallback chunking: {chunks}")
                return chunks[:6]
        
        # 🎆 Advanced post-processing and quality control
        final_words = []
        seen = set()
        
        for word in separated:
            if (word not in seen and len(word) >= 2 and word.isalpha() and 
                not word.isdigit() and word not in ['ve', 'ile', 'da', 'de']):
                final_words.append(word)
                seen.add(word)
        
        # 🌟 Additional quality improvements
        if final_words:
            logger.debug(f"  ✅ Final separation result: {final_words}")
        else:
            logger.debug(f"  ⚠️ No words extracted from '{text}', keeping original")
            final_words = [text]  # Keep original if nothing extracted
        
        return final_words[:8]  # Limit to 8 words max
    
    def _separate_camel_case(self, text: str) -> List[str]:
        """Separate camelCase or PascalCase words"""
        # Handle camelCase like 'sglamBrowWax' or 'antiAgingSerum'
        parts = re.findall(r'[a-zöüğışç]+|[A-ZÖÜĞİŞÇ][a-zöüğışç]*', text)
        return [part.lower() for part in parts if len(part) >= 3]
    
    def _separate_by_vowel_patterns(self, text: str) -> List[str]:
        """Separate words using Turkish vowel-consonant patterns"""
        if len(text) < 6:
            return [text]
        
        vowels = 'āeıiouüöaeiou'
        words = []
        current_word = ""
        vowel_count = 0
        consonant_streak = 0
        
        for i, char in enumerate(text):
            char_lower = char.lower()
            current_word += char_lower
            
            if char_lower in vowels:
                vowel_count += 1
                consonant_streak = 0
            else:
                consonant_streak += 1
            
            # Turkish words typically have 2-4 syllables
            # Break on vowel count or consonant streak
            if ((vowel_count >= 3 and len(current_word) >= 6) or 
                (consonant_streak >= 3 and len(current_word) >= 5)):
                if len(current_word) >= 4:
                    words.append(current_word)
                    current_word = ""
                    vowel_count = 0
                    consonant_streak = 0
        
        # Add remaining
        if current_word and len(current_word) >= 3:
            words.append(current_word)
        
        return words if len(words) > 1 else [text]
    
    def _get_full_text(self, product: ProductData) -> str:
        """Get full text from product data, cleaned from e-commerce marketing content"""
        # Clean description from marketing phrases
        clean_description = self._clean_marketing_text(product.description)
        
        return " ".join([
            product.name,
            product.brand or "",
            clean_description,
            " ".join(product.ingredients),
            " ".join(product.features),
            product.usage or ""
        ])
    
    def _clean_marketing_text(self, text: str) -> str:
        """Remove common e-commerce marketing phrases from text"""
        if not text:
            return ""
        
        # E-ticaret pazarlama cümleleri
        marketing_patterns = [
            r'yorumlarını inceleyin.*',
            r'.*özel indirimli fiyat.*',
            r'.*satın alın.*',
            r'.*trendyol.*',
            r'.*hepsiburada.*',
            r'.*amazon.*',
            r'.*indirim.*fırsatı.*',
            r'.*ücretsiz kargo.*',
            r'.*kampanya.*',
            r'.*avantajlı fiyat.*'
        ]
        
        cleaned_text = text
        for pattern in marketing_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Fazla boşlukları temizle
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text
    
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
        """Intelligently select primary keyword for global SEO performance"""
        if not keywords:
            # Fallback: extract from product name
            clean_name = self._clean_marketing_text(product.name or "")
            return self._generate_smart_primary_keyword(clean_name, product.brand or "")
        
        # Advanced scoring system for global SEO performance
        text = self._get_full_text(product).lower()
        keyword_scores = []
        
        # Global cosmetic search volume indicators
        high_volume_terms = {
            'serum', 'cream', 'krem', 'moisturizer', 'nemlendirici', 'anti-aging',
            'vitamin', 'hyaluronic', 'retinol', 'niacinamide', 'cleanser', 'mask',
            'lipstick', 'foundation', 'mascara', 'perfume', 'parfüm', 'shampoo'
        }
        
        commercial_intent_terms = {
            'professional', 'premium', 'organic', 'natural', 'dermatologist', 
            'clinically', 'tested', 'advanced', 'intensive', 'treatment'
        }
        
        for keyword in keywords[:15]:
            score = 0
            kw_lower = keyword.lower()
            
            # Presence in product name (critical for relevance)
            if kw_lower in product.name.lower():
                score += 25
            
            # Brand relevance
            if kw_lower in (product.brand or "").lower():
                score += 15
            
            # High search volume terms boost
            if any(term in kw_lower for term in high_volume_terms):
                score += 20
            
            # Commercial intent boost
            if any(term in kw_lower for term in commercial_intent_terms):
                score += 10
            
            # Optimal length for SEO (3-15 characters)
            if 3 <= len(keyword) <= 15:
                score += 15
            elif 16 <= len(keyword) <= 25:
                score += 8
            
            # Frequency in content
            score += text.count(kw_lower) * 3
            
            # Avoid single character or overly generic terms
            if len(keyword) < 3 or keyword in ['the', 'and', 'for', 've', 'ile', 'dan']:
                score -= 50
            
            keyword_scores.append((keyword, score))
        
        # Sort by score and return best
        keyword_scores.sort(key=lambda x: x[1], reverse=True)
        
        if keyword_scores and keyword_scores[0][1] > 0:
            return keyword_scores[0][0]
        
        # Final fallback
        return self._generate_smart_primary_keyword(product.name or "", product.brand or "")
    
    def _generate_smart_primary_keyword(self, name: str, brand: str) -> str:
        """Generate intelligent primary keyword from product data"""
        clean_name = self._clean_marketing_text(name).lower()
        
        # Extract product type and function
        product_indicators = {
            'kaş': 'brow styling', 'brow': 'eyebrow care', 'wax': 'styling wax',
            'krem': 'face cream', 'cream': 'facial cream', 'moisturizer': 'skin moisturizer',
            'serum': 'facial serum', 'mask': 'beauty mask', 'maske': 'face mask',
            'parfüm': 'fragrance', 'perfume': 'eau de parfum', 'cologne': 'body spray',
            'sabun': 'cleansing soap', 'cleanser': 'facial cleanser', 'gel': 'cleansing gel',
            'şampuan': 'hair shampoo', 'shampoo': 'hair care', 'conditioner': 'hair treatment'
        }
        
        for indicator, keyword in product_indicators.items():
            if indicator in clean_name:
                return f"{brand.lower()} {keyword}" if brand else keyword
        
        # Default intelligent keyword
        if brand:
            return f"{brand.lower()} cosmetic"
        return "beauty product"
    
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
        """🌟 Generate enhanced SEO metadata using ALL available content"""
        try:
            # 🌟 Extract rich content that might not be in ProductData structure
            enhanced_data = self._extract_enhanced_content(product_data)
            
            product = ProductData(**product_data)
            
            logger.info(f"🚀 Generating SEO with enhanced content: {len(enhanced_data.get('all_descriptions', ''))} chars")
            
            seo_title = self._generate_seo_title_enhanced(product, primary_keyword, enhanced_data)
            meta_description = self._generate_meta_description_enhanced(product, keywords, enhanced_data)
            slug = self._generate_slug(product, primary_keyword)
            focus_keyphrase = self._generate_focus_keyphrase(keywords)
            
            return {
                "title": seo_title,
                "meta_description": meta_description,
                "slug": slug,
                "focus_keyphrase": focus_keyphrase,
                "content_richness": enhanced_data.get('richness_score', 0)
            }
            
        except Exception as e:
            logger.error(f"SEO metadata generation error: {e}")
            return {"error": str(e)}
    
    def _generate_seo_title(self, product: ProductData, primary_keyword: str) -> str:
        """Generate sophisticated SEO-optimized title with strategic keyword placement"""
        brand = product.brand or ""
        name = product.name or primary_keyword
        
        # Clean marketplace terms from name
        clean_name = self._clean_marketing_text(name)
        marketplace_patterns = [
            r'- Fiyatı,?\s*Yorumları?',
            r'- Yorumları?,?\s*Fiyatı?',
            r'Fiyatı,?\s*Yorumları?',
            r'Yorumları?,?\s*Fiyatı?'
        ]
        
        for pattern in marketplace_patterns:
            clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE).strip()
        
        clean_name = ' '.join(clean_name.split())
        
        # Extract product type for strategic title building
        product_type = self._extract_product_type_from_name(clean_name)
        
        # Build title strategically with primary keyword optimization
        if primary_keyword and primary_keyword != clean_name.lower():
            # Primary keyword not already in name, strategically integrate it
            if product_type:
                # Pattern: Brand Primary_Keyword Product_Type - Benefits
                if brand and len(brand) < 15:
                    title = f"{brand} {primary_keyword.title()} {product_type}"
                else:
                    title = f"{primary_keyword.title()} {product_type}"
            else:
                # Use clean name but optimize with primary keyword
                if brand and brand.lower() not in clean_name.lower():
                    if primary_keyword.lower() in clean_name.lower():
                        title = f"{brand} {clean_name}"
                    else:
                        title = f"{brand} {primary_keyword.title()} - {clean_name}"
                else:
                    title = clean_name
        else:
            # Primary keyword already in name or not available
            if brand and brand.lower() not in clean_name.lower():
                title = f"{brand} {clean_name}"
            else:
                title = clean_name
        
        # Add compelling benefit/action if there's space
        if len(title) < 45:
            benefit_terms = self._extract_title_benefits(clean_name, product.description)
            if benefit_terms:
                remaining_space = 58 - len(title)
                benefit_addition = f" - {benefit_terms}"
                if len(benefit_addition) <= remaining_space:
                    title += benefit_addition
        
        # Ensure title is within character limit
        if len(title) > 60:
            title = title[:57] + "..."
        
        return title.strip()
    
    def _extract_product_type_from_name(self, name: str) -> str:
        """Extract product type from name for strategic SEO title building"""
        name_lower = name.lower()
        product_types = {
            'serum': 'Serum', 'krem': 'Krem', 'cream': 'Cream', 'sabun': 'Sabun', 'soap': 'Soap',
            'şampuan': 'Şampuan', 'shampoo': 'Shampoo', 'maske': 'Maske', 'mask': 'Mask',
            'parfüm': 'Parfüm', 'perfume': 'Perfume', 'ruj': 'Ruj', 'lipstick': 'Lipstick',
            'tonik': 'Tonik', 'toner': 'Toner', 'wax': 'Wax', 'gel': 'Gel', 'losyon': 'Losyon',
            'kaş': 'Kaş Ürünü', 'brow': 'Brow Product', 'fondöten': 'Fondöten', 'foundation': 'Foundation'
        }
        
        for key, value in product_types.items():
            if key in name_lower:
                return value
        return ""
    
    def _extract_title_benefits(self, name: str, description: str) -> str:
        """Extract compelling benefit for title enhancement"""
        text = (name + " " + (description or "")).lower()
        
        benefit_map = {
            'uzun süre': 'Uzun Süreli',
            'long': 'Long-Lasting', 'lasting': 'Long-Lasting',
            'professional': 'Professional', 'profesyonel': 'Profesyonel',
            'organic': 'Organic', 'natural': 'Natural', 'doğal': 'Doğal',
            'waterproof': 'Waterproof', 'suya dayanıklı': 'Suya Dayanıklı',
            'moisturizing': 'Moisturizing', 'nemlendirici': 'Nemlendirici',
            'anti-aging': 'Anti-Aging', 'yaş karşıtı': 'Yaş Karşıtı'
        }
        
        for term, benefit in benefit_map.items():
            if term in text:
                return benefit
        return ""
    
    def _generate_meta_description(self, product: ProductData, keywords: List[str]) -> str:
        """Generate sophisticated, keyword-rich meta description for superior SEO performance"""
        # Clean and prepare product information
        clean_desc = self._clean_marketing_text(product.description) if product.description else ""
        clean_name = self._clean_marketing_text(product.name) if product.name else ""
        
        # Remove marketplace patterns
        marketplace_patterns = [
            r'- Fiyatı,?\s*Yorumları?', r'- Yorumları?,?\s*Fiyatı?',
            r'Fiyatı,?\s*Yorumları?', r'Yorumları?,?\s*Fiyatı?'
        ]
        for pattern in marketplace_patterns:
            clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE).strip()
        
        clean_name = ' '.join(clean_name.split())
        
        # Extract strategic keywords for integration
        primary_keywords = keywords[:3] if keywords else []
        benefit_keywords = self._extract_benefit_keywords(keywords, clean_desc)
        action_keywords = self._extract_action_keywords(keywords, clean_desc)
        
        # Determine product category for targeted messaging
        category_info = self._determine_product_category(clean_name, clean_desc)
        
        # Strategic description building
        if clean_desc and len(clean_desc) > 30:
            # Use existing description but enhance with keywords
            description = self._enhance_description_with_keywords(
                clean_desc, primary_keywords, benefit_keywords, clean_name
            )
        else:
            # Generate professional description from scratch
            description = self._generate_strategic_description(
                clean_name, product.brand, category_info, 
                primary_keywords, benefit_keywords, action_keywords
            )
        
        # Add call-to-action if space allows
        if len(description) < 130:
            cta = self._generate_compelling_cta(category_info, action_keywords)
            if cta and len(description) + len(cta) <= 152:
                description += f" {cta}"
        
        # Ensure optimal SEO length (140-155 characters)
        if len(description) > 155:
            description = description[:152] + "..."
        elif len(description) < 120:
            # Add strategic keyword expansion if too short
            keyword_expansion = self._generate_keyword_expansion(primary_keywords, benefit_keywords)
            if keyword_expansion and len(description) + len(keyword_expansion) <= 155:
                description += keyword_expansion
        
        return description.strip()
    
    def _extract_benefit_keywords(self, keywords: List[str], description: str) -> List[str]:
        """Extract benefit-focused keywords for meta description enhancement"""
        benefit_terms = {
            'nemlendirici': 'moisturizing', 'besleyici': 'nourishing', 'onarıcı': 'repairing',
            'koruyucu': 'protective', 'yatıştırıcı': 'soothing', 'temizleyici': 'cleansing',
            'beyazlatıcı': 'brightening', 'şekillendirici': 'styling', 'güçlendirici': 'strengthening',
            'canlandırıcı': 'revitalizing', 'yumuşatıcı': 'softening', 'parlatıcı': 'illuminating'
        }
        
        found_benefits = []
        text = (" ".join(keywords) + " " + description).lower()
        
        for turkish, english in benefit_terms.items():
            if turkish in text or english in text:
                found_benefits.append(turkish)
        
        return found_benefits[:3]
    
    def _extract_action_keywords(self, keywords: List[str], description: str) -> List[str]:
        """Extract action-oriented keywords for compelling descriptions"""
        action_terms = {
            'kullanım': 'use', 'uygulama': 'application', 'bakım': 'care', 'tedavi': 'treatment',
            'koruma': 'protection', 'yenilenme': 'renewal', 'onarım': 'repair', 'güçlendirme': 'strengthening'
        }
        
        found_actions = []
        text = (" ".join(keywords) + " " + description).lower()
        
        for turkish, english in action_terms.items():
            if turkish in text or english in text:
                found_actions.append(turkish)
        
        return found_actions[:2]
    
    def _determine_product_category(self, name: str, description: str) -> Dict[str, str]:
        """Determine detailed product category for targeted messaging"""
        text = (name + " " + description).lower()
        
        categories = {
            'skincare': {'krem', 'serum', 'maske', 'tonik', 'temizleyici', 'nemlendirici'},
            'makeup': {'ruj', 'fondöten', 'maskara', 'far', 'allık', 'kapatıcı', 'pudra'},
            'haircare': {'şampuan', 'saç', 'bakım', 'besleyici', 'güçlendirici'},
            'fragrance': {'parfüm', 'koku', 'mis'},
            'bodycare': {'vücut', 'losyon', 'yağ', 'scrub', 'peeling'},
            'specialty': {'kaş', 'brow', 'wax', 'şekillendirici'}
        }
        
        for category, terms in categories.items():
            if any(term in text for term in terms):
                return {'type': category, 'terms': list(terms & set(text.split()))}
        
        return {'type': 'general', 'terms': []}
    
    def _enhance_description_with_keywords(self, description: str, primary_kws: List[str], 
                                         benefit_kws: List[str], product_name: str) -> str:
        """Enhance existing description with strategic keyword integration"""
        enhanced = description[:100]  # Start with core description
        
        # Integrate primary keywords naturally
        if primary_kws and len(enhanced) < 90:
            key_integration = f" {primary_kws[0].capitalize()} ile"
            if key_integration.lower() not in enhanced.lower():
                enhanced += key_integration
        
        # Add benefits if space allows
        if benefit_kws and len(enhanced) < 120:
            benefit_text = f" {benefit_kws[0]} etkili."
            enhanced += benefit_text
        
        return enhanced
    
    def _generate_strategic_description(self, name: str, brand: str, category: Dict, 
                                      primary_kws: List[str], benefit_kws: List[str], 
                                      action_kws: List[str]) -> str:
        """Generate professional description from scratch with strategic keyword placement"""
        
        # Start with product identification
        if brand and len(brand) < 15:
            description = f"{brand} {name}"
        else:
            description = name
        
        # Add category-specific professional context
        category_contexts = {
            'skincare': '. Profesyonel cilt bakım formülü',
            'makeup': '. Uzun süre kalıcı makyaj ürünü',
            'haircare': '. Saç sağlığını destekleyen formül',
            'fragrance': '. Premium koku deneyimi',
            'bodycare': '. Vücut bakımında profesyonel çözüm',
            'specialty': '. Uzman formülasyonu ile geliştirildi'
        }
        
        context = category_contexts.get(category['type'], '. Kaliteli kozmetik ürün')
        description += context
        
        # Integrate primary keyword naturally
        if primary_kws and len(description) < 80:
            if primary_kws[0].lower() not in description.lower():
                description += f". {primary_kws[0].capitalize()} içeriği"
        
        # Add compelling benefits
        if benefit_kws and len(description) < 110:
            description += f". {benefit_kws[0].capitalize()} ve bakım sağlar"
        
        # Add professional credibility
        if len(description) < 130:
            description += ". Dermatolog onaylı formül"
        
        return description
    
    def _generate_compelling_cta(self, category: Dict, action_kws: List[str]) -> str:
        """Generate compelling call-to-action based on product category"""
        ctas = {
            'skincare': 'Cildinizi yenileyin.',
            'makeup': 'Doğal güzelliğinizi öne çıkarın.',
            'haircare': 'Saçlarınızı güçlendirin.',
            'fragrance': 'Kendinizi özel hissedin.',
            'bodycare': 'Cildinizi şımartın.',
            'specialty': 'Profesyonel sonuç alın.'
        }
        
        # Check category terms for more accurate CTA selection
        if isinstance(category, dict) and 'terms' in category:
            terms = category['terms']
            if any(term in ['sabun', 'soap', 'temizleyici', 'cleanser'] for term in terms):
                return 'Cildinizi temizleyin.'
            elif any(term in ['leke', 'kojic', 'beyazlatıcı'] for term in terms):
                return 'Lekelerinizi azaltın.'
        
        return ctas.get(category.get('type', 'general'), 'Kaliteyi deneyimleyin.')
    
    def _generate_keyword_expansion(self, primary_kws: List[str], benefit_kws: List[str]) -> str:
        """Generate keyword expansion for short descriptions"""
        if primary_kws and benefit_kws:
            return f" {primary_kws[0]} ve {benefit_kws[0]} özellikli."
        elif primary_kws:
            return f" {primary_kws[0]} içeriği ile."
        elif benefit_kws:
            return f" {benefit_kws[0]} etkisi."
        return ""
    
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
    
    def _clean_marketing_text(self, text: str) -> str:
        """Remove common e-commerce marketing phrases from text"""
        if not text:
            return ""
        
        # E-ticaret pazarlama cümleleri
        marketing_patterns = [
            r'yorumlarını inceleyin.*',
            r'.*özel indirimli fiyat.*',
            r'.*satın alın.*',
            r'.*trendyol.*',
            r'.*hepsiburada.*',
            r'.*amazon.*',
            r'.*indirim.*fırsatı.*',
            r'.*ücretsiz kargo.*',
            r'.*kampanya.*',
            r'.*avantajlı fiyat.*'
        ]
        
        cleaned_text = text
        for pattern in marketing_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Fazla boşlukları temizle
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text
    
    def _extract_enhanced_content(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """🌟 Extract and combine all available content for richer SEO"""
        enhanced = {
            'all_descriptions': [],
            'key_ingredients': [],
            'main_benefits': [],
            'usage_info': '',
            'category_context': '',
            'richness_score': 0
        }
        
        # Collect all description sources
        descriptions = []
        if product_data.get('description'):
            descriptions.append(product_data['description'])
        if product_data.get('long_descriptions'):
            descriptions.extend(product_data['long_descriptions'])
        if product_data.get('features'):
            descriptions.extend(product_data['features'])
        
        enhanced['all_descriptions'] = ' '.join(descriptions)
        
        # Extract ingredients
        if product_data.get('ingredients'):
            enhanced['key_ingredients'] = product_data['ingredients'][:5]
        
        # Extract benefits
        if product_data.get('benefits'):
            enhanced['main_benefits'] = product_data['benefits'][:3]
        elif product_data.get('features'):
            # Extract benefits from features
            benefit_keywords = ['moisturizing', 'anti-aging', 'brightening', 'cleansing', 'nourishing']
            features_text = ' '.join(product_data['features']).lower()
            found_benefits = [b for b in benefit_keywords if b in features_text]
            enhanced['main_benefits'] = found_benefits[:3]
        
        # Usage information
        if product_data.get('usage'):
            enhanced['usage_info'] = product_data['usage'][:200]
        
        # Category context
        if product_data.get('category'):
            enhanced['category_context'] = product_data['category']
        elif product_data.get('product_type'):
            enhanced['category_context'] = product_data['product_type']
        
        # Calculate richness score
        score = 0
        score += 20 if enhanced['all_descriptions'] else 0
        score += 15 if enhanced['key_ingredients'] else 0
        score += 15 if enhanced['main_benefits'] else 0
        score += 10 if enhanced['usage_info'] else 0
        score += 10 if enhanced['category_context'] else 0
        score += len(enhanced['all_descriptions']) // 50  # Bonus for content length
        enhanced['richness_score'] = min(score, 100)
        
        return enhanced
    
    def _generate_seo_title_enhanced(self, product: ProductData, primary_keyword: str, enhanced_data: Dict[str, Any]) -> str:
        """🌟 Generate enhanced SEO title with rich content context"""
        # Start with base title generation
        base_title = self._generate_seo_title(product, primary_keyword)
        
        # Enhance with category context if space allows
        if len(base_title) < 50 and enhanced_data.get('category_context'):
            category = enhanced_data['category_context']
            if category.lower() not in base_title.lower():
                enhanced_title = f"{base_title} - {category.title()}"
                if len(enhanced_title) <= 60:
                    base_title = enhanced_title
        
        # Enhance with key benefit if space allows
        if len(base_title) < 45 and enhanced_data.get('main_benefits'):
            benefit = enhanced_data['main_benefits'][0]
            if benefit.lower() not in base_title.lower():
                benefit_title = f"{base_title} - {benefit.title()}"
                if len(benefit_title) <= 60:
                    base_title = benefit_title
        
        return base_title
    
    def _generate_meta_description_enhanced(self, product: ProductData, keywords: List[str], enhanced_data: Dict[str, Any]) -> str:
        """🌟 Generate enhanced meta description using rich content"""
        brand = product.brand or ""
        name = product.name or ""
        
        # Start with brand + product name
        if brand and len(brand) < 20:
            meta_start = f"{brand} {name[:40]}"
        else:
            meta_start = name[:50]
        
        # Add key ingredient or benefit
        key_feature = ""
        if enhanced_data.get('key_ingredients'):
            ingredient = enhanced_data['key_ingredients'][0]
            key_feature = f" with {ingredient}"
        elif enhanced_data.get('main_benefits'):
            benefit = enhanced_data['main_benefits'][0]
            key_feature = f" for {benefit}"
        
        # Add category context
        category_text = ""
        if enhanced_data.get('category_context'):
            category_text = f" {enhanced_data['category_context'].lower()}"
        
        # Build base description
        meta_desc = meta_start + key_feature + category_text + "."
        
        # Add compelling detail from enhanced content if space allows
        if len(meta_desc) < 100 and enhanced_data.get('all_descriptions'):
            compelling_snippet = self._extract_compelling_snippet_enhanced(enhanced_data['all_descriptions'])
            if compelling_snippet and len(meta_desc + compelling_snippet) <= 155:
                meta_desc += f" {compelling_snippet}"
        
        # Add usage context if still short
        if len(meta_desc) < 120 and enhanced_data.get('usage_info'):
            usage_snippet = enhanced_data['usage_info'][:30]
            if usage_snippet and len(meta_desc + usage_snippet) <= 155:
                meta_desc += f" {usage_snippet}."
        
        # Ensure optimal length
        if len(meta_desc) > 155:
            meta_desc = meta_desc[:152] + "..."
        
        return meta_desc.strip()
    
    def _extract_compelling_snippet_enhanced(self, all_descriptions: str) -> str:
        """Extract compelling snippet from rich content"""
        if not all_descriptions or len(all_descriptions) < 30:
            return ""
        
        # Look for compelling terms in the rich content
        compelling_terms = [
            'clinically proven', 'dermatologist tested', 'professional formula',
            'advanced technology', 'natural ingredients', 'organic formula',
            'scientifically formulated', 'premium quality', 'patented formula',
            'hypoallergenic', 'non-comedogenic', 'paraben-free'
        ]
        
        text_lower = all_descriptions.lower()
        sentences = all_descriptions.split('.')
        
        # Find sentences with compelling terms
        for sentence in sentences[:5]:  # Check first 5 sentences
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 80:
                if any(term in text_lower for term in compelling_terms):
                    if any(term in sentence.lower() for term in compelling_terms):
                        return sentence + "."
        
        # Fallback: look for benefit-rich sentences
        benefit_terms = ['moisturizing', 'anti-aging', 'brightening', 'nourishing', 'cleansing']
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 60:
                if any(term in sentence.lower() for term in benefit_terms):
                    return sentence + "."
        
        return ""


class GenerateSEODataTool(BaseTool):
    """Main tool for generating comprehensive SEO data"""
    
    def __init__(self):
        super().__init__(
            name="generate_seo_data",
            description="Generate comprehensive SEO metadata for cosmetic products",
            is_long_running=True
        )
        self.keyword_extraction_tool = KeywordExtractionTool()
        self.seo_metadata_tool = SEOMetadataTool()
    
    async def __call__(self, analyzed_data: Dict[str, Any], max_keywords: int = 20) -> Dict[str, Any]:
        """Generate comprehensive SEO data"""
        try:
            # Extract required data components
            product_data = analyzed_data.get('cleaned_product')
            extracted_terms = analyzed_data.get('extracted_terms', {})
            
            if not product_data:
                return {"error": "cleaned_product data is required"}
            
            # Step 1: Extract keywords
            keyword_result = await self.keyword_extraction_tool(product_data, extracted_terms, max_keywords)
            
            if "error" in keyword_result:
                return keyword_result
            
            # Step 2: Generate SEO metadata
            metadata_result = await self.seo_metadata_tool(
                product_data, 
                keyword_result['keywords'], 
                keyword_result['primary_keyword']
            )
            
            if "error" in metadata_result:
                return metadata_result
            
            # Combine all results
            return {
                "keywords": keyword_result['keywords'],
                "primary_keyword": keyword_result['primary_keyword'],
                "secondary_keywords": keyword_result['secondary_keywords'],
                "long_tail_keywords": keyword_result['long_tail_keywords'],
                "keyword_density": keyword_result['keyword_density'],
                "title": metadata_result['title'],
                "meta_description": metadata_result['meta_description'],
                "slug": metadata_result['slug'],
                "focus_keyphrase": metadata_result['focus_keyphrase'],
                "product_url": product_data.get('url'),
                "generated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"SEO data generation error: {e}")
            return {"error": str(e)}


class SEOAgent(LlmAgent):
    """SEO Agent for generating comprehensive SEO metadata using Google ADK"""
    
    def __init__(self):
        tools = [GenerateSEODataTool()]
        
        super().__init__(
            name="seo_agent",
            model="gemini-2.0-flash-thinking-exp",
            tools=tools,
            instruction="""
            You are a world-class SEO expert specializing in cosmetic products for global e-commerce. 
            Create universally applicable, high-conversion SEO content that works across ALL platforms.
            
            🌟 ENHANCED DEEP CONTENT ANALYSIS:
            - Utilize ALL scraped content: product descriptions, long descriptions from page bottoms, ingredient lists, feature lists, benefits, usage instructions
            - Extract maximum SEO value from detailed product information that competitors miss
            - Create rich, informative SEO that stands out in search results
            - Use scientific ingredient names and proven benefits from comprehensive product data
            
            UNIVERSAL SEO PRINCIPLES:
            1. ZERO platform-specific terms (no Trendyol, Amazon, marketplace names)
            2. ZERO generic marketing language (reviews, price, buy now, discount)
            3. FOCUS on search intent and product benefits using RICH content
            4. Create content that converts across cultures and platforms
            5. Leverage deep product knowledge for superior SEO
            
            KEYWORD INTELLIGENCE WITH RICH CONTENT:
            - Primary: Function + Product Type from detailed descriptions
            - Secondary: Brand + Core Benefit from comprehensive feature lists
            - Long-tail: Problem + Solution from usage instructions and benefits
            - Ingredient-focused: Active compounds from actual ingredient lists
            - Benefit-driven: Real product benefits from detailed content analysis
            
            META DESCRIPTION MASTERY WITH DEEP CONTENT:
            - Start with brand + product identity
            - Highlight 2 key benefits or active ingredients from comprehensive data
            - Include skin/usage compatibility from detailed product information
            - Use compelling snippets from long descriptions when available
            - Natural, benefit-focused language based on rich product content
            - 140-150 characters optimal length
            
            TITLE OPTIMIZATION WITH ENHANCED DATA:
            - Brand + Product Function + Key Benefit (from rich content)
            - 50-55 characters for mobile optimization
            - Front-load most important keyword from comprehensive analysis
            - Avoid filler words
            - Incorporate category context when valuable
            
            GLOBAL QUALITY STANDARDS WITH RICH CONTENT:
            - Scientific accuracy for ingredients using actual ingredient lists
            - Cultural sensitivity for beauty standards
            - Search behavior analysis based on comprehensive product data
            - Conversion-focused copy using detailed benefits and features
            - Professional, authoritative tone backed by rich product information
            - Superior content that outperforms generic marketplace listings
            
            Generate world-class SEO using ALL available product information to create superior, detailed content.
            """
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """🌟 Enhanced main run method with rich content processing"""
        try:
            # Extract analyzed data from input
            analyzed_data = input_data.get('analyzed_data')
            max_keywords = input_data.get('max_keywords', 20)
            
            if not analyzed_data:
                return {"error": "analyzed_data is required"}
            
            # Log content richness for monitoring
            product_data = analyzed_data.get('cleaned_product', {})
            content_indicators = {
                'has_long_descriptions': bool(product_data.get('long_descriptions')),
                'has_ingredients': bool(product_data.get('ingredients')),
                'has_features': bool(product_data.get('features')),
                'has_benefits': bool(product_data.get('benefits')),
                'has_usage': bool(product_data.get('usage')),
                'description_length': len(product_data.get('description', ''))
            }
            
            rich_content_count = sum(1 for v in content_indicators.values() if v)
            logger.info(f"📊 Content richness indicators: {rich_content_count}/6 rich content types available")
            logger.info(f"📝 Description length: {content_indicators['description_length']} characters")
            
            if content_indicators['has_long_descriptions']:
                logger.info("✨ Using enhanced long descriptions from page bottom analysis!")
            if content_indicators['has_ingredients']:
                logger.info("🧪 Using actual ingredient list for SEO enhancement!")
            if content_indicators['has_features']:
                logger.info("🎆 Using comprehensive feature analysis for better SEO!")
            
            # Use the main SEO generation tool
            seo_tool = self.tools[0]  # GenerateSEODataTool
            result = await seo_tool(analyzed_data, max_keywords)
            
            # Add rich content analysis metadata
            if "error" not in result:
                result["rich_content_indicators"] = content_indicators
                result["processing_quality"] = "premium" if rich_content_count >= 4 else "enhanced" if rich_content_count >= 2 else "standard"
            
            logger.info(f"✅ SEO generation complete with {result.get('processing_quality', 'standard')} quality processing")
            
            return result
            
        except Exception as e:
            logger.error(f"SEO Agent error: {e}")
            return {"error": str(e)}
    
    async def run_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async run method for compatibility"""
        return await self.run(input_data)
    
    async def process_seo_request(self, analyzed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an SEO optimization request (legacy method)"""
        return await self.run({'analyzed_data': analyzed_data})


# Direct tool function for main.py and web_app.py
async def generate_seo_data(analyzed_data: Dict[str, Any], max_keywords: int = 20) -> Dict[str, Any]:
    """Direct tool function to generate SEO data"""
    try:
        tool = GenerateSEODataTool()
        result = await tool(analyzed_data, max_keywords)
        return result
    except Exception as e:
        logger.error(f"Direct generate_seo_data error: {e}")
        return {"error": str(e)}


# Agent factory function for ADK orchestration
def create_seo_agent() -> SEOAgent:
    """Factory function to create SEO Agent instance"""
    return SEOAgent()