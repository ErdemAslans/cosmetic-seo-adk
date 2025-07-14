"""
Modern Site Configurations - Updated and Verified
Enhanced configurations for better URL discovery and scraping
"""

from config.models import SiteConfig

MODERN_SITE_CONFIGS = [
    SiteConfig(
        name="trendyol",
        base_url="https://www.trendyol.com",
        category_paths=[
            "/kozmetik-x-c89",
            "/kozmetik/cilt-bakimi-x-c104", 
            "/kozmetik/makyaj-x-c105",
            "/kozmetik/parfum-x-c106",
            "/kozmetik/guzellik-x-c1309"
        ],
        selectors={
            "product_link": "div.p-card-wrppr a, .product-item a, a[href*='/p-'], [data-id] a",
            "next_page": "a.pagination-next, .pagination-next, a[aria-label='Next']",
            "name": "h1.pr-new-br span, h1, .product-name, .product-title",
            "brand": "h1.pr-new-br a, .product-brand, .brand-name, .brand",
            "price": ".prc-dsc, .product-price, .price, .current-price",
            "description": ".detail-desc-list, .product-description, .description, .detail-attr-list",
            "ingredients": ".ingredient-list li, .ingredients li, .detail-attr-item:contains('İçerik')",
            "features": "ul.detail-attr-list li, .product-features li, .features li",
            "reviews": ".comment-text, .review-text, .user-comment",
            "images": "img.detail-img, .product-images img, .gallery img"
        },
        rate_limit=2.0,
        max_pages=20,
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
            "/makyaj-c-12",
            "/cilt-bakimi-c-11", 
            "/parfum-c-14",
            "/sac-bakimi-c-13",
            "/vucut-bakimi-c-16"
        ],
        selectors={
            "product_link": "a[href*='/p/'], .product-item a, .product-card a, [data-product-id] a",
            "next_page": "a[href*='page='], a[rel='next'], .pagination-next, button[aria-label='Next']",
            "name": "h1, .product-name, .product-title, .ems-prd-name",
            "brand": ".product-brand, .brand-name, .brand, .ems-prd-brand",
            "price": ".product-price, .price, .ems-prd-price, [class*='price']",
            "description": ".product-description, .description, .ems-prd-description, .product-detail",
            "ingredients": ".ingredients, .product-ingredients, .ingredients-list li",
            "features": ".product-features li, .features li, .feature-list li",
            "reviews": ".review-content, .reviews .review, .comment-text",
            "images": ".product-image img, .gallery img, img[src*='gratis'], .ems-prd-image img"
        },
        rate_limit=3.0,
        max_pages=15,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
    ),
    
    SiteConfig(
        name="sephora_tr",
        base_url="https://www.sephora.com.tr",
        category_paths=[
            "/makyaj-c301",
            "/cilt-bakimi-c302",
            "/parfum-c303",
            "/sac-bakimi-c304",
            "/erkek-c305"
        ],
        selectors={
            "product_link": "a.product-item-link, .product-tile a, a[href*='/p/'], [data-comp='ProductTile'] a",
            "next_page": "a.action.next, .pagination-next, a[aria-label='Next']",
            "name": "h1.ProductMeta__Title, h1.product-name, h1, .product-title",
            "brand": ".ProductMeta__Brand, .product-brand, .brand-name, .brand",
            "price": ".Price__Value, .product-price, .price, .current-price",
            "description": ".ProductDetail__Description, .product-description, .description",
            "ingredients": ".Ingredients__Content, .ingredients-list, .ingredients li",
            "features": ".ProductBenefits li, .benefits-list li, .features li",
            "reviews": ".ReviewItem__Text, .review-text, .review-content",
            "images": ".ProductImages img, .product-gallery img, .gallery img"
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
            "/cilt-bakimi-c-100",
            "/makyaj-c-200",
            "/parfum-c-300",
            "/sac-bakimi-c-400",
            "/vucut-bakimi-c-500"
        ],
        selectors={
            "product_link": "a.product-item-link, .product-tile a, a[href*='/p/'], .product-card a",
            "next_page": "a.next, .pagination-next, li.next a, a.next-page",
            "name": "h1.product-title, h1, .product-name, .product-title",
            "brand": "div.product-brand, .brand, .manufacturer, .brand-name",
            "price": "span.price-current, .product-price, .price-now, .current-price",
            "description": "div.product-description, .description-content, .description",
            "ingredients": "div.ingredients-list li, .ingredients, .product-ingredients",
            "features": "div.product-features li, .features-list li, .features li",
            "reviews": "div.review-text, .review-content, .comment-content",
            "images": "img.product-image, .gallery img, .product-images img"
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
            "/kozmetik-c-1",
            "/cilt-bakimi-c-2",
            "/makyaj-c-3",
            "/parfum-c-4",
            "/sac-bakimi-c-5"
        ],
        selectors={
            "product_link": "a[href*='/p/'], .product-item a, .product-tile a",
            "next_page": ".pagination-next, a[aria-label='Next']",
            "name": "h1, .product-name, .product-title",
            "brand": ".brand, .product-brand, .brand-name",
            "price": ".price, .product-price, .current-price",
            "description": ".description, .product-description",
            "ingredients": ".ingredients li, .ingredients-list li",
            "features": ".features li, .product-features li",
            "reviews": ".review-text, .review-content",
            "images": ".product-image img, .gallery img"
        },
        rate_limit=2.0,
        max_pages=15,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    )
]