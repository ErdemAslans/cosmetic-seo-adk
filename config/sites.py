from config.models import SiteConfig

SITE_CONFIGS = [
    SiteConfig(
        name="trendyol",
        base_url="https://www.trendyol.com",
        category_paths=[
            "/kozmetik-x-c89",
            "/butik/liste/11/kozmetik",
            "/kozmetik-x-c89?pi=1",
            "/kozmetik-x-c89?pi=2"
        ],
        selectors={
            "product_link": "div.p-card-wrppr a",
            "next_page": "a.pagination-next",
            "name": "h1.pr-new-br",
            "brand": "h1.pr-new-br a",
            "price": "span.prc-dsc",
            "description": "div.info-wrapper",
            "ingredients": "div.ingredient-list li",
            "features": "ul.detail-attr-list li",
            "reviews": "div.comment-text",
            "images": "img.detail-img"
        },
        rate_limit=3.0,
        max_pages=50,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    ),
    
    SiteConfig(
        name="sephora_tr",
        base_url="https://www.sephora.com.tr",
        category_paths=[
            "/parfum-c301",
            "/sephora-collection-tum-urunler",
            "/trends",
            "/avantajli-teklif-5"
        ],
        selectors={
            "product_link": "a.product-item-link",
            "next_page": "a.action.next",
            "name": "h1.page-title",
            "brand": "div.product-brand",
            "price": "span.price",
            "description": "div.product-description",
            "ingredients": "div.ingredients-content",
            "features": "div.product-features li",
            "reviews": "div.review-content",
            "images": "img.gallery-image"
        },
        rate_limit=3.0,
        max_pages=30,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
    ),
    
    SiteConfig(
        name="gratis",
        base_url="https://www.gratis.com",
        category_paths=[
            "/makyaj-c-1",
            "/cilt-bakim-c-2", 
            "/parfum-c-3",
            "/ruj-c-4",
            "/oje-c-5",
            "/fondoten-c-6"
        ],
        selectors={
            "product_link": "a[href*='/p/'], .product-item a, .product-card a, [data-product-id] a, .ems-prd-link a",
            "next_page": "a[href*='page='], .pagination-next, .next-page",
            "name": "h1, .product-name, .product-title, .ems-prd-name, .prd-name, [data-testid='product-name']",
            "brand": ".brand-name, .product-brand, .ems-prd-brand, .prd-brand, .brand",
            "price": ".price, .product-price, .ems-prd-price, .prd-price, .price-current, [class*='price']",
            "description": ".product-description, .product-detail, .ems-prd-desc, .prd-desc",
            "ingredients": ".ingredients, .product-ingredients, .ems-prd-ingredients",
            "features": ".features, .product-features, .ems-prd-features",
            "reviews": ".reviews, .product-reviews, .ems-prd-reviews",
            "images": "img[src*='gratis'], .product-image, .ems-prd-image"
        },
        rate_limit=5.0,
        max_pages=20,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    ),
    
    SiteConfig(
        name="rossmann",
        base_url="https://www.rossmann.com.tr",
        category_paths=[
            "/cilt-bakimi",
            "/makyaj",
            "/cilt-bakimi/yuz-bakimi",
            "/makyaj-yardimcilari",
            "/dogal-makyaj-urunleri",
            "/cilt-bakimi/nemlendiriciler"
        ],
        selectors={
            "product_link": "a.product-item-link",
            "next_page": "a.next",
            "name": "h1.product-title",
            "brand": "div.product-brand",
            "price": "span.price-current",
            "description": "div.product-description",
            "ingredients": "div.ingredients-list li",
            "features": "div.product-features li",
            "reviews": "div.review-text",
            "images": "img.product-image"
        },
        rate_limit=3.0,
        max_pages=30,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
]