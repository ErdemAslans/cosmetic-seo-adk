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
            "/makyaj-c-501",
            "/cilt-bakim-c-502",
            "/erkek-bakim-c-505",
            "/cilt-bakim/cilt-temizleme-urunleri-c-50201"
        ],
        selectors={
            "product_link": "a.product-image-for-grid-item",
            "next_page": ".pagination-next a",
            "name": "h5.title",
            "brand": "h5.title",
            "price": ".product-price .amount",
            "description": "div.product-detail-tab-content",
            "ingredients": "div.ingredients p",
            "features": "div.features-list li",
            "reviews": "div.comment-detail",
            "images": "img.product-image"
        },
        rate_limit=2.5,
        max_pages=40,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
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