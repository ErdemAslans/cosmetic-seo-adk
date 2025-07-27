"""
🌟 ULTRA-ADVANCED Site Configurations - Comprehensive and Intelligent
Enhanced configurations optimized for each site's unique structure and anti-bot measures
Covers ALL major Turkish cosmetic e-commerce platforms with deep content extraction
"""

from config.models import SiteConfig

MODERN_SITE_CONFIGS = [
    SiteConfig(
        name="trendyol",
        base_url="https://www.trendyol.com",
        category_paths=[
            "/butik/liste/11/kozmetik",  # REAL WORKING URL - 160 products found
            "/sr?q=makyaj",  # Search: makeup
            "/sr?q=cilt+bakimi",  # Search: skincare
            "/sr?q=parfum",  # Search: perfume
            "/sr?q=sac+bakimi",  # Search: hair care
            "/sr?q=vucut+bakimi",  # Search: body care
            "/sr?q=kozmetik",  # Search: cosmetics
            "/kozmetik-x-c89",  # Category fallbacks
            "/kozmetik/makyaj-x-c105",
            "/kozmetik/cilt-bakimi-x-c104",
            "/kozmetik/parfum-x-c106"
        ],
        selectors={
            # 🎯 ULTRA-SPECIFIC Trendyol selectors - optimized for deep content extraction
            "product_link": "div.p-card-wrppr > a[href*='-p-'], .p-card-chldrn-cntnr a[href*='-p-'], .product-item a[href*='-p-']",
            "category": "div.breadcrumb a:nth-child(3), nav.breadcrumb a:nth-child(2), .breadcrumb-item:nth-child(2) a",
            "next_page": "a.pagination-next, .pagination-next, a[aria-label='Next'], .ty-pagination .next",
            
            # Product page selectors - COMPREHENSIVE
            "name": "h1.pr-new-br > span, h1.product-name, .pr-new-br span:first-child, h1",
            "brand": "h1.pr-new-br > a, a.product-brand-name-with-link, .pr-new-br a, .brand-name a",
            "price": "span.prc-dsc, span.prc-box-dscntd, .price-current, .discounted-price",
            
            # 🌟 ENHANCED content selectors for rich SEO
            "description": [
                "div.info-wrapper",
                "section.detail-desc-list", 
                "div.product-detail-info",
                "div.detail-desc-item div",
                "div.html-content",
                "div.product-description-content"
            ],
            "long_descriptions": [
                "div.product-detail-bottom .detail-desc-item",
                "div.detail-section-bottom",
                "section.product-detail-content",
                "div.rich-content",
                "div.expandable-content"
            ],
            "ingredients": [
                "div.detail-attr-item:has(span:contains('İçindekiler')) div.detail-attr-value",
                "div[data-testid='ingredients'] ul li",
                "div.ingredients-list li",
                "section:has(h3:contains('İçindekiler')) li"
            ],
            "features": [
                "ul.detail-attr-list > li",
                "div.product-features li",
                "div.benefits-list li",
                "div.detail-list li",
                "ul.feature-list li"
            ],
            "benefits": [
                "div.product-benefits li",
                "ul.benefits li",
                "div.advantages li",
                "section.benefits p"
            ],
            "usage": [
                "div.usage-instructions",
                "section:has(h3:contains('Kullanım')) p",
                "div.how-to-use",
                "div.application-method"
            ],
            "reviews": ".comment-text, .review-text, .user-comment, .comment-item .text",
            "images": "div.product-slide img[data-src], img.detail-section-img, .gallery-img, .product-images img",
            
            # Category and type detection
            "product_type": "div.breadcrumb a:last-child, .category-path a:last-child",
            "category_info": "nav.breadcrumb, .category-navigation, .breadcrumb-container"
        },
        rate_limit=1.5,
        max_pages=15,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none"
        }
    ),
    
    SiteConfig(
        name="gratis",
        base_url="https://www.gratis.com",
        category_paths=[
            "/search?q=makyaj",     # REAL WORKING URL - 73 products found
            "/search?q=kozmetik",   # Search: cosmetics
            "/search?q=cilt+bakimi", # Search: skincare  
            "/search?q=parfum",     # Search: perfume
            "/search?q=sac+bakimi", # Search: hair care
            "/search?q=vucut+bakimi", # Search: body care
            "/search?q=ruj",        # Search: lipstick
            "/search?q=fondoten",   # Search: foundation
            "/search?q=serum",      # Search: serum
            "/search?q=krem",       # Search: cream
            "/makyaj-c-1",          # Category fallbacks
            "/cilt-bakim-c-2",      
            "/parfum-c-3",
            "/sac-bakim-c-4",
            "/vucut-bakim-c-5"
        ],
        selectors={
            # 🎯 ULTRA-COMPREHENSIVE Gratis selectors - adapted for their unique structure
            "product_link": [
                "a[href*='/p/']", 
                "a[href*='-p-']", 
                "[data-testid*='product'] a", 
                ".product-card a", 
                ".product-item a", 
                ".prd-link a",
                "a[href*='/urun/']",
                ".product-wrapper a"
            ],
            "category": "nav[aria-label='breadcrumb'] a:nth-child(2), .breadcrumb a:nth-child(2), .category-breadcrumb a",
            "next_page": ".pagination-next, .page-next, a[href*='page='], button[aria-label='Next'], .load-more",
            
            # Product page selectors - ENHANCED for Gratis structure
            "name": [
                "h1[class*='product-name']", 
                "h1[class*='ProductName']", 
                "h1.product-title",
                "h1", 
                ".product-name", 
                ".product-title",
                "[data-testid='product-name']"
            ],
            "brand": [
                "a[class*='brand']", 
                "span[class*='Brand']", 
                ".brand", 
                ".product-brand",
                ".manufacturer",
                "[data-testid='brand-name']"
            ],
            "price": [
                "span[class*='price']:has-text('₺')", 
                "div[class*='Price'] span", 
                ".price", 
                ".product-price",
                ".current-price",
                "[data-testid='price']"
            ],
            
            # 🌟 DEEP CONTENT extraction for premium SEO
            "description": [
                "div[class*='description']", 
                "section[class*='Description']", 
                ".description", 
                ".product-detail",
                ".product-info",
                "div.content-wrapper",
                ".product-details-content"
            ],
            "long_descriptions": [
                "div.product-detail-tabs div.tab-content",
                "section.product-description-full",
                "div.expandable-description",
                "div.detailed-info",
                ".description-extended",
                "div.product-bottom-content"
            ],
            "ingredients": [
                "div[class*='ingredients'] li", 
                "section:has(h2:contains('İçindekiler')) li", 
                ".ingredients li",
                "div.ingredient-list li",
                "ul.components li",
                "[data-testid='ingredients'] li"
            ],
            "features": [
                "div[class*='features'] li", 
                "ul[class*='Features'] li", 
                ".features li",
                ".product-features li",
                "div.specifications li",
                ".feature-list li"
            ],
            "benefits": [
                "div.benefits li",
                "ul.advantages li",
                "div.product-benefits li",
                "section.benefits p"
            ],
            "usage": [
                "div.usage-info",
                "section:has(h3:contains('Nasıl Kullanılır')) p",
                ".usage-instructions",
                "div.how-to-use"
            ],
            "reviews": ".review-content, .reviews .review-item, .comment-text, .review-text, .user-review",
            "images": [
                "div[class*='gallery'] img", 
                "img[class*='ProductImage']", 
                ".product-image img", 
                ".gallery img",
                ".product-photos img",
                "[data-testid='product-image']"
            ],
            
            # Enhanced metadata
            "product_type": ".breadcrumb a:last-child, .category-name",
            "category_info": "nav[aria-label='breadcrumb'], .category-path"
        },
        rate_limit=10.0,  # Anti-bot koruması için çok yavaş
        max_pages=2,    # Az sayfa - dikkat çekmemek için
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "DNT": "1"
        }
    ),
    
    SiteConfig(
        name="sephora_tr",
        base_url="https://www.sephora.com.tr",
        category_paths=[
            "/makyaj-c301",         # Makeup
            "/cilt-bakimi-c302",    # Skincare
            "/parfum-c303",         # Perfume
            "/sac-bakimi-c304",     # Hair care
            "/erkek-c305",          # Men's products
            "/vucud-c306",          # Body care
            "/goz-makyaji-c307",    # Eye makeup
            "/dudak-makyaji-c308",  # Lip makeup
            "/ten-makyaji-c309",    # Face makeup
            "/anti-aging-c310",     # Anti-aging
            "/gunes-koruma-c311",   # Sun protection
            "/temizlik-c312"        # Cleansing
        ],
        selectors={
            # 🎯 PREMIUM Sephora selectors - optimized for international beauty standards
            "product_link": [
                "a.product-item-link", 
                ".product-tile a", 
                "a[href*='/p/']", 
                "[data-comp='ProductTile'] a",
                ".product-card a",
                "a[href*='/product/']"
            ],
            "next_page": "a.action.next, .pagination-next, a[aria-label='Next'], .next-page",
            
            # Premium product selectors
            "name": [
                "h1.ProductMeta__Title", 
                "h1.product-name", 
                "h1.ProductName",
                "h1", 
                ".product-title",
                "[data-testid='product-title']"
            ],
            "brand": [
                ".ProductMeta__Brand", 
                ".product-brand", 
                ".brand-name", 
                ".brand",
                ".Brand",
                "[data-testid='brand']"
            ],
            "price": [
                ".Price__Value", 
                ".product-price", 
                ".price", 
                ".current-price",
                ".Price",
                "[data-testid='price']"
            ],
            
            # 🌟 PREMIUM content extraction for luxury SEO
            "description": [
                ".ProductDetail__Description", 
                ".product-description", 
                ".description",
                ".ProductDescription",
                ".product-details",
                ".detailed-description"
            ],
            "long_descriptions": [
                ".ProductDetail__FullDescription",
                ".expandable-description",
                ".product-story",
                ".brand-story",
                ".detailed-content",
                ".rich-description"
            ],
            "ingredients": [
                ".Ingredients__Content", 
                ".ingredients-list", 
                ".ingredients li",
                ".Ingredients li",
                ".component-list li",
                "[data-testid='ingredients'] li"
            ],
            "features": [
                ".ProductBenefits li", 
                ".benefits-list li", 
                ".features li",
                ".Benefits li",
                ".key-benefits li",
                ".product-highlights li"
            ],
            "benefits": [
                ".Benefits__List li",
                ".product-benefits li",
                ".key-benefits li",
                ".advantages li"
            ],
            "usage": [
                ".HowToUse__Content",
                ".usage-instructions",
                ".application-tips",
                ".how-to-apply"
            ],
            "reviews": ".ReviewItem__Text, .review-text, .review-content, .Review__Text",
            "images": [
                ".ProductImages img", 
                ".product-gallery img", 
                ".gallery img",
                ".ProductImage img",
                "[data-testid='product-image']"
            ],
            
            # Premium metadata
            "product_type": ".breadcrumb a:last-child, .category-current",
            "category_info": ".breadcrumb, .navigation-path"
        },
        rate_limit=2.5,
        max_pages=25,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
        }
    ),
    
    SiteConfig(
        name="rossmann",
        base_url="https://www.rossmann.com.tr",
        category_paths=[
            "/cilt-bakimi",         # REAL WORKING URL - 82 products found  
            "/makyaj",              # REAL WORKING URL - 79 products found
            "/temizlik"             # REAL WORKING URL - 81 products found
        ],
        selectors={
            # 🎯 COMPREHENSIVE Rossmann selectors - pharmacy-grade precision
            "product_link": [
                "a.product-item-link", 
                ".product-tile a", 
                "a[href*='/p/']", 
                ".product-card a",
                "a[href*='/product/']",
                ".product-wrapper a"
            ],
            "next_page": "a.next, .pagination-next, li.next a, a.next-page, .next-btn",
            
            # Pharmacy-grade product selectors
            "name": [
                "h1.product-title", 
                "h1.ProductTitle",
                "h1", 
                ".product-name", 
                ".product-title",
                "[data-testid='product-name']"
            ],
            "brand": [
                "div.product-brand", 
                ".brand", 
                ".manufacturer", 
                ".brand-name",
                ".Brand",
                "[data-testid='brand']"
            ],
            "price": [
                "span.price-current", 
                ".product-price", 
                ".price-now", 
                ".current-price",
                ".Price",
                "[data-testid='price']"
            ],
            
            # 🌟 PHARMACEUTICAL-grade content extraction
            "description": [
                "div.product-description", 
                ".description-content", 
                ".description",
                ".ProductDescription",
                ".product-info",
                ".detailed-info"
            ],
            "long_descriptions": [
                "div.product-details-extended",
                ".detailed-description",
                ".product-information",
                ".pharmaceutical-info",
                ".extended-content"
            ],
            "ingredients": [
                "div.ingredients-list li", 
                ".ingredients li", 
                ".product-ingredients li",
                ".Ingredients li",
                ".components li",
                "[data-testid='ingredients'] li"
            ],
            "features": [
                "div.product-features li", 
                ".features-list li", 
                ".features li",
                ".product-specs li",
                ".specifications li"
            ],
            "benefits": [
                "div.product-benefits li",
                ".benefits li",
                ".advantages li",
                ".key-features li"
            ],
            "usage": [
                "div.usage-instructions",
                ".how-to-use",
                ".application-method",
                ".usage-info"
            ],
            "reviews": "div.review-text, .review-content, .comment-content, .Review__Content",
            "images": [
                "img.product-image", 
                ".gallery img", 
                ".product-images img",
                ".ProductImages img",
                "[data-testid='product-image']"
            ],
            
            # Pharmaceutical metadata
            "product_type": ".breadcrumb a:last-child, .category-name",
            "category_info": ".breadcrumb, .navigation-breadcrumb"
        },
        rate_limit=2.0,
        max_pages=20,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    ),
    
    SiteConfig(
        name="watsons_tr",
        base_url="https://www.watsons.com.tr",
        category_paths=[
            "/kozmetik-c-1",        # Cosmetics
            "/cilt-bakimi-c-2",     # Skincare
            "/makyaj-c-3",          # Makeup
            "/parfum-c-4",          # Perfume
            "/sac-bakimi-c-5",      # Hair care
            "/vucut-bakimi-c-6",    # Body care
            "/saglik-c-7",          # Health
            "/wellness-c-8",        # Wellness
            "/organik-c-9",         # Organic
            "/gunes-koruma-c-10",   # Sun protection
            "/erkek-c-11",          # Men's products
            "/anne-bebek-c-12"      # Mother & baby
        ],
        selectors={
            # 🎯 COMPREHENSIVE Watsons selectors - health & beauty focused
            "product_link": [
                "a[href*='/p/']", 
                ".product-item a", 
                ".product-tile a",
                "a[href*='/product/']",
                ".product-card a",
                "[data-testid='product-link']"
            ],
            "next_page": ".pagination-next, a[aria-label='Next'], .next-page, .load-more",
            
            # Health & beauty product selectors
            "name": [
                "h1.product-title",
                "h1", 
                ".product-name", 
                ".product-title",
                ".ProductName",
                "[data-testid='product-name']"
            ],
            "brand": [
                ".brand", 
                ".product-brand", 
                ".brand-name",
                ".Brand",
                ".manufacturer",
                "[data-testid='brand']"
            ],
            "price": [
                ".price", 
                ".product-price", 
                ".current-price",
                ".Price",
                ".final-price",
                "[data-testid='price']"
            ],
            
            # 🌟 HEALTH-FOCUSED content extraction
            "description": [
                ".description", 
                ".product-description",
                ".ProductDescription",
                ".product-details",
                ".detailed-info",
                ".product-info"
            ],
            "long_descriptions": [
                ".product-description-full",
                ".detailed-description",
                ".health-info",
                ".wellness-details",
                ".extended-info"
            ],
            "ingredients": [
                ".ingredients li", 
                ".ingredients-list li",
                ".Ingredients li",
                ".components li",
                "[data-testid='ingredients'] li"
            ],
            "features": [
                ".features li", 
                ".product-features li",
                ".benefits li",
                ".key-features li",
                ".specifications li"
            ],
            "benefits": [
                ".benefits li",
                ".health-benefits li",
                ".advantages li",
                ".wellness-benefits li"
            ],
            "usage": [
                ".usage-instructions",
                ".how-to-use",
                ".directions",
                ".application-info"
            ],
            "reviews": ".review-text, .review-content, .Review__Text, .user-review",
            "images": [
                ".product-image img", 
                ".gallery img",
                ".ProductImages img",
                ".product-photos img",
                "[data-testid='product-image']"
            ],
            
            # Health & wellness metadata
            "product_type": ".breadcrumb a:last-child, .category-current",
            "category_info": ".breadcrumb, .category-navigation"
        },
        rate_limit=2.0,
        max_pages=15,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
        }
    ),
    
    # 🌟 BONUS: Additional premium site configuration
    SiteConfig(
        name="douglas_tr",
        base_url="https://www.douglas.com.tr", 
        category_paths=[
            "/parfum-c-1",
            "/makyaj-c-2", 
            "/cilt-bakimi-c-3",
            "/sac-bakimi-c-4",
            "/vucut-bakimi-c-5"
        ],
        selectors={
            # 🎯 LUXURY Douglas selectors - premium beauty focus
            "product_link": [
                "a[href*='/p/']",
                ".product-tile a",
                ".product-card a", 
                "a[href*='/product/']",
                "[data-testid='product-link']"
            ],
            "next_page": ".pagination__next, .next-page, a[aria-label='Next']",
            
            # Premium luxury selectors
            "name": [
                "h1.product-name",
                "h1.ProductName",
                "h1",
                ".product-title",
                "[data-testid='product-title']"
            ],
            "brand": [
                ".brand-name",
                ".product-brand",
                ".Brand",
                ".manufacturer",
                "[data-testid='brand']"
            ],
            "price": [
                ".price-current",
                ".product-price",
                ".Price",
                ".final-price",
                "[data-testid='price']"
            ],
            
            # 🌟 LUXURY content extraction
            "description": [
                ".product-description",
                ".ProductDescription", 
                ".detailed-description",
                ".luxury-details",
                ".brand-story"
            ],
            "long_descriptions": [
                ".product-description-extended",
                ".luxury-content",
                ".premium-details",
                ".brand-heritage",
                ".detailed-story"
            ],
            "ingredients": [
                ".ingredients li",
                ".Ingredients li",
                ".luxury-ingredients li",
                "[data-testid='ingredients'] li"
            ],
            "features": [
                ".features li",
                ".luxury-features li", 
                ".premium-benefits li",
                ".key-features li"
            ],
            "benefits": [
                ".benefits li",
                ".luxury-benefits li",
                ".premium-advantages li"
            ],
            "usage": [
                ".usage-instructions",
                ".luxury-application",
                ".premium-usage",
                ".application-ritual"
            ],
            "reviews": ".review-text, .Review__Text, .luxury-review",
            "images": [
                ".product-image img",
                ".ProductImages img",
                ".luxury-gallery img",
                "[data-testid='product-image']"
            ],
            
            # Luxury metadata
            "product_type": ".breadcrumb a:last-child, .category-luxury",
            "category_info": ".breadcrumb, .luxury-navigation"
        },
        rate_limit=3.0,
        max_pages=20,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
    )
]

# 🌟 SITE-SPECIFIC ANALYSIS CONFIGURATIONS
SITE_ANALYSIS_CONFIGS = {
    "trendyol": {
        "analysis_focus": "marketplace_optimization",
        "content_priority": ["description", "features", "ingredients"],
        "seo_strategy": "competitive_marketplace",
        "special_handling": {
            "anti_bot": "medium",
            "rate_limiting": "aggressive", 
            "content_depth": "comprehensive"
        }
    },
    "gratis": {
        "analysis_focus": "beauty_specialist", 
        "content_priority": ["long_descriptions", "ingredients", "benefits"],
        "seo_strategy": "beauty_authority",
        "special_handling": {
            "anti_bot": "high",
            "rate_limiting": "very_conservative",
            "content_depth": "maximum"
        }
    },
    "sephora_tr": {
        "analysis_focus": "premium_beauty",
        "content_priority": ["brand_story", "luxury_ingredients", "benefits"],
        "seo_strategy": "luxury_positioning", 
        "special_handling": {
            "anti_bot": "medium",
            "rate_limiting": "standard",
            "content_depth": "premium"
        }
    },
    "rossmann": {
        "analysis_focus": "pharmacy_grade",
        "content_priority": ["ingredients", "usage", "health_benefits"],
        "seo_strategy": "health_wellness",
        "special_handling": {
            "anti_bot": "low",
            "rate_limiting": "standard", 
            "content_depth": "pharmaceutical"
        }
    },
    "watsons_tr": {
        "analysis_focus": "health_beauty",
        "content_priority": ["health_benefits", "ingredients", "usage"],
        "seo_strategy": "wellness_focused",
        "special_handling": {
            "anti_bot": "medium",
            "rate_limiting": "standard",
            "content_depth": "health_focused"
        }
    },
    "douglas_tr": {
        "analysis_focus": "luxury_premium",
        "content_priority": ["brand_heritage", "luxury_ingredients", "premium_benefits"],  
        "seo_strategy": "luxury_authority",
        "special_handling": {
            "anti_bot": "medium",
            "rate_limiting": "premium",
            "content_depth": "luxury"
        }
    }
}

def get_site_analysis_config(site_name: str) -> dict:
    """Get site-specific analysis configuration"""
    return SITE_ANALYSIS_CONFIGS.get(site_name.lower(), {
        "analysis_focus": "general_cosmetic",
        "content_priority": ["description", "features", "ingredients"],
        "seo_strategy": "standard",
        "special_handling": {
            "anti_bot": "medium",
            "rate_limiting": "standard",
            "content_depth": "standard"
        }
    })